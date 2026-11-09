"""The entry point run-condition.sh: digest refusal, unlisted-file refusal, and the no-manifest exit on a refused run.

DRAFT (operation OP-PREP-E09). Each case copies the executor directory (without tests/) to a temporary directory, changes it, and
runs the entry point there with the required environment. No browser starts: the Python entry refuses (no Playwright pin
installed in the sandbox) or the digest check refuses first.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC_DIR = os.path.abspath(os.path.join(HERE, '..'))


def copy_executor(dest):
    target = os.path.join(dest, 'executor-copy')
    shutil.copytree(EXEC_DIR, target, ignore=shutil.ignore_patterns('tests', '__pycache__', '*.md'))
    return target


def env_for(out_dir):
    env = {k: v for k, v in os.environ.items() if not k.startswith(('CONDITION_ID', 'OUTPUT_DIR', 'AXE_'))}
    env.update({'CONDITION_ID': 'E09-CTRL-SUT01-STANDARD', 'ASSIGNED_SUT': 'SUT-01', 'EXECUTION_ID': 'EX0001', 'ATTEMPT': '1',
                'EXECUTOR_PROMPT_VERSION': 'TEST-FIXTURE-PROMPT-v1', 'OUTPUT_DIR': out_dir,
                'PROVENANCE_JSON': os.path.join(out_dir, 'no-provenance.json'),
                'RUNTIME_ENVIRONMENT_JSON': os.path.join(out_dir, 'no-runtime.json'), 'RECORD_CLASS': 'MEASURED_EXPERIMENT',
                'AXE_TARBALL': os.path.join(out_dir, 'no-tarball.tgz')})
    return env


class RunConditionTests(unittest.TestCase):
    def run_entry(self, root):
        out = os.path.join(root, 'out', 'E09-CTRL-SUT01-STANDARD__EX0001__A1')
        proc = subprocess.run(['bash', os.path.join(root, 'executor-copy', 'run-condition.sh')], env=env_for(out),
                              capture_output=True, text=True, timeout=120)
        return proc.returncode, proc.stderr

    def test_tampered_file_is_refused_before_anything_runs(self):
        root = tempfile.mkdtemp(prefix='e09-entry-')
        target = copy_executor(root)
        with open(os.path.join(target, 'executor', 'classify.py'), 'a', encoding='utf-8') as f:
            f.write('\n# tampered\n')
        code, err = self.run_entry(root)
        self.assertEqual(code, 1)
        self.assertIn('digest mismatch for executor/classify.py', err)

    def test_unlisted_python_file_is_refused(self):
        root = tempfile.mkdtemp(prefix='e09-entry-')
        target = copy_executor(root)
        with open(os.path.join(target, 'executor', 'extra.py'), 'w', encoding='utf-8') as f:
            f.write('X = 1\n')
        code, err = self.run_entry(root)
        self.assertEqual(code, 1)
        self.assertIn('unlisted Python file under executor/', err)

    def test_unmodified_copy_reaches_the_entry_and_writes_no_manifest_when_refused(self):
        root = tempfile.mkdtemp(prefix='e09-entry-')
        copy_executor(root)
        code, err = self.run_entry(root)
        self.assertEqual(code, 1)
        self.assertIn('no run manifest was written', err)
        self.assertFalse(os.path.exists(os.path.join(root, 'out', 'E09-CTRL-SUT01-STANDARD__EX0001__A1', 'run-manifest.json')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
