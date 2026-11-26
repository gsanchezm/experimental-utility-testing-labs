"""E08-performance executor: metrics, the detection rule, category phases, attribution labels, and the manifest outcome fields.

DRAFT (operation OP-PREP-E08). Pure functions; no SUT and no browser is contacted. The metrics are computed from the raw snapshot of the
in-page script (probe.py) so that a reader can recompute them from the evidence file. The rule of each condition is read from
conditions-draft.json (written before any DRY_RUN); nothing here is tuned to an outcome.

A label outside the declared categories is never mapped to another one; it is kept with a note so that the analysis fails closed on it.
Attribution is mechanical (E05 D-16): TOOLING when an exception happened before the first measured navigation was started, SUT otherwise
and when the cause cannot be assigned mechanically; EXTERNAL for the one category that names a third-party host (the delayed image of the
LCP condition).
"""
from . import config

PHASE_BY_PREFIX = (('START_', 'START'), ('INCONCLUSIVE_', 'METHOD'), ('INTERRUPTED_', 'INTERRUPTED'), ('STUB_', 'STUB'))
OUTCOME_STATUS = {'DETECTED': 'SUCCESS', 'NOT_DETECTED': 'FAILURE', 'START': 'ABORTED', 'METHOD': 'INCONCLUSIVE', 'INTERRUPTED': 'ERROR', 'STUB': 'ERROR'}
EXTERNAL_CATEGORIES = ('INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED',)
CLS_WINDOW_GAP_MS = 1000
CLS_WINDOW_MAX_MS = 5000


# ---- metrics (each returns (value, absent_reason); a value of None means the metric could not be observed) ---------------------------
def first_item_ms(snap):
    v = (snap.get('ready') or {}).get('first_item')
    return (v, None) if isinstance(v, (int, float)) else (None, 'READY_SIGNAL_MISSING')


def longest_longtask_ms(snap):
    if 'longtask' not in (snap.get('supported') or []):
        return None, 'METRIC_ABSENT'
    tasks = snap.get('longtasks') or []
    return (max((t['duration'] for t in tasks), default=0.0), None)


def lcp_ms(snap):
    entries = snap.get('lcp') or []
    if 'largest-contentful-paint' not in (snap.get('supported') or []) or not entries:
        return None, 'METRIC_ABSENT'
    return max(entries, key=lambda e: e['start_time'])['start_time'], None


def cls_value(snap):
    """Cumulative Layout Shift as defined by web.dev: the largest sum of the shifts without recent input over session windows (a window
    ends after a gap of 1 s or when it reaches 5 s). A page with the API and no shift records 0.0."""
    if 'layout-shift' not in (snap.get('supported') or []):
        return None, 'METRIC_ABSENT'
    best, cur, first_t, last_t = 0.0, 0.0, None, None
    for e in sorted((x for x in (snap.get('cls') or []) if not x.get('had_recent_input')), key=lambda x: x['start_time']):
        t = e['start_time']
        if first_t is not None and (t - last_t > CLS_WINDOW_GAP_MS or t - first_t >= CLS_WINDOW_MAX_MS):
            cur, first_t = 0.0, None
        if first_t is None:
            first_t = t
        cur += e['value']
        last_t = t
        best = max(best, cur)
    return round(best, 6), None


METRIC_FUNCTIONS = {'first_item_ms': first_item_ms, 'longest_longtask_ms': longest_longtask_ms, 'lcp_ms': lcp_ms, 'cls': cls_value}


def metric(c, snap):
    return METRIC_FUNCTIONS[c['metric']](snap)


def late_target_shift(snap, min_start_ms, target_element_id):
    """The shift entries (no recent input) at or after min_start_ms whose sources include the element with the given id."""
    return [e for e in (snap.get('cls') or []) if not e.get('had_recent_input') and e['start_time'] >= min_start_ms
            and any(s.get('node_id') == target_element_id for s in (e.get('sources') or []))]


# ---- the rule ------------------------------------------------------------------------------------------------------------------------
def compare(rule, later, earlier):
    """The comparison of the rule on the difference later - earlier."""
    d = later - earlier
    return d >= rule['threshold'] if rule['comparison'] == 'delta_ge' else d > rule['threshold']


def external_image_loaded(c, snap):
    """LCP condition only: True when the delayed image of the external host was painted as a largest-paint candidate; False when it was not
    (its request failed, was not made, or never painted); None for a condition without an external dependency. The host is matched as a
    substring of the entry's url, so a redirect to a subdomain of the same host is still the image (the literal url is kept in the evidence)."""
    ext = c.get('external_dependency')
    if not ext:
        return None
    return any(ext['url_contains'] in (e.get('url') or '') for e in (snap.get('lcp') or []))


def evaluate(c, loads):
    """Decide one execution from its three load snapshots. loads maps the role (D, Ba, Bb) to the snapshot of the load.

    Returns (label, detail). detail records the three metric values, the difference, the rule results, the false-positive record of the
    baseline against the baseline (it needs only the two baselines, so it is recorded even when D is not a valid measurement), and the
    reasons; every number is in the unit of the metric."""
    rule = c['rule']
    values, reasons = {}, {}
    for role in config.ROLES:
        values[role], reasons[role] = metric(c, loads[role])
    # the page under test must have shown its own content in the load (required_ready); a login page or an error page is not a measurement
    missing = {role: [k for k in c['required_ready'] if not isinstance((loads[role].get('ready') or {}).get(k), (int, float))] for role in config.ROLES}
    valid = {role: values[role] is not None and not missing[role] for role in config.ROLES}
    absent = {role: reasons[role] for role in config.ROLES if reasons[role]}
    absent.update({role: 'READY_SIGNAL_MISSING ' + ','.join(m) for role, m in missing.items() if m})
    detail = {'metric': c['metric'], 'unit': c['unit'], 'values': values, 'absent_reasons': absent, 'rule': rule, 'delta_D_minus_Ba': None,
              'delta_Bb_minus_Ba': None, 'detected': None, 'baseline_false_positive': None}
    if valid['Ba'] and valid['Bb']:
        detail['delta_Bb_minus_Ba'] = round(values['Bb'] - values['Ba'], 6)
        detail['baseline_false_positive'] = compare(rule, values['Bb'], values['Ba'])
    if not (valid['D'] and valid['Ba']):
        if missing['D'] or missing['Ba'] or 'READY_SIGNAL_MISSING' in (reasons['D'], reasons['Ba']):
            return 'INCONCLUSIVE_READY_SIGNAL_MISSING', detail
        return f'INCONCLUSIVE_{reasons["D"] or reasons["Ba"]}', detail
    detail['delta_D_minus_Ba'] = round(values['D'] - values['Ba'], 6)
    detected = compare(rule, values['D'], values['Ba'])
    also = rule.get('also') or {}
    if 'late_shift' in also:
        ls = also['late_shift']
        hits = late_target_shift(loads['D'], ls['min_start_ms'], ls['target_element_id'])
        detail['late_target_shift_entries'] = len(hits)
        detected = detected and len(hits) > 0
    detail['detected'] = detected
    if not detected and external_image_loaded(c, loads['D']) is False:
        detail['external_image'] = 'the delayed image was not painted as a largest-paint candidate of the degraded load'
        return 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED', detail
    return ('DETECTED' if detected else 'NOT_DETECTED'), detail


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
