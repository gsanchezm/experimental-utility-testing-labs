"""The DIGESTS block of run-condition.sh equals the current implementation files (run tests/embed_digests.py after every edit).

DRAFT (operation OP-PREP-E06-EXECUTOR). This test reads the repository as it is; it fails when an executor file changed without the
digests being embedded again.
"""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import embed_digests  # noqa: E402

BLOCK = re.compile(r"DIGESTS='\n(.*?)\n'", re.S)


class DigestTests(unittest.TestCase):
    def test_the_embedded_block_matches_every_implementation_file(self):
        with open(embed_digests.ENTRY, encoding='utf-8') as f:
            text = f.read()
        match = BLOCK.search(text)
        self.assertIsNotNone(match, 'the DIGESTS block was not found')
        embedded = [line for line in match.group(1).split('\n') if line.strip()]
        expected = [f'{embed_digests.sha256(os.path.join(embed_digests.EXEC_DIR, rel))}  {rel}' for rel in embed_digests.implementation_files()]
        self.assertEqual(embedded, expected)

    def test_the_package_lists_every_python_file_under_executor(self):
        listed = set(embed_digests.implementation_files())
        for name in sorted(os.listdir(os.path.join(embed_digests.EXEC_DIR, 'executor'))):
            if name.endswith('.py'):
                self.assertIn(f'executor/{name}', listed)

    def test_the_tests_are_not_part_of_the_implementation_digests(self):
        self.assertFalse(any(rel.startswith('tests/') for rel in embed_digests.implementation_files()))


if __name__ == '__main__':
    unittest.main()
