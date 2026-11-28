"""The attempt loop, the bundle and the run manifest, with a fake realization that opens no browser and runs no Node.js (operation OP-PREP-E10).

Static tests: nothing here is a SUT run. The fake realization returns prepared captures and comparisons for each execution, so the loop,
the categories, the attribution, the stub, the bundles and the manifests (checked against schemas/run-manifest.schema.v2.json) are
exercised. The real realizations are exercised only by the ENVIRONMENT_VERIFICATION DRY_RUN."""
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

from executor import attempt, common, compare, config, instance  # noqa: E402
import mini_jsonschema  # noqa: E402

SCHEMA = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')
SECRET = 'ey' + 'JhbGciOiJIUzI1NiJ9.' + 'ey' + 'JzdWIiOiJ4In0.c2lnbmF0dXJl'  # a fake token, built by concatenation so that no literal token prefix sits in the file
W, H = 1280, 800
N = W * H
BOXES = {'price': [(100, 300, 60, 20), (400, 300, 60, 20)], 'image': [(80, 100, 200, 200), (380, 100, 200, 200)]}
PNG = compare.encode_png_rgba(4, 3, bytes(range(48)))


def mask_for(boxes):
    m = bytearray(N)
    for x, y, w, h in boxes:
        for yy in range(y, y + h):
            m[yy * W + x:yy * W + x + w] = b'\x01' * w
    return m


def capture_record(view, role, ready=True, image_loaded=True):
    groups = {}
    for e in view['expected_elements']:
        items = BOXES[e['group']]
        groups[e['group']] = {'error': None, 'elements': [
            {'index': i, 'tag': 'x', 'box': {'x': x, 'y': y, 'w': w, 'h': h}, 'wholly_inside': True,
             'img': ({'complete': True, 'natural_width': 500 if image_loaded else 0, 'host': 'upload.wikimedia.org'} if e.get('image') else None)}
            for i, (x, y, w, h) in enumerate(items)]}
    return {'view_id': view['view_id'], 'role': role, 'ready_ok': ready, 'missing_ready': [] if ready else ['first_item'], 'timed_ok': None,
            'elements': {'groups': groups}, 'png': PNG, 'png_sha256': 'x', 'png_size': [4, 3], 'label': f'{view["view_id"]}-{role}'}


def comparison(mask):
    d = mask.count(1)
    return {'dimension_mismatch': False, 'width': W, 'height': H, 'compared': N, 'differing': d, 'ratio': d / N, 'mask': bytes(mask), 'diff_png': PNG}


class FakeSut01(attempt.Realization):
    """Behaves like the SUT-01 realization without a browser. `script` maps the execution index to a behavior."""
    SPEC = common.Spec('Visual Testing', 'web', [('web', 'web'), ('api', 'api')], True)
    script = {}

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

    def method(self, run):
        mode = self.script.get(self.index)
        self.begin_measurement(run)
        if mode == 'boom':
            raise RuntimeError('the fake browser crashed')
        run.scrub.secret(SECRET)
        run.text('capture-note', f'token {SECRET}')
        view = self.job.c['views'][0]
        all_boxes = BOXES['price'] + BOXES['image']
        ab = comparison(mask_for(all_boxes))
        if mode == 'not_detected':
            ab = comparison(mask_for([]))
        caps = {r: capture_record(view, r, image_loaded=(mode != 'external' or r != 'A')) for r in ('A', 'B', 'A2')}
        if mode == 'missing':
            caps['B'] = capture_record(view, 'B', ready=False)
        run.binary('catalog-A-capture', PNG, 'png')
        run.binary('catalog-AB-diff', PNG, 'png')
        return [{'view': view, 'captures': caps, 'AB': None if mode == 'missing' else ab, 'AA2': comparison(bytearray(N))}]


def make_job(executions, script, first=1, attempt_no=1, record_class='DEVELOPMENT'):
    tmp = tempfile.mkdtemp(prefix='e10-attempt-')
    inst = {'interface_version': 1, 'sut_id': 'SUT-01', 'record_class': record_class,
            'surfaces': {'web': {'base_url': 'http://127.0.0.1:3000'}, 'api': {'base_url': 'http://127.0.0.1:8000'}},
            'provisioning': {'repository': 'https://example.invalid/r', 'commit_sha': 'a' * 40, 'release': None}, 'process': None, 'logs': []}
    with open(os.path.join(tmp, 'instance.json'), 'w') as f:
        json.dump(inst, f)
    os.environ.update({'CONDITION_ID': 'E10-SUT01-WEB-PROBLEM', 'ASSIGNED_SUT': 'SUT-01', 'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1',
                       'OUTPUT_DIR': os.path.join(tmp, 'out'), 'PROVENANCE_JSON': os.path.join(tmp, 'absent-provenance.json'),
                       'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'absent-runtime.json'), 'INSTANCE_JSON': os.path.join(tmp, 'instance.json'),
                       'RECORD_CLASS': record_class, 'EXECUTIONS': str(executions), 'FIRST_EXECUTION': str(first), 'ATTEMPT': str(attempt_no),
                       'EXECUTOR_BASH_VERSION': '5.2.0'})
    env = common.Env()
    cfg = config.load()
    job = common.Job(env, cfg, config.condition(cfg, 'E10-SUT01-WEB-PROBLEM'))
    job.tools.update({'executor_runtime': {'tool': 'python3', 'version': '3.12.0'}, 'visual': {'tool': 'Playwright viewport screenshots compared with Pixelmatch', 'version': '8.0.0'}})
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

    def evidence(self, job, i, suffix):
        d = os.path.join(self.bundle(job, i), 'evidence')
        names = [f for f in sorted(os.listdir(d)) if f.endswith(suffix)]
        self.assertEqual(len(names), 1, (suffix, names))
        return os.path.join(d, names[0])

    def run_job(self, executions, script, **kw):
        job = make_job(executions, script, **kw)
        results = attempt.run_job(job, FakeSut01(job))
        return job, results

    def test_categories_manifests_bundles_and_summary(self):
        job, results = self.run_job(7, {2: 'not_detected', 3: 'missing', 4: 'surface', 5: 'boom', 6: 'external'})
        self.assertEqual([r['category'] for r in results],
                         ['DETECTED', 'NOT_DETECTED', 'INCONCLUSIVE_READY_SIGNAL_MISSING', 'START_SURFACE_NOT_READY', 'INTERRUPTED_',
                          'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED', 'DETECTED'])
        self.assertEqual([r['attribution'] for r in results], ['SUT', 'SUT', 'SUT', 'SUT', 'SUT', 'EXTERNAL', 'SUT'])  # an exception after the first measured capture began is the SUT's
        for n, r in enumerate(results, 1):
            m = self.manifest(job, n)
            self.assertEqual(mini_jsonschema.validate(m, self.schema), [], m['run_id'])
            self.assertEqual((m['campaign_id'], m['modality'], m['platform'], m['condition']), ('E10-visual', 'Visual Testing', 'web', 'E10-SUT01-WEB-PROBLEM'))
            self.assertEqual(m['outcome']['outcome_category'], r['category'])
            self.assertEqual(m['behavior_class'], 'external dependency')
            self.assertIsNone(m['reset_mechanisms'])
            self.assertIsNone(m['establishment_mechanisms'])
            for absent in ('actions', 'scenario'):
                self.assertNotIn(absent, m)
            self.assertEqual(m['toolchain']['visual']['version'], '8.0.0')
            for a in m['artifacts']:
                if a['sha256'] is not None:
                    self.assertEqual(common.sha256_file(os.path.join(self.bundle(job, n), a['path'].split('/', 4)[4])), a['sha256'], a['path'])
            for root, _d, files in os.walk(self.bundle(job, n)):
                for fn in files:
                    with open(os.path.join(root, fn), 'rb') as f:
                        self.assertNotIn(SECRET.encode(), f.read(), fn)
        # the first execution: detection, the two comparison records, the instrument record and the provisional thresholds
        with open(self.evidence(job, 1, 'detection.json'), encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual((d['detected'], d['baseline_false_positive'], d['thresholds']['provisional']), (True, False, True))
        self.assertNotIn('AB', d['views'][0])
        with open(self.evidence(job, 1, 'catalog-AB-comparison.json'), encoding='utf-8') as f:
            ab = json.load(f)
        self.assertEqual((ab['pair'], ab['detected'], len(ab['elements'])), ('A against B', True, 4))
        with open(self.evidence(job, 1, 'catalog-AA2-comparison.json'), encoding='utf-8') as f:
            self.assertFalse(json.load(f)['false_positive'])
        with open(self.evidence(job, 1, 'instrument.json'), encoding='utf-8') as f:
            instrument = json.load(f)
        self.assertEqual((instrument['capture_version'], instrument['pixelmatch_version'], instrument['thresholds']['provisional']), ('e10-capture-v1', '8.0.0', True))
        self.assertEqual(self.manifest(job, 2)['outcome']['status'], 'FAILURE')
        self.assertEqual(self.manifest(job, 3)['outcome']['status'], 'INCONCLUSIVE')
        self.assertEqual(self.manifest(job, 4)['outcome']['status'], 'ABORTED')
        self.assertEqual(self.manifest(job, 5)['outcome']['status'], 'ERROR')
        self.assertEqual(self.manifest(job, 6)['outcome']['status'], 'INCONCLUSIVE')
        with open(os.path.join(job.env.output_dir, 'condition-summary.json'), encoding='utf-8') as f:
            summary = json.load(f)
        self.assertEqual((summary['executions_run'], summary['categories']['DETECTED'], summary['categories']['NOT_DETECTED']), (7, 2, 1))
        self.assertEqual(summary['category_by_attribution']['INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED|EXTERNAL'], 1)

    def test_a_further_attempt_uses_absolute_indexes(self):
        job, results = self.run_job(5, {}, first=4, attempt_no=2)
        self.assertEqual([r['run_id'] for r in results], [f'E10-SUT01-WEB-PROBLEM__DV{i:04d}__A2' for i in (4, 5)])

    def test_an_exception_before_the_first_measured_capture_is_tooling(self):
        class Early(FakeSut01):
            def method(self, run):
                raise RuntimeError('the context could not be created')
        job = make_job(1, {})
        results = attempt.run_job(job, Early(job))
        self.assertEqual((results[0]['category'], results[0]['attribution']), ('INTERRUPTED_', 'TOOLING'))  # the first measured navigation was never started

        class Pre(FakeSut01):
            def check_start(self, run):
                with run.step('starting-state', 'x'):
                    raise RuntimeError('the surface check crashed')
        job = make_job(1, {})
        results = attempt.run_job(job, Pre(job))
        self.assertEqual((results[0]['category'], results[0]['attribution']), ('INTERRUPTED_', 'TOOLING'))

    def test_an_activation_that_is_not_confirmed_is_a_recorded_start_category(self):
        class Refused(FakeSut01):
            def method(self, run):
                raise common.PhaseFailure('method', 'the login of problem_user did not reach the catalogue', label='START_ACTIVATION_NOT_CONFIRMED')
        job = make_job(1, {})
        results = attempt.run_job(job, Refused(job))
        self.assertEqual(results[0]['category'], 'START_ACTIVATION_NOT_CONFIRMED')
        self.assertEqual(self.manifest(job, 1)['outcome']['status'], 'ABORTED')

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

    def test_the_real_realization_hooks_are_the_documented_ones(self):
        for name in ('check_start', 'activate'):
            with self.assertRaises(NotImplementedError):
                getattr(attempt.Realization(make_job(1, {})), name)(None, None, None, None) if name == 'activate' else getattr(attempt.Realization(make_job(1, {})), name)(None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
