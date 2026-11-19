"""E07-cross-layer-continuity executor: the conditions file and its validation.

DRAFT (operation OP-PREP-E07-04); not frozen, not locked, not a START record. The conditions are read from
experiments/E07-cross-layer-continuity/conditions-draft.json (hashed with the campaign configuration at START, if the human research lead
decides it). Nothing here is a result: the success category, the other categories and the causes of an interruption are declared before any
attempt (manifests/campaign-execution-decisions-v12.yaml, D-E07-10)."""
import json
import os
import re

CAMPAIGN = 'E07-cross-layer-continuity'
SUCCESS_CATEGORY = 'VERIFIED'
CATEGORIES = ['VERIFIED', 'NOT_VERIFIED', 'ESTABLISHMENT_FAILED', 'INTERRUPTED', 'RUNNER_ERROR']
INTERRUPTED_CAUSES = ['RESET_FAILED', 'STARTING_STATE_NOT_REACHED', 'WATCHDOG']
CONDITIONS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'conditions-draft.json')
CONDITION_ID = re.compile(r'E07-CS00([56])-SUT0([14])-(API-WEB|WEB-API)')
# The canonical scenario of each direction (experiments/scenario-mappings/CS-005.yaml: API -> WEB; CS-006.yaml: WEB -> API).
DIRECTION = {'CS-005': ('api', 'web'), 'CS-006': ('web', 'api')}
LAYERS = ('web', 'api')


class ConfigError(Exception):
    """The conditions file is inconsistent; the executor refuses to run (no manifest)."""


def load(path=None):
    with open(path or CONDITIONS_FILE, encoding='utf-8') as f:
        cfg = json.load(f)
    validate(cfg)
    return cfg


def validate(cfg):
    if cfg['success_category'] != SUCCESS_CATEGORY:
        raise ConfigError('the success category differs from the executor')
    if cfg['categories'] != CATEGORIES:
        raise ConfigError('the declared categories differ from the executor (D-E07-10)')
    if cfg['interrupted_causes'] != INTERRUPTED_CAUSES:
        raise ConfigError('the declared causes of an interruption differ from the executor')
    if cfg['attribution_labels'] != ['TOOLING', 'SUT']:
        raise ConfigError('the attribution labels differ from the executor')
    seen = set()
    for c in cfg['conditions']:
        cid = c['condition_id']
        m = CONDITION_ID.fullmatch(cid)
        if not m or cid in seen:
            raise ConfigError(f'{cid}: not a valid, unique condition id')
        seen.add(cid)
        scenario, sut_number, direction = f'CS-00{m.group(1)}', m.group(2), m.group(3)
        if c['sut_id'] != f'SUT-0{sut_number}':
            raise ConfigError(f'{cid}: does not belong to {c["sut_id"]}')
        if c['canonical_scenario_id'] != scenario:
            raise ConfigError(f'{cid}: the canonical scenario {c["canonical_scenario_id"]!r} does not match the condition id')
        if (c['source_layer'], c['verification_layer']) != DIRECTION[scenario] or direction != '-'.join(DIRECTION[scenario]).upper():
            raise ConfigError(f'{cid}: the layers do not follow the direction of {scenario}')
        if c['source_layer'] not in LAYERS or c['verification_layer'] not in LAYERS or c['source_layer'] == c['verification_layer']:
            raise ConfigError(f'{cid}: a condition crosses two different layers of web and api')
        if c['expected_category'] != SUCCESS_CATEGORY:
            raise ConfigError(f'{cid}: the expected category is not the success category')
        if not c['identity_keys'] or any(not isinstance(k, str) or not k for k in c['identity_keys']):
            raise ConfigError(f'{cid}: the identity keys are not declared')
        if c['n'] != cfg['n_per_condition']:
            raise ConfigError(f'{cid}: n {c["n"]} differs from the campaign n')


def condition(cfg, condition_id):
    for c in cfg['conditions']:
        if c['condition_id'] == condition_id:
            return c
    raise ConfigError(f'{condition_id} is not a condition of this configuration')
