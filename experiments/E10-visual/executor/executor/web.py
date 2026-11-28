"""E10-visual executor: Playwright for Python helpers.

DRAFT (operation OP-PREP-E10; the browser settings of the E05, E08 and E09 executors). One headless Chromium per job; every capture of every
execution runs in its own fresh browser context (cold: no cache, no storage, no cookies; viewport 1280 x 900, device scale factor 1, en-US,
UTC, reduced motion), so that no capture can warm another and the captures of one view differ only in what the condition varies. No
instrumentation script is injected into the pages: the capture helpers of capture.py only read the page. No implicit retry beyond
Playwright's own actionability waits, each with an explicit timeout.
"""
import importlib.metadata

from . import capture, common, compare

NAV_TIMEOUT_MS = capture.NAV_TIMEOUT_MS
ACTION_TIMEOUT_MS = capture.ACTION_TIMEOUT_MS


class Browser:
    def __init__(self, job):
        from playwright.sync_api import sync_playwright
        self.job = job
        self.contexts = 0
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        job.tools['web_runner'] = {'tool': 'Playwright for Python', 'version': importlib.metadata.version('playwright')}
        job.tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}
        job.tools['visual'] = {'tool': 'Playwright viewport screenshots (' + capture.CAPTURE_VERSION + ') compared with Pixelmatch',
                               'version': compare.PIXELMATCH_VERSION}

    def alive(self):
        try:
            return self.browser.is_connected()
        except Exception:  # noqa: BLE001 - a dead driver answers with an exception
            return False

    def ensure(self, run):
        """A browser that is gone before the first measured navigation of an execution is replaced and the event is recorded (a tooling event)."""
        if not self.alive():
            self.browser = self._pw.chromium.launch(headless=True)
            self.job.tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}
            run.notes.append('tooling: the browser was gone at the start of the execution; a new browser was launched')
        run.log('browser', version=self.browser.version, viewport=capture.VIEWPORT)

    def session(self, run, label):
        self.contexts += 1
        return Session(self, run, label)

    def close(self):
        for closer in (self.browser.close, self._pw.stop):
            try:
                closer()
            except Exception:  # noqa: BLE001 - closing is best effort; the bundles are already written
                pass


class Session:
    """One capture: a fresh context, the network and console logs of that capture."""

    def __init__(self, b, run, label):
        self.b, self.run, self.label = b, run, label
        self.net, self.console = [], []
        self.flushed = False
        self.context = b.browser.new_context(**capture.context_options())
        self.context.set_default_timeout(ACTION_TIMEOUT_MS)
        self.context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        self.page = self.context.new_page()
        self.page.on('response', lambda r: self.net.append({'t': common.stamp(), 'method': r.request.method, 'url': r.url, 'status': r.status,
                                                            'resource_type': r.request.resource_type}))
        self.page.on('requestfailed', lambda q: self.net.append({'t': common.stamp(), 'method': q.method, 'url': q.url, 'status': None,
                                                                 'resource_type': q.resource_type, 'failure': q.failure}))
        self.page.on('console', lambda m: self.console.append({'t': common.stamp(), 'type': m.type, 'text': m.text}))

    def goto(self, url, wait_until='commit'):
        r = self.page.goto(url, wait_until=wait_until)
        return r.status if r else None

    def cookies(self):
        return self.context.cookies()

    def flush_logs(self):
        self.flushed = True
        self.run.jsonfile(f'{self.label}-network-log', self.net)
        self.run.jsonfile(f'{self.label}-console-log', self.console)

    def close(self):
        if not self.flushed:  # a capture that stopped on an exception still leaves its logs
            try:
                self.flush_logs()
            except Exception:  # noqa: BLE001 - evidence only
                pass
        try:
            self.context.close()
        except Exception:  # noqa: BLE001 - best effort
            pass
