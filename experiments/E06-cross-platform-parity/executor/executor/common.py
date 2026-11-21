"""E06-cross-platform-parity executor: environment, scrubbing, the per-execution bundle, and the run manifest (schemas/run-manifest.schema.v2.json).

DRAFT (operation OP-PREP-E06-EXECUTOR). Not frozen, not locked. Adapted from experiments/E09-accessibility/executor/executor/common.py: one
bundle per execution (one run directory per execution, run-manifest.json written last), one scrubber for every text the executor keeps,
no retry anywhere. Both surfaces (web and Android) build their manifest here, so one schema test covers both.
"""
import datetime
import hashlib
import json
import os
import platform
import re
import sys
import tempfile

from . import config

AGENT_ROLE = 'ORCHESTRATOR'
PROTOCOL_VERSION = 'v1'
# The modality enum of schemas/run-manifest.schema.v2.json: E06 has no enum value of its own, so each execution takes the modality of its
# platform (the parity campaign compares the two platforms; the scenario is recorded in the scenario field).
MODALITY_OF_PLATFORM = {'web': 'Web UI Functional', 'android': 'Android Native'}
WORKFLOW_KEYS = ('ci-provenance.json', 'runtime-environment.json', 'run-manifest.json')


class Abort(Exception):
    """The execution stopped before its record was complete (the record says why)."""


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def stamp(t=None):
    return (t or utcnow()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


class Env:
    """The environment the measured workflow, a DRY_RUN, or an environment verification sets (the same names in every case)."""

    def __init__(self, environ=None):
        e = dict(os.environ if environ is None else environ)
        self.condition = e['CONDITION_ID']
        self.attempt = int(e['ATTEMPT'])
        self.record_class = e['RECORD_CLASS']
        self.expected_identity_oracle = e['EXPECTED_IDENTITY_ORACLE']
        self.prompt_version = e.get('EXECUTOR_PROMPT_VERSION') or None
        self.output_dir = os.path.abspath(e['OUTPUT_DIR'])
        self.provenance_json = os.path.abspath(e['PROVENANCE_JSON'])
        self.runtime_environment_json = os.path.abspath(e['RUNTIME_ENVIRONMENT_JSON'])
        self.conditions_file = os.path.abspath(e.get('CONDITIONS_FILE') or config.CONDITIONS_FILE)
        self.executor_dir = os.path.abspath(e.get('EXECUTOR_DIR') or os.path.join(os.path.dirname(__file__), '..'))
        self.harness_dir = os.path.abspath(e.get('HARNESS_DIR') or os.path.join(self.executor_dir, '..', 'harness'))
        self.apk_path = os.path.abspath(e['APK_PATH']) if e.get('APK_PATH') else None
        self.appium_url = e.get('APPIUM_SERVER_URL') or None
        self.udid = e.get('ANDROID_UDID') or None
        self.node_bin = e.get('NODE_BIN') or 'node'
        self.adb_bin = e.get('ADB_BIN') or 'adb'
        self.bash_version = e.get('EXECUTOR_BASH_VERSION')
        self.started = utcnow()


class Scrubber:
    """Applied to every text the executor keeps: passwords and tokens, JWTs, host paths, and private network addresses never enter a kept file."""

    JWT = re.compile(r'eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]*')
    HOME = re.compile(r'/(?:Users|home)/[A-Za-z0-9._-]+')
    PRIVATE_ADDRESS = re.compile(r'\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b')

    def __init__(self, env):
        self.secrets = []
        paths = [(env.output_dir, '<output>'), (env.executor_dir, '<executor>'), (env.harness_dir, '<harness>'),
                 (os.path.dirname(env.conditions_file), '<conditions>'), (os.environ.get('GITHUB_WORKSPACE', ''), '<workspace>'),
                 (os.getcwd(), '<cwd>'), (os.path.expanduser('~'), '<home>'), (os.path.realpath(tempfile.gettempdir()), '<tmp>'),
                 (tempfile.gettempdir(), '<tmp>'), ('/tmp', '<tmp>')]
        # longest path first; ties (the same directory under two labels) are ordered by label, so the replacement never depends on hash order
        self.paths = sorted({(p, m) for p, m in paths if p and len(p) > 1}, key=lambda x: (-len(x[0]), x[1]))

    def secret(self, value):
        if isinstance(value, str) and len(value) >= 6 and value not in self.secrets:
            self.secrets.append(value)
            self.secrets.sort(key=len, reverse=True)

    @staticmethod
    def marker(value):
        return f'<redacted-token sha256:{hashlib.sha256(value.encode()).hexdigest()[:12]}>'

    def __call__(self, text):
        if not isinstance(text, str):
            text = json.dumps(text, ensure_ascii=False, default=str)
        for s in self.secrets:
            text = text.replace(s, self.marker(s))
        text = self.JWT.sub(lambda m: self.marker(m.group(0)), text)
        for p, m in self.paths:
            text = text.replace(p, m)
        text = self.HOME.sub('<home>', text)
        return self.PRIVATE_ADDRESS.sub('<private-address>', text)


class Run:
    """One execution of one condition: its bundle directory, the records written into it, and its executor.log."""

    def __init__(self, env, scrub, index):
        self.env = env
        self.scrub = scrub
        self.index = index
        self.run_id = f'{env.condition}__EX{index:04d}__A{env.attempt}'
        self.out = os.path.join(env.output_dir, self.run_id)
        os.makedirs(os.path.join(self.out, 'evidence'), exist_ok=True)
        self.started = utcnow()
        self.n = 0
        self.notes = []
        self.tools = {}
        self._log = open(os.path.join(self.out, 'executor.log'), 'a', encoding='utf-8')
        self.log('execution-start', condition=env.condition, run_id=self.run_id, record_class=env.record_class)

    def log(self, event, **kv):
        self._log.write(self.scrub(json.dumps({'t': stamp(), 'event': event, **kv}, ensure_ascii=False, default=str)) + '\n')
        self._log.flush()

    def _name(self, name, ext):
        self.n += 1
        safe = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-')[:80]
        return os.path.join('evidence', f'{self.n:03d}-{safe}.{ext}')

    def text(self, name, content, ext='txt'):
        rel = self._name(name, ext)
        with open(os.path.join(self.out, rel), 'w', encoding='utf-8', newline='\n') as f:
            f.write(self.scrub(content))
        return rel

    def jsonfile(self, name, obj):
        return self.text(name, json.dumps(obj, indent=2, ensure_ascii=False, default=str), 'json')

    def binary(self, name, data, ext):
        """Binary evidence (a screenshot). The bytes are kept as they are: a PNG holds no text the scrubber could replace."""
        rel = self._name(name, ext)
        with open(os.path.join(self.out, rel), 'wb') as f:
            f.write(data)
        return rel

    def close(self):
        try:
            self._log.close()
        except Exception:  # noqa: BLE001 - closing is best effort
            pass


def build_manifest(run, *, condition, outcome, environment_type, platform_name, components, toolchain, related_evidence,
                   notes, reset_mechanisms, establishment_mechanisms):
    """The run manifest of one execution (schemas/run-manifest.schema.v2.json). Only the keys the schema allows are written."""
    env = run.env
    base = f'raw-data/{config.CAMPAIGN}/{condition["sut_id"]}/{run.run_id}'
    arts = []
    for root, _dirs, files in os.walk(run.out):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(root, fn), run.out)
            if rel in WORKFLOW_KEYS:
                continue
            if fn.endswith('.png'):
                kind = 'screenshot'
            elif fn.endswith('.log'):
                kind = 'log'
            elif rel.startswith('evidence'):
                kind = 'evidence'
            else:
                kind = 'record'
            arts.append({'type': kind, 'path': f'{base}/{rel}', 'sha256': sha256_file(os.path.join(run.out, rel))})
    arts.sort(key=lambda a: a['path'])
    for src, name in ((env.provenance_json, 'ci-provenance.json'), (env.runtime_environment_json, 'runtime-environment.json')):
        arts.append({'type': 'provenance', 'path': f'{base}/{name}', 'sha256': sha256_file(src) if os.path.exists(src) else None})
    arts.append({'type': 'manifest', 'path': f'{base}/run-manifest.json', 'sha256': None})
    all_notes = [f'record_class={env.record_class}', f'condition={env.condition}', f'execution index {run.index} of the condition',
                 'the artifacts list holds the sha256 of every kept file except run-manifest.json (written last) and the two provenance files copied by the workflow'] + list(notes) + run.notes
    if env.record_class != 'MEASURED_EXPERIMENT':
        all_notes.append('NON-MEASURED: this bundle never enters raw-data/ and never counts in N (DRY_RUN or ENVIRONMENT_VERIFICATION)')
    m = {
        'campaign_id': config.CAMPAIGN,
        'experiment_id': config.EXPERIMENT,
        'sut_id': condition['sut_id'],
        'timestamp': stamp(run.started),
        'sut_provenance': {'ecosystem_id': condition['sut_id'], 'components': components},
        'environment_type': environment_type,
        'platform': platform_name,
        'condition': condition['condition_id'],
        'scenario': config.SCENARIO,
        'modality': MODALITY_OF_PLATFORM[platform_name],
        'attempt': env.attempt,
        'outcome': outcome,
        'artifacts': arts,
        'notes': run.scrub('; '.join(all_notes)),
        'agent_role': AGENT_ROLE,
        'prompt_version': env.prompt_version,
        'protocol_version': PROTOCOL_VERSION,
        'run_id': run.run_id,
        'actions': [],
        'target_state_id': None,
        'starting_state_id': None,
        'establishment_mechanisms': establishment_mechanisms,
        'reset_mechanisms': reset_mechanisms,
        'seed': None,
        'behavior_class': None,
        'related_evidence_ids': list(related_evidence),
        'toolchain': toolchain,
        'environment': {'os': platform.platform(), 'runtime': f'python {platform.python_version()}'},
    }
    return m


def write_manifest(run, manifest):
    with open(os.path.join(run.out, 'run-manifest.json'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(run.scrub(json.dumps(manifest, indent=2, ensure_ascii=False)))


def python_runtime():
    return {'tool': 'Python', 'version': sys.version.split()[0]}
