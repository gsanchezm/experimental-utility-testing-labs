"""Rewrite the embedded DIGESTS block of run-condition.sh from the implementation files (DRAFT, operation OP-PREP-E02).

Usage: python3 tools/refresh_embedded_digests.py [EXECUTOR_DIR]   (EXECUTOR_DIR defaults to the parent of this tools directory)

The list covers every Python file under executor/executor/ and requirements.txt. Every digest is computed from the file's bytes
here; none is typed. Run it after every edit of an implementation file, then recompute the sha256 of run-condition.sh itself
(that hash is the one the measured workflow compares with the locked configuration; it is not embedded in the script).
This tool is outside executor/executor/, so the unlisted-file check of run-condition.sh does not see it.
"""
import glob
import hashlib
import os
import re
import sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main(executor_dir):
    files = [os.path.join('executor', os.path.basename(p)) for p in glob.glob(os.path.join(executor_dir, 'executor', '*.py'))]
    files = sorted(files + ['requirements.txt'])
    lines = [f'{sha256(os.path.join(executor_dir, rel))}  {rel}' for rel in files]
    path = os.path.join(executor_dir, 'run-condition.sh')
    with open(path, encoding='utf-8') as f:
        text = f.read()
    block = "DIGESTS='\n" + '\n'.join(lines) + "\n'"
    new, count = re.subn(r"DIGESTS='\n.*?\n'", lambda m: block, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit('run-condition.sh: the DIGESTS block was not found exactly once')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    for line in lines:
        print(line)
    return 0


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(here)))
