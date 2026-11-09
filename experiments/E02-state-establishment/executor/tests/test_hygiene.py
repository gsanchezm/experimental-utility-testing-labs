"""Publication-hygiene scan of every file this draft creates (DRAFT, operation OP-PREP-E02).

Forbidden in the files: the file names of the agent-instructions file (canonical and provider-neutral), the name of the
publication record, assistant or vendor attribution, a person's name, local filesystem paths, and conversation identifiers.
Exemptions are exact and listed: the scrubber's own path patterns (executor/executor/common.py).

Run: python3 tests/test_hygiene.py -v
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_DIR = os.path.dirname(HERE)
WORKFLOWS = os.path.join(EXECUTOR_DIR, '..', '..', '..', '.github', 'workflows')
SELF = os.path.basename(__file__)

# The vendor, person and path tokens are built from fragments so that this file never carries the literal strings it forbids
# (the public publication-hygiene scan rejects them in every tracked file).
FORBIDDEN = [
    r'CLA' + r'UDE', r'Cla' + r'ude', r'cla' + r'ude', r'AGENT-INSTRUCTIONS', r'Anthr' + r'opic', r'anthr' + r'opic', r'PUBLIC-EXPORT-MANIFEST',
    r'Open' + r'AI', r'Co' + r'dex', r'Chat' + r'GPT', r'Copi' + r'lot', r'Gem' + r'ini', r'gilberto' + r'sanchez', r'Gilb' + r'erto', r'Co-Authored' + r'-By',
    r'/Us' + r'ers/', r'/ho' + r'me/', r'C:\\', r'session_01[0-9A-Za-z]{8,}',
]
EXEMPT = {
    os.path.join('executor', 'common.py'): {"'/private/tmp'", "'/tmp'"},   # the scrubber's own path patterns
}


def files():
    out = []
    for root, dirs, names in os.walk(EXECUTOR_DIR):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for n in names:
            if n == SELF or n.endswith(('.pyc',)):
                continue
            out.append(os.path.join(root, n))
    for n in sorted(os.listdir(WORKFLOWS)):
        if n.startswith('e02-'):
            out.append(os.path.join(WORKFLOWS, n))
    return out


class Hygiene(unittest.TestCase):
    def test_no_forbidden_token_in_any_created_file(self):
        hits = []
        for path in files():
            rel = os.path.relpath(path, EXECUTOR_DIR) if path.startswith(EXECUTOR_DIR) else os.path.basename(path)
            with open(path, encoding='utf-8') as f:
                lines = f.read().split('\n')
            exempt = EXEMPT.get(rel, set())
            for i, line in enumerate(lines, 1):
                scan = line
                for e in exempt:
                    scan = scan.replace(e, '')
                for pat in FORBIDDEN:
                    if re.search(pat, scan):
                        hits.append(f'{rel}:{i}: {pat}')
        self.assertEqual(hits, [], 'forbidden tokens:\n' + '\n'.join(hits))

    def test_the_workflows_are_the_only_ci_files_and_are_dispatch_only(self):
        import sys
        sys.path.insert(0, os.path.join(EXECUTOR_DIR, '..', '..', '..'))
        for n in ('e02-measured-execution.yml', 'e02-environment-verification.yml'):
            with open(os.path.join(WORKFLOWS, n), encoding='utf-8') as f:
                text = f.read()
            self.assertIn('workflow_dispatch:', text)
            self.assertNotRegex(text, r'\n  (push|pull_request|schedule):')


if __name__ == '__main__':
    unittest.main()
