"""E08-performance executor: the conditions file and its validation.

DRAFT (operation OP-PREP-E08); not frozen, not locked. The conditions are read from experiments/E08-performance/conditions-draft.json (hashed
with the campaign configuration at START). Nothing here is a result: the pages, the accounts, the metric, the threshold and the expected
category are written before any execution (campaign-configuration-draft.md, sections 3 and 4).
"""
import json
import os
import re

CAMPAIGN = 'E08-performance'
CONDITIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'conditions-draft.json')
CONDITION_ID = re.compile(r'E08-SUT0[123]-WEB-(DELAY|BLOCK|LCP|CLS)')
METRICS = ('first_item_ms', 'longest_longtask_ms', 'lcp_ms', 'cls')
COMPARISONS = ('delta_ge', 'delta_gt')
ROLES = ('D', 'Ba', 'Bb')


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


def validate(cfg):
    declared = declared_categories(cfg)
    orders = cfg['load_orders']
    if not orders or any(sorted(o) != sorted(ROLES) or o.index('Ba') > o.index('Bb') for o in orders):
        raise ConfigError('load_orders: each order must be a permutation of D, Ba, Bb with Ba earlier than Bb')
    if not isinstance(cfg['observe_window_ms'], int) or cfg['observe_window_ms'] <= 0:
        raise ConfigError('observe_window_ms must be a positive integer')
    seen = set()
    for c in cfg['conditions']:
        cid = c['condition_id']
        if not CONDITION_ID.fullmatch(cid) or cid in seen:
            raise ConfigError(f'{cid}: not a valid, unique condition id')
        seen.add(cid)
        if cid.split('-')[1] != c['sut_id'].replace('-', ''):
            raise ConfigError(f'{cid}: does not belong to {c["sut_id"]}')
        if c['surface'] != 'web':
            raise ConfigError(f'{cid}: surface {c["surface"]!r} (E08 has web conditions only)')
        if c.get('n', cfg['n_per_condition']) != cfg['n_per_condition']:
            raise ConfigError(f'{cid}: n differs from the campaign n')
        if c['metric'] not in METRICS:
            raise ConfigError(f'{cid}: unknown metric {c["metric"]!r}')
        rule = c['rule']
        if rule.get('comparison') not in COMPARISONS or not isinstance(rule.get('threshold'), (int, float)):
            raise ConfigError(f'{cid}: the rule needs a comparison of {COMPARISONS} and a numeric threshold')
        if c['expected_category'] not in declared or c['expected_category'] != 'DETECTED':
            raise ConfigError(f'{cid}: the expected category {c["expected_category"]!r} must be DETECTED and declared')
        for role in ('degraded', 'baseline'):
            if not c[role].get('account') or not str(c[role].get('page', '')).startswith('/'):
                raise ConfigError(f'{cid}: {role} needs an account and a page path')
        if not isinstance(c.get('watch'), dict) or not c['watch'] or not set(c.get('required_ready') or ()) <= set(c['watch']) or not c.get('required_ready'):
            raise ConfigError(f'{cid}: watch must be a non-empty object of key to selector and required_ready a non-empty subset of its keys')
        if c['behavior_class'] not in cfg['behavior_class_values']:
            raise ConfigError(f'{cid}: behavior_class {c["behavior_class"]!r} is not a schema value')
        if not isinstance(c['h5_counted'], bool):
            raise ConfigError(f'{cid}: h5_counted must be a boolean')
        if c['behavior_class'] == 'external dependency' and not c.get('external_dependency'):
            raise ConfigError(f'{cid}: an external-dependency condition must name its external host')


def condition(cfg, condition_id):
    for c in cfg['conditions']:
        if c['condition_id'] == condition_id:
            return c
    raise ConfigError(f'{condition_id} is not a condition of this configuration')


def order_for(cfg, index):
    """The load order of the execution with the absolute index i (1-based): load_orders[(i - 1) mod len]."""
    orders = cfg['load_orders']
    return tuple(orders[(index - 1) % len(orders)])
