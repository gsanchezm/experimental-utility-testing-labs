"""The conditions file and its validation (operation OP-PREP-E10). Static tests."""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import capture, compare, config  # noqa: E402


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_the_four_conditions_their_views_and_n(self):
        self.assertEqual([c['condition_id'] for c in self.cfg['conditions']],
                         ['E10-SUT01-WEB-PROBLEM', 'E10-SUT02-WEB-VISUAL', 'E10-SUT03-WEB-IMAGE', 'E10-SUT03-WEB-SHIFT'])
        self.assertEqual([[v['view_id'] for v in c['views']] for c in self.cfg['conditions']],
                         [['catalog'], ['inventory', 'cart', 'menu_open'], ['shelf'], ['high_cls']])
        self.assertEqual(self.cfg['n_per_condition'], 50)
        self.assertEqual(sum(1 for c in self.cfg['conditions'] if c['h5_counted']), 4)
        self.assertEqual(self.cfg['capture_order'], ['A', 'B', 'A2'])

    def test_the_capture_and_comparison_settings_agree_with_the_implementation(self):
        self.assertEqual(self.cfg['capture']['viewport'], capture.VIEWPORT)
        self.assertEqual(self.cfg['comparison']['options'], compare.PIXELMATCH_OPTIONS)
        self.assertEqual(self.cfg['comparison']['version'], compare.PIXELMATCH_VERSION)
        self.assertEqual(self.cfg['capture']['settle']['timeout_ms'], 20000)

    def test_the_conditions_file_carries_the_calibrated_thresholds_and_null_means_the_floors_provisionally(self):
        # the pair of every condition is the one of manifests/e10-calibration-v1.yaml (every baseline pair gave the floors)
        for c in self.cfg['conditions']:
            thr = config.thresholds(self.cfg, c)
            self.assertEqual(thr, {'T_R': 0.0005, 'T_e': 0.01, 'provisional': False, 'source': 'calibration record'}, c['condition_id'])
        nulled = copy.deepcopy(self.cfg)
        for c in nulled['conditions']:
            c['thresholds'] = {'T_R': None, 'T_e': None}
            thr = config.thresholds(nulled, c)
            self.assertTrue(thr['provisional'], c['condition_id'])
            self.assertEqual((thr['T_R'], thr['T_e']), (nulled['rule']['floors']['T_R'], nulled['rule']['floors']['T_e']))

    def test_a_per_condition_pair_is_used_and_null_means_floors(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['conditions'][0]['thresholds'] = {'T_R': 0.003, 'T_e': 0.05}
        cfg['conditions'][1]['thresholds'] = {'T_R': None, 'T_e': None}
        config.validate(cfg)
        self.assertEqual(config.thresholds(cfg, cfg['conditions'][0]), {'T_R': 0.003, 'T_e': 0.05, 'provisional': False, 'source': 'calibration record'})
        other = config.thresholds(cfg, cfg['conditions'][1])
        self.assertTrue(other['provisional'])
        self.assertEqual((other['T_R'], other['T_e']), (cfg['rule']['floors']['T_R'], cfg['rule']['floors']['T_e']))

    def test_a_campaign_level_pair_is_refused(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['rule']['thresholds'] = {'T_R': 0.001, 'T_e': 0.02}
        with self.assertRaises(config.ConfigError):
            config.validate(cfg)

    def mutate(self, fn):
        cfg = copy.deepcopy(self.cfg)
        fn(cfg)
        with self.assertRaises(config.ConfigError):
            config.validate(cfg)

    def test_validation_refuses_inconsistent_files(self):
        self.mutate(lambda c: c['conditions'][0].update(condition_id='E10-SUT02-WEB-PROBLEM'))  # SUT does not match the id
        self.mutate(lambda c: c['conditions'][1].update(condition_id=c['conditions'][0]['condition_id']))  # duplicate
        self.mutate(lambda c: c['conditions'][0].update(surface='api'))
        self.mutate(lambda c: c['conditions'][0].update(expected_category='NOT_DETECTED'))
        self.mutate(lambda c: c['conditions'][0].update(behavior_class='sometimes'))
        self.mutate(lambda c: c['conditions'][0].update(external_dependency=None))  # an external-dependency condition names its hosts
        self.mutate(lambda c: c['conditions'][1].update(external_dependency={'hosts': ['x'], 'category_when_baseline_image_not_loaded': 'DETECTED'}))
        self.mutate(lambda c: c['conditions'][0]['views'][0]['expected_elements'][1].pop('image'))  # no group flagged image
        self.mutate(lambda c: c['conditions'][0].update(state_a={}))
        self.mutate(lambda c: c['conditions'][0].update(views=[]))
        self.mutate(lambda c: c['conditions'][1]['views'][1].update(view_id='inventory'))  # duplicate view id
        self.mutate(lambda c: c['conditions'][0]['views'][0].update(route='catalog'))
        self.mutate(lambda c: c['conditions'][1]['views'][2]['steps'][0].update(action='hover'))
        self.mutate(lambda c: c['conditions'][1]['views'][2]['steps'][0].pop('selector'))
        self.mutate(lambda c: c['conditions'][0]['views'][0].update(required_ready=['nope']))
        self.mutate(lambda c: c['conditions'][0]['views'][0].update(ready_timeout_ms=0))
        self.mutate(lambda c: c['conditions'][3]['views'][0]['capture_at_ms'].pop('A2'))
        self.mutate(lambda c: c['conditions'][0]['views'][0].update(expected_elements=[]))
        self.mutate(lambda c: c['conditions'][0]['views'][0]['expected_elements'][1].update(group='price'))  # duplicate group
        self.mutate(lambda c: c.update(capture_order=['A', 'A2', 'B']))
        self.mutate(lambda c: c['capture']['viewport'].update(width=0))
        self.mutate(lambda c: c['capture'].update(device_scale_factor=2))
        self.mutate(lambda c: c['capture'].update(scroll_position=100))
        self.mutate(lambda c: c['comparison']['options'].update(extra=1))
        self.mutate(lambda c: c['comparison']['options'].update(threshold=2))
        self.mutate(lambda c: c['comparison'].update(tool='other'))
        self.mutate(lambda c: c['rule']['floors'].update(T_R=0))
        self.mutate(lambda c: c['rule'].update(calibration_factor=0))
        self.mutate(lambda c: c['rule'].update(type='ratio'))
        self.mutate(lambda c: c['rule'].update(thresholds={'T_R': 0.001, 'T_e': None}))  # one of the pair null
        self.mutate(lambda c: c['rule'].update(thresholds={'T_R': 0.001}))
        self.mutate(lambda c: c['conditions'][0].update(thresholds={'T_R': -1, 'T_e': 0.1}))

    def test_unknown_condition(self):
        with self.assertRaises(config.ConfigError):
            config.condition(self.cfg, 'E10-SUT09-WEB-IMAGE')


if __name__ == '__main__':
    unittest.main(verbosity=2)
