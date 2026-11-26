"""E08 realizations on SUT-03 (web): E08-SUT03-WEB-LCP and E08-SUT03-WEB-CLS. DRAFT (operation OP-PREP-E08).

The ground-truth conditions are two pages of the SUT's own performance test area (pages/sut/ui/ at the pinned commit): high-lcp.jsx delays
the largest element 3000 ms (a timer, then an image from an external host, SUT03-EV-0013) and high-cls.jsx changes the height of a block at
4000 ms (SUT03-EV-0012); zero-cls.jsx renders everything at once and is the paired baseline of both (SUT03-EV-0014). All three pages check a
client-side cookie that the area's own login page sets (/sut/login, the dummy credentials its label shows), with no server round trip.
Static readings V-3 and V-4 (configuration draft, section 4c).

Blocks per execution: starting-state = the web surface answers 200; method = three loads of the condition's pages, each in a fresh context: the
login form of the area sets the cookie (documented flow), then the measured navigation to the page is a full document load; the page is
observed for the fixed window of conditions-draft.json (observe_window_ms) counted from the start of the document, then the raw snapshot
is read. The metrics are computed afterwards (classify.py).
"""
from . import attempt, common, instance

USERNAME = 'testuser'
PASSWORD = 'password'  # the dummy credentials of /sut/login (shown in its labels); not registered as a secret: the word is part of the page and of every form field name
SESSION_COOKIE = 'sutSessionId'
LOGIN_BUDGET_MS = 30000
HYDRATION_BUDGET_MS = 10000
SPEC = common.Spec('Performance', 'web', [('web', 'web')], True)


class Sut03Web(attempt.Realization):
    SPEC = SPEC

    @property
    def site(self):
        return instance.base(self.job.instance, 'web')

    def check_start(self, run):
        with run.step('starting-state', 'the web surface answers 200') as rec:
            obs = {'web_status': instance.http_status(self.site + '/sut/login')}
            rec['observation'] = obs
            if obs['web_status'] != 200:
                raise common.PhaseFailure('starting-state', f'the login page of the performance test area did not answer 200: {obs}',
                                          label='START_SURFACE_NOT_READY')

    def login(self, s, account):
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
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
        s.page.locator('#password-input').fill(PASSWORD)
        s.page.locator('#login-submit-btn').click()
        s.page.wait_for_url('**/sut/dashboard', timeout=LOGIN_BUDGET_MS)
        cookie = next((c for c in s.cookies() if c['name'] == SESSION_COOKIE), None)
        return {'account': account, 'session_cookie_present': cookie is not None, 'url_after_login': s.page.url, 'form_hydrated_before_click': hydrated}

    def load(self, run, role):
        c = self.job.c
        side = self.side(role)
        label = self.next_label(role)
        window = self.job.cfg['observe_window_ms']
        s = self.b.session(run, label, c['watch'])
        try:
            try:
                activation = self.login(s, side['account'])
            except Exception as e:  # noqa: BLE001 - a login that does not reach the dashboard is an observation of the activation
                raise common.PhaseFailure('method', f'the login of {side["account"]} did not reach the dashboard: {e.__class__.__name__}: {e}',
                                          label='START_ACTIVATION_NOT_CONFIRMED') from e
            if not activation['session_cookie_present']:
                raise common.PhaseFailure('method', f'the session cookie was not set: {activation}', label='START_ACTIVATION_NOT_CONFIRMED')
            run.jsonfile(f'{label}-activation', activation)
            self.begin_measurement(run)
            status = s.goto(self.site + side['page'], wait_until='commit')
            s.page.wait_for_function('(w) => performance.now() >= w', arg=window, timeout=window + 20000)
            return self.finish_load(run, s, role, label, side['account'], side['page'], status, {'observe_window_ms': window})
        finally:
            s.close()


REALIZATIONS = {'E08-SUT03-WEB-LCP': Sut03Web, 'E08-SUT03-WEB-CLS': Sut03Web}
