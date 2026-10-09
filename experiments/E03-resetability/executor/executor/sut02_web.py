"""E03-CS001-SUT02-WEB (README section 4.3). DRAFT (operation OP-PREP-E03)."""
from . import common, instance, web

MODALITY, PLATFORM = 'Web UI Functional', 'web'
RESET_MECHANISMS = ['APP_DATA_CLEAR']
ESTABLISHMENT_MECHANISMS = ['PREDEFINED_ACCOUNT', 'UI_FLOW']
EXPECTED = "after 'Reset App State', the cart link shows no badge and reads \"Cart, empty\""
CITATIONS = ['experiments/scenario-mappings/CS-001.yaml (SUT-02 entry)', 'SUT02-EV-0002', 'src/utils/shopping-cart.js:39-52@60fdd63',
             'src/components/CartButton.jsx:24-42@60fdd63', 'src/components/DrawerMenu.jsx:20-23,152-164@60fdd63']


def components(run):
    return instance.components(run, [('web', 'web')])


def read_cart_link(b):
    link = b.page.locator('[data-test="shopping-cart-link"]')
    badge = b.page.locator('[data-test="shopping-cart-badge"]')
    return {'aria_label': link.get_attribute('aria-label'), 'badge_count': badge.count(),
            'badge_text': badge.first.inner_text() if badge.count() else None, 'cart-contents': web.local_storage(b, 'cart-contents')}


def run(run):
    site = instance.base(run.instance, 'web')
    b = web.Browser(run)
    try:
        with run.step('precondition', 'login standard_user at {web}/', ['PREDEFINED_ACCOUNT']) as s:
            status = b.goto(site + '/')
            b.page.locator('#user-name').fill('standard_user')
            b.page.locator('[data-test="password"]').fill('secret_sauce')
            b.page.locator('#login-button').click()
            b.page.wait_for_url('**/inventory.html', timeout=web.NAV_TIMEOUT_MS)
            s['observation'] = {'status': status, 'url': b.page.url}
        with run.step('declared-starting-state', 'cart link and cart-contents before the establishment') as s:
            s['observation'] = read_cart_link(b)
            run.capture(s, b.storage, 'sut02-storage-start')
        o = s['observation']
        run.declare_starting_state('localStorage cart-contents absent; the cart link reads "Cart, empty" without a badge (src/utils/shopping-cart.js:39-52; src/components/CartButton.jsx:24-42)',
                                   CITATIONS, o, o['cart-contents'] is None and o['aria_label'] == 'Cart, empty' and o['badge_count'] == 0)
        with run.step('establishment', 'click [data-test="add-to-cart-sauce-labs-backpack"]', ['UI_FLOW']) as s:
            b.page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
            s['observation'] = {'cart-contents': web.local_storage(b, 'cart-contents')}
        with run.step('pre-reset-verification', '[data-test="shopping-cart-badge"] text 1') as s:
            o = read_cart_link(b)
            s['observation'] = o
            if (o['badge_text'] or '').strip() != '1':
                s['outcome'] = 'FAILURE'
            run.capture(s, b.shot, 'sut02-pre-reset')
            run.capture(s, b.storage, 'sut02-storage-pre-reset')
        with run.action('navigation action', 'open the side drawer: click #react-burger-menu-btn') as a:
            b.page.locator('#react-burger-menu-btn').click()
            b.page.locator('#reset_sidebar_link').wait_for(state='visible', timeout=web.ACTION_TIMEOUT_MS)
            a['observation'] = {'reset_control_visible': True}
            a['outcome'] = 'SUCCESS'
        with run.action('reset action', "click 'Reset App State' (#reset_sidebar_link)") as a:
            b.page.locator('#reset_sidebar_link').click()
            a['outcome'] = 'SUCCESS'
            run.capture(a, web.local_storage, b, 'cart-contents', key='cart-contents after the click')
            run.capture(a, b.storage, 'sut02-storage-after-reset-click')
        o = None
        with run.action('UI action', 'read the cart link') as a:
            settle = b.settle()
            o = read_cart_link(b)
            a['observation'] = {**o, 'settle': settle}
            a['outcome'] = 'SUCCESS'
            run.capture(a, b.shot, 'sut02-after-reset')
            run.capture(a, b.dom, 'sut02-header-text', '.primary_header')
    finally:
        b.close()
    if o is None:
        return common.Result('INCONCLUSIVE', EXPECTED, 'the cart link could not be read', RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
    observed = f"badge elements {o['badge_count']}; aria-label {o['aria_label']!r}"
    ok = o['badge_count'] == 0 and o['aria_label'] == 'Cart, empty'
    return common.Result('SUCCESS' if ok else 'FAILURE', EXPECTED, observed, RESET_MECHANISMS, ESTABLISHMENT_MECHANISMS)
