"""E04-repeatability executor: block phases, the success and failure categories, attribution labels, and the manifest outcome fields.

DRAFT (operation OP-PREP-E04). Pure functions; no SUT is contacted. The categories are the E05 failure categories of the reset,
starting-state, establishment and verification blocks, plus STUB_NO_BUNDLE, and one success category, TARGET_STATE_VERIFIED. There is no
stimulus phase, so no S_ or INTERRUPTED_ category exists in E04. Attribution is the mechanical rule of
IMPLEMENTATION-NOTES.md, point 3 (issue (xix), decision D-16 option B; the response boundary of the design default is an open item)."""
from . import config

PHASE_BY_PREFIX = ((config.SUCCESS_PREFIX, 'VERIFIED'), ('RESET_', 'RESET'), ('ESTABLISHMENT_', 'ESTABLISHMENT'), ('STUB_', 'STUB'))
OUTCOME_STATUS = {'VERIFIED': None, 'RESET': 'ABORTED', 'ESTABLISHMENT': 'ABORTED', 'STUB': 'ERROR'}


def phase(label):
    for prefix, name in PHASE_BY_PREFIX:
        if label.startswith(prefix):
            return name
    return None


def label_for_failure(phase_name, interrupted):
    """The failure category of an attempt that stopped in a block before its verification held.

    reset: the reset did not hold or could not run (RESET_FAILED). starting-state: the declared starting state was not reached
    (RESET_STARTING_STATE_NOT_REACHED, recorded as ABORTED with its cause). establishment and verification: an interruption of the harness
    or the client is ESTABLISHMENT_INTERRUPTED; a recorded failure is ESTABLISHMENT_FAILED or ESTABLISHMENT_VERIFICATION_FAILED."""
    if phase_name == 'reset':
        return 'RESET_FAILED'
    if phase_name == 'starting-state':
        return 'RESET_STARTING_STATE_NOT_REACHED'
    if phase_name == 'establishment':
        return 'ESTABLISHMENT_INTERRUPTED' if interrupted else 'ESTABLISHMENT_FAILED'
    if phase_name == 'verification':
        return 'ESTABLISHMENT_INTERRUPTED' if interrupted else 'ESTABLISHMENT_VERIFICATION_FAILED'
    raise ValueError(f'no failure category for the block {phase_name!r}')


def attribution(interrupted, infrastructure_interruption):
    """Mechanical attribution (IMPLEMENTATION-NOTES.md, point 3): TOOLING for an interruption (a harness or client exception, a client or
    browser crash or a disconnect) or for an infrastructure interruption recorded by the workflow; SUT otherwise, including every
    attempt whose cause cannot be assigned mechanically."""
    return 'TOOLING' if (interrupted or infrastructure_interruption) else 'SUT'


def manifest_outcome(c, label, observed):
    """The run-manifest outcome object (schema v2) of one attempt. status SUCCESS means only that the target state was verified;
    matches_expected compares the label with the pre-declared category and is never derived from an observation."""
    ph = phase(label)
    if ph is None:
        raise ValueError(f'undeclared category {label!r}')
    status = OUTCOME_STATUS[ph] or 'SUCCESS'
    return {'status': status, 'expected': c['expected_category'], 'observed': observed, 'outcome_category': label,
            'matches_expected': label == c['expected_category']}
