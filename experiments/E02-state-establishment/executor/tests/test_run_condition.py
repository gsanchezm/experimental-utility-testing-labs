"""Embedded-digest lock tests for run-condition.sh (DRAFT, operation OP-PREP-E02).

The executor directory is copied to a temporary directory (tests excluded), and run-condition.sh is run there on
the copy: the embedded digests must match the files; a changed implementation file, an unlisted Python file, and a missing
environment variable must each stop the script before any manifest is written. Nothing is dispatched; no SUT is touched.

Run: python3 tests/test_run_condition.py -v
"""
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_DIR = os.path.dirname(HERE)
SKIP = {'tests', '__pycache__'}


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def embedded(script_text):
    block = re.search(r"DIGESTS='\n(.*?)\n'", script_text, re.S).group(1)
    out = {}
    for line in block.splitlines():
        digest, path = line.split(None, 1)
        out[path.strip()] = digest
    return out


class DigestLock(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='e02-digest-')
        self.addCleanup(shutil.rmtree, self.root, True)
        self.copy = os.path.join(self.root, 'executor')
        os.makedirs(self.copy)
        for name in os.listdir(EXECUTOR_DIR):
            if name in SKIP:
                continue
            src = os.path.join(EXECUTOR_DIR, name)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(self.copy, name), ignore=shutil.ignore_patterns('__pycache__'))
            else:
                shutil.copy2(src, os.path.join(self.copy, name))
        self.out = os.path.join(self.root, 'out')
        self.env = {**os.environ, 'CONDITION_ID': 'E02-CS003-SUT01-API', 'ASSIGNED_SUT': 'SUT-01', 'EXECUTION_ID': 'DV0001', 'ATTEMPT': '1',
                    'EXECUTOR_PROMPT_VERSION': 'test', 'OUTPUT_DIR': os.path.join(self.out, 'E02-CS003-SUT01-API__DV0001__A1'),
                    'PROVENANCE_JSON': os.path.join(self.root, 'p.json'), 'RUNTIME_ENVIRONMENT_JSON': os.path.join(self.root, 'r.json'),
                    'RECORD_CLASS': 'DEVELOPMENT', 'INSTANCE_JSON': os.path.join(self.root, 'instance.json')}

    def script(self):
        return os.path.join(self.copy, 'run-condition.sh')

    def run_script(self, env=None):
        return subprocess.run(['bash', self.script()], env=env or self.env, capture_output=True, text=True)

    def test_embedded_digests_match_the_copied_files(self):
        with open(self.script(), encoding='utf-8') as f:
            table = embedded(f.read())
        listed = set(table)
        actual = {'requirements.txt'} | {os.path.join('executor', n) for n in os.listdir(os.path.join(self.copy, 'executor')) if n.endswith('.py')}
        self.assertEqual(listed, actual, 'the embedded list covers exactly the implementation files')
        for rel, digest in table.items():
            self.assertEqual(sha256(os.path.join(self.copy, rel)), digest, rel)

    def test_a_changed_implementation_file_stops_before_any_manifest(self):
        path = os.path.join(self.copy, 'executor', 'common.py')
        with open(path, 'a', encoding='utf-8') as f:
            f.write('\n# tampered after the lock\n')
        proc = self.run_script()
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('digest mismatch for executor/common.py', proc.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.env['OUTPUT_DIR'], 'run-manifest.json')))

    def test_an_unlisted_python_file_under_the_package_stops_the_script(self):
        with open(os.path.join(self.copy, 'executor', 'extra.py'), 'w', encoding='utf-8') as f:
            f.write('X = 1\n')
        proc = self.run_script()
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('unlisted Python file under executor/: executor/extra.py', proc.stderr)

    def test_a_missing_environment_variable_stops_the_script(self):
        env = dict(self.env)
        del env['RECORD_CLASS']
        proc = self.run_script(env)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('RECORD_CLASS is not set', proc.stderr)

    def test_the_refresh_tool_reproduces_the_block_it_wrote(self):
        tool = os.path.join(self.copy, 'tools', 'refresh_embedded_digests.py')
        with open(self.script(), encoding='utf-8') as f:
            before = f.read()
        proc = subprocess.run(['python3', tool, self.copy], capture_output=True, text=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(self.script(), encoding='utf-8') as f:
            self.assertEqual(f.read(), before, 'the tool is idempotent on unchanged files')


if __name__ == '__main__':
    unittest.main()
