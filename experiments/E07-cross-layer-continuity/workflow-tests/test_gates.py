"""The gates of the two E07 workflows, executed on fake trees (workflow-tests/test_gates.py).

DRAFT (operation OP-PREP-E07-05). Each gate script is extracted from its workflow file (the python heredoc of the step with id "gates" of the
measured or verification gate job, and the heredoc of the job "plan" for the matrix), written to a temporary file, and run with the working
directory set to a fake tree and the GATE_* inputs set in its environment. The must-pass trees are complete and fictitious (TEST-FIXTURE
identifiers, not issued authorizations); every must-fail case changes exactly one thing and must fail on the gate it names. The "as-is"
cases run against the files of this repository as they are and must fail closed, because E07 is NOT_STARTED: it has no START, no locked
configuration, no dispatch authorization, no verified controlled instance, no FROZEN scenario record and no frozen prompt.

The gate scripts import PyYAML, which this environment may lack. When a subprocess cannot import yaml, the tests place a stand-in module
next to the script: it parses JSON directly and any other text through the Ruby YAML library, so that the gates read the repository's
own YAML files. The fixtures are JSON (which is YAML), so they read the same way with PyYAML. The gate tests are skipped only when ruby is
absent and PyYAML is missing. The tests need no executor: the executor file is a fixture text in the fake trees; only the as-is test of the
verification gate reads the real one and is skipped while it is absent.
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
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MEASURED = os.path.join(REPO, '.github', 'workflows', 'e07-measured-execution.yml')
VERIFY = os.path.join(REPO, '.github', 'workflows', 'e07-environment-verification.yml')
CONDITIONS = os.path.join(REPO, 'experiments', 'E07-cross-layer-continuity', 'conditions-draft.json')

CAMPAIGN = 'E07-cross-layer-continuity'
README = 'experiments/E07-cross-layer-continuity/README.md'
STUDY = 'manifests/study-manifest.yaml'
CHANGELOG = 'protocol/CHANGELOG.md'
START_RECORD = 'manifests/e07-campaign-start-v1.yaml'
CONTROLLED = 'experiments/E07-cross-layer-continuity/controlled-instance-status.yaml'
IMPL = 'experiments/E07-cross-layer-continuity/executor/run-condition.sh'
GOV = 'protocol/agent-governance-v6.md'
SCHEMA = 'schemas/run-manifest.schema.v2.json'
MAPPINGS = {'CS-005': 'experiments/scenario-mappings/CS-005.yaml', 'CS-006': 'experiments/scenario-mappings/CS-006.yaml'}
SUT_MANIFEST = 'manifests/sut-manifest.yaml'
CONDITIONS_REL = 'experiments/E07-cross-layer-continuity/conditions-draft.json'
SUT_TAGS = {'SUT-01': 'sut01', 'SUT-04': 'sut04'}

AUTH_START = 'TEST-FIXTURE-E07-START'
AUTH_DISPATCH = 'TEST-FIXTURE-E07-DISPATCH'
PV = 'TEST-FIXTURE-PROMPT-v1'
REAL_PROMPT = 'ORCHESTRATOR-E07-cross-layer-continuity-v1'  # the working copy of the dispatch prompt (frozen at the campaign START)
PROMPT_TEXT = b'DRAFT fixture prompt text for the E07 gate tests only.\n'
IMPL_TEXT = b'DRAFT fixture implementation text for the E07 gate tests only.\n'
PROMPT_SHA = hashlib.sha256(PROMPT_TEXT).hexdigest()
IMPL_SHA = hashlib.sha256(IMPL_TEXT).hexdigest()
SUT01_COMMIT = '9ca37674d374e9303912e259641ee86baf3aabe1'
SUT04_COMMIT = 'd36bd3f8647a091d406e53bad463c5e3e5d2ece1'
SUT04_RELEASE = '2.2'
GOV_TEXT = '| Protocol state | FROZEN-PRE-DATA |\n\n### 3.7 Dispatch authorization for E02 and E04-E12 (fixture)\n'
COND_A = 'E07-CS005-SUT01-API-WEB'   # SUT-01, CS-005, api to web
COND_B = 'E07-CS006-SUT04-WEB-API'   # SUT-04, CS-006, web to api

with open(CONDITIONS, 'rb') as _f:
    CONDITIONS_BYTES = _f.read()
COND_FILE_SHA = hashlib.sha256(CONDITIONS_BYTES).hexdigest()
WORKFLOW_REL = '.github/workflows/e07-measured-execution.yml'
with open(MEASURED, 'rb') as _f:
    MEASURED_BYTES = _f.read()
MEASURED_SHA = hashlib.sha256(MEASURED_BYTES).hexdigest()
CONDITIONS_DOC = json.loads(CONDITIONS_BYTES.decode('utf-8'))
SUT_OF = {c['condition_id']: c['sut_id'] for c in CONDITIONS_DOC['conditions']}
SCENARIO_OF = {c['condition_id']: c['canonical_scenario_id'] for c in CONDITIONS_DOC['conditions']}

YAML_SHIM = '''"""Stand-in for PyYAML, written next to a gate script by the E07 gate tests only when PyYAML is not importable.

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
        'SUT-04': {'components': {'web': {'commit_sha': SUT04_COMMIT, 'release': SUT04_RELEASE},
                                  'api': {'commit_sha': SUT04_COMMIT, 'release': SUT04_RELEASE}}}}}


def readme_fixture(cond, sut):
    commits = {'SUT-01': [SUT01_COMMIT], 'SUT-04': [SUT04_COMMIT, SUT04_RELEASE]}[sut]
    return ('# E07 fixture README\n\n## Campaign configuration\n\n'
            f'- Condition: {cond}\n- SUT: {sut}\n- Schema: schemas/run-manifest.schema.v2.json\n- Executor prompt: {PV}\n'
            f'- Executor implementation SHA-256: {IMPL_SHA}\n- Conditions file SHA-256: {COND_FILE_SHA}\n'
            f'- Workflow file SHA-256: {MEASURED_SHA}\n'
            '- Sample size: N = 50 executions per condition\n'
            f'- Canonical scenarios: CS-005 (API to WEB) and CS-006 (WEB to API); the scenario of this condition: {SCENARIO_OF[cond]}\n'
            '- Primary metric: continuity success proportion (fixture)\n'
            + ''.join(f'- Pinned commit: {c}\n' for c in commits) + '\n## Next\n')


def dispatch_fixture(cond, sut):
    return {'authorization_id': AUTH_DISPATCH, 'record_class': 'E07_DISPATCH_AUTHORIZATION', 'status': 'ISSUED',
            'record_validity': 'VALID', 'dispatch_eligibility': 'ELIGIBLE', 'revoked': False, 'issued_by': 'human research lead',
            'authorization_date': 'FIXTURE-DATE', 'assigned_sut': sut, 'conditions': [cond], 'n_executions': 50, 'attempt': 1,
            'campaign_start_authorization_id': AUTH_START,
            'frozen_inputs': {'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_sha256': PROMPT_SHA}}


def controlled_fixture(cond):
    return {'conditions': {cond: {'status': 'CONTROLLED',
                                  'github_actions_verification': {'status': 'VERIFIED', 'environment_type': 'SELF_HOSTED'},
                                  'reverification_required': False}}}


def mapping_fixtures(cond, sut):
    """Both scenario records FROZEN; the entry of the assigned SUT is COMPARABLE in the scenario of the condition and NOT_COMPARABLE in the other
    direction (an open cell of one direction does not block the other direction)."""
    scn = SCENARIO_OF[cond]
    other = 'CS-006' if scn == 'CS-005' else 'CS-005'
    return {MAPPINGS[scn]: json.dumps({'canonical_scenario_id': scn, 'mapping_status': 'FROZEN', 'mappings': [{'sut_id': sut, 'comparability': 'COMPARABLE'}]}),
            MAPPINGS[other]: json.dumps({'canonical_scenario_id': other, 'mapping_status': 'FROZEN', 'mappings': [{'sut_id': sut, 'comparability': 'NOT_COMPARABLE'}]})}


def measured_inputs(cond, sut):
    return {'GATE_CONDITION_ID': cond, 'GATE_ASSIGNED_SUT': sut, 'GATE_CAMPAIGN_START_AUTHORIZATION_ID': AUTH_START,
            'GATE_DISPATCH_AUTHORIZATION_ID': AUTH_DISPATCH, 'GATE_EXECUTOR_PROMPT_VERSION': PV,
            'GATE_EXECUTOR_IMPLEMENTATION_SHA256': IMPL_SHA, 'GATE_ATTEMPT': '1', 'GATE_FIRST_EXECUTION': '1'}


def further_fixture(cond, sut, attempt=2, first=7):
    return {'record_class': 'E07_FURTHER_ATTEMPT_APPROVAL', 'status': 'ISSUED', 'revoked': False, 'assigned_sut': sut,
            'issued_by': 'human research lead', 'dispatch_authorization_id': AUTH_DISPATCH, 'campaign_start_authorization_id': AUTH_START,
            'executor_implementation_sha256': IMPL_SHA, 'executor_prompt_version': PV, 'executor_prompt_sha256': PROMPT_SHA,
            'governing_protocol': 'protocol/agent-governance-v6.md, Sections 3.6 and 3.7 (Further attempts)',
            'attempts': [{'condition_id': cond, 'first_execution': first, 'attempt': attempt, 'previous_attempt': attempt - 1}]}


def further_state(cond=COND_A, attempt=2, first=7):
    """The must-pass state of a further attempt: attempt 2 from execution 7, with its approval record."""
    state = measured_state(cond)
    state['inputs']['GATE_ATTEMPT'], state['inputs']['GATE_FIRST_EXECUTION'] = str(attempt), str(first)
    state['files'][f'manifests/e07-further-attempt-approval-{SUT_TAGS[SUT_OF[cond]]}-v1.yaml'] = json.dumps(further_fixture(cond, SUT_OF[cond], attempt, first))
    return state


def measured_state(cond=COND_A):
    """The must-pass state of the measured-execution gate: every gate satisfied by fictitious fixture content."""
    sut = SUT_OF[cond]
    files = {
        STUDY: json.dumps({'campaigns': [{'id': CAMPAIGN, 'status': 'IN_PROGRESS'}]}),
        CHANGELOG: f'| FIXTURE | experiments/E07-cross-layer-continuity/README.md | campaign NOT_STARTED -> IN_PROGRESS | {AUTH_START} |\n',
        START_RECORD: json.dumps({'record_class': 'CAMPAIGN_START', 'campaign_id': CAMPAIGN, 'authorization_id': AUTH_START}),
        README: readme_fixture(cond, sut),
        CONDITIONS_REL: CONDITIONS_BYTES.decode('utf-8'),
        SUT_MANIFEST: json.dumps(sut_manifest_fixture()),
        GOV: GOV_TEXT,
        f'manifests/e07-dispatch-authorization-{SUT_TAGS[sut]}-v1.yaml': json.dumps(dispatch_fixture(cond, sut)),
        CONTROLLED: json.dumps(controlled_fixture(cond)),
        SCHEMA: json.dumps({'$id': 'urn:eus-2026-001:schemas:run-manifest:v2'}),
        f'prompts/frozen/{PV}.md': PROMPT_TEXT.decode('utf-8'),
        IMPL: IMPL_TEXT.decode('utf-8'),
        WORKFLOW_REL: MEASURED_BYTES.decode('utf-8'),
    }
    files.update(mapping_fixtures(cond, sut))
    return {'files': files, 'inputs': measured_inputs(cond, sut)}


def verify_state(cond=COND_A):
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


def fail_lines(out):
    return [l for l in out.splitlines() if l.startswith('FAIL ')]


@unittest.skipIf(shutil.which('ruby') is None and not _pyyaml_importable(), 'the gates need PyYAML or ruby (stand-in)')
class MeasuredGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = extract_heredoc(MEASURED, 'gate', 'gates')
        cls.work = tempfile.mkdtemp(prefix='e07-measured-gate-')

    def assertPasses(self, state, label):
        code, out = run_script(state, self.script, os.path.join(self.work, label), self.work)
        self.assertEqual(code, 0, out)
        self.assertIn('ALL GATES PASSED', out)

    def assertFailsOn(self, state, label, fragment):
        code, out = run_script(state, self.script, os.path.join(self.work, label), self.work)
        self.assertNotEqual(code, 0, f'{label} unexpectedly passed:\n{out}')
        self.assertTrue(any(fragment in l for l in fail_lines(out)), f'{label}: no FAIL line names {fragment!r}\n{out}')

    def test_must_pass_each_of_the_four_conditions(self):
        for cond in SUT_OF:
            with self.subTest(condition=cond):
                self.assertPasses(measured_state(cond), 'pass-' + cond)

    def test_must_pass_when_the_other_direction_of_the_same_sut_is_not_comparable(self):
        state = measured_state(COND_A)
        other = json.loads(state['files'][MAPPINGS['CS-006']])
        self.assertEqual(other['mappings'][0]['comparability'], 'NOT_COMPARABLE')  # the fixture is the asymmetric case
        self.assertPasses(state, 'pass-asymmetric')

    def mutate(self, label, fragment, change, cond=COND_A):
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

        def dispatch(key, value, cond=COND_A):
            def f(s):
                path = f'manifests/e07-dispatch-authorization-{SUT_TAGS[SUT_OF[cond]]}-v1.yaml'
                d = json.loads(s['files'][path])
                if key == 'frozen_inputs.impl':
                    d['frozen_inputs']['executor_implementation_sha256'] = value
                elif key == 'frozen_inputs.prompt':
                    d['frozen_inputs']['executor_prompt_sha256'] = value
                else:
                    d[key] = value
                s['files'][path] = json.dumps(d)
            return f

        def controlled(key, value, cond=COND_A):
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

        def mapping(scn, key, value):
            def f(s):
                d = json.loads(s['files'][MAPPINGS[scn]])
                if key == 'sut':
                    d['mappings'] = [{'sut_id': 'SUT-02', 'comparability': 'COMPARABLE'}]
                elif key == 'comparability':
                    d['mappings'][0]['comparability'] = value
                else:
                    d[key] = value
                s['files'][MAPPINGS[scn]] = json.dumps(d)
            return f

        def conditions_field(cond, key, value):
            def f(s):
                doc = json.loads(s['files'][CONDITIONS_REL])
                for c in doc['conditions']:
                    if c['condition_id'] == cond:
                        c[key] = value
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

        scn_a = SCENARIO_OF[COND_A]  # CS-005
        cases = [
            ('campaign-not-started', 'E07 campaign status IN_PROGRESS',
             put(STUDY, json.dumps({'campaigns': [{'id': CAMPAIGN, 'status': 'NOT_STARTED'}]}))),
            ('campaign-frozen', 'E07 campaign status IN_PROGRESS',
             put(STUDY, json.dumps({'campaigns': [{'id': CAMPAIGN, 'status': 'FROZEN'}]}))),
            ('no-start-row', 'exactly one E07 campaign START change-log row', rm(CHANGELOG)),
            ('start-row-without-auth-id', 'the START row carries the campaign START authorization id',
             start_rows('| FIXTURE | experiments/E07-cross-layer-continuity/README.md | campaign NOT_STARTED -> IN_PROGRESS |\n')),
            ('two-start-rows', 'exactly one E07 campaign START change-log row',
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
            ('configuration-without-the-primary-metric', 'configuration names the primary metric, the continuity success proportion',
             edit(README, 'continuity success proportion', 'TSRR')),
            ('configuration-without-the-scenario-of-the-condition', 'configuration names the canonical scenario of the condition',
             edit(README, scn_a, 'CS-009')),
            ('configuration-without-cs006', 'configuration names both canonical scenarios CS-005 and CS-006', edit(README, 'CS-006', 'CS-009')),
            ('configuration-without-commit', 'configuration names the pinned commit of every E07 surface component',
             edit(README, SUT01_COMMIT, 'x')),
            ('governance-draft', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', put(GOV, '| Protocol state | DRAFT |\n\n### 3.7 Dispatch authorization\n')),
            ('governance-missing', 'agent-governance-v6 is FROZEN-PRE-DATA or AMENDED', rm(GOV)),
            ('governance-without-section-3-7', 'agent-governance-v6 names the per-SUT dispatch authorization of Section 3.7',
             put(GOV, '| Protocol state | FROZEN-PRE-DATA |\n')),
            ('dispatch-authorization-absent', 'exactly one dispatch authorization record of the assigned SUT',
             rm('manifests/e07-dispatch-authorization-sut01-v1.yaml')),
            ('dispatch-authorization-pending', 'dispatch authorization is ISSUED, VALID', dispatch('status', 'PENDING')),
            ('dispatch-not-eligible', 'dispatch authorization is ISSUED, VALID', dispatch('dispatch_eligibility', 'NOT_ELIGIBLE')),
            ('dispatch-revoked', 'dispatch authorization is ISSUED, VALID', dispatch('revoked', True)),
            ('dispatch-issued-by-agent', 'issued by the human research lead', dispatch('issued_by', 'ORCHESTRATOR')),
            ('dispatch-sut-mismatch', 'dispatch authorization names the assigned SUT', dispatch('assigned_sut', 'SUT-04')),
            ('dispatch-condition-missing', 'dispatch authorization names this condition', dispatch('conditions', ['E07-CS006-SUT01-WEB-API'])),
            ('dispatch-n-30', 'dispatch authorization names N = 50 executions per condition', dispatch('n_executions', 30)),
            ('dispatch-attempt-two', 'dispatch authorization records attempt 1', dispatch('attempt', 2)),
            ('dispatch-without-date', 'dispatch authorization records attempt 1 and an authorization date', dispatch('authorization_date', None)),
            ('dispatch-start-id-mismatch', 'dispatch authorization names the campaign START authorization id', dispatch('campaign_start_authorization_id', 'OTHER')),
            ('dispatch-impl-hash-mismatch', 'records the executor implementation SHA-256 equal to the input', dispatch('frozen_inputs.impl', '0' * 64)),
            ('dispatch-prompt-hash-mismatch', 'records the executor prompt SHA-256 equal to the frozen prompt file', dispatch('frozen_inputs.prompt', '0' * 64)),
            ('prompt-file-missing', 'executor prompt frozen file exists', rm(f'prompts/frozen/{PV}.md')),
            ('controlled-instance-candidate', 'controlled instance status CONTROLLED', controlled('status', 'CANDIDATE')),
            ('controlled-instance-not-verified-status', 'controlled instance status CONTROLLED', controlled('status', 'NOT_VERIFIED')),
            ('github-verification-not-verified', 'GitHub Actions environment verification VERIFIED', controlled('verification', 'NOT_VERIFIED')),
            ('reverification-required', 'no provisioning change awaiting re-verification', controlled('reverification_required', True)),
            ('public-hosted-target', 'environment_type SELF_HOSTED', controlled('environment_type', 'PUBLIC_HOSTED')),
            ('cs005-draft', 'CS-005 mapping FROZEN', mapping('CS-005', 'mapping_status', 'DRAFT')),
            ('cs006-draft', 'CS-006 mapping FROZEN', mapping('CS-006', 'mapping_status', 'DRAFT')),
            ('cs005-absent', 'CS-005 mapping FROZEN', rm(MAPPINGS['CS-005'])),
            ('cs006-absent', 'CS-006 mapping FROZEN', rm(MAPPINGS['CS-006'])),
            ('cs005-without-the-assigned-sut', 'CS-005 names a mapping entry for the assigned SUT', mapping('CS-005', 'sut', None)),
            ('cs006-without-the-assigned-sut', 'CS-006 names a mapping entry for the assigned SUT', mapping('CS-006', 'sut', None)),
            ('entry-not-comparable-in-the-scenario-of-the-condition', 'the mapping entry of the assigned SUT in the scenario of the condition is COMPARABLE',
             mapping(scn_a, 'comparability', 'NOT_COMPARABLE')),
            ('scenario-record-carries-another-id', 'the mapping record of the condition scenario carries that canonical_scenario_id',
             mapping(scn_a, 'canonical_scenario_id', 'CS-009')),
            ('condition-scenario-not-an-e07-scenario', 'condition names a canonical scenario of E07', conditions_field(COND_A, 'canonical_scenario_id', 'CS-009')),
            ('condition-layers-swapped', 'condition layers are the direction of its scenario', conditions_field(COND_A, 'source_layer', 'web')),
            ('condition-mobile-layer', 'condition layers are the direction of its scenario', conditions_field(COND_A, 'verification_layer', 'android')),
            ('schema-id-wrong', 'run-manifest schema v2 present with the v2 id', put(SCHEMA, '{"$id": "urn:other"}')),
            ('implementation-hash-differs', 'executor implementation exists and equals the locked hash', put(IMPL, 'changed\n')),
            ('condition-not-in-file', 'condition is one of the four E07 conditions', inp('GATE_CONDITION_ID', 'E07-OTHER-API-01')),
            ('condition-wrong-sut', 'condition belongs to the assigned SUT', inp('GATE_ASSIGNED_SUT', 'SUT-04')),
            ('assigned-sut-not-in-e07', 'assigned SUT is one of the two SUTs of E07', inp('GATE_ASSIGNED_SUT', 'SUT-03')),
            ('sut-manifest-without-commit', 'SUT has pinned commits for the E07 surface components', sut_manifest_without_commit('SUT-01')),
            ('campaign-start-id-absent', 'campaign START authorization id is present', inp('GATE_CAMPAIGN_START_AUTHORIZATION_ID', '')),
            ('implementation-hash-malformed', 'executor implementation hash is a SHA-256 value', inp('GATE_EXECUTOR_IMPLEMENTATION_SHA256', 'abc')),
            ('prompt-id-malformed', 'executor prompt version is a plain identifier', inp('GATE_EXECUTOR_PROMPT_VERSION', '../x')),
        ]
        for label, fragment, change in cases:
            with self.subTest(case=label):
                self.mutate(label, fragment, change)

    def test_a_further_attempt_with_its_approval_record_passes(self):
        self.assertPasses(further_state(COND_A), 'pass-further-sut01')
        self.assertPasses(further_state(COND_B, attempt=3, first=1), 'pass-further-sut04')

    def test_a_further_attempt_without_a_matching_approval_fails_closed(self):
        path = lambda c: f'manifests/e07-further-attempt-approval-{SUT_TAGS[SUT_OF[c]]}-v1.yaml'

        def appr(key, value, cond=COND_A):
            def f(s):
                d = json.loads(s['files'][path(cond)])
                d[key] = value
                s['files'][path(cond)] = json.dumps(d)
            return f

        def entry(key, value, cond=COND_A):
            def f(s):
                d = json.loads(s['files'][path(cond)])
                d['attempts'][0][key] = value
                s['files'][path(cond)] = json.dumps(d)
            return f

        def inp(key, value):
            return lambda s: s['inputs'].__setitem__(key, value)

        no_entry = 'exactly one further-attempt approval entry names this condition, this first execution and this attempt'
        cases = [
            ('record-absent', no_entry, lambda s: s['files'].pop(path(COND_A))),
            ('other-condition', no_entry, entry('condition_id', 'E07-CS006-SUT01-WEB-API')),
            ('other-first-execution', no_entry, entry('first_execution', 8)),
            ('other-attempt', no_entry, entry('attempt', 3)),
            ('revoked', 'the approval is an ISSUED, unrevoked E07 further-attempt approval', appr('revoked', True)),
            ('not-issued', 'the approval is an ISSUED, unrevoked E07 further-attempt approval', appr('status', 'PENDING')),
            ('issued-by-agent', 'the approval is an ISSUED, unrevoked E07 further-attempt approval', appr('issued_by', 'ORCHESTRATOR')),
            ('wrong-class', 'the approval is an ISSUED, unrevoked E07 further-attempt approval', appr('record_class', 'E07_DISPATCH_AUTHORIZATION')),
            ('other-sut', 'the approval is an ISSUED, unrevoked E07 further-attempt approval', appr('assigned_sut', 'SUT-04')),
            ('other-dispatch-id', 'the approval cites the dispatch authorization of this dispatch', appr('dispatch_authorization_id', 'OTHER')),
            ('other-start-id', 'the approval cites the dispatch authorization of this dispatch', appr('campaign_start_authorization_id', 'OTHER')),
            ('other-impl-hash', 'the approval cites the dispatch authorization of this dispatch', appr('executor_implementation_sha256', '0' * 64)),
            ('other-prompt-version', 'the approval cites the dispatch authorization of this dispatch', appr('executor_prompt_version', 'OTHER')),
            ('other-prompt-sha', 'the approval names the executor prompt SHA-256', appr('executor_prompt_sha256', '0' * 64)),
            ('no-section-3-7', 'the approval cites governance v6, Section 3.7', appr('governing_protocol', 'protocol/agent-governance-v6.md, Section 3.6')),
            ('wrong-previous-attempt', 'the approval cites governance v6, Section 3.7, and names the attempt before this one', entry('previous_attempt', 5)),
            ('attempt-zero', 'attempt is a positive integer', inp('GATE_ATTEMPT', '0')),
            ('attempt-text', 'attempt is a positive integer', inp('GATE_ATTEMPT', 'two')),
            ('first-fifty-one', 'first execution is an integer from 1 to 50', inp('GATE_FIRST_EXECUTION', '51')),
            ('first-zero', 'first execution is an integer from 1 to 50', inp('GATE_FIRST_EXECUTION', '0')),
            ('attempt-1-from-execution-5', 'first execution is an integer from 1 to 50, and 1 for attempt 1', None),
        ]
        for label, fragment, change in cases:
            with self.subTest(case=label):
                state = further_state(COND_A)
                if change is None:
                    state = measured_state(COND_A)
                    state['inputs']['GATE_FIRST_EXECUTION'] = '5'
                else:
                    change(state)
                self.assertFailsOn(state, 'fa-' + label, fragment)

    def test_attempt_1_needs_no_approval_and_ignores_a_stray_one(self):
        self.assertPasses(measured_state(COND_A), 'attempt-1-plain')
        state = measured_state(COND_A)  # a stray approval record for attempt 2 does not change an attempt-1 dispatch
        state['files'][f'manifests/e07-further-attempt-approval-{SUT_TAGS[SUT_OF[COND_A]]}-v1.yaml'] = json.dumps(further_fixture(COND_A, SUT_OF[COND_A]))
        self.assertPasses(state, 'attempt-1-stray-approval')

    def test_sut04_release_missing_from_the_configuration_fails(self):
        self.mutate('sut04-release-absent', 'configuration names the pinned release of the assigned SUT',
                    lambda s: s['files'].__setitem__(README, s['files'][README].replace(SUT04_RELEASE, 'x')), cond=COND_B)

    def test_refused_by_gate_g1_alone_when_the_campaign_is_not_in_progress(self):
        """The counterpart of the as-is check of E04 on a fully fixtured tree: with every other input in place, a campaign that is NOT_STARTED
        (today's state) or FROZEN is refused by the status check of G-1 and by no other check."""
        for status in ('NOT_STARTED', 'FROZEN'):
            with self.subTest(status=status):
                state = measured_state(COND_A)
                state['files'][STUDY] = json.dumps({'campaigns': [{'id': CAMPAIGN, 'status': status}]})
                code, out = run_script(state, self.script, os.path.join(self.work, 'g1-alone-' + status), self.work)
                self.assertNotEqual(code, 0, out)
                self.assertEqual(fail_lines(out), ['FAIL E07 campaign status IN_PROGRESS: ' + status], out)

    def test_as_is_repository_state_fails_closed(self):
        """The files of this repository as they are now (copied where present) must not pass the gate: E07 is NOT_STARTED, so the status check
        of G-1 fails, and so do the checks about the START record, the locked configuration, the dispatch authorization, the controlled-instance
        status (every condition NOT_VERIFIED), the scenario records (DRAFT) and the frozen prompt. Once the campaign START and the freeze of the
        scenario records have written those records, this test is adapted as the E04 one was (the checks that may still fail are named)."""
        files = {}
        for rel in (STUDY, CHANGELOG, GOV, README, CONDITIONS_REL, SUT_MANIFEST, SCHEMA, IMPL, WORKFLOW_REL, START_RECORD, CONTROLLED,
                    MAPPINGS['CS-005'], MAPPINGS['CS-006'], f'prompts/frozen/{REAL_PROMPT}.md'):
            path = os.path.join(REPO, rel)
            if os.path.isfile(path):
                with open(path, encoding='utf-8') as f:
                    files[rel] = f.read()
        inputs = measured_inputs(COND_A, 'SUT-01')
        inputs['GATE_EXECUTOR_PROMPT_VERSION'] = REAL_PROMPT
        impl_path = os.path.join(REPO, IMPL)
        inputs['GATE_EXECUTOR_IMPLEMENTATION_SHA256'] = hashlib.sha256(open(impl_path, 'rb').read()).hexdigest() if os.path.isfile(impl_path) else '0' * 64
        inputs['GATE_CAMPAIGN_START_AUTHORIZATION_ID'] = 'E07-START-AUTH-01'  # the proposed START authorization id
        code, out = run_script({'files': files, 'inputs': inputs}, self.script, os.path.join(self.work, 'as-is'), self.work)
        self.assertNotEqual(code, 0, out)
        fails = fail_lines(out)
        self.assertTrue(any('E07 campaign status IN_PROGRESS' in l for l in fails), out)
        self.assertTrue(any('exactly one dispatch authorization record of the assigned SUT' in l for l in fails), out)
        self.assertIn('PASS run-manifest schema v2 present with the v2 id', out)


class VerificationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = extract_heredoc(VERIFY, 'gate', 'gates')
        cls.work = tempfile.mkdtemp(prefix='e07-verify-gate-')

    def test_must_pass_with_the_working_prompt_copy(self):
        code, out = run_script(verify_state(), self.script, os.path.join(self.work, 'pass'), self.work)
        self.assertEqual(code, 0, out)
        self.assertIn('ALL GATES PASSED', out)

    def test_must_pass_for_every_condition_and_for_all(self):
        for target in ['all'] + list(SUT_OF):
            with self.subTest(target=target):
                code, out = run_script(verify_state(target), self.script, os.path.join(self.work, 'pass-' + target), self.work)
                self.assertEqual(code, 0, out)

    def test_must_fail_matrix(self):
        def inp(key, value):
            return lambda s: s['inputs'].__setitem__(key, value)

        def conditions_doc(change):
            def f(s):
                doc = json.loads(s['files'][CONDITIONS_REL])
                change(doc)
                s['files'][CONDITIONS_REL] = json.dumps(doc)
            return f

        def add_condition(doc):
            extra = dict(doc['conditions'][0])
            extra['condition_id'] = 'E07-CS005-SUT01-API-WEB-EXTRA'
            doc['conditions'].append(extra)

        def same_layers(doc):
            doc['conditions'][0]['verification_layer'] = doc['conditions'][0]['source_layer']

        def mobile_layer(doc):
            doc['conditions'][0]['verification_layer'] = 'android'

        def other_scenario(doc):
            doc['conditions'][0]['canonical_scenario_id'] = 'CS-001'

        cases = [
            ('executions-fifty', 'executions is 2 or 3', inp('GATE_EXECUTIONS', '50')),
            ('target-unknown', 'target is all or one condition of the conditions file', inp('GATE_TARGET', 'E07-NOPE-API-01')),
            ('impl-hash-differs', 'executor implementation hash equals the input', inp('GATE_EXECUTOR_IMPLEMENTATION_SHA256', '0' * 64)),
            ('prompt-id-malformed', 'executor prompt version is a plain identifier', inp('GATE_EXECUTOR_PROMPT_VERSION', '../x')),
            ('working-prompt-absent', 'executor prompt working copy exists', lambda s: s['files'].pop(f'prompts/working/{PV}.md')),
            ('five-conditions', 'conditions file lists four unique E07 conditions', conditions_doc(add_condition)),
            ('conditions-file-absent', 'conditions file lists four unique E07 conditions', lambda s: s['files'].pop(CONDITIONS_REL)),
            ('same-layers', 'every condition is a web and api cross-layer condition', conditions_doc(same_layers)),
            ('mobile-layer', 'every condition is a web and api cross-layer condition', conditions_doc(mobile_layer)),
            ('scenario-of-another-campaign', 'every condition is a web and api cross-layer condition', conditions_doc(other_scenario)),
        ]
        for label, fragment, change in cases:
            with self.subTest(case=label):
                state = verify_state()
                change(state)
                code, out = run_script(state, self.script, os.path.join(self.work, label), self.work)
                self.assertNotEqual(code, 0, out)
                self.assertTrue(any(fragment in l for l in fail_lines(out)), out)

    def test_as_is_repository_state_has_the_working_prompt_of_e07(self):
        """The working copy of the E07 dispatch procedure is in this repository (prompts/working/ORCHESTRATOR-E07-cross-layer-continuity-v1.md), so
        the working-copy check of the verification gate passes on the repository state; with that file absent the same check fails. The test
        reads the real executor file and is skipped while the executor is absent."""
        impl_path = os.path.join(REPO, IMPL)
        if not os.path.isfile(impl_path):
            self.skipTest('the E07 executor is not present in this tree (experiments/E07-cross-layer-continuity/executor/run-condition.sh); the test runs once it is')
        prompt_rel = 'prompts/working/ORCHESTRATOR-E07-cross-layer-continuity-v1.md'
        files = {}
        for rel in (CONDITIONS_REL, GOV, SCHEMA, IMPL, prompt_rel):
            with open(os.path.join(REPO, rel), encoding='utf-8') as f:
                files[rel] = f.read()
        inputs = dict(verify_state()['inputs'])
        inputs['GATE_EXECUTOR_PROMPT_VERSION'] = 'ORCHESTRATOR-E07-cross-layer-continuity-v1'
        inputs['GATE_EXECUTOR_IMPLEMENTATION_SHA256'] = hashlib.sha256(open(impl_path, 'rb').read()).hexdigest()
        code, out = run_script({'files': files, 'inputs': inputs}, self.script, os.path.join(self.work, 'as-is-prompt'), self.work)
        self.assertIn('PASS executor prompt working copy exists', out)
        del files[prompt_rel]
        code, out = run_script({'files': files, 'inputs': inputs}, self.script, os.path.join(self.work, 'no-prompt'), self.work)
        self.assertNotEqual(code, 0, out)
        self.assertIn('FAIL executor prompt working copy exists', out)

    def test_the_working_prompt_check_passes_on_the_repository_files_without_the_executor(self):
        """The same check with the repository's working prompt and a fixture executor text: it does not depend on the executor being present."""
        prompt_rel = 'prompts/working/ORCHESTRATOR-E07-cross-layer-continuity-v1.md'
        with open(os.path.join(REPO, prompt_rel), encoding='utf-8') as f:
            prompt_text = f.read()
        state = verify_state()
        state['files'][prompt_rel] = prompt_text
        state['inputs']['GATE_EXECUTOR_PROMPT_VERSION'] = 'ORCHESTRATOR-E07-cross-layer-continuity-v1'
        code, out = run_script(state, self.script, os.path.join(self.work, 'repo-prompt'), self.work)
        self.assertEqual(code, 0, out)
        self.assertIn('PASS executor prompt working copy exists', out)


@unittest.skipIf(shutil.which('ruby') is None, 'ruby is needed to read the workflow plan step')
class PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = extract_heredoc(VERIFY, 'plan', 'plan')
        cls.work = tempfile.mkdtemp(prefix='e07-plan-')

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

    def test_all_builds_the_four_conditions_with_their_suts(self):
        code, out, matrix = self.plan('all')
        self.assertEqual(code, 0, out)
        self.assertEqual(len(matrix['include']), 4)
        self.assertEqual({i['sut_id'] for i in matrix['include']}, {'SUT-01', 'SUT-04'})
        for item in matrix['include']:
            self.assertEqual(item['sut_id'], SUT_OF[item['condition_id']])

    def test_one_condition_builds_one_job(self):
        code, out, matrix = self.plan(COND_B)
        self.assertEqual(code, 0, out)
        self.assertEqual(matrix['include'], [{'condition_id': COND_B, 'sut_id': 'SUT-04'}])

    def test_an_unknown_target_fails_closed(self):
        code, out, matrix = self.plan('E07-NOPE-API-01')
        self.assertNotEqual(code, 0)
        self.assertIsNone(matrix)
        self.assertIn('unknown target', out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
