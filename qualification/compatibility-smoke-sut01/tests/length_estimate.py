# OP-CI-15 expression-length estimate, the same formula as the step "Assert no string that carries an expression can exceed the
# expression length limit of GitHub" of .github/workflows/e03-validate.yml, applied to every workflow file of a repository root.
# Usage: PYTHONPATH=<directory holding a PyYAML installation> python3 length_estimate.py <repository root>
import glob
import os
import sys

import yaml

ROOT = os.path.abspath(sys.argv[1])
OPEN = '$' + '{' + '{'
LIMIT = 20000
measured = []


def walk(o, f, where):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, f, where + [str(k)])
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f, where + [str(i)])
    elif isinstance(o, str) and OPEN in o:
        measured.append((len(o) + o.count("'") + o.count('{') + o.count('}'), len(o), f, '/'.join(where)))


files = sorted(glob.glob(os.path.join(ROOT, '.github', 'workflows', '*.yml')))
for f in files:
    walk(yaml.safe_load(open(f, encoding='utf-8')), os.path.relpath(f, ROOT), [])
measured.sort(reverse=True)
bad = [m for m in measured if m[0] > LIMIT]
print('workflows', len(files), '| strings that carry an expression', len(measured), '| longest estimate', measured[0][0] if measured else 0, '| limit', LIMIT)
for m in measured[:6]:
    print('  estimate %d (characters %d) %s %s' % (m[0], m[1], m[2], m[3]))
for m in bad:
    print('FAIL %s %s: %d characters (estimate %d) exceed %d' % (m[2], m[3], m[1], m[0], LIMIT))
print('expression length check ok' if not bad else 'expression length check FAILED')
sys.exit(1 if bad else 0)
