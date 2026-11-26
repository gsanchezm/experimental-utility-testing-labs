"""E08 realization on SUT-02 (web): E08-SUT02-WEB-BLOCK. DRAFT (operation OP-PREP-E08).

The ground-truth condition is the documented account `performance_glitch_user`: when it is the session user, the inventory page runs a
synchronous busy-wait loop of 5000 ms while it renders (SUT02-EV-0001, -0011; src/pages/Inventory.jsx at the pinned commit, which calls
startPerformanceGlitch(5000) in the body of the component). Static reading V-2 (configuration draft, section 4c): the wait is in the render of
the page, so it is one task of the main thread that the Long Tasks API reports (the browser reports every task longer than 50 ms).

Blocks per execution: starting-state = the web surface answers 200; method = three loads of /inventory.html, each in a fresh context: the
account logs in through the login form of the application (documented flow; the session is a cookie), the inventory list is awaited (for the
glitch account the application blocks for 5 s while it renders after the login, and that block is not measured), and then the measured
navigation to /inventory.html is a full document load with the measurement script present from the start of the document; the metric is the
longest long task of that document (conditions-draft.json, metric longest_longtask_ms).
"""
from . import attempt, common, instance

PASSWORD = 'secret_sauce'  # the shared password of the six fixed accounts (SUT02-EV-0001; src/utils/Constants.js)
SESSION_COOKIE = 'session-username'
LOGIN_BUDGET_MS = 60000
SETTLE_AFTER_READY_MS = 1000
SPEC = common.Spec('Performance', 'web', [('web', 'web')], True)


class Sut02Web(attempt.Realization):
    SPEC = SPEC

    @property
    def site(self):
        return instance.base(self.job.instance, 'web')

    def check_start(self, run):
        with run.step('starting-state', 'the web surface answers 200') as rec:
            obs = {'web_status': instance.http_status(self.site + '/')}
            rec['observation'] = obs
            if obs['web_status'] != 200:
                raise common.PhaseFailure('starting-state', f'the web surface did not answer 200: {obs}', label='START_SURFACE_NOT_READY')

    def login(self, run, s, account):
        """The documented login form; returns the activation record (the session cookie is the activation of the account)."""
        run.scrub.secret(PASSWORD)
        s.goto(self.site + '/', wait_until='load')
        s.page.locator('#user-name').fill(account)
        s.page.locator('[data-test="password"]').fill(PASSWORD)
        s.page.locator('#login-button').click()
        # the application renders the inventory page after the login (a glitch account blocks 5 s there); this wait is not measured
        s.page.wait_for_selector('[data-test="inventory-list"]', timeout=LOGIN_BUDGET_MS)
        cookie = next((c['value'] for c in s.cookies() if c['name'] == SESSION_COOKIE), None)
        return {'account': account, 'session_cookie_value': cookie, 'url_after_login': s.page.url}

    def load(self, run, role):
        c = self.job.c
        side = self.side(role)
        label = self.next_label(role)
        s = self.b.session(run, label, c['watch'])
        try:
            try:
                activation = self.login(run, s, side['account'])
            except Exception as e:  # noqa: BLE001 - a login that does not reach the inventory list is an observation of the activation
                raise common.PhaseFailure('method', f'the login of {side["account"]} did not reach the inventory list: {e.__class__.__name__}: {e}',
                                          label='START_ACTIVATION_NOT_CONFIRMED') from e
            if activation['session_cookie_value'] != side['account']:
                raise common.PhaseFailure('method', f'the session cookie does not name the account: {activation}', label='START_ACTIVATION_NOT_CONFIRMED')
            run.jsonfile(f'{label}-activation', activation)
            self.begin_measurement(run)
            status = s.goto(self.site + side['page'], wait_until='commit')
            ready = self.wait_ready(s, c['required_ready'], c['ready_timeout_ms'])
            s.page.wait_for_timeout(SETTLE_AFTER_READY_MS)
            return self.finish_load(run, s, role, label, side['account'], side['page'], status, {'ready_within_budget': ready})
        finally:
            s.close()


REALIZATIONS = {'E08-SUT02-WEB-BLOCK': Sut02Web}
