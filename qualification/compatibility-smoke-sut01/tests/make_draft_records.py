# DRAFT generator (not an authorization). Computes every hash of the SUT-01 Android compatibility-smoke draft records by script
# over the files as they stand in the repository, and writes:
#   manifests/compatibility-smoke-implementation-lock-v5.draft.yaml              (successor implementation lock, draft)
#   manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml   (authorization APPIUM3-COMPAT-SMOKE-AUTH-04, PREPARED, NOT ISSUED)
#   qualification/compatibility-smoke-sut01/patches/compatibility-smoke-status.draft.patch   (mirror entry; NOT applied)
# Usage: PYTHONPATH=<directory holding a PyYAML installation> python3 make_draft_records.py <repository root>
# It only reads the repository and writes the three files above. Re-running it after a change to a locked file changes the draft.
import difflib
import hashlib
import json
import os
import subprocess
import sys

import yaml

ROOT = os.path.abspath(sys.argv[1])
S1 = 'qualification/compatibility-smoke-sut01'
WF = '.github/workflows/e06-compatibility-smoke-sut01.yml'
LOCK = 'manifests/compatibility-smoke-implementation-lock-v5.draft.yaml'
AUTH = 'manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml'
MIRROR = 'manifests/compatibility-smoke-status.yaml'
PATCH = S1 + '/patches/compatibility-smoke-status.draft.patch'
README = S1 + '/README.md'
TODAY = '2026-11-06'
ARTIFACTS = [
    (WF, 'ORCHESTRATOR', 'dispatch-only, fail-closed SUT-01 Android smoke workflow (installed under E06-SMOKE-CI-WRITE-AUTH-01)'),
    (S1 + '/smoke-common.sh', 'ORCHESTRATOR', 'build acquisition and digest verification, toolchain check, backend probe, Appium server start, harness invocation, stop records'),
    (S1 + '/run-smoke-android.sh', 'ORCHESTRATOR', 'Android platform entry point: emulator checks, clean start, probe, run'),
    (S1 + '/harness/package.json', 'ORCHESTRATOR', 'exact Appium core and driver pins (copied byte-identical from the SUT-02 harness)'),
    (S1 + '/harness/package-lock.json', 'ORCHESTRATOR', 'deterministic install input for npm ci (copied byte-identical from the SUT-02 harness)'),
    (S1 + '/harness/wd.mjs', 'ORCHESTRATOR', 'shared W3C WebDriver client (copied byte-identical from the SUT-02 harness, lock v4)'),
    (S1 + '/harness/smoke.mjs', 'ORCHESTRATOR', 'SUT-01 realization (REALIZATION.android), step runner, record writer'),
]


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(rel):
    with open(os.path.join(ROOT, rel), 'rb') as fh:
        return sha_bytes(fh.read())


def text(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as fh:
        return fh.read()


def realization_section():
    r = text(README)
    return r[r.index('## Concrete realization'):r.index('\n## Implementation')]


def command_sequence():
    s = text(S1 + '/harness/smoke.mjs')
    start = "  try {\n    await step('install and launch the pinned build (MC-01)'"
    end = "  } catch (e) {\n    failed = e.step"
    return s[s.index(start):s.index(end)]


def harness_realization_hash():
    code = ("import { realizationSha256 } from './" + S1 + "/harness/smoke.mjs'; "
            "process.stdout.write(realizationSha256());")
    out = subprocess.run(['node', '--input-type=module', '-e', code], cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def integrity(pkg):
    pl = json.loads(text(S1 + '/harness/package-lock.json'))
    return pl['packages'][pkg]['version'], pl['packages'][pkg]['integrity']


def main():
    # Consistency checks against the recorded pins (the draft never invents a value).
    tc = text('manifests/toolchain-manifest.yaml')
    android_sha = '1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4'
    assert android_sha in tc, 'android build digest is not the recorded pin'
    v4 = yaml.safe_load(text('manifests/compatibility-smoke-implementation-lock-v4.yaml'))
    policy_v4 = v4['governing_policy']['sha256']
    appium_v, appium_i = integrity('node_modules/appium')
    uia_v, uia_i = integrity('node_modules/appium-uiautomator2-driver')
    xcu_v, xcu_i = integrity('node_modules/appium-xcuitest-driver')
    assert (appium_v, uia_v, xcu_v) == ('3.7.0', '8.7.0', '12.13.2')
    assert appium_i == v4['toolchain']['appium_core']['integrity']
    assert uia_i == v4['toolchain']['android_driver']['integrity']

    arts = []
    for rel, role, desc in ARTIFACTS:
        arts.append({'path': rel, 'authored_by_role': role, 'role': desc,
                     'bytes': os.path.getsize(os.path.join(ROOT, rel)), 'sha256': sha_file(rel)})
    sec = realization_section()
    lock = {
        'record_class': 'COMPATIBILITY_SMOKE_IMPLEMENTATION_LOCK',
        'lock_id': 'APPIUM3-COMPAT-SMOKE-IMPLEMENTATION-LOCK-05',
        'study_id': 'EUS-2026-001',
        'protocol_version': 'v1',
        'created_on': TODAY,
        'created_by_role': 'ORCHESTRATOR',
        'status': 'DRAFT_NOT_EXECUTED',
        'active_execution_baseline': False,
        'human_decision': 'DRAFT only. The execution plan of 2026-11-05 (manifests/campaign-execution-plan-v1.yaml) fixes the minimal mobile suite (Android, SUT-01 versus SUT-02, N = 50 for E06, iOS deferred) and that a FAIL_RUNNER yields no data with no successor drafted in advance; it approves no smoke. The CI grant HD-7 was given on 2026-11-06 (E06-SMOKE-CI-WRITE-AUTH-01) and the failure risk was accepted (manifests/campaign-execution-decisions-v2.yaml, lines D and E); neither issues nor dispatches anything. Open decisions: HD-13 (lock version and namespace), HD-16 (launch activity).',
        'scope': {'sut_id': 'SUT-01', 'platforms': ['android'], 'runner': 'Appium 3', 'runner_version': '3.7.0', 'executions': 1,
                  'attempts_allowed': 1, 'ios': 'deferred (HD-1)'},
        'supersedes': None,
        'scenario_reference': {'id': 'CS-007', 'record': 'experiments/scenario-mappings/CS-007.yaml', 'status': 'DRAFT (not frozen; reference only; not an input to this smoke or to any campaign configuration)', 'realized_here': 'Android precondition (quick login of the documented account), sign-in, arrival at the catalogue', 'not_realized_here': 'catalogue item-identity oracle (DP-3 fallback)'},
        'topology': 'Android only; iOS deferred (HD-1)',
        'governance_route': 'protocol/agent-governance-v6.md, Section 3.4 (FROZEN-PRE-DATA 2026-11-06, carried from v5); its Section 3.7 does not cover this smoke',
        'supersedes_note': ('none: a new scope (SUT-01 Android). Lock v4 (SUT-02 iOS, the 9.7 remediation) is not superseded and stays the '
                            'execution baseline of APPIUM3-COMPAT-SMOKE-AUTH-03; lock v5 is the next free lock number, not a successor of v4.'),
        'governing_policy': {'path': 'protocol/mobile-runner-policy-v3.md', 'sha256_canonical_as_recorded_in_lock_v4': policy_v4,
                             'sha256_in_this_worktree': sha_file('protocol/mobile-runner-policy-v3.md'),
                             'note': 'computed by this script over the canonical tree, so it is the canonical value; it equals the value recorded in lock v4 while the policy is unchanged'},
        'hash_convention': 'SHA-256 (hex) of the exact committed bytes of each file at its repository path, computed by tests/make_draft_records.py',
        'artifacts': arts,
        'realization_section': {'path': README, 'heading': '## Concrete realization',
                                'extraction': 'UTF-8 text from the first character of "## Concrete realization" up to, and excluding, the line feed that immediately precedes "## Implementation"; SHA-256 of that string encoded as UTF-8',
                                'sha256': hashlib.sha256(sec.encode('utf-8')).hexdigest(), 'characters': len(sec),
                                'known_open_items': ['launch activity TBD (HD-16)']},
        'harness_realization_sha256': harness_realization_hash(),
        'harness_realization_note': 'realizationSha256() of harness/smoke.mjs (SHA-256 of the JSON of REALIZATION), recomputed by the gate through node',
        'command_sequence': {'extraction': 'UTF-8 text of harness/smoke.mjs from the first character of the line "  try {" that is followed by the line "    await step(\'install and launch the pinned build (MC-01)\'" up to, and excluding, the first character of the line "  } catch (e) {" that is followed by the line "    failed = e.step"',
                             'sha256': hashlib.sha256(command_sequence().encode('utf-8')).hexdigest()},
        'toolchain': {
            'appium_core': {'package': 'appium', 'version': appium_v, 'integrity': appium_i},
            'android_driver': {'package': 'appium-uiautomator2-driver', 'version': uia_v, 'integrity': uia_i},
            'ios_driver': {'package': 'appium-xcuitest-driver', 'version': xcu_v, 'integrity': xcu_i, 'used': False},
            'client': {'library': 'none', 'kind': 'harness-owned minimal W3C WebDriver client over node:http (wd.mjs, shared)'},
            'node': {'version': '22.23.2', 'provisioned_by': 'actions/setup-node@v4 (node-version pinned in the workflow; smoke-common.sh refuses any other version)'},
            'lockfile': {'path': S1 + '/harness/package-lock.json', 'lockfile_version': 3},
            'plugins': 'none',
        },
        'sut_builds': {'android': {
            'sut_component_id': 'SUT-01-android', 'repository': 'https://github.com/gsanchezm/OmniPizza', 'release': 'v1.1.8',
            'commit_sha_or_tag': '3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a', 'tag_object': 'lightweight tag, resolves directly to the commit',
            'asset': 'omnipizza-release.apk', 'url': 'https://github.com/gsanchezm/OmniPizza/releases/download/v1.1.8/omnipizza-release.apk',
            'bytes': 84930726, 'sha256': android_sha,
            'sha256_basis': 'GitHub release record of tag v1.1.8 (API, retrieved 2026-11-06T02:23Z UTC) publishes the same digest; the binary was not downloaded for this draft',
            'application_id': 'com.omnipizza.app', 'version_name': '1.1.8', 'version_code': None,
            'version_code_note': 'not in the pinned tree (the Android project is generated by prebuild); TBD'}},
        'substrates': {'android': 'GitHub-hosted ubuntu-24.04; ReactiveCircus/android-emulator-runner pinned at a421e43855164a8197daf9d8d40fe71c6996bb0d; system-images;android-35;google_apis;x86_64; profile pixel_7; environment_type EMULATED'},
        'backend': {'origin': 'https://omnipizza-backend.onrender.com', 'pin_source': 'frontend-mobile/src/api/client.ts line 27 at commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a',
                    'environment_type': 'PUBLIC_HOSTED', 'classification': 'HUMAN DECISION HD-3 (default: hosted read-only sign-in, HOSTED_MAPPING_UNVERIFIED disclosed)',
                    'probe': 'pre-runner: /health must answer HTTP 200 (smoke-common.sh smoke_probe_backend)'},
        'output_namespace': {'android': S1 + '/formal/<authorization id>/SUT-01-android/', 'rule': 'absent or empty before the execution; never the Mobilewright or SUT-02 trees; never raw-data/'},
        'attribution_implementation': 'policy v3, 9.1-9.4 as carried from v2; a failure after the session request is proposed FAIL_RUNNER with its basis (HUMAN DECISION HD-15 for backend-side refusals); a probe failure before the runner is NOT_EXECUTED / INFRASTRUCTURE',
        'change_rule': 'any change to a locked byte, the realization section, the governing policy, a build pin, or a toolchain pin requires a new lock file and a new authorization record naming it',
    }
    lock_text = ('# Compatibility-smoke implementation lock v5 -- DRAFT. EUS-2026-001. SUT-01 (OmniPizza) x Android x Appium 3 (3.7.0).\n'
                 '# Generated by ' + S1 + '/tests/make_draft_records.py: every hash below is computed over the files as they stand in the repository.\n'
                 '# Not an authorization and not an execution baseline. The readiness gate of .github/workflows/e06-compatibility-smoke-sut01.yml recomputes all hashes.\n')
    lock_body = yaml.safe_dump(lock, sort_keys=False, allow_unicode=True, width=10000)
    with open(os.path.join(ROOT, LOCK), 'w', encoding='utf-8') as fh:
        fh.write(lock_text + lock_body)
    lock_sha = sha_file(LOCK)

    auth = {
        'authorization_id': 'APPIUM3-COMPAT-SMOKE-AUTH-04',
        'authorization_type': 'COMPATIBILITY_SMOKE_EXECUTION',
        'record_class': 'COMPATIBILITY_SMOKE_EXECUTION_AUTHORIZATION_DRAFT',
        'status': 'PREPARED_AWAITING_EXPLICIT_HUMAN_AUTHORIZATION',
        'record_validity': None,
        'authorizes_execution': False,
        'dispatch_eligibility': 'NOT_ELIGIBLE_UNTIL_ISSUED',
        'dispatch_performed': False,
        'issued_by': None,
        'issued_at': None,
        'issued_under_instruction': None,
        'execution_at_preparation': 'none: no workflow run, no Appium, no emulator, no SUT-01 launch, no result, no mirror change',
        'study_id': 'EUS-2026-001',
        'protocol_version': 'v1',
        'prepared_by_role': 'ORCHESTRATOR',
        'prepared_on': TODAY,
        'prepared_under': 'preparation only; no authorization exists until the explicit human issuance (HUMAN DECISION HD-13 names this id)',
        'governing_policy': 'protocol/mobile-runner-policy-v3.md',
        'scenario_reference': 'CS-007 (DRAFT reference only; experiments/scenario-mappings/CS-007.yaml)',
        'plan_reference': 'manifests/campaign-execution-plan-v1.yaml (approvals_not_given lists APPIUM3-COMPAT-SMOKE-AUTH-04; its approval is still required)',
        'governance_route': "protocol/agent-governance-v6.md, Section 3.4 (FROZEN-PRE-DATA 2026-11-06, carried from v5); the dispatch needs the human research lead's explicit approval of that exact dispatch; Section 3.7 of v6 does not apply",
        'executing_role': 'ORCHESTRATOR (protocol/agent-governance-v6.md, Section 3.4)',
        'scope': {'sut_id': 'SUT-01', 'platforms': ['android'], 'runner': 'Appium 3', 'runner_version': '3.7.0', 'executions': 1,
                  'attempts_allowed': 1, 'result_vocabulary': ['PASS', 'FAIL_RUNNER', 'NOT_EXECUTED'],
                  'not_in_scope': 'SUT-01 iOS (HD-1); SUT-02 of any platform; any other SUT or runner; any Mobilewright execution; E06 START or any E06 measurement; any restoration or remediation record'},
        'implementation_lock': {'path': LOCK, 'sha256': lock_sha, 'status_at_this_draft': 'DRAFT_NOT_EXECUTED'},
        'realization_section_sha256': lock['realization_section']['sha256'],
        'harness_realization_sha256': lock['harness_realization_sha256'],
        'command_sequence_sha256': lock['command_sequence']['sha256'],
        'workflow': {'path': WF, 'trigger': 'workflow_dispatch only', 'inputs': {'instruction_id': 'APPIUM3-COMPAT-SMOKE-AUTH-04', 'confirm': 'EXECUTE-COMPATIBILITY-SMOKE-SUT01'},
                     'topology': 'readiness gate, then one Android job on ubuntu-24.04 (no iOS job)', 'rerun': 'refused (run attempt must be 1)',
                     'status': 'installed under E06-SMOKE-CI-WRITE-AUTH-01 (2026-11-06); refuses every dispatch until AUTH-04 is issued'},
        'output_namespace': {'android': S1 + '/formal/APPIUM3-COMPAT-SMOKE-AUTH-04/SUT-01-android/', 'state_at_preparation': 'absent'},
        'launch_prompt': {'frozen_copy': None, 'sha256': None, 'prompt_version_id': None,
                          'owed': 'the frozen launch prompt is not written: it exists only at issuance (the naming orchestrator-compat-smoke-sut01-v<n> is the draft choice; the gate requires prompts/frozen/<prompt_version_id>.md)'},
        'issuance_procedure': [
            'the human research lead reviews the draft files (this folder, the lock, this record, the workflow, the mirror patch) in a published snapshot (HD-14)',
            'on a separate explicit human issuance instruction only, the ORCHESTRATOR writes the frozen launch prompt, applies the mirror patch, and promotes this record in place to status ISSUED, record_validity VALID, authorizes_execution true, dispatch_eligibility ELIGIBLE, with issued_by and issued_at',
            'the issued state is published (a public export; GitHub Actions evaluates only the public repository) before any dispatch',
            'on a further separate explicit human dispatch instruction only, exactly one dispatch; the dispatch is recorded before it is made; afterwards this record is closed in place as CONSUMED_AFTER_DISPATCH',
        ],
        'open_before_issuance': ['HD-3 (backend classification)', 'HD-13 (namespace)',
                                 'HD-15 (backend-side refusal attribution)', 'HD-16 (launch activity)', 'HD-17 (locator match rule)', 'HD-18 (E06 NOT_STARTED precondition)'],
        'resolved_2026_11_06': ['HD-2 (risk acceptance for a FAIL_RUNNER: accepted, policy v3 as written)', 'HD-7 (CI grant: E06-SMOKE-CI-WRITE-AUTH-01)', 'HD-19 (governance route: Section 3.4 sentence updated at the freeze of v6, HD-8)'],
    }
    auth_text = ('# Compatibility-smoke execution authorization APPIUM3-COMPAT-SMOKE-AUTH-04 -- PREPARED, NOT ISSUED (DRAFT).\n'
                 '# Generated by ' + S1 + '/tests/make_draft_records.py. Authorizes nothing. dispatch_eligibility is NOT_ELIGIBLE_UNTIL_ISSUED.\n'
                 '# The record class, status, and empty issuance fields follow the PREPARED lifecycle that the static checks of the validation workflow require.\n')
    with open(os.path.join(ROOT, AUTH), 'w', encoding='utf-8') as fh:
        fh.write(auth_text + yaml.safe_dump(auth, sort_keys=False, allow_unicode=True, width=10000))

    # Mirror entry (NOT applied): appended after the last entry of manifests/compatibility-smoke-status.yaml.
    old = text(MIRROR)
    entry = ('  - sut_id: SUT-01\n'
             '    platform: android\n'
             '    runner: "Appium 3"\n'
             '    runner_version: null\n'
             '    result: NOT_STARTED  # DRAFT patch (not applied): no smoke has been executed for SUT-01 Android; transcribed only after a recorded row\n'
             '    qualifier_record: null\n'
             '    executed_at: null\n'
             '    authorization_id: null\n'
             '    transcribed_by: null\n'
             '    transcribed_at: null\n'
             '    e03_condition: null  # no E03 condition uses SUT-01 mobile surfaces; E06 is the campaign that will use it\n')
    new = old if old.endswith('\n') else old + '\n'
    new = new + entry
    diff = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                fromfile='a/' + MIRROR, tofile='b/' + MIRROR)
    header = ('# DRAFT patch, NOT applied. Adds the SUT-01 Android mirror entry (NOT_STARTED) to manifests/compatibility-smoke-status.yaml.\n'
              '# Apply only with the issuance of APPIUM3-COMPAT-SMOKE-AUTH-04 (HUMAN DECISION HD-13). Generated by ' + S1 + '/tests/make_draft_records.py.\n')
    with open(os.path.join(ROOT, PATCH), 'w', encoding='utf-8') as fh:
        fh.write(header + ''.join(diff))
    print('lock sha256', lock_sha)
    print('auth written', AUTH)
    print('patch written', PATCH)
    print('harness realization', lock['harness_realization_sha256'])
    print('realization section', lock['realization_section']['sha256'])
    print('command sequence', lock['command_sequence']['sha256'])


if __name__ == '__main__':
    main()
