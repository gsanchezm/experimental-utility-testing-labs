"""Static checks of the two E09 workflows, of the executor imports, and of the publication hygiene of every new file.

DRAFT (operation OP-PREP-E09). actionlint and shellcheck run only when their binaries are named by the environment variables
ACTIONLINT and SHELLCHECK (or are on PATH); otherwise the lint test reports SKIPPED. The OP-CI-15 length estimate follows the
validation step of the repository's validation workflow: a string that carries an expression is estimated as its length plus
the count of quote, left brace, and right brace characters, and must not exceed 20000.
"""
import glob
import os
import py_compile
import re
import shutil
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
EXEC = os.path.join(REPO, 'experiments', 'E09-accessibility', 'executor')
WORKFLOWS = [os.path.join(REPO, '.github', 'workflows', 'e09-measured-execution.yml'),
             os.path.join(REPO, '.github', 'workflows', 'e09-environment-verification.yml')]
NEW_FILES = sorted(set(
    [p for p in glob.glob(os.path.join(EXEC, '**', '*'), recursive=True) if os.path.isfile(p) and '__pycache__' not in p]
    + WORKFLOWS + [os.path.join(REPO, 'experiments', 'E09-accessibility', 'executor', 'IMPLEMENTATION-NOTES.md')]))
OPENER = '$' + '{' + '{'
LIMIT = 20000

try:
    import yaml
except ImportError:
    yaml = None


def load(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def strings(obj, where=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from strings(v, where + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from strings(v, where + (str(i),))
    elif isinstance(obj, str):
        yield where, obj


@unittest.skipIf(yaml is None, 'PyYAML is not importable')
class WorkflowTests(unittest.TestCase):
    def test_both_workflows_parse_and_are_dispatch_only(self):
        for path in WORKFLOWS:
            wf = load(path)
            triggers = wf.get('on', wf.get(True))  # PyYAML reads the bare key "on" as a boolean
            self.assertEqual(list(triggers.keys()), ['workflow_dispatch'], path)
            self.assertEqual(wf['permissions'], {'contents': 'read'}, path)

    def test_no_expression_inside_any_run_script(self):
        for path in WORKFLOWS:
            wf = load(path)
            for job_name, job in wf['jobs'].items():
                for step in job.get('steps', []):
                    if 'run' in step:
                        self.assertNotIn(OPENER, step['run'], f'{os.path.basename(path)} {job_name}: {step.get("name")}')

    def test_gate_reads_every_dispatch_input_from_its_environment(self):
        wf = load(WORKFLOWS[0])
        gate = next(s for s in wf['jobs']['gate']['steps'] if s.get('id') == 'gates')
        names = ['GATE_CONDITION_ID', 'GATE_ASSIGNED_SUT', 'GATE_EXECUTION_ID', 'GATE_ATTEMPT', 'GATE_CAMPAIGN_START_AUTHORIZATION_ID',
                 'GATE_DISPATCH_AUTHORIZATION_ID', 'GATE_EXECUTOR_PROMPT_VERSION', 'GATE_EXECUTOR_IMPLEMENTATION_SHA256']
        for n in names:
            self.assertIn(n, gate['env'])
            self.assertIn(OPENER, gate['env'][n])
            self.assertIn(f"os.environ['{n}']", gate['run'])

    def test_expression_length_limit_oP_CI_15(self):
        measured = []
        for path in WORKFLOWS:
            for where, s in strings(load(path)):
                if OPENER in s:
                    estimate = len(s) + s.count("'") + s.count('{') + s.count('}')
                    measured.append((estimate, len(s), os.path.basename(path), '/'.join(where)))
        measured.sort(reverse=True)
        print('\nOP-CI-15 estimate: strings that carry an expression:', len(measured),
              '| longest estimate:', measured[0][0] if measured else 0, '| limit:', LIMIT)
        for estimate, length, name, where in measured[:5]:
            print(f'  {name} {where}: length {length}, estimate {estimate}')
        self.assertTrue(all(m[0] <= LIMIT for m in measured))

    def test_pins_in_workflows_match_the_implementation(self):
        sys.path.insert(0, os.path.join(EXEC))
        from executor import scanner
        wf = load(WORKFLOWS[0])
        env = wf['env']
        self.assertEqual(env['AXE_CORE_VERSION'], scanner.AXE_VERSION)
        self.assertEqual(env['AXE_CORE_NPM_INTEGRITY'], scanner.AXE_NPM_INTEGRITY)
        self.assertEqual(env['AXE_CORE_TARBALL_URL'], scanner.AXE_TARBALL_URL)

    def test_measured_job_checks_out_only_its_own_raw_data_subtree(self):
        wf = load(WORKFLOWS[0])
        steps = wf['jobs']['measured-execution']['steps']
        checkout = steps[0]['with']['sparse-checkout']
        self.assertIn('raw-data/E09-accessibility/${{ inputs.assigned_sut }}', checkout)
        self.assertNotIn('raw-data/E09-accessibility\n', checkout)

    def test_measured_job_refuses_attempts_other_than_one_and_requires_the_locked_hash(self):
        with open(WORKFLOWS[0], encoding='utf-8') as f:
            text = f.read()
        self.assertIn('test "$GATE_RUN_ATTEMPT" = "1"', text)
        self.assertIn('LOCKED_IMPLEMENTATION_SHA256', text)
        self.assertIn('overwrite: false', text)

    def test_environment_verification_writes_no_measured_output(self):
        with open(WORKFLOWS[1], encoding='utf-8') as f:
            text = f.read()
        self.assertNotIn('raw-data/E09', text)  # no output path under raw-data/ (negative mentions are in prose only)
        self.assertIn('ENTRY_MODULE: executor.verify', text)
        self.assertIn('OUTPUT_DIR: ${{ runner.temp }}/e09-verification', text)

    def test_dry_run_step_uses_a_dry_run_instance_file_and_fails_on_an_error_bundle(self):
        # Rehearsal lesson of run 43292830947: the step ended green with two ERROR bundles (record class mismatch; exit 0 by design).
        with open(WORKFLOWS[1], encoding='utf-8') as f:
            text = f.read()
        i = text.index('Run the executor once per condition as a DRY_RUN')
        step = text[i:text.index('- name:', i + 10)]
        self.assertIn('INSTANCE_JSON: instance-dry-run.json', step)
        self.assertIn("inst['record_class'] = 'DRY_RUN'", step)
        self.assertIn("RUNNER_FAULT", step)
        self.assertIn("('ERROR', 'ABORTED')", step)
        self.assertIn('sys.exit(', step)


class ImportAndCompileTests(unittest.TestCase):
    def test_every_executor_module_compiles(self):
        for path in glob.glob(os.path.join(EXEC, 'executor', '*.py')):
            with open(path, encoding='utf-8') as f:
                compile(f.read(), path, 'exec')

    def test_every_executor_module_imports_without_a_browser(self):
        sys.path.insert(0, EXEC)
        for name in ('classify', 'common', 'config', 'instance', 'probe', 'scanner', 'sut01_catalog', 'run', 'verify'):
            __import__(f'executor.{name}')


class LintTests(unittest.TestCase):
    def binary(self, env_name, default):
        return os.environ.get(env_name) or shutil.which(default)

    def test_actionlint_with_shellcheck(self):
        actionlint = self.binary('ACTIONLINT', 'actionlint')
        shellcheck = self.binary('SHELLCHECK', 'shellcheck')
        if not actionlint or not shellcheck:
            self.skipTest('actionlint or shellcheck not available (set ACTIONLINT and SHELLCHECK)')
        proc = subprocess.run([actionlint, '-no-color', '-shellcheck', shellcheck] + WORKFLOWS, capture_output=True, text=True, timeout=300)
        print('\nactionlint exit status:', proc.returncode)
        if proc.stdout or proc.stderr:
            print(proc.stdout + proc.stderr)
        self.assertEqual(proc.returncode, 0)


class HygieneTests(unittest.TestCase):
    # Built from fragments so that this test file never contains the terms it forbids (no assistant or vendor name, and no
    # file name of the agent-instructions file, in any file of the study).
    FORBIDDEN = ['Cla' + 'ude', 'cla' + 'ude', 'Anthro' + 'pic', 'anthro' + 'pic', 'Open' + 'AI', 'Co' + 'dex', 'Hai' + 'ku',
                 'CLAU' + 'DE', 'Co-Author' + 'ed-By', 'Generated ' + 'with', '/' + 'Users/', '/pri' + 'vate/', '/ho' + 'me/',
                 'gilbert' + 'osanchez']

    def test_no_attribution_local_paths_or_agent_instruction_file_name_in_new_files(self):
        hits = []
        for path in NEW_FILES:
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue
            with open(path, encoding='utf-8', errors='replace') as f:
                text = f.read()
            for term in self.FORBIDDEN:
                if term in text:
                    hits.append((os.path.relpath(path, REPO), term))
        self.assertEqual(hits, [])

    def test_every_new_file_states_its_draft_status(self):
        for path in NEW_FILES:
            if path.endswith('.py') and os.path.basename(path) == '__init__.py':
                continue
            with open(path, encoding='utf-8', errors='replace') as f:
                head = f.read(1200)
            self.assertIn('DRAFT', head, os.path.relpath(path, REPO))


if __name__ == '__main__':
    unittest.main(verbosity=2)
