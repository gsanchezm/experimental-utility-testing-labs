"""E03-CS001-SUT03-WEB (README section 4.4). DRAFT (operation OP-PREP-E03)."""
import urllib.parse

from . import common, instance, web

MODALITY, PLATFORM = 'Web UI Functional', 'web'
RESET_MECHANISMS = ['SESSION_RESET']
ESTABLISHMENT_MECHANISMS = ['PREDEFINED_ACCOUNT', 'UI_FLOW']
EXPECTED = "after 'Logout', the closed-cart bag shows 0 (UI_STATE oracle, the mapping's disclosed deviation)"
CITATIONS = ['experiments/scenario-mappings/CS-001.yaml (SUT-03 entry)', 'SUT03-EV-0001', 'SUT03-EV-0030', 'SUT03-EV-0031', 'SUT03-EV-0032',
             'src/components/FloatChart/index.jsx:128-136@7ab934d', 'src/services/store.js:6-31@7ab934d']
BAG = '.bag--float-cart-closed .bag__quantity'


def components(run):
    return instance.components(run, [('web', 'web')])


def products_in(state):
    try:
        return (state or {}).get('cart', {}).get('products')
    except AttributeError:
        return None


def run(run):
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.step('precondition', 'sign in demouser at {web}/signin', ['PREDEFINED_ACCOUNT']) as s:
            status = b.goto(site + '/signin')
            s['observation'] = {'status': status, 'navigator.connection.effectiveType':
                                b.page.evaluate('() => (navigator.connection && navigator.connection.effectiveType) || null')}
            b.page.locator('#username').click()
            b.page.get_by_text('demouser', exact=True).click()
            b.page.locator('#password').click()
            b.page.get_by_text('testingisfun99', exact=True).click()
            b.page.locator('#login-btn').click()
            b.page.wait_for_url(lambda u: urllib.parse.urlparse(u).path == '/', timeout=web.NAV_TIMEOUT_MS)
            b.page.locator('span#signin', has_text='Logout').wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            s['observation']['url'] = b.page.url
        with run.step('declared-starting-state', 'closed-cart bag and sessionStorage state before the establishment') as s:
            b.page.locator(BAG).wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            state = web.parse(web.session_storage(b, 'state'))
            s['observation'] = {'bag_quantity': b.page.locator(BAG).inner_text().strip(), 'sessionStorage.state.cart.products': products_in(state)}
            run.capture(s, b.storage, 'sut03-storage-start')
        o = s['observation']
        run.declare_starting_state('the closed-cart bag shows 0; sessionStorage state, when present, holds cart.products [] (src/components/FloatChart/index.jsx:128-136; src/services/store.js:6-31)',
                                   CITATIONS, o, o['bag_quantity'] == '0' and o['sessionStorage.state.cart.products'] in (None, []))
        with run.step('establishment', 'buy button of product 1, then close the self-opened float cart', ['UI_FLOW']) as s:
            b.page.locator('div.shelf-item[id="1"] .shelf-item__buy-btn').click()
            b.page.locator('.float-cart__close-btn').click()
            b.page.locator('.bag--float-cart-closed').wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            s['observation'] = {'float_cart_closed': True}
        with run.step('pre-reset-verification', 'closed-cart bag shows 1') as s:
            q = b.page.locator(BAG).inner_text().strip()
            s['observation'] = {'bag_quantity': q}
            if q != '1':
                s['outcome'] = 'FAILURE'
            run.capture(s, b.shot, 'sut03-pre-reset')
            run.capture(s, b.storage, 'sut03-storage-pre-reset')
        with run.action('reset action', "click 'Logout' (span#signin); its own handler clears the session store and routes to /") as a:
            b.page.locator('span#signin', has_text='Logout').click()
            b.page.wait_for_url(lambda u: urllib.parse.urlparse(u).path == '/' and not urllib.parse.urlparse(u).query, timeout=web.NAV_TIMEOUT_MS)
            a['observation'] = {'url': b.page.url}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.storage, 'sut03-storage-after-logout')
        q = None
        with run.action('UI action', 'read the closed-cart bag quantity') as a:
            settle = b.settle()
            q = b.page.locator(BAG).inner_text(timeout=web.ACTION_TIMEOUT_MS).strip()
            a['observation'] = {'bag_quantity': q, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut03-after-reset')
    finally:
        b.close()
    if q is None:
        return common.Result('INCONCLUSIVE', EXPECTED, 'the closed-cart bag could not be read', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
    return common.Result('SUCCESS' if q == '0' else 'FAILURE', EXPECTED, f'closed-cart bag quantity {q!r}', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
