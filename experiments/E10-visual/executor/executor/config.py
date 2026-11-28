"""E10-visual executor: the conditions file and its validation.

DRAFT (operation OP-PREP-E10); not frozen, not locked. The conditions are read from experiments/E10-visual/conditions-draft.json (hashed
with the campaign configuration at START). Nothing here is a result: the pages, the accounts, the views, the expected elements, the capture
settings and the rule are written before any execution (campaign-configuration-draft.md, sections 2 and 3). The thresholds T_R and T_e of
the rule are null in the draft on purpose: they come from the calibration record (classify.calibrate), which does not exist before the
DRY_RUN rounds; a DRY_RUN classifies with the floors and labels the result provisional, and a MEASURED_EXPERIMENT refuses null thresholds.
"""
import json
import os
import re

CAMPAIGN = 'E10-visual'
CONDITIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'conditions-draft.json')
CONDITION_ID = re.compile(r'E10-SUT0[123]-WEB-(PROBLEM|VISUAL|IMAGE|SHIFT)')
ROLES = ('A', 'B', 'A2')
STEP_ACTIONS = ('click', 'wait_visible')


class ConfigError(Exception):
    """The conditions file is inconsistent; the executor refuses to run (no manifest)."""


def load(path=None):
    with open(path or CONDITIONS_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    validate(cfg)
    return cfg


def declared_categories(cfg):
    sets = cfg['category_sets']
    return set(sets['start']) | set(sets['method']) | set(sets['any'])


def _positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _threshold_pair(holder, where):
    """A pair {T_R, T_e} that is either both null (not calibrated) or both positive numbers."""
    pair = holder.get('thresholds') if isinstance(holder, dict) else None
    if pair is None:
        return None
    if not isinstance(pair, dict) or set(pair) != {'T_R', 'T_e'}:
        raise ConfigError(f'{where}: thresholds must be an object with exactly T_R and T_e')
    nulls = [v is None for v in pair.values()]
    if all(nulls):
        return pair
    if any(nulls) or not all(_positive(v) for v in pair.values()):
        raise ConfigError(f'{where}: T_R and T_e must both be null or both be positive numbers')
    return pair


def validate(cfg):
    declared = declared_categories(cfg)
    if cfg.get('capture_order') != list(ROLES):
        raise ConfigError(f'capture_order must be {list(ROLES)}')
    cap = cfg['capture']
    vp = cap.get('viewport') or {}
    if not (isinstance(vp.get('width'), int) and isinstance(vp.get('height'), int) and vp['width'] > 0 and vp['height'] > 0):
        raise ConfigError('capture.viewport needs a positive integer width and height')
    if cap.get('device_scale_factor') != 1:
        raise ConfigError('capture.device_scale_factor must be 1 (the capture is a viewport of css pixels)')
    if cap.get('scroll_position') != 0:
        raise ConfigError('capture.scroll_position must be 0 (the first screen only)')
    settle = cap.get('settle') or {}
    if not (_positive(settle.get('timeout_ms')) and isinstance(settle.get('animation_frames'), int) and settle['animation_frames'] >= 1):
        raise ConfigError('capture.settle needs timeout_ms and animation_frames')
    cmpr = cfg['comparison']
    opts = cmpr.get('options') or {}
    if cmpr.get('tool') != 'pixelmatch' or set(opts) != {'threshold', 'includeAA', 'alpha'} or not isinstance(opts['includeAA'], bool):
        raise ConfigError('comparison must name pixelmatch with exactly the options threshold, includeAA and alpha')
    if not (isinstance(opts['threshold'], (int, float)) and 0 <= opts['threshold'] <= 1 and isinstance(opts['alpha'], (int, float)) and 0 <= opts['alpha'] <= 1):
        raise ConfigError('comparison.options threshold and alpha must lie in [0, 1]')
    rule = cfg['rule']
    floors = rule.get('floors') or {}
    if not (_positive(floors.get('T_R')) and _positive(floors.get('T_e')) and _positive(rule.get('calibration_factor'))):
        raise ConfigError('rule needs positive floors.T_R, floors.T_e and a positive calibration_factor')
    if rule.get('type') != 'ratio_and_boxes':
        raise ConfigError('rule.type must be ratio_and_boxes')
    if 'thresholds' in rule:
        raise ConfigError('thresholds are per condition (conditions[].thresholds), not in rule')
    seen = set()
    for c in cfg['conditions']:
        cid = c['condition_id']
        if not CONDITION_ID.fullmatch(cid) or cid in seen:
            raise ConfigError(f'{cid}: not a valid, unique condition id')
        seen.add(cid)
        if cid.split('-')[1] != c['sut_id'].replace('-', ''):
            raise ConfigError(f'{cid}: does not belong to {c["sut_id"]}')
        if c['surface'] != 'web':
            raise ConfigError(f'{cid}: surface {c["surface"]!r} (E10 has web conditions only)')
        if c.get('n', cfg['n_per_condition']) != cfg['n_per_condition']:
            raise ConfigError(f'{cid}: n differs from the campaign n')
        if c['expected_category'] not in declared or c['expected_category'] != 'DETECTED':
            raise ConfigError(f'{cid}: the expected category {c["expected_category"]!r} must be DETECTED and declared')
        for state in ('state_a', 'state_b'):
            if not isinstance(c.get(state), dict) or not c[state].get('account'):
                raise ConfigError(f'{cid}: {state} needs an account')
        if c['behavior_class'] not in cfg['behavior_class_values']:
            raise ConfigError(f'{cid}: behavior_class {c["behavior_class"]!r} is not a schema value')
        if not isinstance(c['h5_counted'], bool):
            raise ConfigError(f'{cid}: h5_counted must be a boolean')
        ext = c.get('external_dependency')
        if c['behavior_class'] == 'external dependency':
            if not ext or not ext.get('hosts') or not ext.get('category_when_baseline_image_not_loaded') in declared:
                raise ConfigError(f'{cid}: an external-dependency condition must name its external hosts and a declared category')
            if not any(e.get('image') for v in c['views'] for e in v['expected_elements']):
                raise ConfigError(f'{cid}: an external-dependency condition needs an expected group flagged image')
        elif ext:
            raise ConfigError(f'{cid}: external_dependency is set but behavior_class is {c["behavior_class"]!r}')
        _threshold_pair(c, cid)
        views = c.get('views')
        if not views:
            raise ConfigError(f'{cid}: at least one view is required')
        view_ids = set()
        for v in views:
            vid = v.get('view_id')
            if not vid or vid in view_ids:
                raise ConfigError(f'{cid}: view ids must be present and unique')
            view_ids.add(vid)
            if not str(v.get('route', '')).startswith('/'):
                raise ConfigError(f'{cid}/{vid}: route must be a path')
            for step in v.get('steps') or []:
                if step.get('action') not in STEP_ACTIONS or not step.get('selector'):
                    raise ConfigError(f'{cid}/{vid}: a step needs an action of {STEP_ACTIONS} and a selector')
            ready = v.get('ready')
            if not isinstance(ready, dict) or not ready or not v.get('required_ready') or not set(v['required_ready']) <= set(ready):
                raise ConfigError(f'{cid}/{vid}: ready must be a non-empty object of key to selector and required_ready a non-empty subset of its keys')
            if not _positive(v.get('ready_timeout_ms')):
                raise ConfigError(f'{cid}/{vid}: ready_timeout_ms must be positive')
            at = v.get('capture_at_ms')
            if at is not None and (not isinstance(at, dict) or set(at) != set(ROLES) or not all(_positive(x) for x in at.values())):
                raise ConfigError(f'{cid}/{vid}: capture_at_ms must be null or give a positive time for each of {ROLES}')
            groups = set()
            if not v.get('expected_elements'):
                raise ConfigError(f'{cid}/{vid}: expected_elements must not be empty')
            for e in v['expected_elements']:
                if not e.get('group') or not e.get('selector') or e['group'] in groups:
                    raise ConfigError(f'{cid}/{vid}: each expected element needs a unique group and a selector')
                groups.add(e['group'])


def condition(cfg, condition_id):
    for c in cfg['conditions']:
        if c['condition_id'] == condition_id:
            return c
    raise ConfigError(f'{condition_id} is not a condition of this configuration')


def thresholds(cfg, c):
    """The thresholds of a condition as {T_R, T_e, provisional, source}: the per-condition pair (written at the configuration lock from the
    calibration record); with the pair null the floors are returned and the result is provisional (a DRY_RUN or a DEVELOPMENT run only)."""
    pair = _threshold_pair(c, c['condition_id'])
    if pair and pair['T_R'] is not None:
        return {'T_R': pair['T_R'], 'T_e': pair['T_e'], 'provisional': False, 'source': 'calibration record'}
    fl = cfg['rule']['floors']
    return {'T_R': fl['T_R'], 'T_e': fl['T_e'], 'provisional': True, 'source': 'floors (no calibration record)'}
