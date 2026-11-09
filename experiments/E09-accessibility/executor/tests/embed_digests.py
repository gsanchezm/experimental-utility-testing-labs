"""Compute the implementation digests and embed them in run-condition.sh (run this last, after every edit of executor files).

DRAFT (operation OP-PREP-E09). Writes the DIGESTS block of run-condition.sh: one "sha256  path" line per file of
executor/executor/*.py and of requirements.txt, paths relative to the executor directory, sorted (the Python files byte-wise, then
requirements.txt). The E03 lock mechanism applies: the entry point verifies these digests before anything else, and an unlisted
Python file under executor/executor/ is refused. Usage: python3 tests/embed_digests.py (from any directory).
"""
import glob
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC_DIR = os.path.abspath(os.path.join(HERE, '..'))
ENTRY = os.path.join(EXEC_DIR, 'run-condition.sh')
BLOCK = re.compile(r"(DIGESTS='\n)(.*?)(\n')", re.S)


def implementation_files():
    py = sorted(glob.glob(os.path.join(EXEC_DIR, 'executor', '*.py')), key=lambda p: os.path.basename(p).encode('utf-8'))
    rel = [os.path.relpath(p, EXEC_DIR).replace(os.sep, '/') for p in py]
    return rel + ['requirements.txt']


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    lines = [f'{sha256(os.path.join(EXEC_DIR, rel))}  {rel}' for rel in implementation_files()]
    with open(ENTRY, encoding='utf-8') as f:
        text = f.read()
    match = BLOCK.search(text)
    if not match:
        print('embed_digests: the DIGESTS block was not found in run-condition.sh', file=sys.stderr)
        return 1
    new_text = text[:match.start(2)] + '\n'.join(lines) + text[match.end(2):]
    if new_text != text:
        with open(ENTRY, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_text)
    for line in lines:
        print(line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
