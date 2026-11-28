"""The detection rule, the false-positive record, the calibration rule, categories, attribution, and manifest outcome fields, on synthetic
captures and masks (operation OP-PREP-E10).

Static tests: no browser, no Node.js and no SUT. A capture record has the shape that executor/capture.py returns (keys: ready_ok,
missing_ready, timed_ok, elements); a comparison has the shape that executor/compare.py returns (width, height, compared, differing, ratio,
mask)."""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import classify, common, config  # noqa: E402

CFG = config.load()
W, H = 1280, 900
N = W * H
THR = {'T_R': 0.0005, 'T_e': 0.01, 'provisional': True, 'source': 'floors (no calibration record)'}


def cond(cid):
    return config.condition(CFG, cid)


def mask_of(rects, extra=0):
    """A mask with every pixel of the rectangles set, plus `extra` pixels at the end of the capture (outside any expected region)."""
    m = bytearray(N)
    for x0, y0, x1, y1 in rects:
        for y in range(y0, y1):
            m[y * W + x0:y * W + x1] = b'\x01' * (x1 - x0)
    if extra:
        m[N - extra:] = b'\x01' * extra
    return m


def cmp_of(mask, width=W, height=H):
    d = mask.count(1)
    return {'dimension_mismatch': False, 'width': width, 'height': height, 'compared': width * height, 'differing': d, 'ratio': d / (width * height),
            'mask': bytes(mask)}


def box(x, y, w, h):
    return {'x': x, 'y': y, 'w': w, 'h': h}


def img(loaded=True, host='upload.wikimedia.org'):
    return {'complete': True, 'natural_width': 500 if loaded else 0, 'natural_height': 500 if loaded else 0, 'host': host, 'src': 'https://' + host + '/x.jpg'}


def cap(groups, ready=True, missing=(), timed=None):
    """groups: {group: [(box, img or None), ...]}"""
    return {'ready_ok': ready, 'missing_ready': list(missing), 'timed_ok': timed,
            'elements': {'groups': {g: {'error': None, 'elements': [{'index': i, 'box': b, 'img': im} for i, (b, im) in enumerate(items)]} for g, items in groups.items()}}}


PRICES = [box(100, 300, 60, 20), box(400, 300, 60, 20)]
IMAGES = [box(80, 100, 200, 200), box(380, 100, 200, 200)]


def problem_cap(loaded=True, ready=True, image_a=True):
    return cap({'price': [(b, None) for b in PRICES], 'image': [(b, img(loaded)) for b in IMAGES]}, ready=ready)


def rects(*boxes):
    return [classify.box_to_rect(b, W, H) for b in boxes]


def view_data(c, ab, aa2, a=None, b=None, a2=None, view_index=0):
    return {'view': c['views'][view_index], 'captures': {'A': a or problem_cap(), 'B': b or problem_cap(), 'A2': a2 or problem_cap()},
            'AB': ab, 'AA2': aa2}


FULL = mask_of(rects(*PRICES, *IMAGES))


class GeometryTests(unittest.TestCase):
    def test_wholly_inside(self):
        self.assertTrue(classify.wholly_inside(box(0, 0, 1280, 900), W, H))
        self.assertTrue(classify.wholly_inside(box(10, 890, 20, 10), W, H))
        self.assertFalse(classify.wholly_inside(box(10, 891, 20, 10), W, H))
        self.assertFalse(classify.wholly_inside(box(-1, 5, 20, 10), W, H))
        self.assertTrue(classify.wholly_inside(box(40, 200, 700, 0), W, H))  # a zero-area box (a block of zero height) counts when its position is inside

    def test_box_to_rect_clips_and_drops_empty_boxes(self):
        self.assertEqual(classify.box_to_rect(box(10.2, 20.7, 30.1, 5.4), W, H), (10, 20, 41, 27))
        self.assertEqual(classify.box_to_rect(box(-5, -5, 20, 20), W, H), (0, 0, 15, 15))
        self.assertEqual(classify.box_to_rect(box(1270, 890, 50, 50), W, H), (1270, 890, 1280, 900))
        self.assertIsNone(classify.box_to_rect(box(40, 200, 700, 0), W, H))
        self.assertIsNone(classify.box_to_rect(None, W, H))

    def test_union_stats_counts_overlapping_rectangles_once(self):
        m = mask_of([(0, 0, 10, 10)])
        self.assertEqual(classify.union_stats(m, W, [(0, 0, 10, 10)]), (100, 100))
        self.assertEqual(classify.union_stats(m, W, [(0, 0, 10, 10), (5, 5, 15, 15)]), (100, 175))  # 100 + 100 - 25 pixels
        self.assertEqual(classify.union_stats(m, W, [(20, 20, 30, 30)]), (0, 100))


class RuleTests(unittest.TestCase):
    def setUp(self):
        self.c = cond('E10-SUT01-WEB-PROBLEM')

    def evaluate(self, ab_mask, aa2_mask=None, thr=THR, **kw):
        ab = cmp_of(ab_mask)
        aa2 = cmp_of(aa2_mask if aa2_mask is not None else bytearray(N))
        return classify.evaluate(self.c, CFG, thr, [view_data(self.c, ab, aa2, **kw)])

    def test_detected_when_every_expected_element_differs(self):
        label, d = self.evaluate(FULL)
        self.assertEqual(label, 'DETECTED')
        v = d['views'][0]
        self.assertEqual((v['detected'], v['false_positive'], d['detected'], d['baseline_false_positive']), (True, False, True, False))
        self.assertEqual(len(v['AB']['elements']), 4)
        self.assertTrue(all(e['detected'] and e['r'] == 1.0 for e in v['AB']['elements']))
        self.assertEqual(v['unlisted_diff_ratio'], 0.0)

    def test_the_whole_frame_clause_at_one_pixel_below_at_and_above_the_threshold(self):
        differing = FULL.count(1)
        thr = {**THR, 'T_R': differing / N}
        self.assertEqual(self.evaluate(FULL, thr=thr)[0], 'DETECTED')  # R equals T_R exactly
        self.assertEqual(self.evaluate(FULL, thr={**thr, 'T_R': (differing + 1) / N})[0], 'NOT_DETECTED')
        self.assertEqual(self.evaluate(FULL, thr={**thr, 'T_R': (differing - 1) / N})[0], 'DETECTED')

    def test_the_box_clause_at_one_pixel_below_at_and_above_the_threshold(self):
        # a price region is 60 x 20 = 1200 pixels: 12 differing pixels are exactly T_e = 0.01
        def with_price_pixels(n):
            m = mask_of(rects(PRICES[1], *IMAGES))
            for i in range(n):
                m[300 * W + 100 + i] = 1
            return m
        self.assertEqual(self.evaluate(with_price_pixels(12), thr={**THR, 'T_R': 0.0001})[0], 'DETECTED')
        label, d = self.evaluate(with_price_pixels(11), thr={**THR, 'T_R': 0.0001})
        self.assertEqual(label, 'NOT_DETECTED')
        self.assertEqual([e['detected'] for e in d['views'][0]['AB']['elements']].count(False), 1)

    def test_one_missing_element_fails_the_conjunction_even_when_the_frame_clause_holds(self):
        label, d = self.evaluate(mask_of(rects(PRICES[0], *IMAGES), extra=5000))  # the second price is untouched, many unlisted pixels
        self.assertEqual(label, 'NOT_DETECTED')
        self.assertGreater(d['views'][0]['unlisted_diff_ratio'], 0.004)
        self.assertGreaterEqual(d['views'][0]['R_AB'], THR['T_R'])

    def test_unlisted_differences_alone_are_never_a_detection(self):
        label, d = self.evaluate(mask_of([], extra=200000))
        self.assertEqual(label, 'NOT_DETECTED')
        self.assertTrue(d['views'][0]['AB']['whole_frame_clause'])
        self.assertAlmostEqual(d['views'][0]['unlisted_diff_ratio'], 200000 / N)

    def test_the_region_is_the_union_of_the_boxes_in_a_and_in_b(self):
        # an element that moved: its box in B differs from its box in A; a difference at either place counts
        c = cond('E10-SUT02-WEB-VISUAL')
        cart_a = box(1200, 10, 40, 40)
        cart_b = box(1000, 40, 40, 40)
        burger = box(20, 20, 30, 30)
        a = cap({'cart_icon_container': [(cart_a, None)], 'burger_icon': [(burger, None)]})
        b = cap({'cart_icon_container': [(cart_b, None)], 'burger_icon': [(burger, None)]})
        m = mask_of(rects(cart_a, cart_b, burger))
        ab = cmp_of(m)
        view = c['views'][0]
        res = classify.evaluate_view(c, CFG, THR, {'view': view, 'captures': {'A': a, 'B': b, 'A2': a}, 'AB': ab, 'AA2': cmp_of(bytearray(N))})
        self.assertEqual(res['status'], 'OK')
        cart = [e for e in res['AB']['elements'] if e['group'] == 'cart_icon_container'][0]
        self.assertEqual(cart['pixels'], 3200)  # 1600 + 1600, disjoint
        self.assertEqual(cart['r'], 1.0)
        only_b = cmp_of(mask_of(rects(cart_b, burger)))
        res = classify.evaluate_view(c, CFG, THR, {'view': view, 'captures': {'A': a, 'B': b, 'A2': a}, 'AB': only_b, 'AA2': cmp_of(bytearray(N))})
        cart = [e for e in res['AB']['elements'] if e['group'] == 'cart_icon_container'][0]
        self.assertEqual((cart['differing'], cart['pixels']), (1600, 3200))
        self.assertTrue(cart['detected'])  # half of the region differs, far above T_e

    def test_a_zero_area_box_in_a_contributes_nothing_and_the_region_is_the_box_in_b(self):
        c = cond('E10-SUT03-WEB-SHIFT')
        a = cap({'shift_target': [(box(40, 200, 700, 0), None)]})
        b = cap({'shift_target': [(box(40, 200, 700, 320), None)]})
        res = classify.evaluate_view(c, CFG, THR, {'view': c['views'][0], 'captures': {'A': a, 'B': b, 'A2': a},
                                                   'AB': cmp_of(mask_of([(40, 200, 740, 520)])), 'AA2': cmp_of(bytearray(N))})
        el = res['AB']['elements'][0]
        self.assertEqual((el['pixels'], el['r'], res['detected']), (700 * 320, 1.0, True))
        # absent from B and zero-area in A: an empty region cannot be detected
        gone = cap({'shift_target': []})
        res = classify.evaluate_view(c, CFG, THR, {'view': c['views'][0], 'captures': {'A': a, 'B': gone, 'A2': a},
                                                   'AB': cmp_of(mask_of([(40, 200, 740, 520)])), 'AA2': cmp_of(bytearray(N))})
        el = res['AB']['elements'][0]
        self.assertEqual((el['empty_region'], el['present_in_b'], el['detected'], res['detected']), (True, False, False, False))

    def test_elements_not_wholly_inside_the_viewport_in_a_are_not_considered(self):
        a = cap({'price': [(PRICES[0], None), (box(100, 890, 60, 30), None)], 'image': [(IMAGES[0], img())]})
        label, d = self.evaluate(mask_of(rects(PRICES[0], IMAGES[0])), a=a, b=a, a2=a)
        self.assertEqual(label, 'DETECTED')
        self.assertEqual(len(d['views'][0]['AB']['elements']), 2)

    def test_a_group_without_a_considered_element_is_inconclusive_never_not_detected(self):
        a = cap({'price': [(PRICES[0], None)], 'image': [(box(80, 790, 200, 200), img())]})
        label, d = self.evaluate(FULL, a=a, b=a, a2=a)
        self.assertEqual(label, 'INCONCLUSIVE_READY_SIGNAL_MISSING')
        self.assertEqual(d['views'][0]['groups_without_element'], ['image'])
        self.assertIsNone(d['detected'])


class FalsePositiveTests(unittest.TestCase):
    def setUp(self):
        self.c = cond('E10-SUT01-WEB-PROBLEM')

    def fp(self, differing):
        m = bytearray(N)
        for i in range(differing):
            m[i] = 1
        return classify.evaluate(self.c, CFG, THR, [view_data(self.c, cmp_of(FULL), cmp_of(m))])[1]

    def test_the_baseline_record_at_one_pixel_below_and_at_the_floor(self):
        self.assertFalse(self.fp(575)['baseline_false_positive'])  # 575 / 1152000 < 0.0005
        d = self.fp(576)  # 576 / 1152000 == 0.0005
        self.assertTrue(d['baseline_false_positive'])
        self.assertTrue(d['views'][0]['false_positive'])

    def test_the_box_clause_is_not_applied_but_the_boxes_ratios_are_recorded(self):
        d = self.fp(0)
        self.assertEqual(d['views'][0]['AA2']['elements'][0]['r'], 0.0)
        self.assertEqual(len(d['views'][0]['AA2']['elements']), 4)

    def test_the_record_is_kept_when_b_is_not_a_valid_measurement(self):
        c = self.c
        label, d = classify.evaluate(c, CFG, THR, [view_data(c, None, cmp_of(mask_of([(0, 0, 100, 100)])), b=problem_cap(ready=False))])
        self.assertEqual(label, 'INCONCLUSIVE_READY_SIGNAL_MISSING')
        self.assertTrue(d['baseline_false_positive'])

    def test_an_invalid_a2_removes_only_the_record(self):
        c = self.c
        label, d = classify.evaluate(c, CFG, THR, [view_data(c, cmp_of(FULL), None, a2=problem_cap(ready=False))])
        self.assertEqual(label, 'DETECTED')
        self.assertIsNone(d['baseline_false_positive'])

    def test_any_view_with_a_positive_record_makes_the_execution_record_true(self):
        c = cond('E10-SUT02-WEB-VISUAL')
        views = []
        for i, positives in enumerate((False, True, False)):
            v = c['views'][i]
            groups = {e['group']: [(box(100 + 100 * k, 100, 40, 40), None)] for k, e in enumerate(v['expected_elements'])}
            rect_list = [classify.box_to_rect(items[0][0], W, H) for items in groups.values()]
            views.append({'view': v, 'captures': {r: cap(groups) for r in ('A', 'B', 'A2')}, 'AB': cmp_of(mask_of(rect_list)),
                          'AA2': cmp_of(mask_of([(0, 0, 1000, 10)]) if positives else bytearray(N))})
        label, d = classify.evaluate(c, CFG, THR, views)
        self.assertEqual(label, 'DETECTED')
        self.assertEqual([v['false_positive'] for v in d['views']], [False, True, False])
        self.assertTrue(d['baseline_false_positive'])


class ViewsAndCategoriesTests(unittest.TestCase):
    def three_views(self, c, detect):
        views = []
        for i, v in enumerate(c['views']):
            groups = {e['group']: [(box(100 + 100 * k, 100, 40, 40), None)] for k, e in enumerate(v['expected_elements'])}
            rect_list = [classify.box_to_rect(items[0][0], W, H) for items in groups.values()]
            ab = mask_of(rect_list) if detect[i] else mask_of([], extra=0)
            views.append({'view': v, 'captures': {r: cap(groups) for r in ('A', 'B', 'A2')}, 'AB': cmp_of(ab), 'AA2': cmp_of(bytearray(N))})
        return views

    def test_the_execution_is_detected_only_when_every_view_is(self):
        c = cond('E10-SUT02-WEB-VISUAL')
        self.assertEqual(classify.evaluate(c, CFG, THR, self.three_views(c, (True, True, True)))[0], 'DETECTED')
        label, d = classify.evaluate(c, CFG, THR, self.three_views(c, (True, False, True)))
        self.assertEqual((label, [v['detected'] for v in d['views']]), ('NOT_DETECTED', [True, False, True]))

    def test_the_strongest_inconclusive_view_decides_the_label(self):
        c = cond('E10-SUT02-WEB-VISUAL')
        views = self.three_views(c, (True, True, True))
        views[1]['AB'] = {'dimension_mismatch': True, 'size_a': [1280, 900], 'size_b': [1280, 600]}
        label, d = classify.evaluate(c, CFG, THR, views)
        self.assertEqual(label, 'INCONCLUSIVE_CAPTURE_DIMENSION_MISMATCH')
        views[2]['captures']['B']['ready_ok'] = False
        views[2]['captures']['B']['missing_ready'] = ['close_icon']
        self.assertEqual(classify.evaluate(c, CFG, THR, views)[0], 'INCONCLUSIVE_READY_SIGNAL_MISSING')

    def test_a_capture_of_another_size_than_the_viewport_is_a_dimension_mismatch(self):
        c = cond('E10-SUT01-WEB-PROBLEM')
        small = cmp_of(bytearray(640 * 400), 640, 400)
        self.assertEqual(classify.evaluate(c, CFG, THR, [view_data(c, small, small)])[0], 'INCONCLUSIVE_CAPTURE_DIMENSION_MISMATCH')

    def test_a_capture_whose_layout_never_stopped_moving_is_inconclusive(self):
        c = cond('E10-SUT03-WEB-SHIFT')
        groups = {'shift_target': [(box(40, 200, 700, 320), None)]}
        caps = {'A': cap(groups, timed=True), 'B': cap(groups, timed=True), 'A2': cap(groups, timed=True)}
        v = {'view': c['views'][0], 'captures': caps, 'AB': cmp_of(mask_of([(40, 200, 740, 520)])), 'AA2': cmp_of(bytearray(N))}
        v['captures']['B']['settle'] = {'boxes_stable': False}
        label, d = classify.evaluate(c, CFG, THR, [v])
        self.assertEqual(label, 'INCONCLUSIVE_READY_SIGNAL_MISSING')
        self.assertIn('LAYOUT_NOT_STABLE', d['views'][0]['reasons'][0])
        # a capture that records no stability information is not refused (only an explicit False is)
        v['captures']['B']['settle'] = {'boxes_stable': True}
        self.assertEqual(classify.evaluate(c, CFG, THR, [v])[0], 'DETECTED')

    def test_a_timed_capture_taken_too_late_is_inconclusive(self):
        c = cond('E10-SUT03-WEB-SHIFT')
        groups = {'shift_target': [(box(40, 200, 700, 320), None)]}
        ok = {'A': cap(groups, timed=True), 'B': cap(groups, timed=True), 'A2': cap(groups, timed=True)}
        v = {'view': c['views'][0], 'captures': ok, 'AB': cmp_of(mask_of([(40, 200, 740, 520)])), 'AA2': cmp_of(bytearray(N))}
        self.assertEqual(classify.evaluate(c, CFG, THR, [v])[0], 'DETECTED')
        late = copy.deepcopy(v)
        late['captures']['A']['timed_ok'] = False
        label, d = classify.evaluate(c, CFG, THR, [late])
        self.assertEqual(label, 'INCONCLUSIVE_READY_SIGNAL_MISSING')
        self.assertIn('CAPTURE_TIME_MISSED', d['views'][0]['reasons'][0])
        # an untimed capture is never checked for timing
        untimed = copy.deepcopy(v)
        untimed['view'] = {**c['views'][0], 'capture_at_ms': None}
        untimed['captures']['A']['timed_ok'] = False
        self.assertEqual(classify.evaluate(c, CFG, THR, [untimed])[0], 'DETECTED')

    def test_the_thresholds_used_and_their_provisional_label_are_in_the_detail(self):
        c = cond('E10-SUT01-WEB-PROBLEM')
        label, d = classify.evaluate(c, CFG, {**THR, 'provisional': False, 'source': 'calibration record', 'T_R': 0.002}, [view_data(c, cmp_of(FULL), cmp_of(bytearray(N)))])
        self.assertEqual(d['thresholds'], {'T_R': 0.002, 'T_e': 0.01, 'provisional': False, 'source': 'calibration record'})
        self.assertEqual(d['views'][0]['AB']['T_R'], 0.002)


class ExternalImageTests(unittest.TestCase):
    def setUp(self):
        self.c = cond('E10-SUT01-WEB-PROBLEM')

    def evaluate(self, **caps):
        return classify.evaluate(self.c, CFG, THR, [view_data(self.c, cmp_of(FULL), cmp_of(bytearray(N)), **caps)])

    def test_a_baseline_image_that_did_not_load_is_inconclusive_with_attribution_external(self):
        label, d = self.evaluate(a=problem_cap(loaded=False), b=problem_cap(loaded=True))
        self.assertEqual(label, 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED')
        self.assertEqual(classify.attribution(False, label), 'EXTERNAL')
        self.assertEqual(classify.attribution(True, label), 'EXTERNAL')  # even an exception-free early phase flag cannot override the external label
        self.assertEqual(len(d['views'][0]['external_images_not_loaded']), 2)
        label, d = self.evaluate(a2=problem_cap(loaded=False))
        self.assertEqual(label, 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED')
        self.assertEqual(d['views'][0]['external_images_not_loaded'][0]['role'], 'A2')

    def test_the_state_of_the_images_of_b_is_recorded_and_never_a_validity_condition(self):
        label, d = self.evaluate(b=problem_cap(loaded=False))
        self.assertEqual(label, 'DETECTED')
        images_b = [e['img_b'] for e in d['views'][0]['AB']['elements'] if e['group'] == 'image']
        self.assertEqual(len(images_b), 2)
        self.assertTrue(all(i['natural_width'] == 0 for i in images_b))

    def test_a_page_without_content_is_ready_missing_before_it_is_an_image_question(self):
        label, _d = self.evaluate(a=problem_cap(loaded=False, ready=False))
        self.assertEqual(label, 'INCONCLUSIVE_READY_SIGNAL_MISSING')

    def test_an_image_that_is_not_complete_counts_as_not_loaded(self):
        a = problem_cap()
        a['elements']['groups']['image']['elements'][0]['img']['complete'] = False
        self.assertEqual(self.evaluate(a=a)[0], 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED')

    def test_a_condition_without_an_external_dependency_has_no_image_rule(self):
        c = cond('E10-SUT03-WEB-IMAGE')
        groups = {'thumbnail': [(box(100, 200, 200, 250), img(loaded=False))]}
        v = {'view': c['views'][0], 'captures': {r: cap(groups) for r in ('A', 'B', 'A2')}, 'AB': cmp_of(mask_of([(100, 200, 300, 450)])), 'AA2': cmp_of(bytearray(N))}
        self.assertEqual(classify.evaluate(c, CFG, THR, [v])[0], 'DETECTED')


class CalibrationTests(unittest.TestCase):
    FLOORS = CFG['rule']['floors']

    def test_all_zero_baselines_give_the_floors(self):
        out = classify.calibrate([{'R': 0.0, 'r': [0.0, 0.0]}, {'R': 0.0, 'r': [0.0]}], self.FLOORS, 2)
        self.assertEqual((out['T_R'], out['T_e'], out['n_pairs']), (0.0005, 0.01, 2))

    def test_the_factor_applies_to_the_largest_baseline_ratios(self):
        out = classify.calibrate([{'R': 0.0001, 'r': [0.003]}, {'R': 0.0012, 'r': [0.02, 0.004]}], self.FLOORS, 2)
        self.assertEqual((out['T_R'], out['T_e']), (0.0024, 0.04))
        self.assertEqual((out['max_R_AA2'], out['max_r_AA2']), (0.0012, 0.02))

    def test_a_baseline_below_half_the_floor_keeps_the_floor(self):
        out = classify.calibrate([{'R': 0.0002, 'r': [0.004]}], self.FLOORS, 2)
        self.assertEqual((out['T_R'], out['T_e']), (0.0005, 0.01))

    def test_no_pair_no_calibration(self):
        with self.assertRaises(ValueError):
            classify.calibrate([], self.FLOORS, 2)

    def test_a_pair_without_boxes_still_calibrates_the_frame_clause(self):
        out = classify.calibrate([{'R': 0.001, 'r': []}], self.FLOORS, 2)
        self.assertEqual((out['T_R'], out['T_e']), (0.002, 0.01))


class PhaseAndManifestTests(unittest.TestCase):
    def setUp(self):
        self.c = cond('E10-SUT01-WEB-PROBLEM')

    def test_phases_and_attribution(self):
        self.assertEqual([classify.phase(x) for x in ('DETECTED', 'NOT_DETECTED', 'START_SURFACE_NOT_READY', 'INCONCLUSIVE_CAPTURE_DIMENSION_MISMATCH',
                                                      'INTERRUPTED_', 'STUB_NO_BUNDLE')], ['METHOD', 'METHOD', 'START', 'METHOD', 'INTERRUPTED', 'STUB'])
        self.assertEqual(classify.attribution(True), 'TOOLING')
        self.assertEqual(classify.attribution(False), 'SUT')
        self.assertEqual(classify.attribution(True, 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED'), 'EXTERNAL')

    def test_manifest_outcome_status_and_match(self):
        for label, status, matches in (('DETECTED', 'SUCCESS', True), ('NOT_DETECTED', 'FAILURE', False), ('INCONCLUSIVE_READY_SIGNAL_MISSING', 'INCONCLUSIVE', None),
                                       ('INCONCLUSIVE_CAPTURE_DIMENSION_MISMATCH', 'INCONCLUSIVE', None), ('INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED', 'INCONCLUSIVE', None),
                                       ('START_ACTIVATION_NOT_CONFIRMED', 'ABORTED', None), ('INTERRUPTED_', 'ERROR', None), ('STUB_NO_BUNDLE', 'ERROR', None)):
            o = classify.manifest_outcome(CFG, self.c, label, 'x')
            self.assertEqual((o['status'], o['matches_expected'], o['outcome_category']), (status, matches, label))
            self.assertEqual(o['expected'], self.c['expected_text'])

    def test_every_category_of_the_executor_is_declared_and_an_undeclared_one_is_kept_with_a_note(self):
        declared = config.declared_categories(CFG)
        for label in classify.VIEW_LABEL.values():
            self.assertIn(label, declared)
        self.assertEqual(classify.finalize_label(CFG, self.c, 'DETECTED'), ('DETECTED', None))
        label, note = classify.finalize_label(CFG, self.c, 'NEW_LABEL')
        self.assertEqual(label, 'NEW_LABEL')
        self.assertIn('no catch-all', note)

    def test_failure_labels(self):
        self.assertEqual(classify.label_for_failure(common.PhaseFailure('starting-state', 'x', label='START_SURFACE_NOT_READY')), 'START_SURFACE_NOT_READY')
        self.assertEqual(classify.label_for_failure(common.PhaseFailure('method', 'x', interrupted=True)), 'INTERRUPTED_')

    def test_observed_text_names_the_thresholds_the_views_and_the_provisional_label(self):
        c = cond('E10-SUT01-WEB-PROBLEM')
        _label, d = classify.evaluate(c, CFG, THR, [view_data(c, cmp_of(FULL), cmp_of(bytearray(N)))])
        text = classify.observed_text(d)
        for part in ('T_R=0.0005', 'provisional', 'catalog:', 'detected=True', 'false_positive=False'):
            self.assertIn(part, text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
