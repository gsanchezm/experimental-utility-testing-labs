"""E04 realizations on SUT-02 (web): E04-SUT02-WEB-01 (establishment-only; E05 counterpart E05-SUT02-WEB-01). DRAFT (operation OP-PREP-E04).

Blocks per attempt: reset = the surface's own control, 'Reset App State' in the side drawer (APP_DATA_CLEAR; E03 block 4.3), performed in every
attempt on the persistent browser context of the job; starting-state check = the cart link reads 'Cart, empty' without a badge; establishment =
the first inventory item added (the E03 SUT-02 establishment); verification = the badge reads 1. The stimulus of the E05 counterpart (the next
add-to-cart control, F07) is removed.

E05-SUT02-WEB-02 is not carried over: it was retired before the E05 START (its visual marker is defined by no recorded source; decisions-v9),
and the E04 conditions mirror the thirteen configured E05 conditions only.
"""
from . import attempt, common, instance, web

PASSWORD = 'secret_sauce'
SPEC = common.Spec('Web UI Functional', 'web', ['APP_DATA_CLEAR'], ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'], [('web', 'web')], True)
FIRST_ITEM = '[data-test="add-to-cart-sauce-labs-backpack"]'
EMPTY_CONTENTS = (None, '', '[]')


class Sut02(attempt.Realization):
    SPEC = SPEC

    def __init__(self, job):
        super().__init__(job)
        self.account = job.c['account']

    def open(self):
        self.b = web.Browser(self.job)

    def bind(self, run):
        self.b.bind(run)

    def end(self, run):
        self.b.flush()

    def close(self):
        self.b.close()

    @property
    def site(self):
        return instance.base(self.job.instance, 'web')

    def read_cart_link(self):
        b = self.b
        link, badge = b.page.locator('[data-test="shopping-cart-link"]'), b.page.locator('[data-test="shopping-cart-badge"]')
        return {'aria_label': link.get_attribute('aria-label'), 'badge_count': badge.count(),
                'badge_text': badge.first.inner_text() if badge.count() else None, 'cart-contents': web.local_storage(b, 'cart-contents')}

    def reset(self, run):
        b = self.b
        with run.step('reset', "ensure the logged-in session, open the side drawer, click 'Reset App State'", ['APP_DATA_CLEAR']) as rec:
            status = b.goto(self.site + '/inventory.html')
            login_form_shown = b.page.locator('#user-name').count() > 0
            if login_form_shown:
                run.scrub.secret(PASSWORD)
                b.page.locator('#user-name').fill(self.account)
                b.page.locator('[data-test="password"]').fill(PASSWORD)
                b.page.locator('#login-button').click()
                b.page.wait_for_url('**/inventory.html', timeout=web.NAV_TIMEOUT_MS)
            rec['observation'] = {'status': status, 'url': b.page.url, 'login_form_was_shown': login_form_shown}
            b.page.locator('#react-burger-menu-btn').click()
            opened = b.visible(b.page.locator('#reset_sidebar_link'))
            rec['observation']['reset_control_visible'] = opened
            if not opened:
                rec['outcome'] = 'FAILURE'
                return
            b.page.locator('#reset_sidebar_link').click()
            rec['observation']['settle'] = b.settle()
            run.capture(rec, web.local_storage, b, 'cart-contents', key='cart-contents after the click')
            run.capture(rec, b.storage, 'sut02-storage-after-reset')

    def check_start(self, run):
        with run.step('starting-state', "the cart link reads 'Cart, empty' with no badge") as rec:
            o = self.read_cart_link()
            rec['observation'] = o
            if not (o['aria_label'] == 'Cart, empty' and o['badge_count'] == 0 and o['cart-contents'] in EMPTY_CONTENTS):
                rec['outcome'] = 'FAILURE'
            run.capture(rec, self.b.shot, 'sut02-start')

    def establish(self, run):
        """The inventory page keeps the 'Remove' state of the buttons it showed before 'Reset App State' until it is loaded again (observed in the E05 first DRY_RUN: the cart badge was gone, the add control of the first item was not there), so the establishment loads the page first."""
        with run.step('establishment', f'load {{web}}/inventory.html, then click {FIRST_ITEM}', ['DIRECT_ROUTE', 'UI_FLOW']) as rec:
            status = self.b.goto(self.site + '/inventory.html')
            self.b.page.locator(FIRST_ITEM).click()
            rec['observation'] = {'status': status, 'cart-contents': web.local_storage(self.b, 'cart-contents')}

    def verify_target(self, run):
        with run.step('verification', '[data-test="shopping-cart-badge"] text 1') as rec:
            o = self.read_cart_link()
            rec['observation'] = o
            if (o['badge_text'] or '').strip() != '1':
                rec['outcome'] = 'FAILURE'
            run.capture(rec, self.b.shot, 'sut02-target-state')


class Web01(Sut02):
    """E04-SUT02-WEB-01 (establishment-only): the target state is one inventory item in the cart (badge 1); no stimulus."""


REALIZATIONS = {'E04-SUT02-WEB-01': Web01}
