"""E02 realizations for SUT-01 (OmniPizza): CS-003 API and WEB, and CS-004 WEB. DRAFT (operation OP-PREP-E02).

The endpoints, the client storage keys, and the test ids are those that the E03 executor used on the pinned SUT-01 commit
(experiments/E03-resetability/executor/README.md, sections 4.1 and 4.2, and its DEVELOPMENT and hosted DRY_RUN runs). The
establish-side sequences, the counting, and the oracles are new (experiments/E02-state-establishment/executor/README.md, section 4).
"""
import json

from . import common, instance, web

ACCOUNT = {'username': 'standard_user', 'password': 'pizza123'}
LINE = {'pizza_id': 'p02', 'quantity': 1, 'size': 'small', 'toppings': []}
ORDER_LINE = '[data-testid="order-item-p02"]'
SEED_JS = '(seed) => { for (const [k, v] of Object.entries(seed)) window.localStorage.setItem(k, v); }'
READ_JS = '(keys) => Object.fromEntries(keys.map((k) => [k, window.localStorage.getItem(k)]))'
CITATIONS_CS003 = ['experiments/scenario-mappings/CS-003.yaml (SUT-01 entry)', 'SUT01-EV-0001', 'SUT01-EV-0002', 'SUT01-EV-0004',
                   'SUT01-EV-0005', 'SUT01-EV-0007', 'backend/middleware.py:8,28-50@9ca3767']
CITATIONS_CS004 = ['experiments/scenario-mappings/CS-004.yaml (SUT-01 entry)', 'SUT01-EV-0001', 'SUT01-EV-0004', 'SUT01-EV-0005',
                   'SUT01-EV-0007']
EXPECTED_API = 'after the establishment, GET /api/session shows exactly one p02 line of quantity 1'
EXPECTED_WEB = 'after the establishment, the Checkout view shows the p02 order line'
EXPECTED_CS004 = 'the Checkout view presents the seeded p02 line; the committing step is not performed'
WEB_MECH = ['PREDEFINED_ACCOUNT', 'API_SEED', 'APP_STATE_CONTROL', 'DIRECT_ROUTE']


def _bearer(token):
    return {'Authorization': f'Bearer {token}'}


def _json(r):
    try:
        return r.json() if r.status == 200 else None
    except ValueError:
        return None


def _line_ok(items):
    return isinstance(items, list) and len(items) == 1 and items[0].get('pizza_id') == 'p02' and items[0].get('quantity') == 1


def _storage(token, behavior):
    """The client storage of the documented web atomic entry (README section 4.2; SUT01-EV-0001, SUT01-EV-0002). The omnipizza-release
    key is not written: the first load stores the build's value, which the realization reads and leaves unchanged."""
    return {
        'omnipizza-auth': json.dumps({'state': {'token': token, 'username': ACCOUNT['username'], 'behavior': behavior}, 'version': 0}),
        'omnipizza-country': json.dumps({'state': {'countryCode': 'MX', 'countryInfo': None, 'language': 'es', 'locale': 'es-MX',
                                                   'currency': 'MXN'}, 'version': 0}),
        'token': token,
        'username': ACCOUNT['username'],
        'countryCode': 'MX',
        'omnipizza-cart': json.dumps({'state': {'items': []}, 'version': 0}),
    }


def _cart_empty(cart):
    return isinstance(cart, dict) and (cart.get('state') or {}).get('items') in (None, [])


def components_api(run):
    return instance.components(run, [('api', 'api')])


def components_web(run):
    return instance.components(run, [('api', 'api'), ('web', 'web')])


def cs003_api(run):
    """CS-003, SUT-01 API. Counted: login, cart seed, verification read (3). Starting state: no authenticated session."""
    api = instance.base(run.instance, 'api')
    with run.step('declared-starting-state', 'GET /api/session without a token before the actor acts') as s:
        r = run.http('GET', f'{api}/api/session', label='sut01-session-unauthenticated')
        s['evidence'].append(r.evidence)
        s['observation'] = {'status': r.status}
    run.declare_starting_state('no authenticated session exists in the fresh instance, so no session cart does (backend/middleware.py:8,28-50)',
                               CITATIONS_CS003, s['observation'], r.status in (401, 403))
    with run.action('API action', 'POST /api/auth/login with the documented standard account (authentication)', 'PREDEFINED_ACCOUNT') as a:
        r = run.http('POST', f'{api}/api/auth/login', ACCOUNT, label='sut01-login')
        a['evidence'].append(r.evidence)
        token = (_json(r) or {}).get('access_token')
        run.scrub.secret(token)
        a['observation'] = {'status': r.status, 'token_received': bool(token)}
        a['outcome'] = 'SUCCESS' if token else 'FAILURE'
    with run.action('API action', 'POST /api/cart with one p02 line (seeds the session cart)', 'API_SEED') as a:
        r = run.http('POST', f'{api}/api/cart', {'items': [LINE]}, headers=_bearer(token), label='sut01-seed-cart')
        a['evidence'].append(r.evidence)
        a['observation'] = {'status': r.status, 'error': r.error}
        a['outcome'] = 'SUCCESS' if r.status == 200 else 'FAILURE'
    with run.action('API action', 'GET /api/session: read the session cart (verification)', None, verification=True) as a:
        r = run.http('GET', f'{api}/api/session', headers=_bearer(token), label='sut01-session-verify')
        a['evidence'].append(r.evidence)
        body = _json(r)
        items = (body or {}).get('cart_items')
        a['observation'] = {'status': r.status, 'cart_items': items}
        a['outcome'] = 'SUCCESS' if body is not None else 'FAILURE'
    return common.Result('SUCCESS' if _line_ok(items) else 'FAILURE', EXPECTED_API,
                         f'cart_items {json.dumps(items)}', ['PREDEFINED_ACCOUNT', 'API_SEED'])


def cs003_web(run):
    """CS-003, SUT-01 WEB. Counted: the first load of the run, API login, client storage injection, cart seed, navigation to
    Checkout, and the verification read (6). The starting state is read after the first load (its check is not counted)."""
    api = instance.base(run.instance, 'api')
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.action('navigation action', 'open {web}/ (the first load of the run; it gives the client storage an origin; counted, HD-15 default)', 'DIRECT_ROUTE') as a:
            status = b.goto(site + '/')
            a['observation'] = {'status': status, 'omnipizza-release (read, not written)': web.local_storage(b, 'omnipizza-release')}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.step('declared-starting-state', 'client storage holds no token and an empty client cart') as s:
            token_before = web.local_storage(b, 'token')
            cart_before = web.parse(web.local_storage(b, 'omnipizza-cart'))
            s['observation'] = {'token_present': token_before is not None, 'omnipizza-cart': cart_before}
        run.declare_starting_state('no token in the client storage and an empty client cart on the first load (src/store.js:5-24,159-225@9ca3767)',
                                   CITATIONS_CS003, s['observation'], token_before is None and _cart_empty(cart_before))
        with run.action('API action', 'POST /api/auth/login with the documented standard account (authentication)', 'PREDEFINED_ACCOUNT') as a:
            r = run.http('POST', f'{api}/api/auth/login', ACCOUNT, label='sut01-web-login')
            a['evidence'].append(r.evidence)
            body = _json(r) or {}
            token = body.get('access_token')
            run.scrub.secret(token)
            a['observation'] = {'status': r.status, 'token_received': bool(token)}
            a['outcome'] = 'SUCCESS' if token else 'FAILURE'
        with run.action('state/configuration action', 'inject the token, username, market, and an empty client cart into the client storage (documented web atomic entry)', 'APP_STATE_CONTROL') as a:
            seed = _storage(token, body.get('behavior'))
            b.page.evaluate(SEED_JS, seed)
            readback = b.page.evaluate(READ_JS, sorted(seed))
            a['observation'] = {'keys': sorted(seed), 'read_back_equal': readback == seed}
            a['outcome'] = 'SUCCESS' if readback == seed else 'FAILURE'
        with run.action('API action', 'POST /api/cart with one p02 line (seeds the server session cart)', 'API_SEED') as a:
            r = run.http('POST', f'{api}/api/cart', {'items': [LINE]}, headers=_bearer(token), label='sut01-web-seed-cart')
            a['evidence'].append(r.evidence)
            a['observation'] = {'status': r.status, 'error': r.error}
            a['outcome'] = 'SUCCESS' if r.status == 200 else 'FAILURE'
        with run.action('navigation action', 'open the Checkout route {web}/checkout (its mount effect fetches GET /api/cart)', 'DIRECT_ROUTE') as a:
            status = b.goto(site + '/checkout')
            a['observation'] = {'status': status, 'url': b.page.url}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.action('UI action', 'read the Checkout view for the p02 order line (verification)', None, verification=True) as a:
            settle = b.settle()
            lines = b.page.locator(ORDER_LINE).count()
            a['observation'] = {'order_lines_p02': lines, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut01-web-after-establishment')
    finally:
        b.close()
    return common.Result('SUCCESS' if lines == 1 else 'FAILURE', EXPECTED_WEB, f'order lines p02 in the Checkout view: {lines}', WEB_MECH)


def cs004_web(run):
    """CS-004, SUT-01 WEB (DRAFT scenario). The seeding is the precondition, not counted (DP-1 SEEDED); counted: the direct navigation
    to Checkout and the verification read (2)."""
    api = instance.base(run.instance, 'api')
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.step('precondition', 'first load of {web}/ (not counted)', ['DIRECT_ROUTE']) as s:
            s['observation'] = {'first_load_status': b.goto(site + '/')}
        with run.step('precondition', 'API login with the standard account (not counted)', ['PREDEFINED_ACCOUNT']) as s:
            r = run.http('POST', f'{api}/api/auth/login', ACCOUNT, label='sut01-cs004-login')
            s['evidence'].append(r.evidence)
            body = _json(r) or {}
            token = body.get('access_token')
            run.scrub.secret(token)
            s['observation'] = {'status': r.status, 'token_received': bool(token)}
            if not token:
                s['outcome'] = 'FAILURE'
        with run.step('precondition', 'one p02 line seeded through POST /api/cart (not counted)', ['API_SEED']) as s:
            r = run.http('POST', f'{api}/api/cart', {'items': [LINE]}, headers=_bearer(token), label='sut01-cs004-seed')
            s['evidence'].append(r.evidence)
            s['observation'] = {'status': r.status}
            if r.status != 200:
                s['outcome'] = 'FAILURE'
        with run.step('precondition', 'client auth injection with an empty client cart (not counted)', ['APP_STATE_CONTROL']) as s:
            seed = _storage(token, body.get('behavior'))
            b.page.evaluate(SEED_JS, seed)
            s['observation'] = {'keys': sorted(seed), 'read_back_equal': b.page.evaluate(READ_JS, sorted(seed)) == seed}
            if not s['observation']['read_back_equal']:
                s['outcome'] = 'FAILURE'
        with run.step('declared-starting-state', 'GET /api/session: the server session cart holds the p02 line; the client holds the token') as s:
            r = run.http('GET', f'{api}/api/session', headers=_bearer(token), label='sut01-cs004-session-start')
            s['evidence'].append(r.evidence)
            items = (_json(r) or {}).get('cart_items')
            s['observation'] = {'status': r.status, 'cart_items': items}
        run.declare_starting_state('the server session cart holds exactly the seeded p02 line; no order has been placed (CS-004 notes)',
                                   CITATIONS_CS004, s['observation'], _line_ok(items))
        with run.action('navigation action', 'open the Checkout route directly {web}/checkout', 'DIRECT_ROUTE') as a:
            status = b.goto(site + '/checkout')
            a['observation'] = {'status': status, 'url': b.page.url}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.action('UI action', 'read the Checkout view for the seeded p02 line (verification)', None, verification=True) as a:
            settle = b.settle()
            lines = b.page.locator(ORDER_LINE).count()
            a['observation'] = {'order_lines_p02': lines, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut01-cs004-checkout')
    finally:
        b.close()
    return common.Result('SUCCESS' if lines == 1 else 'FAILURE', EXPECTED_CS004, f'order lines p02 in the Checkout view: {lines}', WEB_MECH)


SPEC = {
    'E02-CS003-SUT01-API': common.Spec('API', 'api', ['PREDEFINED_ACCOUNT', 'API_SEED'], EXPECTED_API, components_api, True),
    'E02-CS003-SUT01-WEB': common.Spec('Web UI Functional', 'web', WEB_MECH, EXPECTED_WEB, components_web, True),
    'E02-CS004-SUT01-WEB': common.Spec('Web UI Functional', 'web', WEB_MECH, EXPECTED_CS004, components_web, True),
}
