"""E03-CS001-SUT01-API (README section 4.1). DRAFT (operation OP-PREP-E03)."""
import json

from . import common, instance

MODALITY, PLATFORM = 'API', 'api'
RESET_MECHANISMS = ['API_RESET', 'SESSION_RESET']
ESTABLISHMENT_MECHANISMS = ['PREDEFINED_ACCOUNT', 'API_SEED']
EXPECTED = 'after the reset, GET /api/session returns cart_items [] and the starting country_code'
CITATIONS = ['experiments/scenario-mappings/CS-001.yaml (SUT-01 entry)', 'SUT01-EV-0001', 'SUT01-EV-0004', 'SUT01-EV-0006',
             'backend/database.py:139-148@9ca3767', 'backend/test_api.py:193-229@9ca3767']
LINE = {'pizza_id': 'p02', 'quantity': 1, 'size': 'small', 'toppings': []}


def components(run):
    return instance.components(run, [('api', 'api')])


def login(run, api):
    """Precondition shared with E03-CS001-SUT01-WEB: the documented test account (backend/routers/auth.py:20-74)."""
    with run.step('precondition', 'POST /api/auth/login (standard_user)', ['PREDEFINED_ACCOUNT']) as s:
        r = run.http('POST', f'{api}/api/auth/login', {'username': 'standard_user', 'password': 'pizza123'}, label='sut01-login')
        s['evidence'].append(r.evidence)
        body = r.json() if r.status == 200 else {}
        token = body.get('access_token')
        run.scrub.secret(token)
        s['observation'] = {'status': r.status, 'username': body.get('username'), 'behavior': body.get('behavior'), 'token_received': bool(token)}
        if not token:
            s['outcome'] = 'FAILURE'
    return token, body


def session(run, api, token, label):
    return run.http('GET', f'{api}/api/session', headers={'Authorization': f'Bearer {token}'}, label=label)


def read_session(r):
    try:
        return r.json() if r.status == 200 else None
    except ValueError:
        return None


def starting_state(run, api, token):
    with run.step('declared-starting-state', 'GET /api/session before the establishment') as s:
        r = session(run, api, token, 'sut01-session-start')
        s['evidence'].append(r.evidence)
        body = read_session(r) or {}
        s['observation'] = {'status': r.status, 'cart_items': body.get('cart_items'), 'country_code': body.get('country_code')}
        if r.status != 200:
            s['outcome'] = 'FAILURE'
    return s['observation']


def seed(run, api, token):
    with run.step('establishment', 'POST /api/cart with one p02 line', ['API_SEED']) as s:
        r = run.http('POST', f'{api}/api/cart', {'items': [LINE]}, headers={'Authorization': f'Bearer {token}'}, label='sut01-seed-cart')
        s['evidence'].append(r.evidence)
        s['observation'] = {'status': r.status}
        if r.status != 200:
            s['outcome'] = 'FAILURE'


def reset(run, api, token):
    with run.action('reset action', 'POST /api/session/reset with the session token') as a:
        r = run.http('POST', f'{api}/api/session/reset', headers={'Authorization': f'Bearer {token}'}, label='sut01-reset')
        a['evidence'].append(r.evidence)
        a['observation'] = {'status': r.status, 'error': r.error}
        a['outcome'] = 'SUCCESS' if r.status == 200 else 'FAILURE'


def run(run):
    api = instance.base(run.instance, 'api')
    token, _ = login(run, api)
    start = starting_state(run, api, token)
    run.declare_starting_state('the login session holds {cart_items: [], country_code: <starting value>} (backend/database.py:139-148)',
                               CITATIONS, start, start.get('cart_items') == [])
    seed(run, api, token)
    with run.step('pre-reset-verification', 'GET /api/session shows exactly the p02 line') as s:
        r = session(run, api, token, 'sut01-session-pre-reset')
        s['evidence'].append(r.evidence)
        items = (read_session(r) or {}).get('cart_items') or []
        s['observation'] = {'status': r.status, 'cart_items': items}
        if not (len(items) == 1 and items[0].get('pizza_id') == 'p02' and items[0].get('quantity') == 1):
            s['outcome'] = 'FAILURE'
    reset(run, api, token)
    body = None
    with run.action('API action', 'GET /api/session') as a:
        r = session(run, api, token, 'sut01-session-after-reset')
        a['evidence'].append(r.evidence)
        body = read_session(r)
        a['observation'] = {'status': r.status, 'cart_items': (body or {}).get('cart_items'), 'country_code': (body or {}).get('country_code')}
        a['outcome'] = 'SUCCESS' if body is not None else 'FAILURE'
    if body is None:
        return common.Result('INCONCLUSIVE', EXPECTED, 'the post-reset read returned no parseable session', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
    ok = body.get('cart_items') == [] and body.get('country_code') == start.get('country_code')
    observed = f"cart_items {json.dumps(body.get('cart_items'))}; country_code {body.get('country_code')} (starting value {start.get('country_code')})"
    return common.Result('SUCCESS' if ok else 'FAILURE', EXPECTED, observed, RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
