"""A fake OWASP ZAP API for the static tests of the E11 executor (operation OP-PREP-E11). Not ZAP, never part of a run.

An in-process HTTP server that answers the calls zap.py makes (method names as recalled when zap.py was written; the real ones are checked in
the first DRY_RUN). `alerts` is what core/view/alerts returns; `behavior` switches failure modes: 'ok', 'api-error' (HTTP 500 on the scan call),
'never-finishes' (the scan status stays at 40), 'no-scan-id' (the scan call returns no id), 'addons-change' (the add-on list differs after the scan)."""
import http.server
import json
import threading
import urllib.parse


class FakeZap:
    def __init__(self, alerts=None, behavior='ok', key_ok=True):
        self.alerts, self.behavior, self.calls = list(alerts or []), behavior, []
        self.addon_reads = 0
        self.enabled_ids = []
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), self._handler())
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def _handler(self):
        outer = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                u = urllib.parse.urlsplit(self.path)
                q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
                parts = [x for x in u.path.split('/') if x]
                outer.calls.append((parts, q))
                status, body = outer.answer(parts[1:], q)
                data = json.dumps(body).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        return H

    def answer(self, route, q):
        key = '/'.join(route)
        if key == 'core/view/version':
            return 200, {'version': '2.17.0'}
        if key == 'autoupdate/view/installedAddons':
            self.addon_reads += 1
            rows = [{'id': 'ascanrules', 'version': '84'}, {'id': 'pscanrules', 'version': '77'}]
            if self.behavior == 'addons-change' and self.addon_reads > 1:
                rows[0] = {'id': 'ascanrules', 'version': '85'}
            return 200, {'installedAddons': rows}
        if key == 'ascan/action/enableScanners':
            self.enabled_ids = [i for i in q.get('ids', '').split(',') if i]
            return 200, {'Result': 'OK'}
        if key == 'ascan/view/scanners':
            rows = [{'id': i, 'name': 'rule ' + i, 'enabled': 'true', 'attackStrength': 'MEDIUM', 'alertThreshold': 'MEDIUM'} for i in self.enabled_ids]
            rows.append({'id': '99999', 'name': 'a disabled rule', 'enabled': 'false', 'attackStrength': 'MEDIUM', 'alertThreshold': 'MEDIUM'})
            return 200, {'scanners': rows}
        if key.startswith('ascan/view/option'):
            if self.behavior == 'options-unreadable':
                return 400, {'code': 'bad_view'}
            return 200, {key.split('/')[-1][6:]: '0' if 'Duration' in key else '5'}
        if key == 'ascan/action/scan':
            if self.behavior == 'api-error':
                return 500, {'code': 'internal_error'}
            return 200, ({} if self.behavior == 'no-scan-id' else {'scan': '0'})
        if key == 'ascan/view/status':
            return 200, {'status': '40' if self.behavior == 'never-finishes' else '100'}
        if key == 'core/view/alerts':
            return 200, {'alerts': self.alerts}
        return 200, {'Result': 'OK'}

    def called(self, route):
        return [q for parts, q in self.calls if '/'.join(parts[1:]) == route]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class FakeLauncher:
    """Starts nothing: the fake server already runs. Same interface as zap.DockerLauncher."""

    def __init__(self, fake, fail_start=False):
        self.fake, self.fail_start = fake, fail_start
        self.port, self.image = fake.port, 'fake@sha256:0'
        self.started, self.stopped, self.key = 0, 0, None

    def start(self, key):
        if self.fail_start:
            from executor import zap
            raise zap.ZapError('ZAP_START_FAILED', 'fake launcher: the container did not start')
        self.started += 1
        self.key = key
        return 'fake'

    def logs(self):
        return 'fake zap log\n'

    def stop(self):
        self.stopped += 1
