"""E05 realizations on SUT-01: E05-SUT01-API-01 to -06 (api) and E05-SUT01-WEB-01 (web). DRAFT (operation OP-PREP-E05).

Blocks per execution (design brief s.2.1): reset, starting-state check, establishment, target-state verification, stimulus, classification.
* reset: API-02 to API-05 clear the caller's session (POST /api/session/reset, mechanisms API_RESET and SESSION_RESET, the E03 SUT-01 block 4.1);
  API-01, API-06 and WEB-01 restart the backend process, because orders persist beyond that reset (D-03 b, instance.json process block;
  mechanism ENVIRONMENT_RESTART), and log in again, because the restart clears the in-memory session store.
* starting-state check: the server cart is empty (backend/database.py:139-148). establishment: one p02 line (POST /api/cart).
  verification: the session shows exactly that line (web: the Checkout view shows order-item-p02).
* The condition's account (conditions-draft.json) logs in at every execution; every documented test account uses the password of the SUT-01
  README (HD-E09-A; backend/constants.py lines 21-61, SOURCE-READS-03).
"""
import json

from . import attempt, common, instance, sut01_expected as ex, web

PASSWORD = 'pizza123'
LINE = {'pizza_id': 'p02', 'quantity': 1, 'size': 'small', 'toppings': []}
SPEC_RESET = common.Spec('API', 'api', ['API_RESET', 'SESSION_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api')], True)
SPEC_RESTART = common.Spec('API', 'api', ['ENVIRONMENT_RESTART'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api')], True)
SPEC_WEB = common.Spec('Web UI Functional', 'web', ['ENVIRONMENT_RESTART'], ['PREDEFINED_ACCOUNT', 'API_SEED', 'DIRECT_ROUTE'],
                       [('web', 'web'), ('api', 'api')], True)
MX_HEADERS = {'X-Country-Code': 'MX'}  # no X-Language: the catalog route then answers in English
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
            r, body = self.session(run, 'sut01-session-pre-stimulus')
            rec['evidence'].append(r.evidence)
            items = (body or {}).get('cart_items') or []
            rec['observation'] = {'status': r.status, 'cart_items': items}
            if not (len(items) == 1 and items[0].get('pizza_id') == 'p02' and items[0].get('quantity') == 1):
                rec['outcome'] = 'FAILURE'

    def get_catalog(self, run, label, timeout=common.HTTP_TIMEOUT_S):
        run.mark_stimulus_sent()
        r = run.http('GET', f'{self.api()}/api/pizzas', headers={**self.auth(run), **MX_HEADERS}, label=label, timeout=timeout)
        try:
            body = r.json() if r.status == 200 else None
        except ValueError:
            body = None
        return r, body


class Api01(Sut01Api):
    """Stimulus: POST /api/checkout, market MX (F02). Projection: totals, currency, line items; identifiers and timestamps excluded."""

    def stimulus(self, run):
        with run.observe('stimulus', 'POST /api/checkout (market MX, one p02 line, tip 0)') as rec:
            run.mark_stimulus_sent()
            r = run.http('POST', f'{self.api()}/api/checkout', ex.CHECKOUT_BODY, headers=self.auth(run), label='sut01-stimulus-checkout')
            rec['evidence'].append(r.evidence)
            try:
                body = r.json() if r.status == 200 else None
            except ValueError:
                body = None
            obs = {'status': r.status, 'error': r.error, 'projection': ex.project_order(body), 'expected': ex.expected_checkout()}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] != 200:
            return 'S_HTTP_NON_200', f'HTTP {obs["status"]}'
        if obs['projection'] == obs['expected']:
            return 'S_ORDER_TOTAL_MATCH', f'total {obs["projection"]["total"]} {obs["projection"]["currency"]}'
        return 'S_ORDER_TOTAL_MISMATCH', f'projection {json.dumps(obs["projection"])} differs from the expected {json.dumps(obs["expected"])}'


class Api02(Sut01Api):
    """Stimulus: GET /api/pizzas, X-Country-Code MX, no X-Language. Projection: name, description, price, currency per item."""

    def stimulus(self, run):
        with run.observe('stimulus', 'GET /api/pizzas (market MX, no X-Language)') as rec:
            r, body = self.get_catalog(run, 'sut01-stimulus-catalog')
            rec['evidence'].append(r.evidence)
            obs = {'status': r.status, 'error': r.error, 'projection': ex.project_catalog(body), 'expected': ex.expected_catalog()}
            rec['observation'] = {k: v for k, v in obs.items() if k != 'expected'}
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] != 200:
            return 'S_HTTP_NON_200', f'HTTP {obs["status"]}'
        if obs['projection'] == obs['expected']:
            return 'S_CATALOG_MATCH', f'{len(obs["projection"])} items equal the expected catalog'
        return 'S_CATALOG_MISMATCH', 'the catalog projection differs from the expected catalog'


class Api03(Sut01Api):
    """Stimulus: POST /api/auth/login as locked_out_user, in a separate request that carries no token (backend/auth.py lines 25-29)."""

    def stimulus(self, run):
        with run.observe('stimulus', 'POST /api/auth/login as locked_out_user') as rec:
            run.mark_stimulus_sent()
            r = run.http('POST', f'{self.api()}/api/auth/login', {'username': 'locked_out_user', 'password': PASSWORD}, label='sut01-stimulus-lockout')
            rec['evidence'].append(r.evidence)
            try:
                detail = r.json().get('detail')
            except (ValueError, AttributeError):
                detail = None
            obs = {'status': r.status, 'error': r.error, 'detail': detail}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] == ex.LOCKOUT_STATUS and obs['detail'] == ex.LOCKOUT_DETAIL:
            return 'S_LOCKOUT_403_EXACT_MESSAGE', f'HTTP 403, detail {obs["detail"]!r}'
        return 'S_OTHER_STATUS_OR_BODY', f'HTTP {obs["status"]}, detail {obs["detail"]!r}'


class Api04(Api02):
    """Stimulus: GET /api/pizzas as performance_glitch_user (a fixed 3.0 s delay, F04); content only, latency excluded from the comparison;
    the client timeout is the one of the condition (30 s, to be confirmed in the START package)."""

    def stimulus(self, run):
        timeout = self.job.c.get('client_timeout_s', 30)
        with run.observe('stimulus', f'GET /api/pizzas as performance_glitch_user (client timeout {timeout} s)') as rec:
            r, body = self.get_catalog(run, 'sut01-stimulus-catalog', timeout=timeout)
            rec['evidence'].append(r.evidence)
            obs = {'status': r.status, 'error': r.error, 'timed_out': r.timed_out(), 'elapsed_s': r.elapsed_s,
                   'projection': ex.project_catalog(body), 'expected': ex.expected_catalog()}
            rec['observation'] = {k: v for k, v in obs.items() if k != 'expected'}
        return obs

    def classify(self, run, obs):
        if obs['timed_out']:
            return 'S_CLIENT_TIMEOUT', f'no response within the client timeout; {obs["error"]}'
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] != 200:
            return 'S_HTTP_NON_200', f'HTTP {obs["status"]}'
        if obs['projection'] == obs['expected']:
            return 'S_CONTENT_MATCH_200', f'{len(obs["projection"])} items equal the expected catalog (latency {obs["elapsed_s"]} s, not compared)'
        return 'S_CONTENT_MISMATCH', 'the catalog projection differs from the expected catalog'


class Api05(Sut01Api):
    """Stimulus: GET /api/pizzas as a11y_glitch_user. The realized mode (missing_name, wrong_lang, extreme_text; backend/database.py
    lines 57-77 and 280-289) is decided from the body against the pinned catalog."""
    MODES = {'missing_name': 'S_MODE_MISSING_NAME', 'wrong_lang': 'S_MODE_WRONG_LANG', 'extreme_text': 'S_MODE_EXTREME_TEXT'}

    def stimulus(self, run):
        with run.observe('stimulus', 'GET /api/pizzas as a11y_glitch_user (market MX, no X-Language)') as rec:
            r, body = self.get_catalog(run, 'sut01-stimulus-catalog')
            rec['evidence'].append(r.evidence)
            obs = {'status': r.status, 'error': r.error, 'mode': ex.a11y_mode(body)}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] == 200 and obs['mode'] in self.MODES:
            return self.MODES[obs['mode']], f'realized mode {obs["mode"]}'
        return 'S_OTHER', f'HTTP {obs["status"]}, realized mode {obs["mode"]}'


class Api06(Sut01Api):
    """Discriminant control: POST /api/checkout as error_user (HTTP 500 with probability 0.5 per call, F03)."""

    def stimulus(self, run):
        with run.observe('stimulus', 'POST /api/checkout as error_user (market MX, one p02 line, tip 0)') as rec:
            run.mark_stimulus_sent()
            r = run.http('POST', f'{self.api()}/api/checkout', ex.CHECKOUT_BODY, headers=self.auth(run), label='sut01-stimulus-checkout')
            rec['evidence'].append(r.evidence)
            try:
                body = r.json()
            except ValueError:
                body = None
            obs = {'status': r.status, 'error': r.error, 'has_order_id': isinstance(body, dict) and bool(body.get('order_id')),
                   'detail': body.get('detail') if isinstance(body, dict) else None}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] == 200 and obs['has_order_id']:
            return 'S_ORDER_CREATED', 'HTTP 200 with an order'
        if obs['status'] == 500:
            return 'S_HTTP_500', f'HTTP 500, detail {obs["detail"]!r}' + ('' if obs['detail'] == ex.ERROR_USER_DETAIL else ' (not the documented detail)')
        return 'S_OTHER', f'HTTP {obs["status"]}'


class Web01(Sut01Api):
    """Web: Checkout of the SUT-01 web app (E03 realization W-A for the client state; stimulus F05). One browser context per job."""
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
            run.capture(rec, self.b.shot, 'sut01-web-pre-stimulus')

    def stimulus(self, run):
        p = self.b.page
        with run.observe('stimulus', 'fill the Checkout form (market MX), activate the place-order control, confirm in the modal') as rec:
            p.locator('input[data-testid*="full-name"]').fill(ex.CHECKOUT_BODY['name'])
            p.locator('input[data-testid*="address"]').fill(ex.CHECKOUT_BODY['address'])
            p.locator('input[data-testid*="phone"]').fill(ex.CHECKOUT_BODY['phone'])
            p.locator('input[data-testid="colonia"]').fill(ex.CHECKOUT_BODY['colonia'])
            cash = p.locator('[data-testid="payment-method-cash"]')
            if cash.count():
                cash.first.click()
            p.locator('[data-testid*="place-order-btn"]').first.click()
            modal = self.b.visible(p.locator('[data-testid="confirm-order-modal"]'))
            invalid = p.locator('input:invalid').count()
            post = None
            run.mark_stimulus_sent()
            if modal:
                try:
                    with p.expect_response(lambda r: r.request.method == 'POST' and '/api/checkout' in r.url, timeout=web.NAV_TIMEOUT_MS) as info:
                        p.locator('[data-testid="confirm-order-yes"]').click()
                    post = info.value.status
                except Exception as e:  # noqa: BLE001 - no answer to the order post is an observation; the page is still read
                    rec['post_error'] = e.__class__.__name__
            settle = self.b.settle()
            obs = {'modal_shown': modal, 'invalid_fields': invalid, 'post_status': post, 'url': p.url, 'settle': settle,
                   'order_success_route': '/order-success' in p.url}
            run.capture(rec, self.b.shot, 'sut01-web-after-stimulus')
            run.capture(rec, self.b.dom, 'sut01-web-stimulus-text')
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['order_success_route']:
            return 'S_ORDER_CONFIRMED', f'order-success route reached; order post answered {obs["post_status"]}'
        if not obs['modal_shown'] and obs['invalid_fields']:
            return 'S_VALIDATION_MESSAGE', f'{obs["invalid_fields"]} invalid fields, no confirmation modal'
        if obs['post_status'] is not None and obs['post_status'] >= 400:
            return 'S_HTTP_ERROR_VISIBLE', f'order post answered {obs["post_status"]}; the view stays on {obs["url"]}'
        return 'S_OTHER_VIEW', f'url {obs["url"]}; modal {obs["modal_shown"]}; order post answered {obs["post_status"]}'


REALIZATIONS = {'E05-SUT01-API-01': Api01, 'E05-SUT01-API-02': Api02, 'E05-SUT01-API-03': Api03, 'E05-SUT01-API-04': Api04,
                'E05-SUT01-API-05': Api05, 'E05-SUT01-API-06': Api06, 'E05-SUT01-WEB-01': Web01}
