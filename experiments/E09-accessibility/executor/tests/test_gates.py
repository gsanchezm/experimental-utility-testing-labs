"""The measured-execution gate of .github/workflows/e09-measured-execution.yml, executed on fake trees.

DRAFT (operation OP-PREP-E09). The gate script is extracted from the workflow file (step id "gates", the python heredoc), written to
a temporary file, and run with the working directory set to a fake tree and the GATE_* inputs set in its environment. The
must-pass tree is complete and fictitious (fixture identifiers only, not issued authorizations); every must-fail case changes
exactly one thing and must fail on the gate it names. The "as-is" case runs against the files of this repository as they are
and must fail closed, because E09 has no START, no configuration, no dispatch authorization, no controlled instance, no frozen
prompt, and no locked activation password.
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
EXEC = os.path.join(REPO, 'experiments', 'E09-accessibility', 'executor')
sys.path.insert(0, os.path.join(EXEC))
sys.path.insert(0, HERE)

try:
    import yaml
except ImportError:  # the tests need PyYAML (a pure-Python copy is acceptable on PYTHONPATH)
    yaml = None

from executor import scanner  # noqa: E402

WORKFLOW = os.path.join(REPO, '.github', 'workflows', 'e09-measured-execution.yml')
PV = 'TEST-FIXTURE-PROMPT-v1'
AUTH_START = 'TEST-FIXTURE-E09-START'
AUTH_DISPATCH = 'TEST-FIXTURE-DISPATCH-SUT01'
PROMPT_TEXT = b'DRAFT fixture prompt text for the gate tests only.\n'
IMPL_TEXT = b'DRAFT fixture implementation text for the gate tests only.\n'
PROMPT_SHA = hashlib.sha256(PROMPT_TEXT).hexdigest()
IMPL_SHA = hashlib.sha256(IMPL_TEXT).hexdigest()
GLITCH = 'E09-A11Y-SUT01-MISSING-NAME'
CONTROL = 'E09-CTRL-SUT01-STANDARD'
# The SUT-01 web commit of the pinned manifest (design brief, section 14; configuration draft, section 3b).
WEB_COMMIT = '9ca37674d374e9303912e259641ee86baf3aabe1'


def extract_gate_script():
    with open(WORKFLOW, encoding='utf-8') as f:
        wf = yaml.safe_load(f)
    steps = wf['jobs']['gate']['steps']
    run = next(s['run'] for s in steps if s.get('id') == 'gates')
    lines = run.split('\n')
    start = lines.index("python3 - <<'PY'")
    end = lines.index('PY', start)
    return '\n'.join(lines[start + 1:end]) + '\n'


def base_state(cond=GLITCH):
    """The must-pass state: every gate satisfied by fictitious fixture content."""
    account = {GLITCH: 'a11y_glitch_user', CONTROL: 'standard_user'}[cond]
    files = {
        'manifests/study-manifest.yaml': yaml.safe_dump({'campaigns': [{'id': 'E09-accessibility', 'status': 'IN_PROGRESS'}]}),
        'protocol/CHANGELOG.md': f'| FIXTURE | experiments/E09-accessibility/README.md | campaign NOT_STARTED -> IN_PROGRESS | {AUTH_START} |\n',
        'experiments/E09-accessibility/README.md': (
            '# E09 fixture README\n\n## Campaign configuration\n\n'
            f'- Condition: {cond}\n- Schema: schemas/run-manifest.schema.v2.json\n- Executor prompt: {PV}\n'
            f'- Executor implementation SHA-256: {IMPL_SHA}\n'
            f'- Axe-core pin: {scanner.AXE_VERSION} with integrity {scanner.AXE_NPM_INTEGRITY}\n'
            f'- Browser build sha256: {scanner.AXE_MIN_SHA256}\n- Sample size: N = 50 executions per condition\n'
            f'- Web commit (SUT-01): {WEB_COMMIT}\n- Probe record: experiments/E09-accessibility/probe-record.md\n'
            f'- Declared behavior class: stochastic (glitch condition); control to confirm\n'
            '- Comparison: H5, CONFIRMATORY, count unit 1 (HD-2)\n- Scenario mapping: none required (HD-13)\n\n## Next\n'),
        'experiments/E09-accessibility/probe-record.md': 'FIXTURE probe record (not a probe).\n',
        'manifests/sut-manifest.yaml': yaml.safe_dump({'suts': {'SUT-01': {'components': {
            'web': {'repository': 'FIXTURE', 'commit_sha': WEB_COMMIT}, 'api': {'repository': 'FIXTURE', 'commit_sha': WEB_COMMIT}}}}}),
        'protocol/agent-governance-v6.md': '| Protocol state | FROZEN-PRE-DATA |\n\n### 3.7 Dispatch authorization\n',
        f'manifests/e09-dispatch-authorization-sut01-v1.yaml': yaml.safe_dump({
            'authorization_id': AUTH_DISPATCH, 'status': 'ISSUED', 'record_validity': 'VALID', 'dispatch_eligibility': 'ELIGIBLE',
            'issued_by': 'human research lead', 'authorization_date': 'FIXTURE-DATE', 'assigned_sut': 'SUT-01', 'conditions': [cond],
            'n_executions': 50, 'attempt': 1, 'campaign_start_authorization_id': AUTH_START,
            'frozen_inputs': {'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': PROMPT_SHA}}),
        'experiments/E09-accessibility/controlled-instance-status.yaml': yaml.safe_dump({'conditions': {cond: {
            'status': 'CONTROLLED', 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'},
            'reverification_required': False}}}),
        'manifests/toolchain-manifest.yaml': yaml.safe_dump({'tools': {
            'web_runner': {'version': '1.63.0'},
            'accessibility': {'version': scanner.AXE_VERSION, 'npm_integrity': scanner.AXE_NPM_INTEGRITY,
                              'pinned_by': 'FIXTURE', 'pinned_at': 'FIXTURE'}}}),
        'schemas/run-manifest.schema.v2.json': json.dumps({'$id': 'urn:eus-2026-001:schemas:run-manifest:v2'}),
        f'prompts/frozen/{PV}.md': PROMPT_TEXT.decode('utf-8'),
        'experiments/E09-accessibility/executor/run-condition.sh': IMPL_TEXT.decode('utf-8'),
        'experiments/E09-accessibility/executor/executor/scanner.py':
            f"AXE_VERSION = '{scanner.AXE_VERSION}'\nAXE_NPM_INTEGRITY = '{scanner.AXE_NPM_INTEGRITY}'\n"
            f"AXE_MIN_SHA256 = '{scanner.AXE_MIN_SHA256}'\n",
        'experiments/E09-accessibility/executor/executor/config.py':
            "ACCOUNTS = {\n    'standard_user': 'pizza123',\n    'a11y_glitch_user': 'TEST-FIXTURE-PASSWORD',\n}\n",
    }
    if cond == CONTROL:
        files['experiments/E09-accessibility/executor/executor/config.py'] = (
            "ACCOUNTS = {\n    'standard_user': 'pizza123',\n    'a11y_glitch_user': None,\n}\n")
    inputs = {'GATE_CONDITION_ID': cond, 'GATE_ASSIGNED_SUT': 'SUT-01', 'GATE_EXECUTION_ID': 'EX0001', 'GATE_ATTEMPT': '1',
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
        cls.work = tempfile.mkdtemp(prefix='e09-gate-')

    def tree(self, name):
        return os.path.join(self.work, name)

    def assertPasses(self, state, label):
        code, out = run_gate(state, self.script, self.tree(label))
        self.assertEqual(code, 0, out)
        self.assertIn('ALL GATES PASSED', out)

    def assertFailsOn(self, state, label, gate_fragment):
        code, out = run_gate(state, self.script, self.tree(label))
        self.assertNotEqual(code, 0, f'{label} unexpectedly passed:\n{out}')
        fails = [l for l in out.splitlines() if l.startswith('FAIL ')]
        self.assertTrue(any(gate_fragment in l for l in fails), f'{label}: no FAIL line names {gate_fragment!r}\n{out}')

    def test_must_pass_glitch_condition(self):
        self.assertPasses(base_state(GLITCH), 'pass-glitch')

    def test_must_pass_control_condition_needs_only_the_control_password(self):
        self.assertPasses(base_state(CONTROL), 'pass-control')

    def mutate(self, label, fragment, change, cond=GLITCH):
        state = base_state(cond)
        change(state)
        self.assertFailsOn(state, label, fragment)

    def test_must_fail_matrix(self):
        def rm(path):
            return lambda s: s['files'].pop(path)

        def put(path, text):
            return lambda s: s['files'].__setitem__(path, text)

        def edit(path, old, new):
            return lambda s: s['files'].__setitem__(path, s['files'][path].replace(old, new))

        def inp(key, value):
            return lambda s: s['inputs'].__setitem__(key, value)

        def auth(key, value):
            def f(s):
                d = yaml.safe_load(s['files']['manifests/e09-dispatch-authorization-sut01-v1.yaml'])
                d[key] = value
                s['files']['manifests/e09-dispatch-authorization-sut01-v1.yaml'] = yaml.safe_dump(d)
            return f

        def ctl(key, value):
            def f(s):
                d = yaml.safe_load(s['files']['experiments/E09-accessibility/controlled-instance-status.yaml'])
                entry = d['conditions'][GLITCH]
                if key == 'verification_status':
                    entry['github_actions_verification']['status'] = value
                elif key == 'environment_type':
                    entry['github_actions_verification']['environment_type'] = value
                else:
                    entry[key] = value
                s['files']['experiments/E09-accessibility/controlled-instance-status.yaml'] = yaml.safe_dump(d)
            return f

        def tool(key, value):
            def f(s):
                d = yaml.safe_load(s['files']['manifests/toolchain-manifest.yaml'])
                if key == 'web_runner.version':
                    d['tools']['web_runner']['version'] = value
                elif key in ('pinned_by', 'pinned_at'):
                    d['tools']['accessibility'].pop(key)
                else:
                    d['tools']['accessibility'][key] = value
                s['files']['manifests/toolchain-manifest.yaml'] = yaml.safe_dump(d)
            return f

        cases = [
            ('campaign-not-started', 'E09 campaign status IN_PROGRESS', lambda s: s['files'].__setitem__('manifests/study-manifest.yaml', yaml.safe_dump({'campaigns': [{'id': 'E09-accessibility', 'status': 'NOT_STARTED'}]}))),
            ('no-start-row', 'exactly one E09 campaign START', rm('protocol/CHANGELOG.md')),
            ('start-row-without-auth-id', 'START row carries the campaign START authorization id', put('protocol/CHANGELOG.md', 'experiments/E09-accessibility/README.md campaign NOT_STARTED -> IN_PROGRESS\n')),
            ('two-start-rows', 'exactly one E09 campaign START', lambda s: s['files'].__setitem__('protocol/CHANGELOG.md', s['files']['protocol/CHANGELOG.md'] * 2)),
            ('no-configuration-section', 'locked "Campaign configuration" record exists', put('experiments/E09-accessibility/README.md', '# no configuration\n')),
            ('configuration-without-n50', 'configuration names N = 50', edit('experiments/E09-accessibility/README.md', 'N = 50', 'N = 30')),
            ('configuration-without-axe-integrity', 'configuration names the axe-core pin', edit('experiments/E09-accessibility/README.md', scanner.AXE_NPM_INTEGRITY, 'x')),
            ('configuration-without-impl-hash', 'configuration names the executor implementation hash', edit('experiments/E09-accessibility/README.md', IMPL_SHA, 'x')),
            ('governance-draft', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', put('protocol/agent-governance-v6.md', '| Protocol state | DRAFT |\n')),
            ('governance-missing', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', rm('protocol/agent-governance-v6.md')),
            ('dispatch-authorization-absent', 'exactly one dispatch authorization record', rm('manifests/e09-dispatch-authorization-sut01-v1.yaml')),
            ('dispatch-authorization-pending', 'ISSUED, VALID, dispatch-eligible', auth('status', 'PENDING')),
            ('dispatch-authorization-not-eligible', 'ISSUED, VALID, dispatch-eligible', auth('dispatch_eligibility', 'NOT_ELIGIBLE')),
            ('dispatch-issued-by-agent', 'issued by the human research lead', auth('issued_by', 'ORCHESTRATOR')),
            ('dispatch-sut-02', 'dispatch authorization names SUT-01', auth('assigned_sut', 'SUT-02')),
            ('dispatch-condition-missing', 'dispatch authorization names this condition', auth('conditions', [CONTROL])),
            ('dispatch-n-30', 'dispatch authorization names N = 50', auth('n_executions', 30)),
            ('dispatch-start-id-mismatch', 'names the campaign START authorization id', auth('campaign_start_authorization_id', 'OTHER')),
            ('dispatch-impl-hash-mismatch', 'records the executor implementation SHA-256 equal to the input', auth('frozen_inputs', {'executor_implementation_sha256': '0' * 64, 'executor_prompt_sha256': PROMPT_SHA})),
            ('dispatch-prompt-hash-mismatch', 'records the executor prompt SHA-256 equal to the frozen prompt file', auth('frozen_inputs', {'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': '0' * 64})),
            ('controlled-instance-candidate', 'controlled instance status CONTROLLED', ctl('status', 'CANDIDATE')),
            ('github-verification-not-verified', 'GitHub Actions environment verification VERIFIED', ctl('verification_status', 'NOT_VERIFIED')),
            ('reverification-required', 'no provisioning change awaiting re-verification', ctl('reverification_required', True)),
            ('public-hosted-target', 'environment_type SELF_HOSTED', ctl('environment_type', 'PUBLIC_HOSTED')),
            ('toolchain-axe-version-null', 'toolchain accessibility entry pins axe-core', tool('version', None)),
            ('toolchain-axe-integrity-wrong', 'toolchain accessibility entry pins axe-core', tool('npm_integrity', 'sha512-x')),
            ('toolchain-axe-pinned-by-missing', 'records pinned_by and pinned_at', tool('pinned_by', None)),
            ('toolchain-playwright-other-version', 'toolchain web runner is Playwright for Python 1.63.0', tool('web_runner.version', '1.62.0')),
            ('prompt-file-missing', 'executor prompt frozen file exists', rm(f'prompts/frozen/{PV}.md')),
            ('implementation-hash-differs', 'executor implementation exists and equals the locked hash', put('experiments/E09-accessibility/executor/run-condition.sh', 'changed\n')),
            ('glitch-password-not-locked', "activation password of a11y_glitch_user is locked", put('experiments/E09-accessibility/executor/executor/config.py', "ACCOUNTS = {'standard_user': 'pizza123', 'a11y_glitch_user': None}\n")),
            ('schema-id-wrong', 'run-manifest schema v2 present with the v2 id', put('schemas/run-manifest.schema.v2.json', '{"$id": "urn:other"}')),
            ('condition-not-a-candidate', 'condition is one of the E09 candidate conditions', inp('GATE_CONDITION_ID', 'E09-OTHER-SUT01')),
            ('assigned-sut-not-sut01', 'assigned SUT is SUT-01', inp('GATE_ASSIGNED_SUT', 'SUT-02')),
            ('execution-id-malformed', 'execution_id format EXnnnn', inp('GATE_EXECUTION_ID', 'EX1')),
            ('attempt-two', 'attempt is 1 (first attempt only)', inp('GATE_ATTEMPT', '2')),
            ('implementation-hash-malformed', 'executor implementation hash is a SHA-256 value', inp('GATE_EXECUTOR_IMPLEMENTATION_SHA256', 'abc')),
            ('dispatch-attempt-two', 'dispatch authorization records attempt 1', auth('attempt', 2)),
            ('dispatch-without-date', 'dispatch authorization records attempt 1 and an authorization date', auth('authorization_date', None)),
            ('governance-without-section-3-7', 'names the per-SUT dispatch authorization of Section 3.7',
             put('protocol/agent-governance-v6.md', '| Protocol state | FROZEN-PRE-DATA |\n')),
            ('configuration-web-commit-absent', 'configuration records the SUT-01 web commit', edit('experiments/E09-accessibility/README.md', WEB_COMMIT, 'x')),
            ('sut-manifest-absent', 'configuration records the SUT-01 web commit', rm('manifests/sut-manifest.yaml')),
            ('probe-record-absent', 'configuration names a probe record', rm('experiments/E09-accessibility/probe-record.md')),
            ('behavior-class-absent', 'configuration states the declared behavior class', edit('experiments/E09-accessibility/README.md', 'behavior class', 'behaviour x')),
            ('h5-not-confirmatory', 'configuration records H5 as CONFIRMATORY', edit('experiments/E09-accessibility/README.md', 'CONFIRMATORY', 'EXPLORATORY')),
            ('hd13-absent', 'configuration records the scenario mapping decision', edit('experiments/E09-accessibility/README.md', 'HD-13', 'HD-x')),
        ]
        for label, fragment, change in cases:
            with self.subTest(case=label):
                self.mutate(label, fragment, change)

    def test_control_condition_fails_without_its_own_password(self):
        self.mutate('control-password-missing', "activation password of standard_user is locked",
                    lambda s: s['files'].__setitem__('experiments/E09-accessibility/executor/executor/config.py', "ACCOUNTS = {'standard_user': None}\n"),
                    cond=CONTROL)

    def test_as_is_repository_state_fails_closed(self):
        """The files of this repository as they are now (copied where present) must not pass the gate."""
        files = {}
        for rel in ('manifests/study-manifest.yaml', 'protocol/CHANGELOG.md', 'protocol/agent-governance-v6.md',
                    'experiments/E09-accessibility/README.md', 'manifests/toolchain-manifest.yaml', 'schemas/run-manifest.schema.v2.json',
                    'experiments/E09-accessibility/executor/run-condition.sh', 'experiments/E09-accessibility/executor/executor/scanner.py',
                    'experiments/E09-accessibility/executor/executor/config.py'):
            path = os.path.join(REPO, rel)
            if os.path.isfile(path):
                with open(path, encoding='utf-8') as f:
                    files[rel] = f.read()
        inputs = {'GATE_CONDITION_ID': GLITCH, 'GATE_ASSIGNED_SUT': 'SUT-01', 'GATE_EXECUTION_ID': 'EX0001', 'GATE_ATTEMPT': '1',
                  'GATE_CAMPAIGN_START_AUTHORIZATION_ID': AUTH_START, 'GATE_DISPATCH_AUTHORIZATION_ID': AUTH_DISPATCH,
                  'GATE_EXECUTOR_PROMPT_VERSION': PV, 'GATE_EXECUTOR_IMPLEMENTATION_SHA256': IMPL_SHA}
        code, out = run_gate({'files': files, 'inputs': inputs}, self.script, self.tree('as-is'))
        self.assertNotEqual(code, 0, out)
        for fragment in ('E09 campaign status IN_PROGRESS', 'exactly one dispatch authorization record', 'controlled instance status CONTROLLED',
                         'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', 'executor prompt frozen file exists'):
            self.assertIn(fragment, out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
