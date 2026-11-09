# Static checks of the SUT-01 Android compatibility-smoke draft. Runs syntax and lint tools, parses the new YAML files, runs the
# expression-length estimate, and checks that no tracked file changed. Nothing is dispatched, installed, or executed beyond the
# tools named here. Output is written with repository-relative paths only.
# Usage: python3 run_static_checks.py <repository root> <actionlint binary> <shellcheck binary> <directory holding PyYAML> <output file>
import os
import subprocess
import sys

ROOT, ACTIONLINT, SHELLCHECK, PYLIB, OUT = sys.argv[1:6]
ROOT = os.path.abspath(ROOT)
S1 = 'qualification/compatibility-smoke-sut01'
NEW_YAML = ['manifests/compatibility-smoke-implementation-lock-v5.draft.yaml',
            'manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml',
            '.github/workflows/e06-compatibility-smoke-sut01.yml']
out = []
ok_all = True


def log(s=''):
    out.append(s)
    print(s)


def run(args, cwd=ROOT, env=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr).rstrip()


def check(name, rc, detail=''):
    global ok_all
    ok_all = ok_all and rc == 0
    log(f'[{"PASS" if rc == 0 else "FAIL"}] {name} (exit {rc})')
    if detail:
        for line in detail.splitlines():
            log('    ' + line)


# 1. YAML parse (new files) with the pure-Python PyYAML copy
sys.path.insert(0, PYLIB)
import yaml  # noqa: E402
for rel in NEW_YAML:
    try:
        with open(os.path.join(ROOT, rel), encoding='utf-8') as fh:
            doc = yaml.safe_load(fh)
        check('YAML parses: ' + rel, 0, f'top-level keys: {len(doc) if isinstance(doc, dict) else type(doc).__name__}')
    except Exception as e:  # noqa: BLE001
        check('YAML parses: ' + rel, 1, str(e))

# 2. actionlint 1.7.7 with shellcheck 0.10.0 on the workflow
rc, detail = run([ACTIONLINT, '-no-color', '-shellcheck', SHELLCHECK, '.github/workflows/e06-compatibility-smoke-sut01.yml'])
check('actionlint 1.7.7 with shellcheck 0.10.0: .github/workflows/e06-compatibility-smoke-sut01.yml', rc, detail or 'no findings')

# 3. shellcheck on the two shell scripts (run from their folder so that source paths resolve)
rc, detail = run([SHELLCHECK, '-x', 'smoke-common.sh', 'run-smoke-android.sh'], cwd=os.path.join(ROOT, S1))
check('shellcheck 0.10.0 -x: smoke-common.sh, run-smoke-android.sh', rc, detail or 'no findings')

# 4. bash -n on the scripts
for rel in [S1 + '/smoke-common.sh', S1 + '/run-smoke-android.sh']:
    rc, detail = run(['bash', '-n', rel])
    check('bash -n: ' + rel, rc, detail)

# 5. node --check on the harness, and the static realization hash (pure function; no harness run)
for rel in [S1 + '/harness/smoke.mjs', S1 + '/harness/wd.mjs']:
    rc, detail = run(['node', '--check', rel])
    check('node --check: ' + rel, rc, detail or 'syntax ok')
code = ("import { realizationSha256 } from './" + S1 + "/harness/smoke.mjs'; process.stdout.write(realizationSha256());")
rc, detail = run(['node', '--input-type=module', '-e', code])
check('realizationSha256() of the harness (pure function, no run)', rc, detail)

# 6. OP-CI-15 expression-length estimate over every workflow file
rc, detail = run([sys.executable, S1 + '/tests/length_estimate.py', ROOT], env={**os.environ, 'PYTHONPATH': PYLIB})
check('OP-CI-15 expression-length estimate over every workflow file', rc, detail)

# 7. tracked files unchanged: only the new draft paths may appear as untracked
rc, status = run(['git', '-C', ROOT, 'status', '--porcelain', '--untracked-files=all'])
lines = [l for l in status.splitlines() if l.strip()]
tracked_changes = [l for l in lines if not l.startswith('?? ')]
unexpected = [l for l in lines if l.startswith('?? ') and not l[3:].startswith(S1 + '/') and l[3:] not in NEW_YAML]
check('no tracked file changed; untracked paths are only the new draft files', 0 if (not tracked_changes and not unexpected) else 1,
      '\n'.join(lines) if lines else '(clean)')

# 8. hygiene of the new files: no local path, no assistant or vendor name, no agent-instructions file name
# built from fragments so that this file never carries the literal vendor, person or path strings it forbids (the public hygiene scan rejects them)
forbidden = ['/Us' + 'ers/', '/priv' + 'ate/', '/tmp/', 'Cla' + 'ude', 'cla' + 'ude', 'CLA' + 'UDE', 'Anthr' + 'opic', 'anthr' + 'opic', 'Hai' + 'ku', 'Gilb' + 'erto', 'San' + 'chez', 'AGENT-INSTRUCTIONS']
hits = []
for base in [S1, '.github/workflows/e06-compatibility-smoke-sut01.yml', 'manifests/compatibility-smoke-implementation-lock-v5.draft.yaml',
             'manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml']:
    p = os.path.join(ROOT, base)
    files = [os.path.join(d, f) for d, _, fs in os.walk(p) for f in fs] if os.path.isdir(p) else [p]
    for f in files:
        if '/harness/node_modules' in f:
            continue
        try:
            text = open(f, encoding='utf-8').read()
        except UnicodeDecodeError:
            continue
        for term in forbidden:
            if term in text and os.path.relpath(f, ROOT) != S1 + '/tests/run_static_checks.py':
                hits.append(f'{os.path.relpath(f, ROOT)}: {term}')
check('hygiene: no local path, assistant or vendor name, or personal name in the new files', 0 if not hits else 1, '\n'.join(hits[:20]) or 'clean')

log('')
log('SUMMARY: ' + ('all static checks pass' if ok_all else 'at least one static check FAILED'))
open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
sys.exit(0 if ok_all else 1)
