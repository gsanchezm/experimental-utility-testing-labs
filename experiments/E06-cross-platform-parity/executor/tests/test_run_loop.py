"""The execution loop of executor/run.py with fake drivers, the bundles it writes, the run manifests against schema v2, and the refusals.

DRAFT (operation OP-PREP-E06-EXECUTOR). No browser, no device, no network: a scripted driver returns observations built by the same
run.observation helper the real drivers use, so the bundle layout, the classification, and the manifest are the production code paths.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, EXEC)
sys.path.insert(0, HERE)

from executor import common, config, run  # noqa: E402
import mini_jsonschema  # noqa: E402

SCHEMA_PATH = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_schema():
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        return json.load(f)


class ScriptedDriver:
    """A driver that answers each execution from a script of (facts, identity) or a fault message."""

    def __init__(self, env, c, script):
        self.env, self.c, self.script = env, c, list(script)
        self.closed = False

    def run_one(self, run_obj):
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        facts = dict(item)
        return run.observation(run_obj, facts, self.c, self.env, screenshot=b'\x89PNG\r\n\x1a\nfake', dom='<html>fake</html>', extra={})

    def toolchain(self):
        return {'web_runner': {'tool': 'Playwright for Python', 'version': '1.63.0'}, 'executor_runtime': common.python_runtime()}

    def close(self):
        self.closed = True


def arrived_facts(identity='p02'):
    return {'surface': 'web', 'sut_id': 'SUT-01', 'arrived': True, 'identity': identity, 'identity_raw': f'pizza-name-{identity}-desktop',
            'sign_in_submitted': True, 'page_loaded': True, 'backend_observed': True, 'error_text': None, 'login_request_seen': True,
            'login_status': 200, 'catalogue_seen': True, 'catalogue_status': 200, 'steps': ['navigation', 'UI'], 'test_id_suffix': '-desktop'}


def refused_facts():
    return {'surface': 'web', 'sut_id': 'SUT-01', 'arrived': False, 'identity': None, 'sign_in_submitted': True, 'page_loaded': True,
            'backend_observed': True, 'error_text': 'Sorry, this user has been locked out.', 'login_request_seen': True, 'login_status': 403,
            'catalogue_seen': False, 'catalogue_status': None, 'steps': ['UI']}


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='e06-test-')
        self.prov = os.path.join(self.tmp, 'ci-provenance.json')
        self.rt = os.path.join(self.tmp, 'runtime-environment.json')
        with open(self.prov, 'w', encoding='utf-8') as f:
            json.dump({'environment_type': 'PUBLIC_HOSTED'}, f)
        with open(self.rt, 'w', encoding='utf-8') as f:
            json.dump({'runner': 'test'}, f)
        self.schema = load_schema()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def environ(self, **kw):
        base = {'CONDITION_ID': 'E06-CS007-SUT01-WEB', 'ATTEMPT': '1', 'RECORD_CLASS': 'DRY_RUN', 'EXPECTED_IDENTITY_ORACLE': 'item_identity',
                'OUTPUT_DIR': os.path.join(self.tmp, 'out'), 'PROVENANCE_JSON': self.prov, 'RUNTIME_ENVIRONMENT_JSON': self.rt,
                'EXECUTOR_PROMPT_VERSION': ''}
        base.update(kw)
        return base

    def test_a_dry_run_writes_three_bundles_each_with_a_valid_manifest_and_a_summary(self):
        env_map = self.environ()
        env, cfg, c, planned = run.prepare(env_map)
        scrub = common.Scrubber(env)
        scrub.secret('pizza123')
        driver = ScriptedDriver(env, c, [arrived_facts('p02'), refused_facts(), arrived_facts('p07')])
        summary = run.execute_condition(env, scrub, cfg, c, driver, planned)
        self.assertTrue(driver.closed)
        self.assertEqual(summary['executions_run'], 3)
        self.assertEqual(summary['categories'], {'ARRIVED_IDENTITY_READ': 2, 'NOT_ARRIVED_SUT': 1})
        self.assertEqual(summary['reasons'], {'SUT_SIGN_IN_REFUSED': 1})
        self.assertTrue(os.path.isfile(os.path.join(env.output_dir, 'condition-summary.json')))
        for k in (1, 2, 3):
            bundle = os.path.join(env.output_dir, f'E06-CS007-SUT01-WEB__EX{k:04d}__A1')
            manifest = read_json(os.path.join(bundle, 'run-manifest.json'))
            self.assertEqual(mini_jsonschema.validate(manifest, self.schema), [], f'execution {k}')
            self.assertEqual(manifest['environment_type'], 'PUBLIC_HOSTED')
            self.assertEqual(manifest['modality'], 'Web UI Functional')
            self.assertEqual(manifest['run_id'], f'E06-CS007-SUT01-WEB__EX{k:04d}__A1')
            self.assertIn('NON-MEASURED', manifest['notes'])
            self.assertTrue(os.path.isfile(os.path.join(bundle, 'executor.log')))

    def test_the_refused_execution_keeps_its_reason_and_outcome(self):
        env, cfg, c, planned = run.prepare(self.environ())
        scrub = common.Scrubber(env)
        driver = ScriptedDriver(env, c, [refused_facts(), arrived_facts('p02'), arrived_facts('p02')])
        run.execute_condition(env, scrub, cfg, c, driver, planned)
        manifest = read_json(os.path.join(env.output_dir, 'E06-CS007-SUT01-WEB__EX0001__A1', 'run-manifest.json'))
        self.assertEqual(manifest['outcome']['status'], 'FAILURE')
        self.assertEqual(manifest['outcome']['outcome_category'], 'NOT_ARRIVED_SUT')
        self.assertIn('reason=SUT_SIGN_IN_REFUSED', manifest['notes'])

    def test_a_runner_fault_is_an_error_bundle_attributed_to_tooling(self):
        env, cfg, c, planned = run.prepare(self.environ())
        scrub = common.Scrubber(env)
        driver = ScriptedDriver(env, c, [RuntimeError('browser closed unexpectedly'), arrived_facts(), arrived_facts()])
        summary = run.execute_condition(env, scrub, cfg, c, driver, planned)
        self.assertEqual(summary['categories'].get('NOT_ARRIVED_RUNNER'), 1)
        manifest = read_json(os.path.join(env.output_dir, 'E06-CS007-SUT01-WEB__EX0001__A1', 'run-manifest.json'))
        self.assertEqual(manifest['outcome']['status'], 'ERROR')
        self.assertEqual(mini_jsonschema.validate(manifest, self.schema), [])
        self.assertIn('runner_fault=RuntimeError', manifest['notes'])

    def test_the_arrival_only_switch_records_arrival_without_an_identity(self):
        # the locked configuration names arrival_only for this condition: a temporary copy of the draft with that one value changed
        with open(config.CONDITIONS_FILE, encoding='utf-8') as f:
            draft = json.load(f)
        draft['conditions'][0]['identity_oracle'] = 'arrival_only'
        conditions = os.path.join(self.tmp, 'conditions-arrival-only.json')
        with open(conditions, 'w', encoding='utf-8') as f:
            json.dump(draft, f)
        env, cfg, c, planned = run.prepare(self.environ(EXPECTED_IDENTITY_ORACLE='arrival_only', CONDITIONS_FILE=conditions))
        scrub = common.Scrubber(env)
        driver = ScriptedDriver(env, c, [arrived_facts('p02'), arrived_facts('p02'), arrived_facts('p02')])
        summary = run.execute_condition(env, scrub, cfg, c, driver, planned)
        self.assertEqual(summary['categories'], {'ARRIVED_ARRIVAL_ONLY': 3})
        self.assertTrue(all(r['identity'] is None for r in summary['executions']))

    def test_an_unreadable_identity_on_an_arrival_is_recorded_not_excluded(self):
        env, cfg, c, planned = run.prepare(self.environ())
        scrub = common.Scrubber(env)
        unreadable = arrived_facts(identity=None)
        driver = ScriptedDriver(env, c, [unreadable, arrived_facts('p02'), arrived_facts('p02')])
        summary = run.execute_condition(env, scrub, cfg, c, driver, planned)
        self.assertEqual(summary['categories'].get('ARRIVED_IDENTITY_UNREADABLE'), 1)
        self.assertEqual(summary['executions_run'], 3)

    def test_the_configuration_refusals_write_nothing(self):
        cases = [
            self.environ(ATTEMPT='2'),  # a non-measured record is attempt 1 only
            self.environ(ATTEMPT='0'),
            self.environ(FIRST_EXECUTION='0'),
            self.environ(FIRST_EXECUTION='51'),
            self.environ(FIRST_EXECUTION='17'),  # attempt 1 starts at execution 1
            self.environ(RECORD_CLASS='MEASURED_EXPERIMENT', EXECUTOR_PROMPT_VERSION='ORCHESTRATOR-E06-cross-platform-parity-v1', FIRST_EXECUTION='17'),
            self.environ(RECORD_CLASS='LOCAL'),
            self.environ(EXPECTED_IDENTITY_ORACLE='visual'),
            self.environ(EXPECTED_IDENTITY_ORACLE='arrival_only'),  # the configuration names item_identity for this condition
            self.environ(CONDITION_ID='E06-CS007-SUT09-WEB'),
        ]
        for env_map in cases:
            with self.assertRaises((run.ConfigurationRefused, config.ConfigError)):
                run.prepare(env_map)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'out', 'condition-summary.json')))

    def test_an_existing_summary_is_refused_because_attempts_are_immutable(self):
        env_map = self.environ()
        os.makedirs(os.path.join(self.tmp, 'out'), exist_ok=True)
        with open(os.path.join(self.tmp, 'out', 'condition-summary.json'), 'w', encoding='utf-8') as f:
            f.write('{}')
        with self.assertRaises(run.ConfigurationRefused):
            run.prepare(env_map)

    def test_measured_planned_count_is_fifty_with_a_frozen_prompt_version(self):
        env, cfg, c, planned = run.prepare(self.environ(RECORD_CLASS='MEASURED_EXPERIMENT', EXECUTOR_PROMPT_VERSION='ORCHESTRATOR-E06-cross-platform-parity-v1'))
        self.assertEqual(planned, 50)

    def test_a_further_attempt_runs_the_executions_from_the_first_one_it_names_and_its_bundles_carry_the_attempt(self):
        # the measured workflow admits attempt 2 only under a recorded approval (gate G-E06-A2); the executor runs executions FIRST_EXECUTION to N
        env_map = self.environ(RECORD_CLASS='MEASURED_EXPERIMENT', EXECUTOR_PROMPT_VERSION='ORCHESTRATOR-E06-cross-platform-parity-v1',
                               ATTEMPT='2', FIRST_EXECUTION='48')
        env, cfg, c, planned = run.prepare(env_map)
        self.assertEqual((env.attempt, env.first, planned), (2, 48, 50))
        scrub = common.Scrubber(env)
        driver = ScriptedDriver(env, c, [arrived_facts() for _ in range(3)])
        summary = run.execute_condition(env, scrub, cfg, c, driver, planned)
        self.assertEqual(summary['first_execution'], 48)
        self.assertEqual(summary['executions_planned'], 3)
        self.assertEqual(summary['executions_run'], 3)
        self.assertEqual(summary['attempt'], 2)
        self.assertEqual([e['execution_index'] for e in summary['executions']], [48, 49, 50])
        names = sorted(n for n in os.listdir(env.output_dir) if '__EX' in n)
        self.assertEqual(names, [f'E06-CS007-SUT01-WEB__EX00{i}__A2' for i in (48, 49, 50)])
        manifest = read_json(os.path.join(env.output_dir, names[0], 'run-manifest.json'))
        self.assertEqual(manifest['attempt'], 2)
        self.assertEqual(manifest['run_id'], names[0])
        self.assertEqual(mini_jsonschema.validate(manifest, self.schema), [])

    def test_a_measured_execution_without_a_prompt_version_is_refused(self):
        # repository rule 9: a null prompt version is allowed only for a human-executed run
        with self.assertRaises(run.ConfigurationRefused):
            run.prepare(self.environ(RECORD_CLASS='MEASURED_EXPERIMENT', EXECUTOR_PROMPT_VERSION=''))

    def test_a_harness_fault_that_did_not_let_the_execution_arrive_is_a_runner_fault(self):
        # the harness record of a failed session: app_started false, no arrival, a fault message (fixture of the Android harness record)
        env, cfg, c, planned = run.prepare(self.environ(CONDITION_ID='E06-CS007-SUT02-ANDROID'))
        scrub = common.Scrubber(env)
        harness_fixture = {'surface': 'android', 'sut_id': 'SUT-02', 'arrived': False, 'identity': None, 'sign_in_submitted': False,
                           'page_loaded': False, 'backend_observed': False, 'error_text': None, 'login_request_seen': False,
                           'login_status': None, 'catalogue_status': None, 'harness_fault': {'class': 'WebDriverError', 'message': 'POST /session: session not created'},
                           'steps': []}
        driver = ScriptedDriver(env, c, [harness_fixture])
        summary = run.execute_condition(env, scrub, cfg, c, driver, 1)
        self.assertEqual(summary['categories'], {'NOT_ARRIVED_RUNNER': 1})
        manifest = read_json(os.path.join(env.output_dir, 'E06-CS007-SUT02-ANDROID__EX0001__A1', 'run-manifest.json'))
        self.assertEqual(manifest['outcome']['status'], 'ERROR')
        self.assertIn('harness fault: WebDriverError: POST /session: session not created', manifest['notes'])

    def test_main_refuses_with_a_nonzero_status_and_no_bundle(self):
        status = run.main(self.environ(ATTEMPT='3'))
        self.assertEqual(status, 2)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'out', 'condition-summary.json')))


class ScrubberTests(unittest.TestCase):
    def test_secrets_tokens_host_paths_and_private_addresses_are_replaced(self):
        env, _cfg, _c, _p = run.prepare({'CONDITION_ID': 'E06-CS007-SUT01-WEB', 'ATTEMPT': '1', 'RECORD_CLASS': 'DRY_RUN',
                                         'EXPECTED_IDENTITY_ORACLE': 'item_identity', 'OUTPUT_DIR': tempfile.mkdtemp(prefix='e06-s-'),
                                         'PROVENANCE_JSON': '/nonexistent/p.json', 'RUNTIME_ENVIRONMENT_JSON': '/nonexistent/r.json'})
        scrub = common.Scrubber(env)
        scrub.secret('pizza123')
        # the fixture strings are assembled from parts: the public export refuses a private network address and a token-like fragment in any exported text file
        addr = '192.168' + '.1.20'
        jwt_head = 'eyJ' + 'hbGciOi'
        text = f'login pizza123 token {jwt_head}.' + 'eyJ' + 'zdWIiOi.c2ln' + f' at {env.executor_dir}/run.py from {addr}'
        out = scrub(text)
        self.assertNotIn('pizza123', out)
        self.assertNotIn(jwt_head, out)
        self.assertNotIn(env.executor_dir, out)
        self.assertTrue('<executor>/run.py' in out or '<cwd>/run.py' in out, out)
        self.assertNotIn(addr, out)
        self.assertIn('<private-address>', out)


if __name__ == '__main__':
    unittest.main()
