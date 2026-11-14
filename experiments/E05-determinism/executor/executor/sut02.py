"""E05 realizations on SUT-02 (web): E05-SUT02-WEB-01 and E05-SUT02-WEB-02. DRAFT (operation OP-PREP-E05).

Blocks per execution: reset = the surface's own control, 'Reset App State' in the side drawer (APP_DATA_CLEAR; E03 block 4.3), performed in every
execution on the persistent browser context of the job; starting-state check = the cart link reads 'Cart, empty' without a badge;
establishment = the first inventory item added (the E03 SUT-02 establishment); verification = the badge reads 1; stimulus = WEB-01: the next
add-to-cart control (F07); WEB-02: loading the inventory page as visual_user.

E05-SUT02-WEB-02 is NOT configured: its category set rests on a 'visual marker' (row SUT02-EV-0015) that no recorded source defines. The
SUT-02 audit holds no such row, and the only branch for visual_user in the files read at the pin is the random price (src/pages/Inventory.jsx
line 122, which the projection excludes). The marker is a decision for the START package; run.py refuses the condition until it is configured.
"""
from . import attempt, common, instance, web

PASSWORD = 'secret_sauce'
SPEC = common.Spec('Web UI Functional', 'web', ['APP_DATA_CLEAR'], ['PREDEFINED_ACCOUNT', 'UI_FLOW'], [('web', 'web')], True)
SPEC_WEB02 = common.Spec('Web UI Functional', 'web', ['APP_DATA_CLEAR'], ['PREDEFINED_ACCOUNT', 'UI_FLOW'], [('web', 'web')], False)
VISUAL_MARKER = None  # TBD at START: what S_VISUAL_MARKER_PRESENT observes (see the module docstring)
FIRST_ITEM = '[data-test="add-to-cart-sauce-labs-backpack"]'
NEXT_ITEM = '[data-test^="add-to-cart-"]'
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
        with run.step('establishment', f'click {FIRST_ITEM}', ['UI_FLOW']) as rec:
            self.b.page.locator(FIRST_ITEM).click()
            rec['observation'] = {'cart-contents': web.local_storage(self.b, 'cart-contents')}

    def verify_target(self, run):
        with run.step('verification', '[data-test="shopping-cart-badge"] text 1') as rec:
            o = self.read_cart_link()
            rec['observation'] = o
            if (o['badge_text'] or '').strip() != '1':
                rec['outcome'] = 'FAILURE'
            run.capture(rec, self.b.shot, 'sut02-pre-stimulus')


class Web01(Sut02):
    """Stimulus: add a second inventory item (the next add-to-cart control); read the badge."""

    def stimulus(self, run):
        b = self.b
        with run.observe('stimulus', 'click the next add-to-cart control, then read the cart badge') as rec:
            control = b.page.locator(NEXT_ITEM).first
            clicked = control.get_attribute('data-test')
            run.mark_stimulus_sent()
            control.click()
            settle = b.settle()
            o = self.read_cart_link()
            obs = {'clicked_control': clicked, 'badge_text': (o['badge_text'] or '').strip() or None, 'badge_count': o['badge_count'],
                   'aria_label': o['aria_label'], 'settle': settle}
            run.capture(rec, b.shot, 'sut02-after-stimulus')
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['badge_text'] == '2':
            return 'S_BADGE_2', f'badge 2 after clicking {obs["clicked_control"]}'
        if obs['badge_text'] == '1':
            return 'S_NO_CHANGE', f'badge still 1 after clicking {obs["clicked_control"]}'
        return 'S_BADGE_OTHER', f'badge {obs["badge_text"]!r} ({obs["badge_count"]} badge elements)'


class Web02(Sut02):
    """Stimulus: load the inventory page as visual_user. NOT configured (see the module docstring)."""
    SPEC = SPEC_WEB02

    def stimulus(self, run):
        raise NotImplementedError('E05-SUT02-WEB-02: the visual marker is not defined (decision of the START package)')

    def classify(self, run, obs):
        raise NotImplementedError('E05-SUT02-WEB-02: the visual marker is not defined (decision of the START package)')


REALIZATIONS = {'E05-SUT02-WEB-01': Web01, 'E05-SUT02-WEB-02': Web02}
