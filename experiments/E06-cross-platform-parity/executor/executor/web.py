"""E06-cross-platform-parity executor: the web surfaces of CS-007 (SUT-01 web and SUT-02 web).

DRAFT (operation OP-PREP-E06-EXECUTOR). The flows run through a small page interface (goto, click, fill, evaluate, wait_for_timeout,
settle, content, screenshot, current_url), so the tests drive them with a fake page; PlaywrightPage maps that interface to Playwright
for Python 1.63.0 (the only place that imports Playwright). Every selector is taken from the pinned source named in
conditions-draft.json; none is verified against the hosted deployment until a non-measured DRY_RUN has run.

The sign-in is inside the scenario (CS-007 precondition): no token is injected, and no catalogue request is made from Python.
The identity is read from the DOM after the page settles, and the parsing is done by identity.py.
"""
import importlib.metadata

from . import identity

# Routes and timeouts of the web realization. NAV_TIMEOUT_MS is generous because the hosted deployments may cold-start.
SUT01_WEB_ROOT = 'https://omnipizza-frontend.onrender.com/'
SUT02_WEB_ROOT = 'https://www.saucedemo.com/'
VIEWPORT = {'width': 1280, 'height': 800}
TIMEZONE = 'UTC'
BROWSER_LOCALE = 'en-US'
NAV_TIMEOUT_MS = 90000
ACTION_TIMEOUT_MS = 15000
SCREEN_BUDGET_MS = 90000
SIGN_IN_BUDGET_MS = 60000
CATALOGUE_BUDGET_MS = 60000
POLL_MS = 250
SETTLE_TIMEOUT_MS = 15000
QUIET_MS = 500
NET_FRAGMENTS = ('/api/auth/login', '/api/pizzas')

JS_EXISTS = '(sel) => !!document.querySelector(sel)'
JS_LOGIN_ERROR = ("() => { const e = document.querySelector('[data-testid=\"login-error\"]'); "
                  "return e ? (e.textContent || '').trim() : null; }")
JS_SUT02_ERROR = "() => { const e = document.querySelector('[data-test=\"error\"]'); return e ? (e.textContent || '').trim() : null; }"
JS_SUT01_TESTIDS = ("() => Array.from(document.querySelectorAll('[data-testid^=\"pizza-name-\"]'))"
                    ".map(e => e.getAttribute('data-testid'))")
JS_SUT02_NAMES = ("() => Array.from(document.querySelectorAll('[data-test=\"inventory-item-name\"]'))"
                  ".map(e => (e.textContent || '').trim())")
JS_SUT02_ON_INVENTORY = "() => window.location.pathname.endsWith('/inventory.html') && !!document.querySelector('[data-test=\"inventory-list\"]')"
JS_SUT01_CATALOGUE = "() => !!document.querySelector('[data-testid=\"screen-catalog\"]')"


def net_summary(net, fragment):
    """(request seen, last response status) for URLs holding fragment, from the recorded network events (pure)."""
    seen, status = False, None
    for ev in net:
        if fragment not in (ev.get('url') or ''):
            continue
        if ev.get('event') == 'request':
            seen = True
        elif ev.get('event') == 'response':
            status = ev.get('status')
        elif ev.get('event') == 'failed':
            status = None
    return seen, status


def poll(page, js, arg, budget_ms):
    """Evaluate js(arg) every POLL_MS until it is truthy or the budget is spent; returns the last value (never raises on timeout)."""
    waited = 0
    while True:
        value = page.evaluate(f'({js})({_js_arg(arg)})') if arg is not None else page.evaluate(f'({js})()')
        if value:
            return value
        if waited >= budget_ms:
            return value
        page.wait_for_timeout(POLL_MS)
        waited += POLL_MS


def _js_arg(arg):
    if isinstance(arg, str):
        return '"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return str(arg)


def sut01_web(page, net, creds, viewport_width=VIEWPORT['width']):
    """SUT-01 web: market US, sign-in through the form, arrival at screen-catalog, identity of the first card. Returns the facts."""
    user, password = creds
    suffix = identity.expected_suffix(viewport_width)
    facts = {'surface': 'web', 'sut_id': 'SUT-01', 'viewport_width': viewport_width, 'test_id_suffix': suffix,
             'sign_in_submitted': False, 'page_loaded': False, 'backend_observed': True, 'steps': []}
    page.goto(SUT01_WEB_ROOT)
    facts['steps'].append('navigation: root route loaded')
    facts['page_loaded'] = bool(poll(page, JS_EXISTS, '[data-testid="screen-login"]', SCREEN_BUDGET_MS))
    if not facts['page_loaded']:
        return _finish(page, net, facts, arrived=False)
    page.click('[data-testid="market-US"]')
    facts['steps'].append('UI: market US selected')
    page.fill(f'[data-testid="username{suffix}"]', user)
    page.fill(f'[data-testid="password{suffix}"]', password)
    facts['steps'].append('UI: username and password filled')
    facts['sign_in_submitted'] = True
    page.click(f'[data-testid="login-button{suffix}"]')
    facts['steps'].append('UI: sign-in control activated')
    facts['sign_in_state'] = _wait_state(page, SIGN_IN_BUDGET_MS)
    facts['error_text'] = page.evaluate(JS_LOGIN_ERROR)
    arrived = facts['sign_in_state'] == 'CATALOGUE'
    if arrived:
        facts['steps'].append('verification: screen-catalog visible')
        poll(page, JS_EXISTS, '[data-testid^="pizza-name-"]', CATALOGUE_BUDGET_MS)
        page.settle()
        raw = page.evaluate(JS_SUT01_TESTIDS) or []
        facts['raw_identifiers'] = list(raw)
        cards = identity.parse_web_testids(raw)
        facts['normalized_identifiers'] = [c['id'] for c in cards]
        facts['identity_raw'] = cards[0]['raw'] if cards else None
        facts['identity'] = identity.first_identity('SUT-01', cards)
    return _finish(page, net, facts, arrived=arrived)


def sut02_web(page, net, creds):
    """SUT-02 web: sign-in through the form, arrival at the inventory, and the name of the first item in the default name order."""
    user, password = creds
    facts = {'surface': 'web', 'sut_id': 'SUT-02', 'sign_in_submitted': False, 'page_loaded': False,
             'backend_observed': False, 'steps': []}
    page.goto(SUT02_WEB_ROOT)
    facts['steps'].append('navigation: root route loaded')
    facts['page_loaded'] = bool(poll(page, JS_EXISTS, '#user-name', SCREEN_BUDGET_MS))
    if not facts['page_loaded']:
        return _finish(page, net, facts, arrived=False)
    page.fill('#user-name', user)
    page.fill('[data-test="password"]', password)
    facts['steps'].append('UI: username and password filled')
    facts['sign_in_submitted'] = True
    page.click('#login-button')
    facts['steps'].append('UI: sign-in control activated')
    facts['sign_in_state'] = _wait_state_sut02(page, SIGN_IN_BUDGET_MS)
    facts['error_text'] = page.evaluate(JS_SUT02_ERROR)
    arrived = facts['sign_in_state'] == 'CATALOGUE'
    if arrived:
        facts['steps'].append('verification: inventory visible at /inventory.html')
        poll(page, JS_EXISTS, '[data-test="inventory-item-name"]', CATALOGUE_BUDGET_MS)
        page.settle()
        titles = [identity.normalize_title(t) for t in (page.evaluate(JS_SUT02_NAMES) or [])]
        facts['titles'] = titles
        facts['identity'] = identity.first_identity('SUT-02', titles)
        facts['identity_raw'] = facts['identity']
    return _finish(page, net, facts, arrived=arrived)


def _wait_state(page, budget_ms):
    """SUT-01: CATALOGUE when screen-catalog is shown, ERROR when the login error is shown, None when neither within the budget."""
    waited = 0
    while True:
        if page.evaluate(JS_SUT01_CATALOGUE):
            return 'CATALOGUE'
        if page.evaluate(JS_LOGIN_ERROR):
            return 'ERROR'
        if waited >= budget_ms:
            return None
        page.wait_for_timeout(POLL_MS)
        waited += POLL_MS


def _wait_state_sut02(page, budget_ms):
    waited = 0
    while True:
        if page.evaluate(JS_SUT02_ON_INVENTORY):
            return 'CATALOGUE'
        if page.evaluate(JS_SUT02_ERROR):
            return 'ERROR'
        if waited >= budget_ms:
            return None
        page.wait_for_timeout(POLL_MS)
        waited += POLL_MS


def _finish(page, net, facts, arrived):
    facts['arrived'] = bool(arrived)
    facts['login_request_seen'], facts['login_status'] = net_summary(net, '/api/auth/login')
    facts['catalogue_seen'], facts['catalogue_status'] = net_summary(net, '/api/pizzas')
    facts['network_events'] = [dict(e) for e in net]
    facts.setdefault('identity', None)
    facts.setdefault('identity_raw', None)
    facts['screenshot_png'] = page.screenshot()
    facts['dom_html'] = page.content()
    return facts


class PlaywrightPage:
    """The page interface of this module over Playwright for Python. The settle logic is the one of the E09 executor (no request in flight,
    and no network event for QUIET_MS, bounded by SETTLE_TIMEOUT_MS; the read happens once after it)."""

    def __init__(self, page, tracker):
        self.page = page
        self.tracker = tracker

    def goto(self, url):
        response = self.page.goto(url, wait_until='load', timeout=NAV_TIMEOUT_MS)
        return response.status if response else None

    def click(self, selector):
        self.page.click(selector, timeout=ACTION_TIMEOUT_MS)

    def fill(self, selector, value):
        self.page.fill(selector, value, timeout=ACTION_TIMEOUT_MS)

    def evaluate(self, expression):
        return self.page.evaluate(expression)

    def wait_for_timeout(self, ms):
        self.page.wait_for_timeout(ms)

    def settle(self):
        import time
        t0 = time.monotonic()
        while True:
            now = time.monotonic()
            if not self.tracker.inflight and now - max(self.tracker.last_event, t0) >= QUIET_MS / 1000:
                return {'network_quiet': True, 'elapsed_s': round(now - t0, 3)}
            if now - t0 >= SETTLE_TIMEOUT_MS / 1000:
                return {'network_quiet': False, 'elapsed_s': round(now - t0, 3), 'in_flight': len(self.tracker.inflight)}
            self.page.wait_for_timeout(50)

    def content(self):
        return self.page.content()

    def screenshot(self):
        return self.page.screenshot(full_page=True)


class NetTracker:
    """Records the requests and responses of the fragments of NET_FRAGMENTS, and the in-flight requests for the settle logic."""

    def __init__(self):
        import time
        self._time = time.monotonic
        self.events = []
        self.inflight = {}
        self.last_event = self._time()

    def on_request(self, request):
        self.inflight[id(request)] = request.url
        self.last_event = self._time()
        if any(f in request.url for f in NET_FRAGMENTS):
            self.events.append({'event': 'request', 'url': request.url, 'method': request.method})

    def on_response(self, response):
        self.last_event = self._time()
        if any(f in response.url for f in NET_FRAGMENTS):
            self.events.append({'event': 'response', 'url': response.url, 'status': response.status, 'method': response.request.method})

    def on_finished(self, request):
        self.inflight.pop(id(request), None)
        self.last_event = self._time()

    def on_failed(self, request):
        self.inflight.pop(id(request), None)
        self.last_event = self._time()
        if any(f in request.url for f in NET_FRAGMENTS):
            self.events.append({'event': 'failed', 'url': request.url, 'method': request.method, 'failure': str(getattr(request, 'failure', None))})


class Browser:
    """One headless Chromium for the whole job; one fresh browser context per execution (SESSION_RESET)."""

    def __init__(self, run_tools):
        from playwright.sync_api import sync_playwright
        self.run_tools = run_tools
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        self.context = None
        self.tracker = None
        run_tools['web_runner'] = {'tool': 'Playwright for Python', 'version': importlib.metadata.version('playwright')}
        run_tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}

    def new_page(self):
        self.close_context()
        self.tracker = NetTracker()
        self.context = self.browser.new_context(viewport=VIEWPORT, timezone_id=TIMEZONE, locale=BROWSER_LOCALE)
        self.context.set_default_timeout(ACTION_TIMEOUT_MS)
        self.context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        page = self.context.new_page()
        page.on('request', self.tracker.on_request)
        page.on('response', self.tracker.on_response)
        page.on('requestfinished', self.tracker.on_finished)
        page.on('requestfailed', self.tracker.on_failed)
        return PlaywrightPage(page, self.tracker)

    def close_context(self):
        if self.context is not None:
            try:
                self.context.close()
            except Exception:  # noqa: BLE001 - closing is best effort; the bundle is written before it
                pass
            self.context = None

    def close(self):
        self.close_context()
        for closer in (self.browser.close, self._pw.stop):
            try:
                closer()
            except Exception:  # noqa: BLE001 - best effort at the end of the job
                pass
