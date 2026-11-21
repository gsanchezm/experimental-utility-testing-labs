"""Record the output of the executor's test suites into tests/RECORDED-OUTPUT.txt (DRAFT, operation OP-PREP-E06-EXECUTOR).

Runs the Python suite (unittest, with ResourceWarning as an error) and the Node suite (node --test) as subprocesses, collects their
output, replaces every local location with a placeholder (the repository, the executor, the harness, the lint tools, the temporary
directories, and the home directory), and writes the file. The lint binaries and the Python and Node interpreters are named by the
environment variables ACTIONLINT, SHELLCHECK, PYTHON_BIN (default: the running interpreter), and NODE_BIN (default: node).
Usage: python3 tests/record_output.py
"""
import datetime
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.abspath(os.path.join(HERE, '..'))
HARNESS = os.path.abspath(os.path.join(EXEC, '..', 'harness'))
REPO = os.path.abspath(os.path.join(EXEC, '..', '..', '..'))
OUT = os.path.join(HERE, 'RECORDED-OUTPUT.txt')


def version_line(cmd):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        text = (proc.stdout + proc.stderr).strip().splitlines()
        versioned = [line for line in text if line.lower().startswith('version:')]
        return versioned[0] if versioned else (text[0] if text else 'unknown')
    except OSError:
        return 'not available'


def run(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)
    return proc.returncode, proc.stdout + proc.stderr


def sanitize(text):
    replacements = [(REPO, '<repo>'), (EXEC, '<executor>'), (HARNESS, '<harness>'), (os.path.expanduser('~'), '<home>'),
                    (tempfile.gettempdir(), '<tmp>'), ('/' + 'private/tmp', '<tmp>'), ('/' + 'tmp', '<tmp>')]
    for raw, label in replacements:
        if raw and len(raw) > 1:
            text = text.replace(raw, label)
    for var in ('ACTIONLINT', 'SHELLCHECK'):
        value = os.environ.get(var)
        if value:
            text = text.replace(value, f'<lint:{var.lower()}>')
    text = re.sub(r'/(?:Users|home)/[A-Za-z0-9._-]+', '<home>', text)
    # the Node reporter draws its status marks as symbols; the record keeps plain ASCII labels
    for symbol, label in (('\u2714', '[pass]'), ('\u2716', '[fail]'), ('\u2139', 'info:')):
        text = text.replace(symbol, label)
    return text


def main():
    python = os.environ.get('PYTHON_BIN') or sys.executable
    node = os.environ.get('NODE_BIN') or 'node'
    lines = []
    lines.append('RECORDED OUTPUT of the E06-cross-platform-parity executor test suites (DRAFT, operation OP-PREP-E06-EXECUTOR)')
    lines.append('Recorded by tests/record_output.py. Local locations are replaced by placeholders; no test here uses a device, an emulator,')
    lines.append('a browser, Appium, or a hosted system under test. The Python suite runs with ResourceWarning as an error.')
    lines.append('')
    lines.append(f"recorded (UTC): {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"python: {version_line([python, '--version'])}")
    lines.append(f"node: {version_line([node, '--version'])}")
    actionlint = os.environ.get('ACTIONLINT')
    shellcheck = os.environ.get('SHELLCHECK')
    lines.append(f"actionlint: {version_line([actionlint, '-version']) if actionlint else 'not set (lint test skipped unless on PATH)'}")
    lines.append(f"shellcheck: {version_line([shellcheck, '--version']) if shellcheck else 'not set'}")
    lines.append('')
    lines.append('== Python suite: executor/tests (unittest, -v) ==')
    code, text = run([python, '-W', 'error::ResourceWarning', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'], EXEC)
    lines.append(sanitize(text).rstrip())
    lines.append(f'exit status: {code}')
    lines.append('')
    lines.append('== Node suite: harness/tests (node --test) ==')
    code2, text2 = run([node, '--test', 'tests/wd.test.mjs', 'tests/harness.test.mjs'], HARNESS)
    lines.append(sanitize(text2).rstrip())
    lines.append(f'exit status: {code2}')
    lines.append('')
    lines.append('== Digests ==')
    lines.append('The DIGESTS block of executor/run-condition.sh is checked by tests/test_digests.py in the Python suite above.')
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'wrote {os.path.basename(OUT)}: python exit {code}, node exit {code2}')
    return 0 if code == 0 and code2 == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
