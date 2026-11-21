"""E06-cross-platform-parity executor: the conditions file, its validation, and the constants the executor enforces.

DRAFT (operation OP-PREP-E06-EXECUTOR). Not frozen, not locked. The conditions are read from
experiments/E06-cross-platform-parity/conditions-draft.json; the locked file is named by the campaign configuration at START. The executor
refuses any file that differs from the vocabulary below, so a change of category, reason, switch value, or N is a change of this code
(and of its digests), never a silent edit of the draft.
"""
import json
import os
import re

CAMPAIGN = 'E06-cross-platform-parity'
SCENARIO = 'CS-007'
EXPERIMENT = 'E06-CS007'
N_PER_CONDITION = 50
ATTEMPT = 1
DRY_RUN_EXECUTIONS = 3
ENVIRONMENT_VERIFICATION_EXECUTIONS = 1
RECORD_CLASSES = ('MEASURED_EXPERIMENT', 'DRY_RUN', 'ENVIRONMENT_VERIFICATION')
CONDITIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'conditions-draft.json')
CONDITION_ID = re.compile(r'E06-CS007-SUT0([12])-(WEB|ANDROID)')
SUT_OF_NUMBER = {'1': 'SUT-01', '2': 'SUT-02'}
PLATFORM_OF_SURFACE = {'WEB': 'web', 'ANDROID': 'android'}
IDENTITY_KEY_OF_SUT = {'SUT-01': 'pizza_id', 'SUT-02': 'product_title'}
ENVIRONMENT_TYPES = ('PUBLIC_HOSTED', 'SELF_HOSTED', 'LOCAL', 'EMULATED', 'SIMULATED', 'OTHER')
IDENTITY_ORACLE_VALUES = ('item_identity', 'arrival_only')

CATEGORIES = [
    'ARRIVED_IDENTITY_READ',
    'ARRIVED_ARRIVAL_ONLY',
    'ARRIVED_IDENTITY_UNREADABLE',
    'NOT_ARRIVED_INFRASTRUCTURE',
    'NOT_ARRIVED_SUT',
    'NOT_ARRIVED_RUNNER',
]
ARRIVAL_SUCCESS_CATEGORIES = ['ARRIVED_IDENTITY_READ', 'ARRIVED_ARRIVAL_ONLY']
NOT_ARRIVED_REASONS = {
    'NOT_ARRIVED_INFRASTRUCTURE': ['INFRA_USER_LIMIT_429', 'INFRA_BACKEND_5XX', 'INFRA_BACKEND_NO_RESPONSE', 'INFRA_CATALOGUE_TIMEOUT'],
    'NOT_ARRIVED_SUT': ['SUT_SIGN_IN_REFUSED', 'SUT_CATALOGUE_NOT_REACHED_AFTER_SIGN_IN'],
    'NOT_ARRIVED_RUNNER': ['RUNNER_FAULT'],
}
# reasons that are attached to an execution that arrived but whose identity could not be read
IDENTITY_REASON = 'IDENTITY_UNREADABLE'


class ConfigError(Exception):
    """The conditions file is inconsistent with this executor; nothing runs (no record is written)."""


def load(path=None):
    with open(path or CONDITIONS_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    validate(cfg)
    return cfg


def validate(cfg):
    if cfg.get('record_class') != 'CONDITIONS_DRAFT':
        raise ConfigError('record_class is not the conditions record of this campaign')
    if cfg.get('campaign_id') != CAMPAIGN or cfg.get('canonical_scenario_id') != SCENARIO:
        raise ConfigError('campaign or canonical scenario differs from the executor')
    if cfg.get('n_per_condition') != N_PER_CONDITION or cfg.get('attempt') != ATTEMPT:
        raise ConfigError('N or the attempt differs from the executor (N 50, attempt 1)')
    if cfg.get('categories') != CATEGORIES:
        raise ConfigError('the categories differ from the executor vocabulary')
    if cfg.get('arrival_success_categories') != ARRIVAL_SUCCESS_CATEGORIES:
        raise ConfigError('the arrival success categories differ from the executor')
    if cfg.get('not_arrived_reasons') != NOT_ARRIVED_REASONS:
        raise ConfigError('the reasons of a non-arrival differ from the executor vocabulary')
    switch = cfg.get('identity_oracle_switch') or {}
    if tuple(switch.get('values') or ()) != IDENTITY_ORACLE_VALUES or switch.get('default') != 'item_identity':
        raise ConfigError('the identity oracle switch values or default differ from the executor')
    seen = set()
    conditions = cfg.get('conditions')
    if not isinstance(conditions, list) or len(conditions) != 4:
        raise ConfigError('the conditions file must hold exactly four conditions (D-E06-6)')
    for c in conditions:
        cid = c.get('condition_id')
        m = CONDITION_ID.fullmatch(cid or '')
        if not m or cid in seen:
            raise ConfigError(f'{cid!r}: not a valid, unique condition id')
        seen.add(cid)
        sut = SUT_OF_NUMBER[m.group(1)]
        surface = m.group(2)
        if c.get('sut_id') != sut or c.get('surface') != surface or c.get('platform') != PLATFORM_OF_SURFACE[surface]:
            raise ConfigError(f'{cid}: sut, surface or platform does not match the condition id')
        if c.get('canonical_scenario_id') != SCENARIO or c.get('n') != cfg['n_per_condition'] or c.get('attempt') != ATTEMPT:
            raise ConfigError(f'{cid}: scenario, N or attempt differs from the campaign')
        if c.get('environment_type') not in ENVIRONMENT_TYPES:
            raise ConfigError(f'{cid}: environment_type is not an allowed value')
        if c.get('identity_key') != IDENTITY_KEY_OF_SUT[sut]:
            raise ConfigError(f'{cid}: identity key does not match {sut}')
        if c.get('identity_oracle') not in IDENTITY_ORACLE_VALUES or c.get('identity_oracle_default') != 'item_identity':
            raise ConfigError(f'{cid}: identity oracle is not an allowed value')
        username, password = credentials(c)
        if not username or not password:
            raise ConfigError(f'{cid}: the account or its password is not recorded')
        if surface == 'ANDROID':
            apk = c.get('apk') or {}
            if not re.fullmatch(r'[0-9a-f]{64}', apk.get('sha256') or ''):
                raise ConfigError(f'{cid}: the APK digest is not a SHA-256 value')
            if not apk.get('file'):
                raise ConfigError(f'{cid}: the APK file name is missing')


def condition(cfg, condition_id):
    for c in cfg['conditions']:
        if c['condition_id'] == condition_id:
            return c
    raise ConfigError(f'{condition_id} is not a condition of this configuration')


def credentials(c):
    """(username, password) of a condition. SUT-02 Android records a candidate account with its own password (open item 1)."""
    account = c.get('account')
    if isinstance(account, dict):
        return account.get('candidate'), account.get('password')
    return account, c.get('password')


def planned_executions(record_class, cfg):
    if record_class == 'MEASURED_EXPERIMENT':
        return cfg['n_per_condition']
    if record_class == 'DRY_RUN':
        return DRY_RUN_EXECUTIONS
    if record_class == 'ENVIRONMENT_VERIFICATION':
        return ENVIRONMENT_VERIFICATION_EXECUTIONS
    raise ConfigError(f'record class {record_class!r} is not one of {RECORD_CLASSES}')
