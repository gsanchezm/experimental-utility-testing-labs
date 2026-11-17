"""E04 realizations on SUT-01: E04-SUT01-API-01 to -06 (api) and E04-SUT01-WEB-01 (web). DRAFT (operation OP-PREP-E04); pending the START package.

Establishment-only derivation (operation OP-PREP-E04) of the E05 realizations of the same condition, which were written under operation OP-PREP-E05. Reset, starting-state check, establishment
and target-state verification are those of the E05 realization, unchanged; the stimulus and classification blocks are removed.

* reset: API-02 to API-05 clear the caller's session (POST /api/session/reset, mechanisms API_RESET and SESSION_RESET, the E03 SUT-01 block 4.1);
  API-01, API-06 and WEB-01 restart the backend process, because orders persist beyond that reset (E05 decision D-03 b, instance.json process
  block; mechanism ENVIRONMENT_RESTART), and log in again, because the restart clears the in-memory session store.
* starting-state check: the server cart is empty (backend/database.py:139-148). establishment: one p02 line (POST /api/cart).
  verification: the session shows exactly that line (web: the Checkout view shows order-item-p02).
* The condition's account logs in at every attempt; every documented test account uses the password of the SUT-01 README (HD-E09-A;
  backend/constants.py lines 21-61, SOURCE-READS-03).
"""
import json

from . import attempt, common, instance, web

PASSWORD = 'pizza123'
LINE = {'pizza_id': 'p02', 'quantity': 1, 'size': 'small', 'toppings': []}
SPEC_RESET = common.Spec('API', 'api', ['API_RESET', 'SESSION_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api')], True)
SPEC_RESTART = common.Spec('API', 'api', ['ENVIRONMENT_RESTART'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api')], True)
SPEC_WEB = common.Spec('Web UI Functional', 'web', ['ENVIRONMENT_RESTART'], ['PREDEFINED_ACCOUNT', 'API_SEED', 'DIRECT_ROUTE'],
                       [('web', 'web'), ('api', 'api')], True)
ORDERS_NOTE = 'orders persist beyond the session reset (SUT01-EV-0006); the backend process is restarted between executions (D-03 b)'


class Sut01Api(attempt.Realization):
    SPEC = SPEC_RESET

    def __init__(self, job):
        super().__init__(job)
        self.account = job.c['account']
        self.restart = job.c['reset_between_attempts'] == 'process_restart'
        if self.restart and self.SPEC is SPEC_RESET:
            self.SPEC = SPEC_RESTART

    def api(self):
        return instance.base(self.job.instance, 'api')

    def auth(self, run):
        return {'Authorization': f'Bearer {self.carry["token"]}'}

    def login(self, run, label='sut01-login', username=None):
        run.scrub.secret(PASSWORD)
        r = run.http('POST', f'{self.api()}/api/auth/login', {'username': username or self.account, 'password': PASSWORD}, label=label)
        try:
            body = r.json() if r.status == 200 else {}
        except ValueError:
            body = {}
        token = body.get('access_token')
        run.scrub.secret(token)
        return r, token, body

    def session(self, run, label):
        r = run.http('GET', f'{self.api()}/api/session', headers=self.auth(run), label=label)
        try:
            body = r.json() if r.status == 200 else None
        except ValueError:
            body = None
        return r, body

    def new_session(self, run, rec):
        """Log in (the session boundary); the token is the carry of this execution only."""
        r, token, body = self.login(run)
        rec['evidence'].append(r.evidence)
        rec['observation'] = {**(rec.get('observation') or {}), 'login_status': r.status, 'token_received': bool(token), 'behavior': body.get('behavior')}
        if not token:
            rec['outcome'] = 'FAILURE'
            return False
        self.carry = {'token': token, 'login': body}
        return True

    def reset(self, run):
        if self.restart:
            with run.step('reset', 'restart the backend process (SIGTERM to the process group, port refused, start in a new session and group, readiness)',
                          ['ENVIRONMENT_RESTART']) as rec:
                instance.restart(run, rec)
            with run.step('reset', 'POST /api/auth/login after the restart (the restart clears the in-memory session store)', ['PREDEFINED_ACCOUNT']) as rec:
                self.new_session(run, rec)
            return
        with run.step('reset', 'POST /api/auth/login, then POST /api/session/reset with the session token', ['API_RESET', 'SESSION_RESET']) as rec:
            if not self.new_session(run, rec):
                return
            r = run.http('POST', f'{self.api()}/api/session/reset', headers=self.auth(run), label='sut01-reset')
            rec['evidence'].append(r.evidence)
            rec['observation']['reset_status'] = r.status
            if r.status != 200:
                rec['outcome'] = 'FAILURE'

    def check_start(self, run):
        with run.step('starting-state', 'GET /api/session: the cart is empty') as rec:
            r, body = self.session(run, 'sut01-session-start')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'cart_items': (body or {}).get('cart_items'), 'country_code': (body or {}).get('country_code')}
            if body is None or body.get('cart_items') != []:
                rec['outcome'] = 'FAILURE'

    def establish(self, run):
        with run.step('establishment', 'POST /api/cart with one p02 line', ['API_SEED']) as rec:
            r = run.http('POST', f'{self.api()}/api/cart', {'items': [LINE]}, headers=self.auth(run), label='sut01-seed-cart')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status}
            if r.status != 200:
                rec['outcome'] = 'FAILURE'

    def verify_target(self, run):
        with run.step('verification', 'GET /api/session shows exactly the p02 line') as rec:
            r, body = self.session(run, 'sut01-session-target-state')
            rec['evidence'].append(r.evidence)
            items = (body or {}).get('cart_items') or []
            rec['observation'] = {'status': r.status, 'cart_items': items}
            if not (len(items) == 1 and items[0].get('pizza_id') == 'p02' and items[0].get('quantity') == 1):
                rec['outcome'] = 'FAILURE'


class Api01(Sut01Api):
    """E04-SUT01-API-01 (establishment-only). Reset: restart of the backend process, then a login. Account: standard_user."""


class Api02(Sut01Api):
    """E04-SUT01-API-02 (establishment-only). Reset: session clear through the API. Account: standard_user."""


class Api03(Sut01Api):
    """E04-SUT01-API-03 (establishment-only). Reset: session clear through the API. Account: standard_user."""


class Api04(Sut01Api):
    """E04-SUT01-API-04 (establishment-only). Reset: session clear through the API. Account: performance_glitch_user; the blocks are those of E05-SUT01-API-04."""


class Api05(Sut01Api):
    """E04-SUT01-API-05 (establishment-only). Reset: session clear through the API. Account: a11y_glitch_user."""
    MODES = {'missing_name': 'S_MODE_MISSING_NAME', 'wrong_lang': 'S_MODE_WRONG_LANG', 'extreme_text': 'S_MODE_EXTREME_TEXT'}


class Api06(Sut01Api):
    """E04-SUT01-API-06 (establishment-only). Reset: restart of the backend process, then a login. Account: error_user."""


class Web01(Sut01Api):
    """E04-SUT01-WEB-01 (establishment-only): the Checkout view of the SUT-01 web app with the target state, reached by DIRECT_ROUTE; the client state comes from the E03 realization W-A. One browser context per job."""
    SPEC = SPEC_WEB

    SEED_KEYS = ('omnipizza-auth', 'omnipizza-country', 'token', 'username', 'countryCode', 'omnipizza-cart')

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

    def reset(self, run):
        super().reset(run)  # restart (process_restart), then the API login
        b = self.b
        with run.step('reset', 'first load of {web}/ and one injection of client state (session, market, empty client cart)', ['PREDEFINED_ACCOUNT']) as rec:
            status = b.goto(self.site + '/')
            release = web.local_storage(b, 'omnipizza-release')
            login = self.carry['login']
            seed = {'omnipizza-auth': json.dumps({'state': {'token': self.carry['token'], 'username': login.get('username'),
                                                            'behavior': login.get('behavior')}, 'version': 0}),
                    'omnipizza-country': json.dumps({'state': {'countryCode': 'MX', 'countryInfo': None, 'language': 'es', 'locale': 'es-MX',
                                                               'currency': 'MXN'}, 'version': 0}),
                    'token': self.carry['token'], 'username': login.get('username'), 'countryCode': 'MX',
                    'omnipizza-cart': json.dumps({'state': {'items': []}, 'version': 0})}
            b.page.evaluate('(seed) => { for (const [k, v] of Object.entries(seed)) window.localStorage.setItem(k, v); }', seed)
            rec['observation'] = {'first_load_status': status, 'omnipizza-release (read, not written)': release, 'keys_injected': sorted(seed)}
            if status != 200:
                rec['outcome'] = 'FAILURE'
            run.capture(rec, b.storage, 'sut01-web-storage-after-injection')

    def check_start(self, run):
        super().check_start(run)
        with run.step('starting-state', 'the client cart omnipizza-cart holds no item') as rec:
            cart = web.parse(web.local_storage(self.b, 'omnipizza-cart'))
            items = ((cart or {}).get('state') or {}).get('items') if isinstance(cart, dict) else None
            rec['observation'] = {'client_cart_items': items}
            if items != []:
                rec['outcome'] = 'FAILURE'

    def establish(self, run):
        super().establish(run)
        with run.step('establishment', 'navigation to {web}/checkout (Checkout hydrates from GET /api/cart when the local cart is empty)', ['DIRECT_ROUTE']) as rec:
            status = self.b.goto(self.site + '/checkout')
            rec['observation'] = {'status': status, 'url': self.b.page.url}
            if status != 200:
                rec['outcome'] = 'FAILURE'

    def verify_target(self, run):
        with run.step('verification', '[data-testid="order-item-p02"] visible on the Checkout view') as rec:
            shown = self.b.visible(self.b.page.locator('[data-testid="order-item-p02"]'))
            rec['observation'] = {'order_item_p02_visible': shown}
            if not shown:
                rec['outcome'] = 'FAILURE'
            run.capture(rec, self.b.shot, 'sut01-web-target-state')


REALIZATIONS = {'E04-SUT01-API-01': Api01, 'E04-SUT01-API-02': Api02, 'E04-SUT01-API-03': Api03, 'E04-SUT01-API-04': Api04,
                'E04-SUT01-API-05': Api05, 'E04-SUT01-API-06': Api06, 'E04-SUT01-WEB-01': Web01}
