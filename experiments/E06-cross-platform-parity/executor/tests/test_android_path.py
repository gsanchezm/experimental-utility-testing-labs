"""The Android path end to end: AndroidExecutor -> android.run_harness -> the real Node harness -> the fake WebDriver server (a child process).

DRAFT (operation OP-PREP-E06-EXECUTOR). Only the device and the Appium server are replaced: a stub adb answers the uninstall, a temporary
APK file stands in for the release (its SHA-256 is written into a temporary copy of the conditions file), and the fake server of
harness/tests/fake_appium.mjs answers the WebDriver commands. The production run loop writes the bundle and the run manifest, which is
validated against schema v2. Skipped when the node binary is not available.
"""
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
HARNESS_TESTS = os.path.abspath(os.path.join(EXEC, '..', 'harness', 'tests'))
sys.path.insert(0, EXEC)
sys.path.insert(0, HERE)

from executor import common, config, run  # noqa: E402
import mini_jsonschema  # noqa: E402

NODE = shutil.which('node')
SCHEMA = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class FakeServer:
    """The fake WebDriver server as a child process; its URL is read from its first output line."""

    def __init__(self, **options):
        args = [NODE, os.path.join(HARNESS_TESTS, 'serve_fake.mjs')]
        for key, value in options.items():
            args.append(f'--{key}={value}')
        self.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        line = self.proc.stdout.readline().strip()
        if not line.startswith('URL '):
            err = self.proc.stderr.read()
            raise RuntimeError(f'the fake server did not start: {err[:500]}')
        self.url = line.split(' ', 1)[1]

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=20)
        except Exception:  # noqa: BLE001 - the child is stopped in any case
            self.proc.kill()


@unittest.skipIf(NODE is None, 'node is not available')
class AndroidPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='e06-android-path-')
        self.apk = os.path.join(self.tmp, 'apk', 'fixture.apk')
        os.makedirs(os.path.dirname(self.apk))
        with open(self.apk, 'wb') as f:
            f.write(b'fixture bytes standing in for the release APK (never installed)')
        with open(self.apk, 'rb') as fh:
            self.apk_sha = hashlib.sha256(fh.read()).hexdigest()
        self.adb = os.path.join(self.tmp, 'adb')
        with open(self.adb, 'w', encoding='utf-8') as f:
            f.write('#!/bin/sh\necho Success\nexit 0\n')
        os.chmod(self.adb, os.stat(self.adb).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        with open(config.CONDITIONS_FILE, encoding='utf-8') as f:
            draft = json.load(f)
        for c in draft['conditions']:
            if c['surface'] == 'ANDROID':
                c['apk']['sha256'] = self.apk_sha
                c['apk']['file'] = os.path.basename(self.apk)
        self.conditions = os.path.join(self.tmp, 'conditions.json')
        with open(self.conditions, 'w', encoding='utf-8') as f:
            json.dump(draft, f)
        self.servers = []

    def tearDown(self):
        for s in self.servers:
            s.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def server(self, **options):
        s = FakeServer(**options)
        self.servers.append(s)
        return s

    def environ(self, condition, server, out):
        return {'CONDITION_ID': condition, 'ATTEMPT': '1', 'RECORD_CLASS': 'DRY_RUN', 'EXPECTED_IDENTITY_ORACLE': 'item_identity',
                'OUTPUT_DIR': out, 'PROVENANCE_JSON': os.path.join(self.tmp, 'p.json'), 'RUNTIME_ENVIRONMENT_JSON': os.path.join(self.tmp, 'r.json'),
                'EXECUTOR_PROMPT_VERSION': '', 'CONDITIONS_FILE': self.conditions, 'APK_PATH': self.apk, 'APPIUM_SERVER_URL': server.url,
                'ANDROID_UDID': 'emulator-5554', 'ADB_BIN': self.adb, 'NODE_BIN': NODE, 'EXECUTOR_DIR': EXEC,
                'HARNESS_DIR': os.path.abspath(os.path.join(EXEC, '..', 'harness'))}

    def run_one(self, condition, server, out):
        env, cfg, c, planned = run.prepare(self.environ(condition, server, out))
        scrub = common.Scrubber(env)
        driver = run.make_driver(env, cfg, c, scrub)
        summary = run.execute_condition(env, scrub, cfg, c, driver, 1)
        bundle = os.path.join(out, f'{condition}__EX0001__A1')
        manifest = read_json(os.path.join(bundle, 'run-manifest.json'))
        return summary, manifest, bundle

    def assert_schema(self, manifest):
        schema = read_json(SCHEMA)
        self.assertEqual(mini_jsonschema.validate(manifest, schema), [])

    def test_sut01_android_arrives_and_reads_the_first_card_identity_through_the_real_harness(self):
        server = self.server(sut='SUT-01', **{'sign-in': 'ok', 'cards': 'p07,p02'})
        out = os.path.join(self.tmp, 'out-sut01')
        summary, manifest, bundle = self.run_one('E06-CS007-SUT01-ANDROID', server, out)
        self.assertEqual(summary['categories'], {'ARRIVED_IDENTITY_READ': 1})
        self.assertEqual(summary['executions'][0]['identity'], 'p07')
        self.assert_schema(manifest)
        self.assertEqual(manifest['platform'], 'android')
        self.assertEqual(manifest['modality'], 'Android Native')
        self.assertEqual(manifest['environment_type'], 'PUBLIC_HOSTED')
        self.assertEqual(manifest['outcome']['status'], 'SUCCESS')
        self.assertTrue(os.path.isfile(os.path.join(bundle, 'evidence')) or os.path.isdir(os.path.join(bundle, 'evidence')))
        kept = ' '.join(os.path.join(root, f) for root, _d, files in os.walk(bundle) for f in files)
        self.assertIn('page-source', kept)  # the page source is kept for the replay of the identity read

    def test_sut02_android_arrives_and_reads_the_first_title_through_the_real_harness(self):
        server = self.server(sut='SUT-02', **{'sign-in': 'ok', 'titles': 'Sauce Labs Backpack|Sauce Labs Bike Light'})
        out = os.path.join(self.tmp, 'out-sut02')
        summary, manifest, _bundle = self.run_one('E06-CS007-SUT02-ANDROID', server, out)
        self.assertEqual(summary['categories'], {'ARRIVED_IDENTITY_READ': 1})
        self.assertEqual(summary['executions'][0]['identity'], 'Sauce Labs Backpack')
        self.assert_schema(manifest)
        self.assertEqual(manifest['environment_type'], 'EMULATED')

    def test_sut02_android_without_the_logout_row_after_the_sign_in_is_a_non_arrival_of_the_system(self):
        # decision D-E06-13: the catalogue is displayed before any sign-in, so the drawer row Logout Menu Item is the second signal of a session
        server = self.server(sut='SUT-02', **{'sign-in': 'ok', 'logout': 'absent', 'titles': 'Sauce Labs Backpack|Sauce Labs Bike Light'})
        out = os.path.join(self.tmp, 'out-nosession')
        summary, manifest, _bundle = self.run_one('E06-CS007-SUT02-ANDROID', server, out)
        self.assertEqual(summary['categories'], {'NOT_ARRIVED_SUT': 1})
        self.assertEqual(summary['reasons'], {'SUT_SIGN_IN_REFUSED': 1})
        self.assertEqual(summary['category_by_attribution'], {'NOT_ARRIVED_SUT|SUT': 1})
        self.assertEqual(summary['executions'][0]['identity'], None)
        self.assertEqual(manifest['outcome']['status'], 'FAILURE')
        self.assert_schema(manifest)

    def test_sut02_android_that_loses_its_session_while_the_logout_row_is_searched_is_a_runner_fault(self):
        server = self.server(sut='SUT-02', **{'sign-in': 'ok', 'logout': 'absent', 'source-fails-when-menu-open': '1'})
        out = os.path.join(self.tmp, 'out-lost')
        summary, manifest, _bundle = self.run_one('E06-CS007-SUT02-ANDROID', server, out)
        self.assertEqual(summary['categories'], {'NOT_ARRIVED_RUNNER': 1})
        self.assertEqual(manifest['outcome']['status'], 'ERROR')

    def test_the_sut02_android_account_is_the_account_of_sut02_web(self):
        conditions = {c['condition_id']: c for c in json.load(open(config.CONDITIONS_FILE, encoding='utf-8'))['conditions']}
        self.assertEqual(config.credentials(conditions['E06-CS007-SUT02-ANDROID']), config.credentials(conditions['E06-CS007-SUT02-WEB']))
        self.assertEqual(config.credentials(conditions['E06-CS007-SUT02-ANDROID'])[0], 'standard_user')

    def test_a_backend_user_limit_is_an_infrastructure_non_arrival_with_its_message(self):
        server = self.server(sut='SUT-01', **{'sign-in': 'error', 'error-text': 'Too many users'})
        out = os.path.join(self.tmp, 'out-limit')
        summary, manifest, _bundle = self.run_one('E06-CS007-SUT01-ANDROID', server, out)
        self.assertEqual(summary['categories'], {'NOT_ARRIVED_INFRASTRUCTURE': 1})
        self.assertEqual(summary['reasons'], {'INFRA_USER_LIMIT_429': 1})
        self.assertEqual(manifest['outcome']['status'], 'ABORTED')
        self.assert_schema(manifest)

    def test_a_session_that_cannot_be_created_is_a_runner_fault_with_the_harness_message(self):
        server = self.server(sut='SUT-02', **{'fail-session': '1'})
        out = os.path.join(self.tmp, 'out-session')
        summary, manifest, _bundle = self.run_one('E06-CS007-SUT02-ANDROID', server, out)
        self.assertEqual(summary['categories'], {'NOT_ARRIVED_RUNNER': 1})
        self.assertEqual(manifest['outcome']['status'], 'ERROR')
        self.assertIn('harness fault', manifest['notes'])
        self.assert_schema(manifest)

    def test_the_password_never_appears_in_a_kept_file(self):
        server = self.server(sut='SUT-01', **{'sign-in': 'ok', 'cards': 'p07'})
        out = os.path.join(self.tmp, 'out-secret')
        _summary, _manifest, bundle = self.run_one('E06-CS007-SUT01-ANDROID', server, out)
        for root, _d, files in os.walk(bundle):
            for name in files:
                if name.endswith(('.png', '.gz')):
                    continue
                with open(os.path.join(root, name), 'rb') as f:
                    self.assertNotIn(b'pizza123', f.read(), name)


if __name__ == '__main__':
    unittest.main()
