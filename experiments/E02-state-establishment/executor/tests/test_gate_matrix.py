"""Gate matrix for the E02 measured-execution and environment-verification workflows (DRAFT, operation OP-PREP-E02).

The gate script is EXTRACTED from each workflow file (the heredoc of the step with id gates) and EXECUTED on fake repository
trees: one fixture tree that satisfies every gate, one mutation per gate that must fail it, and the real worktree, which must
fail closed. The guard steps (bash) are extracted and executed the same way. Nothing is dispatched and no SUT is touched.

Run: python3 tests/test_gate_matrix.py -v   (set EUS_PYLIB to a directory with PyYAML if it is not importable; the value is read from the
environment and never written into a record)
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
EXECUTOR_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.abspath(os.path.join(EXECUTOR_DIR, '..', '..', '..'))
if os.environ.get('EUS_PYLIB'):
    sys.path.insert(0, os.environ['EUS_PYLIB'])
import yaml  # noqa: E402

MEASURED = os.environ.get('EUS_E02_MEASURED') or os.path.join(REPO_ROOT, '.github', 'workflows', 'e02-measured-execution.yml')
VERIFY = os.path.join(REPO_ROOT, '.github', 'workflows', 'e02-environment-verification.yml')

AUTH = 'E02-START-AUTH-01'
DISPATCH_ID = 'E02-DISPATCH-SUT01-AUTH-01'
PV = 'ORCHESTRATOR-E02-state-establishment-v1'
COND = 'E02-CS003-SUT01-API'
FURTHER = 'manifests/e02-further-attempt-approval-sut01-v1.yaml'
SUT = 'SUT-01'
EXEC_ID = 'EX0001'
IMPL_TEXT = 'set -euo pipefail\necho fixture implementation\n'
REQ_TEXT = 'playwright==1.63.0\n'
CHANGELOG_ROW = ('| 2026-11-10 | experiments/E02-state-establishment/README.md | none | none | campaign NOT_STARTED -> IN_PROGRESS | '
                 f'E02 campaign start, authorization {AUTH}. |\n')


def sha_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def extract(workflow, job, step_id=None, step_name=None):
    """The run text of one step, as GitHub reads it (the YAML block scalar has its indentation removed)."""
    with open(workflow, encoding='utf-8') as f:
        wf = yaml.safe_load(f)
    for s in wf['jobs'][job]['steps']:
        if (step_id and s.get('id') == step_id) or (step_name and s.get('name') == step_name):
            return s
    raise KeyError(f'{job}: step {step_id or step_name} not found')


def heredoc_python(run):
    """The Python program of a run text that is `python3 - <<'PY' ... PY`."""
    lines = run.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == "python3 - <<'PY'")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == 'PY')
    return '\n'.join(lines[start + 1:end]) + '\n'


def fixture(impl_sha, req_sha):
    """Every file the gate reads, in the state that satisfies every gate. Keys are repository-relative paths."""
    readme = ('# E02 fixture README\n\nSome text.\n\n## Campaign configuration\n\n'
              f'Condition: {COND}\nSchema: schemas/run-manifest.schema.v2.json\nPrompt version: {PV}\n'
              f'Executor implementation sha256: {impl_sha}\nExecutor requirements sha256: {req_sha}\n'
              'Scenarios: CS-003 and CS-004 (both FROZEN)\n'
              'H2 comparison: SUT-01 versus SUT-02 and SUT-01 versus SUT-03, WEB, establish Required Actions, descriptive (G-E02-D)\n\n'
              '## Current status\n\nNOT STARTED\n')
    mapping = lambda sc, comp, surfaces, status='FROZEN': json.dumps({  # noqa: E731
        'mapping_status': status,
        'mappings': [{'sut_id': SUT, 'comparability': comp, 'surfaces_used': surfaces},
                     {'sut_id': 'SUT-02', 'comparability': 'COMPARABLE', 'surfaces_used': ['WEB']}]})
    auth = {'record_class': 'E02_DISPATCH_AUTHORIZATION', 'authorization_id': DISPATCH_ID, 'assigned_sut': SUT,
            'status': 'ISSUED', 'revoked': False, 'campaign_start_authorization_id': AUTH,
            'executor_implementation_sha256': impl_sha, 'executor_prompt_version': PV, 'attempt': 1,
            'governing_protocol': 'protocol/agent-governance-v6.md, Section 3.7',
            'executor_prompt_sha256': sha_text('# frozen prompt fixture\n'),
            'conditions': [{'condition_id': COND, 'executions': 50}]}
    cis = {'conditions': {COND: {'status': 'CONTROLLED', 'reverification_required': False,
                                 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'}}}}
    return {
        'manifests/study-manifest.yaml': json.dumps({'campaigns': [{'id': 'E02-state-establishment', 'status': 'IN_PROGRESS'}]}),
        'protocol/CHANGELOG.md': '# Changelog\n\n' + CHANGELOG_ROW,
        'experiments/E02-state-establishment/README.md': readme,
        'experiments/E02-state-establishment/executor/run-condition.sh': IMPL_TEXT,
        'experiments/E02-state-establishment/executor/requirements.txt': REQ_TEXT,
        'experiments/E02-state-establishment/controlled-instance-status.yaml': json.dumps(cis),
        'experiments/scenario-mappings/CS-003.yaml': mapping('CS-003', 'COMPARABLE', ['API', 'WEB']),
        'experiments/scenario-mappings/CS-004.yaml': mapping('CS-004', 'COMPARABLE', ['WEB']),
        'schemas/run-manifest.schema.v2.json': json.dumps({'$id': 'urn:eus-2026-001:schemas:run-manifest:v2'}),
        'protocol/agent-governance-v6.md': '# Agent governance\n\n| Protocol state | FROZEN-PRE-DATA |\n\n'
                                           '### 3.7 Dispatch authorization for E02 and E04–E12 (new in v6)\n',
        'manifests/e02-dispatch-authorization-sut01-v1.yaml': json.dumps(auth),
        f'prompts/frozen/{PV}.md': '# frozen prompt fixture\n',
        f'prompts/working/{PV}.md': '# frozen prompt fixture\n',  # byte-identical to the frozen copy, as the START leaves it
        '.github/workflows/e02-measured-execution.yml': 'name: fixture\n',
    }


def approval(impl_sha, **over):
    """A further-attempt approval record (OP-CI-18) for attempt 2 of EX0001 of the fixture condition."""
    d = {'record_class': 'E02_FURTHER_ATTEMPT_APPROVAL', 'approval_id': 'E02-FURTHER-ATTEMPT-SUT01-APPROVAL-01', 'assigned_sut': SUT,
         'status': 'ISSUED', 'revoked': False, 'dispatch_authorization_id': DISPATCH_ID, 'campaign_start_authorization_id': AUTH,
         'executor_implementation_sha256': impl_sha, 'executor_prompt_version': PV, 'executor_prompt_sha256': sha_text('# frozen prompt fixture\n'),
         'governing_protocol': 'protocol/agent-governance-v6.md, Section 3.7 (Further attempts)',
         'attempts': [{'condition_id': COND, 'execution_id': EXEC_ID, 'attempt': 2, 'previous_attempt': 1}]}
    d.update(over)
    return json.dumps(d)


def write_tree(files):
    root = tempfile.mkdtemp(prefix='e02-gate-')
    for rel, content in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    return root


def run_gate(script, cwd, env_values):
    """Run the gate program with cwd as the repository root; GITHUB_OUTPUT goes to a temporary file outside the tree."""
    fd, output = tempfile.mkstemp(prefix='e02-github-output-')
    os.close(fd)
    env = {k: v for k, v in os.environ.items() if not k.startswith('GATE_')}
    env.update(env_values)
    env['GITHUB_OUTPUT'] = output
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    if os.environ.get('EUS_PYLIB'):
        env['PYTHONPATH'] = os.environ['EUS_PYLIB']
    try:
        proc = subprocess.run([sys.executable, '-'], input=script, text=True, cwd=cwd, env=env, capture_output=True)
    finally:
        os.remove(output)
    return proc.returncode, proc.stdout + proc.stderr, output


class GateMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.impl_sha = sha_text(IMPL_TEXT)
        cls.req_sha = sha_text(REQ_TEXT)
        cls.measured_script = heredoc_python(extract(MEASURED, 'gate', step_id='gates')['run'])
        cls.verify_script = heredoc_python(extract(VERIFY, 'gate', step_id='gates')['run'])
        cls.measured_env = {'GATE_CONDITION_ID': COND, 'GATE_ASSIGNED_SUT': SUT, 'GATE_EXECUTION_ID': EXEC_ID, 'GATE_ATTEMPT': '1',
                            'GATE_CAMPAIGN_START_AUTHORIZATION_ID': AUTH, 'GATE_DISPATCH_AUTHORIZATION_ID': DISPATCH_ID,
                            'GATE_EXECUTOR_PROMPT_VERSION': PV, 'GATE_EXECUTOR_IMPLEMENTATION_SHA256': cls.impl_sha}
        cls.verify_env = {'GATE_CONDITION_ID': COND, 'GATE_ASSIGNED_SUT': SUT, 'GATE_EXECUTION_ID': 'DR0001',
                          'GATE_EXECUTOR_PROMPT_VERSION': PV, 'GATE_EXECUTOR_IMPLEMENTATION_SHA256': cls.impl_sha}
        cls.results = []

    def _tree(self, mutate=None):
        files = fixture(self.impl_sha, self.req_sha)
        if mutate:
            mutate(files)
        root = write_tree(files)
        self.addCleanup(shutil.rmtree, root, True)
        return root

    def _check(self, name, mutate, expect_fail_text, env=None, script=None):
        root = self._tree(mutate)
        code, out, _ = run_gate(script or self.measured_script, root, env or self.measured_env)
        self.results.append((name, code))
        if expect_fail_text is None:
            self.assertEqual(code, 0, f'{name} must pass:\n{out}')
            self.assertIn('ALL GATES PASSED', out)
        else:
            self.assertNotEqual(code, 0, f'{name} must fail:\n{out}')
            self.assertIn(expect_fail_text, out, f'{name}: the failing gate is not named:\n{out}')
            self.assertNotIn('Traceback', out, f'{name}: the gate must fail by its gate, not by a traceback:\n{out}')

    def test_fixture_passes_every_gate(self):
        self._check('fixture-pass', None, None)

    def test_mutations_of_the_measured_gate_each_fail_closed(self):
        def set_json(path, key, value):
            def m(files):
                d = json.loads(files[path])
                d[key] = value
                files[path] = json.dumps(d)
            return m

        def drop_auth_row(files):
            files['protocol/CHANGELOG.md'] = '# Changelog\n\n'

        cases = [
            ('campaign not IN_PROGRESS', set_json('manifests/study-manifest.yaml', 'campaigns', [{'id': 'E02-state-establishment', 'status': 'NOT_STARTED'}]), 'E02 campaign status is IN_PROGRESS'),
            ('no START row', drop_auth_row, 'exactly one E02 campaign START change-log row'),
            ('START row without the id', lambda f: f.__setitem__('protocol/CHANGELOG.md', CHANGELOG_ROW.replace(AUTH, 'E02-START-AUTH-99')), 'the E02 START row carries the START authorization id'),
            ('no configuration section', lambda f: f.__setitem__('experiments/E02-state-establishment/README.md', '# no section\n'), 'locked "Campaign configuration" section exists'),
            ('configuration without the condition', lambda f: f.__setitem__('experiments/E02-state-establishment/README.md', f.get('experiments/E02-state-establishment/README.md').replace(COND, 'E02-CS003-SUT01-WEB')), 'configuration names the condition'),
            ('configuration without the prompt version', lambda f: f.__setitem__('experiments/E02-state-establishment/README.md', f['experiments/E02-state-establishment/README.md'].replace(PV, 'other')), 'configuration names the executor prompt version'),
            ('configuration without the implementation hash', lambda f: f.__setitem__('experiments/E02-state-establishment/README.md', f['experiments/E02-state-establishment/README.md'].replace(self.impl_sha, '0' * 64)), 'configuration names the executor implementation hash'),
            ('configuration without the requirements hash', lambda f: f.__setitem__('experiments/E02-state-establishment/README.md', f['experiments/E02-state-establishment/README.md'].replace(self.req_sha, '0' * 64)), 'configuration names the executor requirements hash'),
            ('configuration cites CS-002', lambda f: f.__setitem__('experiments/E02-state-establishment/README.md', f['experiments/E02-state-establishment/README.md'].replace('Scenarios:', 'Scenarios: CS-002 and')), 'configuration cites no excluded mapping (CS-002)'),
            ('CS-003 DRAFT', set_json('experiments/scenario-mappings/CS-003.yaml', 'mapping_status', 'DRAFT'), 'CS-003 mapping is FROZEN'),
            ('CS-004 absent', lambda f: f.pop('experiments/scenario-mappings/CS-004.yaml'), 'CS-004 mapping is FROZEN'),
            ('SUT not COMPARABLE on the scenario', set_json('experiments/scenario-mappings/CS-003.yaml', 'mappings', [{'sut_id': SUT, 'comparability': 'NOT_COMPARABLE', 'surfaces_used': ['API', 'WEB']}]), 'is COMPARABLE on CS-003 for API'),
            ('surface not mapped for the SUT', set_json('experiments/scenario-mappings/CS-003.yaml', 'mappings', [{'sut_id': SUT, 'comparability': 'COMPARABLE', 'surfaces_used': ['WEB']}]), 'is COMPARABLE on CS-003 for API'),
            ('schema without the v2 identifier', set_json('schemas/run-manifest.schema.v2.json', '$id', 'urn:eus-2026-001:schemas:run-manifest:v1'), 'schema v2 present with the v2 identifier'),
            ('governance DRAFT', lambda f: f.__setitem__('protocol/agent-governance-v6.md', '| Protocol state | DRAFT |\n'), 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED'),
            ('governance absent', lambda f: f.pop('protocol/agent-governance-v6.md'), 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED'),
            ('no dispatch authorization file', lambda f: f.pop('manifests/e02-dispatch-authorization-sut01-v1.yaml'), 'exactly one E02 dispatch authorization record names this dispatch id'),
            ('dispatch authorization DRAFT', set_json('manifests/e02-dispatch-authorization-sut01-v1.yaml', 'status', 'DRAFT'), 'the authorization is an ISSUED, unrevoked E02 dispatch authorization'),
            ('dispatch authorization revoked', set_json('manifests/e02-dispatch-authorization-sut01-v1.yaml', 'revoked', True), 'the authorization is an ISSUED, unrevoked E02 dispatch authorization'),
            ('dispatch authorization for another SUT', set_json('manifests/e02-dispatch-authorization-sut01-v1.yaml', 'assigned_sut', 'SUT-02'), 'the authorization names the assigned SUT'),
            ('dispatch authorization with zero executions', lambda f: f.__setitem__('manifests/e02-dispatch-authorization-sut01-v1.yaml', json.dumps({**json.loads(f['manifests/e02-dispatch-authorization-sut01-v1.yaml']), 'conditions': [{'condition_id': COND, 'executions': 0}]})), 'the authorization names this condition, N executions'),
            ('dispatch authorization with another START id', set_json('manifests/e02-dispatch-authorization-sut01-v1.yaml', 'campaign_start_authorization_id', 'E02-START-AUTH-02'), 'the authorization names the START id'),
            ('dispatch authorization with another implementation hash', set_json('manifests/e02-dispatch-authorization-sut01-v1.yaml', 'executor_implementation_sha256', '0' * 64), 'the authorization names the START id, the implementation hash'),
            ('dispatch authorization for attempt 2', set_json('manifests/e02-dispatch-authorization-sut01-v1.yaml', 'attempt', 2), 'the authorization is for attempt 1'),
            ('configuration without the H2 specification', lambda f: f.__setitem__('experiments/E02-state-establishment/README.md', f['experiments/E02-state-establishment/README.md'].replace('H2 comparison', 'comparison')), 'configuration names the H2 comparison specification'),
            ('governance without Section 3.7', lambda f: f.__setitem__('protocol/agent-governance-v6.md', '| Protocol state | FROZEN-PRE-DATA |\n'), 'governance v6 contains Section 3.7'),
            ('authorization prompt SHA-256 mismatch', set_json('manifests/e02-dispatch-authorization-sut01-v1.yaml', 'executor_prompt_sha256', '0' * 64), 'the authorization names the executor prompt SHA-256'),
            ('two authorization files name the same id', lambda f: f.__setitem__('manifests/e02-dispatch-authorization-sut01-v2.yaml', f['manifests/e02-dispatch-authorization-sut01-v1.yaml']), 'exactly one E02 dispatch authorization record names this dispatch id'),
            ('controlled instance absent', lambda f: f.pop('experiments/E02-state-establishment/controlled-instance-status.yaml'), 'controlled instance of this condition is CONTROLLED'),
            ('controlled instance not CONTROLLED', set_json('experiments/E02-state-establishment/controlled-instance-status.yaml', 'conditions', {COND: {'status': 'NOT_CONTROLLED', 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'}}}), 'controlled instance of this condition is CONTROLLED'),
            ('GitHub Actions verification not VERIFIED', set_json('experiments/E02-state-establishment/controlled-instance-status.yaml', 'conditions', {COND: {'status': 'CONTROLLED', 'github_actions_verification': {'status': 'NOT_VERIFIED', 'environment_type': 'SELF_HOSTED'}}}), 'GitHub Actions verification of this condition is VERIFIED'),
            ('reverification required', set_json('experiments/E02-state-establishment/controlled-instance-status.yaml', 'conditions', {COND: {'status': 'CONTROLLED', 'reverification_required': True, 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'}}}), 'no provisioning change awaits re-verification'),
            ('PUBLIC_HOSTED instance', set_json('experiments/E02-state-establishment/controlled-instance-status.yaml', 'conditions', {COND: {'status': 'CONTROLLED', 'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'PUBLIC_HOSTED'}}}), 'environment_type is SELF_HOSTED or LOCAL'),
            ('prompt file missing', lambda f: f.pop(f'prompts/frozen/{PV}.md'), 'executor prompt is a frozen file'),
            ('implementation file missing', lambda f: f.pop('experiments/E02-state-establishment/executor/run-condition.sh'), 'executor implementation exists'),
            ('implementation changed after the lock', lambda f: f.__setitem__('experiments/E02-state-establishment/executor/run-condition.sh', IMPL_TEXT + '# edited\n'), 'executor implementation hash equals the input and the configuration'),
            ('condition not one of the ten', None, 'condition is one of the ten E02 conditions'),
            ('condition of another SUT', None, 'condition matches the assigned SUT'),
            ('execution id malformed', None, 'execution_id has the format EXnnnn'),
            ('attempt 2 without an approval record', None, 'exactly one further-attempt approval entry names this condition, this execution and this attempt'),
            ('attempt 0', None, 'attempt is a positive integer'),
            ('attempt not a number', None, 'attempt is a positive integer'),
            ('prompt version with a path', None, 'executor prompt version is a plain identifier'),
        ]
        envs = {
            'condition not one of the ten': {'GATE_CONDITION_ID': 'E02-CS003-SUT06-API'},
            'condition of another SUT': {'GATE_ASSIGNED_SUT': 'SUT-02'},
            'execution id malformed': {'GATE_EXECUTION_ID': 'EX1'},
            'attempt 2 without an approval record': {'GATE_ATTEMPT': '2'},
            'attempt 0': {'GATE_ATTEMPT': '0'},
            'attempt not a number': {'GATE_ATTEMPT': 'x'},
            'prompt version with a path': {'GATE_EXECUTOR_PROMPT_VERSION': '../x'},
        }
        for name, mutate, text in cases:
            with self.subTest(case=name):
                env = {**self.measured_env, **envs.get(name, {})}
                self._check(name, mutate, text, env=env)

    def test_further_attempt_gate(self):
        env2 = {**self.measured_env, 'GATE_ATTEMPT': '2'}
        put = lambda **over: (lambda f: f.__setitem__(FURTHER, approval(self.impl_sha, **over)))  # noqa: E731
        entry = lambda **over: [{'condition_id': COND, 'execution_id': EXEC_ID, 'attempt': 2, 'previous_attempt': 1, **over}]  # noqa: E731
        # attempt 1 is unchanged by the approval record: it passes with or without one
        self._check('attempt 1 with an unrelated approval record present', put(), None)
        # the approved further attempt passes every gate
        self._check('attempt 2 with its approval', put(), None, env=env2)
        cases = [
            ('approval for another execution', put(attempts=entry(execution_id='EX0002')), 'exactly one further-attempt approval entry'),
            ('approval for another condition', put(attempts=entry(condition_id='E02-CS003-SUT01-WEB')), 'exactly one further-attempt approval entry'),
            ('approval for attempt 3 only', put(attempts=entry(attempt=3, previous_attempt=2)), 'exactly one further-attempt approval entry'),
            ('approval entry names the wrong previous attempt', put(attempts=entry(previous_attempt=2)), 'names the attempt before this one'),
            ('approval DRAFT', put(status='DRAFT'), 'ISSUED, unrevoked E02 further-attempt approval'),
            ('approval revoked', put(revoked=True), 'ISSUED, unrevoked E02 further-attempt approval'),
            ('approval for another SUT', put(assigned_sut='SUT-02'), 'ISSUED, unrevoked E02 further-attempt approval'),
            ('approval of another record class', put(record_class='E02_DISPATCH_AUTHORIZATION'), 'ISSUED, unrevoked E02 further-attempt approval'),
            ('approval cites another dispatch authorization', put(dispatch_authorization_id='E02-DISPATCH-SUT01-AUTH-99'), 'cites the dispatch authorization of this dispatch'),
            ('approval cites another START id', put(campaign_start_authorization_id='E02-START-AUTH-02'), 'cites the dispatch authorization of this dispatch'),
            ('approval cites another implementation hash', put(executor_implementation_sha256='0' * 64), 'cites the dispatch authorization of this dispatch'),
            ('approval cites another prompt SHA-256', put(executor_prompt_sha256='0' * 64), 'names the executor prompt SHA-256, which equals the frozen prompt file'),
            ('approval cites no governance section', put(governing_protocol='none'), 'names the attempt before this one'),
            ('two approval files name the same attempt', lambda f: (f.__setitem__(FURTHER, approval(self.impl_sha)), f.__setitem__(FURTHER.replace('-v1', '-v2'), approval(self.impl_sha))), 'exactly one further-attempt approval entry'),
            ('no approval file at all', None, 'exactly one further-attempt approval entry'),
        ]
        for name, mutate, text in cases:
            with self.subTest(case=name):
                self._check(name, mutate, text, env=env2)
        # the dispatch authorization still admits attempt 1 only: attempt 2 under an authorization that says attempt 2 is refused
        def auth_for_attempt_2(f):
            d = json.loads(f['manifests/e02-dispatch-authorization-sut01-v1.yaml']); d['attempt'] = 2
            f['manifests/e02-dispatch-authorization-sut01-v1.yaml'] = json.dumps(d); f[FURTHER] = approval(self.impl_sha)
        self._check('authorization itself edited to attempt 2', auth_for_attempt_2, 'the authorization is for attempt 1', env=env2)

    def test_verification_gate_fails_closed_today_and_passes_on_the_fixture(self):
        self._check('verify-fixture-pass', None, None, env=self.verify_env, script=self.verify_script)
        self._check('verify-governance-draft', lambda f: f.__setitem__('protocol/agent-governance-v6.md', '| Protocol state | DRAFT |\n'),
                    'governance v6 is FROZEN-PRE-DATA or AMENDED', env=self.verify_env, script=self.verify_script)
        # OP-CI-17: the DRY_RUN verification precedes the START, so it checks the working prompt; the frozen copy is written at the START
        self._check('verify-working-prompt-missing', lambda f: f.pop(f'prompts/working/{PV}.md'), 'executor prompt working copy exists',
                    env=self.verify_env, script=self.verify_script)
        self._check('verify-before-start-no-frozen-copy', lambda f: f.pop(f'prompts/frozen/{PV}.md'), None,
                    env=self.verify_env, script=self.verify_script)
        self._check('verify-frozen-copy-differs', lambda f: f.__setitem__(f'prompts/frozen/{PV}.md', '# another text\n'),
                    'is byte-identical to the working copy', env=self.verify_env, script=self.verify_script)
        self._check('verify-hash-mismatch', None, 'executor implementation hash equals the input',
                    env={**self.verify_env, 'GATE_EXECUTOR_IMPLEMENTATION_SHA256': '0' * 64}, script=self.verify_script)
        self._check('verify-execution-id-format', None, 'execution_id has the format DRnnnn',
                    env={**self.verify_env, 'GATE_EXECUTION_ID': 'DV0001'}, script=self.verify_script)

    def test_real_worktree_fails_closed(self):
        """The repository before the START: the campaign is NOT_STARTED and no START row, dispatch authorization, or verified instance exists, so the gate must refuse."""
        code, out, _ = run_gate(self.measured_script, REPO_ROOT, self.measured_env)
        self.results.append(('real-worktree (fail-closed today)', code))
        self.assertNotEqual(code, 0, out)
        for expected in ('E02 campaign status is IN_PROGRESS', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED',
                         'exactly one E02 dispatch authorization record names this dispatch id'):
            self.assertIn(expected, out)
        self.assertNotIn('Traceback', out)

    def test_guard_steps_refuse_what_they_must(self):
        guard = extract(MEASURED, 'gate', step_name='Refuse a GitHub-native re-run, a malformed attempt, and a dispatch off the default branch')['run']
        verify_guard = extract(VERIFY, 'gate', step_name='Refuse anything but a DRY_RUN on the default branch')['run']
        cases = [
            (guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_INPUT_ATTEMPT': '1'}, 0),
            (guard, {'GUARD_REF': 'refs/heads/feature', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_INPUT_ATTEMPT': '1'}, 1),
            (guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '2', 'GUARD_INPUT_ATTEMPT': '1'}, 1),
            (guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_INPUT_ATTEMPT': '2'}, 0),
            (guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_INPUT_ATTEMPT': '0'}, 1),
            (guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_INPUT_ATTEMPT': 'x'}, 1),
            (guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_INPUT_ATTEMPT': ''}, 1),
            (guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '2', 'GUARD_INPUT_ATTEMPT': '2'}, 1),
            (verify_guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_DRY_RUN': 'true'}, 0),
            (verify_guard, {'GUARD_REF': 'refs/heads/main', 'GUARD_RUN_ATTEMPT': '1', 'GUARD_DRY_RUN': 'false'}, 1),
        ]
        for script, env_values, expected in cases:
            with self.subTest(env=env_values, expected=expected):
                proc = subprocess.run(['bash', '-c', script], env={**os.environ, **env_values}, capture_output=True, text=True)
                self.results.append((f'guard {env_values}', proc.returncode))
                self.assertEqual(proc.returncode != 0, expected != 0, proc.stdout + proc.stderr)

    @classmethod
    def tearDownClass(cls):
        passed = sum(1 for _, c in cls.results if c == 0)
        print(f'\ngate matrix: {len(cls.results)} runs recorded; exit 0 in {passed}; exit non-zero in {len(cls.results) - passed}')


if __name__ == '__main__':
    unittest.main()
