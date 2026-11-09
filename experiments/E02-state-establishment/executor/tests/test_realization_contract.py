"""Static contract of the E02 realizations (DRAFT, operation OP-PREP-E02).

The web realizations cannot run here (no SUT, no browser), so their declared counts are checked on the source: each counted
operation is a `with run.action(...)` statement; the test counts them per function, checks the action classes and the
establishment mechanisms against the run-manifest vocabulary, and checks the configuration of each condition (a realization
that is not configured, if one exists, must raise NotImplementedError and must be refused by run.py).

Run: python3 tests/test_realization_contract.py -v
"""
import ast
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXECUTOR_DIR = os.path.dirname(HERE)
PACKAGE = os.path.join(EXECUTOR_DIR, 'executor')
sys.path.insert(0, EXECUTOR_DIR)

from executor import run as runner  # noqa: E402

ACTION_CLASSES = {'API action', 'UI action', 'navigation action', 'state/configuration action', 'reset action', 'manual action'}
MECHANISM = re.compile(r'^(UI_FLOW|API_SEED|DIRECT_ROUTE|DEEP_LINK|FIXTURE|PREDEFINED_ACCOUNT|CONFIGURATION|APP_STATE_CONTROL|NONE)$|^OTHER: .+$')
MODALITIES = {'API', 'Web UI Functional'}
PLATFORMS = {'web', 'api'}

# counted operations per realization (declared in the executor README, section 4); None = not configured (raises)
EXPECTED_COUNTS = {
    ('sut01', 'cs003_api'): 3, ('sut01', 'cs003_web'): 6, ('sut01', 'cs004_web'): 2,
    ('sut02', 'cs003_web'): 6, ('sut02', 'cs004_web'): 4,
    ('sut03', 'cs003_web'): 7, ('sut03', 'cs004_web'): 2,
    ('sut04', 'cs003_api'): 3, ('sut04', 'cs003_web'): 13,
    ('sut05', 'cs003_api'): 3,
}
NOT_CONFIGURED = set()  # the CS-004 selectors of SUT-02 and SUT-03 were read from the pinned sources on 2026-11-06 (decisions-v3); a DRY_RUN verifies them


def counted_operations(module, function):
    """(class, mechanism, verification) for each `with run.action(...)` of the function, in source order."""
    with open(os.path.join(PACKAGE, module + '.py'), encoding='utf-8') as f:
        tree = ast.parse(f.read())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    out = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            call = item.context_expr
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'action' \
                    and isinstance(call.func.value, ast.Name) and call.func.value.id == 'run':
                args = [a.value for a in call.args if isinstance(a, ast.Constant)]
                mech = args[2] if len(args) > 2 else None
                verification = any(k.arg == 'verification' and isinstance(k.value, ast.Constant) and k.value.value is True for k in call.keywords)
                out.append((args[0] if args else None, mech, verification, node.lineno))
    out.sort(key=lambda x: x[3])
    return [(c, m, v) for c, m, v, _ in out]


def raises_not_implemented(module, function):
    with open(os.path.join(PACKAGE, module + '.py'), encoding='utf-8') as f:
        tree = ast.parse(f.read())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    return len(body) == 1 and isinstance(body[0], ast.Raise) and 'NotImplementedError' in ast.unparse(body[0])


def used_mechanisms(module, function):
    """Every mechanism named by a `run.action(...)` (third positional argument) or a `run.step(...)` (third positional argument or `mechanisms=`) of the function."""
    with open(os.path.join(PACKAGE, module + '.py'), encoding='utf-8') as f:
        tree = ast.parse(f.read())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    used = set()
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ('action', 'step')
                and isinstance(node.func.value, ast.Name) and node.func.value.id == 'run'):
            continue
        cand = [node.args[2]] if len(node.args) > 2 else []
        cand += [k.value for k in node.keywords if k.arg == 'mechanisms']
        for c in cand:
            if isinstance(c, ast.Constant) and isinstance(c.value, str):
                used.add(c.value)
            elif isinstance(c, ast.List):
                used.update(e.value for e in c.elts if isinstance(e, ast.Constant) and isinstance(e.value, str))
    return used


class RealizationContract(unittest.TestCase):
    def test_the_ten_conditions_map_to_realizations(self):
        self.assertEqual(len(runner.CONDITIONS), 10)
        for condition, (module, function) in runner.CONDITIONS.items():
            with self.subTest(condition=condition):
                mod = __import__(f'executor.{module}', fromlist=['SPEC'])
                self.assertIn(condition, mod.SPEC)
                self.assertTrue(callable(getattr(mod, function)))
                self.assertIn(f'{module}', ('sut01', 'sut02', 'sut03', 'sut04', 'sut05'))

    def test_declared_counts_match_the_source(self):
        for (module, function), expected in EXPECTED_COUNTS.items():
            with self.subTest(realization=f'{module}.{function}'):
                if expected is None:
                    self.assertTrue(raises_not_implemented(module, function), 'an unconfigured realization must raise')
                    continue
                ops = counted_operations(module, function)
                self.assertEqual(len(ops), expected, f'{module}.{function}: {len(ops)} counted operations, declared {expected}')

    def test_each_counted_operation_uses_the_vocabulary_and_the_verification_flag_is_explicit(self):
        for (module, function), expected in EXPECTED_COUNTS.items():
            if expected is None:
                continue
            ops = counted_operations(module, function)
            for cls, mech, verification in ops:
                with self.subTest(realization=f'{module}.{function}', cls=cls):
                    self.assertIn(cls, ACTION_CLASSES)
                    if mech is not None:
                        self.assertRegex(mech, MECHANISM)
            self.assertGreaterEqual(sum(1 for _, _, v in ops if v), 1, 'every realization ends with a verification operation')
            self.assertTrue(ops[-1][2], f'{module}.{function}: the last counted operation must be the verification (rule 8)')

    def test_specs_are_well_formed_and_configuration_is_explicit(self):
        for condition, (module, function) in runner.CONDITIONS.items():
            mod = __import__(f'executor.{module}', fromlist=['SPEC'])
            spec = mod.SPEC[condition]
            with self.subTest(condition=condition):
                self.assertIn(spec.modality, MODALITIES)
                self.assertIn(spec.platform, PLATFORMS)
                self.assertTrue(spec.mechanisms)
                for m in spec.mechanisms:
                    self.assertRegex(m, MECHANISM)
                self.assertTrue(spec.expected)
                self.assertEqual(spec.configured, condition not in NOT_CONFIGURED)
                self.assertTrue(callable(spec.components))

    def test_declared_mechanisms_cover_every_mechanism_the_realization_uses(self):
        """The run-level establishment_mechanisms of a condition must name every mechanism that its counted operations and its precondition steps use (OP-PREP-05: the first load was
        marked DIRECT_ROUTE for SUT-02 and SUT-03 but the declared list omitted it, unlike SUT-01 and SUT-04)."""
        for condition, (module, function) in runner.CONDITIONS.items():
            mod = __import__(f'executor.{module}', fromlist=['SPEC'])
            declared = set(mod.SPEC[condition].mechanisms)
            used = used_mechanisms(module, function)
            with self.subTest(condition=condition):
                self.assertTrue(used <= declared, f'{condition}: used {sorted(used)} but declared {sorted(declared)}')

    def test_every_condition_is_configured_and_no_realization_is_a_stub(self):
        self.assertEqual(NOT_CONFIGURED, set())
        for condition, (module, function) in runner.CONDITIONS.items():
            with self.subTest(condition=condition):
                self.assertFalse(raises_not_implemented(module, function))


if __name__ == '__main__':
    unittest.main()
