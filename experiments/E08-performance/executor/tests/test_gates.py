"""The measured-execution gate of .github/workflows/e08-measured-execution.yml, executed on fake trees (operation OP-PREP-E08).

The gate script is extracted from the workflow file (step id "gates", the python heredoc), written to a temporary file, and run with the working
directory set to a fake tree and the GATE_* inputs set in its environment. The must-pass tree is complete and fictitious (fixture identifiers
only, not issued authorizations); every must-fail case changes exactly one thing and must fail on the gate it names. The "as-is" case runs
against the files of this repository as they are and must fail closed, because E08 has no START, no configuration, no dispatch authorization,
no frozen prompt (the instrument pin was approved and the four conditions were verified by the DRY_RUN round of 2026-11-26, so those gates pass).
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
EXEC = os.path.join(REPO, 'experiments', 'E08-performance', 'executor')

try:
    import yaml
except ImportError:  # the tests need PyYAML (a pure-Python copy is acceptable on PYTHONPATH)
    yaml = None

WORKFLOW = os.path.join(REPO, '.github', 'workflows', 'e08-measured-execution.yml')
CONDITIONS_FILE = os.path.join(REPO, 'experiments', 'E08-performance', 'conditions-draft.json')
PV = 'TEST-FIXTURE-PROMPT-v1'
AUTH_START = 'TEST-FIXTURE-E08-START'
AUTH_DISPATCH = 'TEST-FIXTURE-DISPATCH-SUT03'
PROMPT_TEXT = b'DRAFT fixture prompt text for the gate tests only.\n'
IMPL_TEXT = b'DRAFT fixture implementation text for the gate tests only.\n'
PROMPT_SHA = hashlib.sha256(PROMPT_TEXT).hexdigest()
IMPL_SHA = hashlib.sha256(IMPL_TEXT).hexdigest()
COND = 'E08-SUT03-WEB-LCP'
SUT = 'SUT-03'
WEB_COMMIT = '7ab934d733f2f74d4b912e94e86f59ae0f6b7609'
PLAYWRIGHT = '1.63.0'
PROBE = 'e08-probe-v1'
DISPATCH = 'manifests/e08-dispatch-authorization-sut03-v1.yaml'
FURTHER = 'manifests/e08-further-attempt-approval-sut03-v1.yaml'
CONTROLLED = 'experiments/E08-performance/controlled-instance-status.yaml'
README = 'experiments/E08-performance/README.md'


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


def base_state(attempt='1', first='1'):
    """The must-pass state: every gate satisfied by fictitious fixture content."""
    with open(WORKFLOW, encoding='utf-8') as f:
        workflow_text = f.read()
    with open(CONDITIONS_FILE, encoding='utf-8') as f:
        conditions_text = f.read()
    cfg = (f'# E08 fixture README\n\n## Campaign configuration\n\n- Condition: {COND}\n- Schema: schemas/run-manifest.schema.v2.json\n'
           f'- Executor prompt: {PV}\n- Executor implementation SHA-256: {IMPL_SHA}\n- Sample size: N = 50 executions per condition\n'
           f'- Comparison: H5, CONFIRMATORY, count unit 1 (E08-D-2)\n- Conditions file sha256: {hashlib.sha256(conditions_text.encode()).hexdigest()}\n'
           f'- Web commit (SUT-03): {WEB_COMMIT}\n- Scenario mapping: no canonical scenario (E08-D-10)\n'
           f'- Measured workflow sha256: {hashlib.sha256(workflow_text.encode()).hexdigest()}\n\n## Next\n')
    files = {
        'manifests/study-manifest.yaml': yaml.safe_dump({'campaigns': [{'id': 'E08-performance', 'status': 'IN_PROGRESS'}]}),
        'protocol/CHANGELOG.md': f'| FIXTURE | {README} | campaign NOT_STARTED -> IN_PROGRESS | {AUTH_START} |\n',
        README: cfg,
        'experiments/E08-performance/conditions-draft.json': conditions_text,
        'manifests/e08-campaign-start-v1.yaml': yaml.safe_dump({'record_class': 'CAMPAIGN_START', 'campaign_id': 'E08-performance', 'authorization_id': AUTH_START}),
        'manifests/sut-manifest.yaml': yaml.safe_dump({'suts': {SUT: {'components': {'web': {'repository': 'FIXTURE', 'commit_sha': WEB_COMMIT, 'release': None}}}}}),
        'protocol/agent-governance-v6.md': '| Protocol state | FROZEN-PRE-DATA |\n\n### 3.7 Dispatch authorization\n',
        DISPATCH: yaml.safe_dump({
            'authorization_id': AUTH_DISPATCH, 'status': 'ISSUED', 'record_validity': 'VALID', 'dispatch_eligibility': 'ELIGIBLE', 'revoked': False,
            'issued_by': 'human research lead', 'authorization_date': 'FIXTURE-DATE', 'assigned_sut': SUT, 'conditions': [COND, 'E08-SUT03-WEB-CLS'],
            'n_executions': 50, 'attempt': 1, 'campaign_start_authorization_id': AUTH_START,
            'frozen_inputs': {'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': PROMPT_SHA}}),
        CONTROLLED: yaml.safe_dump({'conditions': {COND: {'status': 'CONTROLLED', 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'},
                                                          'reverification_required': False}}}),
        'manifests/toolchain-manifest.yaml': yaml.safe_dump({'tools': {
            'web_runner': {'version': PLAYWRIGHT},
            'performance': {'candidate': 'Playwright with the browser Performance APIs', 'version': PLAYWRIGHT, 'probe_version': PROBE}}}),
        'schemas/run-manifest.schema.v2.json': json.dumps({'$id': 'urn:eus-2026-001:schemas:run-manifest:v2'}),
        f'prompts/frozen/{PV}.md': PROMPT_TEXT.decode('utf-8'),
        'experiments/E08-performance/executor/run-condition.sh': IMPL_TEXT.decode('utf-8'),
        'experiments/E08-performance/executor/requirements.txt': f'playwright=={PLAYWRIGHT} \\\n    --hash=sha256:00\n',
        'experiments/E08-performance/executor/executor/probe.py': f"PROBE_VERSION = '{PROBE}'\n",
        '.github/workflows/e08-measured-execution.yml': workflow_text,
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
        cls.work = tempfile.mkdtemp(prefix='e08-gate-')

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

    def test_a_further_attempt_passes_only_with_its_own_approval(self):
        state = base_state(attempt='2', first='7')
        self.assertFailsOn(state, 'further-without-approval', 'exactly one further-attempt approval entry')
        state['files'][FURTHER] = yaml.safe_dump({
            'record_class': 'E08_FURTHER_ATTEMPT_APPROVAL', 'status': 'ISSUED', 'revoked': False, 'assigned_sut': SUT, 'issued_by': 'human research lead',
            'dispatch_authorization_id': AUTH_DISPATCH, 'campaign_start_authorization_id': AUTH_START, 'executor_implementation_sha256': IMPL_SHA,
            'executor_prompt_version': PV, 'executor_prompt_sha256': PROMPT_SHA, 'governing_protocol': 'protocol/agent-governance-v6.md, Section 3.7',
            'attempts': [{'condition_id': COND, 'first_execution': 7, 'attempt': 2, 'previous_attempt': 1}]})
        self.assertPasses(state, 'further-with-approval')

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

        cases = [
            ('campaign-not-started', 'E08 campaign status IN_PROGRESS', put('manifests/study-manifest.yaml', yaml.safe_dump({'campaigns': [{'id': 'E08-performance', 'status': 'NOT_STARTED'}]}))),
            ('no-start-row', 'exactly one E08 campaign START', rm('protocol/CHANGELOG.md')),
            ('two-start-rows', 'exactly one E08 campaign START', lambda s: s['files'].__setitem__('protocol/CHANGELOG.md', s['files']['protocol/CHANGELOG.md'] * 2)),
            ('start-row-without-id', 'START row carries the campaign START authorization id', put('protocol/CHANGELOG.md', f'| X | {README} | campaign NOT_STARTED -> IN_PROGRESS |\n')),
            ('no-start-record', 'START record exists', rm('manifests/e08-campaign-start-v1.yaml')),
            ('no-configuration', 'locked "Campaign configuration" record exists', put(README, '# nothing\n')),
            ('configuration-without-n50', 'configuration names N = 50', edit(README, 'N = 50', 'N = 30')),
            ('configuration-without-h5', 'configuration names the H5 hypothesis label', edit(README, 'H5', 'H3')),
            ('configuration-without-scenario-statement', 'no canonical scenario', edit(README, 'no canonical scenario', 'a scenario')),
            ('configuration-without-commit', 'pinned commit of every E08 surface component', edit(README, WEB_COMMIT, 'x')),
            ('conditions-file-changed', 'sha256 of the conditions file', lambda s: s['files'].__setitem__('experiments/E08-performance/conditions-draft.json', s['files']['experiments/E08-performance/conditions-draft.json'] + ' ')),
            ('workflow-changed', 'sha256 of the measured workflow file', lambda s: s['files'].__setitem__('.github/workflows/e08-measured-execution.yml', s['files']['.github/workflows/e08-measured-execution.yml'] + '# x\n')),
            ('no-dispatch-authorization', 'exactly one dispatch authorization record', rm(DISPATCH)),
            ('dispatch-not-issued', 'dispatch authorization is ISSUED', ydict(DISPATCH, lambda d: d.update(status='PREPARED'))),
            ('dispatch-revoked', 'dispatch authorization is ISSUED', ydict(DISPATCH, lambda d: d.update(revoked=True))),
            ('dispatch-other-sut', 'dispatch authorization names the assigned SUT', ydict(DISPATCH, lambda d: d.update(assigned_sut='SUT-02'))),
            ('dispatch-without-condition', 'dispatch authorization names this condition', ydict(DISPATCH, lambda d: d.update(conditions=['E08-SUT03-WEB-CLS']))),
            ('dispatch-n30', 'dispatch authorization names N = 50', ydict(DISPATCH, lambda d: d.update(n_executions=30))),
            ('dispatch-other-implementation', 'executor implementation SHA-256 equal to the input', ydict(DISPATCH, lambda d: d['frozen_inputs'].update(executor_implementation_sha256='0' * 64))),
            ('dispatch-other-prompt', 'executor prompt SHA-256 equal to the frozen prompt file', ydict(DISPATCH, lambda d: d['frozen_inputs'].update(executor_prompt_sha256='0' * 64))),
            ('prompt-not-frozen', 'executor prompt frozen file exists', rm(f'prompts/frozen/{PV}.md')),
            ('governance-draft', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', put('protocol/agent-governance-v6.md', '| Protocol state | DRAFT |\n\n### 3.7 Dispatch authorization\n')),
            ('governance-without-3-7', 'names the per-SUT dispatch authorization of Section 3.7', put('protocol/agent-governance-v6.md', '| Protocol state | FROZEN-PRE-DATA |\n')),
            ('no-schema-v2', 'run-manifest schema v2 present', put('schemas/run-manifest.schema.v2.json', '{}')),
            ('instance-not-controlled', 'controlled instance status CONTROLLED', ydict(CONTROLLED, lambda d: d['conditions'][COND].update(status='NOT_CONTROLLED'))),
            ('instance-not-verified', 'GitHub Actions environment verification VERIFIED', ydict(CONTROLLED, lambda d: d['conditions'][COND]['github_actions_verification'].update(status='NOT_VERIFIED'))),
            ('reverification-required', 'no provisioning change awaiting re-verification', ydict(CONTROLLED, lambda d: d['conditions'][COND].update(reverification_required=True))),
            ('public-hosted', 'environment_type SELF_HOSTED', ydict(CONTROLLED, lambda d: d['conditions'][COND]['github_actions_verification'].update(environment_type='PUBLIC_HOSTED'))),
            ('implementation-changed', 'executor implementation exists and equals the locked hash', put('experiments/E08-performance/executor/run-condition.sh', 'other\n')),
            ('instrument-tbd', 'tools.performance names the instrument and a version', ydict('manifests/toolchain-manifest.yaml', lambda d: d['tools']['performance'].update(candidate='TBD between appropriate open-source tools', version=None))),
            ('instrument-other-version', 'tools.performance version equals the Playwright pin', ydict('manifests/toolchain-manifest.yaml', lambda d: d['tools']['performance'].update(version='1.60.0'))),
            ('instrument-other-web-runner', 'tools.performance version equals the Playwright pin', ydict('manifests/toolchain-manifest.yaml', lambda d: d['tools']['web_runner'].update(version='1.60.0'))),
            ('instrument-other-probe', 'names the measurement script version', ydict('manifests/toolchain-manifest.yaml', lambda d: d['tools']['performance'].update(probe_version='e08-probe-v0'))),
            ('input-not-a-hash', 'executor implementation hash is a SHA-256 value', inp('GATE_EXECUTOR_IMPLEMENTATION_SHA256', 'zz')),
            ('condition-of-another-sut', 'condition belongs to the assigned SUT', inp('GATE_ASSIGNED_SUT', 'SUT-02')),
            ('unknown-condition', 'one of the four E08 conditions', inp('GATE_CONDITION_ID', 'E08-SUT03-WEB-OTHER')),
            ('sut-without-ground-truth', 'one of the three SUTs of E08', inp('GATE_ASSIGNED_SUT', 'SUT-04')),
            ('attempt-zero', 'attempt is a positive integer', inp('GATE_ATTEMPT', '0')),
            ('first-execution-above-50', 'first execution is an integer from 1 to 50', inp('GATE_FIRST_EXECUTION', '51')),
            ('first-execution-with-attempt-1', 'first execution is an integer from 1 to 50, and 1 for attempt 1', inp('GATE_FIRST_EXECUTION', '2')),
        ]
        for label, fragment, change in cases:
            state = base_state()
            change(state)
            with self.subTest(label):
                self.assertFailsOn(state, label, fragment)

    def test_as_is_repository_state_fails_closed(self):
        """Run the gate against this repository as it is: the START was applied on 2026-11-26 (E08-START-AUTH-01) and no dispatch authorization was issued, so with
        placeholder ids the gate must fail on the START id, the dispatch authorization and the frozen prompt of the placeholder, while the START status and the
        locked configuration hold."""
        state = base_state()
        proc = subprocess.run([sys.executable, '-c', 'pass'])
        self.assertEqual(proc.returncode, 0)
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
        for fragment in ('START row carries the campaign START authorization id', 'exactly one dispatch authorization record', 'executor prompt frozen file exists'):
            self.assertTrue(any(fragment in l for l in fails), fragment + '\n' + r.stdout)
        passes_start = [l for l in r.stdout.splitlines() if l.startswith('PASS ')]
        for fragment in ('E08 campaign status IN_PROGRESS', 'locked "Campaign configuration" record exists'):
            self.assertTrue(any(fragment in l for l in passes_start), fragment + '\n' + r.stdout)
        # the instrument pin was approved on 2026-11-26 (decisions v23) and the first DRY_RUN round verified the four conditions: their gates hold on the repository as it is
        passes = [l for l in r.stdout.splitlines() if l.startswith('PASS ')]
        for fragment in ('toolchain entry tools.performance names the instrument', 'tools.performance version equals the Playwright pin', 'tools.performance names the measurement script version',
                         'controlled instance status CONTROLLED', 'GitHub Actions environment verification VERIFIED', 'environment_type SELF_HOSTED'):
            self.assertTrue(any(fragment in l for l in passes), fragment + '\n' + r.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
