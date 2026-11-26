"""Metrics, the detection rule, categories, attribution, and manifest outcome fields, on synthetic snapshots (operation OP-PREP-E08).

Static tests: no browser and no SUT. A snapshot has the shape that executor/probe.py returns (keys: supported, ready, lcp, cls, longtasks)."""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import classify, common, config  # noqa: E402

CFG = config.load()
SUPPORTED = ['largest-contentful-paint', 'layout-shift', 'longtask', 'paint']


def snap(ready=None, lcp=None, cls=None, longtasks=None, supported=SUPPORTED):
    return {'supported': list(supported), 'ready': dict(ready or {}), 'lcp': list(lcp or []), 'cls': list(cls or []), 'longtasks': list(longtasks or [])}


def shift(t, value, ids=(), recent=False):
    return {'start_time': t, 'value': value, 'had_recent_input': recent, 'sources': [{'node': f'div#{i}', 'node_id': i} for i in ids]}


def lcp_entry(t, url=''):
    return {'start_time': t, 'url': url, 'size': 1000, 'element': 'img' if url else 'p'}


def cond(cid):
    return config.condition(CFG, cid)


class MetricTests(unittest.TestCase):
    def test_first_item_present_and_missing(self):
        self.assertEqual(classify.first_item_ms(snap(ready={'first_item': 3150.5})), (3150.5, None))
        self.assertEqual(classify.first_item_ms(snap(ready={})), (None, 'READY_SIGNAL_MISSING'))
        self.assertEqual(classify.first_item_ms(snap(ready={'first_item': None})), (None, 'READY_SIGNAL_MISSING'))

    def test_longest_longtask(self):
        self.assertEqual(classify.longest_longtask_ms(snap(longtasks=[{'start_time': 1, 'duration': 80.0}, {'start_time': 9, 'duration': 5012.0}])), (5012.0, None))
        self.assertEqual(classify.longest_longtask_ms(snap()), (0.0, None))  # observed and none: zero
        self.assertEqual(classify.longest_longtask_ms(snap(supported=['paint'])), (None, 'METRIC_ABSENT'))

    def test_lcp_is_the_last_entry(self):
        self.assertEqual(classify.lcp_ms(snap(lcp=[lcp_entry(400), lcp_entry(3600, 'https://picsum.photos/1000/600'), lcp_entry(900)])), (3600, None))
        self.assertEqual(classify.lcp_ms(snap()), (None, 'METRIC_ABSENT'))
        self.assertEqual(classify.lcp_ms(snap(lcp=[lcp_entry(1)], supported=['paint'])), (None, 'METRIC_ABSENT'))

    def test_cls_session_windows(self):
        self.assertEqual(classify.cls_value(snap()), (0.0, None))
        self.assertEqual(classify.cls_value(snap(supported=['paint'])), (None, 'METRIC_ABSENT'))
        # two shifts in one window add up
        self.assertEqual(classify.cls_value(snap(cls=[shift(4000, 0.1), shift(4400, 0.05)])), (0.15, None))
        # a gap of more than 1 s starts a new window: the larger window is the value
        self.assertEqual(classify.cls_value(snap(cls=[shift(1000, 0.2), shift(3000, 0.05), shift(3100, 0.04)])), (0.2, None))
        # a shift with recent input never counts
        self.assertEqual(classify.cls_value(snap(cls=[shift(1000, 0.3, recent=True)])), (0.0, None))
        # a window ends at 5 s even without a gap
        entries = [shift(t, 0.01) for t in range(0, 6000, 500)]
        value, _ = classify.cls_value(snap(cls=entries))
        self.assertAlmostEqual(value, 0.10, places=6)  # the first window holds the entries at 0..4500 (ten), the second the entries from 5000

    def test_late_target_shift(self):
        s = snap(cls=[shift(3000, 0.1, ['target-text']), shift(4100, 0.1, ['other']), shift(4200, 0.1, ['target-text']), shift(4300, 0.1, ['target-text'], recent=True)])
        hits = classify.late_target_shift(s, 3500, 'target-text')
        self.assertEqual([h['start_time'] for h in hits], [4200])


class RuleTests(unittest.TestCase):
    def loads(self, d, ba, bb):
        return {'D': d, 'Ba': ba, 'Bb': bb}

    def test_delay_detected_not_detected_and_false_positive(self):
        c = cond('E08-SUT01-WEB-DELAY')
        ok = lambda t: snap(ready={'first_item': t})  # noqa: E731
        label, d = classify.evaluate(c, self.loads(ok(3600.0), ok(480.0), ok(510.0)))
        self.assertEqual((label, d['detected'], d['baseline_false_positive']), ('DETECTED', True, False))
        self.assertEqual(d['delta_D_minus_Ba'], 3120.0)
        # exactly the threshold counts (delta_ge)
        self.assertEqual(classify.evaluate(c, self.loads(ok(2980.0), ok(480.0), ok(480.0)))[0], 'DETECTED')
        self.assertEqual(classify.evaluate(c, self.loads(ok(2979.9), ok(480.0), ok(480.0)))[0], 'NOT_DETECTED')
        # baseline against baseline above the threshold is a false positive, recorded and not a detection
        label, d = classify.evaluate(c, self.loads(ok(480.0), ok(480.0), ok(3300.0)))
        self.assertEqual((label, d['baseline_false_positive']), ('NOT_DETECTED', True))

    def test_delay_inconclusive_when_the_ready_signal_is_missing(self):
        c = cond('E08-SUT01-WEB-DELAY')
        good = snap(ready={'first_item': 500.0})
        for loads in (self.loads(snap(), good, good), self.loads(good, snap(), good)):
            self.assertEqual(classify.evaluate(c, loads)[0], 'INCONCLUSIVE_READY_SIGNAL_MISSING')
        # the false-positive record needs only the two baselines: it is recorded when D is not a valid measurement and absent when Ba is not
        self.assertEqual(classify.evaluate(c, self.loads(snap(), good, good))[1]['baseline_false_positive'], False)
        self.assertEqual(classify.evaluate(c, self.loads(snap(), good, snap(ready={'first_item': 3500.0})))[1]['baseline_false_positive'], True)
        self.assertIsNone(classify.evaluate(c, self.loads(good, snap(), good))[1]['baseline_false_positive'])
        # a missing signal of the later baseline only removes the false-positive check: the detection is still decided
        label, d = classify.evaluate(c, self.loads(snap(ready={'first_item': 3600.0}), good, snap()))
        self.assertEqual((label, d['baseline_false_positive']), ('DETECTED', None))

    def test_block_rule(self):
        c = cond('E08-SUT02-WEB-BLOCK')
        mk = lambda dur: snap(ready={'inventory_list': 6000.0}, longtasks=[{'start_time': 100.0, 'duration': dur}] if dur else [])  # noqa: E731
        self.assertEqual(classify.evaluate(c, self.loads(mk(5100.0), mk(120.0), mk(90.0)))[0], 'DETECTED')
        self.assertEqual(classify.evaluate(c, self.loads(mk(4619.0), mk(120.0), mk(90.0)))[0], 'NOT_DETECTED')  # 4499 below 4500
        self.assertEqual(classify.evaluate(c, self.loads(mk(4620.0), mk(120.0), mk(90.0)))[0], 'DETECTED')
        # a page that never showed the inventory list is not a measurement
        no_list = snap(longtasks=[{'start_time': 1.0, 'duration': 10.0}])
        self.assertEqual(classify.evaluate(c, self.loads(no_list, mk(120.0), mk(90.0)))[0], 'INCONCLUSIVE_READY_SIGNAL_MISSING')
        self.assertEqual(classify.evaluate(c, self.loads(mk(5100.0), mk(120.0), snap()))[1]['baseline_false_positive'], None)

    def test_lcp_rule_and_the_external_image(self):
        c = cond('E08-SUT03-WEB-LCP')
        url = 'https://picsum.photos/1000/600'
        deg = lambda t: snap(ready={'content': 200.0}, lcp=[lcp_entry(300), lcp_entry(t, url)])  # noqa: E731
        base = lambda t: snap(ready={'content': 200.0}, lcp=[lcp_entry(t)])  # noqa: E731
        self.assertEqual(classify.evaluate(c, self.loads(deg(3900.0), base(350.0), base(360.0)))[0], 'DETECTED')
        # the image painted but not late enough: a recorded non-detection
        self.assertEqual(classify.evaluate(c, self.loads(deg(2000.0), base(350.0), base(360.0)))[0], 'NOT_DETECTED')
        # the image never painted: inconclusive, never a non-detection (the external host is outside the evaluated version)
        no_image = snap(ready={'content': 200.0}, lcp=[lcp_entry(300)])
        label, d = classify.evaluate(c, self.loads(no_image, base(350.0), base(360.0)))
        self.assertEqual(label, 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED')
        self.assertEqual(classify.attribution(False, label), 'EXTERNAL')
        # no LCP entry at all: the metric is absent
        self.assertEqual(classify.evaluate(c, self.loads(snap(ready={'content': 1.0}), base(350.0), base(360.0)))[0], 'INCONCLUSIVE_METRIC_ABSENT')

    def test_cls_rule_needs_a_late_shift_of_the_target(self):
        c = cond('E08-SUT03-WEB-CLS')
        ready = {'content': 200.0}
        base = snap(ready=ready)
        late = snap(ready=ready, cls=[shift(4000.0, 0.12, ['target-text'])])
        self.assertEqual(classify.evaluate(c, self.loads(late, base, base))[0], 'DETECTED')
        # the predicted outcome of the static reading: no shift at all
        self.assertEqual(classify.evaluate(c, self.loads(base, base, base))[0], 'NOT_DETECTED')
        # a shift of another element, or an early one, does not satisfy the rule
        other = snap(ready=ready, cls=[shift(4000.0, 0.12, ['other'])])
        early = snap(ready=ready, cls=[shift(1000.0, 0.12, ['target-text'])])
        self.assertEqual(classify.evaluate(c, self.loads(other, base, base))[0], 'NOT_DETECTED')
        self.assertEqual(classify.evaluate(c, self.loads(early, base, base))[0], 'NOT_DETECTED')
        # the baseline shifting is a false positive of the baseline against the baseline
        label, d = classify.evaluate(c, self.loads(late, base, snap(ready=ready, cls=[shift(100.0, 0.02)])))
        self.assertEqual((label, d['baseline_false_positive']), ('DETECTED', True))

    def test_evaluate_does_not_mutate_its_input(self):
        c = cond('E08-SUT01-WEB-DELAY')
        loads = self.loads(snap(ready={'first_item': 3600.0}), snap(ready={'first_item': 500.0}), snap(ready={'first_item': 510.0}))
        before = copy.deepcopy(loads)
        classify.evaluate(c, loads)
        self.assertEqual(loads, before)


class OutcomeTests(unittest.TestCase):
    def test_phase_attribution_and_manifest_outcome(self):
        c = cond('E08-SUT01-WEB-DELAY')
        cases = {'DETECTED': ('SUCCESS', True), 'NOT_DETECTED': ('FAILURE', False), 'INCONCLUSIVE_READY_SIGNAL_MISSING': ('INCONCLUSIVE', None),
                 'INCONCLUSIVE_METRIC_ABSENT': ('INCONCLUSIVE', None), 'START_SURFACE_NOT_READY': ('ABORTED', None),
                 'START_ACTIVATION_NOT_CONFIRMED': ('ABORTED', None), 'INTERRUPTED_': ('ERROR', None), 'STUB_NO_BUNDLE': ('ERROR', None)}
        for label, (status, matches) in cases.items():
            o = classify.manifest_outcome(CFG, c, label, 'text')
            self.assertEqual((o['status'], o['matches_expected'], o['outcome_category'], o['observed']), (status, matches, label, 'text'), label)
            self.assertEqual(o['expected'], c['expected_text'])
            self.assertEqual(set(o), {'status', 'expected', 'observed', 'matches_expected', 'outcome_category'})
        self.assertEqual(classify.attribution(True, 'INTERRUPTED_'), 'TOOLING')
        self.assertEqual(classify.attribution(False, 'INTERRUPTED_'), 'SUT')
        self.assertEqual(classify.attribution(False, 'DETECTED'), 'SUT')

    def test_failure_labels(self):
        self.assertEqual(classify.label_for_failure(common.PhaseFailure('method', 'x', interrupted=True)), 'INTERRUPTED_')
        self.assertEqual(classify.label_for_failure(common.PhaseFailure('starting-state', 'x', label='START_SURFACE_NOT_READY')), 'START_SURFACE_NOT_READY')

    def test_every_label_the_classifier_can_return_is_declared(self):
        declared = config.declared_categories(CFG)
        for label in ('DETECTED', 'NOT_DETECTED', 'INCONCLUSIVE_READY_SIGNAL_MISSING', 'INCONCLUSIVE_METRIC_ABSENT',
                      'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED', 'START_SURFACE_NOT_READY', 'START_ACTIVATION_NOT_CONFIRMED', 'INTERRUPTED_', 'STUB_NO_BUNDLE'):
            self.assertIn(label, declared)
        self.assertEqual(classify.finalize_label(CFG, cond('E08-SUT01-WEB-DELAY'), 'SOMETHING_ELSE')[0], 'SOMETHING_ELSE')
        self.assertIn('undeclared', classify.finalize_label(CFG, cond('E08-SUT01-WEB-DELAY'), 'SOMETHING_ELSE')[1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
