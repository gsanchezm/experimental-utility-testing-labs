"""E11-security executor: the cells file and its validation.

DRAFT (operation OP-PREP-E11); not frozen, not locked. The cells are read from experiments/E11-security/conditions-draft.json (hashed with
the campaign configuration at START). Nothing here is a result: the expected categories and the expected M2 rule, method and path are
written before any execution (campaign-configuration-draft.md, sections 2, 4 and 4b)."""
import json
import os
import re

CAMPAIGN = 'E11-security'
CONDITIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'conditions-draft.json')
CELL_ID = re.compile(r'E11-SUT0[15]-(IDOR-ORDER|SQLI-LOGIN|SQLI-SEARCH|DIRLIST-FTP)-M[12](-CTRL)?')
KINDS = ('CONDITION', 'CONTROL')
M1_CATEGORIES = {'CONDITION': ('M1_ORACLE_FLIPPED', 'M1_IDOR_BYPASS_OBSERVED'), 'CONTROL': ('M1_ORACLE_NOT_FLIPPED', 'M1_IDOR_BLOCKED')}
M2_CATEGORIES = {'CONDITION': ('M2_EXPECTED_ALERT',), 'CONTROL': ('M2_NO_EXPECTED_ALERT',)}


class ConfigError(Exception):
    """The cells file is inconsistent; the executor refuses to run (no manifest)."""


def load(path=None):
    with open(path or CONDITIONS_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    validate(cfg)
    return cfg


def declared_categories(cfg):
    sets = cfg['category_sets']
    return set(sets['reset']) | set(sets['m1']) | set(sets['m2']) | set(sets['any'])


def validate(cfg):
    declared = declared_categories(cfg)
    seen = set()
    for c in cfg['cells']:
        cid = c['cell_id']
        if not CELL_ID.fullmatch(cid) or cid in seen:
            raise ConfigError(f'{cid}: not a valid, unique cell id')
        seen.add(cid)
        if cid.split('-')[1] != c['sut_id'].replace('-', ''):
            raise ConfigError(f'{cid}: does not belong to {c["sut_id"]}')
        if c['kind'] not in KINDS or (c['kind'] == 'CONTROL') != cid.endswith('-CTRL'):
            raise ConfigError(f'{cid}: kind {c["kind"]!r} does not match the id')
        if c['method'] not in ('M1', 'M2') or f'-{c["method"]}' not in cid:
            raise ConfigError(f'{cid}: method {c["method"]!r} does not match the id')
        if c['n'] != cfg['n_per_cell']:
            raise ConfigError(f'{cid}: n {c["n"]} differs from the campaign n')
        allowed = (M1_CATEGORIES if c['method'] == 'M1' else M2_CATEGORIES)[c['kind']]
        if c['expected_category'] not in allowed or c['expected_category'] not in declared:
            raise ConfigError(f'{cid}: the expected category {c["expected_category"]!r} is not a declared {c["method"]} {c["kind"]} category')
        if c['method'] == 'M2' and c['kind'] == 'CONDITION' and not (c.get('expected_m2_rule_id') and c.get('expected_m2_target')):
            raise ConfigError(f'{cid}: an M2 condition cell needs its expected rule id and target')
        if c['method'] == 'M2' and c['sut_id'] != 'SUT-05':
            raise ConfigError(f'{cid}: M2 is configured on SUT-05 only (E11-D-9: no rule of the pinned set targets the SUT-01 class)')


def cell(cfg, cell_id):
    for c in cfg['cells']:
        if c['cell_id'] == cell_id:
            return c
    raise ConfigError(f'{cell_id} is not a cell of this configuration')
