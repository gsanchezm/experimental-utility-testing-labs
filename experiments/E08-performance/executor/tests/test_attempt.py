"""The attempt loop, the bundle and the run manifest, with a fake realization that opens no browser (operation OP-PREP-E08).

Static tests: nothing here is a SUT run. The fake realization returns prepared snapshots for the three loads of each execution, so the loop, the
load order, the categories, the attribution, the stub, the bundles and the manifests (checked against schemas/run-manifest.schema.v2.json)
are exercised. The real realizations are exercised only by the ENVIRONMENT_VERIFICATION DRY_RUN."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import attempt, common, config, instance  # noqa: E402
import mini_jsonschema  # noqa: E402

SCHEMA = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')
SUPPORTED = ['largest-contentful-paint', 'layout-shift', 'longtask', 'paint']
SECRET = 'ey' + 'JhbGciOiJIUzI1NiJ9.' + 'ey' + 'JzdWIiOiJ4In0.c2lnbmF0dXJl'  # a fake token, built by concatenation so that no literal token prefix sits in the file


def snap(first_item):
    return {'supported': SUPPORTED, 'ready': {'first_item': first_item} if first_item is not None else {}, 'lcp': [], 'cls': [], 'longtasks': [],
            'final_url': 'http://127.0.0.1:3000/catalog'}


class FakeSut01(attempt.Realization):
    """Behaves like the SUT-01 realization without a browser. `script` maps the execution index to a behavior."""
    SPEC = common.Spec('Performance', 'web', [('web', 'web'), ('api', 'api')], True)
    script = {}
    seen_orders = []

    def open(self):
        pass

    def bind(self, run):
        self.carry = {}
        self.index = run.index

    def close(self):
        pass

    def check_start(self, run):
        mode = self.script.get(self.index)
        with run.step('starting-state', 'fake surface check') as rec:
            rec['observation'] = {'web_status': 200}
            if mode == 'surface':
                raise common.PhaseFailure('starting-state', 'a surface did not answer 200', label='START_SURFACE_NOT_READY')

    def load(self, run, role):
        mode = self.script.get(self.index)
        self.begin_measurement(run)
        if mode == 'boom' and role == 'Ba':
            raise RuntimeError('the fake browser crashed')
        run.scrub.secret(SECRET)
        run.text(f'{self.next_label(role)}-note', f'token {SECRET}')
        t = {'D': 3600.0, 'Ba': 480.0, 'Bb': 500.0}[role]
        if mode == 'not_detected' and role == 'D':
            t = 700.0
        if mode == 'missing' and role == 'D':
            return {'role': role, 'account': 'x', 'page': '/catalog', 'snapshot': snap(None)}
        return {'role': role, 'account': 'x', 'page': '/catalog', 'snapshot': snap(t)}


def make_job(executions, script, first=1, attempt_no=1, record_class='DEVELOPMENT'):
    tmp = tempfile.mkdtemp(prefix='e08-attempt-')
    inst = {'interface_version': 1, 'sut_id': 'SUT-01', 'record_class': record_class,
            'surfaces': {'web': {'base_url': 'http://127.0.0.1:3000'}, 'api': {'base_url': 'http://127.0.0.1:8000'}},
            'provisioning': {'repository': 'https://example.invalid/r', 'commit_sha': 'a' * 40, 'release': None}, 'process': None, 'logs': []}
    with open(os.path.join(tmp, 'instance.json'), 'w') as f:
        json.dump(inst, f)
    os.environ.update({'CONDITION_ID': 'E08-SUT01-WEB-DELAY', 'ASSIGNED_SUT': 'SUT-01', 'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1',
                       'OUTPUT_DIR': os.path.join(tmp, 'out'), 'PROVENANCE_JSON': os.path.join(tmp, 'absent-provenance.json'),
                       'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'absent-runtime.json'), 'INSTANCE_JSON': os.path.join(tmp, 'instance.json'),
                       'RECORD_CLASS': record_class, 'EXECUTIONS': str(executions), 'FIRST_EXECUTION': str(first), 'ATTEMPT': str(attempt_no),
                       'EXECUTOR_BASH_VERSION': '5.2.0'})
    env = common.Env()
    cfg = config.load()
    job = common.Job(env, cfg, config.condition(cfg, 'E08-SUT01-WEB-DELAY'))
    job.tools.update({'executor_runtime': {'tool': 'python3', 'version': '3.12.0'}})
    instance.load(job)
    os.makedirs(os.path.join(env.output_dir, 'executions'), exist_ok=True)
    FakeSut01.script = script
    return job


class AttemptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA, encoding='utf-8') as f:
            cls.schema = json.load(f)

    def bundle(self, job, i):
        return os.path.join(job.env.output_dir, 'executions', job.env.run_id(i))

    def manifest(self, job, i):
        with open(os.path.join(self.bundle(job, i), 'run-manifest.json'), encoding='utf-8') as f:
            return json.load(f)

    def run_job(self, executions, script, **kw):
        job = make_job(executions, script, **kw)
        results = attempt.run_job(job, FakeSut01(job))
        return job, results

    def test_categories_orders_manifests_and_summary(self):
        job, results = self.run_job(8, {2: 'not_detected', 3: 'missing', 4: 'surface', 5: 'boom'})
        self.assertEqual([r['category'] for r in results],
                         ['DETECTED', 'NOT_DETECTED', 'INCONCLUSIVE_READY_SIGNAL_MISSING', 'START_SURFACE_NOT_READY', 'INTERRUPTED_', 'DETECTED', 'DETECTED', 'DETECTED'])
        self.assertEqual([r['attribution'] for r in results][3:5], ['SUT', 'SUT'])  # an exception after the first measured load began is the SUT's (D-16, uncertain goes to SUT)
        for n, r in enumerate(results, 1):
            m = self.manifest(job, n)
            self.assertEqual(mini_jsonschema.validate(m, self.schema), [], m['run_id'])
            self.assertEqual((m['campaign_id'], m['modality'], m['platform'], m['condition']), ('E08-performance', 'Performance', 'web', 'E08-SUT01-WEB-DELAY'))
            self.assertEqual(m['outcome']['outcome_category'], r['category'])
            self.assertEqual(m['behavior_class'], 'deterministic')
            self.assertIsNone(m['reset_mechanisms'])
            self.assertIsNone(m['establishment_mechanisms'])
            for absent in ('actions', 'scenario'):
                self.assertNotIn(absent, m)
            self.assertIn('performance', m['toolchain'] if 'performance' in m['toolchain'] else {'performance': 1})
            for a in m['artifacts']:
                if a['sha256'] is not None:
                    self.assertEqual(common.sha256_file(os.path.join(self.bundle(job, n), a['path'].split('/', 4)[4])), a['sha256'], a['path'])
            for root, _d, files in os.walk(self.bundle(job, n)):
                for fn in files:
                    with open(os.path.join(root, fn), 'rb') as f:
                        self.assertNotIn(SECRET.encode(), f.read(), fn)
        # the detection record of the first execution names the order and the values
        with open(os.path.join(self.bundle(job, 1), 'evidence', [f for f in os.listdir(os.path.join(self.bundle(job, 1), 'evidence')) if f.endswith('detection.json')][0]), encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual((d['order'], d['detected'], d['baseline_false_positive']), (['D', 'Ba', 'Bb'], True, False))
        self.assertEqual(self.manifest(job, 2)['outcome']['status'], 'FAILURE')
        self.assertEqual(self.manifest(job, 4)['outcome']['status'], 'ABORTED')
        self.assertEqual(self.manifest(job, 5)['outcome']['status'], 'ERROR')
        with open(os.path.join(job.env.output_dir, 'condition-summary.json'), encoding='utf-8') as f:
            summary = json.load(f)
        self.assertEqual((summary['executions_run'], summary['categories']['DETECTED'], summary['categories']['NOT_DETECTED']), (8, 4, 1))

    def test_the_first_execution_of_a_further_attempt_keeps_the_load_schedule(self):
        job, results = self.run_job(5, {}, first=4, attempt_no=2)
        self.assertEqual([r['run_id'] for r in results], [f'E08-SUT01-WEB-DELAY__DV{i:04d}__A2' for i in (4, 5)])
        for n in (4, 5):
            order = config.order_for(job.cfg, n)
            with open(os.path.join(self.bundle(job, n), 'evidence', [f for f in os.listdir(os.path.join(self.bundle(job, n), 'evidence')) if f.endswith('detection.json')][0]), encoding='utf-8') as f:
                self.assertEqual(json.load(f)['order'], list(order))

    def test_an_exception_before_the_first_measured_load_is_tooling(self):
        class Early(FakeSut01):
            def load(self, run, role):
                raise RuntimeError('the context could not be created')
        job = make_job(1, {})
        results = attempt.run_job(job, Early(job))
        self.assertEqual((results[0]['category'], results[0]['attribution']), ('INTERRUPTED_', 'TOOLING'))  # the first measured navigation was never started
        # an exception in the starting-state block is tooling as well
        class Pre(FakeSut01):
            def check_start(self, run):
                with run.step('starting-state', 'x'):
                    raise RuntimeError('the surface check crashed')
        job = make_job(1, {})
        results = attempt.run_job(job, Pre(job))
        self.assertEqual((results[0]['category'], results[0]['attribution']), ('INTERRUPTED_', 'TOOLING'))

    def test_a_bundle_that_cannot_be_written_leaves_a_stub(self):
        job = make_job(1, {})
        real = FakeSut01(job)
        calls = {'n': 0}
        original = common.build_manifest

        def flaky(*a, **k):
            calls['n'] += 1
            if calls['n'] == 1:
                raise OSError('disk full')
            return original(*a, **k)
        common.build_manifest = flaky
        try:
            results = attempt.run_job(job, real)
        finally:
            common.build_manifest = original
        self.assertEqual(results[0]['category'], 'STUB_NO_BUNDLE')
        self.assertEqual(mini_jsonschema.validate(self.manifest(job, 1), self.schema), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
