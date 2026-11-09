# Static test of the readiness gate of .github/workflows/e06-compatibility-smoke-sut01.yml (DRAFT).
# It extracts the gate script from the workflow file (the run block of the step "gate"), runs it with the working directory set to
# a repository tree, and checks the outcome against a must-pass and a must-fail matrix. Trees are copies: the repository is never
# modified. Nothing is dispatched, installed, or executed beyond the gate script and the pure node function of the harness.
# Usage: PYTHONPATH=<directory holding a PyYAML installation> python3 run_gate_matrix.py <repository root> <output file>
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

REPO = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
S1 = 'qualification/compatibility-smoke-sut01'
WF = '.github/workflows/e06-compatibility-smoke-sut01.yml'
AUTH = 'manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml'
LOCK = 'manifests/compatibility-smoke-implementation-lock-v5.draft.yaml'
INSTR = 'APPIUM3-COMPAT-SMOKE-AUTH-04'
PV = 'orchestrator-compat-smoke-sut01-v1'
CONFIRM = 'EXECUTE-COMPATIBILITY-SMOKE-SUT01'
SUBSET = ['manifests', 'protocol', 'qualification/compatibility-smoke', S1, '.github/workflows', 'PUBLIC-EXPORT-MANIFEST.yaml']
GEN = os.path.join(REPO, S1, 'tests', 'make_draft_records.py')
SCRATCH = tempfile.mkdtemp(prefix='gate-matrix-')
lines_out = []


def say(s=''):
    lines_out.append(s)
    print(s)


def gate_code():
    doc = yaml.safe_load(open(os.path.join(REPO, WF), encoding='utf-8'))
    step = [s for s in doc['jobs']['gate']['steps'] if s.get('id') == 'gate'][0]
    run = step['run']
    begin = run.index("python3 - <<'PY'\n") + len("python3 - <<'PY'\n")
    end = run.index('\nPY\n', begin)
    return run[begin:end] + '\n'


def copy_tree(src, dst):
    for part in SUBSET:
        s, d = os.path.join(src, part), os.path.join(dst, part)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        elif os.path.isfile(s):
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)


def run_gate(tree, confirm=CONFIRM, instr=INSTR, attempt='1'):
    code_path = os.path.join(SCRATCH, 'gate_code.py')
    with open(code_path, 'w', encoding='utf-8') as fh:
        fh.write(GATE)
    out_file = os.path.join(SCRATCH, 'github_output.txt')
    if os.path.exists(out_file):
        os.remove(out_file)
    env = dict(os.environ)
    env.update({'SMOKE_CONFIRM': confirm, 'SMOKE_INSTRUCTION_ID': instr, 'GITHUB_RUN_ATTEMPT': attempt, 'GITHUB_OUTPUT': out_file})
    r = subprocess.run([sys.executable, code_path], cwd=tree, env=env, capture_output=True, text=True)
    fails = [l for l in r.stdout.splitlines() if l.startswith('FAIL ')]
    passes = [l for l in r.stdout.splitlines() if l.startswith('PASS ')]
    return r.returncode, passes, fails, r.stdout + r.stderr


def rewrite(tree, rel, fn):
    p = os.path.join(tree, rel)
    s = open(p, encoding='utf-8').read()
    t = fn(s)
    assert t != s, 'mutation did not change ' + rel
    open(p, 'w', encoding='utf-8').write(t)


def regen(tree):
    env = dict(os.environ)
    r = subprocess.run([sys.executable, GEN, tree], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr


def load_yaml(tree, rel):
    return yaml.safe_load(open(os.path.join(tree, rel), encoding='utf-8'))


def dump_yaml(tree, rel, obj):
    head = open(os.path.join(tree, rel), encoding='utf-8').read().split('\n', 3)
    comment = '\n'.join(l for l in open(os.path.join(tree, rel), encoding='utf-8').read().splitlines() if l.startswith('#')) + '\n'
    open(os.path.join(tree, rel), 'w', encoding='utf-8').write(comment + yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=10000))


def set_artifact_sha(tree, rel_path, new_sha):
    lock = load_yaml(tree, LOCK)
    for a in lock['artifacts']:
        if a['path'] == rel_path:
            a['sha256'] = new_sha
    dump_yaml(tree, LOCK, lock)
    # the auth record pins the lock file's hash; refresh it so that only the intended gate fails
    refresh_auth_lock_hash(tree)


def sha_of(tree, rel):
    import hashlib
    return hashlib.sha256(open(os.path.join(tree, rel), 'rb').read()).hexdigest()


def refresh_auth_lock_hash(tree):
    auth = load_yaml(tree, AUTH)
    auth['implementation_lock']['sha256'] = sha_of(tree, LOCK)
    dump_yaml(tree, AUTH, auth)


def make_pass_base():
    base = os.path.join(SCRATCH, 'base')
    os.makedirs(base)
    copy_tree(REPO, base)
    # the must-pass fixture resolves the one documented open item (launch activity) and issues the record in the fixture only
    rewrite(base, S1 + '/README.md', lambda s: s.replace('TBD', 'not fixed'))  # fixture only: resolves every open TBD of the realization
    regen(base)
    auth = load_yaml(base, AUTH)
    prompt_rel = 'prompts/frozen/' + PV + '.md'
    os.makedirs(os.path.join(base, 'prompts', 'frozen'), exist_ok=True)
    prompt_text = ('# Frozen launch prompt (fixture only)\n\nStatus: FROZEN LAUNCH PROMPT OF ' + INSTR + '. Prompt version: ' + PV + '.\n')
    open(os.path.join(base, prompt_rel), 'w', encoding='utf-8').write(prompt_text)
    auth.update({'record_class': 'COMPATIBILITY_SMOKE_EXECUTION_AUTHORIZATION', 'status': 'ISSUED', 'record_validity': 'VALID',
                 'authorizes_execution': True, 'dispatch_eligibility': 'ELIGIBLE', 'dispatch_performed': False,
                 'issued_by': 'fixture-human-research-lead', 'issued_at': '2026-11-05',
                 'authorization_type': 'COMPATIBILITY_SMOKE_EXECUTION'})
    auth['launch_prompt'] = {'frozen_copy': prompt_rel, 'sha256': sha_of(base, prompt_rel), 'prompt_version_id': PV}
    dump_yaml(base, AUTH, auth)
    # the mirror patch is applied in the fixture
    patch_text = open(os.path.join(base, S1, 'patches', 'compatibility-smoke-status.draft.patch'), encoding='utf-8').read()
    added = [l[1:] for l in patch_text.splitlines() if l.startswith('+') and not l.startswith('+++')]
    mirror_path = os.path.join(base, 'manifests', 'compatibility-smoke-status.yaml')
    open(mirror_path, 'a', encoding='utf-8').write('\n'.join(added) + '\n')
    return base


def case(name, expect_exit, expect_fail_substr=None, mutate=None, base=None, tree=None, **kw):
    if tree is None:
        tree = os.path.join(SCRATCH, 'case-' + str(len(lines_out)))
        shutil.copytree(base, tree)
        if mutate:
            mutate(tree)
    rc, passes, fails, full = run_gate(tree, **kw)
    ok = rc == expect_exit and (expect_fail_substr is None or any(expect_fail_substr in f for f in fails))
    say(f'[{"OK  " if ok else "BAD "}] {name}: exit {rc} (expected {expect_exit}); PASS {len(passes)}, FAIL {len(fails)}')
    for f in fails:
        say('      ' + f)
    if expect_fail_substr and not any(expect_fail_substr in f for f in fails):
        say('      !! expected a FAIL containing: ' + expect_fail_substr)
    return ok, passes, fails, full


GATE = gate_code()
results = []

# 1. the repository as it stands (the draft is not issued): must refuse, and the study-wide mobile-runner rule must hold on the real data
rc, passes, fails, full = run_gate(REPO)
say(f'[INFO] as-is repository: exit {rc}; PASS {len(passes)}, FAIL {len(fails)}')
for l in full.splitlines():
    if l.startswith(('PASS ', 'FAIL ')):
        say('      ' + l)
study_gates = [p for p in passes if 'mobile-runner' in p or 'FAIL_RUNNER' in p or 'admissible study-wide' in p or 'SELECTED' in p]
say(f'[INFO] study-wide admissibility gates passing on the as-is tree: {len(study_gates)}')
results.append(rc == 1 and any('exactly one SUT-01 smoke authorization record' in f or 'status is exactly ISSUED' in f for f in fails))

base = make_pass_base()
ok, passes, fails, full = case('must-pass fixture (issued record, frozen prompt, lock hashes, realization complete, mirror NOT_STARTED)', 0, base=base)
results.append(ok)
for l in full.splitlines():
    if l.startswith(('PASS ', 'FAIL ')):
        say('      ' + l)

MUTATIONS = [
    ('record PREPARED again (status and dispatch fields as drafted)', 1, 'status is exactly ISSUED',
     lambda t: refresh_auth_lock_hash(t) or dump_yaml(t, AUTH, {**load_yaml(t, AUTH), 'status': 'PREPARED_AWAITING_EXPLICIT_HUMAN_AUTHORIZATION', 'record_validity': None, 'authorizes_execution': False, 'dispatch_eligibility': 'NOT_ELIGIBLE_UNTIL_ISSUED'})),
    ('dispatch already performed', 1, 'has not been dispatched before',
     lambda t: dump_yaml(t, AUTH, {**load_yaml(t, AUTH), 'dispatch_performed': True})),
    ('issued by an agent role', 1, 'issued_by is a human identity',
     lambda t: dump_yaml(t, AUTH, {**load_yaml(t, AUTH), 'issued_by': 'orchestrator'})),
    ('dispatch eligibility consumed', 1, 'dispatch_eligibility is exactly ELIGIBLE',
     lambda t: dump_yaml(t, AUTH, {**load_yaml(t, AUTH), 'dispatch_eligibility': 'CONSUMED_AFTER_DISPATCH'})),
    ('scope widened to iOS', 1, 'scope is SUT-01 Android only',
     lambda t: dump_yaml(t, AUTH, {**load_yaml(t, AUTH), 'scope': {**load_yaml(t, AUTH)['scope'], 'platforms': ['android', 'ios']}})),
    ('frozen launch prompt missing', 1, 'launch prompt frozen copy present',
     lambda t: os.remove(os.path.join(t, 'prompts', 'frozen', PV + '.md'))),
    ('lock file edited after the record was written', 1, 'implementation lock file present and equal',
     lambda t: rewrite(t, LOCK, lambda s: s.replace('created_on: ', 'created_on_edit: '))),
    ('an execution-critical artifact edited without a new lock', 1, 'lock hash matches: ' + S1 + '/smoke-common.sh',
     lambda t: rewrite(t, S1 + '/smoke-common.sh', lambda s: s + '\n# edited\n')),
    ('the concrete-realization section edited without a new lock', 1, 'concrete-realization section hash matches',
     lambda t: rewrite(t, S1 + '/README.md', lambda s: s.replace('Sign In', 'Sign-In'))),
    ('the REALIZATION constant changed, artifact hash refreshed, realization hash not', 1, 'harness REALIZATION hash',
     lambda t: (rewrite(t, S1 + '/harness/smoke.mjs', lambda s: s.replace("navigate: { using: 'accessibility id', value: 'Standard' }", "navigate: { using: 'accessibility id', value: 'Problem' }")), set_artifact_sha(t, S1 + '/harness/smoke.mjs', sha_of(t, S1 + '/harness/smoke.mjs')))),
    ('the step sequence changed, artifact hash refreshed, sequence hash not', 1, 'step-sequence hash',
     lambda t: (rewrite(t, S1 + '/harness/smoke.mjs', lambda s: s.replace("await step('capture the terminal artifacts (MC-10)'", "await step('capture the terminal artifacts (MC-10), edited'")), set_artifact_sha(t, S1 + '/harness/smoke.mjs', sha_of(t, S1 + '/harness/smoke.mjs')))),
    ('the Android APK digest changed in the build pin', 1, 'Android build pin',
     lambda t: (rewrite(t, S1 + '/smoke-common.sh', lambda s: s.replace('1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4', '0' * 64)), set_artifact_sha(t, S1 + '/smoke-common.sh', sha_of(t, S1 + '/smoke-common.sh')))),
    ('the TBD launch activity reintroduced into the realization', 1, 'no null and no TBD',
     lambda t: (rewrite(t, S1 + '/README.md', lambda s: s.replace('Launch activity: not fixed', 'Launch activity: TBD')), dump_yaml(t, LOCK, {**load_yaml(t, LOCK), 'realization_section': {**load_yaml(t, LOCK)['realization_section'], 'sha256': hashlib_sha(sec_of(t))}}), refresh_auth_lock_hash(t))),
    ('the historical AUTH-02 lineage record removed (the retained FAIL_RUNNER is then unverified)', 1, 'remediation lineage record',
     lambda t: os.remove(os.path.join(t, 'manifests', 'mobile-runner-remediation-v1.yaml'))),
    ('study-level status UNRESOLVED_AFTER_FALLBACK_FAILURE', 1, 'study-level mobile-runner status is SELECTED',
     lambda t: rewrite(t, 'manifests/toolchain-manifest.yaml', lambda s: s.replace('mobile_runner_status: SELECTED', 'mobile_runner_status: UNRESOLVED_AFTER_FALLBACK_FAILURE', 1))),
    ('E06 already IN_PROGRESS', 1, 'E06-cross-platform-parity is NOT_STARTED',
     lambda t: rewrite(t, 'manifests/study-manifest.yaml', lambda s: s.replace('- id: E06-cross-platform-parity\n    status: NOT_STARTED', '- id: E06-cross-platform-parity\n    status: IN_PROGRESS', 1))),
    ('an output namespace already holds a file', 1, 'output namespace absent or empty',
     lambda t: (os.makedirs(os.path.join(t, S1, 'formal', INSTR, 'SUT-01-android'), exist_ok=True), open(os.path.join(t, S1, 'formal', INSTR, 'SUT-01-android', 'record.json'), 'w').write('{}'))),
    ('a smoke row for SUT-01 Android already in the README', 1, 'holds no row for SUT-01',
     lambda t: rewrite(t, S1 + '/README.md', lambda s: s.replace('| sut_id | platform (android / ios) | environment_type (EMULATED / SIMULATED) | pinned build identity | timestamp | runner version | steps executed (MC ids) | result | artifacts | notes / reason |\n|---|---|---|---|---|---|---|---|---|---|\n',
                                                                 '| sut_id | platform (android / ios) | environment_type (EMULATED / SIMULATED) | pinned build identity | timestamp | runner version | steps executed (MC ids) | result | artifacts | notes / reason |\n|---|---|---|---|---|---|---|---|---|---|\n| SUT-01 | android | EMULATED | x | x | x | x | PASS | x | x |\n', 1))),
    ('mirror entry transcribed as PASS without a record', 1, 'mirror holds exactly one SUT-01 android entry',
     lambda t: rewrite(t, 'manifests/compatibility-smoke-status.yaml', lambda s: s.replace('    result: NOT_STARTED  # DRAFT patch', '    result: PASS  # DRAFT patch'))),
    ('a FAIL_RUNNER of the selected runner recorded for SUT-01 Android', 1, 'no unresolved FAIL_RUNNER',
     lambda t: rewrite(t, 'manifests/compatibility-smoke-status.yaml', lambda s: s.replace('    result: NOT_STARTED  # DRAFT patch', '    result: FAIL_RUNNER  # DRAFT patch'))),
    ('wrong confirmation token', 1, 'explicit confirmation token', None),
    ('a GitHub re-run (attempt 2)', 1, 'run attempt 1', None),
]


def sec_of(t):
    r = open(os.path.join(t, S1, 'README.md'), encoding='utf-8').read()
    return r[r.index('## Concrete realization'):r.index('\n## Implementation')]


def hashlib_sha(s):
    import hashlib
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


for name, code, substr, mut in MUTATIONS:
    if name == 'wrong confirmation token':
        ok, *_ = case(name, code, substr, base=base, confirm='WRONG')
    elif name == 'a GitHub re-run (attempt 2)':
        ok, *_ = case(name, code, substr, base=base, attempt='2')
    else:
        ok, *_ = case(name, code, substr, mutate=mut, base=base)
    results.append(ok)

say('')
say(f'SUMMARY: {sum(1 for r in results if r)} of {len(results)} checks as expected')
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines_out) + '\n')
shutil.rmtree(SCRATCH, ignore_errors=True)
sys.exit(0 if all(results) else 1)
