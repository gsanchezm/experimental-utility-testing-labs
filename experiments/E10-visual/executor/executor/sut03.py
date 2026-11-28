"""E10 realizations on SUT-03 (web): E10-SUT03-WEB-IMAGE and E10-SUT03-WEB-SHIFT. DRAFT (operation OP-PREP-E10).

E10-SUT03-WEB-IMAGE. The ground-truth condition is the documented account `image_not_loading_user`: the thumbnail source of every product is
forced to an empty string (SUT03-EV-0001, -0021; src/components/Shelf/Product/index.js and src/constants/users.js at the pinned commit). State
A is `demouser`, State B `image_not_loading_user`; the account is chosen at the sign-in page (the E03 SUT-03 web realization: the react-select
`#username` and `#password`, then `#login-btn`), and the view `shelf` is the first screen of the shelf at `/`. The shelf is fetched after
mount, so the ready signal is the first `.shelf-item`; the settle check waits for the images inside the viewport (an empty source is a
complete image of natural width zero).

E10-SUT03-WEB-SHIFT. The ground-truth condition is the timer of pages/sut/ui/high-cls.jsx at the pinned commit: 4000 ms after the client-side
cookie check it sets the height, the padding and the content of `#shift-target` (SUT03-EV-0012, -0014, -0023). State A and State B are the
same page captured 2000 ms and 5500 ms after the document commit (E10-D-10); the area's own login page sets the cookie (the dummy credentials
its labels show), with no server round trip. The capture times are read as `performance.now()` of the measured document (capture.py).

Blocks per execution: starting-state = the sign-in page (IMAGE) or the login page of the test area (SHIFT) answers 200; method = three
captures A, B, A2 of the single view, each in a fresh context with its own login, then the two comparisons.
"""
import urllib.parse

from . import attempt, common, instance

SHELF_PASSWORD = 'testingisfun99'  # a documented dummy password that the sign-in page shows in its own list; clicked by its text, not registered as a secret
SUT_LOGIN_PASSWORD = 'password'  # the dummy credentials of /sut/login (shown in its labels); not registered as a secret: the word is part of every form field name
SUT_LOGIN_USER = 'testuser'
SESSION_COOKIE = 'sutSessionId'
LOGIN_BUDGET_MS = 30000
HYDRATION_BUDGET_MS = 10000
SPEC = common.Spec('Visual Testing', 'web', [('web', 'web')], True)


class Sut03Image(attempt.Realization):
    SPEC = SPEC

    def check_start(self, run):
        with run.step('starting-state', 'the sign-in page answers 200') as rec:
            obs = {'web_status': instance.http_status(self.site + '/signin')}
            rec['observation'] = obs
            if obs['web_status'] != 200:
                raise common.PhaseFailure('starting-state', f'the sign-in page did not answer 200: {obs}', label='START_SURFACE_NOT_READY')

    def activate(self, run, s, account, label):
        """The sign-in flow of the E03 SUT-03 web realization; the account is picked from the react-select list, the password by its text."""
        try:
            status = s.goto(self.site + '/signin', wait_until='load')
            s.page.locator('#username').click()
            s.page.get_by_text(account, exact=True).click()
            s.page.locator('#password').click()
            s.page.get_by_text(SHELF_PASSWORD, exact=True).click()
            s.page.locator('#login-btn').click()
            s.page.wait_for_url(lambda u: urllib.parse.urlparse(u).path == '/', timeout=LOGIN_BUDGET_MS)
            s.page.locator('span#signin', has_text='Logout').wait_for(state='visible', timeout=LOGIN_BUDGET_MS)
        except Exception as e:  # noqa: BLE001 - a sign-in that does not reach the signed-in shelf is an observation of the activation
            raise common.PhaseFailure('method', f'the sign-in of {account} did not reach the signed-in shelf: {e.__class__.__name__}: {e}',
                                      label='START_ACTIVATION_NOT_CONFIRMED') from e
        return {'account': account, 'signin_status': status, 'url_after_login': s.page.url, 'logout_visible': True}


class Sut03Shift(attempt.Realization):
    SPEC = SPEC

    def check_start(self, run):
        with run.step('starting-state', 'the login page of the test area answers 200') as rec:
            obs = {'web_status': instance.http_status(self.site + '/sut/login')}
            rec['observation'] = obs
            if obs['web_status'] != 200:
                raise common.PhaseFailure('starting-state', f'the login page of the test area did not answer 200: {obs}', label='START_SURFACE_NOT_READY')

    def activate(self, run, s, account, label):
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        try:
            s.goto(self.site + '/sut/login', wait_until='load')
            # The page is server-rendered: a click before the hydration submits the form natively (a GET with the credentials in the query string).
            # The form carries a React internal key once it is hydrated; the wait is bounded and its result is evidence.
            try:
                s.page.wait_for_function("() => { const f = document.querySelector('form'); return !!f && Object.keys(f).some((k) => k.startsWith('__react')); }",
                                         timeout=HYDRATION_BUDGET_MS)
                hydrated = True
            except PlaywrightTimeout:
                hydrated = False
            s.page.locator('#username-input').fill(account)
            s.page.locator('#password-input').fill(SUT_LOGIN_PASSWORD)
            s.page.locator('#login-submit-btn').click()
            s.page.wait_for_url('**/sut/dashboard', timeout=LOGIN_BUDGET_MS)
        except Exception as e:  # noqa: BLE001 - a login that does not reach the dashboard is an observation of the activation
            raise common.PhaseFailure('method', f'the login of {account} did not reach the dashboard: {e.__class__.__name__}: {e}',
                                      label='START_ACTIVATION_NOT_CONFIRMED') from e
        cookie = next((c for c in s.cookies() if c['name'] == SESSION_COOKIE), None)
        activation = {'account': account, 'session_cookie_present': cookie is not None, 'url_after_login': s.page.url, 'form_hydrated_before_click': hydrated}
        if cookie is None:
            raise common.PhaseFailure('method', f'the session cookie was not set: {activation}', label='START_ACTIVATION_NOT_CONFIRMED')
        return activation


REALIZATIONS = {'E10-SUT03-WEB-IMAGE': Sut03Image, 'E10-SUT03-WEB-SHIFT': Sut03Shift}
