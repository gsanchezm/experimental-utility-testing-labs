"""E05-determinism executor: job context, per-execution run, recording, evidence, HTTP client, run manifest.

DRAFT (operation OP-PREP-E05). Derived from the E02 and E03 executors by copying (each campaign locks its own implementation hash;
nothing is imported from another campaign path at run time), then changed where E05 needs other semantics:

* A step that does not hold is a recorded phase outcome (PhaseFailure with its phase), never a stop of the job; the attempt loop maps
  the phase to a pre-declared category (config s.10) and the job goes on to the next execution (IMPLEMENTATION-NOTES.md, point 2).
* The reset is a step, not an action: no actions[] are emitted (D-08c). The stimulus is observed, never raised on: an unexpected SUT
  answer is a classified outcome (a category of the closed set), not an error.
* One job (one dispatch) runs the N executions of one condition on one shared instance; each execution writes its own bundle under
  OUTPUT_DIR/executions/<run_id>/ completely before the next one starts (partial-upload survival).
"""
import collections
import contextlib
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import tempfile
import time
import urllib.error
import urllib.request

CAMPAIGN = 'E05-determinism'
AGENT_ROLE = 'ORCHESTRATOR'
PROTOCOL_VERSION = 'v1'
RECORD_CLASSES = ('MEASURED_EXPERIMENT', 'DRY_RUN', 'DEVELOPMENT')
EXECUTION_PREFIX = {'MEASURED_EXPERIMENT': 'EX', 'DRY_RUN': 'DR', 'DEVELOPMENT': 'DV'}
HTTP_TIMEOUT_S = 30
BODY_LIMIT = 65536
WATCHDOG_S = 600  # per execution; the alarm is re-armed for every execution
PHASES = ('reset', 'starting-state', 'establishment', 'verification', 'stimulus', 'classification')
PROVENANCE_COPIES = (('provenance_json', 'ci-provenance.json'), ('runtime_environment_json', 'runtime-environment.json'))

Spec = collections.namedtuple('Spec', 'modality platform reset_mechanisms establishment_mechanisms components configured')


class Watchdog(Exception):
    """The per-execution budget was exceeded (recorded as an interruption of the phase that was running)."""


class PhaseFailure(Exception):
    """A block of the attempt did not hold or could not run.

    phase: one of PHASES. interrupted: True when the cause is an exception of the harness or of the client (not a recorded observation
    that the SUT or the instance did not hold the expected state). tooling: True only when that exception happened before the stimulus
    request was sent (D-16, rules 1 to 3; uncertain goes to SUT)."""

    def __init__(self, phase, cause, interrupted=False, tooling=False):
        super().__init__(cause)
        self.phase, self.cause, self.interrupted, self.tooling = phase, cause, interrupted, tooling


class Outcome:
    """The classified result of one execution: the category label, what was observed, and the mechanical attribution inputs."""

    def __init__(self, label, observed, cause=None, attribution='SUT', notes=None):
        self.label, self.observed, self.cause, self.attribution = label, observed, cause, attribution
        self.notes = list(notes or [])


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
    """The environment the measured workflow sets (or a DRY_RUN / DEVELOPMENT caller sets the same names). Job level: one condition."""

    def __init__(self):
        e = os.environ
        self.condition = e['CONDITION_ID']
        self.sut = e['ASSIGNED_SUT']
        self.prompt_version = e['EXECUTOR_PROMPT_VERSION']
        self.output_dir = os.path.abspath(e['OUTPUT_DIR'])
        self.provenance_json = os.path.abspath(e['PROVENANCE_JSON'])
        self.runtime_environment_json = os.path.abspath(e['RUNTIME_ENVIRONMENT_JSON'])
        self.instance_json = os.path.abspath(e.get('INSTANCE_JSON') or 'instance.json')
        self.record_class = e['RECORD_CLASS']
        self.executor_dir = os.path.abspath(e.get('EXECUTOR_DIR') or os.path.join(os.path.dirname(__file__), '..'))
        self.bash_version = e.get('EXECUTOR_BASH_VERSION')
        self.attempt = int(e.get('ATTEMPT') or 1)
        self.first = int(e.get('FIRST_EXECUTION') or 1)
        self.executions = int(e['EXECUTIONS']) if e.get('EXECUTIONS') else None  # None: the configuration's n (measured runs only)

    def execution_id(self, index):
        return f'{EXECUTION_PREFIX[self.record_class]}{index:04d}'

    def run_id(self, index):
        return f'{self.condition}__{self.execution_id(index)}__A{self.attempt}'


class Scrubber:
    """Applied to every text the executor writes: session secrets, host paths, and private network addresses never enter a kept file."""

    JWT = re.compile(r'eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]*')
    HOME = re.compile(r'/(?:Users|home)/[A-Za-z0-9._-]+')
    # An IPv4 literal of the three private ranges of RFC 1918: the same pattern as the private-address redaction rule of the publication record.
    PRIVATE_ADDRESS = re.compile(r'\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b')

    def __init__(self, env):
        self.secrets = []
        paths = [(env.output_dir, '<output>'), (env.executor_dir, '<executor>'), (os.path.dirname(env.instance_json), '<instance>'),
                 (os.environ.get('GITHUB_WORKSPACE', ''), '<workspace>'), (os.getcwd(), '<cwd>'), (os.path.expanduser('~'), '<home>'),
                 (os.path.realpath(tempfile.gettempdir()), '<tmp>'), (tempfile.gettempdir(), '<tmp>'), ('/private/tmp', '<tmp>'), ('/tmp', '<tmp>')]
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


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())


class Response:
    def __init__(self, status, headers, body, error, evidence, elapsed_s):
        self.status, self.headers, self.body, self.error, self.evidence, self.elapsed_s = status, headers, body, error, evidence, elapsed_s

    def json(self):
        return json.loads(self.body.decode('utf-8'))

    def timed_out(self):
        return bool(self.error) and 'timed out' in self.error.lower()


class Job:
    """What the N executions of one condition share: the environment, the configuration of the condition, the instance, the tools."""

    def __init__(self, env, cfg, c):
        self.env, self.cfg, self.c = env, cfg, c
        self.instance = None
        self.instance_sha256 = None
        self.tools = {}
        self.notes = []
        self.summary = []
        self.scrub = Scrubber(env)  # job-level: secrets registered by one execution are scrubbed in every later one
        self.restarted_logs = []
        self.first = env.first
        self.last = env.executions if env.executions is not None else cfg['n_per_condition']
        self.planned = self.last - self.first + 1


class Run:
    """One execution (attempt A<n>): the bundle under OUTPUT_DIR/executions/<run_id>/ and the records written into it."""

    def __init__(self, job, index):
        self.job, self.env, self.index = job, job.env, index
        self.execution_id = job.env.execution_id(index)
        self.run_id = job.env.run_id(index)
        self.started = utcnow()
        self.out = os.path.join(job.env.output_dir, 'executions', self.run_id)
        os.makedirs(os.path.join(self.out, 'evidence'), exist_ok=True)
        self.scrub = job.scrub
        self.n = 0
        self.steps = []
        self.notes = []
        self.stimulus_sent = False
        self.phase = None
        self._log = open(os.path.join(self.out, 'executor.log'), 'a', encoding='utf-8')
        self.log('run-start', condition=self.env.condition, run_id=self.run_id, record_class=self.env.record_class)

    # ---- logging and evidence -------------------------------------------------------------------------------
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

    def capture(self, rec, fn, *args, key=None):
        """Evidence capture is not an observation of the SUT: a failed capture is recorded under evidence_errors and changes no outcome."""
        try:
            value = fn(*args)
        except Exception as e:  # noqa: BLE001 - evidence only
            rec.setdefault('evidence_errors', []).append(f'{key or getattr(fn, "__name__", "capture")}: {e.__class__.__name__}: {e}')
            self.log('evidence-error', error=rec['evidence_errors'][-1])
            return None
        if key:
            rec['observation'] = {**(rec.get('observation') or {}), key: value}
        else:
            rec['evidence'].append(value)
        return value

    # ---- HTTP (Python standard library; no redirect following, no proxy, no retry) ----------------------------
    def _register_cookies(self, headers):
        for raw in (headers.get_all('Set-Cookie') or []) if headers is not None else []:
            pair = raw.split(';', 1)[0]
            if '=' in pair:
                self.scrub.secret(pair.split('=', 1)[1].strip().strip('"'))

    def http(self, method, url, body=None, headers=None, label='http', timeout=HTTP_TIMEOUT_S):
        hdrs = {'Accept': 'application/json', **(headers or {})}
        data = None
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode('utf-8')
            hdrs.setdefault('Content-Type', 'application/json')
        elif isinstance(body, (bytes, str)):
            data = body.encode('utf-8') if isinstance(body, str) else body
        req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
        t0 = time.monotonic()
        started = stamp()
        status, rheaders, rbody, error = None, {}, b'', None
        try:
            with _OPENER.open(req, timeout=timeout) as r:
                status, rheaders, rbody = r.status, dict(r.headers.items()), r.read()
                self._register_cookies(r.headers)
        except urllib.error.HTTPError as e:
            status, rheaders = e.code, dict((e.headers or {}).items())
            self._register_cookies(e.headers)
            try:
                rbody = e.read() or b''
            except Exception:  # noqa: BLE001 - the body of an error response is evidence only
                rbody = b''
            finally:
                e.close()
        except Exception as e:  # noqa: BLE001 - a transport failure is an observation, recorded as such
            error = f'{e.__class__.__name__}: {e}'
        elapsed = round(time.monotonic() - t0, 3)
        shown = None if data is None else data.decode('utf-8', 'replace')
        rec = {'started_at': started, 'elapsed_s': elapsed, 'request': {'method': method, 'url': url, 'headers': hdrs, 'body': shown},
               'response': {'status': status, 'headers': rheaders, 'body': rbody[:BODY_LIMIT].decode('utf-8', 'replace'), 'body_bytes': len(rbody)},
               'error': error}
        ev = self.jsonfile(label, rec)
        self.log('http', method=method, url=url, status=status, error=error, elapsed_s=elapsed, evidence=ev)
        return Response(status, rheaders, rbody, error, ev, elapsed)

    def rescrub(self, rel):
        """Rewrite one evidence file through the scrubber once a secret that appeared in it is registered (SUT-04's token is not a JWT)."""
        path = os.path.join(self.out, rel)
        with open(path, encoding='utf-8') as f:
            text = f.read()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.scrub(text))

    # ---- blocks of the attempt ---------------------------------------------------------------------------------
    def mark_stimulus_sent(self):
        """Called by a realization immediately before it sends the stimulus (the boundary of D-16, rule 1)."""
        self.stimulus_sent = True
        self.log('stimulus-sent')

    def _begin(self, phase, description, mechanisms):
        if phase not in PHASES:
            raise ValueError(f'unknown phase {phase!r}')
        rec = {'phase': phase, 'description': description, 'mechanisms': mechanisms or [], 'started_at': stamp(), 'outcome': None,
               'observation': None, 'evidence': []}
        self.steps.append(rec)
        self.phase = phase
        self.log('step-start', phase=phase, description=description)
        return rec

    @contextlib.contextmanager
    def step(self, phase, description, mechanisms=None):
        """A block that must hold for the attempt to go on. The body sets rec['outcome'] = 'FAILURE' when the SUT or the instance does not
        hold what the block requires (a recorded observation: PhaseFailure with interrupted False). An exception of the harness or of the
        client is an interruption (PhaseFailure with interrupted True, tooling True while the stimulus request has not been sent)."""
        rec = self._begin(phase, description, mechanisms)
        try:
            yield rec
        except PhaseFailure:
            rec['outcome'] = rec['outcome'] or 'FAILURE'
            raise
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as e:  # noqa: BLE001 - Watchdog and every harness or client exception: an interruption of this phase
            rec['outcome'] = 'ERROR'
            rec['error'] = f'{e.__class__.__name__}: {e}'
            raise PhaseFailure(phase, f'{phase} was interrupted ({description}): {rec["error"]}', interrupted=True,
                               tooling=not self.stimulus_sent) from e
        finally:
            rec['finished_at'] = stamp()
            self.log('step-end', phase=phase, outcome=rec['outcome'])
        if rec['outcome'] is None:
            rec['outcome'] = 'SUCCESS'
        if rec['outcome'] != 'SUCCESS':
            raise PhaseFailure(phase, f'{phase} did not hold ({description}): {rec.get("observation")}')

    @contextlib.contextmanager
    def observe(self, phase, description, mechanisms=None):
        """A block whose outcome is classified, never judged: stimulus and classification reads. An observation that is a SUT answer is
        recorded and returned; only an exception of the harness or of the client is an interruption (PhaseFailure, interrupted True)."""
        rec = self._begin(phase, description, mechanisms)
        try:
            yield rec
            if rec['outcome'] is None:
                rec['outcome'] = 'OBSERVED'
        except PhaseFailure:
            rec['outcome'] = rec['outcome'] or 'ERROR'
            raise
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as e:  # noqa: BLE001
            rec['outcome'] = 'ERROR'
            rec['error'] = f'{e.__class__.__name__}: {e}'
            raise PhaseFailure(phase, f'{phase} was interrupted ({description}): {rec["error"]}', interrupted=True,
                               tooling=not self.stimulus_sent) from e
        finally:
            rec['finished_at'] = stamp()
            self.log('step-end', phase=phase, outcome=rec['outcome'])

    # ---- bundle files ---------------------------------------------------------------------------------------
    def duration_s(self):
        return round((utcnow() - self.started).total_seconds(), 3)

    def write_records(self, outcome, c, label_note=None):
        rec = {'record_class': self.env.record_class, 'run_id': self.run_id, 'condition': self.env.condition, 'execution_id': self.execution_id,
               'attempt': self.env.attempt, 'scenario': 'CS-001', 'outcome_category': outcome.label, 'observed': outcome.observed,
               'cause': outcome.cause, 'attribution': outcome.attribution, 'stimulus_request_sent': self.stimulus_sent,
               'last_phase': self.phase, 'duration_s': self.duration_s(), 'steps': self.steps, 'notes': self.notes + outcome.notes,
               'note': 'attribution is mechanical (D-16, D-16b): TOOLING only for an exception before the stimulus request was sent; '
                       'the label is carried in outcome.outcome_category of run-manifest.json and never changes a rate'}
        with open(os.path.join(self.out, 'attempt-record.json'), 'w', encoding='utf-8') as f:
            f.write(self.scrub(json.dumps(rec, indent=2, ensure_ascii=False, default=str)))
        with open(os.path.join(self.out, 'tool-versions.json'), 'w', encoding='utf-8') as f:
            f.write(self.scrub(json.dumps(self.job.tools, indent=2, ensure_ascii=False)))

    def copy_provenance(self):
        for attr, name in PROVENANCE_COPIES:
            src = getattr(self.env, attr)
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(self.out, name))

    def close(self):
        try:
            self._log.close()
        except Exception:  # noqa: BLE001
            pass


def build_manifest(run, outcome_obj, spec, components, notes_extra=None):
    """The run manifest (schema v2) of one execution. outcome_obj is classify.manifest_outcome(...)."""
    env, job = run.env, run.job
    prov = read_json(env.provenance_json) if os.path.exists(env.provenance_json) else {}
    env_type = prov.get('environment_type') or ('LOCAL' if env.record_class == 'DEVELOPMENT' else None)
    base = f'raw-data/{CAMPAIGN}/{env.sut}/{run.run_id}'
    arts = []
    for root, _dirs, files in os.walk(run.out):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(root, fn), run.out)
            if rel == 'run-manifest.json':
                continue
            kind = ('screenshot' if fn.endswith('.png') else 'provenance' if rel in ('ci-provenance.json', 'runtime-environment.json')
                    else 'log' if fn.endswith('.log') else 'evidence' if rel.startswith('evidence') else 'record')
            arts.append({'type': kind, 'path': f'{base}/{rel}', 'sha256': sha256_file(os.path.join(run.out, rel))})
    arts.sort(key=lambda a: a['path'])
    arts.append({'type': 'manifest', 'path': f'{base}/run-manifest.json', 'sha256': None})
    notes = [f'record_class={env.record_class}', f'execution {run.execution_id} of the condition',
             f'instance.json sha256={job.instance_sha256}' if job.instance_sha256 else 'instance.json: not read',
             'one shared instance for the N executions of the condition; the reset of the condition runs first in every execution (D-02, model B)',
             'artifacts: run-manifest.json carries sha256 null because a file cannot carry its own digest; the job-level files (stdout.log, stderr.log, '
             'exit-status.txt, finished-at.txt, condition-summary.json) sit at the artifact root and are not part of this bundle',
             'no manual intervention', 'no actions[]: the reset is not emitted as an action (D-08c) and the stimulus is classified, not counted'] \
        + list(notes_extra or []) + list(run.notes) + list(job.notes)
    if env_type is None:
        notes.append('environment_type absent from the provenance record: recorded as OTHER')
    toolchain = {k: v for k, v in job.tools.items() if isinstance(v, dict) and 'tool' in v}
    return {'campaign_id': CAMPAIGN, 'experiment_id': env.condition, 'sut_id': env.sut, 'timestamp': stamp(run.started),
            'sut_provenance': {'ecosystem_id': env.sut, 'components': components}, 'environment_type': env_type or 'OTHER',
            'platform': spec.platform, 'scenario': 'CS-001', 'condition': env.condition, 'modality': spec.modality, 'attempt': env.attempt,
            'seed': None, 'outcome': outcome_obj, 'artifacts': arts, 'notes': run.scrub('; '.join(notes)), 'agent_role': AGENT_ROLE,
            'prompt_version': env.prompt_version, 'protocol_version': PROTOCOL_VERSION, 'run_id': run.run_id,
            'target_state_id': 'CS-001', 'starting_state_id': 'CS-001-STARTING',
            'establishment_mechanisms': list(spec.establishment_mechanisms), 'reset_mechanisms': list(spec.reset_mechanisms),
            'behavior_class': job.c['behavior_class'], 'toolchain': toolchain,
            'environment': {'os': platform.platform(), 'runtime': f'python {platform.python_version()}'}}


def write_manifest(run, manifest):
    with open(os.path.join(run.out, 'run-manifest.json'), 'w', encoding='utf-8') as f:
        f.write(run.scrub(json.dumps(manifest, indent=2, ensure_ascii=False)))
