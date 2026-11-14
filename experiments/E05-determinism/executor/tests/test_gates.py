"""The gates of the two E05 workflows, executed on fake trees (tests/test_gates.py).

DRAFT (operation OP-PREP-E05). Each gate script is extracted from its workflow file (the python heredoc of the step with id "gates" of the
measured or verification gate job, and the heredoc of the job "plan" for the matrix), written to a temporary file, and run with the working
directory set to a fake tree and the GATE_* inputs set in its environment. The must-pass trees are complete and fictitious (TEST-FIXTURE
identifiers, not issued authorizations); every must-fail case changes exactly one thing and must fail on the gate it names. The "as-is"
cases run against the files of this repository as they are and must fail closed, because E05 has no START, no locked configuration, no
dispatch authorization, no controlled instance, and no frozen or working prompt.

The gate scripts import PyYAML, which this environment lacks. When a subprocess cannot import yaml, the tests place a stand-in module
next to the script: it parses JSON directly and any other text through the Ruby YAML library, so that the gates read the repository's
own YAML files. The fixtures are JSON (which is YAML), so they read the same way with PyYAML. The gate tests are skipped only when ruby is
absent and PyYAML is missing.
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
MEASURED = os.path.join(REPO, '.github', 'workflows', 'e05-measured-execution.yml')
VERIFY = os.path.join(REPO, '.github', 'workflows', 'e05-environment-verification.yml')
CONDITIONS = os.path.join(REPO, 'experiments', 'E05-determinism', 'conditions-draft.json')

CAMPAIGN = 'E05-determinism'
README = 'experiments/E05-determinism/README.md'
STUDY = 'manifests/study-manifest.yaml'
CHANGELOG = 'protocol/CHANGELOG.md'
START_RECORD = 'manifests/e05-campaign-start-v1.yaml'
CONTROLLED = 'experiments/E05-determinism/controlled-instance-status.yaml'
IMPL = 'experiments/E05-determinism/executor/run-condition.sh'
GOV = 'protocol/agent-governance-v6.md'
SCHEMA = 'schemas/run-manifest.schema.v2.json'
MAPPING = 'experiments/scenario-mappings/CS-001.yaml'
SUT_MANIFEST = 'manifests/sut-manifest.yaml'
CONDITIONS_REL = 'experiments/E05-determinism/conditions-draft.json'
SUT_TAGS = {'SUT-01': 'sut01', 'SUT-02': 'sut02', 'SUT-04': 'sut04', 'SUT-05': 'sut05'}

AUTH_START = 'TEST-FIXTURE-E05-START'
AUTH_DISPATCH = 'TEST-FIXTURE-E05-DISPATCH'
PV = 'TEST-FIXTURE-PROMPT-v1'
PROMPT_TEXT = b'DRAFT fixture prompt text for the E05 gate tests only.\n'
IMPL_TEXT = b'DRAFT fixture implementation text for the E05 gate tests only.\n'
PROMPT_SHA = hashlib.sha256(PROMPT_TEXT).hexdigest()
IMPL_SHA = hashlib.sha256(IMPL_TEXT).hexdigest()
SUT01_COMMIT = '9ca37674d374e9303912e259641ee86baf3aabe1'
SUT05_COMMIT = '1618a611b173b4bf114028e6e02549950606e29d'
SUT05_RELEASE = 'v20.2.0'
GOV_TEXT = '| Protocol state | FROZEN-PRE-DATA |\n\n### 3.7 Dispatch authorization for E02 and E04-E12 (fixture)\n'
COND_SUT01 = 'E05-SUT01-API-02'
COND_SUT05 = 'E05-SUT05-API-01'

with open(CONDITIONS, 'rb') as _f:
    CONDITIONS_BYTES = _f.read()
COND_FILE_SHA = hashlib.sha256(CONDITIONS_BYTES).hexdigest()
WORKFLOW_REL = '.github/workflows/e05-measured-execution.yml'
with open(MEASURED, 'rb') as _f:
    MEASURED_BYTES = _f.read()
MEASURED_SHA = hashlib.sha256(MEASURED_BYTES).hexdigest()
CONDITIONS_DOC = json.loads(CONDITIONS_BYTES.decode('utf-8'))
SURFACE_OF = {c['condition_id']: c['surface'] for c in CONDITIONS_DOC['conditions']}
SUT_OF = {c['condition_id']: c['sut_id'] for c in CONDITIONS_DOC['conditions']}

YAML_SHIM = '''"""Stand-in for PyYAML, written next to a gate script by the E05 gate tests only when PyYAML is not importable.

safe_load parses JSON directly; any other text is parsed by the Ruby YAML library (Psych) and returned as JSON-compatible data.
"""
import json
import subprocess


class YAMLError(Exception):
    pass


def safe_load(stream):
    text = stream.read() if hasattr(stream, 'read') else stream
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except ValueError:
        pass
    proc = subprocess.run(['ruby', '-ryaml', '-rjson', '-e', 'print JSON.generate([YAML.load(STDIN.read)])'],
                          input=text, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise YAMLError(proc.stderr.strip())
    return json.loads(proc.stdout)[0]


def safe_dump(data, **_kwargs):
    return json.dumps(data, indent=2)
'''


def _pyyaml_importable():
    proc = subprocess.run([sys.executable, '-c', 'import yaml'], capture_output=True, text=True, timeout=60)
    return proc.returncode == 0


YAML_SHIM_NEEDED = not _pyyaml_importable()


def load_workflow(path):
    if shutil.which('ruby') is None:
        raise unittest.SkipTest('ruby is needed to parse the workflow YAML (no PyYAML in this environment)')
    script = 'require "yaml"; require "json"; print JSON.generate(YAML.load(File.read(ARGV[0], encoding: "UTF-8")))'
    proc = subprocess.run(['ruby', '-ryaml', '-rjson', '-e', script, path], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise AssertionError(f'{path} does not parse as YAML: {proc.stderr.strip()}')
    return json.loads(proc.stdout)


def extract_heredoc(workflow, job, step_id):
    """The python script of the step with the given id: the lines between "python3 - <<'PY'" and the next "PY" line."""
    wf = load_workflow(workflow)
    run = next(s['run'] for s in wf['jobs'][job]['steps'] if s.get('id') == step_id)
    lines = run.split('\n')
    start = lines.index("python3 - <<'PY'")
    end = lines.index('PY', start)
    return '\n'.join(lines[start + 1:end]) + '\n'


def sut_manifest_fixture():
    return {'suts': {
        'SUT-01': {'components': {'web': {'commit_sha': SUT01_COMMIT, 'release': None},
                                  'api': {'commit_sha': SUT01_COMMIT, 'release': None}}},
        'SUT-02': {'components': {'web': {'commit_sha': '60fdd634bb111c092282fa07977513a0a7765593', 'release': None},
                                  'api': {'commit_sha': None, 'release': None}}},
        'SUT-04': {'components': {'web': {'commit_sha': 'd36bd3f8647a091d406e53bad463c5e3e5d2ece1', 'release': '2.2'},
                                  'api': {'commit_sha': 'd36bd3f8647a091d406e53bad463c5e3e5d2ece1', 'release': '2.2'}}},
        'SUT-05': {'components': {'api': {'commit_sha': SUT05_COMMIT, 'release': SUT05_RELEASE}}}}}


def readme_fixture(cond, sut):
    commits = {'SUT-01': [SUT01_COMMIT], 'SUT-05': [SUT05_COMMIT, SUT05_RELEASE]}[sut]
    return ('# E05 fixture README\n\n## Campaign configuration\n\n'
            f'- Condition: {cond}\n- SUT: {sut}\n- Schema: schemas/run-manifest.schema.v2.json\n- Executor prompt: {PV}\n'
            f'- Executor implementation SHA-256: {IMPL_SHA}\n- Conditions file SHA-256: {COND_FILE_SHA}\n'
            f'- Workflow file SHA-256: {MEASURED_SHA}\n'
            '- Sample size: N = 50 executions per condition\n- Target scenario: CS-001\n- Hypothesis: H3 (fixture)\n'
            + ''.join(f'- Pinned commit: {c}\n' for c in commits) + '\n## Next\n')


def dispatch_fixture(cond, sut):
    return {'authorization_id': AUTH_DISPATCH, 'record_class': 'E05_DISPATCH_AUTHORIZATION', 'status': 'ISSUED',
            'record_validity': 'VALID', 'dispatch_eligibility': 'ELIGIBLE', 'revoked': False, 'issued_by': 'human research lead',
            'authorization_date': 'FIXTURE-DATE', 'assigned_sut': sut, 'conditions': [cond], 'n_executions': 50, 'attempt': 1,
            'campaign_start_authorization_id': AUTH_START,
            'frozen_inputs': {'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': PROMPT_SHA}}


def controlled_fixture(cond):
    return {'conditions': {cond: {'status': 'CONTROLLED',
                                  'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'},
                                  'reverification_required': False}}}


def measured_inputs(cond, sut):
    return {'GATE_CONDITION_ID': cond, 'GATE_ASSIGNED_SUT': sut, 'GATE_CAMPAIGN_START_AUTHORIZATION_ID': AUTH_START,
            'GATE_DISPATCH_AUTHORIZATION_ID': AUTH_DISPATCH, 'GATE_EXECUTOR_PROMPT_VERSION': PV,
            'GATE_EXECUTOR_IMPLEMENTATION_SHA256': IMPL_SHA}


def measured_state(cond=COND_SUT01):
    """The must-pass state of the measured-execution gate: every gate satisfied by fictitious fixture content."""
    sut = SUT_OF[cond]
    files = {
        STUDY: json.dumps({'campaigns': [{'id': CAMPAIGN, 'status': 'IN_PROGRESS'}]}),
        CHANGELOG: f'| FIXTURE | experiments/E05-determinism/README.md | campaign NOT_STARTED -> IN_PROGRESS | {AUTH_START} |\n',
        START_RECORD: json.dumps({'record_class': 'CAMPAIGN_START', 'campaign_id': CAMPAIGN, 'authorization_id': AUTH_START}),
        README: readme_fixture(cond, sut),
        CONDITIONS_REL: CONDITIONS_BYTES.decode('utf-8'),
        SUT_MANIFEST: json.dumps(sut_manifest_fixture()),
        GOV: GOV_TEXT,
        f'manifests/e05-dispatch-authorization-{SUT_TAGS[sut]}-v1.yaml': json.dumps(dispatch_fixture(cond, sut)),
        CONTROLLED: json.dumps(controlled_fixture(cond)),
        MAPPING: json.dumps({'mapping_status': 'FROZEN', 'mappings': [{'sut_id': sut}]}),
        SCHEMA: json.dumps({'$id': 'urn:eus-2026-001:schemas:run-manifest:v2'}),
        f'prompts/frozen/{PV}.md': PROMPT_TEXT.decode('utf-8'),
        IMPL: IMPL_TEXT.decode('utf-8'),
        WORKFLOW_REL: MEASURED_BYTES.decode('utf-8'),
    }
    return {'files': files, 'inputs': measured_inputs(cond, sut)}


def verify_state(cond=COND_SUT01):
    """The must-pass state of the verification gate (the working prompt copy exists; no frozen copy yet)."""
    files = {
        CONDITIONS_REL: CONDITIONS_BYTES.decode('utf-8'),
        f'prompts/working/{PV}.md': PROMPT_TEXT.decode('utf-8'),
        IMPL: IMPL_TEXT.decode('utf-8'),
        GOV: GOV_TEXT,
        SCHEMA: json.dumps({'$id': 'urn:eus-2026-001:schemas:run-manifest:v2'}),
    }
    inputs = {'GATE_TARGET': cond, 'GATE_EXECUTIONS': '2', 'GATE_EXECUTOR_PROMPT_VERSION': PV,
              'GATE_EXECUTOR_IMPLEMENTATION_SHA256': IMPL_SHA}
    return {'files': files, 'inputs': inputs}


def run_script(state, script_text, tree_root, work_dir):
    """Materialize the state in a fake tree, run the script with the tree as its working directory, return (status, output)."""
    if os.path.isdir(tree_root):
        shutil.rmtree(tree_root)
    for rel, content in state['files'].items():
        path = os.path.join(tree_root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    script = os.path.join(work_dir, os.path.basename(tree_root) + '-gate.py')
    with open(script, 'w', encoding='utf-8') as f:
        f.write(script_text)
    if YAML_SHIM_NEEDED:
        with open(os.path.join(work_dir, 'yaml.py'), 'w', encoding='utf-8') as f:
            f.write(YAML_SHIM)
    out_file = os.path.join(work_dir, os.path.basename(tree_root) + '-github-output.txt')
    env = {k: v for k, v in os.environ.items() if not k.startswith('GATE_') and k != 'PYTHONPATH'}
    env.update(state['inputs'])
    env['GITHUB_OUTPUT'] = out_file
    proc = subprocess.run([sys.executable, script], cwd=tree_root, env=env, capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


@unittest.skipIf(shutil.which('ruby') is None and not _pyyaml_importable(), 'the gates need PyYAML or ruby (stand-in)')
class MeasuredGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = extract_heredoc(MEASURED, 'gate', 'gates')
        cls.work = tempfile.mkdtemp(prefix='e05-measured-gate-')

    def assertPasses(self, state, label):
        code, out = run_script(state, self.script, os.path.join(self.work, label), self.work)
        self.assertEqual(code, 0, out)
        self.assertIn('ALL GATES PASSED', out)

    def assertFailsOn(self, state, label, fragment):
        code, out = run_script(state, self.script, os.path.join(self.work, label), self.work)
        self.assertNotEqual(code, 0, f'{label} unexpectedly passed:\n{out}')
        fails = [l for l in out.splitlines() if l.startswith('FAIL ')]
        self.assertTrue(any(fragment in l for l in fails), f'{label}: no FAIL line names {fragment!r}\n{out}')

    def test_must_pass_sut01_api_condition(self):
        self.assertPasses(measured_state(COND_SUT01), 'pass-sut01')

    def test_must_pass_sut05_api_condition_needs_the_release_in_the_configuration(self):
        self.assertPasses(measured_state(COND_SUT05), 'pass-sut05')

    def mutate(self, label, fragment, change, cond=COND_SUT01):
        state = measured_state(cond)
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

        def dispatch(key, value, cond=COND_SUT01):
            def f(s):
                path = f'manifests/e05-dispatch-authorization-{SUT_TAGS[SUT_OF[cond]]}-v1.yaml'
                d = json.loads(s['files'][path])
                if key == 'frozen_inputs.impl':
                    d['frozen_inputs']['executor_implementation_sha256'] = value
                elif key == 'frozen_inputs.prompt':
                    d['frozen_inputs']['executor_prompt_sha256'] = value
                else:
                    d[key] = value
                s['files'][path] = json.dumps(d)
            return f

        def controlled(key, value, cond=COND_SUT01):
            def f(s):
                d = json.loads(s['files'][CONTROLLED])
                entry = d['conditions'][cond]
                if key == 'verification':
                    entry['github_actions_verification']['status'] = value
                elif key == 'environment_type':
                    entry['github_actions_verification']['environment_type'] = value
                else:
                    entry[key] = value
                s['files'][CONTROLLED] = json.dumps(d)
            return f

        def mapping(key, value):
            def f(s):
                d = json.loads(s['files'][MAPPING])
                if key == 'sut':
                    d['mappings'] = [{'sut_id': 'SUT-02'}]
                else:
                    d[key] = value
                s['files'][MAPPING] = json.dumps(d)
            return f

        def conditions_surface(cond, surface):
            def f(s):
                doc = json.loads(s['files'][CONDITIONS_REL])
                for c in doc['conditions']:
                    if c['condition_id'] == cond:
                        c['surface'] = surface
                s['files'][CONDITIONS_REL] = json.dumps(doc)
            return f

        def sut_manifest_without_commit(sut):
            def f(s):
                d = json.loads(s['files'][SUT_MANIFEST])
                for comp in d['suts'][sut]['components'].values():
                    comp['commit_sha'] = None
                s['files'][SUT_MANIFEST] = json.dumps(d)
            return f

        def start_rows(text):
            return lambda s: s['files'].__setitem__(CHANGELOG, text)

        cases = [
            ('campaign-not-started', 'E05 campaign status IN_PROGRESS',
             put(STUDY, json.dumps({'campaigns': [{'id': CAMPAIGN, 'status': 'NOT_STARTED'}]}))),
            ('no-start-row', 'exactly one E05 campaign START change-log row', rm(CHANGELOG)),
            ('start-row-without-auth-id', 'the START row carries the campaign START authorization id',
             start_rows('| FIXTURE | experiments/E05-determinism/README.md | campaign NOT_STARTED -> IN_PROGRESS |\n')),
            ('two-start-rows', 'exactly one E05 campaign START change-log row',
             lambda s: s['files'].__setitem__(CHANGELOG, s['files'][CHANGELOG] * 2)),
            ('start-record-absent', 'START record exists and names the campaign', rm(START_RECORD)),
            ('start-record-other-authorization', 'START record exists and names the campaign',
             put(START_RECORD, json.dumps({'record_class': 'CAMPAIGN_START', 'campaign_id': CAMPAIGN, 'authorization_id': 'OTHER'}))),
            ('no-configuration-section', 'locked "Campaign configuration" record exists', put(README, '# no configuration\n')),
            ('configuration-without-n50', 'configuration names N = 50 executions', edit(README, 'N = 50', 'N = 30')),
            ('configuration-without-impl-hash', 'configuration names the executor implementation hash', edit(README, IMPL_SHA, 'x')),
            ('configuration-without-conditions-hash', 'configuration names the sha256 of the conditions file', edit(README, COND_FILE_SHA, 'x')),
            ('configuration-without-workflow-sha', 'configuration names the sha256 of the measured workflow file',
             edit(README, MEASURED_SHA, 'x')),
            ('configuration-without-h3', 'configuration names the H3 hypothesis label', edit(README, 'H3', 'H4')),
            ('configuration-without-cs001', 'configuration names the target scenario CS-001', edit(README, 'CS-001', 'CS-002')),
            ('configuration-without-commit', 'configuration names the pinned commit of every E05 surface component',
             edit(README, SUT01_COMMIT, 'x')),
            ('governance-draft', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', put(GOV, '| Protocol state | DRAFT |\n\n### 3.7 Dispatch authorization\n')),
            ('governance-missing', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', rm(GOV)),
            ('governance-without-section-3-7', 'agent-governance-v6 names the per-SUT dispatch authorization of Section 3.7',
             put(GOV, '| Protocol state | FROZEN-PRE-DATA |\n')),
            ('dispatch-authorization-absent', 'exactly one dispatch authorization record of the assigned SUT',
             rm(f'manifests/e05-dispatch-authorization-sut01-v1.yaml')),
            ('dispatch-authorization-pending', 'dispatch authorization is ISSUED, VALID', dispatch('status', 'PENDING')),
            ('dispatch-not-eligible', 'dispatch authorization is ISSUED, VALID', dispatch('dispatch_eligibility', 'NOT_ELIGIBLE')),
            ('dispatch-revoked', 'dispatch authorization is ISSUED, VALID', dispatch('revoked', True)),
            ('dispatch-issued-by-agent', 'issued by the human research lead', dispatch('issued_by', 'ORCHESTRATOR')),
            ('dispatch-sut-mismatch', 'dispatch authorization names the assigned SUT', dispatch('assigned_sut', 'SUT-05')),
            ('dispatch-condition-missing', 'dispatch authorization names this condition', dispatch('conditions', ['E05-SUT01-API-01'])),
            ('dispatch-n-30', 'dispatch authorization names N = 50 executions per condition', dispatch('n_executions', 30)),
            ('dispatch-attempt-two', 'dispatch authorization records attempt 1', dispatch('attempt', 2)),
            ('dispatch-without-date', 'dispatch authorization records attempt 1 and an authorization date', dispatch('authorization_date', None)),
            ('dispatch-start-id-mismatch', 'dispatch authorization names the campaign START authorization id', dispatch('campaign_start_authorization_id', 'OTHER')),
            ('dispatch-impl-hash-mismatch', 'records the executor implementation SHA-256 equal to the input', dispatch('frozen_inputs.impl', '0' * 64)),
            ('dispatch-prompt-hash-mismatch', 'records the executor prompt SHA-256 equal to the frozen prompt file', dispatch('frozen_inputs.prompt', '0' * 64)),
            ('prompt-file-missing', 'executor prompt frozen file exists', rm(f'prompts/frozen/{PV}.md')),
            ('controlled-instance-candidate', 'controlled instance status CONTROLLED', controlled('status', 'CANDIDATE')),
            ('github-verification-not-verified', 'GitHub Actions environment verification VERIFIED', controlled('verification', 'NOT_VERIFIED')),
            ('reverification-required', 'no provisioning change awaiting re-verification', controlled('reverification_required', True)),
            ('public-hosted-target', 'environment_type SELF_HOSTED', controlled('environment_type', 'PUBLIC_HOSTED')),
            ('mapping-draft', 'CS-001 mapping FROZEN', mapping('mapping_status', 'DRAFT')),
            ('mapping-without-the-assigned-sut', 'CS-001 names a mapping entry for the assigned SUT', mapping('sut', None)),
            ('schema-id-wrong', 'run-manifest schema v2 present with the v2 id', put(SCHEMA, '{"$id": "urn:other"}')),
            ('implementation-hash-differs', 'executor implementation exists and equals the locked hash', put(IMPL, 'changed\n')),
            ('condition-not-in-file', 'condition is one of the fourteen E05 conditions', inp('GATE_CONDITION_ID', 'E05-OTHER-API-01')),
            ('condition-wrong-sut', 'condition belongs to the assigned SUT', inp('GATE_ASSIGNED_SUT', 'SUT-05')),
            ('condition-mobile-surface', 'condition is a web or api condition', conditions_surface(COND_SUT01, 'android')),
            ('sut-manifest-without-commit', 'SUT has pinned commits for the E05 surface components', sut_manifest_without_commit('SUT-01')),
            ('campaign-start-id-absent', 'campaign START authorization id is present', inp('GATE_CAMPAIGN_START_AUTHORIZATION_ID', '')),
            ('implementation-hash-malformed', 'executor implementation hash is a SHA-256 value', inp('GATE_EXECUTOR_IMPLEMENTATION_SHA256', 'abc')),
            ('prompt-id-malformed', 'executor prompt version is a plain identifier', inp('GATE_EXECUTOR_PROMPT_VERSION', '../x')),
        ]
        for label, fragment, change in cases:
            with self.subTest(case=label):
                self.mutate(label, fragment, change)

    def test_sut05_release_missing_from_the_configuration_fails(self):
        self.mutate('sut05-release-absent', 'configuration names the pinned release of the assigned SUT',
                    lambda s: s['files'].__setitem__(README, s['files'][README].replace(SUT05_RELEASE, 'x')), cond=COND_SUT05)

    def test_as_is_repository_state_fails_closed(self):
        """The files of this repository as they are now (copied where present) must not pass the gate."""
        files = {}
        for rel in (STUDY, CHANGELOG, GOV, README, CONDITIONS_REL, SUT_MANIFEST, MAPPING, SCHEMA, IMPL, WORKFLOW_REL):
            path = os.path.join(REPO, rel)
            if os.path.isfile(path):
                with open(path, encoding='utf-8') as f:
                    files[rel] = f.read()
        code, out = run_script({'files': files, 'inputs': measured_inputs(COND_SUT01, 'SUT-01')}, self.script,
                               os.path.join(self.work, 'as-is'), self.work)
        self.assertNotEqual(code, 0, out)
        for fragment in ('E05 campaign status IN_PROGRESS', 'exactly one E05 campaign START change-log row',
                         'locked "Campaign configuration" record exists',
                         'exactly one dispatch authorization record of the assigned SUT', 'controlled instance status CONTROLLED',
                         'executor prompt frozen file exists'):
            self.assertIn(fragment, out)


@unittest.skipIf(shutil.which('ruby') is None and not _pyyaml_importable(), 'the gates need PyYAML or ruby (stand-in)')
class VerificationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = extract_heredoc(VERIFY, 'gate', 'gates')
        cls.work = tempfile.mkdtemp(prefix='e05-verify-gate-')

    def test_must_pass_with_the_working_prompt_copy(self):
        code, out = run_script(verify_state(), self.script, os.path.join(self.work, 'pass'), self.work)
        self.assertEqual(code, 0, out)
        self.assertIn('ALL GATES PASSED', out)

    def test_must_fail_matrix(self):
        def inp(key, value):
            return lambda s: s['inputs'].__setitem__(key, value)

        cases = [
            ('executions-fifty', 'executions is 2 or 3', inp('GATE_EXECUTIONS', '50')),
            ('target-unknown', 'target is all or one condition of the conditions file', inp('GATE_TARGET', 'E05-NOPE-API-01')),
            ('impl-hash-differs', 'executor implementation hash equals the input', inp('GATE_EXECUTOR_IMPLEMENTATION_SHA256', '0' * 64)),
            ('prompt-id-malformed', 'executor prompt version is a plain identifier', inp('GATE_EXECUTOR_PROMPT_VERSION', '../x')),
            ('working-prompt-absent', 'executor prompt working copy exists', lambda s: s['files'].pop(f'prompts/working/{PV}.md')),
        ]
        for label, fragment, change in cases:
            with self.subTest(case=label):
                state = verify_state()
                change(state)
                code, out = run_script(state, self.script, os.path.join(self.work, label), self.work)
                self.assertNotEqual(code, 0, out)
                self.assertTrue(any(fragment in l for l in out.splitlines() if l.startswith('FAIL ')), out)

    def test_as_is_repository_state_fails_closed_for_want_of_a_working_prompt(self):
        files = {}
        for rel in (CONDITIONS_REL, GOV, SCHEMA, IMPL):
            with open(os.path.join(REPO, rel), encoding='utf-8') as f:
                files[rel] = f.read()
        state = {'files': files, 'inputs': verify_state()['inputs']}
        code, out = run_script(state, self.script, os.path.join(self.work, 'as-is'), self.work)
        self.assertNotEqual(code, 0, out)
        self.assertIn('executor prompt working copy exists', out)


@unittest.skipIf(shutil.which('ruby') is None, 'ruby is needed to read the workflow plan step')
class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = extract_heredoc(VERIFY, 'plan', 'plan')
        cls.work = tempfile.mkdtemp(prefix='e05-plan-')

    def plan(self, target):
        out_file = os.path.join(self.work, target + '-output.txt')
        if os.path.exists(out_file):
            os.remove(out_file)
        script = os.path.join(self.work, target + '-plan.py')
        with open(script, 'w', encoding='utf-8') as f:
            f.write(self.script)
        env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
        env.update({'PLAN_TARGET': target, 'GITHUB_OUTPUT': out_file})
        proc = subprocess.run([sys.executable, script], cwd=REPO, env=env, capture_output=True, text=True, timeout=120)
        matrix = None
        if os.path.isfile(out_file):
            with open(out_file, encoding='utf-8') as f:
                for line in f:
                    if line.startswith('matrix='):
                        matrix = json.loads(line[len('matrix='):])
        return proc.returncode, proc.stdout + proc.stderr, matrix

    def test_all_builds_the_fourteen_conditions_with_their_suts(self):
        code, out, matrix = self.plan('all')
        self.assertEqual(code, 0, out)
        self.assertEqual(len(matrix['include']), 14)
        for item in matrix['include']:
            self.assertEqual(item['sut_id'], SUT_OF[item['condition_id']])

    def test_one_condition_builds_one_job(self):
        code, out, matrix = self.plan(COND_SUT05)
        self.assertEqual(code, 0, out)
        self.assertEqual(matrix['include'], [{'condition_id': COND_SUT05, 'sut_id': 'SUT-05'}])

    def test_an_unknown_target_fails_closed(self):
        code, out, matrix = self.plan('E05-NOPE-API-01')
        self.assertNotEqual(code, 0)
        self.assertIsNone(matrix)
        self.assertIn('unknown target', out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
