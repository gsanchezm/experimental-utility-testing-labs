"""E04-repeatability executor: the conditions file, its validation, the classifier and the manifest outcome (operation OP-PREP-E04).

Static tests; nothing here contacts a SUT. The mirror check reads the E05 conditions file (read only)."""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

from executor import classify, config  # noqa: E402

E05_CONDITIONS = os.path.join(HERE, '..', '..', '..', 'E05-determinism', 'conditions-draft.json')
FAILURE = ['RESET_FAILED', 'RESET_STARTING_STATE_NOT_REACHED', 'ESTABLISHMENT_FAILED', 'ESTABLISHMENT_VERIFICATION_FAILED',
           'ESTABLISHMENT_INTERRUPTED', 'STUB_NO_BUNDLE']
PENDING = {'E04-SUT01-API-02', 'E04-SUT01-API-03', 'E04-SUT05-API-01', 'E04-SUT05-API-02', 'E04-SUT04-API-02'}


class ConditionsFile(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_shape(self):
        self.assertEqual(len(self.cfg['conditions']), 13)
        self.assertEqual(self.cfg['success_category'], 'TARGET_STATE_VERIFIED')
        self.assertEqual(self.cfg['failure_categories'], FAILURE)
        self.assertEqual(self.cfg['attribution_labels'], ['TOOLING', 'SUT'])
        self.assertEqual(self.cfg['n_per_condition'], 50)

    def test_each_condition_mirrors_the_e05_condition_of_the_same_sut_surface_account_and_reset(self):
        with open(E05_CONDITIONS, encoding='utf-8') as f:
            e05 = {c['condition_id']: c for c in json.load(f)['conditions']}
        self.assertEqual(len(e05), 13)
        for c in self.cfg['conditions']:
            with self.subTest(c['condition_id']):
                m = e05[c['mirrors']]
                self.assertEqual(c['condition_id'], 'E04' + c['mirrors'][3:])
                self.assertEqual((m['sut_id'], m['surface'], m['account'], m['reset_between_attempts']),
                                 (c['sut_id'], c['surface'], c['account'], c['reset_between_attempts']))

    def test_no_stimulus_or_classification_field_is_declared(self):
        for c in self.cfg['conditions']:
            for key in ('stimulus_categories', 'k', 'behavior_class', 'h3_labeled', 'client_timeout_s', 'expected_policy'):
                self.assertNotIn(key, c, c['condition_id'])
        for key in ('min_s_for_h3', 'wilson_z', 'schema_class_values'):
            self.assertNotIn(key, self.cfg)

    def test_every_expected_category_is_the_success_category(self):
        self.assertTrue(all(c['expected_category'] == 'TARGET_STATE_VERIFIED' and c['establishment_only'] is True for c in self.cfg['conditions']))

    def test_the_identical_conditions_and_the_message_baseline_are_pending(self):
        self.assertEqual({c['condition_id'] for c in self.cfg['conditions'] if c['pending']}, PENDING)


class Refusals(unittest.TestCase):
    def refused(self, mutate):
        cfg = copy.deepcopy(config.load())
        mutate(cfg)
        with self.assertRaises(config.ConfigError):
            config.validate(cfg)

    def test_duplicate_id(self):
        self.refused(lambda c: c['conditions'].append(copy.deepcopy(c['conditions'][0])))

    def test_sut_mismatch(self):
        self.refused(lambda c: c['conditions'][0].update(sut_id='SUT-02'))

    def test_surface_mismatch(self):
        self.refused(lambda c: c['conditions'][0].update(surface='web'))

    def test_expected_is_not_the_success_category(self):
        self.refused(lambda c: c['conditions'][0].update(expected_category='RESET_FAILED'))

    def test_a_condition_that_is_not_establishment_only(self):
        self.refused(lambda c: c['conditions'][0].update(establishment_only=False))

    def test_a_wrong_mirror(self):
        self.refused(lambda c: c['conditions'][0].update(mirrors='E05-SUT01-API-02'))

    def test_n_differs(self):
        self.refused(lambda c: c['conditions'][0].update(n=49))

    def test_success_prefix_changed(self):
        self.refused(lambda c: c['phase_prefixes'].update(success='S_'))

    def test_success_listed_as_a_failure(self):
        self.refused(lambda c: c['failure_categories'].append('TARGET_STATE_VERIFIED'))

    def test_failure_without_a_failure_prefix(self):
        self.refused(lambda c: c['failure_categories'].append('S_OTHER'))

    def test_unknown_condition(self):
        with self.assertRaises(config.ConfigError):
            config.condition(config.load(), 'E04-SUT03-WEB-01')


class Classifier(unittest.TestCase):
    def setUp(self):
        self.c = config.condition(config.load(), 'E04-SUT05-API-01')

    def test_phases(self):
        self.assertEqual(classify.phase('TARGET_STATE_VERIFIED'), 'VERIFIED')
        for label in FAILURE:
            self.assertIn(classify.phase(label), ('RESET', 'ESTABLISHMENT', 'STUB'), label)

    def test_only_the_success_category_yields_status_success(self):
        self.assertEqual(classify.manifest_outcome(self.c, 'TARGET_STATE_VERIFIED', 'x')['status'], 'SUCCESS')
        for label in FAILURE:
            with self.subTest(label):
                self.assertNotEqual(classify.manifest_outcome(self.c, label, None)['status'], 'SUCCESS')

    def test_failure_statuses(self):
        for label in FAILURE:
            status = classify.manifest_outcome(self.c, label, None)['status']
            self.assertEqual(status, 'ERROR' if label.startswith('STUB_') else 'ABORTED', label)

    def test_label_for_failure(self):
        self.assertEqual(classify.label_for_failure('reset', False), 'RESET_FAILED')
        self.assertEqual(classify.label_for_failure('reset', True), 'RESET_FAILED')
        self.assertEqual(classify.label_for_failure('starting-state', False), 'RESET_STARTING_STATE_NOT_REACHED')
        self.assertEqual(classify.label_for_failure('establishment', False), 'ESTABLISHMENT_FAILED')
        self.assertEqual(classify.label_for_failure('establishment', True), 'ESTABLISHMENT_INTERRUPTED')
        self.assertEqual(classify.label_for_failure('verification', False), 'ESTABLISHMENT_VERIFICATION_FAILED')
        self.assertEqual(classify.label_for_failure('verification', True), 'ESTABLISHMENT_INTERRUPTED')
        with self.assertRaises(ValueError):
            classify.label_for_failure('stimulus', False)

    def test_attribution_is_mechanical_and_uncertain_goes_to_sut(self):
        self.assertEqual(classify.attribution(True, False), 'TOOLING')
        self.assertEqual(classify.attribution(False, True), 'TOOLING')
        self.assertEqual(classify.attribution(False, False), 'SUT')

    def test_matches_expected_is_never_taken_from_the_observation(self):
        self.assertFalse(classify.manifest_outcome(self.c, 'RESET_FAILED', 'TARGET_STATE_VERIFIED')['matches_expected'])
        self.assertTrue(classify.manifest_outcome(self.c, 'TARGET_STATE_VERIFIED', None)['matches_expected'])

    def test_an_undeclared_label_is_refused(self):
        with self.assertRaises(ValueError):
            classify.manifest_outcome(self.c, 'S_ORDER_TOTAL_MATCH', None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
