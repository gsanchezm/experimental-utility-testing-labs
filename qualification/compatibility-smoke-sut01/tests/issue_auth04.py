# Issuance script of APPIUM3-COMPAT-SMOKE-AUTH-04 (SUT-01 x Android compatibility smoke). NOT RUN until the human research lead's explicit issuance.
# Authorizes nothing by existing. On the human issuance only, the ORCHESTRATOR runs it once, over the repository root, with the verbatim text of
# the human answer in a file. It writes: the frozen launch prompt (rendered from the working copy; two placeholders only), the SUT-01 Android
# mirror entry (NOT_STARTED; applied from the draft patch), the promotion of the lock to the issued baseline, the promotion in place of the
# authorization record (ISSUED / VALID / ELIGIBLE, nothing dispatched), and the status paragraph of the package README.
# It refuses to run if the frozen prompt already exists, if the record is not the PREPARED draft, or if the mirror already has a SUT-01 entry.
# Usage: PYTHONPATH=<PyYAML dir> python3 issue_auth04.py <repository root> <answer text file> <issuer> <YYYY-MM-DD>
import hashlib
import json
import os
import re
import sys

import yaml

ROOT, ANSWER, ISSUER, DATE = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', DATE)
S1 = 'qualification/compatibility-smoke-sut01'
LOCK = 'manifests/compatibility-smoke-implementation-lock-v5.draft.yaml'
AUTH = 'manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml'
MIRROR = 'manifests/compatibility-smoke-status.yaml'
PATCH = S1 + '/patches/compatibility-smoke-status.draft.patch'
README = S1 + '/README.md'
WORKING = 'prompts/working/orchestrator-compat-smoke-sut01-v1.md'
PV = 'orchestrator-compat-smoke-sut01-v1'
FROZEN = 'prompts/frozen/' + PV + '.md'
INSTR = 'APPIUM3-COMPAT-SMOKE-AUTH-04'


def p(rel):
    return os.path.join(ROOT, rel)


def rd(rel):
    with open(p(rel), encoding='utf-8', newline='') as fh:
        return fh.read()


def wr(rel, s):
    with open(p(rel), 'w', encoding='utf-8', newline='') as fh:
        fh.write(s)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(rel):
    with open(p(rel), 'rb') as fh:
        return sha_bytes(fh.read())


answer = open(ANSWER, encoding='utf-8', newline='').read()
assert answer.strip(), 'empty answer text'
answer_sha = sha_bytes(answer.encode('utf-8'))

# --- refusals
assert not os.path.exists(p(FROZEN)), 'frozen prompt already exists'
auth = yaml.safe_load(rd(AUTH))
assert auth['authorization_id'] == INSTR and auth['status'] == 'PREPARED_AWAITING_EXPLICIT_HUMAN_AUTHORIZATION' and auth['record_validity'] is None
assert auth['dispatch_eligibility'] == 'NOT_ELIGIBLE_UNTIL_ISSUED' and auth['dispatch_performed'] is False
mirror = yaml.safe_load(rd(MIRROR))
assert not [e for e in mirror['entries'] if e.get('sut_id') == 'SUT-01'], 'mirror already has a SUT-01 entry'
lock_text = rd(LOCK)
assert 'status: DRAFT_NOT_EXECUTED' in lock_text and 'active_execution_baseline: false' in lock_text

# --- 1. frozen launch prompt (exactly two placeholders rendered)
work = rd(WORKING)
assert work.count('{{PROMPT_STATUS}}') == 2 and work.count('{{INSTRUCTION_DATE}}') == 2, (work.count('{{PROMPT_STATUS}}'), work.count('{{INSTRUCTION_DATE}}'))
frozen = work.replace('{{PROMPT_STATUS}}', 'FROZEN LAUNCH PROMPT OF ' + INSTR).replace('{{INSTRUCTION_DATE}}', DATE)
assert re.search(r'\{\{[A-Z_]+\}\}', frozen) is None
os.makedirs(os.path.dirname(p(FROZEN)), exist_ok=True)
wr(FROZEN, frozen)
frozen_sha = sha_file(FROZEN)

# --- 2. mirror entry (new entry only, from the draft patch)
patch = rd(PATCH)
added = [l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++')]
old = rd(MIRROR)
wr(MIRROR, (old if old.endswith('\n') else old + '\n') + '\n'.join(added) + '\n')

# --- 3. lock promoted to the issued baseline (text edits; hashes of the locked artifacts are unchanged)
lock_text = lock_text.replace('# Compatibility-smoke implementation lock v5 -- DRAFT.', '# Compatibility-smoke implementation lock v5 -- ISSUED BASELINE of ' + INSTR + ' (issued ' + DATE + ', not executed).', 1)
lock_text = lock_text.replace('# Not an authorization and not an execution baseline.', '# Became the execution baseline through the issuance of ' + INSTR + ' (the filename suffix draft is historical); it is not itself an authorization.', 1)
lock_text = lock_text.replace('status: DRAFT_NOT_EXECUTED', 'status: ISSUED_BASELINE_NOT_EXECUTED', 1)
lock_text = lock_text.replace('active_execution_baseline: false', 'active_execution_baseline: true', 1)
lock_text = lock_text.replace('human_decision: ', 'issued_with_authorization: ' + INSTR + '\nissued_on: ' + DATE + '\nhuman_decision: ', 1)
wr(LOCK, lock_text)
lock_sha = sha_file(LOCK)

# --- 4. authorization record promoted in place
before = {k: auth[k] for k in ('record_class', 'status', 'record_validity', 'authorizes_execution', 'dispatch_eligibility', 'dispatch_performed', 'issued_by', 'issued_at')}
auth['record_class'] = 'COMPATIBILITY_SMOKE_EXECUTION_AUTHORIZATION'
auth['status'] = 'ISSUED'
auth['record_validity'] = 'VALID'
auth['authorizes_execution'] = True
auth['dispatch_eligibility'] = 'ELIGIBLE'
auth['dispatch_performed'] = False
auth['issued_by'] = ISSUER
auth['issued_at'] = DATE
auth['issued_under_instruction'] = "the human research lead's answer of " + DATE + " to the ORCHESTRATOR's issuance dialog of APPIUM3-COMPAT-SMOKE-AUTH-04; verbatim below"
auth['issuance_instruction_verbatim'] = {'text': answer, 'sha256': answer_sha, 'sha256_convention': 'UTF-8 text exactly as stored, without a trailing line feed'}
auth['lifecycle_before_issuance'] = before
auth['execution_at_issuance'] = 'none: no workflow run, no Appium, no emulator, no SUT-01 launch, no result; static checks only (the readiness gate on the issued tree and the fixture matrix)'
auth['publication_before_dispatch'] = 'required: GitHub Actions evaluates only the public repository, so the issued record, the frozen launch prompt, every locked file, the README and the lock must be present in a published snapshot (a public export, needing its own explicit human approval) before any dispatch'
auth['dispatch_requires'] = 'another, separate explicit human dispatch instruction naming this authorization; exactly one dispatch; the dispatch recorded before it is made and the run identity after; this record then closed in place (dispatch_performed true, dispatch_eligibility CONSUMED_AFTER_DISPATCH)'
auth['implementation_lock'] = {'path': LOCK, 'sha256': lock_sha, 'status_at_issuance': 'ISSUED_BASELINE_NOT_EXECUTED'}
auth['launch_prompt'] = {'frozen_copy': FROZEN, 'sha256': frozen_sha, 'prompt_version_id': PV, 'working_copy': WORKING, 'working_copy_sha256': sha_file(WORKING)}
auth['workflow']['status'] = 'installed under E06-SMOKE-CI-WRITE-AUTH-01 (2026-11-06); passes its readiness gate on the issued tree; dispatch needs the separate human instruction'
auth['open_before_issuance'] = []
auth.setdefault('resolved_2026_11_20', []).append('HD-13 (namespace: APPIUM3-COMPAT-SMOKE-AUTH-04, lock v5, record prefix sut01-; working default accepted at the issuance)')
header = ('# Compatibility-smoke execution authorization APPIUM3-COMPAT-SMOKE-AUTH-04 (SUT-01 x Android x Appium 3) -- ISSUED ' + DATE + ', NOT DISPATCHED.\n'
          '# Promoted in place from its PREPARED draft (git history shows the PREPARED text); the draft filename suffix is historical and no second file may carry this authorization_id.\n'
          '# The lifecycle fields (record_class, status, record_validity, issued_by, issued_at, authorizes_execution, dispatch_eligibility, dispatch_performed) are authoritative.\n'
          '# Issuance is not publication and not dispatch: the dispatch needs a further, separate explicit human instruction after the issued state is public.\n')
wr(AUTH, header + yaml.safe_dump(auth, sort_keys=False, allow_unicode=True, width=10000))

# --- 5. package README status paragraph
r = rd(README)
m = re.search(r'## Status\n\n(DRAFT\. Prepared, not issued, not executed\..*?)\n\n', r, re.S)
assert m, 'status paragraph not found'
new_status = ('ISSUED on ' + DATE + ' (' + INSTR + '), not dispatched, not executed. The authorization record `' + AUTH + '` is ISSUED / VALID / ELIGIBLE with dispatch_performed false; '
              'the implementation lock `' + LOCK + '` is the issued baseline; the frozen launch prompt is `' + FROZEN + '`. A dispatch needs the publication of this state (a public export) and a separate explicit human dispatch instruction. '
              'No row of the Smoke records table below is filled. Open items and decisions are in `IMPLEMENTATION-NOTES.md` and in manifests/campaign-execution-decisions-v16.yaml.')
r = r[:m.start(1)] + new_status + r[m.end(1):]
wr(README, r)

print('frozen prompt', FROZEN, frozen_sha)
print('lock', lock_sha)
print('auth', sha_file(AUTH))
print('mirror entry added; answer sha', answer_sha)
