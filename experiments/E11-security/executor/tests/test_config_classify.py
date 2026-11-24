"""The cells file and the classifier (operation OP-PREP-E11). Static tests; nothing is contacted."""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import classify, config  # noqa: E402


class CellsFileTests(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_the_draft_has_the_fourteen_cells_and_700_executions(self):
        cells = self.cfg['cells']
        self.assertEqual(len(cells), 14)
        self.assertEqual(sum(c['n'] for c in cells), 700)
        self.assertEqual(sum(1 for c in cells if c['sut_id'] == 'SUT-01'), 2)
        self.assertEqual(sum(1 for c in cells if c['sut_id'] == 'SUT-05'), 12)
        self.assertEqual(sum(1 for c in cells if c['kind'] == 'CONTROL'), 7)

    def test_m2_exists_on_sut05_only_and_every_m2_condition_has_its_expectation(self):
        m2 = [c for c in self.cfg['cells'] if c['method'] == 'M2']
        self.assertEqual({c['sut_id'] for c in m2}, {'SUT-05'})
        for c in m2:
            self.assertIn(c['expected_m2_rule_id'], ('40018', '0'))
            if c['kind'] == 'CONDITION':
                self.assertTrue(c['expected_m2_target'])
            else:
                self.assertTrue(c['control_endpoint'])

    def test_expectations_follow_the_decision_e11_d_9(self):
        by = {c['cell_id']: c for c in self.cfg['cells']}
        self.assertEqual(by['E11-SUT05-SQLI-LOGIN-M2']['expected_m2_rule_id'], '40018')
        self.assertEqual(by['E11-SUT05-SQLI-SEARCH-M2']['expected_m2_rule_id'], '40018')
        self.assertEqual(by['E11-SUT05-DIRLIST-FTP-M2']['expected_m2_rule_id'], '0')
        self.assertNotIn('E11-SUT01-IDOR-ORDER-M2', by)
        mr = self.cfg['matching_rules']
        self.assertEqual(mr['expected_m2_path']['DIRLIST-FTP'], '/ftp/')
        self.assertEqual(mr['expected_m2_method']['SQLI-LOGIN'], 'POST')

    def test_control_cells_expect_the_negative_category_and_conditions_the_positive(self):
        for c in self.cfg['cells']:
            neg = c['expected_category'] in ('M1_ORACLE_NOT_FLIPPED', 'M1_IDOR_BLOCKED', 'M2_NO_EXPECTED_ALERT')
            self.assertEqual(neg, c['kind'] == 'CONTROL', c['cell_id'])

    def test_the_controls_of_m2_are_not_the_rate_limited_reset_password_endpoint(self):
        for c in self.cfg['cells']:
            if c['method'] == 'M2' and c['kind'] == 'CONTROL':
                self.assertNotIn('reset-password', c['control_endpoint'])

    def test_validation_refuses_inconsistent_cells(self):
        for mutate, fragment in (
                (lambda c: c['cells'][0].update(n=49), 'differs from the campaign n'),
                (lambda c: c['cells'][0].update(kind='CONTROL'), 'does not match the id'),
                (lambda c: c['cells'][0].update(expected_category='M1_ORACLE_NOT_FLIPPED'), 'is not a declared'),
                (lambda c: c['cells'].append(copy.deepcopy(c['cells'][0])), 'not a valid, unique cell id'),
                (lambda c: c['cells'][0].update(cell_id='E11-SUT01-OTHER-M1'), 'not a valid, unique cell id')):
            cfg = copy.deepcopy(self.cfg)
            mutate(cfg)
            with self.assertRaises(config.ConfigError) as cm:
                config.validate(cfg)
            self.assertIn(fragment, str(cm.exception))

    def test_m2_on_sut01_is_refused(self):
        cfg = copy.deepcopy(self.cfg)
        c = copy.deepcopy(next(x for x in cfg['cells'] if x['cell_id'] == 'E11-SUT05-SQLI-LOGIN-M2'))
        c.update(cell_id='E11-SUT01-SQLI-LOGIN-M2', sut_id='SUT-01')
        cfg['cells'].append(c)
        with self.assertRaises(config.ConfigError) as cm:
            config.validate(cfg)
        self.assertIn('M2 is configured on SUT-05 only', str(cm.exception))

    def test_an_unknown_cell_is_refused(self):
        with self.assertRaises(config.ConfigError):
            config.cell(self.cfg, 'E11-SUT05-NOPE-M1')


class ClassifierTests(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()
        self.cell = config.cell(self.cfg, 'E11-SUT05-SQLI-LOGIN-M1')

    def test_phases(self):
        for label, ph in (('M1_ORACLE_FLIPPED', 'M1'), ('M2_EXPECTED_ALERT', 'M2'), ('ZAP_SCAN_TIMEOUT', 'ZAP'), ('INTERRUPTED_', 'INTERRUPTED'),
                          ('RESET_FAILED', 'RESET'), ('STUB_NO_BUNDLE', 'STUB'), ('SOMETHING', None)):
            self.assertEqual(classify.phase(label), ph, label)

    def test_failure_labels(self):
        self.assertEqual(classify.label_for_failure('reset', True), 'RESET_FAILED')
        self.assertEqual(classify.label_for_failure('starting-state', False), 'RESET_STARTING_STATE_NOT_REACHED')
        self.assertEqual(classify.label_for_failure('method', True), 'INTERRUPTED_')
        self.assertEqual(classify.label_for_failure('classification', True), 'INTERRUPTED_')

    def test_attribution_is_mechanical(self):
        self.assertEqual(classify.attribution(True, False), 'TOOLING')
        self.assertEqual(classify.attribution(False, False), 'SUT')
        self.assertEqual(classify.attribution(False, True), 'TOOLING')
        self.assertEqual(classify.attribution(False, False, 'ZAP_API_ERROR'), 'TOOLING')
        self.assertEqual(classify.attribution(False, False, 'M2_NO_EXPECTED_ALERT'), 'SUT')

    def test_manifest_outcome_status_and_match(self):
        ok = classify.manifest_outcome(self.cfg, self.cell, 'M1_ORACLE_FLIPPED', 'x')
        self.assertEqual((ok['status'], ok['matches_expected'], ok['expected']), ('SUCCESS', True, 'M1_ORACLE_FLIPPED'))
        miss = classify.manifest_outcome(self.cfg, self.cell, 'M1_ORACLE_NOT_FLIPPED', 'x')
        self.assertEqual((miss['status'], miss['matches_expected']), ('SUCCESS', False))  # not detected is an observation, not an error
        self.assertEqual(classify.manifest_outcome(self.cfg, self.cell, 'ZAP_API_ERROR', None)['status'], 'ERROR')
        self.assertEqual(classify.manifest_outcome(self.cfg, self.cell, 'RESET_FAILED', None)['status'], 'ABORTED')
        self.assertEqual(classify.manifest_outcome(self.cfg, self.cell, 'INTERRUPTED_', None)['status'], 'ERROR')

    def test_an_undeclared_label_is_kept_with_a_note(self):
        label, note = classify.finalize_label(self.cfg, self.cell, 'M1_SURPRISE')
        self.assertEqual(label, 'M1_SURPRISE')
        self.assertIn('undeclared category', note)
        self.assertEqual(classify.finalize_label(self.cfg, self.cell, 'M1_RESPONSE_OTHER'), ('M1_RESPONSE_OTHER', None))


if __name__ == '__main__':
    unittest.main(verbosity=2)
