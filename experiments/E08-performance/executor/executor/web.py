"""E08-performance executor: Playwright for Python helpers.

DRAFT (operation OP-PREP-E08; the browser settings of the E05 and E09 executors). One headless Chromium per job; every page load of every
execution runs in its own fresh browser context (cold: no cache, no storage, no cookies), so that no load can warm another and the paired
loads of one execution differ only in what the condition varies. The measurement script (probe.py) is injected into every document of the
context before any page script runs. No implicit retry beyond Playwright's own actionability waits, each with an explicit timeout.
"""
import importlib.metadata

from . import common, probe

NAV_TIMEOUT_MS = 30000
ACTION_TIMEOUT_MS = 15000
VIEWPORT = {'width': 1280, 'height': 800}
BROWSER_LOCALE = 'en-US'
TIMEZONE = 'UTC'


class Browser:
    def __init__(self, job):
        from playwright.sync_api import sync_playwright
        self.job = job
        self.contexts = 0
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        job.tools['web_runner'] = {'tool': 'Playwright for Python', 'version': importlib.metadata.version('playwright')}
        job.tools['browser'] = {'tool': 'Chromium', 'version': self.browser.version}
        job.tools['performance'] = {'tool': 'Playwright with the browser Performance APIs (PerformanceObserver script ' + probe.PROBE_VERSION + ')',
                                    'version': importlib.metadata.version('playwright')}

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
        run.log('browser', version=self.browser.version, viewport=VIEWPORT)

    def session(self, run, label, watch):
        self.contexts += 1
        return Session(self, run, label, watch)

    def close(self):
        for closer in (self.browser.close, self._pw.stop):
            try:
                closer()
            except Exception:  # noqa: BLE001 - closing is best effort; the bundles are already written
                pass


class Session:
    """One page load: a fresh context with the probe, the network and console logs of that load, and its snapshot."""

    def __init__(self, b, run, label, watch):
        self.b, self.run, self.label = b, run, label
        self.net, self.console = [], []
        self.flushed = False
        self.context = b.browser.new_context(viewport=VIEWPORT, timezone_id=TIMEZONE, locale=BROWSER_LOCALE)
        self.context.set_default_timeout(ACTION_TIMEOUT_MS)
        self.context.set_default_navigation_timeout(NAV_TIMEOUT_MS)
        self.context.add_init_script(script=probe.init_script(watch))
        self.page = self.context.new_page()
        self.page.on('response', lambda r: self.net.append({'t': common.stamp(), 'method': r.request.method, 'url': r.url, 'status': r.status,
                                                            'resource_type': r.request.resource_type}))
        self.page.on('requestfailed', lambda q: self.net.append({'t': common.stamp(), 'method': q.method, 'url': q.url, 'status': None,
                                                                 'resource_type': q.resource_type, 'failure': q.failure}))
        self.page.on('console', lambda m: self.console.append({'t': common.stamp(), 'type': m.type, 'text': m.text}))

    def goto(self, url, wait_until='commit'):
        r = self.page.goto(url, wait_until=wait_until)
        return r.status if r else None

    def snapshot(self):
        """Flush the observers of the document and return the raw snapshot (a dict); None when the page is gone."""
        return self.page.evaluate(probe.FLUSH_JS)

    def shot(self, name):
        return self.run.binary(name, self.page.screenshot(full_page=False), 'png')

    def cookies(self):
        return self.context.cookies()

    def flush_logs(self):
        self.flushed = True
        self.run.jsonfile(f'{self.label}-network-log', self.net)
        self.run.jsonfile(f'{self.label}-console-log', self.console)

    def close(self):
        if not self.flushed:  # a load that stopped on an exception still leaves its logs
            try:
                self.flush_logs()
            except Exception:  # noqa: BLE001 - evidence only
                pass
        try:
            self.context.close()
        except Exception:  # noqa: BLE001 - best effort
            pass
