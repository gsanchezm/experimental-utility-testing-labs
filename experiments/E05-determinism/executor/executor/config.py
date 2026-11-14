"""E05-determinism executor: the conditions file and its validation.

DRAFT (operation OP-PREP-E05); not frozen, not locked. The conditions are read from experiments/E05-determinism/conditions-draft.json
(hashed with the campaign configuration at START). Nothing here is a result: the declared categories, classes and expected values are
written before any execution (protocol/repeatability-determinism-v1.md, section 4)."""
import json
import os
import re

CAMPAIGN = 'E05-determinism'
BEHAVIOR_CLASSES = ('deterministic', 'stochastic', 'time-dependent', 'external dependency')
CONDITIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'conditions-draft.json')
CONDITION_ID = re.compile(r'E05-SUT0[1-6]-(API|WEB)-[0-9]{2}')


class ConfigError(Exception):
    """The conditions file is inconsistent; the executor refuses to run (no manifest)."""


def load(path=None):
    with open(path or CONDITIONS_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    validate(cfg)
    return cfg


def validate(cfg):
    in_s, not_in_s = tuple(cfg['phase_prefixes']['in_S']), tuple(cfg['phase_prefixes']['not_in_S'])
    non_stim = set(cfg['non_stimulus_categories'])
    if any(not c.startswith(not_in_s) for c in non_stim):
        raise ConfigError('a non-stimulus category does not carry a phase prefix outside S')
    seen = set()
    for c in cfg['conditions']:
        cid = c['condition_id']
        if not CONDITION_ID.fullmatch(cid) or cid in seen:
            raise ConfigError(f'{cid}: not a valid, unique condition id')
        seen.add(cid)
        if cid.split('-')[1] != c['sut_id'].replace('-', ''):
            raise ConfigError(f'{cid}: does not belong to {c["sut_id"]}')
        if c['behavior_class'] not in BEHAVIOR_CLASSES:
            raise ConfigError(f'{cid}: behavior class {c["behavior_class"]!r}')
        cats = c['stimulus_categories']
        if len(set(cats)) != len(cats) or c['k'] != len(cats):
            raise ConfigError(f'{cid}: k {c["k"]} does not match its {len(cats)} distinct categories')
        if any(not x.startswith(in_s) for x in cats):
            raise ConfigError(f'{cid}: a stimulus category does not carry a phase prefix inside S')
        if 'INTERRUPTED_' not in cats or c['expected_category'] not in cats or c['expected_category'] == 'INTERRUPTED_':
            raise ConfigError(f'{cid}: the expected category is not a declared stimulus-phase category')
        if c['n'] != cfg['n_per_condition']:
            raise ConfigError(f'{cid}: n {c["n"]} differs from the campaign n')
        if c['h3_labeled'] and (c['sut_id'] != 'SUT-01' or c['behavior_class'] != 'deterministic'):
            raise ConfigError(f'{cid}: the H3 label applies to deterministic SUT-01 conditions only')


def condition(cfg, condition_id):
    for c in cfg['conditions']:
        if c['condition_id'] == condition_id:
            return c
    raise ConfigError(f'{condition_id} is not a condition of this configuration')


def catch_all(c):
    """The declared category that receives a response no other category describes, or None when the condition declares none."""
    for pattern in (r'S_OTHER', r'S_.*_OTHER$', r'S_.*MISMATCH$'):
        for cat in c['stimulus_categories']:
            if re.match(pattern, cat):
                return cat
    return None
