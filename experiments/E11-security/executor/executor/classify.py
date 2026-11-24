"""E11-security executor: category phases, attribution labels, and the manifest outcome fields.

DRAFT (operation OP-PREP-E11). Pure functions; no SUT is contacted. The categories are the closed sets of conditions-draft.json
(`category_sets`); a label outside them is never mapped to another one (there is no catch-all: M1_RESPONSE_OTHER is declared where an
unexpected response is possible), it is kept with a note so that the analysis fails closed on it instead of dropping the execution.
Attribution is mechanical (E05 D-16): TOOLING when an exception happened before the first request that can change the SUT was sent, when
ZAP itself failed (ZAP_ categories), or when the workflow recorded an infrastructure interruption; SUT otherwise, and SUT when the cause
cannot be assigned mechanically."""

from . import config

PHASE_BY_PREFIX = (('M1_', 'M1'), ('M2_', 'M2'), ('ZAP_', 'ZAP'), ('INTERRUPTED_', 'INTERRUPTED'), ('RESET_', 'RESET'), ('STUB_', 'STUB'))
OUTCOME_STATUS = {'M1': None, 'M2': None, 'ZAP': 'ERROR', 'INTERRUPTED': 'ERROR', 'RESET': 'ABORTED', 'STUB': 'ERROR'}
TOOLING_PREFIXES = ('ZAP_',)


def phase(label):
    for prefix, name in PHASE_BY_PREFIX:
        if label.startswith(prefix):
            return name
    return None


def finalize_label(cfg, c, label):
    """Return (label, note). A declared label is returned as is; an undeclared one is returned unchanged with a note."""
    if label in config.declared_categories(cfg):
        return label, None
    return label, f'undeclared category {label!r}: {c["cell_id"]} has no catch-all category, the label is kept'


def label_for_failure(phase_name, interrupted):
    """The category of an execution that stopped in a block before its classification.

    reset: the reset did not hold or could not run (RESET_FAILED). starting-state: the declared starting state was not reached
    (RESET_STARTING_STATE_NOT_REACHED, recorded as ABORTED with its cause). method or classification: an exception of the harness or of
    the client is INTERRUPTED_; a method that returns an observation never reaches this function."""
    if phase_name == 'reset':
        return 'RESET_FAILED'
    if phase_name == 'starting-state':
        return 'RESET_STARTING_STATE_NOT_REACHED'
    return 'INTERRUPTED_'


def attribution(interruption_before_request_sent, infrastructure_interruption, label=None):
    if label and label.startswith(TOOLING_PREFIXES):
        return 'TOOLING'
    return 'TOOLING' if (interruption_before_request_sent or infrastructure_interruption) else 'SUT'


def manifest_outcome(cfg, c, label, observed):
    """The run-manifest outcome object (schema v2). status SUCCESS means only that the method reached an observation; the detection result
    is the outcome_category. matches_expected compares the label with the cell's pre-declared expected category."""
    ph = phase(label)
    status = OUTCOME_STATUS.get(ph) or 'SUCCESS'
    return {'status': status, 'expected': c['expected_category'], 'observed': observed, 'outcome_category': label,
            'matches_expected': label == c['expected_category']}
