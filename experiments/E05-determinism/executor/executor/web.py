"""E05-determinism executor: Playwright for Python helpers.

DRAFT (operation OP-PREP-E05; derived from the E03 executor by copying). One headless Chromium and one browser context per condition job,
kept across the N executions (IMPLEMENTATION-NOTES.md, point 8): the reset of the condition is then a real measurement, which a fresh
context per execution would make nominal. Per execution the network log, the console log, and the in-flight bookkeeping start empty (bind)
and are written into that execution's bundle (flush). A context or page that is gone before the stimulus is a tooling interruption: a new
context is created and the event is recorded (ensure_page). No implicit retry beyond Playwright's own actionability waits, each with an
explicit timeout. Every web read waits for the same bounded network-quiet settle before it reads, identically for every SUT.
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
    def __init__(self, job):
        from playwright.sync_api import sync_playwright
        self.job = job
        self.run = None
        self.contexts = 0
        self._reset_logs()
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        job.tools['web_runner'] = {'tool': 'Playwright for Python', 'version': importlib.metadata.version('playwright')}
        job.tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}
        self._new_context()

    def _reset_logs(self):
        self.net, self.console, self.inflight, self.at_navigation = [], [], {}, []
        self.pending_navigation = None
        self.last_event = time.monotonic()

    def _new_context(self):
        self.contexts += 1
        self.context = self.browser.new_context(viewport=VIEWPORT, timezone_id='UTC', locale='en-US')
        self.context.set_default_timeout(ACTION_TIMEOUT_MS)
        self.context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        self.page = self.context.new_page()
        self.page.on('request', self._on_request)
        self.page.on('response', self._on_response)
        self.page.on('requestfinished', self._on_finished)
        self.page.on('requestfailed', self._on_failed)
        self.page.on('framenavigated', self._on_navigated)
        self.page.on('console', lambda m: self.console.append({'t': common.stamp(), 'type': m.type, 'text': m.text}))

    def bind(self, run):
        """Start of an execution: its logs start empty and go into its bundle; a page or context that is gone is replaced (recorded)."""
        self.run = run
        self._reset_logs()
        try:
            alive = self.browser.is_connected() and not self.page.is_closed()
        except Exception:  # noqa: BLE001 - a dead driver answers with an exception
            alive = False
        if not alive:
            try:
                self.context.close()
            except Exception:  # noqa: BLE001 - best effort
                pass
            if not self.browser.is_connected():
                self.browser = self._pw.chromium.launch(headless=True)
                self.job.tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}
            self._new_context()
            run.notes.append(f'tooling: the browser context was gone at the start of the execution; context number {self.contexts} was created')
        run.log('browser', version=self.browser.version, viewport=VIEWPORT, context_number=self.contexts)

    def _on_request(self, q):
        self.inflight[q] = {'started_at': common.stamp(), 'method': q.method, 'url': q.url, 'resource_type': q.resource_type,
                            'response_status': None}
        if q.is_navigation_request() and self._in_main_frame(q):
            self.pending_navigation = q
        self.last_event = time.monotonic()

    def _in_main_frame(self, q):
        try:
            return q.frame == self.page.main_frame
        except Exception:  # noqa: BLE001 - a service-worker request has no frame
            return False

    def _on_finished(self, q):
        self.inflight.pop(q, None)
        self.last_event = time.monotonic()

    def _on_response(self, r):
        self.last_event = time.monotonic()
        if r.request in self.inflight:
            self.inflight[r.request]['response_status'] = r.status
        self.net.append({'t': common.stamp(), 'mono': time.monotonic(), 'method': r.request.method, 'url': r.url, 'status': r.status,
                         'resource_type': r.request.resource_type})

    def _on_failed(self, q):
        self.inflight.pop(q, None)
        if q is self.pending_navigation:  # its document never commits (a 204 or 205 answer, a download, an error)
            self.pending_navigation = None
        self.last_event = time.monotonic()
        self.net.append({'t': common.stamp(), 'mono': time.monotonic(), 'method': q.method, 'url': q.url, 'status': None,
                         'resource_type': q.resource_type, 'failure': q.failure})

    def _on_navigated(self, frame):
        """At the commit of a new document in the main frame, after a navigation request of the main frame, the requests of the replaced
        document leave the wait (the browser closes them at the commit and Playwright reports no event for them); each is kept for the
        network log file (in_flight_at_navigation). Same-document navigations, commits without a navigation request, and subframe commits
        change nothing."""
        if frame != self.page.main_frame or self.pending_navigation is None:
            return
        t, keep, self.pending_navigation = common.stamp(), self.pending_navigation, None
        for q in [q for q in self.inflight if q is not keep]:
            e = self.inflight.pop(q)
            self.at_navigation.append({'t': t, 'method': e['method'], 'url': e['url'], 'status': None, 'resource_type': e['resource_type'],
                                       'in_flight_at_navigation': True, 'started_at': e['started_at'],
                                       'response_status': e['response_status'], 'navigated_to': frame.url})

    def goto(self, url):
        r = self.page.goto(url, wait_until='load')
        return r.status if r else None

    def reload(self):
        r = self.page.reload(wait_until='load')
        return r.status if r else None

    def in_flight_requests(self):
        return [dict(v) for v in self.inflight.values()]

    def settle(self):
        """Bounded network-quiet wait before a read; its result is evidence, not an action. Quiet means no request of the page in flight
        and no request, response, finish, or failure event for QUIET_MS, counted from the later of the last such event and the start of
        the wait; the wait ends at quiet or after SETTLE_TIMEOUT_MS, and the read happens once either way."""
        t0 = time.monotonic()
        try:
            while True:
                now = time.monotonic()
                if not self.inflight and now - max(self.last_event, t0) >= QUIET_MS / 1000:
                    return {'network_quiet': True, 'quiet_ms': QUIET_MS, 'elapsed_s': round(now - t0, 3)}
                if now - t0 >= SETTLE_TIMEOUT_MS / 1000:
                    return {'network_quiet': False, 'quiet_ms': QUIET_MS, 'elapsed_s': round(now - t0, 3), 'in_flight': len(self.inflight),
                            'in_flight_requests': self.in_flight_requests()}
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

    def visible(self, locator, timeout_ms=ACTION_TIMEOUT_MS):
        """True when the locator becomes visible within the budget; False is an observation (the page did not show it), not an exception."""
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        try:
            locator.first.wait_for(state='visible', timeout=timeout_ms)
            return True
        except PlaywrightTimeout:
            return False

    def flush(self):
        """End of an execution: the network log lists the responses and failures in event order, then the requests that left the wait at a
        main-frame navigation, then one entry per request still in flight; the page and the context stay open for the next execution."""
        t = common.stamp()
        at_close = [{'t': t, 'method': e['method'], 'url': e['url'], 'status': None, 'resource_type': e['resource_type'],
                     'in_flight_at_close': True, 'started_at': e['started_at'], 'response_status': e['response_status']}
                    for e in self.in_flight_requests()]
        self.run.jsonfile('network-log', [{k: v for k, v in n.items() if k != 'mono'} for n in self.net] + self.at_navigation + at_close)
        self.run.jsonfile('console-log', self.console)

    def close(self):
        for closer in (self.context.close, self.browser.close, self._pw.stop):
            try:
                closer()
            except Exception:  # noqa: BLE001 - closing is best effort; the bundles are already written
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
