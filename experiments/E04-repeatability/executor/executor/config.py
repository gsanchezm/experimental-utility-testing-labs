"""E04-repeatability executor: the conditions file and its validation.

DRAFT (operation OP-PREP-E04); not frozen, not locked, not a START record. The conditions are read from
experiments/E04-repeatability/conditions-draft.json (hashed with the campaign configuration at START, if the human research lead
decides it). Nothing here is a result: the success category and the failure categories are declared before any attempt
(protocol/repeatability-determinism-v1.md, section 4)."""
import json
import os
import re

CAMPAIGN = 'E04-repeatability'
SUCCESS_CATEGORY = 'TARGET_STATE_VERIFIED'
SUCCESS_PREFIX = 'TARGET_STATE_'
CONDITIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'conditions-draft.json')
CONDITION_ID = re.compile(r'E04-SUT0[1-6]-(API|WEB)-[0-9]{2}')
MIRROR_ID = re.compile(r'E05-SUT0[1-6]-(API|WEB)-[0-9]{2}')


class ConfigError(Exception):
    """The conditions file is inconsistent; the executor refuses to run (no manifest)."""


def load(path=None):
    with open(path or CONDITIONS_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    validate(cfg)
    return cfg


def validate(cfg):
    failure = tuple(cfg['phase_prefixes']['failure'])
    if cfg['success_category'] != SUCCESS_CATEGORY or cfg['phase_prefixes']['success'] != SUCCESS_PREFIX:
        raise ConfigError('the success category or its phase prefix differs from the executor')
    if not SUCCESS_CATEGORY.startswith(SUCCESS_PREFIX) or SUCCESS_CATEGORY.startswith(failure):
        raise ConfigError('the success category carries a failure phase prefix, or no success prefix')
    failures = cfg['failure_categories']
    if len(set(failures)) != len(failures) or SUCCESS_CATEGORY in failures:
        raise ConfigError('a failure category is duplicated or equals the success category')
    if any(not c.startswith(failure) for c in failures):
        raise ConfigError('a failure category does not carry a failure phase prefix')
    seen = set()
    for c in cfg['conditions']:
        cid = c['condition_id']
        if not CONDITION_ID.fullmatch(cid) or cid in seen:
            raise ConfigError(f'{cid}: not a valid, unique condition id')
        seen.add(cid)
        if cid.split('-')[1] != c['sut_id'].replace('-', ''):
            raise ConfigError(f'{cid}: does not belong to {c["sut_id"]}')
        if c['surface'] not in ('web', 'api') or c['surface'].upper() != cid.split('-')[2]:
            raise ConfigError(f'{cid}: surface {c["surface"]!r} does not match the condition id')
        if c['expected_category'] != SUCCESS_CATEGORY:
            raise ConfigError(f'{cid}: the expected category is not the success category')
        if c['establishment_only'] is not True:
            raise ConfigError(f'{cid}: E04 conditions are establishment-only')
        if not MIRROR_ID.fullmatch(c['mirrors']) or c['mirrors'] != 'E05-' + cid[4:]:
            raise ConfigError(f'{cid}: the mirrored E05 condition {c["mirrors"]!r} is not the same condition of E05')
        if c['n'] != cfg['n_per_condition']:
            raise ConfigError(f'{cid}: n {c["n"]} differs from the campaign n')


def condition(cfg, condition_id):
    for c in cfg['conditions']:
        if c['condition_id'] == condition_id:
            return c
    raise ConfigError(f'{condition_id} is not a condition of this configuration')
