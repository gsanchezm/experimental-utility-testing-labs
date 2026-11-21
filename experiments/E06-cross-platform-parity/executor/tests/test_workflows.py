"""Static checks of the two E06 workflows, of the conditions file they pin, and of the publication hygiene of every new non-test file.

DRAFT (operation OP-PREP-E06-EXECUTOR). actionlint and shellcheck run only when their binaries are named by the environment variables
ACTIONLINT and SHELLCHECK (or are on PATH); otherwise the lint test is skipped. The OP-CI-15 length estimate follows the validation step of the
repository's validation workflow: a string that carries an expression is estimated as its length plus the count of quote, left brace, and
right brace characters, and must not exceed 20000.
"""
import glob
import json
import os
import py_compile
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(EXEC, '..', '..', '..'))
WORKFLOWS = [os.path.join(REPO, '.github', 'workflows', 'e06-measured-execution.yml'),
             os.path.join(REPO, '.github', 'workflows', 'e06-environment-verification.yml')]
MEASURED, VERIFY = WORKFLOWS
CONDITIONS = os.path.join(EXEC, '..', 'conditions-draft.json')
RUNNER_ACTION = 'ReactiveCircus/android-emulator-runner@a421e43855164a8197daf9d8d40fe71c6996bb0d'
OPENER = '$' + '{' + '{'
LIMIT = 20000
def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

CONDITION_IDS = ['E06-CS007-SUT01-WEB', 'E06-CS007-SUT01-ANDROID', 'E06-CS007-SUT02-WEB', 'E06-CS007-SUT02-ANDROID']
# words of the publication-hygiene rule (no tool or vendor attribution in a new file); built from parts so that this file does not hold them
FORBIDDEN = [''.join(p) for p in (('Cl', 'aude'), ('Anth', 'ropic'), ('Co', 'dex'), ('Hai', 'ku'), ('Open', 'AI'), ('Chat', 'GPT'))]

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
    def test_both_workflows_are_dispatch_only_and_read_only(self):
        for path in WORKFLOWS:
            wf = load(path)
            triggers = wf.get('on', wf.get(True))
            self.assertEqual(list(triggers.keys()), ['workflow_dispatch'], path)
            self.assertEqual(wf['permissions'], {'contents': 'read'}, path)

    def test_no_expression_inside_any_run_script(self):
        for path in WORKFLOWS:
            for job_name, job in load(path)['jobs'].items():
                for step in job.get('steps', []):
                    if 'run' in step:
                        self.assertNotIn(OPENER, step['run'], f'{os.path.basename(path)} {job_name}: {step.get("name")}')

    def test_the_gate_reads_every_dispatch_input_from_its_environment(self):
        gate = next(s for s in load(MEASURED)['jobs']['gates']['steps'] if s.get('id') == 'gates')
        names = ['GATE_CONDITION_ID', 'GATE_CONFIRM', 'GATE_DISPATCH_AUTHORIZATION_ID', 'GATE_CAMPAIGN_START_AUTHORIZATION_ID',
                 'GATE_EXECUTOR_PROMPT_VERSION', 'GATE_EXECUTOR_IMPLEMENTATION_SHA256', 'GATE_RUN_ATTEMPT', 'GATE_REF', 'GATE_SHA']
        for n in names:
            self.assertIn(n, gate['env'] if 'env' in gate else load(MEASURED)['jobs']['gates']['env'], n)
            self.assertIn(f"env.get('{n}'", gate['run'], n)  # the gate script reads the variable from the environment

    def test_the_expression_length_limit_of_op_ci_15(self):
        measured = []
        for path in WORKFLOWS:
            for where, s in strings(load(path)):
                if OPENER in s:
                    estimate = len(s) + s.count("'") + s.count('{') + s.count('}')
                    measured.append((estimate, len(s), os.path.basename(path), '/'.join(where)))
        measured.sort(reverse=True)
        print('\nOP-CI-15 estimate: strings that carry an expression:', len(measured), '| longest estimate:', measured[0][0] if measured else 0, '| limit:', LIMIT)
        self.assertTrue(all(m[0] <= LIMIT for m in measured))

    def test_the_measured_workflow_has_one_gated_job_per_condition(self):
        jobs = load(MEASURED)['jobs']
        seen = []
        for name, job in jobs.items():
            if name in ('gates', 'provenance'):
                continue
            self.assertEqual(job.get('needs'), ['gates', 'provenance'], name)
            cond = re.search(r"inputs\.condition == '([^']+)'", job['if'])
            self.assertIsNotNone(cond, name)
            self.assertEqual(job['env']['CONDITION_ID'], cond.group(1), name)
            self.assertEqual(job['env']['EXPECTED_IDENTITY_ORACLE'], 'item_identity', name)
            seen.append(cond.group(1))
        self.assertEqual(sorted(seen), sorted(CONDITION_IDS))

    def test_every_measured_job_refuses_a_re_run_and_writes_no_raw_data(self):
        for name, job in load(MEASURED)['jobs'].items():
            if name in ('gates', 'provenance'):
                continue
            text = json.dumps(job)
            self.assertIn('GATE_RUN_ATTEMPT', text, name)
            self.assertIn('E06-MEASURED_EXPERIMENT-${{ inputs.condition }}-provenance', text, f'{name}: it downloads the provenance record of its own condition')
            self.assertIn('test ! -e raw-data', text, name)  # the checkout holds no raw-data path
            self.assertNotIn('raw-data/E06', text, f'{name}: no output path under raw-data/')
            self.assertIn('"RECORD_CLASS": "MEASURED_EXPERIMENT"', text, name)

    def test_the_provenance_job_records_the_frozen_inputs_and_writes_no_raw_data(self):
        job = load(MEASURED)['jobs']['provenance']
        self.assertEqual(job['needs'], 'gates')
        self.assertIn("needs.gates.outputs.ready == 'true'", job['if'])
        text = json.dumps(job)
        self.assertNotIn('raw-data', text)
        for key in ('e06_configuration_sha256', 'conditions_file_sha256', 'run_manifest_schema_v2_sha256', 'executor_prompt_sha256',
                    'executor_implementation_sha256', 'agent_governance_v6_sha256', 'dispatch_authorization_sha256', 'timeout_policy', 'retry_policy',
                    'concurrency_policy', 'sut_version', 'environment_type', 'secrets'):
            self.assertIn(key, text, key)
        self.assertIn('E06-MEASURED_EXPERIMENT-${{ inputs.condition }}-provenance', text)
        # every output of the gate that the provenance reads is declared by the gates job
        declared = load(MEASURED)['jobs']['gates']['outputs']
        for used in re.findall(r'needs\.gates\.outputs\.([a-z0-9_]+)', text):
            self.assertIn(used, declared, used)

    def test_the_verification_workflow_is_non_measured_and_writes_no_raw_data(self):
        text = read_text(VERIFY)
        self.assertNotIn('MEASURED_EXPERIMENT', text)
        self.assertNotIn('raw-data/E06', text)
        self.assertIn('ENVIRONMENT_VERIFICATION', text)
        self.assertIn('DRY_RUN', text)

    def test_the_android_pins_equal_the_conditions_file(self):
        with open(CONDITIONS, encoding='utf-8') as f:
            cfg = json.load(f)
        pins = {c['condition_id']: c['apk'] for c in cfg['conditions'] if c['surface'] == 'ANDROID'}
        for path in WORKFLOWS:
            wf = load(path)
            for name, job in wf['jobs'].items():
                env = job.get('env') or {}
                if 'APK_SHA256' not in env:
                    continue
                cid = env['CONDITION_ID']
                self.assertEqual(env['APK_SHA256'], pins[cid]['sha256'], f'{os.path.basename(path)} {name}')
                self.assertEqual(env['APK_URL'], pins[cid].get('url') or self.url_of(cid), f'{os.path.basename(path)} {name}')

    def url_of(self, cid):
        return {'E06-CS007-SUT01-ANDROID': 'https://github.com/gsanchezm/OmniPizza/releases/download/v1.1.8/omnipizza-release.apk',
                'E06-CS007-SUT02-ANDROID': 'https://github.com/saucelabs/my-demo-app-android/releases/download/2.2.0/mda-2.2.0-25.apk'}[cid]

    def test_the_emulator_runner_is_the_pinned_commit(self):
        for path in WORKFLOWS:
            text = read_text(path)
            self.assertIn(RUNNER_ACTION, text, os.path.basename(path))
            self.assertIn('node-version: "22.23.2"', text, os.path.basename(path))
            # the Appium stack is the one of the SUT-01 smoke: npm ci from its lockfile, in its harness directory (no floating transitive tree)
            self.assertIn('npm ci --no-audit --no-fund', text, os.path.basename(path))
            self.assertIn('qualification/compatibility-smoke-sut01/harness/node_modules/.bin/appium', text, os.path.basename(path))
            self.assertNotIn('--no-package-lock', text, os.path.basename(path))
            self.assertIn('qualification/compatibility-smoke-sut01', text.split('E06_CHECKOUT_PATHS: |', 1)[1].split('jobs:', 1)[0], os.path.basename(path))

    def test_the_locked_appium_stack_pins_the_versions_of_the_smoke(self):
        lock = os.path.join(REPO, 'qualification', 'compatibility-smoke-sut01', 'harness', 'package-lock.json')
        with open(lock, encoding='utf-8') as f:
            packages = json.load(f)['packages']
        self.assertEqual(packages['node_modules/appium']['version'], '3.7.0')
        self.assertEqual(packages['node_modules/appium-uiautomator2-driver']['version'], '8.7.0')
        self.assertTrue(packages['node_modules/appium']['integrity'])
        self.assertFalse([k for k, v in packages.items() if k.endswith('node_modules/appium') and str(v.get('version', '')).startswith('2.')])

    def test_the_gate_script_compiles(self):
        with open(MEASURED, encoding='utf-8') as f:
            wf = yaml.safe_load(f)
        run = next(s['run'] for s in wf['jobs']['gates']['steps'] if s.get('id') == 'gates')
        lines = run.split('\n')
        body = '\n'.join(lines[lines.index("python3 - <<'PY'") + 1:lines.index('PY', lines.index("python3 - <<'PY'"))]) + '\n'
        tmp = tempfile.mkdtemp(prefix='e06-compile-')
        try:
            path = os.path.join(tmp, 'gate.py')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(body)
            py_compile.compile(path, doraise=True, cfile=os.path.join(tmp, 'gate.pyc'))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class ScriptTests(unittest.TestCase):
    def test_the_shell_scripts_parse(self):
        for name in ('run-condition.sh', 'android-job.sh'):
            proc = subprocess.run(['bash', '-n', os.path.join(EXEC, name)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_the_shell_scripts_hold_no_expression_of_the_workflows(self):
        for name in ('run-condition.sh', 'android-job.sh'):
            self.assertNotIn(OPENER, read_text(os.path.join(EXEC, name)), name)


class LintTests(unittest.TestCase):
    def binary(self, env_name, default):
        return os.environ.get(env_name) or shutil.which(default)

    def test_actionlint_with_shellcheck(self):
        actionlint = self.binary('ACTIONLINT', 'actionlint')
        shellcheck = self.binary('SHELLCHECK', 'shellcheck')
        if not actionlint or not shellcheck:
            self.skipTest('actionlint or shellcheck not available (set ACTIONLINT and SHELLCHECK)')
        proc = subprocess.run([actionlint, '-no-color', '-shellcheck', shellcheck] + WORKFLOWS, capture_output=True, text=True, timeout=300, cwd=REPO)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_shellcheck_on_the_scripts(self):
        shellcheck = self.binary('SHELLCHECK', 'shellcheck')
        if not shellcheck:
            self.skipTest('shellcheck not available (set SHELLCHECK)')
        scripts = [os.path.join(EXEC, 'run-condition.sh'), os.path.join(EXEC, 'android-job.sh')]
        proc = subprocess.run([shellcheck, '-x'] + scripts, capture_output=True, text=True, timeout=300)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class HygieneTests(unittest.TestCase):
    def test_no_attribution_or_session_identifier_in_a_new_non_test_file(self):
        patterns = [re.compile(re.escape(w), re.I) for w in FORBIDDEN]
        files = [p for p in glob.glob(os.path.join(EXEC, '**', '*'), recursive=True) if os.path.isfile(p)
                 and '__pycache__' not in p and os.sep + 'tests' + os.sep not in p]
        files += [os.path.join(REPO, '.github', 'workflows', os.path.basename(w)) for w in WORKFLOWS]
        files += [os.path.join(EXEC, '..', 'conditions-draft.json')]
        files += glob.glob(os.path.join(EXEC, '..', 'harness', '*.mjs')) + [os.path.join(EXEC, '..', 'harness', 'package.json')]
        hits = []
        for path in files:
            with open(path, encoding='utf-8', errors='replace') as fh:
                text = fh.read()
            for p in patterns:
                if p.search(text):
                    hits.append(os.path.relpath(path, REPO))
        self.assertEqual(sorted(set(hits)), [])

    def test_no_absolute_local_path_in_a_new_non_test_file(self):
        files = [p for p in glob.glob(os.path.join(EXEC, '**', '*'), recursive=True) if os.path.isfile(p)
                 and '__pycache__' not in p and os.sep + 'tests' + os.sep not in p]
        for path in files:
            with open(path, encoding='utf-8', errors='replace') as fh:
                text = fh.read()
            self.assertNotIn('/' + 'Users/', text, os.path.relpath(path, REPO))
            self.assertNotIn('/' + 'private/', text, os.path.relpath(path, REPO))


if __name__ == '__main__':
    unittest.main()
