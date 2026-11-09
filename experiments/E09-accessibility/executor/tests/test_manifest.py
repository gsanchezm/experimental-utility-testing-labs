"""The run manifest of an attempt conforms to schemas/run-manifest.schema.v2.json (checked with mini_jsonschema).

DRAFT (operation OP-PREP-E09). Builds one manifest per outcome class from a temporary bundle directory with the executor's own
common.build_manifest, then validates it against the schema. Also checks that the schema uses only supported keywords.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

from executor import common, config  # noqa: E402
import mini_jsonschema  # noqa: E402

SCHEMA = os.path.join(REPO, 'schemas', 'run-manifest.schema.v2.json')


def make_run(condition, run_id):
    tmp = tempfile.mkdtemp(prefix='e09-manifest-')
    out = os.path.join(tmp, run_id)
    env_vars = {'CONDITION_ID': condition, 'ASSIGNED_SUT': 'SUT-01', 'EXECUTION_ID': 'EX0001', 'ATTEMPT': '1',
                'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1', 'OUTPUT_DIR': out,
                'PROVENANCE_JSON': os.path.join(tmp, 'absent-provenance.json'),
                'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'absent-runtime.json'),
                'RECORD_CLASS': 'MEASURED_EXPERIMENT', 'AXE_TARBALL': os.path.join(tmp, 'absent.tgz'),
                'EXECUTOR_BASH_VERSION': '5.2.0'}
    os.environ.update(env_vars)
    env = common.Env()
    run = common.Run(env)
    return run


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA, encoding='utf-8') as f:
            cls.schema = json.load(f)

    def toolchain(self, version):
        return {'web_runner': {'tool': 'Playwright for Python', 'version': '1.63.0'},
                'browser': {'tool': 'Chromium', 'version': '000.0.0.0 (fixture)'},
                'executor_runtime': {'tool': 'python3', 'version': '3.12.0'},
                'scripting_runtime': {'tool': 'bash', 'version': '5.2.0'},
                'accessibility': {'tool': 'axe-core', 'version': version}}

    def components(self):
        return [{'component': 'web', 'repository': 'https://example.invalid/fixture', 'commit_sha_or_release': 'fixture-commit',
                 'endpoint': 'http://127.0.0.1:3000', 'environment_type': 'SELF_HOSTED'}]

    def check(self, result, condition, version):
        run = make_run(condition, f'{condition}__EX0001__A1')
        run.jsonfile('fixture', {'note': 'synthetic fixture'})
        run.close()
        m = common.build_manifest(run, result, self.components(), condition,
                                  config.CONDITIONS[condition]['behavior_class'], config.ROUTE_EVIDENCE, self.toolchain(version))
        errors = mini_jsonschema.validate(m, self.schema)
        self.assertEqual(errors, [], errors)
        self.assertEqual(m['modality'], 'Accessibility — Web only')
        self.assertNotIn('scenario', m)
        self.assertEqual(m['actions'], [])
        return m

    def test_schema_uses_only_supported_keywords(self):
        self.assertEqual(mini_jsonschema.unsupported_keywords(self.schema), set())

    def test_detected_glitch_manifest_conforms(self):
        common_result = common.Result('SUCCESS', 'DETECTED', 'expected text', 'observed text', True, notes=['fixture'])
        m = self.check(common_result, 'E09-A11Y-SUT01-MISSING-NAME', '4.14.0')
        self.assertEqual(m['outcome']['outcome_category'], 'DETECTED')
        self.assertEqual(m['behavior_class'], 'stochastic')

    def test_aborted_before_scan_manifest_conforms(self):
        r = common.Result('ABORTED', 'ABORTED_BEFORE_SCAN', 'expected', 'stopped', None)
        m = self.check(r, 'E09-CTRL-SUT01-STANDARD', None)
        self.assertIsNone(m['toolchain']['accessibility']['version'])

    def test_control_manifest_conforms(self):
        r = common.Result('SUCCESS', 'CONTROL_RULE_ABSENT', 'expected', 'observed', True)
        m = self.check(r, 'E09-CTRL-SUT01-STANDARD', '4.14.0')
        self.assertIsNone(m['behavior_class'])

    def test_validator_refuses_an_extra_outcome_key(self):
        r = common.Result('SUCCESS', 'DETECTED', 'e', 'o', True)
        run = make_run('E09-A11Y-SUT01-MISSING-NAME', 'E09-A11Y-SUT01-MISSING-NAME__EX0001__A1')
        run.close()
        m = common.build_manifest(run, r, self.components(), 'E09-A11Y-SUT01-MISSING-NAME', 'stochastic', [], self.toolchain('4.14.0'))
        m['outcome']['detail'] = 'not allowed'
        self.assertTrue(mini_jsonschema.validate(m, self.schema))


if __name__ == '__main__':
    unittest.main(verbosity=2)
