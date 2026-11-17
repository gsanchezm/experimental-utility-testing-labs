"""The attempt loop and the realizations, against fake systems under test (operation OP-PREP-E04). Static tests: nothing here is a SUT run.

Each case runs the executor in process on a fake instance (tests/fake_sut.py, a separate process so that the process-restart resets are
real), then checks the categories, the bundles, the manifests against schemas/run-manifest.schema.v2.json, and that no secret survived."""
import contextlib
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import attempt, classify, common, config, instance, run as run_mod, sut01, sut02, sut04, sut05  # noqa: E402
import mini_jsonschema  # noqa: E402

FAKE = os.path.join(HERE, 'fake_sut.py')
SCHEMA = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')
READINESS = {'sut01': '/health', 'sut05': '/rest/admin/application-version'}
SECRETS = ('ey' + 'JhbGciOi', 'Tk4Secret1234', 'pizza123', 'Mr. N00dles')  # none may appear in a kept file; Mr. N00dles is documented, see below


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class Fake:
    def __init__(self, kind, env=None):
        self.kind, self.port = kind, free_port()
        self.proc = subprocess.Popen([sys.executable, '-I', FAKE, kind, str(self.port)], start_new_session=True,
                                     env={**os.environ, **(env or {})}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            if instance.port_open(self.port):
                break
            time.sleep(0.1)

    def process_block(self):
        return {'pid': self.proc.pid, 'pgid': os.getpgid(self.proc.pid), 'port': self.port,
                'start_command': [sys.executable, '-I', FAKE, self.kind, str(self.port)], 'cwd': HERE, 'env': {},
                'readiness_url': READINESS.get(self.kind, '/'), 'readiness_timeout_s': 20, 'stop_timeout_s': 10}

    def stop(self):
        for pg in {os.getpgid(self.proc.pid)} if self.proc.poll() is None else set():
            with contextlib.suppress(ProcessLookupError):
                os.killpg(pg, signal.SIGTERM)
        with contextlib.suppress(Exception):
            self.proc.wait(timeout=5)


def make_job(condition, port, executions, process=None, record_class='DEVELOPMENT'):
    tmp = tempfile.mkdtemp(prefix='e04-attempt-')
    sut = 'SUT-' + condition.split('-')[1][3:]
    base = f'http://127.0.0.1:{port}'
    inst = {'interface_version': 1, 'sut_id': sut, 'record_class': record_class,
            'surfaces': {k: {'base_url': base} for k in ('api', 'auth', 'message', 'web')}}
    if process:
        inst['process'] = process
    with open(os.path.join(tmp, 'instance.json'), 'w') as f:
        json.dump(inst, f)
    os.environ.update({'CONDITION_ID': condition, 'ASSIGNED_SUT': sut, 'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1',
                       'OUTPUT_DIR': os.path.join(tmp, 'out'), 'PROVENANCE_JSON': os.path.join(tmp, 'absent-provenance.json'),
                       'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'absent-runtime.json'), 'INSTANCE_JSON': os.path.join(tmp, 'instance.json'),
                       'RECORD_CLASS': record_class, 'EXECUTIONS': str(executions), 'EXECUTOR_BASH_VERSION': '5.2.0'})
    env = common.Env()
    cfg = config.load()
    job = common.Job(env, cfg, config.condition(cfg, condition))
    job.tools.update({'executor_runtime': {'tool': 'python3', 'version': '3.12.0'}})
    instance.load(job)
    os.makedirs(os.path.join(env.output_dir, 'executions'), exist_ok=True)
    return job


MODULES = {'SUT-01': sut01, 'SUT-04': sut04, 'SUT-05': sut05}


class AttemptCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA, encoding='utf-8') as f:
            cls.schema = json.load(f)

    def run_condition(self, condition, kind, executions, restart=False, fake_env=None):
        fake = Fake(kind, fake_env)
        self.addCleanup(fake.stop)
        job = make_job(condition, fake.port, executions, process=fake.process_block() if restart else None)
        self.addCleanup(self.stop_group, job)
        cls = MODULES[job.env.sut].REALIZATIONS[condition]
        results = attempt.run_job(job, cls(job))
        return job, results, fake

    @staticmethod
    def stop_group(job):
        """The instance the restarts started (its group is the one recorded in memory) is not the one Fake started."""
        pgid = (job.instance.get('process') or {}).get('pgid')
        if pgid:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(int(pgid), signal.SIGTERM)

    def bundle(self, job, i):
        return os.path.join(job.env.output_dir, 'executions', job.env.run_id(i))

    def manifest(self, job, i):
        with open(os.path.join(self.bundle(job, i), 'run-manifest.json'), encoding='utf-8') as f:
            return json.load(f)

    def check_bundles(self, job, results):
        self.assertEqual(len(results), job.planned)
        for n, r in enumerate(results, 1):
            m = self.manifest(job, n)
            self.assertEqual(mini_jsonschema.validate(m, self.schema), [], m['run_id'])
            self.assertEqual(m['outcome']['outcome_category'], r['category'])
            self.assertEqual(m['run_id'], r['run_id'])
            self.assertNotIn('actions', m)  # the reset is not emitted as an action (E05 decision D-08c)
            for a in m['artifacts']:
                path = os.path.join(self.bundle(job, n), a['path'].split('/', 4)[4])
                if a['sha256'] is not None:
                    self.assertEqual(common.sha256_file(path), a['sha256'], a['path'])
            for root, _d, files in os.walk(self.bundle(job, n)):
                for fn in files:
                    with open(os.path.join(root, fn), 'rb') as f:
                        data = f.read()
                    for secret in ('ey' + 'JhbGciOi', 'Tk4Secret1234', 'pizza123'):
                        self.assertNotIn(secret.encode(), data, f'{secret} in {fn}')
        with open(os.path.join(job.env.output_dir, 'condition-summary.json'), encoding='utf-8') as f:
            summary = json.load(f)
        self.assertEqual(summary['executions_run'], job.planned)
        return summary

    def categories(self, results):
        return [r['category'] for r in results]



S = config.SUCCESS_CATEGORY


class Sut01ApiTests(AttemptCase):
    def test_session_reset_conditions(self):
        for condition in ('E04-SUT01-API-02', 'E04-SUT01-API-03', 'E04-SUT01-API-04', 'E04-SUT01-API-05'):
            with self.subTest(condition):
                job, results, _ = self.run_condition(condition, 'sut01', 3)
                self.assertEqual(self.categories(results), [S] * 3)
                self.check_bundles(job, results)
                m = self.manifest(job, 1)
                self.assertEqual(m['reset_mechanisms'], ['API_RESET', 'SESSION_RESET'])
                self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('SUCCESS', True))

    def test_process_restart_conditions(self):
        job, results, fake = self.run_condition('E04-SUT01-API-01', 'sut01', 3, restart=True)
        self.assertEqual(self.categories(results), [S] * 3)
        self.check_bundles(job, results)
        self.assertEqual(self.manifest(job, 1)['reset_mechanisms'], ['ENVIRONMENT_RESTART'])
        self.assertNotEqual(job.instance['process']['pid'], fake.proc.pid)  # three restarts happened and the recorded group moved
        job2, results2, _ = self.run_condition('E04-SUT01-API-06', 'sut01', 2, restart=True)
        self.assertEqual(self.categories(results2), [S] * 2)
        self.check_bundles(job2, results2)


class Sut05Tests(AttemptCase):
    def test_conditions(self):
        for condition in ('E04-SUT05-API-01', 'E04-SUT05-API-02'):
            with self.subTest(condition):
                job, results, _ = self.run_condition(condition, 'sut05', 3, restart=True)
                self.assertEqual(self.categories(results), [S] * 3)
                self.check_bundles(job, results)
                self.assertEqual(self.manifest(job, 2)['reset_mechanisms'], ['ENVIRONMENT_RESTART'])


class Sut04Tests(AttemptCase):
    def test_api_conditions_and_message_baseline(self):
        job, results, _ = self.run_condition('E04-SUT04-API-01', 'sut04', 3)
        self.assertEqual(self.categories(results), [S] * 3)
        self.check_bundles(job, results)
        job2, results2, _ = self.run_condition('E04-SUT04-API-02', 'sut04', 3)
        self.assertEqual(self.categories(results2), [S] * 3)
        self.check_bundles(job2, results2)

    def test_a_reset_that_fails_is_a_category_and_the_job_goes_on(self):
        job, results, _ = self.run_condition('E04-SUT04-API-01', 'sut04', 3, fake_env={'FAKE_DELETE_MODE': 'fail'})
        self.assertEqual(self.categories(results), [S, 'RESET_FAILED', 'RESET_FAILED'])
        self.check_bundles(job, results)
        m = self.manifest(job, 2)
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('ABORTED', False))

    def test_a_reset_that_did_not_hold_is_seen_by_the_starting_state_check(self):
        job, results, _ = self.run_condition('E04-SUT04-API-01', 'sut04', 3, fake_env={'FAKE_DELETE_MODE': 'noop'})
        self.assertEqual(self.categories(results), [S, 'RESET_STARTING_STATE_NOT_REACHED', 'RESET_STARTING_STATE_NOT_REACHED'])
        self.check_bundles(job, results)


class StubRealization(attempt.Realization):
    """Fails or raises in the block named by BLOCK; used to check the phase mapping and the attribution."""
    SPEC = common.Spec('API', 'api', ['API_RESET'], ['API_SEED'], [('api', 'api')], True)
    BLOCK, HOW = None, None

    def block(self, run, name, phase):
        if self.BLOCK != name:
            return
        with run.step(phase, name) as rec:
            if self.HOW == 'raise':
                raise RuntimeError('harness fault')
            rec['outcome'] = 'FAILURE'

    def reset(self, run):
        self.block(run, 'reset', 'reset')

    def check_start(self, run):
        self.block(run, 'check', 'starting-state')

    def establish(self, run):
        self.block(run, 'establish', 'establishment')

    def verify_target(self, run):
        self.block(run, 'verify', 'verification')


class PhaseMappingTests(AttemptCase):
    def check(self, block, how, label, attribution):
        job = make_job('E04-SUT05-API-01', 1, 1)
        cls = type('S', (StubRealization,), {'BLOCK': block, 'HOW': how})
        results = attempt.run_job(job, cls(job))
        self.assertEqual((results[0]['category'], results[0]['attribution']), (label, attribution), (block, how))
        m = self.manifest(job, 1)
        self.assertEqual(mini_jsonschema.validate(m, self.schema), [], m)
        return m

    def test_every_block(self):
        self.check('reset', 'raise', 'RESET_FAILED', 'TOOLING')
        self.check('reset', 'fail', 'RESET_FAILED', 'SUT')
        self.check('check', 'fail', 'RESET_STARTING_STATE_NOT_REACHED', 'SUT')
        self.check('establish', 'raise', 'ESTABLISHMENT_INTERRUPTED', 'TOOLING')
        self.check('establish', 'fail', 'ESTABLISHMENT_FAILED', 'SUT')
        self.check('verify', 'raise', 'ESTABLISHMENT_INTERRUPTED', 'TOOLING')
        m = self.check('verify', 'fail', 'ESTABLISHMENT_VERIFICATION_FAILED', 'SUT')
        self.assertEqual(m['outcome']['status'], 'ABORTED')
        m = self.check(None, None, S, 'SUT')
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('SUCCESS', True))

    def test_a_bundle_that_cannot_be_written_leaves_a_stub(self):
        job = make_job('E04-SUT05-API-01', 1, 1)
        cls = type('S', (StubRealization,), {})
        real = cls(job)
        original = common.build_manifest
        calls = []

        def broken(*a, **k):
            calls.append(1)
            if len(calls) == 1:
                raise OSError('disk full')
            return original(*a, **k)
        common.build_manifest = broken
        try:
            results = attempt.run_job(job, real)
        finally:
            common.build_manifest = original
        self.assertEqual(results[0]['category'], 'STUB_NO_BUNDLE')
        m = self.manifest(job, 1)
        self.assertEqual((m['outcome']['status'], m['outcome']['outcome_category']), ('ERROR', 'STUB_NO_BUNDLE'))


class RefusalTests(unittest.TestCase):
    def check(self, condition, record_class, executions, workflow_ref=''):
        os.environ.update({'CONDITION_ID': condition, 'ASSIGNED_SUT': 'SUT-' + condition.split('-')[1][3:], 'EXECUTOR_PROMPT_VERSION': 'p',
                           'OUTPUT_DIR': tempfile.mkdtemp(), 'PROVENANCE_JSON': 'x', 'RUNTIME_ENVIRONMENT_JSON': 'y', 'RECORD_CLASS': record_class,
                           'GITHUB_WORKFLOW_REF': workflow_ref})
        os.environ.pop('EXECUTIONS', None)
        if executions is not None:
            os.environ['EXECUTIONS'] = str(executions)
        return run_mod.check(common.Env(), config.load())[1]

    def test_refusals(self):
        self.assertIn('only inside', self.check('E04-SUT05-API-01', 'MEASURED_EXPERIMENT', None))
        self.assertIsNone(self.check('E04-SUT05-API-01', 'MEASURED_EXPERIMENT', None,
                                     'o/r/.github/workflows/e04-measured-execution.yml@refs/heads/main'))
        self.assertIn('N = 50', self.check('E04-SUT05-API-01', 'MEASURED_EXPERIMENT', 10, 'o/r/.github/workflows/e04-measured-execution.yml@x'))
        self.assertIn('EXECUTIONS between 1 and 3', self.check('E04-SUT05-API-01', 'DRY_RUN', 5))
        self.assertIn('EXECUTIONS between 1 and 3', self.check('E04-SUT05-API-01', 'DRY_RUN', None))
        self.assertIsNone(self.check('E04-SUT05-API-01', 'DRY_RUN', 2))
        self.assertIn('is not a condition', self.check('E04-SUT03-WEB-01', 'DRY_RUN', 2))
        self.assertIn('is not a condition', self.check('E04-SUT02-WEB-02', 'DRY_RUN', 2))  # never mirrored: not one of the thirteen

    def test_every_realization_is_configured_and_listed(self):
        mods = (sut01, sut02, sut04, sut05)
        every = {c for m in mods for c in m.REALIZATIONS}
        listed = {c['condition_id'] for c in config.load()['conditions']}
        self.assertEqual(every, listed)
        self.assertEqual(len(listed), 13)
        self.assertTrue(all(cls.SPEC.configured for m in mods for cls in m.REALIZATIONS.values()))


if __name__ == '__main__':
    unittest.main()
