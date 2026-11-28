"""The measured-execution gate of .github/workflows/e10-measured-execution.yml, executed on fake trees (operation OP-PREP-E10).

The gate script is extracted from the workflow file (step id "gates", the python heredoc), written to a temporary file, and run with the working
directory set to a fake tree and the GATE_* inputs set in its environment. The must-pass tree is complete and fictitious (fixture identifiers
only, not issued authorizations); every must-fail case changes exactly one thing and must fail on the gate it names. The "as-is" case runs
against the files of this repository as they are and must fail closed, because E10 has no START, no locked configuration, no dispatch
authorization, no frozen prompt, no verified controlled instance, no pinned visual instrument (`tools.visual` has no version) and no
calibration record.

The fixture tree states the instrument pins in the interface forms of the implementation: PIXELMATCH_VERSION, PIXELMATCH_TARBALL_SHA256 and
PIXELMATCH_INDEX_SHA256 in executor/compare.py, CAPTURE_VERSION in executor/capture.py, the Playwright pin in requirements.txt. The
calibration record has the shape `conditions.<condition id>: {T_R, T_e, dry_run_run_ids}`; the locked configuration states the thresholds
of a condition on one line that names the condition, as `T_R = <number>` and `T_e = <number>`; the conditions file states them per condition
(`conditions[].thresholds`, null until the calibration), and the three places must agree.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))

try:
    import yaml
except ImportError:  # the tests need PyYAML (a pure-Python copy is acceptable on PYTHONPATH)
    yaml = None

WORKFLOW = os.path.join(REPO, '.github', 'workflows', 'e10-measured-execution.yml')
CONDITIONS_FILE = os.path.join(REPO, 'experiments', 'E10-visual', 'conditions-draft.json')
CONDITIONS_REL = 'experiments/E10-visual/conditions-draft.json'
PV = 'TEST-FIXTURE-PROMPT-v1'
AUTH_START = 'TEST-FIXTURE-E10-START'
AUTH_DISPATCH = 'TEST-FIXTURE-DISPATCH-SUT03'
PROMPT_TEXT = b'DRAFT fixture prompt text for the gate tests only.\n'
IMPL_TEXT = b'DRAFT fixture implementation text for the gate tests only.\n'
PROMPT_SHA = hashlib.sha256(PROMPT_TEXT).hexdigest()
IMPL_SHA = hashlib.sha256(IMPL_TEXT).hexdigest()
COND = 'E10-SUT03-WEB-IMAGE'
COND2 = 'E10-SUT03-WEB-SHIFT'
SUT = 'SUT-03'
WEB_COMMIT = '7ab934d733f2f74d4b912e94e86f59ae0f6b7609'
PLAYWRIGHT = '1.63.0'
PIXELMATCH = '8.0.0'
TARBALL_SHA = 'ab59d4c4ec73fbf456c72cbd8200b1529a76142fd9291de72a62ba6e3a845e75'
INDEX_SHA = '5b8583627704b4e1fe4fea472c283c8ca03d10ae4c94e5e029ea3b271a998ee6'
CAPTURE = 'e10-capture-v1'
DISPATCH = 'manifests/e10-dispatch-authorization-sut03-v1.yaml'
FURTHER = 'manifests/e10-further-attempt-approval-sut03-v1.yaml'
CONTROLLED = 'experiments/E10-visual/controlled-instance-status.yaml'
README = 'experiments/E10-visual/README.md'
CAL = 'manifests/e10-calibration-v1.yaml'
COMPARE = 'experiments/E10-visual/executor/executor/compare.py'
CAPTURE_PY = 'experiments/E10-visual/executor/executor/capture.py'
TOOLCHAIN = 'manifests/toolchain-manifest.yaml'
THRESHOLDS = {COND: (0.0006, 0.012), COND2: (0.0007, 0.011)}


def sha_of(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def extract_gate_script():
    with open(WORKFLOW, encoding='utf-8') as f:
        wf = yaml.safe_load(f)
    steps = wf['jobs']['gate']['steps']
    run = next(s['run'] for s in steps if s.get('id') == 'gates')
    lines = run.split('\n')
    start = lines.index("python3 - <<'PY'")
    end = lines.index('PY', start)
    return '\n'.join(lines[start + 1:end]) + '\n'


def calibration_text(thresholds=None):
    th = thresholds or THRESHOLDS
    return yaml.safe_dump({'record_class': 'E10_CALIBRATION_RECORD', 'campaign_id': 'E10-visual', 'status': 'LOCKED',
                           'conditions': {c: {'T_R': a, 'T_e': b, 'dry_run_run_ids': [1001, 1002]} for c, (a, b) in th.items()}})


def base_state(attempt='1', first='1'):
    """The must-pass state: every gate satisfied by fictitious fixture content."""
    with open(WORKFLOW, encoding='utf-8') as f:
        workflow_text = f.read()
    with open(CONDITIONS_FILE, encoding='utf-8') as f:
        conditions_doc = json.load(f)
    for c in conditions_doc['conditions']:
        if c['condition_id'] in THRESHOLDS:
            c['thresholds'] = {'T_R': THRESHOLDS[c['condition_id']][0], 'T_e': THRESHOLDS[c['condition_id']][1]}
    conditions_text = json.dumps(conditions_doc, indent=2) + '\n'
    cal = calibration_text()
    cfg = (f'# E10 fixture README\n\n## Campaign configuration\n\n- Condition: {COND}\n- Schema: schemas/run-manifest.schema.v2.json\n'
           f'- Executor prompt: {PV}\n- Executor implementation SHA-256: {IMPL_SHA}\n- Sample size: N = 50 executions per condition\n'
           f'- Comparison: H5, CONFIRMATORY, count unit 1 (E10-D-2)\n- Conditions file sha256: {hashlib.sha256(conditions_text.encode()).hexdigest()}\n'
           f'- Web commit (SUT-03): {WEB_COMMIT}\n- Scenario mapping: no canonical scenario\n'
           f'- Measured workflow sha256: {hashlib.sha256(workflow_text.encode()).hexdigest()}\n'
           f'- Thresholds, {COND}: T_R = {THRESHOLDS[COND][0]}, T_e = {THRESHOLDS[COND][1]}\n'
           f'- Thresholds, {COND2}: T_R = {THRESHOLDS[COND2][0]}, T_e = {THRESHOLDS[COND2][1]}\n'
           f'- Calibration record sha256: {hashlib.sha256(cal.encode()).hexdigest()}\n\n## Next\n')
    files = {
        'manifests/study-manifest.yaml': yaml.safe_dump({'campaigns': [{'id': 'E10-visual', 'status': 'IN_PROGRESS'}]}),
        'protocol/CHANGELOG.md': f'| FIXTURE | {README} | campaign NOT_STARTED -> IN_PROGRESS | {AUTH_START} |\n',
        README: cfg,
        'experiments/E10-visual/conditions-draft.json': conditions_text,
        'manifests/e10-campaign-start-v1.yaml': yaml.safe_dump({'record_class': 'CAMPAIGN_START', 'campaign_id': 'E10-visual', 'authorization_id': AUTH_START}),
        'manifests/sut-manifest.yaml': yaml.safe_dump({'suts': {SUT: {'components': {'web': {'repository': 'FIXTURE', 'commit_sha': WEB_COMMIT, 'release': None}}}}}),
        'protocol/agent-governance-v6.md': '| Protocol state | FROZEN-PRE-DATA |\n\n### 3.7 Dispatch authorization\n',
        DISPATCH: yaml.safe_dump({
            'record_class': 'E10_DISPATCH_AUTHORIZATION', 'campaign_id': 'E10-visual',
            'authorization_id': AUTH_DISPATCH, 'status': 'ISSUED', 'record_validity': 'VALID', 'dispatch_eligibility': 'ELIGIBLE', 'revoked': False,
            'issued_by': 'human research lead', 'authorization_date': 'FIXTURE-DATE', 'assigned_sut': SUT, 'conditions': [COND, COND2],
            'n_executions': 50, 'attempt': 1, 'campaign_start_authorization_id': AUTH_START,
            'frozen_inputs': {'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': PROMPT_SHA}}),
        CONTROLLED: yaml.safe_dump({'conditions': {COND: {'status': 'CONTROLLED', 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'},
                                                          'reverification_required': False}}}),
        TOOLCHAIN: yaml.safe_dump({'tools': {
            'web_runner': {'version': PLAYWRIGHT},
            'visual': {'candidate': 'Playwright viewport screenshots compared with Pixelmatch', 'version': PIXELMATCH, 'playwright_version': PLAYWRIGHT,
                       'tarball_sha256': TARBALL_SHA, 'index_sha256': INDEX_SHA, 'capture_version': CAPTURE}}}),
        'schemas/run-manifest.schema.v2.json': json.dumps({'$id': 'urn:eus-2026-001:schemas:run-manifest:v2'}),
        f'prompts/frozen/{PV}.md': PROMPT_TEXT.decode('utf-8'),
        'experiments/E10-visual/executor/run-condition.sh': IMPL_TEXT.decode('utf-8'),
        'experiments/E10-visual/executor/requirements.txt': f'playwright=={PLAYWRIGHT} \\\n    --hash=sha256:00\n',
        COMPARE: f"PIXELMATCH_VERSION = '{PIXELMATCH}'\nPIXELMATCH_TARBALL_SHA256 = '{TARBALL_SHA}'\nPIXELMATCH_INDEX_SHA256 = '{INDEX_SHA}'\n",
        CAPTURE_PY: f"CAPTURE_VERSION = '{CAPTURE}'\n",
        CAL: cal,
        '.github/workflows/e10-measured-execution.yml': workflow_text,
    }
    inputs = {'GATE_CONDITION_ID': COND, 'GATE_ASSIGNED_SUT': SUT, 'GATE_ATTEMPT': attempt, 'GATE_FIRST_EXECUTION': first,
              'GATE_CAMPAIGN_START_AUTHORIZATION_ID': AUTH_START, 'GATE_DISPATCH_AUTHORIZATION_ID': AUTH_DISPATCH,
              'GATE_EXECUTOR_PROMPT_VERSION': PV, 'GATE_EXECUTOR_IMPLEMENTATION_SHA256': IMPL_SHA}
    return {'files': files, 'inputs': inputs}


def run_gate(state, script_text, tree_root):
    """Materialize the state in a fake tree, run the gate there, and return (exit status, output text)."""
    if os.path.isdir(tree_root):
        shutil.rmtree(tree_root)
    for rel, content in state['files'].items():
        path = os.path.join(tree_root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    script = os.path.join(tree_root, '..', os.path.basename(tree_root) + '-gate.py')
    with open(script, 'w', encoding='utf-8') as f:
        f.write(script_text)
    out_file = os.path.join(tree_root, '..', os.path.basename(tree_root) + '-github-output.txt')
    env = {k: v for k, v in os.environ.items() if not k.startswith('GATE_')}
    env.update(state['inputs'])
    env['GITHUB_OUTPUT'] = out_file
    proc = subprocess.run([sys.executable, script], cwd=tree_root, env=env, capture_output=True, text=True, timeout=120)
    return proc.returncode, proc.stdout + proc.stderr


@unittest.skipIf(yaml is None, 'PyYAML is not importable (set PYTHONPATH to a PyYAML copy)')
class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = extract_gate_script()
        cls.work = tempfile.mkdtemp(prefix='e10-gate-')

    def tree(self, name):
        return os.path.join(self.work, name)

    def assertPasses(self, state, label):
        code, out = run_gate(state, self.script, self.tree(label))
        self.assertEqual(code, 0, out)
        self.assertIn('ALL GATES PASSED', out)

    def assertFailsOn(self, state, label, fragment):
        code, out = run_gate(state, self.script, self.tree(label))
        self.assertNotEqual(code, 0, f'{label} unexpectedly passed:\n{out}')
        fails = [l for l in out.splitlines() if l.startswith('FAIL ')]
        self.assertTrue(any(fragment in l for l in fails), f'{label}: no FAIL line names {fragment!r}\n{out}')

    def test_must_pass(self):
        self.assertPasses(base_state(), 'pass')

    def test_a_sentence_ending_period_after_a_threshold_is_not_part_of_the_number(self):
        state = base_state()
        state['files'][README] = state['files'][README].replace(f'T_e = {THRESHOLDS[COND][1]}\n', f'T_e = {THRESHOLDS[COND][1]}.\n', 1)
        self.assertPasses(state, 'threshold-then-period')

    def test_the_calibration_record_hash_travels_to_the_outputs(self):
        state = base_state()
        code, out = run_gate(state, self.script, self.tree('outputs'))
        self.assertEqual(code, 0, out)
        with open(os.path.join(self.work, 'outputs-github-output.txt'), encoding='utf-8') as f:
            written = f.read()
        self.assertIn('calibration_record_sha256=' + hashlib.sha256(state['files'][CAL].encode()).hexdigest(), written)

    def test_a_further_attempt_passes_only_with_its_own_approval(self):
        state = base_state(attempt='2', first='7')
        self.assertFailsOn(state, 'further-without-approval', 'exactly one further-attempt approval entry')
        state['files'][FURTHER] = yaml.safe_dump({
            'record_class': 'E10_FURTHER_ATTEMPT_APPROVAL', 'status': 'ISSUED', 'revoked': False, 'assigned_sut': SUT, 'issued_by': 'human research lead',
            'dispatch_authorization_id': AUTH_DISPATCH, 'campaign_start_authorization_id': AUTH_START, 'executor_implementation_sha256': IMPL_SHA,
            'executor_prompt_version': PV, 'executor_prompt_sha256': PROMPT_SHA, 'governing_protocol': 'protocol/agent-governance-v6.md, Section 3.7',
            'attempts': [{'condition_id': COND, 'first_execution': 7, 'attempt': 2, 'previous_attempt': 1}]})
        self.assertPasses(state, 'further-with-approval')
        wrong = base_state(attempt='2', first='7')
        wrong['files'][FURTHER] = state['files'][FURTHER].replace('E10_FURTHER_ATTEMPT_APPROVAL', 'E08_FURTHER_ATTEMPT_APPROVAL')
        self.assertFailsOn(wrong, 'further-other-class', 'ISSUED, unrevoked E10 further-attempt approval')

    def test_must_fail_matrix(self):
        def put(path, text):
            return lambda s: s['files'].__setitem__(path, text)

        def rm(path):
            return lambda s: s['files'].pop(path)

        def edit(path, old, new):
            def f(s):
                assert old in s['files'][path], (path, old)
                s['files'][path] = s['files'][path].replace(old, new)
            return f

        def inp(key, value):
            return lambda s: s['inputs'].__setitem__(key, value)

        def ydict(path, fn):
            def f(s):
                d = yaml.safe_load(s['files'][path])
                fn(d)
                s['files'][path] = yaml.safe_dump(d)
            return f

        def cal_edit(fn):
            return ydict(CAL, fn)

        def cond_json(fn):
            """Edit the conditions file and keep the sha256 that the configuration names equal to it, so that exactly one thing changes."""
            def f(s):
                old = s['files'][CONDITIONS_REL]
                d = json.loads(old)
                fn(d['conditions'][[c['condition_id'] for c in d['conditions']].index(COND)])
                new = json.dumps(d, indent=2) + '\n'
                s['files'][CONDITIONS_REL] = new
                s['files'][README] = s['files'][README].replace(hashlib.sha256(old.encode()).hexdigest(), hashlib.sha256(new.encode()).hexdigest())
            return f

        t_r, t_e = THRESHOLDS[COND]
        cases = [
            # the campaign and its configuration
            ('campaign-not-started', 'E10 campaign status IN_PROGRESS', put('manifests/study-manifest.yaml', yaml.safe_dump({'campaigns': [{'id': 'E10-visual', 'status': 'NOT_STARTED'}]}))),
            ('no-start-row', 'exactly one E10 campaign START', rm('protocol/CHANGELOG.md')),
            ('two-start-rows', 'exactly one E10 campaign START', lambda s: s['files'].__setitem__('protocol/CHANGELOG.md', s['files']['protocol/CHANGELOG.md'] * 2)),
            ('start-row-without-id', 'START row carries the campaign START authorization id', put('protocol/CHANGELOG.md', f'| X | {README} | campaign NOT_STARTED -> IN_PROGRESS |\n')),
            ('no-start-record', 'START record exists', rm('manifests/e10-campaign-start-v1.yaml')),
            ('no-configuration', 'locked "Campaign configuration" record exists', put(README, '# nothing\n')),
            ('configuration-without-n50', 'configuration names N = 50', edit(README, 'N = 50', 'N = 30')),
            ('configuration-without-h5', 'configuration names the H5 hypothesis label', edit(README, 'H5', 'H3')),
            ('configuration-without-scenario-statement', 'no canonical scenario', edit(README, 'no canonical scenario', 'a scenario')),
            ('configuration-without-commit', 'pinned commit of every E10 surface component', edit(README, WEB_COMMIT, 'x')),
            ('conditions-file-changed', 'sha256 of the conditions file', lambda s: s['files'].__setitem__('experiments/E10-visual/conditions-draft.json', s['files']['experiments/E10-visual/conditions-draft.json'] + ' ')),
            ('workflow-changed', 'sha256 of the measured workflow file', lambda s: s['files'].__setitem__('.github/workflows/e10-measured-execution.yml', s['files']['.github/workflows/e10-measured-execution.yml'] + '# x\n')),
            # the dispatch authorization
            ('no-dispatch-authorization', 'exactly one dispatch authorization record', rm(DISPATCH)),
            ('dispatch-not-issued', 'dispatch authorization is ISSUED', ydict(DISPATCH, lambda d: d.update(status='PREPARED'))),
            ('dispatch-revoked', 'dispatch authorization is ISSUED', ydict(DISPATCH, lambda d: d.update(revoked=True))),
            ('dispatch-other-class', 'E10_DISPATCH_AUTHORIZATION record of E10-visual', ydict(DISPATCH, lambda d: d.update(record_class='E08_DISPATCH_AUTHORIZATION'))),
            ('dispatch-other-campaign', 'E10_DISPATCH_AUTHORIZATION record of E10-visual', ydict(DISPATCH, lambda d: d.update(campaign_id='E08-performance'))),
            ('dispatch-other-sut', 'dispatch authorization names the assigned SUT', ydict(DISPATCH, lambda d: d.update(assigned_sut='SUT-02'))),
            ('dispatch-without-condition', 'dispatch authorization names this condition', ydict(DISPATCH, lambda d: d.update(conditions=[COND2]))),
            ('dispatch-n30', 'dispatch authorization names N = 50', ydict(DISPATCH, lambda d: d.update(n_executions=30))),
            ('dispatch-other-implementation', 'executor implementation SHA-256 equal to the input', ydict(DISPATCH, lambda d: d['frozen_inputs'].update(executor_implementation_sha256='0' * 64))),
            ('dispatch-other-prompt', 'executor prompt SHA-256 equal to the frozen prompt file', ydict(DISPATCH, lambda d: d['frozen_inputs'].update(executor_prompt_sha256='0' * 64))),
            ('prompt-not-frozen', 'executor prompt frozen file exists', rm(f'prompts/frozen/{PV}.md')),
            # governance, schema, controlled instance, implementation
            ('governance-draft', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', put('protocol/agent-governance-v6.md', '| Protocol state | DRAFT |\n\n### 3.7 Dispatch authorization\n')),
            ('governance-without-3-7', 'names the per-SUT dispatch authorization of Section 3.7', put('protocol/agent-governance-v6.md', '| Protocol state | FROZEN-PRE-DATA |\n')),
            ('no-schema-v2', 'run-manifest schema v2 present', put('schemas/run-manifest.schema.v2.json', '{}')),
            ('instance-not-controlled', 'controlled instance status CONTROLLED', ydict(CONTROLLED, lambda d: d['conditions'][COND].update(status='NOT_CONTROLLED'))),
            ('instance-not-verified', 'GitHub Actions environment verification VERIFIED', ydict(CONTROLLED, lambda d: d['conditions'][COND]['github_actions_verification'].update(status='NOT_VERIFIED'))),
            ('reverification-required', 'no provisioning change awaiting re-verification', ydict(CONTROLLED, lambda d: d['conditions'][COND].update(reverification_required=True))),
            ('public-hosted', 'environment_type SELF_HOSTED', ydict(CONTROLLED, lambda d: d['conditions'][COND]['github_actions_verification'].update(environment_type='PUBLIC_HOSTED'))),
            ('implementation-changed', 'executor implementation exists and equals the locked hash', put('experiments/E10-visual/executor/run-condition.sh', 'other\n')),
            # G-10, the instrument pin
            ('instrument-tbd', 'tools.visual names the instrument and a version', ydict(TOOLCHAIN, lambda d: d['tools']['visual'].update(candidate='TBD between appropriate open-source tools', version=None))),
            ('instrument-no-version', 'tools.visual names the instrument and a version', ydict(TOOLCHAIN, lambda d: d['tools']['visual'].update(version=None))),
            ('instrument-no-entry', 'tools.visual names the instrument and a version', ydict(TOOLCHAIN, lambda d: d['tools'].pop('visual'))),
            ('instrument-other-pixelmatch-version', 'tools.visual version equals PIXELMATCH_VERSION', ydict(TOOLCHAIN, lambda d: d['tools']['visual'].update(version='7.1.0'))),
            ('implementation-other-pixelmatch-version', 'tools.visual version equals PIXELMATCH_VERSION', edit(COMPARE, "PIXELMATCH_VERSION = '8.0.0'", "PIXELMATCH_VERSION = '8.0.1'")),
            ('instrument-other-tarball', 'tools.visual tarball_sha256 equals PIXELMATCH_TARBALL_SHA256', ydict(TOOLCHAIN, lambda d: d['tools']['visual'].update(tarball_sha256='0' * 64))),
            ('implementation-other-tarball', 'tools.visual tarball_sha256 equals PIXELMATCH_TARBALL_SHA256', edit(COMPARE, TARBALL_SHA, '1' * 64)),
            ('instrument-other-module', 'tools.visual index_sha256 equals PIXELMATCH_INDEX_SHA256', ydict(TOOLCHAIN, lambda d: d['tools']['visual'].update(index_sha256='0' * 64))),
            ('implementation-other-module', 'tools.visual index_sha256 equals PIXELMATCH_INDEX_SHA256', edit(COMPARE, INDEX_SHA, '1' * 64)),
            ('no-compare-module', 'tools.visual version equals PIXELMATCH_VERSION', rm(COMPARE)),
            ('instrument-other-playwright', 'tools.visual playwright_version equals the Playwright pin', ydict(TOOLCHAIN, lambda d: d['tools']['visual'].update(playwright_version='1.60.0'))),
            ('requirements-other-playwright', 'tools.visual playwright_version equals the Playwright pin', put('experiments/E10-visual/executor/requirements.txt', 'playwright==1.60.0 \\\n    --hash=sha256:00\n')),
            ('instrument-other-web-runner', 'tools.visual playwright_version equals the Playwright pin', ydict(TOOLCHAIN, lambda d: d['tools']['web_runner'].update(version='1.60.0'))),
            ('instrument-other-capture-version', 'tools.visual capture_version equals CAPTURE_VERSION', ydict(TOOLCHAIN, lambda d: d['tools']['visual'].update(capture_version='e10-capture-v0'))),
            ('implementation-other-capture-version', 'tools.visual capture_version equals CAPTURE_VERSION', edit(CAPTURE_PY, CAPTURE, 'e10-capture-v2')),
            ('no-capture-module', 'tools.visual capture_version equals CAPTURE_VERSION', rm(CAPTURE_PY)),
            # G-11, the calibration record
            ('no-calibration-record', 'calibration record exists, is an E10_CALIBRATION_RECORD of E10-visual and is LOCKED', rm(CAL)),
            ('calibration-not-locked', 'is an E10_CALIBRATION_RECORD of E10-visual and is LOCKED', cal_edit(lambda d: d.update(status='DRAFT'))),
            ('calibration-other-class', 'is an E10_CALIBRATION_RECORD of E10-visual and is LOCKED', cal_edit(lambda d: d.update(record_class='E08_CALIBRATION_RECORD'))),
            ('calibration-other-campaign', 'is an E10_CALIBRATION_RECORD of E10-visual and is LOCKED', cal_edit(lambda d: d.update(campaign_id='E08-performance'))),
            ('calibration-misses-a-condition-of-the-sut', 'calibration record covers every condition of the assigned SUT', cal_edit(lambda d: d['conditions'].pop(COND2))),
            ('calibration-t-r-below-floor', 'at or above the floors of the conditions file', cal_edit(lambda d: d['conditions'][COND].update(T_R=0.0001))),
            ('calibration-t-e-below-floor', 'at or above the floors of the conditions file', cal_edit(lambda d: d['conditions'][COND].update(T_e=0.001))),
            ('calibration-t-r-null', 'at or above the floors of the conditions file', cal_edit(lambda d: d['conditions'][COND].update(T_R=None))),
            ('calibration-t-e-boolean', 'at or above the floors of the conditions file', cal_edit(lambda d: d['conditions'][COND].update(T_e=True))),
            ('calibration-t-r-zero', 'at or above the floors of the conditions file', cal_edit(lambda d: d['conditions'][COND].update(T_R=0))),
            ('calibration-t-r-text', 'at or above the floors of the conditions file', cal_edit(lambda d: d['conditions'][COND].update(T_R='0.0006'))),
            ('calibration-without-dry-run-ids', 'names the DRY_RUN runs of the condition', cal_edit(lambda d: d['conditions'][COND].update(dry_run_run_ids=[]))),
            ('calibration-non-numeric-run-id', 'names the DRY_RUN runs of the condition', cal_edit(lambda d: d['conditions'][COND].update(dry_run_run_ids=['abc']))),
            ('configuration-states-another-t-r', 'states T_R and T_e of the condition once, equal to the calibration record', edit(README, f'{COND}: T_R = {t_r}', f'{COND}: T_R = 0.0009')),
            ('configuration-states-another-t-e', 'states T_R and T_e of the condition once, equal to the calibration record', edit(README, f'T_e = {t_e}', 'T_e = 0.02')),
            ('configuration-states-no-thresholds', 'states T_R and T_e of the condition once, equal to the calibration record', edit(README, f'{COND}: T_R = {t_r}, T_e = {t_e}', f'{COND}: calibrated')),
            ('configuration-states-the-thresholds-twice', 'states T_R and T_e of the condition once, equal to the calibration record', edit(README, '## Next', f'- Again, {COND}: T_R = {t_r}, T_e = {t_e}\n\n## Next')),
            ('conditions-file-thresholds-null', 'the conditions file states T_R and T_e of the condition', cond_json(lambda c: c.update(thresholds={'T_R': None, 'T_e': None}))),
            ('conditions-file-without-thresholds', 'the conditions file states T_R and T_e of the condition', cond_json(lambda c: c.pop('thresholds'))),
            ('conditions-file-t-r-differs', 'the conditions file states T_R and T_e of the condition', cond_json(lambda c: c['thresholds'].update(T_R=0.0009))),
            ('conditions-file-t-e-differs', 'the conditions file states T_R and T_e of the condition', cond_json(lambda c: c['thresholds'].update(T_e=0.02))),
            ('conditions-file-t-e-boolean', 'the conditions file states T_R and T_e of the condition', cond_json(lambda c: c['thresholds'].update(T_e=True))),
            ('configuration-names-another-calibration-hash', 'names the sha256 of the calibration record', lambda s: s['files'].__setitem__(README, s['files'][README].replace(hashlib.sha256(s['files'][CAL].encode()).hexdigest(), '0' * 64))),
            ('calibration-changed-after-the-lock', 'names the sha256 of the calibration record', lambda s: s['files'].__setitem__(CAL, s['files'][CAL] + '# edited after the lock\n')),
            # the inputs of the dispatch
            ('input-not-a-hash', 'executor implementation hash is a SHA-256 value', inp('GATE_EXECUTOR_IMPLEMENTATION_SHA256', 'zz')),
            ('condition-of-another-sut', 'condition belongs to the assigned SUT', inp('GATE_ASSIGNED_SUT', 'SUT-02')),
            ('unknown-condition', 'one of the four E10 conditions', inp('GATE_CONDITION_ID', 'E10-SUT03-WEB-OTHER')),
            ('condition-of-the-other-campaign', 'one of the four E10 conditions', inp('GATE_CONDITION_ID', 'E08-SUT03-WEB-LCP')),
            ('sut-without-ground-truth', 'one of the three SUTs of E10', inp('GATE_ASSIGNED_SUT', 'SUT-04')),
            ('attempt-zero', 'attempt is a positive integer', inp('GATE_ATTEMPT', '0')),
            ('first-execution-above-50', 'first execution is an integer from 1 to 50', inp('GATE_FIRST_EXECUTION', '51')),
            ('first-execution-with-attempt-1', 'first execution is an integer from 1 to 50, and 1 for attempt 1', inp('GATE_FIRST_EXECUTION', '2')),
        ]
        for label, fragment, change in cases:
            state = base_state()
            change(state)
            with self.subTest(label):
                self.assertFailsOn(state, label, fragment)

    def test_every_gate_of_the_calibration_record_is_exercised_for_each_condition_of_the_sut(self):
        """The second condition of SUT-03 passes with its own thresholds and fails when the record gives it a value below the floor."""
        state = base_state()
        state['inputs']['GATE_CONDITION_ID'] = COND2
        state['files'][CONTROLLED] = yaml.safe_dump({'conditions': {COND2: {'status': 'CONTROLLED', 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'},
                                                                         'reverification_required': False}}})
        self.assertPasses(state, 'second-condition-pass')
        d = yaml.safe_load(state['files'][CAL])
        d['conditions'][COND2]['T_e'] = 0.001
        state['files'][CAL] = yaml.safe_dump(d)
        self.assertFailsOn(state, 'second-condition-below-floor', 'at or above the floors of the conditions file')
        # and the conditions file of the second condition must agree with the record
        state = base_state()
        state['inputs']['GATE_CONDITION_ID'] = COND2
        cdoc = json.loads(state['files'][CONDITIONS_REL])
        for c in cdoc['conditions']:
            if c['condition_id'] == COND2:
                c['thresholds']['T_R'] = 0.0003
        new = json.dumps(cdoc, indent=2) + '\n'
        state['files'][README] = state['files'][README].replace(hashlib.sha256(state['files'][CONDITIONS_REL].encode()).hexdigest(), hashlib.sha256(new.encode()).hexdigest())
        state['files'][CONDITIONS_REL] = new
        self.assertFailsOn(state, 'second-condition-conditions-file-differs', 'the conditions file states T_R and T_e of the condition')

    def test_as_is_repository_state_fails_closed(self):
        """Run the gate against this repository as it is. E10 is NOT_STARTED: it has no START row, no START record, no locked configuration, no dispatch
        authorization, no frozen prompt, no verified controlled instance and no calibration record (the instrument is pinned in `tools.visual` since the
        approval of 2026-11-28, so the six gates of G-10 hold), so with placeholder ids the gate must fail on each of these, and on the three gates of the calibration record in particular. The gates
        that depend only on files that exist (the conditions file, governance v6, the run-manifest schema v2) hold."""
        state = base_state()
        script = os.path.join(self.work, 'as-is-gate.py')
        with open(script, 'w', encoding='utf-8') as f:
            f.write(self.script)
        env = {k: v for k, v in os.environ.items() if not k.startswith('GATE_')}
        env.update(state['inputs'])
        env['GATE_CAMPAIGN_START_AUTHORIZATION_ID'] = 'NOT-ISSUED'
        env['GATE_DISPATCH_AUTHORIZATION_ID'] = 'NOT-ISSUED'
        env['GITHUB_OUTPUT'] = os.path.join(self.work, 'as-is-output.txt')
        r = subprocess.run([sys.executable, script], cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        fails = [l for l in r.stdout.splitlines() if l.startswith('FAIL ')]
        passes = [l for l in r.stdout.splitlines() if l.startswith('PASS ')]
        for fragment in ('E10 campaign status IN_PROGRESS: NOT_STARTED', 'exactly one E10 campaign START change-log row', 'START record exists',
                         'locked "Campaign configuration" record exists', 'exactly one dispatch authorization record', 'executor prompt frozen file exists',
                         'controlled instance status CONTROLLED', 'GitHub Actions environment verification VERIFIED',
                         # the calibration record: no record exists and the configuration states no thresholds
                         'calibration record exists, is an E10_CALIBRATION_RECORD of E10-visual and is LOCKED', 'calibration record covers every condition of the assigned SUT',
                         'calibration thresholds of the condition are positive numbers at or above the floors', 'names the DRY_RUN runs of the condition',
                         'states T_R and T_e of the condition once, equal to the calibration record', 'configuration names the sha256 of the calibration record',
                         # the as-is conditions file has null thresholds, so the per-condition thresholds gate fails as well
                         'the conditions file states T_R and T_e of the condition'):
            self.assertTrue(any(fragment in l for l in fails), fragment + '\n' + r.stdout)
        for fragment in ('condition is one of the four E10 conditions of the conditions file', 'condition belongs to the assigned SUT', 'condition is a web condition',
                         'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', 'run-manifest schema v2 present',
                         # G-10: the instrument pin of manifests/toolchain-manifest.yaml agrees with the executor
                         'toolchain entry tools.visual names the instrument and a version', 'tools.visual version equals PIXELMATCH_VERSION',
                         'tools.visual tarball_sha256 equals', 'tools.visual index_sha256 equals', 'tools.visual playwright_version equals',
                         'tools.visual capture_version equals'):
            self.assertTrue(any(fragment in l for l in passes), fragment + '\n' + r.stdout)
        # nothing of the repository is changed by the gate
        self.assertFalse(os.path.exists(os.path.join(REPO, 'manifests', 'e10-calibration-v1.yaml')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
