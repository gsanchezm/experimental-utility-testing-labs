"""Static checks of the two E05 workflows, of their link to the executor, and of the publication hygiene of every new file.

DRAFT (operation OP-PREP-E05). The workflows are parsed through the Ruby YAML library (Psych), because this environment has no PyYAML;
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
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
EXEC = os.path.join(REPO, 'experiments', 'E05-determinism', 'executor')
CONDITIONS = os.path.join(REPO, 'experiments', 'E05-determinism', 'conditions-draft.json')
VERIFY = os.path.join(REPO, '.github', 'workflows', 'e05-environment-verification.yml')
MEASURED = os.path.join(REPO, '.github', 'workflows', 'e05-measured-execution.yml')
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
                'Write the instance interface instance.json (experiments/E05-determinism/executor/README.md, section 3)']


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
        self.assertNotIn('SUT-03', inputs_of(self.m)['assigned_sut']['options'])

    def test_no_mobile_condition_in_either_choice_list(self):
        for cid in self.ids:
            self.assertIn(cid.split('-')[2], ('API', 'WEB'), cid)

    def test_no_attempt_or_execution_input_and_the_first_attempt_guard(self):
        self.assertNotIn('attempt', inputs_of(self.m))
        self.assertNotIn('execution_id', inputs_of(self.m))
        guard = named(self.m['jobs']['gate']['steps'], 'Refuse anything but a first attempt of a dispatch on the default branch')
        self.assertIn('test "$GUARD_RUN_ATTEMPT" = "1"', guard['run'])
        self.assertIn('test "$GUARD_REF" = "refs/heads/main"', named(self.m['jobs']['gate']['steps'], 'Refuse anything but a first attempt of a dispatch on the default branch')['run'])

    def test_record_class_is_fixed_per_workflow_and_never_crossed(self):
        self.assertEqual(self.m['env']['RECORD_CLASS'], 'MEASURED_EXPERIMENT')
        self.assertEqual(self.v['env']['RECORD_CLASS'], 'DRY_RUN')
        self.assertNotIn('MEASURED_EXPERIMENT', self.vtext)
        self.assertNotIn('RECORD_CLASS: DRY_RUN', self.mtext)

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
            self.assertEqual(step['env']['ATTEMPT'], '1')

    def test_executions_are_set_only_by_the_verification(self):
        verify_exec = next(s for s in self.v['jobs']['verify']['steps'] if s.get('name', '').startswith('Run the executor'))
        measured_exec = next(s for s in self.m['jobs']['measured-execution']['steps'] if s.get('name', '').startswith('Execute the condition'))
        self.assertIn('EXECUTIONS', verify_exec['env'])
        self.assertNotIn('EXECUTIONS', measured_exec['env'])
        self.assertEqual(self.m['env']['EXPECTED_EXECUTIONS'], '50')

    def test_measured_job_runs_one_condition_with_the_provisional_timeout(self):
        job = self.m['jobs']['measured-execution']
        self.assertEqual(job['timeout-minutes'], 330)
        self.assertIn('330 minutes is a provisional ceiling', self.mtext)
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
        self.assertEqual(self.m['concurrency']['group'], 'e05-measured-' + OPENER + ' inputs.condition_id }}')
        self.assertFalse(self.m['concurrency']['cancel-in-progress'])
        self.assertFalse(self.v['concurrency']['cancel-in-progress'])

    def test_measured_checkout_and_outputs_are_only_the_assigned_sut_subtree(self):
        checkout = next(s for s in self.m['jobs']['measured-execution']['steps'] if s.get('uses', '').startswith('actions/checkout'))
        sparse = checkout['with']['sparse-checkout']
        self.assertIn('raw-data/E05-determinism/' + OPENER + ' inputs.assigned_sut }}', sparse)
        self.assertNotIn('raw-data/E05-determinism\n', sparse)
        run = next(s for s in self.m['jobs']['measured-execution']['steps'] if s.get('name', '').startswith('Execute the condition'))
        self.assertEqual(run['env']['OUTPUT_DIR'], 'raw-data/E05-determinism/' + OPENER + ' inputs.assigned_sut }}/' + OPENER + ' inputs.condition_id }}')

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
        self.assertGreaterEqual(len(v_steps), 20)
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
        self.assertEqual(bundle_m['with']['name'], 'e05-' + OPENER + ' inputs.condition_id }}')
        bundle_v = next(s for s in uploads_v)
        self.assertEqual(bundle_v['if'], 'always()')
        self.assertTrue(bundle_v['with']['name'].startswith('E05-DRY_RUN-'))
        self.assertTrue(any(s['with']['name'].startswith('E05-MEASURED_EXPERIMENT-') for s in uploads_m))

    def test_scrubbing_and_checks_run_always_before_the_upload(self):
        for wf, names in ((self.m, ['Replace runner host paths and private network addresses in the kept stdout.log and stderr.log by neutral markers (publication hygiene at capture; the bundle files are not edited)',
                                    'Validate the bundle (fail closed on an incomplete or invalid bundle; recorded outcomes are data, never errors)']),
                          (self.v, ['Check the DRY_RUN bundles (fail on a non-zero executor status, a missing run manifest, an ERROR or ABORTED outcome, or a TOOLING attribution)',
                                    'Replace runner host paths and private network addresses in the kept stdout.log and stderr.log by neutral markers (publication hygiene at capture; the bundles are not edited)'])):
            steps = [s for _, s in all_steps(wf)]
            for n in names:
                self.assertEqual(named(steps, n)['if'], 'always()', n)
        scrub_m = named(self.m['jobs']['measured-execution']['steps'], 'Replace runner host paths and private network addresses in the kept stdout.log and stderr.log by neutral markers (publication hygiene at capture; the bundle files are not edited)')
        self.assertIn("('stdout.log', 'stderr.log')", self.mtext)
        self.assertIsNotNone(scrub_m)

    def test_dry_run_check_fails_closed_on_error_aborted_tooling_and_missing_manifests(self):
        check = named(self.v['jobs']['verify']['steps'], 'Check the DRY_RUN bundles (fail on a non-zero executor status, a missing run manifest, an ERROR or ABORTED outcome, or a TOOLING attribution)')
        for fragment in ("'ERROR', 'ABORTED'", "attribution == 'TOOLING'", 'sys.exit(', "executor exit status", 'run manifests, expected'):
            self.assertIn(fragment, check['run'], fragment)

    def test_plan_fails_closed_on_an_unknown_target(self):
        plan = named(self.v['jobs']['plan']['steps'], 'Build the job matrix from the conditions file (fail closed on an unknown target)')
        self.assertIn("unknown target", plan['run'])
        self.assertIn('sys.exit(', plan['run'])

    def test_measured_gate_refuses_branches_other_than_main_and_reruns(self):
        self.assertIn('refs/heads/main', self.mtext)
        self.assertIn('GitHub-native re-run refused', self.mtext)

    def test_the_executor_names_this_measured_workflow_file(self):
        with open(os.path.join(EXEC, 'executor', 'run.py'), encoding='utf-8') as f:
            run_py = f.read()
        self.assertIn("MEASURED_WORKFLOW = '/.github/workflows/e05-measured-execution.yml@'", run_py)
        self.assertTrue(os.path.isfile(MEASURED))

    def test_measured_inputs_are_exactly_the_declared_set(self):
        self.assertEqual(sorted(inputs_of(self.m)), sorted(['condition_id', 'assigned_sut', 'campaign_start_authorization_id',
                                                             'dispatch_authorization_id', 'executor_prompt_version',
                                                             'executor_implementation_sha256']))


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
        files = [VERIFY, MEASURED]
        for root, _dirs, names in os.walk(EXEC):
            if '__pycache__' in root:
                continue
            for n in names:
                files.append(os.path.join(root, n))
        return sorted(set(files))

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
