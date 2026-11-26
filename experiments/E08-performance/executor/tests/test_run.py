"""The entry checks of executor.run and the registry of realizations (operation OP-PREP-E08). Static tests: no browser, no SUT."""
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
    tmp = tempfile.mkdtemp(prefix='e08-run-')
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
            self.assertEqual((cls.SPEC.modality, cls.SPEC.platform), ('Performance', 'web'))

    def test_a_dry_run_is_bounded_and_a_measured_run_needs_the_workflow(self):
        c, problem = self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'DRY_RUN', executions=3)
        self.assertIsNone(problem)
        self.assertEqual(c['condition_id'], 'E08-SUT01-WEB-DELAY')
        self.assertIn('between 1 and 3', self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'DRY_RUN', executions=4)[1])
        self.assertIn('between 1 and 3', self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'DRY_RUN')[1])
        os.environ.pop('GITHUB_WORKFLOW_REF', None)
        self.assertIn('only inside .github/workflows/e08-measured-execution.yml', self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'MEASURED_EXPERIMENT')[1])
        os.environ['GITHUB_WORKFLOW_REF'] = 'o/r/.github/workflows/e08-measured-execution.yml@refs/heads/main'
        try:
            self.assertIsNone(self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'MEASURED_EXPERIMENT')[1])
            self.assertIn('N = 50', self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'MEASURED_EXPERIMENT', executions=10)[1])
            self.assertIsNone(self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'MEASURED_EXPERIMENT', first=4, attempt=2)[1])
        finally:
            del os.environ['GITHUB_WORKFLOW_REF']

    def test_refusals(self):
        self.assertIn('does not belong to SUT-02', self.check('E08-SUT01-WEB-DELAY', 'SUT-02', 'DRY_RUN', executions=1)[1])
        self.assertIn('not a condition', self.check('E08-SUT01-WEB-OTHER', 'SUT-01', 'DRY_RUN', executions=1)[1])
        self.assertIn('RECORD_CLASS', self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'NOPE', executions=1)[1])
        self.assertIn('not valid', self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'DRY_RUN', executions=2, first=3)[1])
        self.assertIn('not valid', self.check('E08-SUT01-WEB-DELAY', 'SUT-01', 'DRY_RUN', executions=2, attempt=0)[1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
