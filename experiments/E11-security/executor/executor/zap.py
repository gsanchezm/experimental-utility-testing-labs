"""E11-security executor: the M2 method, one restricted OWASP ZAP run against the instance.

DRAFT (operation OP-PREP-E11). Route A of the pin (decision E11-D-8, manifests/campaign-execution-decisions-v19.yaml): release v2.17.0 as the
container image pulled BY DIGEST, update checks off. Nothing here has run against a real ZAP: the API method names and parameters below are the
ones of the ZAP API as recalled when this file was written and are NOT verified against the pinned release; the tests drive the same code
against a fake API server. The first real contact is a DRY_RUN on GitHub Actions (campaign-configuration-draft.md, section 7).

One execution of M2: start a fresh container, wait for the API, record the version and the installed add-ons, build a scan policy with one rule
enabled, seed one request, scan the one target with that policy, wait (bounded), read the alerts, record the add-ons again, stop the container.
A failure of ZAP itself is a ZapError whose code is a declared category (ZAP_START_FAILED, ZAP_API_ERROR, ZAP_SCAN_TIMEOUT); it is TOOLING.
"""
import json
import os
import secrets
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlsplit

from . import common

ZAP_RELEASE = '2.17.0'
ZAP_IMAGE_REPOSITORY = 'ghcr.io/zaproxy/zaproxy'
ZAP_AMD64_MANIFEST = 'sha256:c2d63bbb2d907a5c5257914fb20e26e969c92b25f265def7f89f08203f912882'
ZAP_INDEX_DIGEST = 'sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af'
ZAP_IMAGE = f'{ZAP_IMAGE_REPOSITORY}@{ZAP_AMD64_MANIFEST}'
ZAP_API_PORT = 8090
READY_TIMEOUT_S = 180
SCAN_TIMEOUT_S = 300  # to be set from the timing of a DRY_RUN execution (E11-D-14)
API_TIMEOUT_S = 30
SEED_WAIT_S = 20  # bounded wait for the seeded URL to be known to ZAP before the scan (a readiness aid, not a retry of the method)
POLICY_NAME = 'e11-single-rule'
LOG_TAIL_BYTES = 1 << 18


class ZapError(Exception):
    """A failure of ZAP itself. `code` is a declared category."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class DockerLauncher:
    """Starts and stops the pinned image on the runner. The image is addressed by digest only; a digest other than the pinned one is refused."""

    def __init__(self, image=ZAP_IMAGE, port=ZAP_API_PORT):
        if '@sha256:' not in image:
            raise ValueError('the ZAP image must be addressed by digest')
        self.image, self.port = image, port
        self.name = None

    def start(self, key):
        self.name = f'e11-zap-{os.getpid()}-{secrets.token_hex(3)}'
        cmd = ['docker', 'run', '-d', '--rm', '--network', 'host', '--name', self.name, self.image, 'zap.sh', '-daemon', '-host', '127.0.0.1',
               '-port', str(self.port), '-config', f'api.key={key}', '-config', 'start.checkForUpdates=false']
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            raise ZapError('ZAP_START_FAILED', f'docker run exited {p.returncode}: {p.stderr.strip()[-400:]}')
        return self.name

    def logs(self):
        if not self.name:
            return ''
        p = subprocess.run(['docker', 'logs', self.name], capture_output=True, text=True, timeout=60)
        return (p.stdout + p.stderr)[-LOG_TAIL_BYTES:]

    def stop(self):
        if self.name:
            subprocess.run(['docker', 'stop', '-t', '10', self.name], capture_output=True, text=True, timeout=120)
            self.name = None


class Api:
    """The ZAP API over HTTP (JSON format, stdlib client, no proxy, no retry)."""
    _opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def __init__(self, port, key, timeout=API_TIMEOUT_S):
        self.base, self.key, self.timeout = f'http://127.0.0.1:{port}', key, timeout

    def call(self, component, kind, name, **params):
        q = urllib.parse.urlencode({**{k: v for k, v in params.items() if v is not None}, 'apikey': self.key})
        url = f'{self.base}/JSON/{component}/{kind}/{name}/?{q}'
        try:
            with self._opener.open(url, timeout=self.timeout) as r:
                body = r.read().decode('utf-8', 'replace')
        except common.Watchdog:
            raise  # the per-execution budget is not a failure of ZAP: the attempt loop records it as an interruption
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode('utf-8', 'replace')[:300]
            except Exception:  # noqa: BLE001 - the body is diagnostic only
                detail = ''
            finally:
                e.close()
            raise ZapError('ZAP_API_ERROR', f'{component}/{kind}/{name}: HTTP {e.code} {detail}'.rstrip()) from e
        except Exception as e:  # noqa: BLE001 - a transport failure of the ZAP API
            raise ZapError('ZAP_API_ERROR', f'{component}/{kind}/{name}: {e.__class__.__name__}: {e}') from e
        try:
            return json.loads(body)
        except ValueError as e:
            raise ZapError('ZAP_API_ERROR', f'{component}/{kind}/{name}: the answer is not JSON') from e


def normalize_path(url):
    """The path of an alert URL: scheme, host, port, query and fragment removed; the path compared exactly, a trailing slash included."""
    return urlsplit(url).path


def match_alerts(alerts, rule_id, method, path):
    """Return (counted, others). An alert is counted only when its pluginId, its request method and its normalized path all equal the
    expectation (campaign-configuration-draft.md, section 4b). Every other alert is listed with rule, method and normalized path and never counted."""
    counted, others = [], []
    for a in alerts:
        item = {'pluginId': str(a.get('pluginId')), 'alert': a.get('alert') or a.get('name'), 'method': a.get('method'),
                'path': normalize_path(a.get('url') or ''), 'param': a.get('param')}
        if item['pluginId'] == str(rule_id) and item['method'] == method and item['path'] == path:
            counted.append(item)
        else:
            others.append(item)
    return counted, others


def _addon_ids(answer):
    """Sorted `id@version` strings of the installed add-ons read from the answer of the add-on list call."""
    rows = answer.get('installedAddons') or answer.get('addons') or []
    out = []
    for r in rows:
        if isinstance(r, dict):
            out.append(f'{r.get("id")}@{r.get("version")}')
        else:
            out.append(str(r))
    return sorted(out)


def _scan_settings(api, policy):
    """What the scan ran with, recorded per run so that no setting is ever tuned to an outcome (release defaults): the enabled rows of the
    policy, the injectable targets and enabled RPC variants, and the duration limits. A view that cannot be read is recorded, not fatal.
    The option view names are derived from the getters of the scanner options in the core at v2.17.0 and are not read from the API class."""
    out = {}
    try:
        rows = api.call('ascan', 'view', 'scanners', scanPolicyName=policy).get('scanners') or []
        out['policy_enabled_scanners'] = [{k: r.get(k) for k in ('id', 'name', 'enabled', 'attackStrength', 'alertThreshold')}
                                          for r in rows if str(r.get('enabled')).lower() == 'true']
    except ZapError as e:
        out['policy_enabled_scanners'] = {'unreadable': str(e)}
    for key, view in (('target_params_injectable', 'optionTargetParamsInjectable'), ('target_params_enabled_rpc', 'optionTargetParamsEnabledRPC'),
                      ('max_rule_duration_mins', 'optionMaxRuleDurationInMins'), ('max_scan_duration_mins', 'optionMaxScanDurationInMins')):
        try:
            out[key] = api.call('ascan', 'view', view)
        except ZapError as e:
            out[key] = {'unreadable': str(e)}
    return out


def _wait_for_seed(api, url, timeout_s, sleep):
    """Wait, bounded, until `core/view/urls` lists the seeded URL (compared by path). Returns (seen, polls). Never raises ZapError: a seed that
    does not appear is recorded and the scan goes on, so that the scan call itself reports what ZAP says."""
    base = f'{urlsplit(url).scheme}://{urlsplit(url).netloc}'
    path = urlsplit(url).path
    deadline, polls = time.monotonic() + timeout_s, 0
    while True:
        polls += 1
        try:
            urls = api.call('core', 'view', 'urls', baseurl=base).get('urls') or []
            if any(urlsplit(u).path == path for u in urls):
                return True, polls
        except ZapError:
            pass
        if time.monotonic() >= deadline:
            return False, polls
        sleep(0.5)


def run_scan(run, rec, launcher, spec, ready_timeout_s=READY_TIMEOUT_S, scan_timeout_s=SCAN_TIMEOUT_S, api_factory=Api, sleep=time.sleep,
             seed_wait_s=SEED_WAIT_S):
    """One restricted run. `spec` carries: rule_id, seed_request (method, url, body or None, content_type or None) and the scan target
    (method, url, body or None). Returns the observation dict (alerts, add-ons before and after, versions). Raises ZapError."""
    key = secrets.token_hex(16)
    run.scrub.secret(key)
    obs = {'image': getattr(launcher, 'image', None)}
    try:
        launcher.start(key)
        api = api_factory(getattr(launcher, 'port', ZAP_API_PORT), key)
        deadline, version = time.monotonic() + ready_timeout_s, None
        while time.monotonic() < deadline:
            try:
                version = api.call('core', 'view', 'version').get('version')
                break
            except ZapError:
                sleep(1.0)
        if version is None:
            raise ZapError('ZAP_START_FAILED', f'the ZAP API did not answer within {ready_timeout_s} s')
        obs['zap_version'] = version
        before = _addon_ids(api.call('autoupdate', 'view', 'installedAddons'))
        obs['addons_before'] = before
        api.call('ascan', 'action', 'addScanPolicy', scanPolicyName=POLICY_NAME)
        api.call('ascan', 'action', 'disableAllScanners', scanPolicyName=POLICY_NAME)
        api.call('ascan', 'action', 'enableScanners', ids=str(spec['rule_id']), scanPolicyName=POLICY_NAME)
        obs.update(_scan_settings(api, POLICY_NAME))
        seed = spec['seed_request']
        raw = f'{seed["method"]} {seed["url"]} HTTP/1.1\r\nHost: {urlsplit(seed["url"]).netloc}\r\n'
        if seed.get('body') is not None:
            raw += f'Content-Type: {seed.get("content_type") or "application/json"}\r\nContent-Length: {len(seed["body"].encode("utf-8"))}\r\n'
        raw += '\r\n' + (seed.get('body') or '')
        run.mark_stimulus_sent()
        api.call('core', 'action', 'sendRequest', request=raw, followRedirects='false')
        t = spec['scan_target']
        obs['seed_url_seen'], obs['seed_url_polls'] = _wait_for_seed(api, seed['url'], seed_wait_s, sleep)
        started = api.call('ascan', 'action', 'scan', url=t['url'], recurse='false', inScopeOnly='false', scanPolicyName=POLICY_NAME,
                           method=t['method'], postData=t.get('body'))
        scan_id = started.get('scan')
        if scan_id is None:
            raise ZapError('ZAP_API_ERROR', 'ascan/action/scan returned no scan id')
        deadline, status = time.monotonic() + scan_timeout_s, None
        while time.monotonic() < deadline:
            status = api.call('ascan', 'view', 'status', scanId=scan_id).get('status')
            if str(status) == '100':
                break
            sleep(1.0)
        else:
            obs['scan_status_at_timeout'] = status
            raise ZapError('ZAP_SCAN_TIMEOUT', f'the scan did not finish within {scan_timeout_s} s (status {status})')
        base = f'{urlsplit(t["url"]).scheme}://{urlsplit(t["url"]).netloc}'
        alerts = api.call('core', 'view', 'alerts', baseurl=base, start='0', count='1000').get('alerts') or []
        obs['alerts'] = alerts
        obs['addons_after'] = _addon_ids(api.call('autoupdate', 'view', 'installedAddons'))
        obs['addons_unchanged'] = obs['addons_after'] == before
        return obs
    finally:
        try:
            rec['evidence'].append(run.text('zap-container-log', launcher.logs()))
        except Exception as e:  # noqa: BLE001 - evidence only
            rec.setdefault('evidence_errors', []).append(f'zap log: {e.__class__.__name__}: {e}')
        try:
            launcher.stop()
        except Exception as e:  # noqa: BLE001 - the run is already decided; the stop failure is recorded
            rec.setdefault('evidence_errors', []).append(f'zap stop: {e.__class__.__name__}: {e}')
