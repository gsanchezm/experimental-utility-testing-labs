"""E09 browser driver: Playwright for Python (the only module that imports Playwright).

DRAFT (operation OP-PREP-E09). One headless Chromium context per attempt, the viewport, time zone, and locale of
config.py, no retry, and explicit timeouts. Screenshots, the DOM snapshot, storage, and the network log are evidence.
The catalog responses are kept as Playwright response objects and read once after the page settles; no request is
ever made from Python to the SUT (a request from Python would draw a new activation mode; design brief, section 4.4).
"""
import importlib.metadata
import json
import time

from . import common, config

CATALOG_API_FRAGMENT = config.CATALOG_API_PATH


class Browser:
    def __init__(self, run):
        from playwright.sync_api import sync_playwright
        self.run = run
        self.net = []
        self.console = []
        self.inflight = {}
        self.catalog_responses = []
        self.last_event = time.monotonic()
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        self.context = self.browser.new_context(viewport=config.VIEWPORT, timezone_id=config.TIMEZONE, locale=config.BROWSER_LOCALE)
        self.context.set_default_timeout(config.ACTION_TIMEOUT_MS)
        self.context.set_default_navigation_timeout(config.NAV_TIMEOUT_MS)
        self.page = self.context.new_page()
        self.page.on('request', self._on_request)
        self.page.on('response', self._on_response)
        self.page.on('requestfinished', self._on_finished)
        self.page.on('requestfailed', self._on_failed)
        self.page.on('console', lambda m: self.console.append({'t': common.stamp(), 'type': m.type, 'text': m.text}))
        run.tools['web_runner'] = {'tool': 'Playwright for Python', 'version': importlib.metadata.version('playwright')}
        run.tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}
        run.log('browser', version=self.browser.version, viewport=config.VIEWPORT)

    def _on_request(self, q):
        self.inflight[q] = {'started_at': common.stamp(), 'method': q.method, 'url': q.url, 'resource_type': q.resource_type}
        self.last_event = time.monotonic()

    def _on_finished(self, q):
        self.inflight.pop(q, None)
        self.last_event = time.monotonic()

    def _on_failed(self, q):
        self.inflight.pop(q, None)
        self.last_event = time.monotonic()
        self.net.append({'t': common.stamp(), 'method': q.method, 'url': q.url, 'status': None, 'resource_type': q.resource_type,
                         'failure': q.failure})

    def _on_response(self, r):
        self.last_event = time.monotonic()
        self.net.append({'t': common.stamp(), 'method': r.request.method, 'url': r.url, 'status': r.status,
                         'resource_type': r.request.resource_type})
        if r.request.method == 'GET' and CATALOG_API_FRAGMENT in r.url:
            self.catalog_responses.append({'t': common.stamp(), 'url': r.url, 'status': r.status, 'response': r})

    def goto(self, url):
        r = self.page.goto(url, wait_until='load')
        return r.status if r else None

    def settle(self):
        """Bounded network-quiet wait before a read (evidence, not a judgment): no request in flight and no event for QUIET_MS."""
        t0 = time.monotonic()
        try:
            while True:
                now = time.monotonic()
                if not self.inflight and now - max(self.last_event, t0) >= config.QUIET_MS / 1000:
                    return {'network_quiet': True, 'elapsed_s': round(now - t0, 3)}
                if now - t0 >= config.SETTLE_TIMEOUT_MS / 1000:
                    return {'network_quiet': False, 'elapsed_s': round(now - t0, 3), 'in_flight': len(self.inflight)}
                self.page.wait_for_timeout(50)
        except Exception as e:  # noqa: BLE001 - recorded; the read still happens once
            return {'network_quiet': False, 'elapsed_s': round(time.monotonic() - t0, 3), 'note': e.__class__.__name__}

    def catalog_bodies(self):
        """Each captured GET of the catalog API: status and the body text (read once, after the page settled)."""
        out = []
        for c in self.catalog_responses:
            try:
                body = c['response'].text()
            except Exception as e:  # noqa: BLE001 - a body that cannot be read is evidence of that fact
                body = None
                out.append({'t': c['t'], 'url': c['url'], 'status': c['status'], 'body': None, 'error': e.__class__.__name__})
                continue
            out.append({'t': c['t'], 'url': c['url'], 'status': c['status'], 'body': body[:config.BODY_LIMIT]})
        return out

    def content(self):
        return self.page.content()

    def shot(self):
        return self.page.screenshot(full_page=True)

    def storage(self, name):
        data = self.page.evaluate("() => ({localStorage: Object.fromEntries(Object.entries(window.localStorage))})")
        for k, v in list(data['localStorage'].items()):
            if k == 'token' and isinstance(v, str):
                self.run.scrub.secret(v)
        return self.run.jsonfile(name, data)

    def close(self):
        """The network log and console log are written; then the browser closes (best effort)."""
        try:
            self.run.jsonfile('network-log', self.net)
            self.run.jsonfile('console-log', self.console)
        finally:
            for closer in (self.context.close, self.browser.close, self._pw.stop):
                try:
                    closer()
                except Exception:  # noqa: BLE001 - closing is best effort; the bundle is already written
                    pass


def json_text(text):
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return None
