"""E02 realizations for SUT-03 (React Shopping Cart demo, web). DRAFT (operation OP-PREP-E02).

The CS-003 selectors and the sign-in steps are those the E03 executor used and verified on the pinned SUT-03 commit
(experiments/E03-resetability/executor/README.md, section 4.4, DEVELOPMENT run DV0008; executor/sut03_web.py). The CS-004
checkout entry (the float cart's checkout control) and the checkout view are NOT in any E03 record or E01 row. Their selectors
were read from the pinned source (commit 7ab934d7, read-only, from the local E01 audit clone; decision of 2026-11-06,
manifests/campaign-execution-decisions-v3.yaml) and are verified only by a DRY_RUN: src/components/FloatChart/index.jsx:80-88
(proceedToCheckout, route /checkout), :139-141 (header bag), :156,178 (footer and Checkout control), pages/checkout/index.jsx:148-171
(order summary, product list, title, quantity option).
"""
import urllib.parse

from . import common, instance, web

SIGNIN_BUTTON = '#login-btn'
BUY_PRODUCT_1 = 'div.shelf-item[id="1"] .shelf-item__buy-btn'
CLOSE_FLOAT_CART = '.float-cart__close-btn'
BAG_CLOSED = '.bag--float-cart-closed'
BAG = '.bag--float-cart-closed .bag__quantity'
CITATIONS_CS003 = ['experiments/scenario-mappings/CS-003.yaml (SUT-03 entry)', 'SUT03-EV-0001', 'SUT03-EV-0003', 'SUT03-EV-0005',
                   'SUT03-EV-0032', 'src/components/FloatChart/index.jsx:51-68,119-136@7ab934d', 'src/services/store.js:6-31@7ab934d']
EXPECTED_CS003 = 'after the buy of product 1 and the closing of the float cart, the closed-cart bag shows 1 (UI_STATE oracle, the mapping disclosed deviation)'
MECH_CS003 = ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW']  # also the list of the CS-004 conditions; DIRECT_ROUTE is the first load, which every realization of this module marks DIRECT_ROUTE (OP-PREP-05: it was missing here and present for SUT-01 and SUT-04)
FLOAT_CART_OPEN_CHECKOUT = '.float-cart--open .float-cart__footer .buy-btn'
FLOAT_CART_OPEN_BAG = '.float-cart--open .float-cart__header .bag__quantity'
ORDER_SUMMARY = '[data-test="cart"]'
SUMMARY_HEADING = '[data-test="cart"] .cart-section-heading'
PRODUCT_1_ITEM = '[data-test="cart"] li.productList-item[id="1"]'
PRODUCT_TITLE = '.product-title'
PRODUCT_OPTION = '.product-options .product-option'
CITATIONS_CS004 = ['experiments/scenario-mappings/CS-004.yaml (SUT-03 entry)', 'SUT03-EV-0001', 'SUT03-EV-0003', 'SUT03-EV-0005',
                   'SUT03-EV-0032', 'src/components/FloatChart/index.jsx:80-88,139-141,156,178@7ab934d', 'pages/checkout/index.jsx:148-171@7ab934d']
EXPECTED_CS004 = 'after the buy of product 1, the checkout view presents product 1 with quantity 1 in its order summary (UI_STATE oracle, the mapping disclosed deviation)'


def components(run):
    return instance.components(run, [('web', 'web')])


def _products(state):
    try:
        return (state or {}).get('cart', {}).get('products')
    except AttributeError:
        return None


def cs003_web(run):
    """CS-003, SUT-03 WEB. Counted: the load of the sign-in page (CS-003 entry step), username selection, password entry, sign-in
    (authentication), buy of product 1, closing the self-opened float cart (counted: an experimenter operation with an observable
    effect, rule 1), and the bag read (7). The bag exists only for a signed-in actor, so the starting-state read follows the
    sign-in (identity acquisition, not a state change)."""
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.action('navigation action', 'open {web}/signin, the sign-in page (the first load of the run; counted)', 'DIRECT_ROUTE') as a:
            status = b.goto(site + '/signin')
            a['observation'] = {'status': status}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.action('UI action', 'select the documented username demouser (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator('#username').click()
            b.page.get_by_text('demouser', exact=True).click()
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'enter the documented password (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator('#password').click()
            b.page.get_by_text('testingisfun99', exact=True).click()
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'submit the sign-in form; the route changes to / with Logout visible (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator(SIGNIN_BUTTON).click()
            landed = False
            try:
                b.page.wait_for_url(lambda u: urllib.parse.urlparse(u).path == '/', timeout=web.NAV_TIMEOUT_MS)
                b.page.locator('span#signin', has_text='Logout').wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
                landed = True
            except Exception:  # noqa: BLE001 - recorded as the action's FAILURE below
                landed = False
            a['observation'] = {'url': b.page.url, 'signed_in': landed}
            a['outcome'] = 'SUCCESS' if landed else 'FAILURE'
        with run.step('declared-starting-state', 'closed-cart bag shows 0; sessionStorage cart holds no products (after the sign-in)') as s:
            b.page.locator(BAG).wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            bag = b.page.locator(BAG).inner_text().strip()
            products = _products(web.parse(web.session_storage(b, 'state')))
            s['observation'] = {'bag_quantity': bag, 'sessionStorage.state.cart.products': products}
        run.declare_starting_state('the closed-cart bag shows 0 and sessionStorage holds no cart products (src/components/FloatChart/index.jsx:128-136@7ab934d; src/services/store.js:6-31@7ab934d)',
                                   CITATIONS_CS003, s['observation'], bag == '0' and products in (None, []))
        with run.action('UI action', 'click the buy control of product 1 (establishment)', 'UI_FLOW') as a:
            b.page.locator(BUY_PRODUCT_1).click()
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'close the float cart that the buy opened (establishment; default view)', 'UI_FLOW') as a:
            b.page.locator(CLOSE_FLOAT_CART).click()
            b.page.locator(BAG_CLOSED).wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'read the closed-cart bag quantity (verification)', None, verification=True) as a:
            settle = b.settle()
            quantity = b.page.locator(BAG).inner_text(timeout=web.ACTION_TIMEOUT_MS).strip()
            a['observation'] = {'bag_quantity': quantity, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut03-after-establishment')
    finally:
        b.close()
    return common.Result('SUCCESS' if quantity == '1' else 'FAILURE', EXPECTED_CS003, f'closed-cart bag quantity {quantity!r}', MECH_CS003)


def _checkout_control_shown(text):
    """The control reads 'Checkout' in the markup and the page's CSS renders it in upper case (DRY_RUN finding of 2026-11-09), so it is compared without regard to case."""
    return isinstance(text, str) and text.strip().lower() == 'checkout'


def cs004_web(run):
    """CS-004, SUT-03 WEB. The seeding is the precondition, not counted (DP-1 SEEDED): the load of the sign-in page, the sign-in with
    the documented demouser account, and the buy of product 1, which opens the float cart (all through the app's own controls).
    Counted (2): the click on the Checkout control of the open float cart, which routes to /checkout, and the read of the order summary
    of the checkout view (verification). The order submission, which calls the checkout API gate, is not performed. The oracle is UI
    state only: the cart is never reflected in any API response (the SUT-03 entry of CS-004, SUT03-EV-0032)."""
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.step('precondition', 'first load of {web}/signin, the sign-in page (not counted)', ['DIRECT_ROUTE']) as s:
            status = b.goto(site + '/signin')
            s['observation'] = {'first_load_status': status}
            if status != 200:
                s['outcome'] = 'FAILURE'
        with run.step('precondition', 'select the documented demouser, enter the documented password, and sign in (not counted)', ['PREDEFINED_ACCOUNT']) as s:
            b.page.locator('#username').click()
            b.page.get_by_text('demouser', exact=True).click()
            b.page.locator('#password').click()
            b.page.get_by_text('testingisfun99', exact=True).click()
            b.page.locator(SIGNIN_BUTTON).click()
            landed = False
            try:
                b.page.wait_for_url(lambda u: urllib.parse.urlparse(u).path == '/', timeout=web.NAV_TIMEOUT_MS)
                b.page.locator('span#signin', has_text='Logout').wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
                landed = True
            except Exception:  # noqa: BLE001 - recorded as the step's failure below
                landed = False
            s['observation'] = {'url': b.page.url, 'signed_in': landed}
            if not landed:
                s['outcome'] = 'FAILURE'
        with run.step('precondition', 'the buy control of product 1 clicked; the float cart opens with the Checkout control (not counted)', ['UI_FLOW']) as s:
            b.page.locator(BUY_PRODUCT_1).click()
            b.page.locator(FLOAT_CART_OPEN_CHECKOUT).wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            s['observation'] = {'checkout_control_text': b.page.locator(FLOAT_CART_OPEN_CHECKOUT).inner_text().strip()}
        with run.step('declared-starting-state', 'the open float cart holds the seeded product: header bag quantity 1, one product in sessionStorage, Checkout control present') as s:
            bag = b.page.locator(FLOAT_CART_OPEN_BAG).inner_text().strip()
            products = _products(web.parse(web.session_storage(b, 'state')))
            control = b.page.locator(FLOAT_CART_OPEN_CHECKOUT).inner_text().strip()
            s['observation'] = {'bag_quantity': bag, 'sessionStorage.state.cart.products': products, 'checkout_control_text': control}
        run.declare_starting_state('the open float cart holds the seeded product: header bag quantity 1, one product in sessionStorage, Checkout control present (src/components/FloatChart/index.jsx:139-141,156,178@7ab934d)',
                                   CITATIONS_CS004, s['observation'], bag == '1' and isinstance(products, list) and len(products) == 1 and _checkout_control_shown(control))
        with run.action('navigation action', 'click the Checkout control of the float cart; the route changes to /checkout (establishment)', 'UI_FLOW') as a:
            b.page.locator(FLOAT_CART_OPEN_CHECKOUT).click()
            landed = False
            try:
                b.page.wait_for_url(lambda u: urllib.parse.urlparse(u).path == '/checkout', timeout=web.NAV_TIMEOUT_MS)
                b.page.locator(ORDER_SUMMARY).wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
                landed = True
            except Exception:  # noqa: BLE001 - recorded as the action's FAILURE below
                landed = False
            a['observation'] = {'url': b.page.url, 'landed_on_checkout': landed}
            a['outcome'] = 'SUCCESS' if landed else 'FAILURE'
        with run.action('UI action', 'read the order summary of the checkout view for the seeded product and its quantity (verification)', None, verification=True) as a:
            settle = b.settle()
            items = b.page.locator(PRODUCT_1_ITEM).count()
            titles = b.page.locator(f'{PRODUCT_1_ITEM} {PRODUCT_TITLE}').all_inner_texts()
            options = b.page.locator(f'{PRODUCT_1_ITEM} {PRODUCT_OPTION}').all_inner_texts()
            quantity = options[1].strip() if len(options) > 1 else None
            heading = b.page.locator(SUMMARY_HEADING).first.inner_text().strip() if b.page.locator(SUMMARY_HEADING).count() else None
            a['observation'] = {'product_1_items': items, 'titles': titles, 'options': options, 'quantity': quantity, 'heading': heading, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut03-cs004-checkout')
    finally:
        b.close()
    return common.Result('SUCCESS' if items == 1 and quantity == '1' else 'FAILURE', EXPECTED_CS004,
                         f'order-summary items for product 1: {items}; quantity {quantity!r}; heading {heading!r}', MECH_CS003)


SPEC = {
    'E02-CS003-SUT03-WEB': common.Spec('Web UI Functional', 'web', MECH_CS003, EXPECTED_CS003, components, True),
    'E02-CS004-SUT03-WEB': common.Spec('Web UI Functional', 'web', MECH_CS003, EXPECTED_CS004, components, True),
}
