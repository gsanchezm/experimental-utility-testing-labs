"""E07-cross-layer-continuity executor: the categories of an execution, their causes, attribution labels, and the manifest outcome fields.

DRAFT (operation OP-PREP-E07-04). Pure functions; no SUT is contacted. The categories are the five of decision D-E07-10
(manifests/campaign-execution-decisions-v12.yaml): VERIFIED, NOT_VERIFIED, ESTABLISHMENT_FAILED, INTERRUPTED (with the cause RESET_FAILED,
STARTING_STATE_NOT_REACHED or WATCHDOG) and RUNNER_ERROR. Attribution is the mechanical rule of IMPLEMENTATION-NOTES.md, point 3: TOOLING for an
exception of the executor, the browser, the client or the infrastructure and for the per-execution watchdog, SUT for a recorded failure and for
every execution whose cause cannot be assigned mechanically."""
from . import config

# run-manifest outcome.status of each category (schema v2: SUCCESS and FAILURE describe the scenario outcome, ABORTED a run stopped before its
# verification completed, ERROR a runner or infrastructure fault).
OUTCOME_STATUS = {'VERIFIED': 'SUCCESS', 'NOT_VERIFIED': 'FAILURE', 'ESTABLISHMENT_FAILED': 'ABORTED', 'INTERRUPTED': 'ABORTED', 'RUNNER_ERROR': 'ERROR'}
# the block in which a recorded (not excepted) failure puts the execution
PHASE_LABEL = {'reset': ('INTERRUPTED', 'RESET_FAILED'), 'starting-state': ('INTERRUPTED', 'STARTING_STATE_NOT_REACHED'),
               'establishment': ('ESTABLISHMENT_FAILED', None), 'establishment-check': ('ESTABLISHMENT_FAILED', None),
               'verification': ('NOT_VERIFIED', None)}


def label_for_failure(phase_name, interrupted, watchdog=False):
    """(category, cause of an interruption or None) of an attempt that stopped in a block before its verification held.

    watchdog: the per-execution budget was exceeded in that block (INTERRUPTED, cause WATCHDOG). interrupted: an exception of the executor, the
    browser, the client or the infrastructure stopped the block (RUNNER_ERROR). Otherwise the block recorded that the SUT or the instance did
    not hold what it requires: the reset (INTERRUPTED, RESET_FAILED), the starting-state check (INTERRUPTED, STARTING_STATE_NOT_REACHED), the
    establishment or its source-side check (ESTABLISHMENT_FAILED), the verification on the other layer (NOT_VERIFIED)."""
    if phase_name not in PHASE_LABEL:
        raise ValueError(f'no failure category for the block {phase_name!r}')
    if watchdog:
        return 'INTERRUPTED', 'WATCHDOG'
    if interrupted:
        return 'RUNNER_ERROR', None
    return PHASE_LABEL[phase_name]


def attribution(interrupted, infrastructure_interruption):
    """Mechanical attribution (IMPLEMENTATION-NOTES.md, point 3): TOOLING for an interruption (an exception, a watchdog, a browser crash or a
    disconnect) or for an infrastructure interruption recorded by the workflow; SUT otherwise, including every attempt whose cause cannot be
    assigned mechanically."""
    return 'TOOLING' if (interrupted or infrastructure_interruption) else 'SUT'


def manifest_outcome(c, label, observed):
    """The run-manifest outcome object (schema v2) of one attempt. status SUCCESS means only that the continuity was verified;
    matches_expected compares the label with the pre-declared category and is never derived from an observation."""
    if label not in config.CATEGORIES:
        raise ValueError(f'undeclared category {label!r}')
    return {'status': OUTCOME_STATUS[label], 'expected': c['expected_category'], 'observed': observed, 'outcome_category': label,
            'matches_expected': label == c['expected_category']}
