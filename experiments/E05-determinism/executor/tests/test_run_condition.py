"""The entry point run-condition.sh: digest refusal, unlisted-file refusal, and the refusal of a run that the executor cannot start.

DRAFT (operation OP-PREP-E05). Each case copies the executor directory (without tests/) to a temporary directory, changes it, and runs the
entry point there with the required environment. No browser starts and no instance is needed: the digest check refuses first, or the Python
entry refuses (a measured run outside the measured workflow) before it contacts anything.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC_DIR = os.path.abspath(os.path.join(HERE, '..'))
CONDITION = 'E05-SUT05-API-01'


def copy_executor(dest):
    target = os.path.join(dest, 'executor-copy')
    shutil.copytree(EXEC_DIR, target, ignore=shutil.ignore_patterns('tests', '__pycache__', '*.md', 'tools'))
    # the conditions file the executor reads sits two levels above the executor directory
    shutil.copyfile(os.path.join(EXEC_DIR, '..', 'conditions-draft.json'), os.path.join(dest, 'conditions-draft.json'))
    return target


def env_for(out_dir):
    env = {k: v for k, v in os.environ.items() if not k.startswith(('CONDITION_ID', 'OUTPUT_DIR', 'GITHUB_WORKFLOW_REF', 'EXECUTIONS'))}
    env.update({'CONDITION_ID': CONDITION, 'ASSIGNED_SUT': 'SUT-05', 'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1', 'OUTPUT_DIR': out_dir,
                'PROVENANCE_JSON': os.path.join(out_dir, 'no-provenance.json'),
                'RUNTIME_ENVIRONMENT_JSON': os.path.join(out_dir, 'no-runtime.json'), 'RECORD_CLASS': 'MEASURED_EXPERIMENT'})
    return env


class RunConditionTests(unittest.TestCase):
    def run_entry(self, root):
        out = os.path.join(root, 'out')
        proc = subprocess.run(['bash', os.path.join(root, 'executor-copy', 'run-condition.sh')], env=env_for(out), capture_output=True, text=True,
                              timeout=120)
        return proc.returncode, proc.stderr

    def test_tampered_file_is_refused_before_anything_runs(self):
        root = tempfile.mkdtemp(prefix='e05-entry-')
        target = copy_executor(root)
        with open(os.path.join(target, 'executor', 'classify.py'), 'a', encoding='utf-8') as f:
            f.write('\n# tampered\n')
        code, err = self.run_entry(root)
        self.assertEqual(code, 1)
        self.assertIn('digest mismatch for executor/classify.py', err)

    def test_tampered_data_file_is_refused(self):
        root = tempfile.mkdtemp(prefix='e05-entry-')
        target = copy_executor(root)
        with open(os.path.join(target, 'expected-sut01.json'), 'a', encoding='utf-8') as f:
            f.write(' ')
        code, err = self.run_entry(root)
        self.assertEqual(code, 1)
        self.assertIn('digest mismatch for expected-sut01.json', err)

    def test_unlisted_python_file_is_refused(self):
        root = tempfile.mkdtemp(prefix='e05-entry-')
        target = copy_executor(root)
        with open(os.path.join(target, 'executor', 'extra.py'), 'w', encoding='utf-8') as f:
            f.write('X = 1\n')
        code, err = self.run_entry(root)
        self.assertEqual(code, 1)
        self.assertIn('unlisted Python file under executor/', err)

    def test_a_missing_variable_is_refused(self):
        root = tempfile.mkdtemp(prefix='e05-entry-')
        copy_executor(root)
        env = env_for(os.path.join(root, 'out'))
        del env['RECORD_CLASS']
        proc = subprocess.run(['bash', os.path.join(root, 'executor-copy', 'run-condition.sh')], env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('RECORD_CLASS is not set', proc.stderr)

    def test_unmodified_copy_reaches_the_entry_and_a_measured_run_outside_the_workflow_is_refused(self):
        root = tempfile.mkdtemp(prefix='e05-entry-')
        copy_executor(root)
        code, err = self.run_entry(root)
        self.assertEqual(code, 2)
        self.assertIn('only inside .github/workflows/e05-measured-execution.yml', err)
        self.assertFalse(os.path.exists(os.path.join(root, 'out', 'executions')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
