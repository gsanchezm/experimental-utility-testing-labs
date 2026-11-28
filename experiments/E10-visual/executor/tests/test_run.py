"""The entry checks of executor.run and the registry of realizations (operation OP-PREP-E10). Static tests: no browser, no SUT."""
import copy
import importlib
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import common, config, run  # noqa: E402

CFG = config.load()


def env_for(condition, sut, record_class, executions=None, first=1, attempt=1):
    tmp = tempfile.mkdtemp(prefix='e10-run-')
    os.environ.pop('EXECUTIONS', None)
    os.environ.update({'CONDITION_ID': condition, 'ASSIGNED_SUT': sut, 'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1', 'OUTPUT_DIR': os.path.join(tmp, 'out'),
                       'PROVENANCE_JSON': os.path.join(tmp, 'p.json'), 'RUNTIME_ENVIRONMENT_JSON': os.path.join(tmp, 'r.json'), 'RECORD_CLASS': record_class,
                       'FIRST_EXECUTION': str(first), 'ATTEMPT': str(attempt)})
    if executions is not None:
        os.environ['EXECUTIONS'] = str(executions)
    return common.Env()


class CheckTests(unittest.TestCase):
    def check(self, *a, **k):
        env = env_for(*a, **k)
        return run.check(env, CFG)

    def test_every_condition_has_a_configured_realization_of_its_sut(self):
        for c in CFG['conditions']:
            mod = importlib.import_module(f'executor.{run.MODULES[c["sut_id"]]}')
            cls = mod.REALIZATIONS[c['condition_id']]
            self.assertTrue(cls.SPEC.configured)
            self.assertEqual((cls.SPEC.modality, cls.SPEC.platform), ('Visual Testing', 'web'))

    def test_a_dry_run_is_bounded_and_a_measured_run_needs_the_workflow_and_calibrated_thresholds(self):
        c, problem = self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'DRY_RUN', executions=3)
        self.assertIsNone(problem)
        self.assertEqual(c['condition_id'], 'E10-SUT01-WEB-PROBLEM')
        self.assertIn('between 1 and 3', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'DRY_RUN', executions=4)[1])
        self.assertIn('between 1 and 3', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'DRY_RUN')[1])
        os.environ.pop('GITHUB_WORKFLOW_REF', None)
        self.assertIn('only inside .github/workflows/e10-measured-execution.yml', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'MEASURED_EXPERIMENT')[1])
        os.environ['GITHUB_WORKFLOW_REF'] = 'o/r/.github/workflows/e10-measured-execution.yml@refs/heads/main'
        try:
            self.assertIn('N = 50', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'MEASURED_EXPERIMENT', executions=10)[1])
            # a configuration whose thresholds are null (no calibration written): a measured run fails closed
            uncal = copy.deepcopy(CFG)
            for cond in uncal['conditions']:
                cond['thresholds'] = {'T_R': None, 'T_e': None}
            env = env_for('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'MEASURED_EXPERIMENT')
            self.assertIn('calibrated thresholds', run.check(env, uncal)[1])
            # the conditions file now carries the thresholds of the calibration record, so the real configuration passes this check
            env = env_for('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'MEASURED_EXPERIMENT')
            self.assertIsNone(run.check(env, CFG)[1])
            calibrated = copy.deepcopy(CFG)
            for cond in calibrated['conditions']:
                cond['thresholds'] = {'T_R': 0.001, 'T_e': 0.02}
            env = env_for('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'MEASURED_EXPERIMENT')
            self.assertIsNone(run.check(env, calibrated)[1])
            env = env_for('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'MEASURED_EXPERIMENT', first=4, attempt=2)
            self.assertIsNone(run.check(env, calibrated)[1])
            # a DRY_RUN and a DEVELOPMENT run need no calibration (with null thresholds the floors are used and the result is labeled provisional)
            self.assertIsNone(self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'DEVELOPMENT', executions=5)[1])
        finally:
            del os.environ['GITHUB_WORKFLOW_REF']

    def test_refusals(self):
        self.assertIn('does not belong to SUT-02', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-02', 'DRY_RUN', executions=1)[1])
        self.assertIn('not a condition', self.check('E10-SUT01-WEB-OTHER', 'SUT-01', 'DRY_RUN', executions=1)[1])
        self.assertIn('RECORD_CLASS', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'NOPE', executions=1)[1])
        self.assertIn('not valid', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'DRY_RUN', executions=2, first=3)[1])
        self.assertIn('not valid', self.check('E10-SUT01-WEB-PROBLEM', 'SUT-01', 'DRY_RUN', executions=2, attempt=0)[1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
