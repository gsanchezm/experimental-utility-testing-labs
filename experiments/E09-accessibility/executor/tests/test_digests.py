"""The embedded-digest lock: run-condition.sh lists exactly the implementation files, with their current SHA-256 digests.

DRAFT (operation OP-PREP-E09). Independent of embed_digests.py: it re-reads the DIGESTS block of run-condition.sh and compares
each entry with the file on disk, and it checks that no Python file under executor/executor/ is unlisted.
"""
import glob
import hashlib
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC_DIR = os.path.abspath(os.path.join(HERE, '..'))


class DigestLockTests(unittest.TestCase):
    def block(self):
        with open(os.path.join(EXEC_DIR, 'run-condition.sh'), encoding='utf-8') as f:
            text = f.read()
        m = re.search(r"DIGESTS='\n(.*?)\n'", text, re.S)
        self.assertIsNotNone(m, 'DIGESTS block not found')
        return [line.split() for line in m.group(1).splitlines() if line.strip()]

    def test_every_listed_digest_matches_its_file(self):
        entries = self.block()
        self.assertTrue(entries)
        for digest, rel in entries:
            with open(os.path.join(EXEC_DIR, rel), 'rb') as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest, rel)

    def test_listed_set_equals_the_python_files_plus_requirements(self):
        listed = {rel for _digest, rel in self.block()}
        present = {os.path.relpath(p, EXEC_DIR).replace(os.sep, '/') for p in glob.glob(os.path.join(EXEC_DIR, 'executor', '*.py'))}
        self.assertEqual(listed, present | {'requirements.txt'})

    def test_entry_point_is_not_listed_in_its_own_block(self):
        self.assertNotIn('run-condition.sh', {rel for _d, rel in self.block()})


if __name__ == '__main__':
    unittest.main(verbosity=2)
