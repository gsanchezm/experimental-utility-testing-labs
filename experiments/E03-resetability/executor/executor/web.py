"""E03-resetability executor: Playwright for Python helpers (README sections 3 and 10).

DRAFT (operation OP-PREP-E03). One Chromium context per run; no implicit retry beyond Playwright's own actionability
waits, each with an explicit timeout. Screenshots, DOM text, storage snapshots, and the network log are evidence, not
actions. Every web read waits for the same bounded network-quiet settle before it reads, identically for every SUT.
"""
import importlib.metadata
import json
import time

from . import common

NAV_TIMEOUT_MS = 30000
ACTION_TIMEOUT_MS = 15000
SETTLE_TIMEOUT_MS = 15000
QUIET_MS = 500
VIEWPORT = {'width': 1280, 'height': 800}


class Browser:
    def __init__(self, run):
        from playwright.sync_api import sync_playwright
        self.run = run
        self.net = []
        self.console = []
        self.inflight = set()
        self.last_event = time.monotonic()
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        self.context = self.browser.new_context(viewport=VIEWPORT, timezone_id='UTC', locale='en-US')
        self.context.set_default_timeout(ACTION_TIMEOUT_MS)
        self.context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        self.page = self.context.new_page()
        self.page.on('request', self._on_request)
        self.page.on('response', self._on_response)
        self.page.on('requestfinished', self._on_finished)
        self.page.on('requestfailed', self._on_failed)
        self.page.on('console', lambda m: self.console.append({'t': common.stamp(), 'type': m.type, 'text': m.text}))
        run.tools['web_runner'] = {'tool': 'Playwright for Python', 'version': importlib.metadata.version('playwright')}
        run.tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}
        run.log('browser', version=self.browser.version, viewport=VIEWPORT)

    def _on_request(self, q):
        self.inflight.add(q)
        self.last_event = time.monotonic()

    def _on_finished(self, q):
        self.inflight.discard(q)
        self.last_event = time.monotonic()

    def _on_response(self, r):
        self.last_event = time.monotonic()
        self.net.append({'t': common.stamp(), 'mono': time.monotonic(), 'method': r.request.method, 'url': r.url, 'status': r.status,
                         'resource_type': r.request.resource_type})

    def _on_failed(self, q):
        self.inflight.discard(q)
        self.last_event = time.monotonic()
        self.net.append({'t': common.stamp(), 'mono': time.monotonic(), 'method': q.method, 'url': q.url, 'status': None,
                         'resource_type': q.resource_type, 'failure': q.failure})

    def goto(self, url):
        r = self.page.goto(url, wait_until='load')
        return r.status if r else None

    def reload(self):
        r = self.page.reload(wait_until='load')
        return r.status if r else None

    def settle(self):
        """Bounded network-quiet wait before a read (README section 10); its result is evidence, not an action.

        Quiet means no request of the page in flight and no request, response, finish, or failure event for QUIET_MS, counted from
        the later of the last such event and the start of the wait, so a request that the page starts a few milliseconds after the
        action (a timer, an effect) is waited for; the wait ends at quiet or after SETTLE_TIMEOUT_MS, and the read happens once
        either way. Playwright's own networkidle load state is not used: once a page has reached it, waiting for it returns at once,
        whatever the page requests later (operations OP-PREP-E03-REV-01 and -REV-01b)."""
        t0 = time.monotonic()
        try:
            while True:
                now = time.monotonic()
                if not self.inflight and now - max(self.last_event, t0) >= QUIET_MS / 1000:
                    return {'network_quiet': True, 'quiet_ms': QUIET_MS, 'elapsed_s': round(now - t0, 3)}
                if now - t0 >= SETTLE_TIMEOUT_MS / 1000:
                    return {'network_quiet': False, 'quiet_ms': QUIET_MS, 'elapsed_s': round(now - t0, 3), 'in_flight': len(self.inflight)}
                self.page.wait_for_timeout(50)
        except Exception as e:  # noqa: BLE001 - recorded, the read still happens once
            return {'network_quiet': False, 'quiet_ms': QUIET_MS, 'elapsed_s': round(time.monotonic() - t0, 3), 'note': e.__class__.__name__}

    def shot(self, name):
        return self.run.binary(name, self.page.screenshot(full_page=True), 'png')

    def dom(self, name, selector='body'):
        return self.run.text(name, self.page.locator(selector).first.inner_text(timeout=ACTION_TIMEOUT_MS))

    def storage(self, name):
        data = self.page.evaluate("() => ({localStorage: Object.fromEntries(Object.entries(window.localStorage)), "
                                  "sessionStorage: Object.fromEntries(Object.entries(window.sessionStorage))})")
        data['cookies'] = self.context.cookies()
        for c in data['cookies']:
            if c.get('name') == 'token':
                self.run.scrub.secret(c.get('value'))
        return self.run.jsonfile(name, data)

    def responses_since(self, mono, method, fragment):
        return [n for n in self.net if n['mono'] >= mono and n['method'] == method and fragment in n['url'] and n.get('status') is not None]

    def close(self):
        try:
            self.run.jsonfile('network-log', [{k: v for k, v in n.items() if k != 'mono'} for n in self.net])
            self.run.jsonfile('console-log', self.console)
        finally:
            for closer in (self.context.close, self.browser.close, self._pw.stop):
                try:
                    closer()
                except Exception:  # noqa: BLE001 - closing is best effort; the bundle is already written
                    pass


def local_storage(b, key):
    return b.page.evaluate('(k) => window.localStorage.getItem(k)', key)


def session_storage(b, key):
    return b.page.evaluate('(k) => window.sessionStorage.getItem(k)', key)


def parse(text):
    try:
        return json.loads(text) if text is not None else None
    except ValueError:
        return text
