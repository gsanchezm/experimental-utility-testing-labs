"""E09 accessibility executor: run context, scrubbing, recording, and the run manifest (schemas/run-manifest.schema.v2.json).

DRAFT (operation OP-PREP-E09). Not frozen, not locked. Adapted by copying the generic helpers of the E03 executor
(experiments/E03-resetability/executor/executor/common.py); nothing is imported from the E03 path at run time.
Every text the executor writes passes the scrubber; no retry anywhere; the manifest is written last.
"""
import datetime
import hashlib
import json
import os
import platform
import re
import tempfile

CAMPAIGN = 'E09-accessibility'
EXPERIMENT = 'E09-A11Y-SUT01'
MODALITY = 'Accessibility — Web only'
PLATFORM = 'web'
AGENT_ROLE = 'ORCHESTRATOR'
PROTOCOL_VERSION = 'v1'
RECORD_CLASSES = ('MEASURED_EXPERIMENT', 'DRY_RUN', 'DEVELOPMENT', 'ENVIRONMENT_VERIFICATION')
WORKFLOW_FILES = ('stdout.log', 'stderr.log', 'exit-status.txt', 'finished-at.txt')


class Abort(Exception):
    """The run stops before the scan (outcome ABORTED; no detection is judged)."""


class Watchdog(Exception):
    """The whole-run budget was exceeded (outcome ERROR)."""


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def stamp(t=None):
    return (t or utcnow()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class Env:
    """The environment the measured workflow sets (a DRY_RUN, DEVELOPMENT, or verification caller sets the same names)."""

    def __init__(self):
        e = os.environ
        self.condition = e['CONDITION_ID']
        self.sut = e['ASSIGNED_SUT']
        self.execution_id = e['EXECUTION_ID']
        self.attempt = int(e['ATTEMPT'])
        self.prompt_version = e['EXECUTOR_PROMPT_VERSION']
        self.output_dir = os.path.abspath(e['OUTPUT_DIR'])
        self.provenance_json = os.path.abspath(e['PROVENANCE_JSON'])
        self.runtime_environment_json = os.path.abspath(e['RUNTIME_ENVIRONMENT_JSON'])
        self.instance_json = os.path.abspath(e.get('INSTANCE_JSON') or 'instance.json')
        self.axe_tarball = os.path.abspath(e['AXE_TARBALL']) if e.get('AXE_TARBALL') else None
        self.record_class = e['RECORD_CLASS']
        self.executor_dir = os.path.abspath(e.get('EXECUTOR_DIR') or os.path.join(os.path.dirname(__file__), '..'))
        self.bash_version = e.get('EXECUTOR_BASH_VERSION')
        self.run_id = f'{self.condition}__{self.execution_id}__A{self.attempt}'


class Scrubber:
    """Applied to every text the executor writes: secrets, JWTs, host paths, and private network addresses never enter a kept file."""

    JWT = re.compile(r'eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]*')
    HOME = re.compile(r'/(?:Users|home)/[A-Za-z0-9._-]+')
    PRIVATE_ADDRESS = re.compile(r'\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b')

    def __init__(self, env):
        self.secrets = []
        paths = [(env.output_dir, '<output>'), (env.executor_dir, '<executor>'), (os.path.dirname(env.instance_json), '<instance>'),
                 (os.environ.get('GITHUB_WORKSPACE', ''), '<workspace>'), (os.getcwd(), '<cwd>'), (os.path.expanduser('~'), '<home>'),
                 (os.path.realpath(tempfile.gettempdir()), '<tmp>'), (tempfile.gettempdir(), '<tmp>'), ('/tmp', '<tmp>')]
        self.paths = sorted({(p, m) for p, m in paths if p and len(p) > 1}, key=lambda x: -len(x[0]))

    def secret(self, value):
        if isinstance(value, str) and len(value) >= 8 and value not in self.secrets:
            self.secrets.append(value)
            self.secrets.sort(key=len, reverse=True)

    @staticmethod
    def marker(value):
        return f'<redacted-token sha256:{hashlib.sha256(value.encode()).hexdigest()[:12]}>'

    def __call__(self, text):
        for s in self.secrets:
            text = text.replace(s, self.marker(s))
        text = self.JWT.sub(lambda m: self.marker(m.group(0)), text)
        for p, m in self.paths:
            text = text.replace(p, m)
        text = self.HOME.sub('<home>', text)
        return self.PRIVATE_ADDRESS.sub('<private-address>', text)


class Run:
    """One condition, one attempt: the bundle under OUTPUT_DIR and the records written into it."""

    def __init__(self, env):
        self.env = env
        self.started = utcnow()
        self.out = env.output_dir
        os.makedirs(os.path.join(self.out, 'evidence'), exist_ok=True)
        self.scrub = Scrubber(env)
        self.n = 0
        self.notes = []
        self.tools = {}
        self.instance = None
        self.instance_sha256 = None
        self._log = open(os.path.join(self.out, 'executor.log'), 'a', encoding='utf-8')
        self.log('run-start', condition=env.condition, run_id=env.run_id, record_class=env.record_class)

    def log(self, event, **kv):
        self._log.write(self.scrub(json.dumps({'t': stamp(), 'event': event, **kv}, ensure_ascii=False, default=str)) + '\n')
        self._log.flush()

    def _name(self, name, ext):
        self.n += 1
        safe = re.sub(r'[^A-Za-z0-9._-]+', '-', name).strip('-')[:80]
        return os.path.join('evidence', f'{self.n:03d}-{safe}.{ext}')

    def text(self, name, content, ext='txt'):
        rel = self._name(name, ext)
        with open(os.path.join(self.out, rel), 'w', encoding='utf-8') as f:
            f.write(self.scrub(content))
        return rel

    def jsonfile(self, name, obj):
        return self.text(name, json.dumps(obj, indent=2, ensure_ascii=False, default=str), 'json')

    def binary(self, name, data, ext):
        rel = self._name(name, ext)
        with open(os.path.join(self.out, rel), 'wb') as f:
            f.write(data)
        return rel

    def close(self):
        try:
            self._log.close()
        except Exception:  # noqa: BLE001 - closing is best effort
            pass


class Result:
    """The attempt's outcome. status and outcome_category follow the mapping of classify.classify."""

    def __init__(self, status, category, expected, observed, matches_expected, notes=None):
        self.status, self.category, self.expected, self.observed = status, category, expected, observed
        self.matches_expected = matches_expected
        self.notes = notes or []


def build_manifest(run, result, components, condition, behavior_class, related_evidence, toolchain):
    """The run manifest of one attempt (schemas/run-manifest.schema.v2.json). Keys are only those the schema allows."""
    env = run.env
    prov = read_json(env.provenance_json) if os.path.exists(env.provenance_json) else {}
    env_type = prov.get('environment_type') or ('LOCAL' if env.record_class == 'DEVELOPMENT' else None)
    base = f'raw-data/{CAMPAIGN}/{env.sut}/{env.run_id}'
    arts = []
    for root, _dirs, files in os.walk(run.out):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(root, fn), run.out)
            if rel in WORKFLOW_FILES or rel in ('ci-provenance.json', 'runtime-environment.json', 'run-manifest.json'):
                continue
            kind = 'screenshot' if fn.endswith('.png') else ('log' if fn.endswith('.log') else ('evidence' if rel.startswith('evidence') else 'record'))
            arts.append({'type': kind, 'path': f'{base}/{rel}', 'sha256': sha256_file(os.path.join(run.out, rel))})
    arts.sort(key=lambda a: a['path'])
    for src, name in ((env.provenance_json, 'ci-provenance.json'), (env.runtime_environment_json, 'runtime-environment.json')):
        arts.append({'type': 'provenance', 'path': f'{base}/{name}', 'sha256': sha256_file(src) if os.path.exists(src) else None})
    for fn in WORKFLOW_FILES:
        arts.append({'type': 'log' if fn.endswith('.log') else 'record', 'path': f'{base}/{fn}', 'sha256': None})
    arts.append({'type': 'manifest', 'path': f'{base}/run-manifest.json', 'sha256': None})
    notes = [f'record_class={env.record_class}', f'condition kind and account per the E09 configuration draft, section 3e',
             f'instance.json sha256={run.instance_sha256}' if run.instance_sha256 else 'instance.json: not read',
             'artifacts: stdout.log, stderr.log, exit-status.txt, and finished-at.txt carry sha256 null because the workflow writes them after the manifest; run-manifest.json carries null because a file cannot carry its own digest; ci-provenance.json and runtime-environment.json are hashed from the source paths the workflow copies byte for byte',
             'no Required Actions are recorded for E09 (HUMAN DECISION HD-15, default used); the activation is recorded in activation.json, not counted',
             'behavior_class null: TBD for the control condition until confirmed (brief, section 13 item 3)' if behavior_class is None and condition.startswith('E09-CTRL') else 'behavior_class as configured']
    notes += list(result.notes) + list(run.notes)
    if env_type is None:
        notes.append('environment_type absent from the provenance record: recorded as OTHER')
    outcome = {'status': result.status, 'expected': result.expected, 'observed': result.observed,
               'matches_expected': result.matches_expected, 'outcome_category': result.category}
    m = {'campaign_id': CAMPAIGN, 'experiment_id': EXPERIMENT, 'sut_id': env.sut, 'timestamp': stamp(run.started),
         'sut_provenance': {'ecosystem_id': env.sut, 'components': components}, 'environment_type': env_type or 'OTHER',
         'platform': PLATFORM, 'condition': condition, 'modality': MODALITY, 'attempt': env.attempt, 'outcome': outcome,
         'artifacts': arts, 'notes': run.scrub('; '.join(notes)), 'agent_role': AGENT_ROLE, 'prompt_version': env.prompt_version,
         'protocol_version': PROTOCOL_VERSION, 'run_id': env.run_id, 'actions': [], 'target_state_id': None,
         'starting_state_id': None, 'establishment_mechanisms': None, 'reset_mechanisms': None, 'seed': None,
         'behavior_class': behavior_class, 'related_evidence_ids': list(related_evidence), 'toolchain': toolchain,
         'environment': {'os': platform.platform(), 'runtime': f'python {platform.python_version()}'}}
    return m


def write_manifest(run, manifest):
    with open(os.path.join(run.out, 'run-manifest.json'), 'w', encoding='utf-8') as f:
        f.write(run.scrub(json.dumps(manifest, indent=2, ensure_ascii=False)))
