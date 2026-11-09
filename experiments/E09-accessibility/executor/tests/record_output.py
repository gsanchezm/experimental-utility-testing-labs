"""Run the static suite and write tests/RECORDED-OUTPUT.txt, with the repository and temporary-directory roots replaced by markers.

DRAFT (operation OP-PREP-E09). Usage (optional environment: ACTIONLINT and SHELLCHECK name the binaries for test_workflows.py;
E09_AXE_TARBALL_FOR_TEST names a local copy of the pinned tarball; PYTHONPATH may name a pure-Python PyYAML):
    python3 tests/record_output.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
OUT = os.path.join(HERE, 'RECORDED-OUTPUT.txt')


def main():
    proc = subprocess.run([sys.executable, '-W', 'ignore', '-m', 'unittest', 'discover', '-s', HERE, '-p', 'test_*.py', '-v'],
                          cwd=HERE, capture_output=True, text=True, timeout=900)
    text = proc.stdout + proc.stderr
    for root, marker in ((REPO, '<repo>'), (os.path.realpath(tempfile.gettempdir()), '<tmp>'), (tempfile.gettempdir(), '<tmp>')):
        text = text.replace(root, marker)
    header = ('DRAFT (operation OP-PREP-E09). Recorded output of the static suite of experiments/E09-accessibility/executor/tests/.\n'
              'Paths are repository-relative or marked <repo> / <tmp>. Synthetic fixtures only; no SUT was contacted.\n\n')
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header + text + f'\n[exit status of the unittest run: {proc.returncode}]\n')
    print(f'wrote {os.path.relpath(OUT, REPO)} (exit {proc.returncode})')
    return proc.returncode


if __name__ == '__main__':
    sys.exit(main())
