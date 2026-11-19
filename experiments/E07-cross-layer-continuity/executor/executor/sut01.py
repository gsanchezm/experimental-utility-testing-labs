"""E07 realizations on SUT-01: E07-CS005-SUT01-API-WEB (CS-005, API to WEB) and E07-CS006-SUT01-WEB-API (CS-006, WEB to API). DRAFT (operation OP-PREP-E07-04).

The unit is one cart line of the session cart: pizza_id p02, quantity 1 (decision D-E07-9). The identity keys compared on the verification layer
are the sid claim of the login token (recorded as a digest), the number of cart lines, and the pizza_id and quantity of the line.

Sources (every selector, endpoint and flow below comes from one of these; a step without a source says so):
* API login, session read, cart seed and session reset: the E04 realization of E04-SUT01-API-02 (itself the E03 block 4.1), SUT01-EV-0004,
  SUT01-EV-0006, SUT01-EV-0007; the password of the documented accounts is the one of the SUT-01 README (HD-E09-A).
* Browser entry, client-state injection (token, username, market, empty client cart; one injection per execution, before the establishment):
  the E03 realization W-A of block 4.2 (experiments/E03-resetability/executor/README.md), as copied by the E04 executor.
* Checkout: navigation to {web}/checkout, where the view hydrates from GET /api/cart when the local cart is empty (E03 section 4.2; SUT01-EV-0004),
  `[data-testid="screen-checkout"]`, the order lines `[data-testid^="order-item-"]` filtered as in the E03 module sut01_web.py (ORDER_LINES).
* READ FROM THE PINNED COMMIT 9ca37674 OF THE SUT SOURCE IN A LOCAL CLONE (not from a CS record, an E01 row, or an E03/E04 text; to be confirmed
  by the non-measured DRY_RUN rounds): the catalog route /catalog (frontend/src/App.jsx:51); the add control `add-to-cart-<pizza_id>` built by
  tid(), which appends `-desktop` at a viewport of 768 px or more (frontend/src/components/ProductCard.jsx:45, frontend/src/hooks/useResponsive.js:3-20,
  and tid passed by frontend/src/pages/Catalog.jsx:140), so `add-to-cart-p02-desktop` at the 1280 x 800 viewport; the control opens the customizer
  modal (frontend/src/pages/Catalog.jsx:52-55,138,166), whose confirm control is `confirm-add-to-cart` (frontend/src/components/PizzaCustomizerModal.jsx:284);
  the confirmation calls addConfiguredItem (Catalog.jsx:62-68), which writes the persisted client store `omnipizza-cart` ({state: {items: [{pizza_id,
  quantity, config, ...}]}}) and makes no request (frontend/src/store.js:159-221); the order line details `order-item-details-<pizza_id>` read
  `{quantity}x • {size}` (frontend/src/pages/Checkout.jsx:964-968), the source of the quantity on the WEB layer. That the UI add does not write the
  server cart is the source fact behind the open cell of D-E07-6: it is recorded and not adjusted for. A UI add that leaves the server cart without
  the line is NOT_VERIFIED.

Reset (decision D-E07-8, outside the scenario and not counted): login and POST /api/session/reset through the API, a new browser context (web.py,
bind) and one injection of client state. Orders persist beyond the session reset (SUT01-EV-0006); E07 creates no order.
"""
import json
import re

from . import attempt, common, instance, web

PASSWORD = 'pizza123'
PIZZA = 'p02'
LINE = {'pizza_id': PIZZA, 'quantity': 1, 'size': 'small', 'toppings': []}
EXPECTED = {'cart_line.count': 1, 'cart_line.pizza_id': PIZZA, 'cart_line.quantity': 1}
KEYS = ['sid', 'cart_line.count', 'cart_line.pizza_id', 'cart_line.quantity']
DECLARED = ['JWT claim sid', 'cart line: pizza_id p02, quantity 1']
ADD_CONTROL = f'add-to-cart-{PIZZA}-desktop'  # tid('add-to-cart-p02') at a viewport of 768 px or more; the E07 viewport is 1280 x 800 (web.VIEWPORT)
ORDER_LINES = "() => Array.from(document.querySelectorAll('[data-testid^=\"order-item-\"]')).map(e => e.getAttribute('data-testid')).filter(t => /^order-item-[A-Za-z0-9]+$/.test(t))"
QUANTITY = re.compile(r'^\s*(\d+)\s*x')
SPEC_API_WEB = common.Spec('API', 'api', ['API_RESET', 'SESSION_RESET'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('web', 'web'), ('api', 'api')], True)
SPEC_WEB_API = common.Spec('Web UI Functional', 'web', ['API_RESET', 'SESSION_RESET'], ['PREDEFINED_ACCOUNT', 'UI_FLOW'], [('web', 'web'), ('api', 'api')], True)


class Sut01Ui:
    """The web leg of the SUT-01 conditions: Playwright. Every method returns plain data; the realization decides what a value means. A test
    substitutes an object with the same methods (tests/test_attempt.py, FakeSut01Ui), because no browser is installed in the static tests."""

    def __init__(self, job):
        self.b = web.Browser(job)
        self.site = instance.base(job.instance, 'web')
        self.run = None

    def bind(self, run):
        self.run = run
        self.b.bind(run)

    def end(self, run):
        self.b.flush()

    def close(self):
        self.b.close()

    def snapshot(self, run, rec, name):
        run.capture(rec, self.b.storage, name)

    def picture(self, run, rec, name):
        run.capture(rec, self.b.shot, name)

    def inject_session(self, token, login):
        """First load of {web}/ in the new context, then ONE injection of the client state of the E03 realization W-A (the release key is read, never written)."""
        b = self.b
        status = b.goto(self.site + '/')
        release = web.local_storage(b, 'omnipizza-release')
        seed = {'omnipizza-auth': json.dumps({'state': {'token': token, 'username': login.get('username'), 'behavior': login.get('behavior')}, 'version': 0}),
                'omnipizza-country': json.dumps({'state': {'countryCode': 'MX', 'countryInfo': None, 'language': 'es', 'locale': 'es-MX', 'currency': 'MXN'},
                                                 'version': 0}),
                'token': token, 'username': login.get('username'), 'countryCode': 'MX',
                'omnipizza-cart': json.dumps({'state': {'items': []}, 'version': 0})}
        b.page.evaluate('(seed) => { for (const [k, v] of Object.entries(seed)) window.localStorage.setItem(k, v); }', seed)
        return {'first_load_status': status, 'omnipizza-release (read, not written)': release, 'keys_injected': sorted(seed)}, status

    def client_cart(self):
        """The items of the persisted client cart, or None when it cannot be read."""
        cart = web.parse(web.local_storage(self.b, 'omnipizza-cart'))
        items = ((cart or {}).get('state') or {}).get('items') if isinstance(cart, dict) else None
        return items if isinstance(items, list) else None

    def client_token(self):
        auth = web.parse(web.local_storage(self.b, 'omnipizza-auth'))
        token = ((auth or {}).get('state') or {}).get('token') if isinstance(auth, dict) else None
        if token:
            self.run.scrub.secret(token)
        return token

    def add_through_ui(self, pizza_id):
        """Catalog, the add control of the pizza, the confirm control of the customizer modal. Returns what happened, step by step."""
        b = self.b
        obs = {'catalog_status': b.goto(self.site + '/catalog')}
        obs['catalog_loaded'] = b.visible(b.page.locator('[data-testid="screen-catalog"]'))
        add = b.page.locator(f'[data-testid="add-to-cart-{pizza_id}-desktop"]')
        obs['add_control_visible'] = obs['catalog_loaded'] and b.visible(add)
        if not obs['add_control_visible']:
            return obs
        add.first.click()
        confirm = b.page.locator('[data-testid="confirm-add-to-cart"]')
        obs['confirm_control_visible'] = b.visible(confirm)
        if not obs['confirm_control_visible']:
            return obs
        confirm.first.click()
        obs['settle'] = b.settle()
        obs['confirmed'] = True
        return obs

    def open_checkout(self):
        status = self.b.goto(self.site + '/checkout')
        return status

    def checkout_lines(self):
        """Read-only: the order lines of the Checkout view, each with the text of its details. An empty cart view yields []."""
        b = self.b
        b.visible(b.page.locator('[data-testid="screen-checkout"]'))
        b.visible(b.page.locator('[data-testid^="order-item-"]'))  # hydration from GET /api/cart is asynchronous; False is an observation
        b.settle()
        lines = []
        for test_id in b.page.evaluate(ORDER_LINES):
            pizza_id = test_id[len('order-item-'):]
            details = b.page.locator(f'[data-testid="order-item-details-{pizza_id}"]')
            lines.append({'pizza_id': pizza_id, 'details': details.first.inner_text(timeout=web.ACTION_TIMEOUT_MS) if details.count() else None})
        return lines


class Sut01(attempt.Realization):
    KEYS = KEYS
    DECLARED_KEYS = DECLARED

    def __init__(self, job):
        super().__init__(job)
        self.account = job.c['account']
        self.ui = None

    # ---- the web leg ----------------------------------------------------------------------------------------------
    def make_ui(self):
        return Sut01Ui(self.job)

    def open(self):
        self.ui = self.make_ui()

    def bind(self, run):
        self.start_identity(run)
        self.ui.bind(run)

    def end(self, run):
        self.ui.end(run)

    def close(self):
        if self.ui is not None:
            self.ui.close()

    # ---- the API leg ----------------------------------------------------------------------------------------------
    def api(self):
        return instance.base(self.job.instance, 'api')

    def auth(self):
        return {'Authorization': f'Bearer {self.carry["token"]}'}

    def login(self, run, label='sut01-login'):
        run.scrub.secret(PASSWORD)
        r = run.http('POST', f'{self.api()}/api/auth/login', {'username': self.account, 'password': PASSWORD}, label=label)
        try:
            body = r.json() if r.status == 200 else {}
        except ValueError:
            body = {}
        token = body.get('access_token')
        run.scrub.secret(token)
        return r, token, body

    def session(self, run, label):
        r = run.http('GET', f'{self.api()}/api/session', headers=self.auth(), label=label)
        try:
            body = r.json() if r.status == 200 else None
        except ValueError:
            body = None
        return r, body

    # ---- blocks ---------------------------------------------------------------------------------------------------
    def reset(self, run):
        with run.step('reset', 'POST /api/auth/login, then POST /api/session/reset with the session token', ['API_RESET', 'SESSION_RESET']) as rec:
            r, token, body = self.login(run)
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'login_status': r.status, 'token_received': bool(token), 'behavior': body.get('behavior')}
            if not token:
                rec['outcome'] = 'FAILURE'
                return
            self.carry = {'token': token, 'login': body}
            r = run.http('POST', f'{self.api()}/api/session/reset', headers=self.auth(), label='sut01-reset')
            rec['evidence'].append(r.evidence)
            rec['observation']['reset_status'] = r.status
            if r.status != 200:
                rec['outcome'] = 'FAILURE'
        with run.step('reset', 'new browser context: first load of {web}/ and one injection of client state (session, market, empty client cart)',
                      ['PREDEFINED_ACCOUNT']) as rec:
            obs, status = self.ui.inject_session(self.carry['token'], self.carry['login'])
            rec['observation'] = obs
            if status != 200:
                rec['outcome'] = 'FAILURE'
            self.ui.snapshot(run, rec, 'sut01-web-storage-after-injection')

    def check_start(self, run):
        with run.step('starting-state', 'GET /api/session: the server cart is empty') as rec:
            r, body = self.session(run, 'sut01-session-start')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'cart_items': (body or {}).get('cart_items')}
            if body is None or body.get('cart_items') != []:
                rec['outcome'] = 'FAILURE'
        with run.step('starting-state', 'the client cart omnipizza-cart holds no item') as rec:
            items = self.ui.client_cart()
            rec['observation'] = {'client_cart_items': items}
            if items != []:
                rec['outcome'] = 'FAILURE'

    def api_cart(self, body):
        """The identity attributes of a server cart: what the API layer shows."""
        items = (body or {}).get('cart_items')
        items = items if isinstance(items, list) else []
        first = items[0] if items and isinstance(items[0], dict) else {}
        return {'cart_line.count': len(items), 'cart_line.pizza_id': first.get('pizza_id'), 'cart_line.quantity': first.get('quantity')}


class ApiWeb(Sut01):
    """E07-CS005-SUT01-API-WEB: establishment through the API (POST /api/cart), verification on the Checkout view of the web app."""
    SPEC = SPEC_API_WEB

    def establish(self, run):
        with run.step('establishment', 'POST /api/cart with one p02 line (API layer)', ['API_SEED']) as rec:
            r = run.http('POST', f'{self.api()}/api/cart', {'items': [LINE]}, headers=self.auth(), label='sut01-seed-cart')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status}
            if r.status != 200:
                rec['outcome'] = 'FAILURE'

    def establish_check(self, run):
        with run.step('establishment-check', 'GET /api/session shows exactly the p02 line, quantity 1 (read-only, API layer)') as rec:
            r, body = self.session(run, 'sut01-session-established')
            rec['evidence'].append(r.evidence)
            sid = common.jwt_claim(self.carry['token'], 'sid')
            established = {'sid': common.digest(sid) if sid else None, **self.api_cart(body)}
            rec['observation'] = {'status': r.status, 'established': established}
            run.identity['established'] = established
            if sid is None or {k: v for k, v in established.items() if k != 'sid'} != EXPECTED:
                rec['outcome'] = 'FAILURE'

    def verify(self, run):
        with run.step('verification', 'navigation to {web}/checkout, then a read of the order lines and of the session token held by the web client (WEB layer, read-only)') as rec:
            status = self.ui.open_checkout()
            lines = self.ui.checkout_lines() if status == 200 else []
            token = self.ui.client_token() if status == 200 else None
            sid = common.jwt_claim(token, 'sid') if token else None
            first = lines[0] if lines else {}
            m = QUANTITY.match(first.get('details') or '') if first else None
            observed = {'sid': common.digest(sid) if sid else None, 'cart_line.count': len(lines),
                        'cart_line.pizza_id': first.get('pizza_id') or None, 'cart_line.quantity': int(m.group(1)) if m else None}
            rec['evidence'].append(run.jsonfile('sut01-web-order-lines', lines))
            self.ui.picture(run, rec, 'sut01-web-checkout')
            self.conclude(run, rec, observed, checkout_status=status, order_lines=lines)


class WebApi(Sut01):
    """E07-CS006-SUT01-WEB-API: establishment through the web UI (catalog, add control, customizer modal), verification on GET /api/session.
    The source of the SUT makes the UI add a client-store write only (module docstring): the server cart is not expected to hold the line, and
    the observation is recorded as it is (the open cell of D-E07-6)."""
    SPEC = SPEC_WEB_API

    def establish(self, run):
        with run.step('establishment', 'catalog, the add control of the p02 pizza, the confirm control of the customizer modal (WEB layer)', ['UI_FLOW']) as rec:
            obs = self.ui.add_through_ui(PIZZA)
            rec['observation'] = obs
            self.ui.picture(run, rec, 'sut01-web-after-add')
            if not obs.get('confirmed'):
                rec['outcome'] = 'FAILURE'

    def establish_check(self, run):
        with run.step('establishment-check', 'the persisted client cart omnipizza-cart holds exactly the p02 line, quantity 1 (read-only, WEB layer)') as rec:
            items = self.ui.client_cart()
            token = self.ui.client_token()
            sid = common.jwt_claim(token, 'sid') if token else None
            first = items[0] if items and isinstance(items[0], dict) else {}
            established = {'sid': common.digest(sid) if sid else None, 'cart_line.count': len(items or []),
                           'cart_line.pizza_id': first.get('pizza_id'), 'cart_line.quantity': first.get('quantity')}
            rec['observation'] = {'established': established}
            run.identity['established'] = established
            if sid is None or {k: v for k, v in established.items() if k != 'sid'} != EXPECTED:
                rec['outcome'] = 'FAILURE'

    def verify(self, run):
        with run.step('verification', 'GET /api/session with the session token (API layer, read-only)') as rec:
            r, body = self.session(run, 'sut01-session-verification')
            rec['evidence'].append(r.evidence)
            sid = common.jwt_claim(self.carry['token'], 'sid')
            observed = {'sid': common.digest(sid) if sid else None, **self.api_cart(body)} if body is not None else {}
            self.conclude(run, rec, observed, status=r.status, transport_error=r.error)


REALIZATIONS = {'E07-CS005-SUT01-API-WEB': ApiWeb, 'E07-CS006-SUT01-WEB-API': WebApi}
