"""The attempt loop and the realizations, against fake systems under test (operation OP-PREP-E11). Static tests: nothing here is a SUT run.

Each case runs the executor in process on a fake instance (tests/fake_sut.py, a separate process so that the process-restart resets are real)
and, for M2, a fake ZAP API (tests/fake_zap.py), then checks the categories, the bundles, the manifests against schemas/run-manifest.schema.v2.json,
and that no secret survived."""
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

from executor import attempt, common, config, instance, sut01, sut05, zap  # noqa: E402
import mini_jsonschema  # noqa: E402
from fake_zap import FakeLauncher, FakeZap  # noqa: E402

FAKE = os.path.join(HERE, 'fake_sut.py')
SCHEMA = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')
READINESS = {'sut01': '/health', 'sut05': '/rest/admin/application-version'}
SECRETS = ('ey' + 'JhbGciOi', 'pizza123')  # the Juice Shop documented account password (Mr. N00dles) is public and kept as the E05 evidence keeps it


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

    def process_block(self, env=None):
        return {'pid': self.proc.pid, 'pgid': os.getpgid(self.proc.pid), 'port': self.port,
                'start_command': [sys.executable, '-I', FAKE, self.kind, str(self.port)], 'cwd': HERE, 'env': env or {},
                'readiness_url': READINESS[self.kind], 'readiness_timeout_s': 20, 'stop_timeout_s': 10}

    def stop(self):
        if self.proc.poll() is None:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        with contextlib.suppress(Exception):
            self.proc.wait(timeout=5)


def make_job(cell_id, port, executions, process=None, record_class='DEVELOPMENT'):
    tmp = tempfile.mkdtemp(prefix='e11-attempt-')
    sut = 'SUT-' + cell_id.split('-')[1][3:]
    base = f'http://127.0.0.1:{port}'
    inst = {'interface_version': 1, 'sut_id': sut, 'record_class': record_class, 'surfaces': {'api': {'base_url': base}}, 'process': process}
    with open(os.path.join(tmp, 'instance.json'), 'w') as f:
        json.dump(inst, f)
    os.environ.update({'CELL_ID': cell_id, 'ASSIGNED_SUT': sut, 'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1',
                       'OUTPUT_DIR': os.path.join(tmp, 'out'), 'PROVENANCE_JSON': os.path.join(tmp, 'absent-provenance.json'),
                       'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'absent-runtime.json'), 'INSTANCE_JSON': os.path.join(tmp, 'instance.json'),
                       'RECORD_CLASS': record_class, 'EXECUTIONS': str(executions), 'EXECUTOR_BASH_VERSION': '5.2.0'})
    env = common.Env()
    cfg = config.load()
    job = common.Job(env, cfg, config.cell(cfg, cell_id))
    job.tools.update({'executor_runtime': {'tool': 'python3', 'version': '3.12.0'}})
    instance.load(job)
    os.makedirs(os.path.join(env.output_dir, 'executions'), exist_ok=True)
    return job


MODULES = {'SUT-01': sut01, 'SUT-05': sut05}


class AttemptCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA, encoding='utf-8') as f:
            cls.schema = json.load(f)

    def run_cell(self, cell_id, executions, fake_env=None, zap_fake=None, zap_launcher=None):
        kind = 'sut01' if cell_id.startswith('E11-SUT01') else 'sut05'
        fake = Fake(kind, fake_env)
        self.addCleanup(fake.stop)
        job = make_job(cell_id, fake.port, executions, process=fake.process_block(fake_env))  # the switches survive the restarts
        self.addCleanup(self.stop_group, job)
        cls = MODULES[job.env.sut].REALIZATIONS[cell_id]
        if zap_fake is not None:
            self.addCleanup(zap_fake.close)
            launcher = zap_launcher or FakeLauncher(zap_fake)
            cls = type('Patched', (cls,), {'LAUNCHER_FACTORY': staticmethod(lambda: launcher)})
            self.launcher = launcher
        results = attempt.run_job(job, cls(job))
        return job, results

    @staticmethod
    def stop_group(job):
        pgid = (job.instance.get('process') or {}).get('pgid')
        if pgid:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(int(pgid), signal.SIGTERM)

    def bundle(self, job, i):
        return os.path.join(job.env.output_dir, 'executions', job.env.run_id(i))

    def manifest(self, job, i):
        with open(os.path.join(self.bundle(job, i), 'run-manifest.json'), encoding='utf-8') as f:
            return json.load(f)

    def attempt_record(self, job, i):
        with open(os.path.join(self.bundle(job, i), 'attempt-record.json'), encoding='utf-8') as f:
            return json.load(f)

    def check_bundles(self, job, results):
        self.assertEqual(len(results), job.planned)
        for n, r in enumerate(results, 1):
            m = self.manifest(job, n)
            self.assertEqual(mini_jsonschema.validate(m, self.schema), [], m['run_id'])
            self.assertEqual(m['outcome']['outcome_category'], r['category'])
            self.assertEqual((m['campaign_id'], m['modality'], m['platform']), ('E11-security', 'Security Testing', 'api'))
            self.assertEqual(m['experiment_id'], job.env.condition)
            for absent in ('actions', 'scenario'):
                self.assertNotIn(absent, m)
            self.assertIsNone(m['behavior_class'])
            for a in m['artifacts']:
                path = os.path.join(self.bundle(job, n), a['path'].split('/', 4)[4])
                if a['sha256'] is not None:
                    self.assertEqual(common.sha256_file(path), a['sha256'], a['path'])
            for root, _d, files in os.walk(self.bundle(job, n)):
                for fn in files:
                    if 'process-tree' in fn:
                        continue  # the host process list (ps) is host-dependent: the command line that started this test may itself hold a test string
                    with open(os.path.join(root, fn), 'rb') as f:
                        data = f.read()
                    for secret in SECRETS:
                        self.assertNotIn(secret.encode(), data, f'{secret} in {fn}')
        with open(os.path.join(job.env.output_dir, 'condition-summary.json'), encoding='utf-8') as f:
            summary = json.load(f)
        self.assertEqual(summary['executions_run'], job.planned)
        return summary

    def categories(self, results):
        return [r['category'] for r in results]


class M1Sut05Tests(AttemptCase):
    def test_login_injection_flips_the_oracle_in_every_execution_from_a_fresh_instance(self):
        job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M1', 3)
        self.assertEqual(self.categories(results), ['M1_ORACLE_FLIPPED'] * 3)  # the solved flag of one execution does not leak into the next
        summary = self.check_bundles(job, results)
        self.assertEqual(summary['categories'], {'M1_ORACLE_FLIPPED': 3})
        m = self.manifest(job, 1)
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('SUCCESS', True))
        self.assertEqual(m['reset_mechanisms'], ['ENVIRONMENT_RESTART'])

    def test_the_search_union_and_the_ftp_sequences_flip_their_own_challenge_only(self):
        for cell in ('E11-SUT05-SQLI-SEARCH-M1', 'E11-SUT05-DIRLIST-FTP-M1'):
            job, results = self.run_cell(cell, 2)
            self.assertEqual(self.categories(results), ['M1_ORACLE_FLIPPED'] * 2, cell)
            self.check_bundles(job, results)

    def test_the_controls_do_not_flip_the_oracle(self):
        for cell in ('E11-SUT05-SQLI-LOGIN-M1-CTRL', 'E11-SUT05-SQLI-SEARCH-M1-CTRL', 'E11-SUT05-DIRLIST-FTP-M1-CTRL'):
            job, results = self.run_cell(cell, 2)
            self.assertEqual(self.categories(results), ['M1_ORACLE_NOT_FLIPPED'] * 2, cell)
            m = self.manifest(job, 1)
            self.assertTrue(m['outcome']['matches_expected'], cell)
            self.check_bundles(job, results)

    def test_a_condition_whose_oracle_never_moves_is_a_non_detection_not_an_error(self):
        job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M1', 2, fake_env={'FAKE_NO_FLIP': '1'})
        self.assertEqual(self.categories(results), ['M1_ORACLE_NOT_FLIPPED'] * 2)
        m = self.manifest(job, 1)
        self.assertEqual((m['outcome']['status'], m['outcome']['matches_expected']), ('SUCCESS', False))

    def test_an_oracle_that_answers_500_is_M1_RESPONSE_OTHER_after_a_starting_state_that_cannot_be_read(self):
        # the starting-state check reads the same oracle: an unreadable oracle stops the execution before the method
        job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M1', 1, fake_env={'FAKE_ORACLE_500': '1'})
        self.assertEqual(self.categories(results), ['RESET_STARTING_STATE_NOT_REACHED'])
        m = self.manifest(job, 1)
        self.assertEqual(m['outcome']['status'], 'ABORTED')

    def test_a_reset_that_did_not_hold_stops_the_execution_with_its_category(self):
        job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M1', 2, fake_env={'FAKE_SOLVED_AT_START': '1'})
        self.assertEqual(self.categories(results), ['RESET_STARTING_STATE_NOT_REACHED'] * 2)
        self.assertEqual(self.attempt_record(job, 1)['attribution'], 'SUT')  # a recorded observation, not an exception: uncertain goes to SUT (E05 D-16)
        self.check_bundles(job, results)


class IdorTests(AttemptCase):
    def test_the_security_glitch_requester_reads_the_other_users_order(self):
        job, results = self.run_cell('E11-SUT01-IDOR-ORDER-M1', 2)
        self.assertEqual(self.categories(results), ['M1_IDOR_BYPASS_OBSERVED'] * 2)
        self.check_bundles(job, results)
        rec = self.attempt_record(job, 1)
        self.assertEqual([s['phase'] for s in rec['steps']], ['reset', 'starting-state', 'method', 'classification'])

    def test_the_standard_user_control_is_blocked(self):
        job, results = self.run_cell('E11-SUT01-IDOR-ORDER-M1-CTRL', 2)
        self.assertEqual(self.categories(results), ['M1_IDOR_BLOCKED'] * 2)
        self.assertTrue(self.manifest(job, 1)['outcome']['matches_expected'])
        self.check_bundles(job, results)

    def test_a_fixed_system_shows_the_condition_cell_as_blocked(self):
        job, results = self.run_cell('E11-SUT01-IDOR-ORDER-M1', 1, fake_env={'FAKE_IDOR_FIXED': '1'})
        self.assertEqual(self.categories(results), ['M1_IDOR_BLOCKED'])
        self.assertFalse(self.manifest(job, 1)['outcome']['matches_expected'])


class M2Sut05Tests(AttemptCase):
    def login_alert(self, rule='40018', method='POST', path='/rest/user/login'):
        return {'pluginId': rule, 'alert': 'SQL Injection', 'method': method, 'url': f'http://127.0.0.1:3000{path}', 'param': 'email'}

    def test_an_expected_alert_is_a_detection_and_the_tool_is_recorded(self):
        z = FakeZap([self.login_alert(), self.login_alert('10020', 'GET', '/')])
        job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M2', 2, zap_fake=z)
        self.assertEqual(self.categories(results), ['M2_EXPECTED_ALERT'] * 2)
        self.check_bundles(job, results)
        self.assertEqual(self.launcher.started, 2)  # a fresh container for every execution
        self.assertEqual(self.launcher.stopped, 2)
        tools = json.load(open(os.path.join(self.bundle(job, 1), 'tool-versions.json')))
        self.assertEqual(tools['security'], {'tool': 'OWASP ZAP', 'version': '2.17.0'})
        self.assertEqual(self.manifest(job, 1)['toolchain']['security_image']['version'], zap.ZAP_AMD64_MANIFEST)
        self.assertIn('1 other alert(s) not counted', self.manifest(job, 1)['outcome']['observed'])
        step = [s for s in self.attempt_record(job, 1)['steps'] if s['phase'] == 'method'][0]
        self.assertEqual(step['observation']['addons_before'], ['ascanrules@84', 'pscanrules@77'])  # the lists the pin record needs are kept
        self.assertTrue(step['observation']['addons_unchanged'])

    def test_other_alerts_alone_are_not_a_detection(self):
        z = FakeZap([self.login_alert('10020', 'GET', '/'), self.login_alert('40018', 'GET', '/rest/user/login')])  # wrong rule; wrong method
        job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M2', 1, zap_fake=z)
        self.assertEqual(self.categories(results), ['M2_NO_EXPECTED_ALERT'])
        self.assertFalse(self.manifest(job, 1)['outcome']['matches_expected'])

    def test_the_search_condition_counts_an_alert_with_a_payload_in_the_query(self):
        z = FakeZap([{'pluginId': '40018', 'alert': 'SQL Injection', 'method': 'GET', 'url': "http://127.0.0.1:3000/rest/products/search?q=a'+OR+1%3D1--", 'param': 'q'}])
        _job, results = self.run_cell('E11-SUT05-SQLI-SEARCH-M2', 1, zap_fake=z)
        self.assertEqual(self.categories(results), ['M2_EXPECTED_ALERT'])
        scan = z.called('ascan/action/scan')[0]
        self.assertTrue(scan['url'].endswith('/rest/products/search?q=apple'))
        self.assertEqual(z.called('ascan/action/enableScanners')[0]['ids'], '40018')

    def test_the_directory_condition_uses_rule_0_on_the_slash_path_and_a_miss_is_recorded(self):
        z = FakeZap([])  # the predicted outcome (V-7): no alert
        _job, results = self.run_cell('E11-SUT05-DIRLIST-FTP-M2', 1, zap_fake=z)
        self.assertEqual(self.categories(results), ['M2_NO_EXPECTED_ALERT'])
        self.assertEqual(z.called('ascan/action/enableScanners')[0]['ids'], '0')
        self.assertTrue(z.called('ascan/action/scan')[0]['url'].endswith('/ftp/'))

    def test_the_directory_condition_counts_rule_0_on_ftp(self):
        z = FakeZap([{'pluginId': '0', 'alert': 'Directory Browsing', 'method': 'GET', 'url': 'http://127.0.0.1:3000/ftp/', 'param': ''}])
        _job, results = self.run_cell('E11-SUT05-DIRLIST-FTP-M2', 1, zap_fake=z)
        self.assertEqual(self.categories(results), ['M2_EXPECTED_ALERT'])

    def test_a_control_counts_the_same_rule_on_its_own_endpoint_only(self):
        # an alert of rule 40018 on the control endpoint is a false positive (the control expects none); on the condition's endpoint it is not counted
        on_control = {'pluginId': '40018', 'alert': 'SQL Injection', 'method': 'GET', 'url': 'http://127.0.0.1:3000/rest/user/security-question?email=x%27', 'param': 'email'}
        z = FakeZap([on_control])
        _job, results = self.run_cell('E11-SUT05-SQLI-SEARCH-M2-CTRL', 1, zap_fake=z)
        self.assertEqual(self.categories(results), ['M2_EXPECTED_ALERT'])  # the label names the match; kind CONTROL expects the negative one
        self.assertFalse(self.manifest(_job, 1)['outcome']['matches_expected'])
        z2 = FakeZap([{'pluginId': '40018', 'alert': 'SQL Injection', 'method': 'GET', 'url': 'http://127.0.0.1:3000/rest/products/search?q=x', 'param': 'q'}])
        job2, results2 = self.run_cell('E11-SUT05-SQLI-SEARCH-M2-CTRL', 1, zap_fake=z2)
        self.assertEqual(self.categories(results2), ['M2_NO_EXPECTED_ALERT'])
        self.assertTrue(self.manifest(job2, 1)['outcome']['matches_expected'])
        self.assertTrue(z2.called('ascan/action/scan')[0]['url'].startswith('http://127.0.0.1:' + z2.called('ascan/action/scan')[0]['url'].split(':')[2].split('/')[0] + '/rest/user/security-question'))

    def test_the_login_control_posts_to_api_users_not_to_the_rate_limited_endpoint(self):
        z = FakeZap([])
        _job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M2-CTRL', 1, zap_fake=z)
        scan = z.called('ascan/action/scan')[0]
        self.assertTrue(scan['url'].endswith('/api/Users'))
        self.assertEqual(scan['method'], 'POST')
        self.assertEqual(self.categories(results), ['M2_NO_EXPECTED_ALERT'])

    def test_zap_failures_are_recorded_categories_with_tooling_attribution_and_the_job_goes_on(self):
        for behavior, code in (('api-error', 'ZAP_API_ERROR'), ('no-scan-id', 'ZAP_API_ERROR')):
            z = FakeZap(behavior=behavior)
            job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M2', 2, zap_fake=z)
            self.assertEqual(self.categories(results), [code] * 2, behavior)
            self.assertEqual({r['attribution'] for r in results}, {'TOOLING'})
            self.assertEqual(self.manifest(job, 1)['outcome']['status'], 'ERROR')
            self.check_bundles(job, results)

    def test_a_failed_start_is_ZAP_START_FAILED(self):
        z = FakeZap()
        _job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M2', 1, zap_fake=z, zap_launcher=FakeLauncher(z, fail_start=True))
        self.assertEqual(self.categories(results), ['ZAP_START_FAILED'])
        self.assertEqual(results[0]['attribution'], 'TOOLING')

    def test_no_zap_key_survives_in_the_bundle(self):
        z = FakeZap([self.login_alert()])
        job, results = self.run_cell('E11-SUT05-SQLI-LOGIN-M2', 1, zap_fake=z)
        key = self.launcher.key
        for root, _d, files in os.walk(self.bundle(job, 1)):
            for fn in files:
                with open(os.path.join(root, fn), 'rb') as f:
                    self.assertNotIn(key.encode(), f.read(), fn)


if __name__ == '__main__':
    unittest.main(verbosity=2)
