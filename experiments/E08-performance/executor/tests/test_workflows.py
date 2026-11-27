"""Static checks of .github/workflows/e08-environment-verification.yml and e08-measured-execution.yml (operation OP-PREP-E08). Textual: no
YAML parser is needed and nothing runs. actionlint and shellcheck are run when they are on PATH (the local copies live outside the repository).

Both workflows are dispatch-only and read the repository only; they list exactly the conditions of conditions-draft.json; the provisioning
steps of each SUT group are the same in both (so that the measured instance is provisioned as the verified one); no run script of the
measured workflow carries an expression (the OP-CI-15 limit of 21000 characters applies only to scripts with one); the bash of every `run`
block parses (bash -n) and the Python of every heredoc compiles."""
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
VERIFY = os.path.join(REPO, '.github', 'workflows', 'e08-environment-verification.yml')
MEASURED = os.path.join(REPO, '.github', 'workflows', 'e08-measured-execution.yml')
CONDITIONS = os.path.join(REPO, 'experiments', 'E08-performance', 'conditions-draft.json')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def run_blocks(t):
    """The body of every `run: |` block (the lines indented deeper than the key)."""
    lines, out, i = t.split('\n'), [], 0
    while i < len(lines):
        m = re.match(r'^(\s*)run: \|\s*$', lines[i])
        if m:
            indent, body = len(m.group(1)), []
            i += 1
            while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
                body.append(lines[i])
                i += 1
            out.append('\n'.join(body))
        else:
            i += 1
    return out


def step_texts(t):
    """name -> text of every step of a workflow (a step ends at the next step, the next group comment or the next job key)."""
    lines, out, i = t.split('\n'), {}, 0
    while i < len(lines):
        m = re.match(r'^      - name: (.+)$', lines[i])
        if m:
            j = i + 1
            while j < len(lines) and not re.match(r'^(      - name: |      # ---|  [a-z-]+:\s*$)', lines[j]):
                j += 1
            out[m.group(1)] = '\n'.join(lines[i:j]).rstrip('\n')
            i = j
        else:
            i += 1
    return out


def conditions():
    return json.loads(read(CONDITIONS))['conditions']


def which(name):
    """actionlint and shellcheck are looked up on PATH only (the test is skipped when actionlint is absent)."""
    return shutil.which(name)


class CommonTests(unittest.TestCase):
    def check_dispatch_only(self, t):
        head = t.split('\njobs:')[0]
        triggers = re.search(r'^on:\n((?:  .*\n|\n)+)', head, re.M).group(1)
        self.assertEqual(re.findall(r'^  ([a-z_]+):', triggers, re.M), ['workflow_dispatch'])
        for forbidden in ('push:', 'pull_request', 'schedule:', 'workflow_run'):
            self.assertNotIn(forbidden, head)
        self.assertIn('permissions:\n  contents: read\n', head)
        self.assertNotIn('secrets.', t)
        self.assertNotIn(chr(67) + chr(76) + chr(65) + chr(85) + chr(68) + chr(69) + '.md', t)  # the agent-instructions file name, built so that this file does not carry it

    def check_blocks(self, t, minimum):
        blocks = run_blocks(t)
        self.assertGreaterEqual(len(blocks), minimum)
        for n, body in enumerate(blocks):
            lines = body.split('\n')
            ind = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
            with tempfile.NamedTemporaryFile('w', suffix='.sh', delete=False) as f:
                f.write('\n'.join(l[ind:] for l in lines))
                path = f.name
            try:
                r = subprocess.run(['bash', '-n', path], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f'block {n}: {r.stderr}')
            finally:
                os.unlink(path)
            for m in re.finditer(r"<<'PY'\n(.*?)\n\s*PY\b", body, re.S):
                code = m.group(1).split('\n')
                cind = min((len(l) - len(l.lstrip()) for l in code if l.strip()), default=0)
                compile('\n'.join(l[cind:] for l in code), f'block-{n}', 'exec')

    def test_dispatch_only_read_only_and_no_agent_instructions_file_name(self):
        self.check_dispatch_only(read(VERIFY))
        self.check_dispatch_only(read(MEASURED))

    def test_every_run_block_parses_and_every_python_heredoc_compiles(self):
        self.check_blocks(read(VERIFY), 15)
        self.check_blocks(read(MEASURED), 15)

    def test_actionlint_and_shellcheck_when_available(self):
        actionlint = which('actionlint')
        if not actionlint:
            self.skipTest('actionlint is not available')
        env = dict(os.environ)
        sc = which('shellcheck')
        if sc:
            env['PATH'] = os.path.dirname(sc) + os.pathsep + env['PATH']
        r = subprocess.run([actionlint, VERIFY, MEASURED], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_provisioning_steps_are_the_same_in_both_workflows(self):
        ver, meas = step_texts(read(VERIFY)), step_texts(read(MEASURED))
        shared = [n for n in meas if n in ver and ('SUT-0' in n or 'Node.js' in n)]
        self.assertGreaterEqual(len(shared), 15)
        for n in shared:
            a = ver[n].replace('matrix.sut_id', 'inputs.assigned_sut')
            self.assertEqual(a, meas[n], n)
        sut_groups = sorted({re.search(r"'(SUT-0\d)'", re.search(r"if: (.*)", meas[n]).group(1)).group(1) for n in shared if 'if:' in meas[n]})
        self.assertEqual(sut_groups, ['SUT-01', 'SUT-02', 'SUT-03'])

    def test_only_the_three_e08_suts_are_provisioned_and_never_a_restart_step(self):
        for t in (read(VERIFY), read(MEASURED)):
            self.assertEqual(sorted(set(re.findall(r"(?:matrix\.sut_id|inputs\.assigned_sut) == '(SUT-\d\d)'", t))), ['SUT-01', 'SUT-02', 'SUT-03'])
            for absent in ('SUT-04', 'SUT-05', 'SUT-06', 'Maven', 'JDK', 'docker'):
                self.assertNotIn(absent.lower(), t.lower().replace('(sut-04, sut-05 and sut-06 have no ground-truth condition)', ''))

    def test_the_pinned_tool_versions_agree_with_the_implementation(self):
        req = read(os.path.join(REPO, 'experiments', 'E08-performance', 'executor', 'requirements.txt'))
        self.assertIn('playwright==1.63.0', req)
        for t in (read(VERIFY), read(MEASURED)):
            self.assertIn('--require-hashes --only-binary :all: -r experiments/E08-performance/executor/requirements.txt', t)
            self.assertIn('-m playwright install --with-deps chromium', t)


class VerificationWorkflowTests(unittest.TestCase):
    def test_the_target_options_are_all_plus_the_conditions_and_the_plan_requires_four(self):
        t = read(VERIFY)
        opts = re.search(r'target:\n(?:.*\n)*?        options:\n((?:          - .*\n)+)', t).group(1)
        ids = [c['condition_id'] for c in conditions()]
        self.assertEqual(re.findall(r'- (\S+)', opts), ['all'] + ids)
        self.assertEqual(len(ids), 4)
        self.assertIn("if len(ids) != 4 or len(set(ids)) != 4:", t)

    def test_the_dry_run_is_never_measured_or_imported(self):
        t = read(VERIFY)
        self.assertIn('RECORD_CLASS: DRY_RUN', t)
        self.assertIn('test "$GUARD_DRY_RUN" = "true"', t)
        self.assertNotIn('MEASURED_EXPERIMENT', t.replace('never measured', ''))
        self.assertIn('retention-days: 90', t)
        self.assertIn('options: ["2", "3"]', t)
        self.assertIn('group: e08-environment-verification\n  cancel-in-progress: false', t)

    def test_the_dry_run_check_fails_on_error_aborted_and_tooling(self):
        t = read(VERIFY)
        self.assertIn("if o.get('status') in ('ERROR', 'ABORTED') or attribution == 'TOOLING':", t)


class MeasuredWorkflowTests(unittest.TestCase):
    def test_it_serializes_one_run_per_condition_and_records_a_measured_experiment(self):
        t = read(MEASURED)
        head = t.split('\njobs:')[0]
        self.assertIn('group: e08-measured-${{ inputs.condition_id }}\n  cancel-in-progress: false', head)
        self.assertIn('RECORD_CLASS: MEASURED_EXPERIMENT', t)
        self.assertIn('EXPECTED_EXECUTIONS: "50"', t)

    def test_the_condition_options_are_the_conditions_of_the_file_and_the_suts_are_the_three_of_e08(self):
        t = read(MEASURED)
        opts = re.search(r'condition_id:\n(?:.*\n)*?        options:\n((?:          - .*\n)+)', t).group(1)
        self.assertEqual(re.findall(r'- (\S+)', opts), [c['condition_id'] for c in conditions()])
        self.assertIn('options: [SUT-01, SUT-02, SUT-03]', t)

    def test_no_run_script_carries_an_expression_so_the_21000_character_limit_never_applies_to_it(self):
        for n, body in enumerate(run_blocks(read(MEASURED))):
            self.assertNotIn('${{', body, f'run block {n}')
            self.assertLess(len(body), 21000, f'run block {n}')

    def test_the_gate_fails_closed_on_the_inputs_that_do_not_exist_yet(self):
        t = read(MEASURED)
        for needle in ("START_RECORD = 'manifests/e08-campaign-start-v1.yaml'", "'E08 campaign status IN_PROGRESS'", 'G-E08-A2',
                       "manifests/e08-dispatch-authorization-{SUT_TAGS.get(sut", "CONTROLLED = 'experiments/E08-performance/controlled-instance-status.yaml'",
                       "gate('configuration names the H5 hypothesis label'", 'no canonical scenario', 'G-10', 'tools.performance'):
            self.assertIn(needle, t)
        self.assertNotIn('CS-001', t)
        # the START was applied on 2026-11-26 and the three dispatch authorizations were issued on 2026-11-27; no further-attempt approval exists
        self.assertEqual(sorted(os.path.basename(x) for x in glob.glob(os.path.join(REPO, 'manifests', 'e08-dispatch-authorization-*'))),
                         ['e08-dispatch-authorization-sut01-v1.yaml', 'e08-dispatch-authorization-sut02-v1.yaml', 'e08-dispatch-authorization-sut03-v1.yaml'])
        self.assertEqual(glob.glob(os.path.join(REPO, 'manifests', 'e08-further-attempt-approval-*')), [])

    def test_the_executor_is_run_only_on_the_locked_hash_with_no_executions_override_and_the_artifact_is_immutable(self):
        t = read(MEASURED)
        self.assertIn('test "$(sha256sum experiments/E08-performance/executor/run-condition.sh | cut -c1-64)" = "$LOCKED_IMPLEMENTATION_SHA256"', t)
        self.assertNotIn('EXECUTIONS:', t.split('Execute the condition')[1].split('Validate the bundle')[0])
        self.assertIn('overwrite: false', t)
        self.assertIn('OUTPUT_DIR: raw-data/E08-performance/${{ inputs.assigned_sut }}/${{ inputs.condition_id }}', t)
        self.assertIn('timeout-minutes: 120', t)


if __name__ == '__main__':
    unittest.main(verbosity=2)
