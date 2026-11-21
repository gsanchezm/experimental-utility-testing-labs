"""The measured-execution gate of .github/workflows/e06-measured-execution.yml, executed on fictitious and real trees.

DRAFT (operation OP-PREP-E06-EXECUTOR). The gate script is extracted from the workflow (step id "gates", the python heredoc) and run with the
working directory set to a prepared tree and the GATE_* inputs in its environment. The common records of the tree (START, configuration, dispatch
authorization, frozen prompt, governance, mapping) are fictitious: fixture identifiers, not issued authorizations. The conditions file, the SUT
manifest, the measured workflow itself, and, for the Android conditions, the real mobile records (the toolchain, the mirror, both QUALIFIER records, and
the remediation lineage) are the real files of this repository. Every must-fail case changes exactly one thing and must fail on the gate it names. The
as-is case runs against the files of this repository and must fail closed, because E06 has no START, no locked configuration, no dispatch
authorization, and no frozen prompt. The Android admissibility block is the lift of the G-7 block of e03-measured-execution.yml (tests/lift_g7.py);
LiftTests fails when it drifts. Requires PyYAML (the gate tests are skipped without it).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
WORKFLOW_REL = '.github/workflows/e06-measured-execution.yml'
WORKFLOW = os.path.join(REPO, WORKFLOW_REL)
CONDITIONS_REL = 'experiments/E06-cross-platform-parity/conditions-draft.json'
sys.path.insert(0, HERE)

try:
    import yaml
except ImportError:
    yaml = None

PV = 'ORCHESTRATOR-E06-cross-platform-parity-v1'
AUTH_START = 'TEST-FIXTURE-E06-START'
AUTH_DISPATCH = 'TEST-FIXTURE-E06-DISPATCH-SUT01'
IMPL_TEXT = b'fixture entry script for the gate tests only\n'
IMPL_SHA = hashlib.sha256(IMPL_TEXT).hexdigest()
PROMPT_TEXT = f'fixture prompt {PV}\n'
PROMPT_SHA = hashlib.sha256(PROMPT_TEXT.encode('utf-8')).hexdigest()

# The real mobile records that the Android admissibility block reads (found with an audit hook on the unmodified G-7 block of the E03 workflow).
# The Android trees of these tests are built from them, so the block runs on the real remediation lineage, the real mirror, and both real
# QUALIFIER records; every must-fail case changes exactly one thing in them.
REAL_MOBILE_FILES = [
    'manifests/appium3-compat-smoke-auth-02-run-v1.yaml',
    'manifests/appium3-compat-smoke-auth-03-postrun-recording-v1.yaml',
    'manifests/appium3-compat-smoke-auth-03-run-v1.yaml',
    'manifests/compatibility-smoke-execution-auth-v1-prepared.yaml',
    'manifests/compatibility-smoke-execution-auth-v2-prepared.yaml',
    'manifests/compatibility-smoke-execution-auth-v3-prepared.yaml',
    'manifests/compatibility-smoke-implementation-lock-v4.yaml',
    'manifests/compatibility-smoke-status.yaml',
    'manifests/mobile-qualification-execution-auth-v1.yaml',
    'manifests/mobile-qualification-execution-auth-v2-prepared.yaml',
    'manifests/mobile-qualification-execution-auth-v3-prepared.yaml',
    'manifests/mobile-runner-remediation-v1.yaml',
    'manifests/toolchain-manifest.yaml',
    'protocol/mobile-runner-policy-v1.md',
    'protocol/mobile-runner-policy-v2.md',
    'protocol/mobile-runner-policy-v3.md',
    'qualification/compatibility-smoke/README.md',
    'qualification/compatibility-smoke/formal/APPIUM3-COMPAT-SMOKE-AUTH-02/ATTRIBUTION-SUT-02-ios.yaml',
    'qualification/compatibility-smoke/formal/APPIUM3-COMPAT-SMOKE-AUTH-02/IMPORT-RECORD.yaml',
    'qualification/compatibility-smoke/formal/APPIUM3-COMPAT-SMOKE-AUTH-03/IMPORT-RECORD.yaml',
    'qualification/compatibility-smoke-sut01/README.md',
]
SUT01_README = 'qualification/compatibility-smoke-sut01/README.md'
SUT02_README = 'qualification/compatibility-smoke/README.md'
MIRROR = 'manifests/compatibility-smoke-status.yaml'
LINEAGE = 'manifests/mobile-runner-remediation-v1.yaml'
TOOLCHAIN = 'manifests/toolchain-manifest.yaml'
START = 'manifests/e06-campaign-start-v1.yaml'
README = 'experiments/E06-cross-platform-parity/README.md'
MAPPING = 'experiments/scenario-mappings/CS-007.yaml'
GOVERNANCE = 'protocol/agent-governance-v6.md'
SCHEMA = 'schemas/run-manifest.schema.v2.json'
PROMPT = f'prompts/frozen/{PV}.md'


def extract_gate_script():
    with open(WORKFLOW, encoding='utf-8') as f:
        wf = yaml.safe_load(f)
    steps = wf['jobs']['gates']['steps']
    run = next(s['run'] for s in steps if s.get('id') == 'gates')
    lines = run.split('\n')
    start = lines.index("python3 - <<'PY'")
    end = lines.index('PY', start)
    return '\n'.join(lines[start + 1:end]) + '\n'


def read_bytes(rel):
    with open(os.path.join(REPO, rel), 'rb') as f:
        return f.read()


def auth_path(cond):
    return f"manifests/e06-dispatch-authorization-sut{'01' if 'SUT01' in cond else '02'}-v1.yaml"


def dispatch_record(cond, **over):
    d = {'authorization_id': AUTH_DISPATCH, 'status': 'ISSUED', 'record_validity': 'VALID', 'dispatch_eligibility': 'ELIGIBLE', 'revoked': False,
         'issued_by': 'human research lead', 'assigned_sut': 'SUT-01' if 'SUT01' in cond else 'SUT-02', 'conditions': [cond], 'n_executions': 50,
         'attempt': 1, 'authorization_date': '2026-11-22', 'campaign_start_authorization_id': AUTH_START,
         'frozen_inputs': {'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': PROMPT_SHA}}
    d.update(over)
    return yaml.safe_dump(d)


def configuration(cond, **drop):
    """A README with the locked "Campaign configuration" section naming everything the gate looks for; a keyword names one item to leave out."""
    conditions = {c['condition_id']: c for c in json.loads(read_bytes(CONDITIONS_REL))['conditions']}
    c = conditions[cond]
    pin = yaml.safe_load(read_bytes('manifests/sut-manifest.yaml'))['suts'][c['sut_id']]['components'][c['platform']]
    items = {
        'condition': f'- Condition: {cond}',
        'schema': '- Schema: schemas/run-manifest.schema.v2.json',
        'prompt': f'- Prompt version: {PV}',
        'implementation': f'- Implementation SHA-256: {IMPL_SHA}',
        'n': '- Executions: N = 50, attempt 1',
        'scenario': '- Scenario: CS-007',
        'conditions_sha': f"- Conditions file SHA-256: {hashlib.sha256(read_bytes(CONDITIONS_REL)).hexdigest()}",
        'pin': f"- Pinned commit: {pin['commit_sha']}",
        'release': f"- Pinned release: {pin.get('release') or '(none)'}",
        'workflow_sha': f"- Measured workflow SHA-256: {hashlib.sha256(read_bytes(WORKFLOW_REL)).hexdigest()}",
    }
    for k in drop:
        items.pop(k)
    return '# fixture README\n\n## Campaign configuration\n\n' + '\n'.join(items.values()) + '\n'


def fixture(cond):
    android = cond.endswith('ANDROID')
    files = {
        'manifests/study-manifest.yaml': yaml.safe_dump({'campaigns': [{'id': 'E06-cross-platform-parity', 'status': 'IN_PROGRESS'}]}),
        'protocol/CHANGELOG.md': f'| FIXTURE | experiments/E06-cross-platform-parity/README.md | campaign NOT_STARTED -> IN_PROGRESS | {AUTH_START} |\n',
        START: yaml.safe_dump({'record_class': 'CAMPAIGN_START', 'campaign_id': 'E06-cross-platform-parity', 'authorization_id': AUTH_START}),
        README: configuration(cond),
        CONDITIONS_REL: read_bytes(CONDITIONS_REL),
        'manifests/sut-manifest.yaml': read_bytes('manifests/sut-manifest.yaml'),
        WORKFLOW_REL: read_bytes(WORKFLOW_REL),
        MAPPING: yaml.safe_dump({'canonical_scenario_id': 'CS-007', 'mapping_status': 'FROZEN',
                                 'mappings': [{'sut_id': 'SUT-01', 'comparability': 'COMPARABLE'}, {'sut_id': 'SUT-02', 'comparability': 'COMPARABLE'}]}),
        'manifests/cs-007-freeze-v1.yaml': 'fixture freeze record\n',
        SCHEMA: json.dumps({'$id': 'urn:eus-2026-001:run-manifest:v2', 'properties': {'campaign_id': {}}}),
        GOVERNANCE: '| Document | protocol/agent-governance-v6.md |\n| Protocol state | FROZEN-PRE-DATA |\n\n### 3.7 Dispatch authorization (fixture)\n',
        PROMPT: PROMPT_TEXT,
        'experiments/E06-cross-platform-parity/executor/run-condition.sh': IMPL_TEXT,
        auth_path(cond): dispatch_record(cond),
    }
    if android:
        for rel in REAL_MOBILE_FILES:
            files[rel] = read_bytes(rel)
    return files


def write_tree(root, files):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(content if isinstance(content, bytes) else content.encode('utf-8'))


def edit(files, rel, fn):
    # change one record with a text function; the change is asserted to alter the record
    before = files[rel].decode('utf-8') if isinstance(files[rel], bytes) else files[rel]
    after = fn(before)
    assert after != before, f'the mutation of {rel} changed nothing'
    files[rel] = after.encode('utf-8')


def gate_env(cond, out, **overrides):
    env = {'PATH': os.environ.get('PATH', ''), 'GATE_CONDITION_ID': cond, 'GATE_CONFIRM': 'EXECUTE-' + cond,
           'GATE_DISPATCH_AUTHORIZATION_ID': AUTH_DISPATCH, 'GATE_CAMPAIGN_START_AUTHORIZATION_ID': AUTH_START,
           'GATE_EXECUTOR_PROMPT_VERSION': PV, 'GATE_EXECUTOR_IMPLEMENTATION_SHA256': IMPL_SHA, 'GATE_RUN_ATTEMPT': '1',
           'GATE_REF': 'refs/heads/main', 'GATE_SHA': 'a' * 40, 'GITHUB_OUTPUT': out}
    env.update(overrides)
    return env


@unittest.skipIf(yaml is None, 'PyYAML is not importable')
class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='e06-gate-')
        self.script = os.path.join(self.tmp, 'gate.py')
        with open(self.script, 'w', encoding='utf-8') as f:
            f.write(extract_gate_script())
        self.out = os.path.join(self.tmp, 'github-output.txt')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_gate(self, root, cond, **overrides):
        open(self.out, 'w').close()
        proc = subprocess.run([sys.executable, '-I', self.script], cwd=root, env=gate_env(cond, self.out, **overrides),
                              capture_output=True, text=True, timeout=120)
        with open(self.out, encoding='utf-8') as f:
            outputs = dict(l.split('=', 1) for l in f.read().splitlines() if '=' in l)
        return proc.returncode, proc.stdout + proc.stderr, outputs

    def tree(self, cond, mutate=None):
        root = tempfile.mkdtemp(prefix='e06-tree-', dir=self.tmp)
        files = fixture(cond)
        if mutate:
            mutate(files)
        write_tree(root, files)
        return root

    def assert_passes(self, cond):
        root = self.tree(cond)
        status, log, outputs = self.run_gate(root, cond)
        self.assertEqual(status, 0, log)
        self.assertEqual(outputs.get('ready'), 'true')
        return outputs

    def assert_fails_on(self, cond, marker, mutate=None, **overrides):
        root = self.tree(cond, mutate)
        status, log, outputs = self.run_gate(root, cond, **overrides)
        self.assertNotEqual(status, 0, log)
        self.assertEqual(outputs.get('ready'), 'false')
        failed = [l for l in log.splitlines() if l.startswith('FAIL ')]
        self.assertTrue(any(marker in l for l in failed), 'no FAIL line names ' + marker + '; failed: ' + '; '.join(l[:90] for l in failed))

    # ---- complete trees
    def test_the_complete_trees_pass_for_every_condition(self):
        # web: the fictitious common records; android: the same plus the real mobile records (the retained SUT-02 x ios FAIL_RUNNER is exempt
        # through its verified lineage)
        for cond in ('E06-CS007-SUT01-WEB', 'E06-CS007-SUT02-WEB', 'E06-CS007-SUT01-ANDROID', 'E06-CS007-SUT02-ANDROID'):
            with self.subTest(condition=cond):
                self.assert_passes(cond)

    def test_the_outputs_carry_the_hashes_that_the_provenance_records(self):
        outputs = self.assert_passes('E06-CS007-SUT01-WEB')
        self.assertEqual(outputs['workflow_sha256'], hashlib.sha256(read_bytes(WORKFLOW_REL)).hexdigest())
        self.assertEqual(outputs['conditions_sha256'], hashlib.sha256(read_bytes(CONDITIONS_REL)).hexdigest())
        self.assertEqual(outputs['executor_prompt_sha256'], PROMPT_SHA)
        self.assertEqual(outputs['environment_type'], 'PUBLIC_HOSTED')
        for key in ('configuration_sha256', 'schema_v2_sha256', 'governance_sha256', 'dispatch_authorization_sha256'):
            self.assertRegex(outputs[key], r'^[0-9a-f]{64}$', key)

    # ---- inputs
    def test_an_unknown_condition_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'the condition is one of the four measured conditions', GATE_CONDITION_ID='E06-CS007-SUT09-WEB', GATE_CONFIRM='EXECUTE-E06-CS007-SUT09-WEB')

    def test_a_wrong_confirmation_token_fails_on_the_confirmation_gate(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'explicit confirmation token', GATE_CONFIRM='EXECUTE-E06-CS007-SUT01-ANDROID')

    def test_a_re_run_fails_on_the_attempt_gate(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'first attempt only', GATE_RUN_ATTEMPT='2')

    def test_a_non_default_branch_fails_on_the_branch_gate(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'default branch only', GATE_REF='refs/heads/feature')

    def test_a_malformed_commit_fails_on_the_revision_gate(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'the repository commit and the workflow revision are recorded', GATE_SHA='not-a-commit')

    def test_a_prompt_version_of_another_campaign_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'executor prompt version is', GATE_EXECUTOR_PROMPT_VERSION='ORCHESTRATOR-E07-cross-layer-continuity-v1')

    # ---- START and configuration
    def test_a_campaign_that_is_not_in_progress_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'E06 campaign status IN_PROGRESS', lambda f: f.__setitem__('manifests/study-manifest.yaml', yaml.safe_dump({'campaigns': [{'id': 'E06-cross-platform-parity', 'status': 'NOT_STARTED'}]})))

    def test_a_start_row_with_another_id_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'the START row carries the campaign START authorization id', lambda f: f.__setitem__('protocol/CHANGELOG.md', '| FIXTURE | experiments/E06-cross-platform-parity/README.md | campaign NOT_STARTED -> IN_PROGRESS | OTHER |\n'))

    def test_a_missing_start_record_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'START record exists', lambda f: f.pop(START))

    def test_a_configuration_without_the_locked_section_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'locked "Campaign configuration" record exists', lambda f: f.__setitem__(README, '# no section\n'))

    def test_a_configuration_that_omits_one_locked_item_fails_on_the_gate_that_names_it(self):
        cond = 'E06-CS007-SUT01-WEB'
        cases = {'condition': 'configuration names the condition', 'schema': 'configuration names run-manifest schema v2',
                 'prompt': 'configuration names the executor prompt version', 'implementation': 'configuration names the executor implementation hash',
                 'n': 'configuration names N = 50', 'scenario': 'configuration names the canonical scenario CS-007',
                 'conditions_sha': 'configuration names the sha256 of the conditions file', 'pin': 'configuration names the pinned commit',
                 'workflow_sha': 'configuration names the sha256 of the measured workflow file'}
        for key, marker in cases.items():
            with self.subTest(omitted=key):
                self.assert_fails_on(cond, marker, lambda f, k=key: f.__setitem__(README, configuration(cond, **{k: None})))

    def test_the_release_of_a_pinned_android_component_must_be_named_in_the_configuration(self):
        cond = 'E06-CS007-SUT01-ANDROID'
        self.assert_fails_on(cond, 'configuration names the pinned release', lambda f: f.__setitem__(README, configuration(cond, release=None)))

    def test_a_changed_conditions_file_fails_on_its_locked_hash(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'configuration names the sha256 of the conditions file', lambda f: edit(f, CONDITIONS_REL, lambda s: s + '\n'))

    def test_a_changed_workflow_fails_on_its_locked_revision(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'configuration names the sha256 of the measured workflow file', lambda f: edit(f, WORKFLOW_REL, lambda s: s + '\n# changed\n'))

    # ---- frozen inputs
    def test_a_draft_scenario_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'the canonical scenario CS-007 is FROZEN', lambda f: edit(f, MAPPING, lambda s: s.replace('FROZEN', 'DRAFT')))

    def test_a_scenario_entry_that_is_not_comparable_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'the mapping entry of the SUT in CS-007 is COMPARABLE', lambda f: edit(f, MAPPING, lambda s: s.replace('COMPARABLE', 'NOT_COMPARABLE', 1)))

    def test_a_missing_freeze_record_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'the freeze record of CS-007 exists', lambda f: f.pop('manifests/cs-007-freeze-v1.yaml'))

    def test_a_draft_governance_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', lambda f: f.__setitem__(GOVERNANCE, '| Protocol state | DRAFT |\n'))

    def test_a_governance_without_section_3_7_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'names the per-SUT dispatch authorization of Section 3.7', lambda f: f.__setitem__(GOVERNANCE, '| Protocol state | FROZEN-PRE-DATA |\n'))

    def test_a_schema_without_the_v2_id_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'run-manifest schema v2 present', lambda f: f.__setitem__(SCHEMA, json.dumps({'properties': {}})))

    def test_a_missing_frozen_prompt_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'executor prompt frozen file exists', lambda f: f.pop(PROMPT))

    def test_a_changed_implementation_fails_on_the_locked_hash(self):
        self.assert_fails_on('E06-CS007-SUT01-WEB', 'executor implementation exists and equals the locked hash', lambda f: f.__setitem__('experiments/E06-cross-platform-parity/executor/run-condition.sh', 'changed\n'))

    # ---- dispatch authorization
    def test_a_dispatch_authorization_that_is_not_issued_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization is ISSUED', lambda f: f.__setitem__(auth_path(cond), dispatch_record(cond, status='DRAFT')))

    def test_a_revoked_dispatch_authorization_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization is ISSUED', lambda f: f.__setitem__(auth_path(cond), dispatch_record(cond, revoked=True)))

    def test_a_dispatch_authorization_issued_by_an_agent_role_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization is ISSUED', lambda f: f.__setitem__(auth_path(cond), dispatch_record(cond, issued_by='ORCHESTRATOR')))

    def test_a_dispatch_authorization_of_another_condition_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization names this condition', lambda f: f.__setitem__(auth_path(cond), dispatch_record(cond, conditions=['E06-CS007-SUT01-ANDROID'])))

    def test_a_dispatch_authorization_of_another_sut_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization names the assigned SUT', lambda f: f.__setitem__(auth_path(cond), dispatch_record(cond, assigned_sut='SUT-02')))

    def test_a_dispatch_authorization_with_another_start_id_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization names the campaign START authorization id', lambda f: f.__setitem__(auth_path(cond), dispatch_record(cond, campaign_start_authorization_id='OTHER')))

    def test_a_dispatch_authorization_with_another_prompt_hash_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization records the executor prompt SHA-256', lambda f: f.__setitem__(auth_path(cond), dispatch_record(
            cond, frozen_inputs={'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': '0' * 64})))

    def test_a_dispatch_authorization_with_another_implementation_hash_fails(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'dispatch authorization records the executor implementation SHA-256', lambda f: f.__setitem__(auth_path(cond), dispatch_record(
            cond, frozen_inputs={'executor_implementation_sha256': '0' * 64, 'executor_prompt_sha256': PROMPT_SHA})))

    def test_two_records_naming_the_same_authorization_id_fail(self):
        cond = 'E06-CS007-SUT01-WEB'
        self.assert_fails_on(cond, 'exactly one dispatch authorization record', lambda f: f.__setitem__('manifests/e06-dispatch-authorization-sut01-v2.yaml', dispatch_record(cond)))

    # ---- Android admissibility: one change in the real records, each must fail on the gate it names (the block is the lift of the G-7 block of E03)
    def test_a_study_status_that_is_not_selected_fails_for_android(self):
        self.assert_fails_on('E06-CS007-SUT01-ANDROID', 'study-level mobile-runner status is SELECTED', lambda f: edit(
            f, TOOLCHAIN, lambda s: s.replace('mobile_runner_status: SELECTED', 'mobile_runner_status: UNRESOLVED_AFTER_FALLBACK_FAILURE')))

    def test_a_smoke_entry_that_points_to_another_sut_record_fails(self):
        def point_elsewhere(files):
            def change(text):
                doc = yaml.safe_load(text)
                for e in doc['entries']:
                    if e.get('sut_id') == 'SUT-01' and e.get('platform') == 'android':
                        e['qualifier_record'] = SUT02_README
                return yaml.safe_dump(doc)
            edit(files, MIRROR, change)
        self.assert_fails_on('E06-CS007-SUT01-ANDROID', 'points to the QUALIFIER record of its own SUT', point_elsewhere)

    def test_a_pass_row_absent_from_the_sut01_qualifier_record_fails(self):
        self.assert_fails_on('E06-CS007-SUT01-ANDROID', 'has a PASS row for SUT-01 x android', lambda f: edit(
            f, SUT01_README, lambda s: '\n'.join(l for l in s.split('\n') if not l.startswith('| SUT-01 | android'))))

    def test_a_pass_row_absent_from_the_sut02_qualifier_record_fails(self):
        self.assert_fails_on('E06-CS007-SUT02-ANDROID', 'has a PASS row for SUT-02 x android', lambda f: edit(
            f, SUT02_README, lambda s: '\n'.join(l for l in s.split('\n') if not l.startswith('| SUT-02 | android'))))

    def test_a_fail_runner_row_in_the_sut01_record_fails(self):
        def add_fail_row(files):
            def change(text):
                lines = text.split('\n')
                k = next(i for i, l in enumerate(lines) if l.startswith('| SUT-01 | android'))
                bad = lines[k].replace('| PASS |', '| FAIL_RUNNER |', 1).replace('AUTH-04', 'AUTH-05')
                return '\n'.join(lines[:k + 1] + [bad] + lines[k + 1:])
            edit(files, SUT01_README, change)
        self.assert_fails_on('E06-CS007-SUT01-ANDROID', 'no FAIL_RUNNER of the selected runner in the SUT-01 QUALIFIER record', add_fail_row)

    def test_a_fail_runner_entry_in_the_mirror_fails(self):
        def add_entry(files):
            def change(text):
                doc = yaml.safe_load(text)
                doc['entries'].append({'sut_id': 'SUT-01', 'platform': 'ios', 'runner': 'Appium 3', 'runner_version': '3.7.0 appium-uiautomator2-driver 8.7.0',
                                       'result': 'FAIL_RUNNER', 'qualifier_record': SUT01_README, 'authorization_id': 'APPIUM3-COMPAT-SMOKE-AUTH-05',
                                       'executed_at': '2026-11-22T00:00:00Z'})
                return yaml.safe_dump(doc)
            edit(files, MIRROR, change)
        self.assert_fails_on('E06-CS007-SUT02-ANDROID', 'no unresolved FAIL_RUNNER of the selected runner', add_entry)

    def test_without_the_lineage_record_the_historical_fail_runner_closes_the_android_gate(self):
        self.assert_fails_on('E06-CS007-SUT02-ANDROID', 'exactly one remediation lineage record exists', lambda f: f.pop(LINEAGE))

    def test_a_lineage_whose_row_hash_differs_closes_the_android_gate(self):
        self.assert_fails_on('E06-CS007-SUT02-ANDROID', 'the named historical row still exists unchanged', lambda f: edit(
            f, LINEAGE, lambda s: re.sub(r'(row_sha256: )([0-9a-f])', lambda m: m.group(1) + ('0' if m.group(2) != '0' else '1'), s, count=1)))

    def test_a_second_remediation_authorization_closes_the_android_gate(self):
        self.assert_fails_on('E06-CS007-SUT01-ANDROID', 'exactly one remediation authorization exists', lambda f: f.__setitem__(
            'manifests/compatibility-smoke-execution-auth-v9-prepared.yaml',
            'authorization_id: APPIUM3-COMPAT-SMOKE-AUTH-09\nauthorization_type: COMPATIBILITY_SMOKE_REMEDIATION_EXECUTION\n'))

    def test_a_missing_toolchain_record_is_a_failed_gate_and_never_an_exception(self):
        self.assert_fails_on('E06-CS007-SUT01-ANDROID', 'completed without an exception', lambda f: f.pop(TOOLCHAIN))

    # ---- the repository as it is
    def test_the_repository_as_it_is_fails_closed(self):
        status, log, outputs = self.run_gate(REPO, 'E06-CS007-SUT01-ANDROID')
        self.assertNotEqual(status, 0, log)
        self.assertEqual(outputs.get('ready'), 'false')
        self.assertTrue(any(l.startswith('FAIL E06 campaign status IN_PROGRESS') for l in log.splitlines()), 'E06 has no START: that gate must be closed')


class LiftTests(unittest.TestCase):
    def test_the_android_block_is_the_lift_of_the_e03_g7_block(self):
        # the Android admissibility block is generated from the G-7 block of e03-measured-execution.yml (tests/lift_g7.py); a change of either
        # side that is not the other's changes the text and fails here instead of drifting silently
        import lift_g7
        with open(WORKFLOW, encoding='utf-8') as f:
            lines, span = lift_g7.current_region(f.read())
        self.assertIsNotNone(span, 'the E06 workflow has no BEGIN/END markers of the lifted block')
        self.assertEqual('\n'.join(lines[span[0]:span[1] + 1]) + '\n', lift_g7.build_block())


if __name__ == '__main__':
    unittest.main()
