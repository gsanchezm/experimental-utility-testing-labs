"""E03-resetability executor: run context, recording, evidence, HTTP client, run manifest.

DRAFT (operation OP-PREP-E03); not frozen, not locked. Conventions: experiments/E03-resetability/executor/README.md.
Only the reset-side Required Actions enter actions[]; the precondition, the establishment, and the pre-reset
verification are recorded in precondition.json and never counted (protocol/setup-effort-v2.md, Sections 3 and 5).
No retry anywhere: every operation is performed once and keeps its outcome.
"""
import contextlib
import datetime
import hashlib
import json
import os
import platform
import re
import tempfile
import time
import urllib.error
import urllib.request

CAMPAIGN = 'E03-resetability'
EXPERIMENT = 'E03-CS001'
SCENARIO = 'CS-001'
PROTOCOL_VERSION = 'v1'
AGENT_ROLE = 'EXECUTOR-E03-RESETABILITY'
RECORD_CLASSES = ('MEASURED_EXPERIMENT', 'DRY_RUN', 'DEVELOPMENT')
HTTP_TIMEOUT_S = 30
BODY_LIMIT = 65536
WORKFLOW_FILES = ('stdout.log', 'stderr.log', 'exit-status.txt', 'finished-at.txt')


class Abort(Exception):
    """The run stops before the first reset-side action (outcome ABORTED, empty actions[])."""


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


class Env:
    """The environment the measured workflow sets (or a DEVELOPMENT / DRY_RUN caller sets the same names)."""

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
        self.record_class = e['RECORD_CLASS']
        self.executor_dir = os.path.abspath(e.get('EXECUTOR_DIR') or os.path.join(os.path.dirname(__file__), '..'))
        self.bash_version = e.get('EXECUTOR_BASH_VERSION')
        self.run_id = f'{self.condition}__{self.execution_id}__A{self.attempt}'


class Scrubber:
    """Applied to every text the executor writes: session secrets and host paths never enter a kept file."""

    JWT = re.compile(r'eyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]*')
    HOME = re.compile(r'/(?:Users|home)/[A-Za-z0-9._-]+')

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
        return self.HOME.sub('<home>', text)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())


class Response:
    def __init__(self, status, headers, body, error, evidence, elapsed_s):
        self.status, self.headers, self.body, self.error, self.evidence, self.elapsed_s = status, headers, body, error, evidence, elapsed_s

    def json(self):
        return json.loads(self.body.decode('utf-8'))


class Run:
    """One condition, one attempt: the bundle under OUTPUT_DIR and the records written into it."""

    def __init__(self, env):
        self.env = env
        self.started = utcnow()
        self.out = env.output_dir
        os.makedirs(os.path.join(self.out, 'evidence'), exist_ok=True)
        self.scrub = Scrubber(env)
        self.n = 0
        self.pre = []
        self.actions = []
        self.declared = None
        self.notes = []
        self.tools = {}
        self.instance = None
        self.instance_sha256 = None
        self.surfaces_used = []
        self._log = open(os.path.join(self.out, 'executor.log'), 'a', encoding='utf-8')
        self.log('run-start', condition=env.condition, run_id=env.run_id, record_class=env.record_class)

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
        """Evidence capture is not an action (README section 3, item 4): it runs after the record's outcome criterion was
        evaluated, and a failed capture is recorded under evidence_errors without changing any outcome. With key, the value
        goes into the record's observation under that key; otherwise the returned evidence path is appended to its evidence."""
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
        """Every cookie value a response sets is registered with the scrubber before the transcript is written (README section 9),
        whatever the cookie's name and form; a value shorter than eight characters is not registered (Scrubber.secret)."""
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
        except Exception as e:  # noqa: BLE001 - a transport failure is an observation, recorded as such
            error = f'{e.__class__.__name__}: {e}'
        elapsed = round(time.monotonic() - t0, 3)
        rec = {'started_at': started, 'elapsed_s': elapsed, 'request': {'method': method, 'url': url, 'headers': hdrs,
               'body': data.decode('utf-8', 'replace') if data else None},
               'response': {'status': status, 'headers': rheaders, 'body': rbody[:BODY_LIMIT].decode('utf-8', 'replace'),
                            'body_bytes': len(rbody)}, 'error': error}
        ev = self.jsonfile(label, rec)
        self.log('http', method=method, url=url, status=status, error=error, elapsed_s=elapsed, evidence=ev)
        return Response(status, rheaders, rbody, error, ev, elapsed)

    # ---- not-counted steps (precondition, establishment, pre-reset verification) -------------------------------
    @contextlib.contextmanager
    def step(self, phase, description, mechanisms=None):
        if self.actions:
            raise RuntimeError('an establish-side step after a reset-side action is a design error')
        rec = {'phase': phase, 'description': description, 'mechanisms': mechanisms or [], 'started_at': stamp(),
               'outcome': None, 'observation': None, 'evidence': [], 'counted_as_required_action': False}
        self.pre.append(rec)
        self.log('step-start', phase=phase, description=description)
        try:
            yield rec
            if rec['outcome'] is None:
                rec['outcome'] = 'SUCCESS'
        except Abort as a:
            rec['outcome'] = 'FAILURE'
            rec['error'] = str(a)
            raise
        except Exception as e:  # noqa: BLE001 - any failure before the reset side aborts the attempt
            rec['outcome'] = 'FAILURE'
            rec['error'] = f'{e.__class__.__name__}: {e}'
            raise Abort(f'{phase} failed ({description}): {rec["error"]}') from e
        finally:
            rec['finished_at'] = stamp()
            self.log('step-end', phase=phase, outcome=rec['outcome'])
        if rec['outcome'] != 'SUCCESS':
            raise Abort(f'{phase} did not hold ({description}): {rec.get("observation")}')

    def declare_starting_state(self, definition, citations, observed, holds):
        """Section 3, item 11: the declared starting state is read before the establishment; when it does not hold the run is ABORTED."""
        self.declared = {'id': 'CS-001-STARTING', 'definition': definition, 'citations': citations, 'observed_before_establishment': observed,
                         'holds': bool(holds)}
        if not holds:
            raise Abort(f'declared starting state does not hold before the establishment: {observed}')

    # ---- reset-side Required Actions ----------------------------------------------------------------------------
    @contextlib.contextmanager
    def action(self, cls, description):
        a = {'position': len(self.actions) + 1, 'class': cls, 'description': description, 'is_retry': False, 'outcome': None,
             'started_at': stamp(), 'observation': None, 'evidence': []}
        self.actions.append(a)
        self.log('action-start', position=a['position'], cls=cls, description=description)
        try:
            yield a
            if a['outcome'] is None:
                raise RuntimeError(f'action {a["position"]} ended without an outcome (design error)')
        except Exception as e:  # noqa: BLE001 - a failed action keeps its outcome; the run goes on where the row says so
            if a['outcome'] is None or isinstance(e, RuntimeError):
                a['outcome'] = 'FAILURE'
            a['error'] = f'{e.__class__.__name__}: {e}'
        finally:
            a['finished_at'] = stamp()
            self.log('action-end', position=a['position'], outcome=a['outcome'], error=a.get('error'))

    # ---- bundle files ---------------------------------------------------------------------------------------
    def write_records(self, result):
        pre = {'record_class': self.env.record_class, 'run_id': self.env.run_id, 'condition': self.env.condition, 'scenario': SCENARIO,
               'declared_starting_state': self.declared, 'steps': self.pre,
               'note': 'precondition, establishment, and pre-reset verification: recorded, never counted as Required Actions - reset'}
        if result.status == 'ABORTED':
            pre['abort_cause'] = result.observed
        with open(os.path.join(self.out, 'precondition.json'), 'w', encoding='utf-8') as f:
            f.write(self.scrub(json.dumps(pre, indent=2, ensure_ascii=False, default=str)))
        acts = {'run_id': self.env.run_id, 'actions': self.actions,
                'comparison': {'declared_starting_state': (self.declared or {}).get('definition'), 'expected': result.expected,
                               'observed': result.observed, 'outcome': result.status}}
        with open(os.path.join(self.out, 'actions.json'), 'w', encoding='utf-8') as f:
            f.write(self.scrub(json.dumps(acts, indent=2, ensure_ascii=False, default=str)))
        with open(os.path.join(self.out, 'tool-versions.json'), 'w', encoding='utf-8') as f:
            f.write(self.scrub(json.dumps(self.tools, indent=2, ensure_ascii=False)))

    def close(self):
        try:
            self._log.close()
        except Exception:  # noqa: BLE001
            pass


class Result:
    def __init__(self, status, expected, observed, reset_mechanisms, establishment_mechanisms, notes=None):
        self.status, self.expected, self.observed = status, expected, observed
        self.reset_mechanisms, self.establishment_mechanisms = reset_mechanisms, establishment_mechanisms
        self.notes = notes or []


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def build_manifest(run, result, modality, platform_name, components):
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
    notes = [f'record_class={env.record_class}',
             f'instance.json sha256={run.instance_sha256}' if run.instance_sha256 else 'instance.json: not read',
             'artifacts: stdout.log, stderr.log, exit-status.txt, and finished-at.txt carry sha256 null because the workflow writes them after the manifest; run-manifest.json carries null because a file cannot carry its own digest; ci-provenance.json and runtime-environment.json are hashed from the source paths the workflow copies byte for byte',
             'no manual intervention'] + list(result.notes) + list(run.notes)
    if env_type is None:
        notes.append('environment_type absent from the provenance record: recorded as OTHER')
    m = {'campaign_id': CAMPAIGN, 'experiment_id': EXPERIMENT, 'sut_id': env.sut, 'timestamp': stamp(run.started),
         'sut_provenance': {'ecosystem_id': env.sut, 'components': components}, 'environment_type': env_type or 'OTHER',
         'platform': platform_name, 'scenario': SCENARIO, 'condition': env.condition, 'modality': modality, 'attempt': env.attempt,
         'outcome': {'status': result.status, 'expected': result.expected, 'observed': result.observed},
         'artifacts': arts, 'notes': run.scrub('; '.join(notes)), 'agent_role': AGENT_ROLE, 'prompt_version': env.prompt_version,
         'protocol_version': PROTOCOL_VERSION, 'run_id': env.run_id,
         'actions': [{k: a[k] for k in ('position', 'class', 'description', 'is_retry', 'outcome')} for a in run.actions],
         'target_state_id': SCENARIO, 'starting_state_id': 'CS-001-STARTING',
         'establishment_mechanisms': result.establishment_mechanisms or None, 'reset_mechanisms': result.reset_mechanisms,
         'behavior_class': None, 'toolchain': {k: v for k, v in run.tools.items() if isinstance(v, dict) and 'tool' in v},
         'environment': {'os': platform.platform(), 'runtime': f'python {platform.python_version()}'}}
    return m


def write_manifest(run, manifest):
    with open(os.path.join(run.out, 'run-manifest.json'), 'w', encoding='utf-8') as f:
        f.write(run.scrub(json.dumps(manifest, indent=2, ensure_ascii=False)))
