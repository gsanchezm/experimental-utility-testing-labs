"""E08 realization on SUT-01 (web): E08-SUT01-WEB-DELAY. DRAFT (operation OP-PREP-E08).

The ground-truth condition is the documented account `performance_glitch_user`: every request that depends on `apply_user_behavior()`
sleeps 3.0 s on the server (SUT01-EV-0014, -0015; backend/middleware.py), among them GET /api/pizzas, which the catalogue page calls. The
login itself carries no such dependency (backend/routers/auth.py at the pinned commit), so the delay does not fall inside the login.
Static reading V-1 (configuration draft, section 4c).

Blocks per execution: starting-state = the web surface and the API health answer 200 and both accounts log in through the documented
route POST /api/auth/login with the behavior the condition declares (the activation record); method = three loads of the catalogue page,
each in a fresh context: the client state of the E03 SUT-01 web realization is seeded once (market MX, language es, the token of the
account, an empty cart) on a first load of the web root, then the measured navigation to /catalog; the metric is the time at which the
first catalogue item is attached (conditions-draft.json, metric first_item_ms).
"""
import json

from . import attempt, common, instance

MARKET = {'countryCode': 'MX', 'language': 'es', 'locale': 'es-MX', 'currency': 'MXN'}
PASSWORD = 'pizza123'  # the documented password of every SUT-01 test account (README of the pinned commit; E03 executor README, section 4.1)
SETTLE_AFTER_READY_MS = 1000
SPEC = common.Spec('Performance', 'web', [('web', 'web'), ('api', 'api')], True)


def login(run, api, account, label):
    run.scrub.secret(PASSWORD)
    r = run.http('POST', f'{api}/api/auth/login', {'username': account, 'password': PASSWORD}, label=label)
    body = {}
    if r.status == 200 and not r.error:
        try:
            body = r.json()
        except ValueError:
            body = {}
    token = body.get('access_token')
    run.scrub.secret(token)
    return token, body, r.status


def seed_client_state(page, token, body):
    """The client state of the E03 SUT-01 web realization (market MX, language es, the token and the account), one injection."""
    seed = {'omnipizza-auth': json.dumps({'state': {'token': token, 'username': body.get('username'), 'behavior': body.get('behavior')}, 'version': 0}),
            'omnipizza-country': json.dumps({'state': {'countryCode': MARKET['countryCode'], 'countryInfo': None, 'language': MARKET['language'],
                                                       'locale': MARKET['locale'], 'currency': MARKET['currency']}, 'version': 0}),
            'token': token, 'username': body.get('username'), 'countryCode': MARKET['countryCode'],
            'omnipizza-cart': json.dumps({'state': {'items': []}, 'version': 0})}
    page.evaluate('(seed) => { for (const [k, v] of Object.entries(seed)) window.localStorage.setItem(k, v); }', seed)
    return sorted(seed)


class Sut01Web(attempt.Realization):
    SPEC = SPEC

    @property
    def site(self):
        return instance.base(self.job.instance, 'web')

    @property
    def api(self):
        return instance.base(self.job.instance, 'api')

    def check_start(self, run):
        c = self.job.c
        with run.step('starting-state', 'the web surface and the API health answer 200; both accounts log in with the behavior the condition declares') as rec:
            obs = {'web_status': instance.http_status(self.site + '/'), 'api_health_status': instance.http_status(self.api + '/health')}
            rec['observation'] = obs
            if obs['web_status'] != 200 or obs['api_health_status'] != 200:
                raise common.PhaseFailure('starting-state', f'a surface did not answer 200: {obs}', label='START_SURFACE_NOT_READY')
            activation = {}
            for role in ('D', 'Ba'):
                account = self.side(role)['account']
                token, body, status = login(run, self.api, account, f'login-{account}')
                activation[account] = {'login_status': status, 'username': body.get('username'), 'behavior': body.get('behavior'), 'token_received': bool(token)}
                self.carry.setdefault('tokens', {})[account] = (token, body)
            degraded_ok = activation[c['degraded']['account']]['behavior'] == c['degraded']['expected_login_behavior']
            baseline = activation[c['baseline']['account']]
            baseline_ok = baseline['token_received'] and baseline['behavior'] != c['degraded']['expected_login_behavior']
            obs['activation'] = activation
            if not (activation[c['degraded']['account']]['token_received'] and degraded_ok and baseline_ok):
                raise common.PhaseFailure('starting-state', f'activation not confirmed by the login responses: {activation}', label='START_ACTIVATION_NOT_CONFIRMED')
            run.jsonfile('activation', activation)

    def load(self, run, role):
        c = self.job.c
        side = self.side(role)
        label = self.next_label(role)
        token, body = self.carry['tokens'][side['account']]
        s = self.b.session(run, label, c['watch'])
        try:
            first = s.goto(self.site + '/', wait_until='load')
            keys = seed_client_state(s.page, token, body)
            self.begin_measurement(run)
            status = s.goto(self.site + side['page'], wait_until='commit')
            ready = self.wait_ready(s, c['required_ready'], c['ready_timeout_ms'])
            s.page.wait_for_timeout(SETTLE_AFTER_READY_MS)
            return self.finish_load(run, s, role, label, side['account'], side['page'], status,
                                    {'first_load_status': first, 'state_keys_injected': keys, 'ready_within_budget': ready})
        finally:
            s.close()


REALIZATIONS = {'E08-SUT01-WEB-DELAY': Sut01Web}
