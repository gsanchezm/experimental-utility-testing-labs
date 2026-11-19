"""E07-cross-layer-continuity executor: the conditions file, its validation, the classifier and the manifest outcome (operation OP-PREP-E07-04).

Static tests; nothing here contacts a SUT."""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

from executor import classify, config, sut01, sut04  # noqa: E402

CATEGORIES = ['VERIFIED', 'NOT_VERIFIED', 'ESTABLISHMENT_FAILED', 'INTERRUPTED', 'RUNNER_ERROR']
CAUSES = ['RESET_FAILED', 'STARTING_STATE_NOT_REACHED', 'WATCHDOG']
IDS = ['E07-CS005-SUT01-API-WEB', 'E07-CS005-SUT04-API-WEB', 'E07-CS006-SUT01-WEB-API', 'E07-CS006-SUT04-WEB-API']


class ConditionsFile(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_shape(self):
        self.assertEqual([c['condition_id'] for c in self.cfg['conditions']], IDS)
        self.assertEqual(self.cfg['success_category'], 'VERIFIED')
        self.assertEqual(self.cfg['categories'], CATEGORIES)
        self.assertEqual(self.cfg['interrupted_causes'], CAUSES)
        self.assertEqual(self.cfg['attribution_labels'], ['TOOLING', 'SUT'])
        self.assertEqual(self.cfg['n_per_condition'], 50)

    def test_each_condition_crosses_two_layers_in_the_direction_of_its_scenario(self):
        for c in self.cfg['conditions']:
            with self.subTest(c['condition_id']):
                expected = ('api', 'web') if c['canonical_scenario_id'] == 'CS-005' else ('web', 'api')
                self.assertEqual((c['source_layer'], c['verification_layer']), expected)
                self.assertEqual(c['expected_category'], 'VERIFIED')
                self.assertEqual(c['n'], 50)

    def test_the_four_conditions_are_sut01_and_sut04_in_both_directions(self):
        self.assertEqual({(c['sut_id'], c['canonical_scenario_id']) for c in self.cfg['conditions']},
                         {('SUT-01', 'CS-005'), ('SUT-01', 'CS-006'), ('SUT-04', 'CS-005'), ('SUT-04', 'CS-006')})
        self.assertEqual(set(self.cfg['no_condition']), {'SUT-02', 'SUT-03', 'SUT-05', 'SUT-06'})

    def test_the_identity_keys_of_the_file_are_the_keys_each_realization_compares(self):
        for mod in (sut01, sut04):
            for cid, cls in mod.REALIZATIONS.items():
                with self.subTest(cid):
                    self.assertEqual(list(config.condition(self.cfg, cid)['identity_keys']), list(cls.DECLARED_KEYS))
                    self.assertTrue(cls.KEYS)
                    self.assertTrue(set(cls.NOT_COMPARED) <= set(sut04.KEYS_API) | set(sut01.KEYS))


class Refusals(unittest.TestCase):
    def refused(self, mutate):
        cfg = copy.deepcopy(config.load())
        mutate(cfg)
        with self.assertRaises(config.ConfigError):
            config.validate(cfg)

    def test_duplicate_id(self):
        self.refused(lambda c: c['conditions'].append(copy.deepcopy(c['conditions'][0])))

    def test_sut_mismatch(self):
        self.refused(lambda c: c['conditions'][0].update(sut_id='SUT-04'))

    def test_scenario_mismatch(self):
        self.refused(lambda c: c['conditions'][0].update(canonical_scenario_id='CS-006'))

    def test_layers_that_do_not_follow_the_scenario(self):
        self.refused(lambda c: c['conditions'][0].update(source_layer='web', verification_layer='api'))

    def test_a_condition_that_does_not_cross_two_layers(self):
        self.refused(lambda c: c['conditions'][0].update(source_layer='web', verification_layer='web'))

    def test_expected_is_not_the_success_category(self):
        self.refused(lambda c: c['conditions'][0].update(expected_category='NOT_VERIFIED'))

    def test_identity_keys_not_declared(self):
        self.refused(lambda c: c['conditions'][0].update(identity_keys=[]))

    def test_n_differs(self):
        self.refused(lambda c: c['conditions'][0].update(n=49))

    def test_success_category_changed(self):
        self.refused(lambda c: c.update(success_category='SUCCESS'))

    def test_a_category_added_or_removed(self):
        self.refused(lambda c: c['categories'].append('STUB_NO_BUNDLE'))
        self.refused(lambda c: c['categories'].remove('RUNNER_ERROR'))

    def test_the_causes_changed(self):
        self.refused(lambda c: c['interrupted_causes'].append('OTHER'))

    def test_attribution_labels_changed(self):
        self.refused(lambda c: c.update(attribution_labels=['SUT']))

    def test_unknown_condition(self):
        with self.assertRaises(config.ConfigError):
            config.condition(config.load(), 'E07-CS005-SUT03-API-WEB')


class Classifier(unittest.TestCase):
    def setUp(self):
        self.c = config.condition(config.load(), IDS[0])

    def test_only_the_success_category_yields_status_success(self):
        self.assertEqual(classify.manifest_outcome(self.c, 'VERIFIED', 'x')['status'], 'SUCCESS')
        for label in CATEGORIES[1:]:
            with self.subTest(label):
                self.assertNotEqual(classify.manifest_outcome(self.c, label, None)['status'], 'SUCCESS')

    def test_the_status_of_each_category(self):
        self.assertEqual({label: classify.manifest_outcome(self.c, label, None)['status'] for label in CATEGORIES},
                         {'VERIFIED': 'SUCCESS', 'NOT_VERIFIED': 'FAILURE', 'ESTABLISHMENT_FAILED': 'ABORTED', 'INTERRUPTED': 'ABORTED', 'RUNNER_ERROR': 'ERROR'})

    def test_label_for_failure_of_a_recorded_failure(self):
        self.assertEqual(classify.label_for_failure('reset', False), ('INTERRUPTED', 'RESET_FAILED'))
        self.assertEqual(classify.label_for_failure('starting-state', False), ('INTERRUPTED', 'STARTING_STATE_NOT_REACHED'))
        self.assertEqual(classify.label_for_failure('establishment', False), ('ESTABLISHMENT_FAILED', None))
        self.assertEqual(classify.label_for_failure('establishment-check', False), ('ESTABLISHMENT_FAILED', None))
        self.assertEqual(classify.label_for_failure('verification', False), ('NOT_VERIFIED', None))

    def test_label_for_failure_of_an_exception_is_a_runner_error_in_every_block(self):
        for phase in ('reset', 'starting-state', 'establishment', 'establishment-check', 'verification'):
            with self.subTest(phase):
                self.assertEqual(classify.label_for_failure(phase, True), ('RUNNER_ERROR', None))

    def test_the_watchdog_is_an_interruption_in_every_block(self):
        for phase in ('reset', 'starting-state', 'establishment', 'establishment-check', 'verification'):
            with self.subTest(phase):
                self.assertEqual(classify.label_for_failure(phase, True, watchdog=True), ('INTERRUPTED', 'WATCHDOG'))

    def test_a_block_that_does_not_exist_is_refused(self):
        with self.assertRaises(ValueError):
            classify.label_for_failure('stimulus', False)

    def test_every_interruption_cause_is_declared(self):
        causes = {classify.label_for_failure(p, False)[1] for p in ('reset', 'starting-state')} | {classify.label_for_failure('reset', True, True)[1]}
        self.assertEqual(causes, set(CAUSES))

    def test_attribution_is_mechanical_and_uncertain_goes_to_sut(self):
        self.assertEqual(classify.attribution(True, False), 'TOOLING')
        self.assertEqual(classify.attribution(False, True), 'TOOLING')
        self.assertEqual(classify.attribution(False, False), 'SUT')

    def test_matches_expected_is_never_taken_from_the_observation(self):
        self.assertFalse(classify.manifest_outcome(self.c, 'NOT_VERIFIED', 'VERIFIED')['matches_expected'])
        self.assertTrue(classify.manifest_outcome(self.c, 'VERIFIED', None)['matches_expected'])

    def test_an_undeclared_label_is_refused(self):
        for label in ('TARGET_STATE_VERIFIED', 'STUB_NO_BUNDLE', 'S_ORDER_TOTAL_MATCH'):
            with self.subTest(label):
                with self.assertRaises(ValueError):
                    classify.manifest_outcome(self.c, label, None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
