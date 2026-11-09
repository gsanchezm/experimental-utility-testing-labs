"""E09 realization for SUT-01, Catalog page (design brief sections 4.4 to 4.7; configuration draft section 3e). DRAFT (operation OP-PREP-E09).

One attempt: API login as the condition's documented account (its response names the behavior, which is the activation
record); one headless browser context; a first load of the web root, one injection of the client state of the E03
SUT-01 realization (the market, locale, and token keys), then the Catalog page; a bounded settle; the DOM snapshot; the
captured catalog responses; one axe-core run with the explicit rule set; then the classification of classify.py.
No Required Action is performed or counted; no retry; no call to the SUT that the browser does not make itself.
"""
import json
import os
import urllib.error
import urllib.request

from . import classify, common, config, instance, scanner, web

# Read in the page at scan time: one record per product heading, decided from the DOM (classify.dom_state decides).
DOM_RECORDS_JS = """() => Array.from(document.querySelectorAll('h2[data-testid^="pizza-name-"]')).map(e => ({
  data_testid: e.getAttribute('data-testid'), text: e.textContent, aria_label: e.getAttribute('aria-label'),
  aria_labelledby: e.getAttribute('aria-labelledby'), title: e.getAttribute('title')}))"""
AXE_RUN_JS = 'async (opts) => await axe.run(document, opts)'
AXE_VERSION_JS = '() => axe.version'
CONTROL_SEED_NOTE = 'client state of the E03 SUT-01 realization (omnipizza-auth, omnipizza-country, token, username, countryCode, empty omnipizza-cart)'


class Http:
    """A plain HTTP call with no proxy, no redirect following, and no retry; the transcript is evidence (scrubbed)."""

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())

    def __init__(self, run):
        self.run = run

    def call(self, method, url, body=None, headers=None, label='http'):
        hdrs = {'Accept': 'application/json', **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode('utf-8')
            hdrs.setdefault('Content-Type', 'application/json')
        req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
        status, rbody, error = None, b'', None
        try:
            with self.OPENER.open(req, timeout=30) as r:
                status, rbody = r.status, r.read()
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                rbody = e.read() or b''
            except Exception:  # noqa: BLE001 - an unreadable error body is evidence only
                rbody = b''
        except Exception as e:  # noqa: BLE001 - a transport failure is an observation
            error = f'{e.__class__.__name__}: {e}'
        shown = None
        if data is not None:
            shown = {k: ('<redacted-password>' if k == 'password' else v) for k, v in body.items()} if isinstance(body, dict) else body
        rec = {'method': method, 'url': url, 'request_body': None if shown is None else json.dumps(shown),
               'response': {'status': status, 'body': rbody[:config.BODY_LIMIT].decode('utf-8', 'replace'), 'body_bytes': len(rbody)},
               'error': error}
        self.run.jsonfile(label, rec)
        return status, rbody, error


def login(run, api, username, password):
    """POST /api/auth/login (the documented test-account route, E03 executor README section 4.1). Returns (token, body, status)."""
    run.scrub.secret(password)  # every later text of the bundle has the password replaced by a marker
    status, rbody, error = Http(run).call('POST', f'{api}/api/auth/login', {'username': username, 'password': password}, label=f'login-{username}')
    body = {}
    if status == 200 and not error:
        try:
            body = json.loads(rbody.decode('utf-8'))
        except ValueError:
            body = {}
    token = body.get('access_token')
    run.scrub.secret(token)
    return token, body, status


def seed_client_state(b, token, login_body):
    """The client state of the E03 SUT-01 realization (market MX, language es, the token and the account), one injection."""
    seed = {'omnipizza-auth': json.dumps({'state': {'token': token, 'username': login_body.get('username'), 'behavior': login_body.get('behavior')}, 'version': 0}),
            'omnipizza-country': json.dumps({'state': {'countryCode': config.MARKET['countryCode'], 'countryInfo': None,
                                                       'language': config.MARKET['language'], 'locale': config.MARKET['locale'],
                                                       'currency': config.MARKET['currency']}, 'version': 0}),
            'token': token, 'username': login_body.get('username'), 'countryCode': config.MARKET['countryCode'],
            'omnipizza-cart': json.dumps({'state': {'items': []}, 'version': 0})}
    b.page.evaluate('(seed) => { for (const [k, v] of Object.entries(seed)) window.localStorage.setItem(k, v); }', seed)
    return sorted(seed)


def read_scan(b, run, axe_source, expected_version):
    """Inject the verified browser build, check its version, run axe with the explicit options, and record the raw result."""
    b.page.add_script_tag(content=axe_source)
    version = b.page.evaluate(AXE_VERSION_JS)
    if version != expected_version:
        raise scanner.ScannerIntegrityError(f'axe.version {version!r} in the page does not equal the pin {expected_version!r}')
    result = b.page.evaluate(AXE_RUN_JS, scanner.AXE_RUN_OPTIONS)
    run.jsonfile('axe-result', result)
    return version, result


def expected_text(kind):
    """The expectation stated before the run (outcome.expected)."""
    if kind == classify.GLITCH:
        return ('empty-heading (predeclared rule, explicit rule scope) reports at least one node of an h2 whose data-testid starts '
                f'with {classify.TARGET_TEST_ID_PREFIX!r}, when every product heading is empty (missing_name draw)')
    return 'empty-heading reports no node of a product heading (control: the rule is expected absent)'


def run(run_obj, condition, axe_source, axe_version):
    """Return (Result, extra) for one attempt; extra carries the realization facts that the manifest records."""
    kind = config.CONDITIONS[condition]['kind']
    account = config.CONDITIONS[condition]['account']
    password = config.ACCOUNTS.get(account)
    if password is None:
        raise common.Abort(f'the password of {account} is not locked in the implementation (HUMAN DECISION HD-E09-A); no browser was started')
    api, site = instance.base(run_obj.instance, 'api'), instance.base(run_obj.instance, 'web')
    token, body, status = login(run_obj, api, account, password)
    activation = {'account': account, 'login_status': status, 'username': body.get('username'), 'behavior': body.get('behavior'),
                  'token_received': bool(token), 'confirmed': False}
    if token and classify.activation_confirmed(kind, body.get('behavior')):
        activation['confirmed'] = True
    run_obj.jsonfile('activation', activation)
    if not activation['confirmed']:
        raise common.Abort(f'activation of {account} not confirmed by the login response (status {status}, behavior {body.get("behavior")!r})')
    b = web.Browser(run_obj)
    # The environment record of the brief (section 4.9): runner image, Chromium build, locale, time zone, viewport, market.
    run_obj.jsonfile('environment', {'chromium': run_obj.tools.get('browser'), 'viewport': config.VIEWPORT,
                                     'browser_locale': config.BROWSER_LOCALE, 'timezone': config.TIMEZONE, 'market': config.MARKET,
                                     'runner_image': os.environ.get('ImageOS'), 'runner_image_version': os.environ.get('ImageVersion')})
    try:
        first = b.goto(site + '/')
        release = None
        try:
            release = b.page.evaluate("() => window.localStorage.getItem('omnipizza-release')")
        except Exception:  # noqa: BLE001 - recorded as null
            release = None
        keys = seed_client_state(b, token, body)
        run_obj.jsonfile('precondition', {'first_load_status': first, 'omnipizza-release (read, not written)': release,
                                          'keys_injected': keys, 'note': CONTROL_SEED_NOTE})
        catalog_status = b.goto(site + config.CATALOG_PATH)
        try:
            b.page.locator('h2[data-testid^="pizza-name-"]').first.wait_for(state='attached', timeout=config.ACTION_TIMEOUT_MS)
        except Exception:  # noqa: BLE001 - no heading rendered: the DOM state below records NO_CARDS
            pass
        settle = b.settle()
        records = b.page.evaluate(DOM_RECORDS_JS)
        dom, dom_detail = classify.dom_state(records)
        run_obj.text('dom-snapshot', b.content(), 'html')
        run_obj.jsonfile('dom-heading-records', records)
        run_obj.binary('screenshot', b.shot(), 'png')
        bodies = b.catalog_bodies()
        run_obj.jsonfile('catalog-responses', bodies)
        classes = [classify.body_class(x['body']) for x in bodies if x.get('status') == 200 and x.get('body') is not None]
        corr = classify.corroboration(dom, classes)
        consistency = classify.draw_consistency(classes)
        version, axe_result = read_scan(b, run_obj, axe_source, axe_version)
        matches = classify.matching_nodes(axe_result)
        total = classify.rule_node_total(axe_result)
        verdict = classify.classify(kind, dom, matches)
        detection = {'predeclared_rule': classify.RULE_ID, 'predeclared_selector': classify.SELECTOR_TEXT, 'matching_nodes': matches,
                     'rule_nodes_total_descriptive': total, 'axe_run_options': scanner.AXE_RUN_OPTIONS, 'axe_version': version,
                     'dom_state': dom, 'dom_detail': dom_detail, 'catalog_status': catalog_status, 'settle': settle,
                     'corroboration': corr, 'draw_consistency': consistency, 'body_classes': classes}
        run_obj.jsonfile('detection', detection)
        b.storage('storage-after-load')
    finally:
        b.close()
    expected = expected_text(kind)
    observed = (f"DOM state {dom} ({dom_detail}); matching nodes {len(matches)}; targets {[m['target'] for m in matches][:3]}; "
                f"realized draw {verdict['realized_draw']}; corroboration {corr}; draw consistency {consistency}")
    result = common.Result(verdict['status'], verdict['outcome_category'], expected, observed, verdict['matches_expected'],
                           notes=[f"realized_draw={verdict['realized_draw']}", f'axe-core {version}; options {json.dumps(scanner.AXE_RUN_OPTIONS)}'])
    return result, {'accessibility_version': version, 'behavior': body.get('behavior')}
