"""E02 realizations for SUT-02 (Sauce Labs Demo Inventory, web). DRAFT (operation OP-PREP-E02).

The CS-003 selectors (login fields, login button, add-to-cart, cart link, cart badge) are those the E03 executor used and verified
on the pinned SUT-02 commit (experiments/E03-resetability/executor/README.md, section 4.3, DEVELOPMENT runs DV0006 and DV0007).
The CS-004 steps after the cart (the cart page checkout control and the checkout step-one view) are NOT in any E03 record or E01
row (the E01 row cited by CS-004 names the step files, not their selectors). Their selectors were read from the pinned source
(commit 60fdd634, read-only, from the local E01 audit clone; decision of 2026-11-06, manifests/campaign-execution-decisions-v3.yaml)
and are verified only by a DRY_RUN: src/pages/Cart.jsx:26,62-65 (cart container, checkout control), src/pages/CheckOutStepOne.jsx:66,70
(step-one title and container), src/components/HeaderContainer.jsx:45 (title element), src/utils/Constants.js:16-17 (routes).
"""
from . import common, instance, web

USER_NAME = '#user-name'
PASSWORD = '[data-test="password"]'
LOGIN_BUTTON = '#login-button'
ADD_BACKPACK = '[data-test="add-to-cart-sauce-labs-backpack"]'
CART_LINK = '[data-test="shopping-cart-link"]'
BADGE = '[data-test="shopping-cart-badge"]'
CITATIONS_CS003 = ['experiments/scenario-mappings/CS-003.yaml (SUT-02 entry)', 'SUT02-EV-0001', 'SUT02-EV-0002', 'SUT02-EV-0003',
                   'SUT02-EV-0004', 'SUT02-EV-0013', 'src/utils/shopping-cart.js:39-52@60fdd63', 'src/components/CartButton.jsx:24-42@60fdd63']
EXPECTED_CS003 = 'after the add-to-cart of one catalogue item, the cart badge shows 1'
MECH_CS003 = ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW']  # also the list of the CS-004 conditions; DIRECT_ROUTE is the first load, which every realization of this module marks DIRECT_ROUTE (OP-PREP-05: it was missing here and present for SUT-01 and SUT-04)
CART_PAGE = '[data-test="cart-contents-container"]'
CART_ITEM = '[data-test="inventory-item"]'
CART_ITEM_NAME = '[data-test="inventory-item-name"]'
CHECKOUT_CONTROL = '[data-test="checkout"]'
STEP_ONE = '[data-test="checkout-info-container"]'
STEP_ONE_TITLE = '[data-test="title"]'
STEP_ONE_TITLE_TEXT = 'Checkout: Your Information'
CITATIONS_CS004 = ['experiments/scenario-mappings/CS-004.yaml (SUT-02 entry)', 'SUT02-EV-0001', 'SUT02-EV-0002', 'SUT02-EV-0013',
                   'SUT02-EV-0018', 'src/components/CartButton.jsx:26,36-38@60fdd63', 'src/pages/Cart.jsx:26,62-65@60fdd63',
                   'src/pages/CheckOutStepOne.jsx:66,70@60fdd63', 'src/utils/Constants.js:16-17@60fdd63']
EXPECTED_CS004 = 'after the seeded add-to-cart of one catalogue item, the cart badge shows 1 and the checkout step-one view is presented (UI_STATE oracle limited to the badge and the entry view, as the mapping states)'


def components(run):
    return instance.components(run, [('web', 'web')])


def _wait_inventory(b):
    try:
        b.page.wait_for_url('**/inventory.html', timeout=web.NAV_TIMEOUT_MS)
        return True
    except Exception:  # noqa: BLE001 - a navigation that did not land is an observation: the action's outcome is FAILURE
        return False


def cs003_web(run):
    """CS-003, SUT-02 WEB. Counted: the first load of the login page, two fills and a submit (authentication), the add-to-cart click,
    and the badge read (6). The starting state is read after the first load (its check is not counted)."""
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.action('navigation action', 'open {web}/, the login page (the first load of the run; counted, HD-15 default)', 'DIRECT_ROUTE') as a:
            status = b.goto(site + '/')
            a['observation'] = {'status': status}
            a['outcome'] = 'SUCCESS' if status == 200 else 'FAILURE'
        with run.step('declared-starting-state', 'login form present; no cart badge; cart link aria-label "Cart, empty"') as s:
            visible = b.page.locator(USER_NAME).is_visible()
            badges = b.page.locator(BADGE).count()
            label = b.page.locator(CART_LINK).get_attribute('aria-label')
            s['observation'] = {'login_form_visible': visible, 'badge_count': badges, 'cart_link_aria_label': label}
        run.declare_starting_state('login form visible, no badge, cart link reads "Cart, empty" (src/components/CartButton.jsx:24-42@60fdd63)',
                                   CITATIONS_CS003, s['observation'], visible and badges == 0 and label == 'Cart, empty')
        with run.action('UI action', 'fill the documented username standard_user in the login form (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator(USER_NAME).fill('standard_user')
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'fill the documented password in the login form (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator(PASSWORD).fill('secret_sauce')
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'submit the login form; the page lands on /inventory.html (authentication)', 'PREDEFINED_ACCOUNT') as a:
            b.page.locator(LOGIN_BUTTON).click()
            landed = _wait_inventory(b)
            a['observation'] = {'url': b.page.url, 'landed_on_inventory': landed}
            a['outcome'] = 'SUCCESS' if landed else 'FAILURE'
        with run.action('UI action', 'click add-to-cart of the Sauce Labs Backpack (establishment)', 'UI_FLOW') as a:
            b.page.locator(ADD_BACKPACK).click()
            a['outcome'] = 'SUCCESS'
        with run.action('UI action', 'read the cart badge (verification)', None, verification=True) as a:
            settle = b.settle()
            count = b.page.locator(BADGE).count()
            text = b.page.locator(BADGE).inner_text().strip() if count else None
            a['observation'] = {'badge_text': text, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut02-after-establishment')
    finally:
        b.close()
    return common.Result('SUCCESS' if text == '1' else 'FAILURE', EXPECTED_CS003, f'cart badge text {text!r}', MECH_CS003)


def _wait_route(b, pattern):
    try:
        b.page.wait_for_url(pattern, timeout=web.NAV_TIMEOUT_MS)
        return True
    except Exception:  # noqa: BLE001 - a navigation that did not land is an observation: the action's outcome is FAILURE
        return False


def cs004_web(run):
    """CS-004, SUT-02 WEB. The seeding is the precondition, not counted (DP-1 SEEDED): the first load of the login page, the sign-in
    with the documented standard account, and the add-to-cart of one catalogue item, all through the app's own controls. Counted
    (4): the cart-badge read (verification), the open of the cart, the open of checkout step one, and the read of the step-one view
    (verification). The cart link and the checkout control are two operations (rule 2), so the count is one above the mapping's
    indicative 3. The committing steps of the checkout flow are not performed. The oracle is the badge and the entry view only
    (the SUT-02 entry of CS-004 states that no E01 row says whether the checkout views present the item lines)."""
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.step('precondition', 'first load of {web}/, the login page (not counted)', ['DIRECT_ROUTE']) as s:
            status = b.goto(site + '/')
            s['observation'] = {'first_load_status': status}
            if status != 200:
                s['outcome'] = 'FAILURE'
        with run.step('precondition', 'sign in with the documented standard_user account in the login form (not counted)', ['PREDEFINED_ACCOUNT']) as s:
            b.page.locator(USER_NAME).fill('standard_user')
            b.page.locator(PASSWORD).fill('secret_sauce')
            b.page.locator(LOGIN_BUTTON).click()
            landed = _wait_inventory(b)
            s['observation'] = {'url': b.page.url, 'landed_on_inventory': landed}
            if not landed:
                s['outcome'] = 'FAILURE'
        with run.step('precondition', 'one catalogue item (the Sauce Labs Backpack) added through its add-to-cart control (not counted)', ['UI_FLOW']) as s:
            b.page.locator(ADD_BACKPACK).click()
            b.page.locator(BADGE).wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            s['observation'] = {'badge_text': b.page.locator(BADGE).inner_text().strip()}
        with run.step('declared-starting-state', 'the cart holds the seeded item: badge text 1, cart link aria-label "Cart, 1 items", still on the inventory page') as s:
            badge = b.page.locator(BADGE).inner_text().strip() if b.page.locator(BADGE).count() else None
            label = b.page.locator(CART_LINK).get_attribute('aria-label')
            s['observation'] = {'badge_text': badge, 'cart_link_aria_label': label, 'url': b.page.url}
        run.declare_starting_state('the cart holds the seeded item: badge text 1 and cart link aria-label "Cart, 1 items" (src/components/CartButton.jsx:26,36-38@60fdd63); no checkout view opened',
                                   CITATIONS_CS004, s['observation'], badge == '1' and label == 'Cart, 1 items' and b.page.url.endswith('/inventory.html'))
        with run.action('UI action', 'read the cart badge for the seeded item (verification)', None, verification=True) as a:
            settle = b.settle()
            count = b.page.locator(BADGE).count()
            badge_text = b.page.locator(BADGE).inner_text().strip() if count else None
            a['observation'] = {'badge_text': badge_text, 'settle': settle}
            a['outcome'] = 'SUCCESS'
        with run.action('navigation action', 'click the cart link; the route changes to /cart.html (establishment)', 'UI_FLOW') as a:
            b.page.locator(CART_LINK).click()
            landed = _wait_route(b, '**/cart.html')
            if landed:
                b.page.locator(CART_PAGE).wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            a['observation'] = {'url': b.page.url, 'landed_on_cart': landed,
                                'cart_items': b.page.locator(CART_ITEM).count() if landed else None,
                                'cart_item_names': b.page.locator(CART_ITEM_NAME).all_inner_texts() if landed else None}
            a['outcome'] = 'SUCCESS' if landed else 'FAILURE'
        with run.action('navigation action', 'click the Checkout control of the cart page; the route changes to /checkout-step-one.html (establishment)', 'UI_FLOW') as a:
            b.page.locator(CHECKOUT_CONTROL).click()
            landed = _wait_route(b, '**/checkout-step-one.html')
            a['observation'] = {'url': b.page.url, 'landed_on_step_one': landed}
            a['outcome'] = 'SUCCESS' if landed else 'FAILURE'
        with run.action('UI action', 'read the checkout step-one view: its container and its title are presented (verification)', None, verification=True) as a:
            settle = b.settle()
            present = b.page.locator(STEP_ONE).is_visible()
            title = b.page.locator(STEP_ONE_TITLE).inner_text().strip() if b.page.locator(STEP_ONE_TITLE).count() else None
            a['observation'] = {'step_one_visible': present, 'title': title, 'url': b.page.url, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut02-cs004-step-one')
    finally:
        b.close()
    presented = bool(present) and title == STEP_ONE_TITLE_TEXT
    return common.Result('SUCCESS' if badge_text == '1' and presented else 'FAILURE', EXPECTED_CS004,
                         f'cart badge text {badge_text!r}; checkout step-one view presented {presented} (title {title!r})', MECH_CS003)


SPEC = {
    'E02-CS003-SUT02-WEB': common.Spec('Web UI Functional', 'web', MECH_CS003, EXPECTED_CS003, components, True),
    'E02-CS004-SUT02-WEB': common.Spec('Web UI Functional', 'web', MECH_CS003, EXPECTED_CS004, components, True),
}
