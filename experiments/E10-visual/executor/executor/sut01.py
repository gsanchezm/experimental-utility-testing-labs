"""E10 realization on SUT-01 (web): E10-SUT01-WEB-PROBLEM. DRAFT (operation OP-PREP-E10).

The ground-truth condition is the documented account `problem_user`: for the behavior `problem` the catalogue forces price 0.0 and the image
address https://broken-image-url.com/404.jpg on every item (SUT01-EV-0020; backend/database.py get_catalog at the pinned commit). The card
component replaces a failed image source with another image of upload.wikimedia.org (frontend/src/components/ProductCard.jsx), and the 12
images of the standard catalogue are hosted at upload.wikimedia.org too (backend/constants.py): the condition is an external dependency
(configuration draft, section 4; E10-D-12). Nothing here intercepts or answers a request: the SUT is evaluated as found.

Blocks per execution: starting-state = the web surface and the API health answer 200 and both accounts log in through the documented route
POST /api/auth/login with the behavior the condition declares (the activation record); method = for the view `catalog`, three captures A
(standard_user), B (problem_user) and A2 (standard_user), each in a fresh context: the client state of the E03 SUT-01 web realization is
seeded once (market MX, language es, the token of the account, an empty cart) on a first load of the web root, then the measured navigation
to /catalog; the capture is taken after the first catalogue item is attached and the settle check (conditions-draft.json).
"""
import json

from . import attempt, common, instance

MARKET = {'countryCode': 'MX', 'language': 'es', 'locale': 'es-MX', 'currency': 'MXN'}
PASSWORD = 'pizza123'  # the documented password of every SUT-01 test account (README of the pinned commit; E03 executor README, section 4.1)
SPEC = common.Spec('Visual Testing', 'web', [('web', 'web'), ('api', 'api')], True)


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
    def api(self):
        return instance.base(self.job.instance, 'api')

    def check_start(self, run):
        c = self.job.c
        with run.step('starting-state', 'the web surface and the API health answer 200; both accounts log in with the behavior the condition declares') as rec:
            obs = {'web_status': instance.http_status(self.site + '/'), 'api_health_status': instance.http_status(self.api + '/health')}
            rec['observation'] = obs
            if obs['web_status'] != 200 or obs['api_health_status'] != 200:
                raise common.PhaseFailure('starting-state', f'a surface did not answer 200: {obs}', label='START_SURFACE_NOT_READY')
            activation, confirmed = {}, True
            for state in ('state_a', 'state_b'):
                account = c[state]['account']
                token, body, status = login(run, self.api, account, f'login-{account}')
                activation[account] = {'login_status': status, 'username': body.get('username'), 'behavior': body.get('behavior'),
                                       'expected_behavior': c[state]['expected_login_behavior'], 'token_received': bool(token)}
                self.carry.setdefault('tokens', {})[account] = (token, body)
                confirmed = confirmed and bool(token) and body.get('behavior') == c[state]['expected_login_behavior']
            obs['activation'] = activation
            if not confirmed:
                raise common.PhaseFailure('starting-state', f'activation not confirmed by the login responses: {activation}', label='START_ACTIVATION_NOT_CONFIRMED')
            run.jsonfile('activation', activation)

    def activate(self, run, s, account, label):
        token, body = self.carry['tokens'][account]
        first = s.goto(self.site + '/', wait_until='load')
        keys = seed_client_state(s.page, token, body)
        return {'account': account, 'first_load_status': first, 'state_keys_injected': keys, 'behavior': body.get('behavior')}


REALIZATIONS = {'E10-SUT01-WEB-PROBLEM': Sut01Web}
