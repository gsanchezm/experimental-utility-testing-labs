"""E10-visual executor: the detection rule, the calibration rule, category phases, attribution labels, and the manifest outcome fields.

DRAFT (operation OP-PREP-E10). Pure functions; no SUT, no browser and no Node.js is contacted. The inputs are the capture records of
capture.py (boxes read from the DOM, image states) and the comparison results of compare.py (counts and the per-pixel mask), so that a reader
can recompute every ratio from the evidence files. The rule is read from conditions-draft.json (written before any DRY_RUN); nothing here is
tuned to an outcome, and no threshold is ever read from an A-against-B comparison.

The rule (campaign-configuration-draft.md, section 3). For a view: R is the number of differing pixels of A against B divided by the compared
pixels. An expected element is *considered* when its box is wholly inside the viewport in A; its region is the union of its box in A and its
box in B clipped to the capture, and r(e) is the differing pixels inside the region divided by the pixels of the region. The view is detected
when R >= T_R and r(e) >= T_e for every element considered; the execution is DETECTED when every view is detected. The baseline-against-
baseline (false-positive) record of a view is R of A against A2 >= T_R; the box clause is not applied to A against A2.

A label outside the declared categories is never mapped to another one; it is kept with a note so that the analysis fails closed on it.
Attribution is mechanical (E05 D-16): TOOLING when an exception happened before the first measured navigation was started, SUT otherwise and
when the cause cannot be assigned mechanically; EXTERNAL for the one category that names a third-party host (the images of SUT-01).
"""
import math

from . import config

PHASE_BY_PREFIX = (('START_', 'START'), ('INCONCLUSIVE_', 'METHOD'), ('INTERRUPTED_', 'INTERRUPTED'), ('STUB_', 'STUB'))
OUTCOME_STATUS = {'DETECTED': 'SUCCESS', 'NOT_DETECTED': 'FAILURE', 'START': 'ABORTED', 'METHOD': 'INCONCLUSIVE', 'INTERRUPTED': 'ERROR', 'STUB': 'ERROR'}
EXTERNAL_CATEGORIES = ('INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED',)
EPS = 0.01  # css pixels of tolerance when a box is tested against the viewport edge
# view statuses that make a view not a valid measurement, strongest first; the execution takes the strongest of its views
VIEW_PRIORITY = ('READY', 'DIMENSION', 'EXTERNAL', 'NO_ELEMENT')
VIEW_LABEL = {'READY': 'INCONCLUSIVE_READY_SIGNAL_MISSING', 'DIMENSION': 'INCONCLUSIVE_CAPTURE_DIMENSION_MISMATCH',
              'EXTERNAL': 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED', 'NO_ELEMENT': 'INCONCLUSIVE_READY_SIGNAL_MISSING'}


# ---- geometry on the pixel mask -----------------------------------------------------------------------------------------------------------
def wholly_inside(box, width, height):
    """The box (x, y, w, h in css pixels) lies wholly inside the capture. A box of zero area counts when its position is inside."""
    return (box['x'] >= -EPS and box['y'] >= -EPS and box['x'] + box['w'] <= width + EPS and box['y'] + box['h'] <= height + EPS)


def box_to_rect(box, width, height):
    """The box as an integer pixel rectangle (x0, y0, x1, y1) clipped to the capture, or None when it has no pixels."""
    if box is None:
        return None
    x0 = max(0, math.floor(box['x'] + EPS))
    y0 = max(0, math.floor(box['y'] + EPS))
    x1 = min(width, math.ceil(box['x'] + box['w'] - EPS))
    y1 = min(height, math.ceil(box['y'] + box['h'] - EPS))
    return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None


def union_stats(mask, width, rects):
    """(differing pixels, pixels) inside the union of the rectangles; mask is one byte per pixel, 1 = a counted difference."""
    rows = {}
    for x0, y0, x1, y1 in rects:
        for y in range(y0, y1):
            rows.setdefault(y, []).append((x0, x1))
    diff = area = 0
    for y, intervals in rows.items():
        intervals.sort()
        merged = []
        start, end = intervals[0]
        for s, e in intervals[1:]:
            if s <= end:
                end = max(end, e)
            else:
                merged.append((start, end))
                start, end = s, e
        merged.append((start, end))
        base = y * width
        for s, e in merged:
            area += e - s
            diff += mask.count(1, base + s, base + e)
    return diff, area


# ---- the rule for one view ---------------------------------------------------------------------------------------------------------------
def image_loaded(img):
    """An image counts as loaded when the browser reports it complete with a natural width above zero."""
    return bool(img) and bool(img.get('complete')) and (img.get('natural_width') or 0) > 0


def group_elements(cap, group):
    """The elements of one expected group in a capture record (capture.parse_elements: record['elements']['groups'][group]['elements'])."""
    return (((cap.get('elements') or {}).get('groups') or {}).get(group) or {}).get('elements') or []


def considered_elements(view, cap_a, cap_b, width, height):
    """For every expected group: the elements wholly inside the viewport in A, each with its A box, its B box (None when B lacks the element)."""
    out = {}
    for g in view['expected_elements']:
        a_group = group_elements(cap_a, g['group'])
        b_group = group_elements(cap_b, g['group'])
        b_by_index = {e['index']: e for e in b_group}
        items = []
        for e in a_group:
            if not wholly_inside(e['box'], width, height):
                continue
            eb = b_by_index.get(e['index'])
            items.append({'group': g['group'], 'index': e['index'], 'box_a': e['box'], 'box_b': eb['box'] if eb else None,
                          'img_a': e.get('img'), 'img_b': eb.get('img') if eb else None, 'present_in_b': eb is not None})
        out[g['group']] = items
    return out


def element_ratio(mask, width, height, item):
    rects = [r for r in (box_to_rect(item['box_a'], width, height), box_to_rect(item['box_b'], width, height)) if r]
    if not rects:
        return {'r': 0.0, 'differing': 0, 'pixels': 0, 'empty_region': True, 'rects': []}
    diff, area = union_stats(mask, width, rects)
    return {'r': diff / area, 'differing': diff, 'pixels': area, 'empty_region': False, 'rects': rects}


def _capture_valid(cap, view):
    """(valid, reason): the page showed its own content and a timed capture was taken in time."""
    if not cap.get('ready_ok'):
        return False, 'READY_SIGNAL_MISSING ' + ','.join(cap.get('missing_ready') or [])
    if view.get('capture_at_ms') and cap.get('timed_ok') is False:
        return False, 'CAPTURE_TIME_MISSED'
    if (cap.get('settle') or {}).get('boxes_stable') is False:
        return False, 'LAYOUT_NOT_STABLE'
    return True, None


def evaluate_view(c, cfg, thr, vd):
    """One view: status ('OK' or a VIEW_PRIORITY member), the detection, the false-positive record and every number behind them."""
    view = vd['view']
    caps = vd['captures']
    size = (cfg['capture']['viewport']['width'], cfg['capture']['viewport']['height'])
    res = {'view_id': view['view_id'], 'status': 'OK', 'reasons': [], 'R_AB': None, 'R_AA2': None, 'detected': None, 'false_positive': None,
           'unlisted_diff_ratio': None, 'AB': None, 'AA2': None, 'groups_without_element': [], 'external_images_not_loaded': []}
    validity = {role: _capture_valid(caps[role], view) for role in config.ROLES if role in caps}
    ab_ok = validity['A'][0] and validity['B'][0]
    aa2_ok = validity['A'][0] and 'A2' in validity and validity['A2'][0]
    for role in config.ROLES:
        if role in validity and not validity[role][0]:
            res['reasons'].append(f'{role}: {validity[role][1]}')
    # the false-positive record needs only A and A2 (it is recorded even when B is not a valid measurement)
    cmp_aa2 = vd.get('AA2')
    if aa2_ok and cmp_aa2 and not cmp_aa2.get('dimension_mismatch') and (cmp_aa2['width'], cmp_aa2['height']) == size:
        r_aa2 = cmp_aa2['ratio']
        res['R_AA2'] = r_aa2
        res['false_positive'] = r_aa2 >= thr['T_R']
        considered = considered_elements(view, caps['A'], caps['A2'], *size)
        res['AA2'] = {'pair': 'A against A2', 'width': cmp_aa2['width'], 'height': cmp_aa2['height'], 'compared': cmp_aa2['compared'],
                      'differing': cmp_aa2['differing'], 'ratio': r_aa2, 'T_R': thr['T_R'], 'false_positive': res['false_positive'],
                      'elements': [{'group': i['group'], 'index': i['index'], **{k: v for k, v in element_ratio(cmp_aa2['mask'], *size, i).items() if k != 'rects'}}
                                   for items in considered.values() for i in items]}
    cmp_ab = vd.get('AB')
    if not ab_ok:
        res['status'] = 'READY'
        return res
    if not cmp_ab or cmp_ab.get('dimension_mismatch') or (cmp_ab['width'], cmp_ab['height']) != size:
        res['status'] = 'DIMENSION'
        res['reasons'].append(f'capture size is not {size[0]}x{size[1]} for both A and B' + (f' ({cmp_ab.get("size_a")} against {cmp_ab.get("size_b")})' if cmp_ab and cmp_ab.get('dimension_mismatch') else ''))
        return res
    width, height = size
    considered = considered_elements(view, caps['A'], caps['B'], width, height)
    res['groups_without_element'] = [g for g, items in considered.items() if not items]
    # the external image rule: an expected image of State A (A, and A2 when it is a valid capture) that did not load makes the execution inconclusive
    ext = c.get('external_dependency')
    if ext:
        image_groups = {e['group'] for e in view['expected_elements'] if e.get('image')}
        for role in ('A', 'A2'):
            if role == 'A2' and not aa2_ok:
                continue
            for g in sorted(image_groups):
                present = {e['index']: e for e in group_elements(caps[role], g)}
                for i in considered[g]:
                    e = present.get(i['index'])
                    if e is None or not image_loaded(e.get('img')):
                        res['external_images_not_loaded'].append({'role': role, 'group': g, 'index': i['index'],
                                                                  'img': None if e is None else e.get('img')})
        if res['external_images_not_loaded']:
            res['status'] = 'EXTERNAL'
            return res
    if res['groups_without_element']:
        res['status'] = 'NO_ELEMENT'
        res['reasons'].append('no expected element wholly inside the viewport in A for: ' + ', '.join(res['groups_without_element']))
        return res
    mask = cmp_ab['mask']
    elements = []
    all_rects = []
    for g, items in considered.items():
        for i in items:
            ratio = element_ratio(mask, width, height, i)
            all_rects.extend(ratio['rects'])
            elements.append({'group': g, 'index': i['index'], 'box_a': i['box_a'], 'box_b': i['box_b'], 'present_in_b': i['present_in_b'],
                             'r': ratio['r'], 'differing': ratio['differing'], 'pixels': ratio['pixels'], 'empty_region': ratio['empty_region'],
                             'detected': ratio['r'] >= thr['T_e'], 'img_b': i['img_b'] if g in {e['group'] for e in view['expected_elements'] if e.get('image')} else None})
    inside, _area = union_stats(mask, width, all_rects) if all_rects else (0, 0)
    res['R_AB'] = cmp_ab['ratio']
    res['unlisted_diff_ratio'] = (cmp_ab['differing'] - inside) / cmp_ab['compared']
    res['detected'] = bool(res['R_AB'] >= thr['T_R'] and all(e['detected'] for e in elements))
    res['AB'] = {'pair': 'A against B', 'width': width, 'height': height, 'compared': cmp_ab['compared'], 'differing': cmp_ab['differing'], 'ratio': res['R_AB'],
                 'T_R': thr['T_R'], 'T_e': thr['T_e'], 'whole_frame_clause': res['R_AB'] >= thr['T_R'], 'detected': res['detected'], 'elements': elements,
                 'differing_outside_expected_regions': cmp_ab['differing'] - inside, 'unlisted_diff_ratio': res['unlisted_diff_ratio']}
    return res


def evaluate(c, cfg, thr, views):
    """Decide one execution from its views. views: a list of {'view': <view of the condition>, 'captures': {role: capture record}, 'AB': <comparison>, 'AA2': <comparison>}.

    Returns (label, detail). detail records the thresholds used (and whether they are provisional), every view's numbers, the execution's
    detection and baseline-against-baseline record. The false-positive record is kept even when the execution is inconclusive."""
    results = [evaluate_view(c, cfg, thr, vd) for vd in views]
    fps = [r['false_positive'] for r in results if r['false_positive'] is not None]
    detail = {'condition': c['condition_id'], 'rule': {k: cfg['rule'][k] for k in ('type', 'floors', 'calibration_factor')},
              'thresholds': {'T_R': thr['T_R'], 'T_e': thr['T_e'], 'provisional': thr['provisional'], 'source': thr['source']},
              'views': results, 'detected': None, 'baseline_false_positive': (any(fps) if fps else None)}
    statuses = [r['status'] for r in results if r['status'] != 'OK']
    if statuses:
        worst = next(s for s in VIEW_PRIORITY if s in statuses)
        return VIEW_LABEL[worst], detail
    detail['detected'] = all(r['detected'] for r in results)
    return ('DETECTED' if detail['detected'] else 'NOT_DETECTED'), detail


# ---- the calibration rule -------------------------------------------------------------------------------------------------------------------
def calibrate(pairs, floors, factor):
    """T_R = max(floor_R, factor x the largest R of A against A2) and T_e = max(floor_e, factor x the largest r(e) of A against A2), over the
    baseline-against-baseline pairs of the DRY_RUN rounds of one condition. `pairs` is a list of {'R': float, 'r': [floats]}; a comparison of
    A against B must never be passed. No pair, no calibration (ValueError): the rounds are then repeated, the rule is not adjusted."""
    if not pairs:
        raise ValueError('no baseline-against-baseline pair to calibrate from')
    max_r_whole = max(p['R'] for p in pairs)
    max_r_box = max((x for p in pairs for x in p['r']), default=0.0)
    return {'T_R': max(floors['T_R'], factor * max_r_whole), 'T_e': max(floors['T_e'], factor * max_r_box), 'n_pairs': len(pairs),
            'max_R_AA2': max_r_whole, 'max_r_AA2': max_r_box, 'floors': dict(floors), 'factor': factor}


# ---- phases, attribution, manifest fields -------------------------------------------------------------------------------------------
def phase(label):
    for prefix, name in PHASE_BY_PREFIX:
        if label.startswith(prefix):
            return name
    return 'METHOD'


def finalize_label(cfg, c, label):
    """Return (label, note). A declared label is returned as is; an undeclared one is returned unchanged with a note."""
    if label in config.declared_categories(cfg):
        return label, None
    return label, f'undeclared category {label!r}: {c["condition_id"]} has no catch-all category, the label is kept'


def label_for_failure(failure):
    """The category of an execution that stopped in a block before its classification: the pre-declared label of a recorded observation,
    or INTERRUPTED_ for an exception of the harness or of the client."""
    return failure.label or 'INTERRUPTED_'


def attribution(interruption_before_navigation, label=None):
    if label in EXTERNAL_CATEGORIES:
        return 'EXTERNAL'
    return 'TOOLING' if interruption_before_navigation else 'SUT'


def manifest_outcome(cfg, c, label, observed):
    """The run-manifest outcome object (schema v2). matches_expected compares the label with the condition's pre-declared expected
    category (DETECTED); NOT_DETECTED is a recorded FAILURE of the expectation, not an error."""
    status = OUTCOME_STATUS.get(label) or OUTCOME_STATUS[phase(label)]
    matches = None if status in ('INCONCLUSIVE', 'ABORTED', 'ERROR') else label == c['expected_category']
    return {'status': status, 'expected': c['expected_text'], 'observed': observed, 'outcome_category': label, 'matches_expected': matches}


def observed_text(detail):
    parts = []
    for v in detail['views']:
        r_ab = 'none' if v['R_AB'] is None else f'{v["R_AB"]:.6f}'
        r_aa = 'none' if v['R_AA2'] is None else f'{v["R_AA2"]:.6f}'
        lowest = min((e['r'] for e in (v.get('AB') or {}).get('elements', [])), default=None)
        parts.append(f'{v["view_id"]}: status={v["status"]}, R(A,B)={r_ab}, lowest r(e)={"none" if lowest is None else f"{lowest:.6f}"}, '
                     f'detected={v["detected"]}, R(A,A2)={r_aa}, false_positive={v["false_positive"]}')
    t = detail['thresholds']
    return (f'T_R={t["T_R"]}, T_e={t["T_e"]}{" (provisional: floors, no calibration record)" if t["provisional"] else ""}; ' + '; '.join(parts)
            + f'; detected={detail["detected"]}; baseline_false_positive={detail["baseline_false_positive"]}')
