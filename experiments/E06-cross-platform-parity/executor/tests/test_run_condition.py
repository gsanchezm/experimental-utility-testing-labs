"""run-condition.sh: the refusals that happen before any Python runs (attempt, record class, oracle, digests, unlisted files, existing summary).

DRAFT (operation OP-PREP-E06-EXECUTOR). Each refusal test runs the script on a copy of the executor directory, so the repository is never
written. The copy is re-embedded with the digests of the copy by embed_digests (the same routine the repository uses).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

import embed_digests  # noqa: E402


def base_env(out, **kw):
    env = {'PATH': os.environ.get('PATH', ''), 'CONDITION_ID': 'E06-CS007-SUT01-WEB', 'ATTEMPT': '1', 'RECORD_CLASS': 'DRY_RUN',
           'EXPECTED_IDENTITY_ORACLE': 'item_identity', 'OUTPUT_DIR': out, 'PROVENANCE_JSON': '/nonexistent/p.json',
           'RUNTIME_ENVIRONMENT_JSON': '/nonexistent/r.json', 'HOME': os.environ.get('HOME', '/')}
    env.update(kw)
    return env


class RunConditionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='e06-rc-')
        # the layout of the repository: the executor, the conditions file and the harness under experiments/E06-cross-platform-parity, and the
        # locked Appium stack of the SUT-01 smoke under qualification/ (the digests name it relative to the executor directory)
        base = os.path.join(self.tmp, 'experiments', 'E06-cross-platform-parity')
        self.copy = os.path.join(base, 'executor')
        shutil.copytree(EXEC, self.copy, ignore=shutil.ignore_patterns('__pycache__', 'tests'))
        shutil.copytree(os.path.join(EXEC, 'tests'), os.path.join(self.copy, 'tests'), ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy(os.path.join(EXEC, '..', 'conditions-draft.json'), os.path.join(base, 'conditions-draft.json'))
        os.makedirs(os.path.join(base, 'harness'), exist_ok=True)
        for name in ('e06-android.mjs', 'wd.mjs'):
            shutil.copy(os.path.join(EXEC, '..', 'harness', name), os.path.join(base, 'harness', name))
        lock_dir = os.path.join(self.tmp, 'qualification', 'compatibility-smoke-sut01', 'harness')
        os.makedirs(lock_dir, exist_ok=True)
        for name in ('package.json', 'package-lock.json'):
            shutil.copy(os.path.join(EXEC, '..', '..', '..', 'qualification', 'compatibility-smoke-sut01', 'harness', name), os.path.join(lock_dir, name))
        self.embed()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def embed(self):
        embed_digests.EXEC_DIR = self.copy
        embed_digests.ENTRY = os.path.join(self.copy, 'run-condition.sh')
        self.assertEqual(embed_digests.main(), 0)

    def run_script(self, **kw):
        out = os.path.join(self.tmp, 'out')
        proc = subprocess.run(['bash', os.path.join(self.copy, 'run-condition.sh')], env=base_env(out, **kw), capture_output=True, text=True,
                              timeout=120)
        return proc.returncode, proc.stderr

    def test_an_attempt_or_first_execution_that_is_not_a_positive_integer_is_refused_before_anything_runs(self):
        for kw in ({'ATTEMPT': '0'}, {'ATTEMPT': 'two'}, {'ATTEMPT': '02'}, {'FIRST_EXECUTION': '0'}, {'FIRST_EXECUTION': 'x'}):
            with self.subTest(**kw):
                status, err = self.run_script(**kw)
                self.assertNotEqual(status, 0)
                self.assertIn('must be a positive integer', err)

    def test_attempt_one_from_a_later_execution_is_refused_before_anything_runs(self):
        status, err = self.run_script(FIRST_EXECUTION='17')
        self.assertNotEqual(status, 0)
        self.assertIn('attempt 1 starts at execution 1', err)

    def test_a_non_measured_record_of_a_further_attempt_is_refused_by_the_executor(self):
        for kw in ({'ATTEMPT': '2', 'FIRST_EXECUTION': '17'}, {'ATTEMPT': '2'}):
            with self.subTest(**kw):
                status, err = self.run_script(**kw)
                self.assertEqual(status, 2)
                self.assertIn('a non-measured record is attempt 1 from execution 1 only', err)

    def test_an_unknown_record_class_is_refused(self):
        status, err = self.run_script(RECORD_CLASS='LOCAL')
        self.assertNotEqual(status, 0)
        self.assertIn('record class LOCAL is not allowed', err)

    def test_an_unknown_identity_oracle_is_refused(self):
        status, err = self.run_script(EXPECTED_IDENTITY_ORACLE='visual')
        self.assertNotEqual(status, 0)
        self.assertIn('identity oracle visual', err)

    def test_a_missing_required_variable_is_refused(self):
        status, err = self.run_script(CONDITION_ID='')
        self.assertNotEqual(status, 0)
        self.assertIn('CONDITION_ID', err)

    def test_a_changed_implementation_file_is_refused_by_its_digest(self):
        path = os.path.join(self.copy, 'executor', 'classify.py')
        with open(path, 'a', encoding='utf-8') as f:
            f.write('\n# changed after the digests were embedded\n')
        status, err = self.run_script()
        self.assertNotEqual(status, 0)
        self.assertIn('digest mismatch for executor/classify.py', err)

    def test_an_unlisted_python_file_is_refused(self):
        with open(os.path.join(self.copy, 'executor', 'extra.py'), 'w', encoding='utf-8') as f:
            f.write('X = 1\n')
        status, err = self.run_script()
        self.assertNotEqual(status, 0)
        self.assertIn('unlisted Python file under executor/: executor/extra.py', err)

    def test_an_existing_condition_summary_is_refused(self):
        out = os.path.join(self.tmp, 'out')
        os.makedirs(out)
        with open(os.path.join(out, 'condition-summary.json'), 'w', encoding='utf-8') as f:
            f.write('{}')
        status, err = self.run_script()
        self.assertNotEqual(status, 0)
        self.assertIn('attempts are immutable', err)


if __name__ == '__main__':
    unittest.main()
