"""Unit tests of executor/config.py: the conditions draft loads, and every inconsistency with the executor is refused.

DRAFT (operation OP-PREP-E06-EXECUTOR).
"""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))

from executor import config  # noqa: E402


def draft():
    return config.load()


class LoadTests(unittest.TestCase):
    def test_the_draft_holds_the_four_conditions_of_cs007(self):
        cfg = draft()
        self.assertEqual([c['condition_id'] for c in cfg['conditions']],
                         ['E06-CS007-SUT01-WEB', 'E06-CS007-SUT01-ANDROID', 'E06-CS007-SUT02-WEB', 'E06-CS007-SUT02-ANDROID'])
        self.assertEqual(config.planned_executions('MEASURED_EXPERIMENT', cfg), 50)
        self.assertEqual(config.planned_executions('DRY_RUN', cfg), 3)
        self.assertEqual(config.planned_executions('ENVIRONMENT_VERIFICATION', cfg), 1)

    def test_the_identity_switch_defaults_to_item_identity_on_every_condition(self):
        for c in draft()['conditions']:
            self.assertEqual(c['identity_oracle'], 'item_identity')

    def test_credentials_of_both_shapes(self):
        cfg = draft()
        web1 = config.condition(cfg, 'E06-CS007-SUT01-WEB')
        self.assertEqual(config.credentials(web1), ('standard_user', 'pizza123'))
        android2 = config.condition(cfg, 'E06-CS007-SUT02-ANDROID')
        self.assertEqual(config.credentials(android2), ('bod@example.com', '10203040'))

    def test_an_unknown_condition_is_refused(self):
        with self.assertRaises(config.ConfigError):
            config.condition(draft(), 'E06-CS007-SUT03-WEB')

    def test_an_unknown_record_class_is_refused(self):
        with self.assertRaises(config.ConfigError):
            config.planned_executions('LOCAL', draft())


class ValidationTests(unittest.TestCase):
    def mutated(self, fn):
        cfg = copy.deepcopy(draft())
        fn(cfg)
        return cfg

    def assertRefused(self, fn):
        with self.assertRaises(config.ConfigError):
            config.validate(self.mutated(fn))

    def test_n_must_be_fifty(self):
        self.assertRefused(lambda c: c.update(n_per_condition=49))

    def test_the_attempt_must_be_one(self):
        self.assertRefused(lambda c: c.update(attempt=2))

    def test_the_categories_are_fixed(self):
        self.assertRefused(lambda c: c['categories'].append('ARRIVED_WITH_SIGHS'))

    def test_the_reasons_are_fixed(self):
        self.assertRefused(lambda c: c['not_arrived_reasons']['NOT_ARRIVED_SUT'].append('SOMETHING_NEW'))

    def test_the_identity_switch_values_are_fixed(self):
        self.assertRefused(lambda c: c['identity_oracle_switch'].update(values=['item_identity']))

    def test_a_condition_cannot_name_another_sut_or_platform(self):
        self.assertRefused(lambda c: c['conditions'][0].update(sut_id='SUT-02'))
        self.assertRefused(lambda c: c['conditions'][0].update(platform='android'))

    def test_the_identity_key_follows_the_sut(self):
        self.assertRefused(lambda c: c['conditions'][0].update(identity_key='product_title'))

    def test_an_identity_oracle_outside_the_switch_is_refused(self):
        self.assertRefused(lambda c: c['conditions'][1].update(identity_oracle='screenshot'))

    def test_an_environment_type_outside_the_enum_is_refused(self):
        self.assertRefused(lambda c: c['conditions'][0].update(environment_type='CLOUD'))

    def test_an_android_condition_needs_a_sha256_pinned_apk(self):
        self.assertRefused(lambda c: c['conditions'][1]['apk'].update(sha256='abc'))

    def test_a_missing_account_is_refused(self):
        self.assertRefused(lambda c: c['conditions'][0].update(password=''))

    def test_the_conditions_must_be_exactly_four(self):
        self.assertRefused(lambda c: c.update(conditions=c['conditions'][:3]))

    def test_the_draft_file_on_disk_validates(self):
        with open(config.CONDITIONS_FILE, encoding='utf-8') as f:
            json.load(f)
        config.validate(draft())


if __name__ == '__main__':
    unittest.main()
