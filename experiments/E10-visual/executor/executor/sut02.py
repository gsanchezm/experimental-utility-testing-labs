"""E10 realization on SUT-02 (web): E10-SUT02-WEB-VISUAL. DRAFT (operation OP-PREP-E10).

The ground-truth condition is the documented account `visual_user` (SUT02-EV-0001, -0015; src/utils/Credentials.js, src/components/
HeaderContainer.jsx, DrawerMenu.jsx and src/pages/Cart.jsx at the pinned commit): for that account the cart icon container, the burger and
close icons of the drawer and the checkout button receive the classes visual_failure and btn_visual_failure. The checkout button is on the
cart page (route /cart.html) and the close icon exists only in the open drawer, so the condition has three views (E10-D-9): `inventory`
(cart icon container and burger icon), `cart` (checkout button) and `menu_open` (close icon, after a click on the burger icon).

Blocks per execution: starting-state = the web surface answers 200; method = for each view three captures A (standard_user), B
(visual_user) and A2 (standard_user), each in a fresh context: the account logs in through the login form of the application (documented
flow; the session is a cookie), then the measured navigation to the view's route is a full document load, the view's steps run, and the
capture is taken after the ready signal and the settle check. The random prices and the other effects of visual_user that the E01 record
does not name are unlisted differences (classify.py), never a detection.
"""
from . import attempt, common, instance

PASSWORD = 'secret_sauce'  # the shared password of the six fixed accounts (SUT02-EV-0001; src/utils/Constants.js)
SESSION_COOKIE = 'session-username'
LOGIN_BUDGET_MS = 60000
SPEC = common.Spec('Visual Testing', 'web', [('web', 'web')], True)


class Sut02Web(attempt.Realization):
    SPEC = SPEC

    def check_start(self, run):
        with run.step('starting-state', 'the web surface answers 200') as rec:
            obs = {'web_status': instance.http_status(self.site + '/')}
            rec['observation'] = obs
            if obs['web_status'] != 200:
                raise common.PhaseFailure('starting-state', f'the web surface did not answer 200: {obs}', label='START_SURFACE_NOT_READY')

    def activate(self, run, s, account, label):
        """The documented login form; the session cookie is the activation of the account."""
        run.scrub.secret(PASSWORD)
        try:
            s.goto(self.site + '/', wait_until='load')
            s.page.locator('#user-name').fill(account)
            s.page.locator('[data-test="password"]').fill(PASSWORD)
            s.page.locator('#login-button').click()
            # the application renders the inventory page after the login; this wait is not a capture
            s.page.wait_for_selector('[data-test="inventory-list"]', timeout=LOGIN_BUDGET_MS)
        except Exception as e:  # noqa: BLE001 - a login that does not reach the inventory list is an observation of the activation
            raise common.PhaseFailure('method', f'the login of {account} did not reach the inventory list: {e.__class__.__name__}: {e}',
                                      label='START_ACTIVATION_NOT_CONFIRMED') from e
        cookie = next((c['value'] for c in s.cookies() if c['name'] == SESSION_COOKIE), None)
        activation = {'account': account, 'session_cookie_value': cookie, 'url_after_login': s.page.url}
        if cookie != account:
            raise common.PhaseFailure('method', f'the session cookie does not name the account: {activation}', label='START_ACTIVATION_NOT_CONFIRMED')
        return activation


REALIZATIONS = {'E10-SUT02-WEB-VISUAL': Sut02Web}
