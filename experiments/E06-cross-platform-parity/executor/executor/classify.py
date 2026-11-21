"""E06-cross-platform-parity executor: the category of one execution, its reason, its attribution, and the run-manifest outcome.

DRAFT (operation OP-PREP-E06-EXECUTOR). Pure functions; no SUT is contacted. The categories and reasons are the vocabulary of
config.py (declared in the conditions file before any execution). Parity is NOT decided here: it is a pairwise property computed by the
analysis from the arrival and identity of the two executions of a pair (conditions-draft.json, parity_rule).

Attribution (mechanical, declared before the run):
- SUT: an execution the system under test answered and did not let through (NOT_ARRIVED_SUT), and an identity that could not be read
  while the item identity oracle is active (UNDETERMINED: the cause is not assigned mechanically, the record says so).
- INFRASTRUCTURE: a backend refusal or unavailability, or a timeout of the hosted backend or the device, with its message.
- TOOLING: a fault of the executor, the browser, the WebDriver client, or the Appium session (NOT_ARRIVED_RUNNER).
- NONE: an execution that arrived.
"""
from . import config

OUTCOME_STATUS = {
    'ARRIVED_IDENTITY_READ': 'SUCCESS',
    'ARRIVED_ARRIVAL_ONLY': 'SUCCESS',
    'ARRIVED_IDENTITY_UNREADABLE': 'INCONCLUSIVE',
    'NOT_ARRIVED_INFRASTRUCTURE': 'ABORTED',
    'NOT_ARRIVED_SUT': 'FAILURE',
    'NOT_ARRIVED_RUNNER': 'ERROR',
}
ATTRIBUTION_OF = {
    'ARRIVED_IDENTITY_READ': 'NONE',
    'ARRIVED_ARRIVAL_ONLY': 'NONE',
    'ARRIVED_IDENTITY_UNREADABLE': 'UNDETERMINED',
    'NOT_ARRIVED_INFRASTRUCTURE': 'INFRASTRUCTURE',
    'NOT_ARRIVED_SUT': 'SUT',
    'NOT_ARRIVED_RUNNER': 'TOOLING',
}


def reason_category(reason):
    """The non-arrival category that declares a reason, or None when the reason is not declared."""
    for category, reasons in config.NOT_ARRIVED_REASONS.items():
        if reason in reasons:
            return category
    return None


def not_arrived_reason(facts):
    """The reason of a non-arrival, decided from what the driver observed (pure; the precedence is declared here).

    facts keys (each may be None when not observed):
      sign_in_submitted   bool, the sign-in control was activated
      login_status        HTTP status of the sign-in request as the page saw it, or None
      login_request_seen  bool, a sign-in request left the browser
      catalogue_status    HTTP status of the catalogue request, or None
      catalogue_seen      bool, a catalogue request left the browser
      error_text          the text of the sign-in error message shown by the application, or None
      session_not_established  bool, the application showed the catalogue after the sign-in but not the second signal of the authenticated
                          state (SUT-02 Android: the drawer row Logout Menu Item; decision D-E06-13); the system answered and did not admit the actor
      backend_observed    bool, whether the driver can see the backend answers at all (the browser can; the Android app cannot)
    Precedence (first match wins):
      1 the backend refused the sign-in with the user limit (HTTP 429, or the message Too many users) -> INFRA_USER_LIMIT_429
      2 a backend answer with status 5xx (sign-in or catalogue) -> INFRA_BACKEND_5XX
      3 a sign-in or catalogue request left the browser and no answer came within the budget, or the sign-in page was never
        shown (page_loaded False: a cold start of the hosted front end) -> INFRA_BACKEND_NO_RESPONSE
      4 the sign-in was refused (HTTP 401 or 403, or an error message is shown), or the application did not establish a session
        (the second signal of the authenticated state is absent) -> SUT_SIGN_IN_REFUSED
      5 the sign-in was accepted (HTTP 200), the catalogue answered with a status below 500, and it was not shown
        -> SUT_CATALOGUE_NOT_REACHED_AFTER_SIGN_IN
      6 the sign-in was accepted but the catalogue never answered, or the sign-in was submitted and no refusal was shown within the
        budget (the Android application cannot report the backend answers) -> INFRA_CATALOGUE_TIMEOUT
      7 the sign-in was never submitted: the executor could not act -> RUNNER_FAULT
    """
    text = facts.get('error_text') or ''
    login, cat = facts.get('login_status'), facts.get('catalogue_status')
    if 'too many users' in text.lower() or login == 429:
        return 'INFRA_USER_LIMIT_429'
    if (login is not None and login >= 500) or (cat is not None and cat >= 500):
        return 'INFRA_BACKEND_5XX'
    if (facts.get('login_request_seen') and login is None) or (facts.get('catalogue_seen') and cat is None):
        return 'INFRA_BACKEND_NO_RESPONSE'
    if facts.get('page_loaded') is False:
        return 'INFRA_BACKEND_NO_RESPONSE'
    if login in (401, 403) or text or facts.get('session_not_established'):
        return 'SUT_SIGN_IN_REFUSED'
    if login == 200 and cat is not None and cat < 500:
        return 'SUT_CATALOGUE_NOT_REACHED_AFTER_SIGN_IN'
    if login == 200 or facts.get('sign_in_submitted') or facts.get('login_request_seen'):
        return 'INFRA_CATALOGUE_TIMEOUT'
    return 'RUNNER_FAULT'


def classify(*, identity_oracle, arrived, identity=None, reason=None, runner_fault=None):
    """The category of one execution.

    arrived: the authenticated catalogue was reached. identity: the identity read (None when not read or unreadable).
    reason: the non-arrival reason of not_arrived_reason, required when not arrived. runner_fault: a message when an exception of the
    executor, the browser, the client, or the Appium session stopped the execution (overrides everything else).
    """
    if identity_oracle not in config.IDENTITY_ORACLE_VALUES:
        raise ValueError(f'identity oracle {identity_oracle!r} is not one of {config.IDENTITY_ORACLE_VALUES}')
    if runner_fault:
        category, reason = 'NOT_ARRIVED_RUNNER', 'RUNNER_FAULT'
    elif not arrived:
        category = reason_category(reason)
        if category is None:
            raise ValueError(f'the non-arrival reason {reason!r} is not declared in the conditions file')
    elif identity_oracle == 'arrival_only':
        category, reason = 'ARRIVED_ARRIVAL_ONLY', None
    elif not identity:
        category, reason = 'ARRIVED_IDENTITY_UNREADABLE', config.IDENTITY_REASON
    else:
        category, reason = 'ARRIVED_IDENTITY_READ', None
    arrived_now = category in config.ARRIVAL_SUCCESS_CATEGORIES
    if arrived_now:
        matches = True
    elif category == 'NOT_ARRIVED_SUT':
        matches = False
    else:
        matches = None
    return {
        'category': category,
        'reason': reason,
        'attribution': ATTRIBUTION_OF[category],
        'outcome_status': OUTCOME_STATUS[category],
        'arrived': arrived_now,
        'identity_read': identity if category == 'ARRIVED_IDENTITY_READ' else None,
        'matches_expected': matches,
    }


def manifest_outcome(expected, record):
    """The run-manifest outcome object (schema v2) of one execution, from classify(). outcome.status is the schema enum value."""
    observed = record['category'] if record['reason'] is None else f"{record['category']}: {record['reason']}"
    return {
        'status': record['outcome_status'],
        'expected': expected,
        'observed': observed,
        'matches_expected': record['matches_expected'],
        'outcome_category': record['category'],
    }
