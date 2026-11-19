"""Static checks of the two E07 workflows, of their link to the executor, and of the publication hygiene of every new file.

DRAFT (operation OP-PREP-E07-05). The tests sit in experiments/E07-cross-layer-continuity/workflow-tests/ and do not depend on the executor
being present: the tests that read an executor file are skipped with a message while experiments/E07-cross-layer-continuity/executor/ is absent,
and run once it exists. The workflows are parsed through the Ruby YAML library (Psych), because this environment has no PyYAML;
the tests are skipped with a message when ruby is absent. Nothing here contacts the network, dispatches a workflow, or starts a campaign.
actionlint runs only when its binary is named by the environment variable ACTIONLINT (or is on PATH); otherwise the lint test is skipped.
The OP-CI-15 length estimate follows the validation step of the repository's validation workflow: a string that carries an expression is
estimated as its length plus the count of quote, left brace and right brace characters, and must not exceed 20000.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
EXEC = os.path.join(REPO, 'experiments', 'E07-cross-layer-continuity', 'executor')
EXEC_PRESENT = os.path.isdir(os.path.join(EXEC, 'executor'))
PROMPT = os.path.join(REPO, 'prompts', 'working', 'ORCHESTRATOR-E07-cross-layer-continuity-v1.md')
CONTROLLED = os.path.join(REPO, 'experiments', 'E07-cross-layer-continuity', 'controlled-instance-status.yaml')
CONDITIONS = os.path.join(REPO, 'experiments', 'E07-cross-layer-continuity', 'conditions-draft.json')
VERIFY = os.path.join(REPO, '.github', 'workflows', 'e07-environment-verification.yml')
MEASURED = os.path.join(REPO, '.github', 'workflows', 'e07-measured-execution.yml')
OPENER = '$' + '{' + '{'
LIMIT = 20000
RUN_LIMIT = 21000
ALLOWED_USES = {'actions/checkout@v4', 'actions/setup-python@v5', 'actions/setup-node@v4', 'actions/setup-java@v4',
                'actions/upload-artifact@v4', 'actions/download-artifact@v4'}
EXECUTOR_REQUIRED_ENV = {'CONDITION_ID', 'ASSIGNED_SUT', 'EXECUTOR_PROMPT_VERSION', 'OUTPUT_DIR', 'PROVENANCE_JSON',
                         'RUNTIME_ENVIRONMENT_JSON', 'RECORD_CLASS'}
# Steps whose run text must be identical in both workflows (the instance is provisioned exactly as the verified one).
COMMON_STEPS = ['Record the runtime environment',
                "Set up Python 3.12 and install the executor's pinned tools in a venv outside the workspace (Playwright for Python with --require-hashes; Chromium)",
                'Install the executor venv (pinned wheels, hashes checked) and Chromium, and put the venv first on PATH',
                'Write the instance interface instance.json (experiments/E07-cross-layer-continuity/executor/README.md, section 3)']


def load_workflow(path):
    """The workflow as a JSON-compatible dict, parsed by the Ruby YAML library. The key 'on' arrives as the string 'true'."""
    if shutil.which('ruby') is None:
        raise unittest.SkipTest('ruby is needed to parse the workflow YAML (no PyYAML in this environment)')
    script = 'require "yaml"; require "json"; print JSON.generate(YAML.load(File.read(ARGV[0], encoding: "UTF-8")))'
    proc = subprocess.run(['ruby', '-ryaml', '-rjson', '-e', script, path], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise AssertionError(f'{path} does not parse as YAML: {proc.stderr.strip()}')
    return json.loads(proc.stdout)


def triggers(wf):
    return wf.get('on', wf.get('true'))


def inputs_of(wf):
    return triggers(wf)['workflow_dispatch']['inputs']


def all_steps(wf):
    for job_name, job in wf['jobs'].items():
        for step in job.get('steps', []):
            yield job_name, step


def named(steps, name):
    found = [s for s in steps if s.get('name') == name]
    assert len(found) == 1, f'expected one step named {name!r}, found {len(found)}'
    return found[0]


def strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)
    elif isinstance(obj, str):
        yield obj


def condition_ids():
    with open(CONDITIONS, encoding='utf-8') as f:
        conds = json.load(f)['conditions']
    return [c['condition_id'] for c in conds], {c['condition_id']: c['sut_id'] for c in conds}


def conditions():
    with open(CONDITIONS, encoding='utf-8') as f:
        return json.load(f)['conditions']


@unittest.skipIf(shutil.which('ruby') is None, 'ruby is needed to parse the workflow YAML (no PyYAML in this environment)')
class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = load_workflow(VERIFY)
        cls.m = load_workflow(MEASURED)
        with open(VERIFY, encoding='utf-8') as f:
            cls.vtext = f.read()
        with open(MEASURED, encoding='utf-8') as f:
            cls.mtext = f.read()
        cls.ids, cls.sut_of = condition_ids()

    def test_both_workflows_parse_and_are_dispatch_only_with_read_permissions(self):
        for wf in (self.v, self.m):
            self.assertEqual(list(triggers(wf).keys()), ['workflow_dispatch'])
            self.assertEqual(wf['permissions'], {'contents': 'read'})

    def test_no_continue_on_error_anywhere(self):
        for wf in (self.v, self.m):
            self.assertNotIn('continue-on-error', json.dumps(wf))

    def test_every_uses_is_a_pinned_action_of_the_models(self):
        used = {step['uses'] for wf in (self.v, self.m) for _, step in all_steps(wf) if 'uses' in step}
        self.assertTrue(used <= ALLOWED_USES, sorted(used - ALLOWED_USES))

    def test_no_expression_inside_any_run_script(self):
        for path, wf in ((VERIFY, self.v), (MEASURED, self.m)):
            for job_name, step in all_steps(wf):
                if 'run' in step:
                    self.assertNotIn(OPENER, step['run'], f'{os.path.basename(path)} {job_name}: {step.get("name")}')

    def test_every_run_script_is_under_the_github_limit(self):
        for wf in (self.v, self.m):
            for job_name, step in all_steps(wf):
                if 'run' in step:
                    self.assertLess(len(step['run']), RUN_LIMIT, f'{job_name}: {step.get("name")}')

    def test_expression_length_estimate_op_ci_15(self):
        measured = []
        for path, wf in ((VERIFY, self.v), (MEASURED, self.m)):
            for job_name, job in wf['jobs'].items():
                for s in strings(job):
                    if OPENER in s:
                        measured.append((len(s) + s.count("'") + s.count('{') + s.count('}'), os.path.basename(path), job_name))
        measured.sort(reverse=True)
        print('\nOP-CI-15 estimate: strings that carry an expression:', len(measured), '| longest estimate:',
              measured[0][0] if measured else 0, '| limit:', LIMIT)
        self.assertTrue(all(m[0] <= LIMIT for m in measured))

    def test_gates_read_every_dispatch_input_from_their_environment(self):
        gate_v = named(self.v['jobs']['gate']['steps'], 'Verify the gates of the DRY_RUN verification (fail closed)')
        gate_m = named(self.m['jobs']['gate']['steps'], 'Verify every campaign gate against the repository (fail closed)')
        for step, inputs in ((gate_v, ['target', 'executions', 'executor_prompt_version', 'executor_implementation_sha256']),
                             (gate_m, ['condition_id', 'assigned_sut', 'campaign_start_authorization_id', 'dispatch_authorization_id',
                                       'executor_prompt_version', 'executor_implementation_sha256'])):
            env_values = set(step['env'].values())
            for name in inputs:
                self.assertIn(OPENER + ' inputs.' + name + ' }}', env_values, name)
            for key, value in step['env'].items():
                self.assertIn(f"os.environ['{key}']", step['run'], key)
        for wf in (self.v, self.m):
            for name in inputs_of(wf):
                used = any(OPENER + ' inputs.' + name + ' }}' in str(step.get('env', {})) or
                           OPENER + ' inputs.' + name + ' }}' in str(step.get('with', {})) or
                           OPENER + ' inputs.' + name + ' }}' in str(step.get('if', ''))
                           for _, step in all_steps(wf))
                self.assertTrue(used, f'input {name} is never passed to a step')

    def test_choice_lists_equal_the_conditions_file(self):
        self.assertEqual(inputs_of(self.v)['target']['options'], ['all'] + self.ids)
        self.assertEqual(inputs_of(self.m)['condition_id']['options'], self.ids)
        self.assertEqual(sorted(inputs_of(self.v)['executions']['options']), ['2', '3'])
        self.assertEqual(inputs_of(self.v)['executions']['default'], '2')

    def test_assigned_sut_options_are_the_suts_of_the_conditions(self):
        self.assertEqual(sorted(inputs_of(self.m)['assigned_sut']['options']), sorted(set(self.sut_of.values())))
        self.assertEqual(sorted(inputs_of(self.m)['assigned_sut']['options']), ['SUT-01', 'SUT-04'])
        for sut in ('SUT-02', 'SUT-03', 'SUT-05', 'SUT-06'):
            self.assertNotIn(sut, inputs_of(self.m)['assigned_sut']['options'])

    def test_the_conditions_file_lists_four_conditions_of_two_directions_on_two_suts(self):
        conds = conditions()
        self.assertEqual(len(conds), 4)
        self.assertEqual(sorted(c['condition_id'] for c in conds),
                         ['E07-CS005-SUT01-API-WEB', 'E07-CS005-SUT04-API-WEB', 'E07-CS006-SUT01-WEB-API', 'E07-CS006-SUT04-WEB-API'])
        for c in conds:
            self.assertEqual(c['n'], 50)
            self.assertEqual((c['source_layer'], c['verification_layer']),
                             ('api', 'web') if c['canonical_scenario_id'] == 'CS-005' else ('web', 'api'), c['condition_id'])

    def test_no_mobile_condition_in_either_choice_list(self):
        for c in conditions():
            self.assertIn(c['source_layer'], ('api', 'web'), c['condition_id'])
            self.assertIn(c['verification_layer'], ('api', 'web'), c['condition_id'])
        for text in (self.vtext, self.mtext):
            self.assertNotRegex(text, r'(?i)android|ios simulator|appium|mobilewright')

    def test_attempt_inputs_default_to_the_first_attempt_and_the_guard_refuses_rerun_and_malformed_values(self):
        ins = inputs_of(self.m)
        self.assertNotIn('execution_id', ins)
        for key in ('attempt', 'first_execution'):
            self.assertEqual((ins[key]['default'], ins[key]['required'], ins[key]['type']), ('1', False, 'string'), key)
        self.assertNotIn('attempt', inputs_of(self.v))
        guard = named(self.m['jobs']['gate']['steps'], 'Refuse anything but a first attempt of a dispatch on the default branch')
        self.assertIn('test "$GUARD_RUN_ATTEMPT" = "1"', guard['run'])
        self.assertIn('GUARD_INPUT_ATTEMPT" =~ ^[1-9][0-9]*$', guard['run'])
        self.assertIn('GUARD_INPUT_FIRST" =~ ^[1-9][0-9]*$', guard['run'])
        self.assertIn('test "$GUARD_REF" = "refs/heads/main"', named(self.m['jobs']['gate']['steps'], 'Refuse anything but a first attempt of a dispatch on the default branch')['run'])

    def test_record_class_is_fixed_per_workflow_and_never_crossed(self):
        self.assertEqual(self.m['env']['RECORD_CLASS'], 'MEASURED_EXPERIMENT')
        self.assertEqual(self.v['env']['RECORD_CLASS'], 'DRY_RUN')
        self.assertNotIn('MEASURED_EXPERIMENT', self.vtext)
        self.assertNotIn('RECORD_CLASS: DRY_RUN', self.mtext)

    @unittest.skipUnless(EXEC_PRESENT, 'the E07 executor is not present in this tree (experiments/E07-cross-layer-continuity/executor/); the test runs once it is')
    def test_executor_step_environment_satisfies_the_executor_contract(self):
        with open(os.path.join(EXEC, 'executor', 'common.py'), encoding='utf-8') as f:
            src = f.read()
        env_class = src[src.index('class Env'):src.index('def execution_id')]
        read = set(re.findall(r"e\['([A-Z_]+)'\]", env_class))
        self.assertTrue(EXECUTOR_REQUIRED_ENV <= read, sorted(read))
        for wf, job, prefix in ((self.v, 'verify', 'Run the executor'), (self.m, 'measured-execution', 'Execute the condition')):
            step = next(s for s in wf['jobs'][job]['steps'] if s.get('name', '').startswith(prefix))
            provided = set(step.get('env', {})) | set(wf['env'])
            self.assertTrue(EXECUTOR_REQUIRED_ENV <= provided | {'RECORD_CLASS'}, sorted(EXECUTOR_REQUIRED_ENV - provided))
            self.assertEqual(step['env']['ATTEMPT'], '1' if wf is self.v else '${{ inputs.attempt }}')
            if wf is self.m:
                self.assertEqual(step['env']['FIRST_EXECUTION'], '${{ inputs.first_execution }}')

    def test_executions_are_set_only_by_the_verification(self):
        verify_exec = next(s for s in self.v['jobs']['verify']['steps'] if s.get('name', '').startswith('Run the executor'))
        measured_exec = next(s for s in self.m['jobs']['measured-execution']['steps'] if s.get('name', '').startswith('Execute the condition'))
        self.assertIn('EXECUTIONS', verify_exec['env'])
        self.assertNotIn('EXECUTIONS', measured_exec['env'])
        self.assertEqual(self.m['env']['EXPECTED_EXECUTIONS'], '50')

    def test_measured_job_runs_one_condition_with_the_provisional_timeout(self):
        job = self.m['jobs']['measured-execution']
        self.assertEqual(job['timeout-minutes'], 60)
        self.assertIn('60 minutes is the ceiling', self.mtext)
        self.assertIn('(60, provisional: inherited from the E04 and E05 ceiling', self.m['env']['TIMEOUT_POLICY'])
        self.assertEqual(self.m['jobs']['gate']['timeout-minutes'], 10)
        self.assertEqual(self.m['jobs']['provenance']['timeout-minutes'], 10)
        self.assertLessEqual(self.v['jobs']['verify']['timeout-minutes'], 330)

    def test_verification_is_a_matrix_of_one_job_per_condition(self):
        strategy = self.v['jobs']['verify']['strategy']
        self.assertEqual(strategy['fail-fast'], False)
        self.assertEqual(strategy['max-parallel'], 4)
        self.assertEqual(strategy['matrix'], OPENER + ' fromJSON(needs.plan.outputs.matrix) }}')
        self.assertEqual(self.v['jobs']['verify']['needs'], ['gate', 'plan'])

    def test_concurrency_never_cancels_in_progress(self):
        self.assertEqual(self.m['concurrency']['group'], 'e07-measured-' + OPENER + ' inputs.condition_id }}')
        self.assertFalse(self.m['concurrency']['cancel-in-progress'])
        self.assertFalse(self.v['concurrency']['cancel-in-progress'])

    def test_measured_checkout_and_outputs_are_only_the_assigned_sut_subtree(self):
        checkout = next(s for s in self.m['jobs']['measured-execution']['steps'] if s.get('uses', '').startswith('actions/checkout'))
        sparse = checkout['with']['sparse-checkout']
        self.assertIn('raw-data/E07-cross-layer-continuity/' + OPENER + ' inputs.assigned_sut }}', sparse)
        self.assertNotIn('raw-data/E07-cross-layer-continuity\n', sparse)
        run = next(s for s in self.m['jobs']['measured-execution']['steps'] if s.get('name', '').startswith('Execute the condition'))
        self.assertEqual(run['env']['OUTPUT_DIR'], 'raw-data/E07-cross-layer-continuity/' + OPENER + ' inputs.assigned_sut }}/' + OPENER + ' inputs.condition_id }}')

    def test_verification_writes_nothing_under_raw_data(self):
        for _, step in all_steps(self.v):
            self.assertNotIn('raw-data', json.dumps(step.get('env', {})))
            self.assertNotIn('raw-data', json.dumps(step.get('with', {})))
        checkout = next(s for s in self.v['jobs']['gate']['steps'] if s.get('uses', '').startswith('actions/checkout'))
        self.assertNotIn('raw-data', checkout['with']['sparse-checkout'])

    def test_provisioning_steps_are_identical_in_both_workflows(self):
        v_steps = [s for _, s in all_steps(self.v) if 'matrix.sut_id' in str(s.get('if', ''))]
        m_by_name = {s['name']: s for _, s in all_steps(self.m) if 'inputs.assigned_sut' in str(s.get('if', ''))}
        self.assertEqual(len(v_steps), len(m_by_name))
        self.assertGreaterEqual(len(v_steps), 15)
        self.assertEqual({s['if'] for s in v_steps} - {OPENER + " matrix.sut_id == 'SUT-01' }}", OPENER + " matrix.sut_id == 'SUT-04' }}"}, set())
        for s in v_steps:
            self.assertIn(s['name'], m_by_name)
            t = m_by_name[s['name']]
            self.assertEqual(s.get('run'), t.get('run'), s['name'])
            self.assertEqual(s.get('with'), t.get('with'), s['name'])
            self.assertEqual(s.get('uses'), t.get('uses'), s['name'])
            self.assertEqual(sorted(s.get('env', {})), sorted(t.get('env', {})), s['name'])

    def test_common_steps_are_identical_in_both_workflows(self):
        v_by_name = {s['name']: s for _, s in all_steps(self.v) if 'name' in s}
        m_by_name = {s['name']: s for _, s in all_steps(self.m) if 'name' in s}
        for name in COMMON_STEPS:
            self.assertIn(name, v_by_name, name)
            self.assertIn(name, m_by_name, name)
            self.assertEqual(v_by_name[name].get('run'), m_by_name[name].get('run'), name)

    def test_bundle_uploads_run_always_and_never_overwrite(self):
        uploads_m = [s for _, s in all_steps(self.m) if s.get('uses', '').startswith('actions/upload-artifact')]
        uploads_v = [s for _, s in all_steps(self.v) if s.get('uses', '').startswith('actions/upload-artifact')]
        for s in uploads_m + uploads_v:
            self.assertIs(s['with']['overwrite'], False, s['name'])
            self.assertEqual(s['with']['retention-days'], 90, s['name'])
        bundle_m = named(self.m['jobs']['measured-execution']['steps'], 'Upload the immutable attempt bundle (the artifact root holds stdout.log, stderr.log, exit-status.txt and finished-at.txt)')
        self.assertEqual(bundle_m['if'], 'always()')
        self.assertEqual(bundle_m['with']['name'], 'e07-' + OPENER + ' inputs.condition_id }}')
        bundle_v = next(s for s in uploads_v)
        self.assertEqual(bundle_v['if'], 'always()')
        self.assertTrue(bundle_v['with']['name'].startswith('E07-DRY_RUN-'))
        self.assertTrue(any(s['with']['name'].startswith('E07-MEASURED_EXPERIMENT-') for s in uploads_m))

    def test_scrubbing_and_checks_run_always_before_the_upload(self):
        for wf, names in ((self.m, ['Replace runner host paths and private network addresses in the kept stdout.log and stderr.log by neutral markers (publication hygiene at capture; the bundle files are not edited)',
                                    'Validate the bundle (fail closed on an incomplete or invalid bundle; recorded outcomes are data, never errors)']),
                          (self.v, ['Check the DRY_RUN bundles (fail on a non-zero executor status, a missing run manifest or layer field, an ERROR outcome, an outcome category other than VERIFIED or NOT_VERIFIED, or a TOOLING attribution)',
                                    'Replace runner host paths and private network addresses in the kept stdout.log and stderr.log by neutral markers (publication hygiene at capture; the bundles are not edited)'])):
            steps = [s for _, s in all_steps(wf)]
            for n in names:
                self.assertEqual(named(steps, n)['if'], 'always()', n)
        scrub_m = named(self.m['jobs']['measured-execution']['steps'], 'Replace runner host paths and private network addresses in the kept stdout.log and stderr.log by neutral markers (publication hygiene at capture; the bundle files are not edited)')
        self.assertIn("('stdout.log', 'stderr.log')", self.mtext)
        self.assertIsNotNone(scrub_m)

    def test_dry_run_check_fails_closed_on_error_other_categories_tooling_and_missing_manifests(self):
        check = named(self.v['jobs']['verify']['steps'], 'Check the DRY_RUN bundles (fail on a non-zero executor status, a missing run manifest or layer field, an ERROR outcome, an outcome category other than VERIFIED or NOT_VERIFIED, or a TOOLING attribution)')
        for fragment in ("== 'ERROR'", "category not in ('VERIFIED', 'NOT_VERIFIED')", "attribution == 'TOOLING'", 'sys.exit(', "executor exit status", 'run manifests, expected', 'source_layer and verification_layer are mandatory'):
            self.assertIn(fragment, check['run'], fragment)

    def test_plan_fails_closed_on_an_unknown_target(self):
        plan = named(self.v['jobs']['plan']['steps'], 'Build the job matrix from the conditions file (fail closed on an unknown target)')
        self.assertIn("unknown target", plan['run'])
        self.assertIn('sys.exit(', plan['run'])

    def test_measured_gate_refuses_branches_other_than_main_and_reruns(self):
        self.assertIn('refs/heads/main', self.mtext)
        self.assertIn('GitHub-native re-run refused', self.mtext)

    @unittest.skipUnless(EXEC_PRESENT, 'the E07 executor is not present in this tree (experiments/E07-cross-layer-continuity/executor/); the test runs once it is')
    def test_the_executor_names_this_measured_workflow_file(self):
        with open(os.path.join(EXEC, 'executor', 'run.py'), encoding='utf-8') as f:
            run_py = f.read()
        self.assertIn("MEASURED_WORKFLOW = '/.github/workflows/e07-measured-execution.yml@'", run_py)
        self.assertTrue(os.path.isfile(MEASURED))

    def test_measured_inputs_are_exactly_the_declared_set(self):
        self.assertEqual(sorted(inputs_of(self.m)), sorted(['condition_id', 'assigned_sut', 'campaign_start_authorization_id',
                                                             'dispatch_authorization_id', 'executor_prompt_version',
                                                             'executor_implementation_sha256', 'attempt', 'first_execution']))


@unittest.skipUnless(EXEC_PRESENT, 'the E07 executor is not present in this tree (experiments/E07-cross-layer-continuity/executor/); the test runs once it is')
class ImportAndCompileTests(unittest.TestCase):
    def test_every_executor_module_compiles(self):
        for path in glob.glob(os.path.join(EXEC, 'executor', '*.py')):
            with open(path, encoding='utf-8') as f:
                compile(f.read(), path, 'exec')


class LintTests(unittest.TestCase):
    def binary(self, env_name, default):
        return os.environ.get(env_name) or shutil.which(default)

    def test_actionlint_when_available(self):
        actionlint = self.binary('ACTIONLINT', 'actionlint')
        shellcheck = self.binary('SHELLCHECK', 'shellcheck')
        if not actionlint or not shellcheck:
            self.skipTest('actionlint or shellcheck not available (set ACTIONLINT and SHELLCHECK)')
        proc = subprocess.run([actionlint, '-no-color', '-shellcheck', shellcheck, VERIFY, MEASURED], capture_output=True, text=True, timeout=300)
        print('\nactionlint exit status:', proc.returncode)
        if proc.stdout or proc.stderr:
            print(proc.stdout + proc.stderr)
        self.assertEqual(proc.returncode, 0)


class HygieneTests(unittest.TestCase):
    # Built from fragments so that this file never contains the terms it forbids (no assistant or vendor name, no session identifier,
    # no local user path, and no file name of the agent-instructions file, in any file of the study).
    FORBIDDEN = ['Cla' + 'ude', 'cla' + 'ude', 'CLAU' + 'DE', 'Anthro' + 'pic', 'anthro' + 'pic', 'Open' + 'AI', 'Co' + 'dex',
                 'Hai' + 'ku', 'Co-Author' + 'ed-By', 'Generated ' + 'with', 'cla' + 'ude' + '.ai', '/' + 'Users/',
                 'gilbert' + 'osanchez']

    def new_files(self):
        files = [VERIFY, MEASURED, PROMPT, CONTROLLED]
        for base in (HERE, EXEC):
            for root, _dirs, names in os.walk(base):
                if '__pycache__' in root:
                    continue
                for n in names:
                    files.append(os.path.join(root, n))
        return sorted({f for f in files if os.path.isfile(f)})

    def test_no_attribution_local_paths_or_agent_instruction_file_name_in_new_files(self):
        hits = []
        for path in self.new_files():
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue
            with open(path, encoding='utf-8', errors='replace') as f:
                text = f.read()
            for term in self.FORBIDDEN:
                if term in text:
                    hits.append((os.path.relpath(path, REPO), term))
        self.assertEqual(hits, [])

    def test_every_new_workflow_states_its_draft_status(self):
        for path in (VERIFY, MEASURED):
            with open(path, encoding='utf-8') as f:
                self.assertIn('DRAFT', f.read(1200), os.path.relpath(path, REPO))

    def test_the_working_prompt_is_working_and_not_dispatchable_and_names_the_campaign(self):
        with open(PROMPT, encoding='utf-8') as f:
            text = f.read()
        self.assertIn('prompt version id `ORCHESTRATOR-E07-cross-layer-continuity-v1`', text)
        self.assertIn('WORKING / NOT DISPATCHABLE', text)
        self.assertIn('CS-005', text)
        self.assertIn('CS-006', text)
        self.assertIn('manifests/e07-dispatch-authorization-sut0N-v*.yaml', text)
        self.assertIn('.github/workflows/e07-measured-execution.yml', text)
        self.assertNotIn('CS-001', text)

    def test_the_controlled_instance_draft_lists_the_four_conditions_not_verified(self):
        script = 'require "yaml"; require "json"; print JSON.generate(YAML.load(File.read(ARGV[0], encoding: "UTF-8")))'
        proc = subprocess.run(['ruby', '-ryaml', '-rjson', '-e', script, CONTROLLED], capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        doc = json.loads(proc.stdout)
        self.assertEqual(sorted(doc['conditions']), sorted(c['condition_id'] for c in conditions()))
        for cid, entry in doc['conditions'].items():
            self.assertNotEqual(entry['status'], 'CONTROLLED', cid)
            self.assertEqual(entry['github_actions_verification']['status'], 'NOT_VERIFIED', cid)
            self.assertIs(entry['reverification_required'], True, cid)
            self.assertEqual(entry['github_actions_verification']['environment_type'], 'SELF_HOSTED', cid)
            self.assertIsNone(entry['github_actions_verification']['run_id'], cid)


class MeasuredStepRuntimeTests(unittest.TestCase):
    """Runs the read-isolation step and the bundle-validation step of the measured workflow, as written, on synthetic trees.

    The measured workflow cannot be rehearsed on GitHub Actions before the START (every gate fails closed), so these two steps, which carry
    the attempt arithmetic, are executed here with bash. The ajv loop is replaced by a stub that only records its calls."""
    PV = 'TEST-FIXTURE-PROMPT-v1'
    COND, SUT = 'E07-CS005-SUT01-API-WEB', 'SUT-01'
    SCENARIO, SOURCE, VERIFICATION = 'CS-005', 'api', 'web'

    @classmethod
    def setUpClass(cls):
        if shutil.which('bash') is None:
            raise unittest.SkipTest('bash is needed')
        cls.m = load_workflow(MEASURED)
        steps = cls.m['jobs']['measured-execution']['steps']
        cls.iso = next(x for x in steps if x.get('name', '').startswith('Assert read isolation'))['run']
        cls.val = next(x for x in steps if x.get('name', '').startswith('Validate the bundle'))['run']
        cls.work = tempfile.mkdtemp(prefix='e07-steps-')
        cls.bin = os.path.join(cls.work, 'bin')
        os.makedirs(cls.bin)
        npx = os.path.join(cls.bin, 'npx')
        with open(npx, 'w', encoding='utf-8') as f:
            f.write('#!/bin/sh\necho "$@" >> "$FAKE_NPX_LOG"\n')
        os.chmod(npx, 0o755)

    def tree(self, label):
        path = os.path.join(self.work, label)
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)
        return path

    def run_step(self, script, tree, env):
        e = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
        e['PATH'] = self.bin + os.pathsep + e['PATH']
        e['FAKE_NPX_LOG'] = os.path.join(tree, 'npx.log')
        e.update(env)
        return subprocess.run(['bash', '-c', script], cwd=tree, env=e, capture_output=True, text=True, timeout=120)

    def bundle(self, tree, attempt, first, manifest_attempt=None, run_attempt=None, exit_status='0', scenario=None, source=None, verification=None):
        out = os.path.join(tree, 'raw-data', 'E07-cross-layer-continuity', self.SUT, self.COND)
        for i in range(first, 51):
            rid = f'{self.COND}__EX{i:04d}__A{run_attempt or attempt}'
            d = os.path.join(out, 'executions', rid)
            os.makedirs(d)
            with open(os.path.join(d, 'run-manifest.json'), 'w', encoding='utf-8') as f:
                json.dump({'run_id': rid, 'campaign_id': 'E07-cross-layer-continuity', 'sut_id': self.SUT, 'condition': self.COND,
                           'attempt': manifest_attempt or attempt, 'prompt_version': self.PV, 'scenario': scenario or self.SCENARIO,
                           'source_layer': self.SOURCE if source is None else source, 'verification_layer': self.VERIFICATION if verification is None else verification}, f)
        with open(os.path.join(out, 'exit-status.txt'), 'w', encoding='utf-8') as f:
            f.write(exit_status + '\n')
        return out

    def validate(self, tree, attempt, first):
        # the validation step reads the conditions file of the checked-out repository (the measured job checks out experiments/)
        os.makedirs(os.path.join(tree, 'experiments', 'E07-cross-layer-continuity'), exist_ok=True)
        shutil.copy(CONDITIONS, os.path.join(tree, 'experiments', 'E07-cross-layer-continuity', 'conditions-draft.json'))
        env = {'VAL_OUTPUT_DIR': os.path.join('raw-data', 'E07-cross-layer-continuity', self.SUT, self.COND), 'VAL_CONDITION_ID': self.COND,
               'VAL_ASSIGNED_SUT': self.SUT, 'VAL_PROMPT_VERSION': self.PV, 'VAL_ATTEMPT': str(attempt), 'VAL_FIRST_EXECUTION': str(first),
               'EXPECTED_EXECUTIONS': self.m['env']['EXPECTED_EXECUTIONS']}
        return self.run_step(self.val, tree, env)

    def npx_calls(self, tree):
        path = os.path.join(tree, 'npx.log')
        if not os.path.isfile(path):
            return 0
        with open(path, encoding='utf-8') as f:
            return len(f.read().splitlines())

    def test_validation_accepts_attempt_1_with_fifty_executions(self):
        t = self.tree('val-a1')
        self.bundle(t, 1, 1)
        r = self.validate(t, 1, 1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.npx_calls(t), 50)
        self.assertIn('50 run manifests checked: schema v2, identity, scenario and layers', r.stdout)

    def test_validation_accepts_a_further_attempt_from_execution_7(self):
        t = self.tree('val-a2')
        self.bundle(t, 2, 7)
        r = self.validate(t, 2, 7)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.npx_calls(t), 44)
        self.assertIn('44 run manifests checked', r.stdout)

    def test_validation_refuses_the_wrong_number_of_manifests(self):
        t = self.tree('val-count')
        self.bundle(t, 1, 2)  # 49 executions for a job that must hold 50
        r = self.validate(t, 1, 1)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('expected 50 run manifests', r.stdout + r.stderr)
        t = self.tree('val-count-further')
        self.bundle(t, 2, 1)  # 50 executions for a job that starts at execution 7
        r = self.validate(t, 2, 7)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('expected 44 run manifests', r.stdout + r.stderr)

    def test_validation_refuses_a_set_of_run_directories_of_another_attempt(self):
        t = self.tree('val-set')
        self.bundle(t, 2, 7, run_attempt=1)  # 44 directories, but of attempt 1
        r = self.validate(t, 2, 7)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('run directories differ from the expected set', r.stdout + r.stderr)

    def test_validation_refuses_a_manifest_whose_attempt_is_not_the_dispatch_attempt(self):
        t = self.tree('val-attempt')
        self.bundle(t, 2, 7, manifest_attempt=1)
        r = self.validate(t, 2, 7)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('attempt of the dispatch', r.stdout + r.stderr)

    def test_validation_refuses_a_manifest_of_another_scenario_or_with_swapped_layers(self):
        for label, kwargs, fragment in (('scenario', {'scenario': 'CS-006'}, 'scenario is the canonical scenario of the condition'),
                                        ('source', {'source': 'web'}, 'source_layer is the source layer of the condition'),
                                        ('verification', {'verification': 'api'}, 'verification_layer is the verification layer of the condition'),
                                        ('no-layer', {'source': ''}, 'source_layer is the source layer of the condition')):
            with self.subTest(case=label):
                t = self.tree('val-' + label)
                self.bundle(t, 1, 1, **kwargs)
                r = self.validate(t, 1, 1)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(fragment, r.stdout + r.stderr)

    def test_validation_refuses_an_executor_exit_status_that_is_not_0(self):
        t = self.tree('val-exit')
        self.bundle(t, 1, 1, exit_status='1')
        r = self.validate(t, 1, 1)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('executor exit status is not 0', r.stdout + r.stderr)

    def isolate(self, tree, attempt, first):
        env = {'ISO_ASSIGNED_SUT': self.SUT, 'ISO_CONDITION_ID': self.COND, 'ISO_ATTEMPT': str(attempt), 'ISO_FIRST_EXECUTION': str(first)}
        return self.run_step(self.iso, tree, env)

    def imported(self, tree, attempt, first, last, sut=None):
        base = os.path.join(tree, 'raw-data', 'E07-cross-layer-continuity', sut or self.SUT)
        for i in range(first, last + 1):
            os.makedirs(os.path.join(base, f'{self.COND}__EX{i:04d}__A{attempt}'))
        os.makedirs(os.path.join(base, f'{self.COND}__job'), exist_ok=True)

    def test_isolation_admits_a_further_attempt_beside_the_imported_first_attempt(self):
        t = self.tree('iso-ok')
        self.imported(t, 1, 1, 6)
        r = self.isolate(t, 2, 7)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('read isolation ok', r.stdout)

    def test_isolation_admits_attempt_1_on_an_empty_subtree(self):
        t = self.tree('iso-empty')
        os.makedirs(os.path.join(t, 'raw-data', 'E07-cross-layer-continuity', self.SUT))
        self.assertEqual(self.isolate(t, 1, 1).returncode, 0)
        t = self.tree('iso-no-raw-data')
        self.assertEqual(self.isolate(t, 1, 1).returncode, 0)

    def test_isolation_refuses_an_existing_run_directory_of_the_same_attempt(self):
        t = self.tree('iso-existing-a1')
        self.imported(t, 1, 1, 6)
        r = self.isolate(t, 1, 1)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('already exists: attempts are immutable', r.stdout + r.stderr)
        t = self.tree('iso-existing-a2')
        self.imported(t, 1, 1, 6)
        self.imported(t, 2, 10, 10)
        r = self.isolate(t, 2, 7)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('EX0010__A2 already exists', r.stdout + r.stderr)

    def test_isolation_refuses_the_measured_output_of_another_sut(self):
        t = self.tree('iso-other-sut')
        self.imported(t, 1, 1, 2, sut='SUT-04')
        r = self.isolate(t, 1, 1)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('isolation violated', r.stdout + r.stderr)


class DryRunCheckRuntimeTests(unittest.TestCase):
    """Runs the DRY_RUN check step of the verification workflow, as written, on synthetic bundles: a NOT_VERIFIED execution (the recorded
    observation of the continuity, which the open cells of D-E07-6 need) passes; an ERROR, another category, a TOOLING attribution, a missing
    layer field or a wrong number of manifests fails."""

    @classmethod
    def setUpClass(cls):
        if shutil.which('bash') is None:
            raise unittest.SkipTest('bash is needed')
        v = load_workflow(VERIFY)
        cls.step = next(s for s in v['jobs']['verify']['steps'] if s.get('name', '').startswith('Check the DRY_RUN bundles'))['run']
        cls.work = tempfile.mkdtemp(prefix='e07-dryrun-')

    def run_check(self, label, executions, expected, status='0'):
        out = os.path.join(self.work, label)
        shutil.rmtree(out, ignore_errors=True)
        for i, spec in enumerate(executions, 1):
            d = os.path.join(out, 'executions', f'COND__DR{i:04d}__A1')
            os.makedirs(d)
            with open(os.path.join(d, 'run-manifest.json'), 'w', encoding='utf-8') as f:
                json.dump({'run_id': f'COND__DR{i:04d}__A1', 'source_layer': spec.get('source', 'api'), 'verification_layer': spec.get('verification', 'web'),
                           'outcome': {'status': spec.get('status', 'SUCCESS'), 'outcome_category': spec['category']}}, f)
            with open(os.path.join(d, 'attempt-record.json'), 'w', encoding='utf-8') as f:
                json.dump({'attribution': spec.get('attribution', 'SUT')}, f)
        with open(os.path.join(out, 'exit-status.txt'), 'w', encoding='utf-8') as f:
            f.write(status + '\n')
        env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
        env.update({'OUTPUT_DIR': out, 'EXPECTED_EXECUTIONS': str(expected)})
        return subprocess.run(['bash', '-c', self.step], env=env, capture_output=True, text=True, timeout=120)

    def test_verified_and_not_verified_pass_and_the_categories_are_printed(self):
        r = self.run_check('ok', [{'category': 'VERIFIED'}, {'category': 'NOT_VERIFIED', 'status': 'FAILURE'}], 2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('DRY_RUN check passed', r.stdout)
        self.assertIn('"NOT_VERIFIED": 1', r.stdout)

    def test_each_problem_fails_the_check(self):
        cases = [
            ('error-status', [{'category': 'VERIFIED'}, {'category': 'VERIFIED', 'status': 'ERROR'}], 2, '0', 'status ERROR'),
            ('runner-error', [{'category': 'VERIFIED'}, {'category': 'RUNNER_ERROR', 'status': 'FAILURE'}], 2, '0', 'category RUNNER_ERROR'),
            ('interrupted', [{'category': 'VERIFIED'}, {'category': 'INTERRUPTED'}], 2, '0', 'category INTERRUPTED'),
            ('establishment-failed', [{'category': 'VERIFIED'}, {'category': 'ESTABLISHMENT_FAILED'}], 2, '0', 'category ESTABLISHMENT_FAILED'),
            ('tooling', [{'category': 'VERIFIED'}, {'category': 'VERIFIED', 'attribution': 'TOOLING'}], 2, '0', 'attribution TOOLING'),
            ('no-layer', [{'category': 'VERIFIED'}, {'category': 'VERIFIED', 'source': ''}], 2, '0', 'source_layer and verification_layer are mandatory'),
            ('wrong-count', [{'category': 'VERIFIED'}], 2, '0', 'run manifests, expected 2'),
            ('exit-status', [{'category': 'VERIFIED'}, {'category': 'VERIFIED'}], 2, '1', 'executor exit status 1'),
        ]
        for label, executions, expected, status, fragment in cases:
            with self.subTest(case=label):
                r = self.run_check(label, executions, expected, status)
                self.assertNotEqual(r.returncode, 0, r.stdout)
                self.assertIn(fragment, r.stdout + r.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
