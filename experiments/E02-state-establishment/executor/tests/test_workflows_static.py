"""Static checks of the two E02 workflows (DRAFT, operation OP-PREP-E02).

- both files parse as YAML and are dispatch-only;
- every `inputs.<name>` reference names a declared workflow input;
- the OP-CI-15 length estimate (the algorithm of the validation workflow of the repository, step "Assert no string that carries an
  expression can exceed the expression length limit") is computed for every string that carries an expression, and every
  estimate is below 20000; the gate steps carry no expression in their scripts (the inputs reach them through step env).

Run: python3 tests/test_workflows_static.py -v   (PyYAML is read from the environment variable EUS_PYLIB when it is not importable)
"""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_DIR = os.path.dirname(HERE)
WORKFLOWS = os.path.abspath(os.path.join(EXECUTOR_DIR, '..', '..', '..', '.github', 'workflows'))
if os.environ.get('EUS_PYLIB'):
    sys.path.insert(0, os.environ['EUS_PYLIB'])
import yaml  # noqa: E402

FILES = ['e02-measured-execution.yml', 'e02-environment-verification.yml']
OPEN = '$' + '{' + '{'
LIMIT = 20000
ESTIMATES = []


def walk(obj, path, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, path + [str(k)], out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, path + [str(i)], out)
    elif isinstance(obj, str) and OPEN in obj:
        out.append((len(obj) + obj.count("'") + obj.count('{') + obj.count('}'), len(obj), '/'.join(path)))


def load(name):
    with open(os.path.join(WORKFLOWS, name), encoding='utf-8') as f:
        text = f.read()
    return text, yaml.safe_load(text)


class WorkflowStatic(unittest.TestCase):
    def test_parse_dispatch_only_and_declared_inputs(self):
        for name in FILES:
            with self.subTest(file=name):
                text, wf = load(name)
                on = wf.get(True, wf.get('on'))  # PyYAML reads the key `on` as a boolean
                self.assertEqual(list(on.keys()), ['workflow_dispatch'])
                declared = set(on['workflow_dispatch']['inputs'])
                used = set(re.findall(r'inputs\.([A-Za-z_][A-Za-z0-9_]*)', text))
                self.assertEqual(used - declared, set(), 'every inputs.<name> reference is declared')
                self.assertEqual(wf['permissions'], {'contents': 'read'})

    def test_op_ci_15_length_estimates_are_below_the_limit(self):
        for name in FILES:
            with self.subTest(file=name):
                _, wf = load(name)
                out = []
                walk(wf, [name], out)
                ESTIMATES.extend(out)
                for est, raw, where in out:
                    self.assertLess(est, LIMIT, f'{where}: estimate {est} (length {raw})')

    def test_gate_scripts_carry_no_expression(self):
        for name in FILES:
            with self.subTest(file=name):
                _, wf = load(name)
                for job, body in wf['jobs'].items():
                    for step in body.get('steps', []):
                        if step.get('id') == 'gates' or step.get('name', '').startswith(('Verify', 'Refuse', 'Assert')):
                            run = step.get('run', '')
                            self.assertNotIn(OPEN, run, f'{job}: {step.get("name")} carries an expression in its script')

    def test_inputs_reach_scripts_through_the_environment(self):
        for name in FILES:
            with self.subTest(file=name):
                _, wf = load(name)
                for job, body in wf['jobs'].items():
                    for step in body.get('steps', []):
                        run = step.get('run', '')
                        if 'inputs.' in run:
                            self.fail(f'{job}: {step.get("name")}: a workflow input is used inside a script (pass it through env)')

    def test_the_gate_step_is_the_only_gate_and_no_other_campaign_is_named(self):
        for name in FILES:
            with self.subTest(file=name):
                text, _ = load(name)
                self.assertNotIn('E03-CS001', text, 'no E03 condition id in an E02 workflow')
                self.assertNotIn('E03-resetability', text.replace('E03-resetability executor', ''), 'no E03 campaign path in an E02 workflow')

    @classmethod
    def tearDownClass(cls):
        if ESTIMATES:
            longest = max(ESTIMATES)
            print(f'\nOP-CI-15: {len(ESTIMATES)} strings that carry an expression; longest estimate {longest[0]} '
                  f'(length {longest[1]}) at {longest[2]}; limit {LIMIT}')


if __name__ == '__main__':
    unittest.main()
