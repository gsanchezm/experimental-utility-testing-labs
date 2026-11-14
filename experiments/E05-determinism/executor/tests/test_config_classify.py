"""Static tests of the conditions file and the pure classifier of the E05 executor (no SUT, no network). Run: python3 -m unittest discover -s tests"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from executor import classify, config  # noqa: E402


class ConditionsFile(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_shape(self):
        cs = self.cfg['conditions']
        self.assertEqual(len(cs), 14)
        by_sut = {}
        for c in cs:
            by_sut[c['sut_id']] = by_sut.get(c['sut_id'], 0) + 1
        self.assertEqual(by_sut, {'SUT-01': 7, 'SUT-02': 2, 'SUT-04': 3, 'SUT-05': 2})
        self.assertNotIn('SUT-03', by_sut)
        self.assertTrue(all(c['n'] == 50 for c in cs))

    def test_h3_label_is_five_deterministic_sut01_conditions(self):
        labeled = [c['condition_id'] for c in self.cfg['conditions'] if c['h3_labeled']]
        self.assertEqual(labeled, ['E05-SUT01-API-01', 'E05-SUT01-API-02', 'E05-SUT01-API-03', 'E05-SUT01-API-04', 'E05-SUT01-WEB-01'])

    def test_discriminant_control_is_stochastic_and_not_h3(self):
        c = config.condition(self.cfg, 'E05-SUT01-API-06')
        self.assertTrue(c['discriminant_control'])
        self.assertEqual(c['behavior_class'], 'stochastic')
        self.assertFalse(c['h3_labeled'])

    def test_known_gap_sut04_api_02_has_no_catch_all(self):
        # Recorded in the START package items: the condition declares no other-category (k = 4 without one).
        self.assertIsNone(config.catch_all(config.condition(self.cfg, 'E05-SUT04-API-02')))
        self.assertTrue(all(config.catch_all(c) for c in self.cfg['conditions'] if c['condition_id'] != 'E05-SUT04-API-02'))

    def test_unknown_condition(self):
        with self.assertRaises(config.ConfigError):
            config.condition(self.cfg, 'E05-SUT03-WEB-01')


class Refusals(unittest.TestCase):
    def mutate(self, fn):
        cfg = copy.deepcopy(config.load())
        fn(cfg)
        with self.assertRaises(config.ConfigError):
            config.validate(cfg)

    def test_k_mismatch(self):
        self.mutate(lambda c: c['conditions'][0].update(k=5))

    def test_expected_not_declared(self):
        self.mutate(lambda c: c['conditions'][0].update(expected_category='S_NOT_A_CATEGORY'))

    def test_expected_cannot_be_interrupted(self):
        self.mutate(lambda c: c['conditions'][0].update(expected_category='INTERRUPTED_'))

    def test_phase_prefix(self):
        self.mutate(lambda c: c['conditions'][0]['stimulus_categories'].__setitem__(0, 'X_ORDER_TOTAL_MATCH'))

    def test_duplicate_id(self):
        self.mutate(lambda c: c['conditions'][1].update(condition_id=c['conditions'][0]['condition_id']))

    def test_class_spelling(self):
        self.mutate(lambda c: c['conditions'][0].update(behavior_class='external-dependency'))

    def test_h3_label_outside_sut01(self):
        self.mutate(lambda c: config.condition(c, 'E05-SUT05-API-01').update(h3_labeled=True))

    def test_n_differs(self):
        self.mutate(lambda c: c['conditions'][0].update(n=30))

    def test_non_stimulus_category_inside_s(self):
        self.mutate(lambda c: c['non_stimulus_categories'].append('S_OOPS'))


class Classifier(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_phases(self):
        self.assertEqual([classify.phase(x) for x in ('S_BADGE_2', 'INTERRUPTED_', 'RESET_FAILED', 'ESTABLISHMENT_FAILED', 'STUB_NO_BUNDLE', 'WHATEVER')],
                         ['S', 'INTERRUPTED', 'RESET', 'ESTABLISHMENT', 'STUB', None])

    def test_membership_in_s(self):
        self.assertTrue(classify.in_s('S_BADGE_2'))
        self.assertTrue(classify.in_s('INTERRUPTED_'))
        for x in ('RESET_FAILED', 'ESTABLISHMENT_INTERRUPTED', 'STUB_NO_BUNDLE'):
            self.assertFalse(classify.in_s(x), x)

    def test_every_non_stimulus_label_is_outside_s(self):
        self.assertTrue(all(not classify.in_s(x) for x in self.cfg['non_stimulus_categories']))

    def test_declared_label_is_kept(self):
        c = config.condition(self.cfg, 'E05-SUT02-WEB-01')
        self.assertEqual(classify.finalize_label(self.cfg, c, 'S_BADGE_2'), ('S_BADGE_2', None))
        self.assertEqual(classify.finalize_label(self.cfg, c, 'ESTABLISHMENT_FAILED'), ('ESTABLISHMENT_FAILED', None))

    def test_undeclared_label_goes_to_the_catch_all_with_a_note(self):
        c = config.condition(self.cfg, 'E05-SUT02-WEB-01')
        label, note = classify.finalize_label(self.cfg, c, 'S_BADGE_3')
        self.assertEqual(label, 'S_BADGE_OTHER')
        self.assertIn('S_BADGE_3', note)

    def test_undeclared_label_without_catch_all_stays_visible(self):
        c = config.condition(self.cfg, 'E05-SUT04-API-02')
        label, note = classify.finalize_label(self.cfg, c, 'S_SOMETHING')
        self.assertEqual(label, 'S_SOMETHING')
        self.assertIn('no catch-all', note)

    def test_attribution_is_mechanical_and_uncertain_goes_to_sut(self):
        self.assertEqual(classify.attribution(True, False), 'TOOLING')
        self.assertEqual(classify.attribution(False, True), 'TOOLING')
        self.assertEqual(classify.attribution(False, False), 'SUT')

    def test_manifest_outcome(self):
        c = config.condition(self.cfg, 'E05-SUT05-API-01')
        ok = classify.manifest_outcome(self.cfg, c, 'S_REJECTED_AS_EXPECTED', 'HTTP 401')
        self.assertEqual((ok['status'], ok['matches_expected'], ok['outcome_category']), ('SUCCESS', True, 'S_REJECTED_AS_EXPECTED'))
        other = classify.manifest_outcome(self.cfg, c, 'S_OTHER', 'HTTP 500')
        self.assertEqual((other['status'], other['matches_expected']), ('SUCCESS', False))
        self.assertEqual(classify.manifest_outcome(self.cfg, c, 'INTERRUPTED_', 'x')['status'], 'ERROR')
        self.assertEqual(classify.manifest_outcome(self.cfg, c, 'RESET_FAILED', 'x')['status'], 'ABORTED')
        self.assertEqual(classify.manifest_outcome(self.cfg, c, 'ESTABLISHMENT_FAILED', 'x')['status'], 'ABORTED')
        self.assertEqual(classify.manifest_outcome(self.cfg, c, 'STUB_NO_BUNDLE', 'x')['status'], 'ERROR')

    def test_expected_is_never_taken_from_the_observation(self):
        c = config.condition(self.cfg, 'E05-SUT01-API-05')
        out = classify.manifest_outcome(self.cfg, c, 'S_MODE_WRONG_LANG', 'mode wrong_lang')
        self.assertEqual(out['expected'], 'S_MODE_MISSING_NAME')
        self.assertFalse(out['matches_expected'])


if __name__ == '__main__':
    unittest.main()
