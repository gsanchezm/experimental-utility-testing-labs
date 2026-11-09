"""E09 realization constants: conditions, accounts, market, viewport, and routes (design brief section 4; configuration draft section 3e).

DRAFT (operation OP-PREP-E09). Not frozen, not locked. The condition ids are candidates (not frozen) and must be
confirmed by the locked "Campaign configuration" record before any START.
"""
# Candidate condition ids (configuration draft, section 3e). kind: GLITCH (ground truth possible) or CONTROL.
CONDITIONS = {
    'E09-A11Y-SUT01-MISSING-NAME': {'kind': 'GLITCH', 'account': 'a11y_glitch_user', 'behavior_class': 'stochastic'},
    'E09-CTRL-SUT01-STANDARD': {'kind': 'CONTROL', 'account': 'standard_user', 'behavior_class': None},
}
ASSIGNED_SUT = 'SUT-01'
# Documented SUT-01 test accounts. The control password is the one the E03 SUT-01 realization uses (executor README, section 4.1).
# The password of a11y_glitch_user is NOT recorded in the E01 evidence rows (SUT01-EV-0017 to -0019) and is NOT guessed:
# it stays None until the human research lead decides its source (HUMAN DECISION HD-E09-A). While it is None, every
# glitch attempt is refused before any browser starts.
ACCOUNTS = {
    'standard_user': 'pizza123',
    'a11y_glitch_user': None,
}
CATALOG_PATH = '/catalog'
CATALOG_API_PATH = '/api/pizzas'
ROUTE_EVIDENCE = ['SUT01-EV-0001', 'SUT01-EV-0017', 'SUT01-EV-0018', 'SUT01-EV-0019']
# Market, language, viewport, and browser context: reused from the E03 SUT-01 web realization (HUMAN DECISION HD-7).
MARKET = {'countryCode': 'MX', 'language': 'es', 'locale': 'es-MX', 'currency': 'MXN'}
VIEWPORT = {'width': 1280, 'height': 800}
BROWSER_LOCALE = 'en-US'
TIMEZONE = 'UTC'
# Timeouts (milliseconds), as the E03 web realization: navigation 30 s, actions 15 s, settle 15 s with a 500 ms quiet window.
NAV_TIMEOUT_MS = 30000
ACTION_TIMEOUT_MS = 15000
SETTLE_TIMEOUT_MS = 15000
QUIET_MS = 500
WATCHDOG_S = 900
BODY_LIMIT = 65536
