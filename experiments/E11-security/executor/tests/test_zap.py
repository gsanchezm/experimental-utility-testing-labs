"""zap.py against a fake ZAP API (operation OP-PREP-E11). Static tests: no container starts, no real ZAP is contacted."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

import signal  # noqa: E402
import time  # noqa: E402

from executor import common, zap  # noqa: E402
from fake_zap import FakeLauncher, FakeZap  # noqa: E402


class StubScrub:
    def __init__(self):
        self.secrets = []

    def secret(self, v):
        self.secrets.append(v)


class StubRun:
    def __init__(self):
        self.scrub, self.sent, self.texts = StubScrub(), 0, []

    def mark_stimulus_sent(self):
        self.sent += 1

    def text(self, name, content, ext='txt'):
        self.texts.append((name, content))
        return f'evidence/{name}.{ext}'


SPEC = {'rule_id': '40018', 'seed_request': {'method': 'GET', 'url': 'http://127.0.0.1:3000/rest/products/search?q=apple', 'body': None},
        'scan_target': {'method': 'GET', 'url': 'http://127.0.0.1:3000/rest/products/search?q=apple', 'body': None}}
LOGIN_SPEC = {'rule_id': '40018',
              'seed_request': {'method': 'POST', 'url': 'http://127.0.0.1:3000/rest/user/login', 'body': '{"email": "u@example.org"}', 'content_type': 'application/json'},
              'scan_target': {'method': 'POST', 'url': 'http://127.0.0.1:3000/rest/user/login', 'body': '{"email": "u@example.org"}'}}


def alert(rule, method, url, name='SQL Injection'):
    return {'pluginId': rule, 'alert': name, 'method': method, 'url': url, 'param': 'q', 'attack': "'", 'evidence': 'x'}


class MatchTests(unittest.TestCase):
    def test_normalized_path_ignores_query_host_and_fragment_but_keeps_the_trailing_slash(self):
        self.assertEqual(zap.normalize_path('http://127.0.0.1:3000/rest/products/search?q=x%27%20OR#frag'), '/rest/products/search')
        self.assertEqual(zap.normalize_path('http://other:9/ftp/'), '/ftp/')
        self.assertNotEqual(zap.normalize_path('http://h/ftp'), zap.normalize_path('http://h/ftp/'))

    def test_only_rule_method_and_path_together_are_counted(self):
        alerts = [alert('40018', 'GET', 'http://h/rest/products/search?q=a%27'),   # counted
                  alert('40018', 'POST', 'http://h/rest/products/search'),          # wrong method
                  alert('40019', 'GET', 'http://h/rest/products/search?q=a'),       # wrong rule
                  alert('40018', 'GET', 'http://h/rest/user/security-question?email=x'),  # wrong path
                  alert(40018, 'GET', 'http://h/rest/products/search?q=b')]         # rule id as a number: still the same rule
        counted, others = zap.match_alerts(alerts, '40018', 'GET', '/rest/products/search')
        self.assertEqual(len(counted), 2)
        self.assertEqual(len(others), 3)
        self.assertTrue(all(o['path'] for o in others))

    def test_no_alert_is_no_detection(self):
        self.assertEqual(zap.match_alerts([], '0', 'GET', '/ftp/'), ([], []))


class RunScanTests(unittest.TestCase):
    def run_scan(self, fake, spec=SPEC, launcher=None, scan_timeout_s=3, ready_timeout_s=3):
        self.addCleanup(fake.close)
        run, rec = StubRun(), {'evidence': []}
        launcher = launcher or FakeLauncher(fake)
        try:
            obs = zap.run_scan(run, rec, launcher, spec, ready_timeout_s=ready_timeout_s, scan_timeout_s=scan_timeout_s, sleep=lambda s: None)
        except zap.ZapError as e:
            return run, rec, launcher, e
        return run, rec, launcher, obs

    def test_a_scan_returns_alerts_versions_and_equal_addon_lists(self):
        fake = FakeZap([alert('40018', 'GET', 'http://127.0.0.1:3000/rest/products/search?q=a%27')])
        run, rec, launcher, obs = self.run_scan(fake)
        self.assertEqual(obs['zap_version'], '2.17.0')
        self.assertEqual(len(obs['alerts']), 1)
        self.assertTrue(obs['addons_unchanged'])
        self.assertEqual(obs['addons_before'], ['ascanrules@84', 'pscanrules@77'])
        self.assertEqual((launcher.started, launcher.stopped), (1, 1))
        self.assertEqual(run.sent, 1)  # the boundary is marked once, before the seed request
        self.assertTrue(run.scrub.secrets and run.scrub.secrets[0] == launcher.key)

    def test_the_policy_enables_exactly_the_rule_and_the_scan_is_not_recursive(self):
        fake = FakeZap()
        self.run_scan(fake)
        self.assertEqual(fake.called('ascan/action/enableScanners')[0]['ids'], '40018')
        self.assertEqual(len(fake.called('ascan/action/disableAllScanners')), 1)
        scan = fake.called('ascan/action/scan')[0]
        self.assertEqual((scan['recurse'], scan['inScopeOnly']), ('false', 'false'))
        self.assertEqual(scan['url'], SPEC['scan_target']['url'])
        self.assertEqual(scan['scanPolicyName'], zap.POLICY_NAME)

    def test_a_post_target_carries_its_method_and_body_and_the_seed_is_a_raw_request(self):
        fake = FakeZap()
        self.run_scan(fake, LOGIN_SPEC)
        scan = fake.called('ascan/action/scan')[0]
        self.assertEqual((scan['method'], scan['postData']), ('POST', '{"email": "u@example.org"}'))
        raw = fake.called('core/action/sendRequest')[0]['request']
        self.assertTrue(raw.startswith('POST http://127.0.0.1:3000/rest/user/login HTTP/1.1\r\nHost: 127.0.0.1:3000\r\n'))
        self.assertIn('Content-Length: 26', raw)

    def test_every_call_carries_the_api_key_of_the_execution(self):
        fake = FakeZap()
        run, rec, launcher, obs = self.run_scan(fake)
        self.assertTrue(all(q.get('apikey') == launcher.key for _parts, q in fake.calls))

    def test_a_changed_addon_list_is_reported_not_hidden(self):
        fake = FakeZap(behavior='addons-change')
        _run, _rec, _l, obs = self.run_scan(fake)
        self.assertFalse(obs['addons_unchanged'])

    def test_a_failed_start_is_ZAP_START_FAILED(self):
        fake = FakeZap()
        _run, _rec, launcher, err = self.run_scan(fake, launcher=FakeLauncher(fake, fail_start=True))
        self.assertIsInstance(err, zap.ZapError)
        self.assertEqual(err.code, 'ZAP_START_FAILED')
        self.assertEqual(launcher.stopped, 1)  # the stop runs even when the start failed

    def test_an_api_that_never_answers_is_ZAP_START_FAILED(self):
        fake = FakeZap()
        fake.close()  # the port refuses connections
        run, rec = StubRun(), {'evidence': []}
        with self.assertRaises(zap.ZapError) as cm:
            zap.run_scan(run, rec, FakeLauncher(fake), SPEC, ready_timeout_s=0.3, sleep=lambda s: None)
        self.assertEqual(cm.exception.code, 'ZAP_START_FAILED')

    def test_an_http_error_of_the_api_is_ZAP_API_ERROR(self):
        _run, _rec, launcher, err = self.run_scan(FakeZap(behavior='api-error'))
        self.assertEqual(err.code, 'ZAP_API_ERROR')
        self.assertEqual(launcher.stopped, 1)

    def test_a_missing_scan_id_is_ZAP_API_ERROR(self):
        _run, _rec, _l, err = self.run_scan(FakeZap(behavior='no-scan-id'))
        self.assertEqual(err.code, 'ZAP_API_ERROR')

    def test_a_scan_that_never_finishes_is_ZAP_SCAN_TIMEOUT_and_the_container_is_stopped(self):
        _run, _rec, launcher, err = self.run_scan(FakeZap(behavior='never-finishes'), scan_timeout_s=0.3)
        self.assertEqual(err.code, 'ZAP_SCAN_TIMEOUT')
        self.assertEqual(launcher.stopped, 1)


class SettingsAndWatchdogTests(RunScanTests):
    def test_the_scan_settings_are_recorded_and_only_the_one_rule_is_enabled(self):
        _run, _rec, _l, obs = self.run_scan(FakeZap())
        rows = obs['policy_enabled_scanners']
        self.assertEqual([r['id'] for r in rows], ['40018'])  # the disabled row of the fake is not listed
        self.assertEqual((rows[0]['attackStrength'], rows[0]['alertThreshold']), ('MEDIUM', 'MEDIUM'))
        self.assertIn('target_params_injectable', obs)
        self.assertIn('max_scan_duration_mins', obs)

    def test_an_unreadable_option_view_is_recorded_and_does_not_fail_the_run(self):
        _run, _rec, _l, obs = self.run_scan(FakeZap(behavior='options-unreadable'))
        self.assertIn('unreadable', obs['target_params_injectable'])
        self.assertTrue(obs['addons_unchanged'])

    def test_the_policy_is_created_without_tuning_parameters(self):
        fake = FakeZap()
        self.run_scan(fake)
        self.assertEqual(set(fake.called('ascan/action/addScanPolicy')[0]), {'scanPolicyName', 'apikey'})  # release defaults of strength and threshold

    def test_the_watchdog_is_not_turned_into_a_zap_error_and_the_container_is_still_stopped(self):
        fake = FakeZap()
        self.addCleanup(fake.close)

        class Boom:
            def open(self, *a, **k):
                raise common.Watchdog('budget')
        original = zap.Api._opener
        zap.Api._opener = Boom()
        self.addCleanup(setattr, zap.Api, '_opener', original)
        launcher = FakeLauncher(fake)
        with self.assertRaises(common.Watchdog):
            zap.run_scan(StubRun(), {'evidence': []}, launcher, SPEC, ready_timeout_s=3, scan_timeout_s=3, sleep=lambda s: None)
        self.assertEqual(launcher.stopped, 1)

    def test_an_alarm_during_a_scan_that_never_finishes_surfaces_as_the_watchdog(self):
        fake = FakeZap(behavior='never-finishes')
        self.addCleanup(fake.close)

        def handler(signum, frame):
            raise common.Watchdog('budget')
        old = signal.signal(signal.SIGALRM, handler)
        self.addCleanup(signal.signal, signal.SIGALRM, old)
        launcher = FakeLauncher(fake)
        signal.setitimer(signal.ITIMER_REAL, 0.4)
        try:
            with self.assertRaises(common.Watchdog):
                zap.run_scan(StubRun(), {'evidence': []}, launcher, SPEC, ready_timeout_s=3, scan_timeout_s=60, sleep=lambda s: time.sleep(0.05))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        self.assertEqual(launcher.stopped, 1)

    def test_the_execution_budget_exceeds_the_sum_of_the_m2_budgets(self):
        self.assertGreater(common.WATCHDOG_S, 180 + 30 + zap.READY_TIMEOUT_S + zap.SCAN_TIMEOUT_S)


class LauncherTests(unittest.TestCase):
    def test_the_image_is_addressed_by_digest_and_the_pin_is_route_a(self):
        self.assertIn('@sha256:c2d63bbb2d907a5c5257914fb20e26e969c92b25f265def7f89f08203f912882', zap.ZAP_IMAGE)
        self.assertEqual(zap.ZAP_RELEASE, '2.17.0')
        with self.assertRaises(ValueError):
            zap.DockerLauncher(image='ghcr.io/zaproxy/zaproxy:2.17.0')  # a tag is not a pin

    def test_the_container_command_turns_update_checks_off_and_never_updates_add_ons(self):
        import inspect
        src = inspect.getsource(zap.DockerLauncher.start)
        self.assertIn('start.checkForUpdates=false', src)
        self.assertNotIn('addonupdate', src)


if __name__ == '__main__':
    unittest.main(verbosity=2)
