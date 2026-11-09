"""E02 realization for SUT-05 (OWASP Juice Shop, api). DRAFT (operation OP-PREP-E02).

The account, the login route and its response shape (authentication.token and authentication.bid), the basket read, and the
basket-item route are those of the E03 executor on the pinned SUT-05 commit (experiments/E03-resetability/executor/README.md,
section 4.7; executor/sut05_api.py). The BasketItems create is SOURCE_VERIFIED for its route and model only (E01 did not execute
it individually; SUT05-EV-0008, SUT05-EV-0027), so its first execution is a DRY_RUN check, not evidence.
The between-run state is a fresh instance per run (provisioned in the measured job), so no process restart is performed here.
"""
from . import common, instance

ACCOUNT = {'email': 'mc.safesearch@juice-sh.op', 'password': 'Mr. N00dles'}
CITATIONS = ['experiments/scenario-mappings/CS-003.yaml (SUT-05 entry)', 'SUT05-EV-0002', 'SUT05-EV-0003', 'SUT05-EV-0006',
             'SUT05-EV-0008', 'SUT05-EV-0027', 'data/static/users.yml:131-134@1618a61', 'routes/basket.ts:15-36@1618a61']
EXPECTED = 'after the BasketItems create, GET /rest/basket/{bid} shows ProductId 1 in the basket of the documented account'
MECH = ['PREDEFINED_ACCOUNT', 'API_SEED']


def components(run):
    return instance.components(run, [('api', 'api')])


def _json(r):
    try:
        return r.json() if r.status == 200 else None
    except ValueError:
        return None


def _basket_products(body):
    basket = (body or {}).get('data')
    products = basket.get('Products') if isinstance(basket, dict) else None
    return basket, [p for p in (products or []) if isinstance(p, dict)]


def cs003_api(run):
    """CS-003, SUT-05 API. Counted: login (authentication; returns the token and the basket id), the BasketItems create, and the
    basket read (verification) (3). The starting-state read follows the login, because the basket id comes from it."""
    api = instance.base(run.instance, 'api')
    with run.action('API action', 'POST /rest/user/login with the documented account (authentication; returns token and bid)', 'PREDEFINED_ACCOUNT') as a:
        r = run.http('POST', f'{api}/rest/user/login', ACCOUNT, label='sut05-login')
        a['evidence'].append(r.evidence)
        auth = (_json(r) or {}).get('authentication') or {}
        token, bid = auth.get('token'), auth.get('bid')
        run.scrub.secret(token)
        a['observation'] = {'status': r.status, 'token_received': bool(token), 'bid_received': bid is not None}
        a['outcome'] = 'SUCCESS' if token and bid is not None else 'FAILURE'
    bearer = {'Authorization': f'Bearer {token}'}
    with run.step('declared-starting-state', 'GET /rest/basket/{bid}: the basket of the documented account holds no product') as s:
        r = run.http('GET', f'{api}/rest/basket/{bid}', headers=bearer, label='sut05-basket-start')
        s['evidence'].append(r.evidence)
        basket, products = _basket_products(_json(r))
        s['observation'] = {'status': r.status, 'data_null': basket is None, 'products': len(products)}
    run.declare_starting_state('the basket of the documented account holds no product (routes/basket.ts:15-36@1618a61; data/datacreator.ts:479-550@1618a61)',
                               CITATIONS, s['observation'], r.status == 200 and not products)
    with run.action('API action', 'POST /api/BasketItems with ProductId 1, quantity 1, in the actor basket (establishment)', 'API_SEED') as a:
        r = run.http('POST', f'{api}/api/BasketItems', {'ProductId': 1, 'BasketId': int(bid), 'quantity': 1}, headers=bearer, label='sut05-basket-add')
        a['evidence'].append(r.evidence)
        a['observation'] = {'status': r.status, 'error': r.error}
        a['outcome'] = 'SUCCESS' if r.status in (200, 201) else 'FAILURE'
    with run.action('API action', 'GET /rest/basket/{bid}: read the basket (verification)', None, verification=True) as a:
        r = run.http('GET', f'{api}/rest/basket/{bid}', headers=bearer, label='sut05-basket-verify')
        a['evidence'].append(r.evidence)
        body = _json(r)
        _, products = _basket_products(body)
        ids = [p.get('ProductId', p.get('id')) for p in products]
        a['observation'] = {'status': r.status, 'product_ids': ids}
        a['outcome'] = 'SUCCESS' if body is not None else 'FAILURE'
    return common.Result('SUCCESS' if 1 in ids else 'FAILURE', EXPECTED, f'product ids in the basket: {ids}', MECH)


SPEC = {
    'E02-CS003-SUT05-API': common.Spec('API', 'api', MECH, EXPECTED, components, True),
}
