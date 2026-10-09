"""E03-CS001-SUT05-API (README section 4.7). DRAFT (operation OP-PREP-E03).

The restart is one reset action (the mapping's wording; item Q1 of README section 11 stays flagged). If the pre-reset
token is rejected after the restart, two further predeclared API actions observe; the count is the measurement.
"""
from . import common, instance

MODALITY, PLATFORM = 'API', 'api'
RESET_MECHANISMS = ['ENVIRONMENT_RESTART']
ESTABLISHMENT_MECHANISMS = ['PREDEFINED_ACCOUNT', 'API_SEED']
EXPECTED = "after the restart, GET /rest/basket/{bid} answers 200 with data null (absent) or Products []"
CITATIONS = ['experiments/scenario-mappings/CS-001.yaml (SUT-05 entry)', 'SUT05-EV-0002', 'SUT05-EV-0003', 'SUT05-EV-0006', 'SUT05-EV-0008', 'SUT05-EV-0027',
             'data/static/users.yml:131-134@1618a61', 'routes/basket.ts:15-36@1618a61']
ACCOUNT = {'email': 'mc.safesearch@juice-sh.op', 'password': 'Mr. N00dles'}


def components(run):
    return instance.components(run, [('api', 'api')])


def login(run, api, label):
    r = run.http('POST', f'{api}/rest/user/login', ACCOUNT, label=label)
    try:
        auth = (r.json().get('authentication') or {}) if r.status == 200 else {}
    except ValueError:
        auth = {}
    run.scrub.secret(auth.get('token'))
    return r, auth.get('token'), auth.get('bid')


def basket(run, api, token, bid, label):
    r = run.http('GET', f'{api}/rest/basket/{bid}', headers={'Authorization': f'Bearer {token}'}, label=label)
    try:
        body = r.json() if r.status == 200 else None
    except ValueError:
        body = None
    return r, body


def product_ids(body):
    data = (body or {}).get('data')
    return None if data is None else [p.get('id') for p in (data.get('Products') or [])]


def run(run):
    api = instance.base(run.instance, 'api')
    with run.step('precondition', 'POST /rest/user/login (documented account mc.safesearch)', ['PREDEFINED_ACCOUNT']) as s:
        r, token, bid = login(run, api, 'sut05-login')
        s['evidence'].append(r.evidence)
        s['observation'] = {'status': r.status, 'token_received': bool(token), 'bid': bid}
        if not (token and bid):
            s['outcome'] = 'FAILURE'
    with run.step('declared-starting-state', 'GET /rest/basket/{bid} before the establishment') as s:
        r, body = basket(run, api, token, bid, 'sut05-basket-start')
        s['evidence'].append(r.evidence)
        s['observation'] = {'status': r.status, 'bid': bid, 'product_ids': product_ids(body)}
        if body is None:
            s['outcome'] = 'FAILURE'
    run.declare_starting_state("the actor's basket holds no item (the account has no seeded basket; data/datacreator.ts:479-550)", CITATIONS,
                               s['observation'], s['observation']['product_ids'] == [])
    with run.step('establishment', 'POST /api/BasketItems {ProductId 1, BasketId <bid>, quantity 1}', ['API_SEED']) as s:
        r = run.http('POST', f'{api}/api/BasketItems', {'ProductId': 1, 'BasketId': bid, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'},
                     label='sut05-add-item')
        s['evidence'].append(r.evidence)
        s['observation'] = {'status': r.status}
        if r.status != 200:
            s['outcome'] = 'FAILURE'
    with run.step('pre-reset-verification', 'GET /rest/basket/{bid} shows ProductId 1') as s:
        r, body = basket(run, api, token, bid, 'sut05-basket-pre-reset')
        s['evidence'].append(r.evidence)
        ids = product_ids(body)
        s['observation'] = {'status': r.status, 'product_ids': ids}
        if not ids or 1 not in ids:
            s['outcome'] = 'FAILURE'
    with run.action('reset action', 'restart the SUT process (SIGTERM to the process group, port refused, start in a new session and group, readiness)') as a:
        instance.restart(run, a)
    final, rejected = None, False
    with run.action('API action', 'GET /rest/basket/{bid} with the pre-reset token') as a:
        r, body = basket(run, api, token, bid, 'sut05-basket-after-restart')
        a['evidence'].append(r.evidence)
        a['observation'] = {'status': r.status, 'error': r.error, 'data_is_null': None if body is None else body.get('data') is None, 'product_ids': product_ids(body)}
        rejected = r.status == 401
        if body is not None:
            final = body
        a['outcome'] = 'SUCCESS' if body is not None else 'FAILURE'
    if rejected:
        new_token, new_bid = None, None
        with run.action('API action', 'POST /rest/user/login (same account), the pre-reset token having been rejected') as a:
            r, new_token, new_bid = login(run, api, 'sut05-login-after-restart')
            a['evidence'].append(r.evidence)
            a['observation'] = {'status': r.status, 'token_received': bool(new_token), 'bid': new_bid}
            a['outcome'] = 'SUCCESS' if new_token and new_bid else 'FAILURE'
        with run.action('API action', 'GET /rest/basket/{new bid}') as a:
            r, body = basket(run, api, new_token, new_bid, 'sut05-basket-new-bid')
            a['evidence'].append(r.evidence)
            a['observation'] = {'status': r.status, 'data_is_null': None if body is None else body.get('data') is None, 'product_ids': product_ids(body)}
            final = body
            a['outcome'] = 'SUCCESS' if body is not None else 'FAILURE'
    if final is None:
        return common.Result('INCONCLUSIVE', EXPECTED, 'no parseable basket read after the restart', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
    data = final.get('data')
    ok = data is None or (data.get('Products') or []) == []
    observed = 'data null (absent)' if data is None else f'Products {product_ids(final)}'
    return common.Result('SUCCESS' if ok else 'FAILURE', EXPECTED, observed + (' (read with a new login after the pre-reset token was rejected)' if rejected else ''),
                         RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
