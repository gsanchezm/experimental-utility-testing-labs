"""E03-CS001-SUT01-WEB, realization W-A (README section 4.2). DRAFT (operation OP-PREP-E03).

One injection of client state before the establishment, never repeated after the target state; omnipizza-release is
not written: the value the first load stored is read and recorded (frontend/src/store.js:8-21).
"""
import json

from . import common, instance, sut01_api, web

MODALITY, PLATFORM = 'Web UI Functional', 'web'
RESET_MECHANISMS = ['API_RESET', 'SESSION_RESET']
ESTABLISHMENT_MECHANISMS = ['PREDEFINED_ACCOUNT', 'API_SEED', 'DIRECT_ROUTE']
EXPECTED = 'after the reset and a reload of /checkout, the Checkout view shows the empty-cart view and no order line'
CITATIONS = ['experiments/scenario-mappings/CS-001.yaml (SUT-01 entry)', 'SUT01-EV-0001', 'SUT01-EV-0002', 'SUT01-EV-0004', 'SUT01-EV-0006',
             'frontend/src/store.js:159-225@9ca3767', 'frontend/src/pages/Checkout.jsx:133-187@9ca3767']
ORDER_LINES = "() => Array.from(document.querySelectorAll('[data-testid^=\"order-item-\"]')).map(e => e.getAttribute('data-testid')).filter(t => /^order-item-[A-Za-z0-9]+$/.test(t))"


def components(run):
    return instance.components(run, [('web', 'web'), ('api', 'api')])


def read_view(b):
    empty = b.page.locator('[data-testid="start-order-btn"]').count() > 0
    lines = b.page.evaluate(ORDER_LINES)
    return {'empty_cart_view': empty, 'order_lines': lines}


def run(run):
    api, site = instance.base(run.instance, 'api'), instance.base(run.instance, 'web')
    token, login = sut01_api.login(run, api)
    b = web.Browser(run)
    try:
        with run.step('precondition', 'first load of {web}/ and one injection of client state (session, market, empty client cart)', ['PREDEFINED_ACCOUNT']) as s:
            status = b.goto(site + '/')
            release = web.local_storage(b, 'omnipizza-release')
            seed = {'omnipizza-auth': json.dumps({'state': {'token': token, 'username': login.get('username'), 'behavior': login.get('behavior')}, 'version': 0}),
                    'omnipizza-country': json.dumps({'state': {'countryCode': 'MX', 'countryInfo': None, 'language': 'es', 'locale': 'es-MX', 'currency': 'MXN'}, 'version': 0}),
                    'token': token, 'username': login.get('username'), 'countryCode': 'MX',
                    'omnipizza-cart': json.dumps({'state': {'items': []}, 'version': 0})}
            b.page.evaluate('(seed) => { for (const [k, v] of Object.entries(seed)) window.localStorage.setItem(k, v); }', seed)
            s['observation'] = {'first_load_status': status, 'omnipizza-release (read, not written)': release, 'keys_injected': sorted(seed)}
            if status != 200:
                s['outcome'] = 'FAILURE'
            run.capture(s, b.storage, 'sut01-web-storage-after-injection')
        start = sut01_api.starting_state(run, api, token)
        start['client_cart'] = web.parse(web.local_storage(b, 'omnipizza-cart'))
        client_items = ((start['client_cart'] or {}).get('state') or {}).get('items') if isinstance(start['client_cart'], dict) else None
        run.declare_starting_state('the server session cart is empty (backend/database.py:139-148) and the client cart omnipizza-cart holds no item (frontend/src/store.js:159-225)',
                                   CITATIONS, start, start.get('cart_items') == [] and client_items == [])
        sut01_api.seed(run, api, token)
        with run.step('establishment', 'navigation to {web}/checkout (Checkout hydrates from GET /api/cart when the local cart is empty)', ['DIRECT_ROUTE']) as s:
            status = b.goto(site + '/checkout')
            s['observation'] = {'status': status, 'url': b.page.url}
            if status != 200:
                s['outcome'] = 'FAILURE'
        with run.step('pre-reset-verification', '[data-testid="order-item-p02"] visible') as s:
            b.page.locator('[data-testid="order-item-p02"]').wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            s['observation'] = read_view(b)
            run.capture(s, b.shot, 'sut01-web-pre-reset')
            run.capture(s, b.storage, 'sut01-web-storage-pre-reset')
        sut01_api.reset(run, api, token)
        with run.action('navigation action', 'reload {web}/checkout') as a:
            status = b.reload()
            b.page.locator('[data-testid="screen-checkout"]').first.wait_for(state='attached', timeout=web.ACTION_TIMEOUT_MS)
            a['observation'] = {'status': status, 'url': b.page.url}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        view = None
        with run.action('UI action', 'read the Checkout view') as a:
            settle = b.settle()
            view = read_view(b)
            a['observation'] = {**view, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut01-web-after-reset')
            run.capture(a, b.dom, 'sut01-web-checkout-text', '[data-testid="screen-checkout"]')
            run.capture(a, b.storage, 'sut01-web-storage-after-reset')
    finally:
        b.close()
    if view is None:
        return common.Result('INCONCLUSIVE', EXPECTED, 'the Checkout view could not be read', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
    observed = f"empty-cart view shown: {view['empty_cart_view']}; order lines: {view['order_lines']}"
    if view['order_lines']:
        status = 'FAILURE'
    elif view['empty_cart_view']:
        status = 'SUCCESS'
    else:
        status = 'INCONCLUSIVE'
    return common.Result(status, EXPECTED, observed, RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
