"""The conditions file and its validation (operation OP-PREP-E08). Static tests."""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import config  # noqa: E402


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_the_four_conditions_and_n(self):
        self.assertEqual([c['condition_id'] for c in self.cfg['conditions']],
                         ['E08-SUT01-WEB-DELAY', 'E08-SUT02-WEB-BLOCK', 'E08-SUT03-WEB-LCP', 'E08-SUT03-WEB-CLS'])
        self.assertEqual(self.cfg['n_per_condition'], 50)
        self.assertEqual(sum(1 for c in self.cfg['conditions'] if c['h5_counted']), 4)

    def test_thresholds_are_the_expected_effect_minus_the_tolerance(self):
        for c in self.cfg['conditions']:
            if c['expected_effect'] is not None:
                self.assertEqual(c['rule']['threshold'], c['expected_effect'] - c['tolerance'], c['condition_id'])

    def test_load_order_rotates_over_the_absolute_index(self):
        orders = [config.order_for(self.cfg, i) for i in range(1, 7)]
        self.assertEqual(orders[:3], [('D', 'Ba', 'Bb'), ('Ba', 'D', 'Bb'), ('Ba', 'Bb', 'D')])
        self.assertEqual(orders[3:], orders[:3])
        counts = {pos: sum(1 for i in range(1, 51) if config.order_for(self.cfg, i).index('D') == pos) for pos in range(3)}
        self.assertEqual(sorted(counts.values()), [16, 17, 17])  # the degraded load takes every position in 50 executions

    def mutate(self, fn):
        cfg = copy.deepcopy(self.cfg)
        fn(cfg)
        with self.assertRaises(config.ConfigError):
            config.validate(cfg)

    def test_validation_refuses_inconsistent_files(self):
        self.mutate(lambda c: c['conditions'][0].update(condition_id='E08-SUT02-WEB-DELAY'))  # SUT does not match the id
        self.mutate(lambda c: c['conditions'][1].update(condition_id=c['conditions'][0]['condition_id']))  # duplicate
        self.mutate(lambda c: c['conditions'][0].update(surface='api'))
        self.mutate(lambda c: c['conditions'][0].update(metric='unknown'))
        self.mutate(lambda c: c['conditions'][0]['rule'].update(comparison='delta_lt'))
        self.mutate(lambda c: c['conditions'][0].update(expected_category='NOT_DETECTED'))
        self.mutate(lambda c: c['conditions'][0].update(behavior_class='sometimes'))
        self.mutate(lambda c: c['conditions'][0].update(required_ready=['nope']))
        self.mutate(lambda c: c['conditions'][2].update(external_dependency=None))
        self.mutate(lambda c: c['load_orders'].append(['Bb', 'Ba', 'D']))  # a later baseline listed before the earlier one
        self.mutate(lambda c: c.update(observe_window_ms=0))

    def test_unknown_condition(self):
        with self.assertRaises(config.ConfigError):
            config.condition(self.cfg, 'E08-SUT09-WEB-DELAY')


if __name__ == '__main__':
    unittest.main(verbosity=2)
