"""E05-determinism executor: category phases, label finalization, attribution labels, and the manifest outcome fields.

DRAFT (operation OP-PREP-E05). Pure functions; no SUT is contacted. Decisions applied: D-08 (the phase of an attempt is carried in the
outcome_category label; schema v2 unchanged), D-09 (an attempt that left no bundle is a stub in T), D-16 and D-16b (mechanical TOOLING and
SUT labels beside the raw rates; uncertain goes to SUT; a TOOLING interruption after establishment is an INTERRUPTED_ category)."""
from . import config

PHASE_BY_PREFIX = (('S_', 'S'), ('INTERRUPTED_', 'INTERRUPTED'), ('RESET_', 'RESET'), ('ESTABLISHMENT_', 'ESTABLISHMENT'), ('STUB_', 'STUB'))
OUTCOME_STATUS = {'S': None, 'INTERRUPTED': 'ERROR', 'RESET': 'ABORTED', 'ESTABLISHMENT': 'ABORTED', 'STUB': 'ERROR'}


def phase(label):
    for prefix, name in PHASE_BY_PREFIX:
        if label.startswith(prefix):
            return name
    return None


def in_s(label):
    """S counts attempts whose establishment verification passed: stimulus-phase outcomes and interruptions after it (config s.10)."""
    return phase(label) in ('S', 'INTERRUPTED')


def finalize_label(cfg, c, label):
    """Return (label, note). A label outside the declared sets is mapped to the condition's declared catch-all when it has one; a label
    that cannot be mapped is returned unchanged with a note, so that the analysis fails closed on it instead of dropping the attempt."""
    declared = set(c['stimulus_categories']) | set(cfg['non_stimulus_categories'])
    if label in declared:
        return label, None
    fallback = config.catch_all(c)
    if fallback is None:
        return label, f'undeclared category {label!r}: {c["condition_id"]} declares no catch-all category'
    return fallback, f'undeclared category {label!r} mapped to the declared catch-all {fallback}'


def label_for_failure(phase_name, interrupted):
    """The non-stimulus (or interruption) category of an attempt that stopped in a block before its classification (config s.10).

    reset: the reset did not hold or could not run (RESET_FAILED). starting-state: the declared starting state was not reached
    (RESET_STARTING_STATE_NOT_REACHED, recorded as ABORTED with its cause). establishment and verification: an interruption of the harness
    or the client is ESTABLISHMENT_INTERRUPTED, a recorded failure is ESTABLISHMENT_FAILED or ESTABLISHMENT_VERIFICATION_FAILED. A stop in
    the stimulus or classification block is an INTERRUPTED_ category (protocol section 5, rule 6; D-16b)."""
    if phase_name == 'reset':
        return 'RESET_FAILED'
    if phase_name == 'starting-state':
        return 'RESET_STARTING_STATE_NOT_REACHED'
    if phase_name == 'establishment':
        return 'ESTABLISHMENT_INTERRUPTED' if interrupted else 'ESTABLISHMENT_FAILED'
    if phase_name == 'verification':
        return 'ESTABLISHMENT_INTERRUPTED' if interrupted else 'ESTABLISHMENT_VERIFICATION_FAILED'
    return 'INTERRUPTED_'


def attribution(interruption_before_stimulus_sent, infrastructure_interruption):
    """D-16, rules 1 to 3 (mechanical, from harness records only): TOOLING when an exception, a client or browser crash, or a disconnect
    happened before the stimulus request was sent, or the workflow recorded an infrastructure interruption; SUT otherwise, and SUT when
    the cause cannot be assigned mechanically."""
    return 'TOOLING' if (interruption_before_stimulus_sent or infrastructure_interruption) else 'SUT'


def manifest_outcome(cfg, c, label, observed):
    """The run-manifest outcome object (schema v2) for one execution. status SUCCESS means only that the attempt reached a stimulus-phase
    outcome; matches_expected compares the label with the pre-declared expected category and is never derived from an observed mode."""
    ph = phase(label)
    status = OUTCOME_STATUS.get(ph) or 'SUCCESS'
    return {'status': status, 'expected': c['expected_category'], 'observed': observed, 'outcome_category': label,
            'matches_expected': label == c['expected_category']}
