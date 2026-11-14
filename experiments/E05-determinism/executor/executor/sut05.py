"""E05 realizations on SUT-05 (api): E05-SUT05-API-01 and E05-SUT05-API-02. DRAFT (operation OP-PREP-E05).

Blocks per execution: reset = restart of the SUT process (ENVIRONMENT_RESTART; SIGTERM to the whole group, port refused, start in a new
session and group, readiness), starting-state check = the documented account's basket holds no item (declared starting state of the E03
SUT-05 realization, executor README 4.7), establishment = one basket line (ProductId 1), verification = the basket shows ProductId 1,
stimulus = a wrong-password login (API-01) or a captcha read (API-02). The restart is performed in every execution, the first included.
"""
from . import attempt, common, instance

ACCOUNT = {'email': 'mc.safesearch@juice-sh.op', 'password': 'Mr. N00dles'}
WRONG_PASSWORD = 'wrong-password-e05'
REJECTION_BODY = 'Invalid email or password.'
SPEC = common.Spec('API', 'api', ['ENVIRONMENT_RESTART'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api')], True)


def _text(r):
    t = r.body.decode('utf-8', 'replace').strip()
    return t[1:-1] if len(t) >= 2 and t[0] == '"' and t[-1] == '"' else t


class Sut05(attempt.Realization):
    SPEC = SPEC

    def api(self):
        return instance.base(self.job.instance, 'api')

    def _login(self, run, label):
        r = run.http('POST', f'{self.api()}/rest/user/login', ACCOUNT, label=label)
        try:
            auth = (r.json().get('authentication') or {}) if r.status == 200 else {}
        except ValueError:
            auth = {}
        run.scrub.secret(auth.get('token'))
        return r, auth.get('token'), auth.get('bid')

    def _basket(self, run, label):
        r = run.http('GET', f'{self.api()}/rest/basket/{self.carry["bid"]}', headers={'Authorization': f'Bearer {self.carry["token"]}'}, label=label)
        try:
            body = r.json() if r.status == 200 else None
        except ValueError:
            body = None
        data = None if body is None else body.get('data')
        return r, None if data is None else [p.get('id') for p in (data.get('Products') or [])]

    def reset(self, run):
        with run.step('reset', 'restart the SUT process (SIGTERM to the process group, port refused, start in a new session and group, readiness)',
                      ['ENVIRONMENT_RESTART']) as rec:
            instance.restart(run, rec)
        self.carry = {}

    def check_start(self, run):
        with run.step('starting-state', "POST /rest/user/login (documented account), then GET /rest/basket/{bid}: the basket holds no item") as rec:
            r, token, bid = self._login(run, 'sut05-login')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'login_status': r.status, 'token_received': bool(token), 'bid': bid}
            if not (token and bid):
                rec['outcome'] = 'FAILURE'
                return
            self.carry = {'token': token, 'bid': bid}
            r, ids = self._basket(run, 'sut05-basket-start')
            rec['evidence'].append(r.evidence)
            rec['observation'].update({'basket_status': r.status, 'product_ids': ids})
            if r.status != 200 or ids not in ([], None):
                rec['outcome'] = 'FAILURE'

    def establish(self, run):
        with run.step('establishment', 'POST /api/BasketItems {ProductId 1, BasketId <bid>, quantity 1}', ['API_SEED']) as rec:
            r = run.http('POST', f'{self.api()}/api/BasketItems', {'ProductId': 1, 'BasketId': self.carry['bid'], 'quantity': 1},
                         headers={'Authorization': f'Bearer {self.carry["token"]}'}, label='sut05-add-item')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status}
            if r.status != 200:
                rec['outcome'] = 'FAILURE'

    def verify_target(self, run):
        with run.step('verification', 'GET /rest/basket/{bid} shows ProductId 1') as rec:
            r, ids = self._basket(run, 'sut05-basket-pre-stimulus')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'product_ids': ids}
            if not ids or 1 not in ids:
                rec['outcome'] = 'FAILURE'


class Api01(Sut05):
    """Stimulus: POST /rest/user/login for the documented account with a wrong password (F11: HTTP 401, body 'Invalid email or password.')."""

    def stimulus(self, run):
        with run.observe('stimulus', 'POST /rest/user/login with a wrong password') as rec:
            run.mark_stimulus_sent()
            r = run.http('POST', f'{self.api()}/rest/user/login', {'email': ACCOUNT['email'], 'password': WRONG_PASSWORD}, label='sut05-stimulus-login')
            rec['evidence'].append(r.evidence)
            obs = {'status': r.status, 'error': r.error, 'body': _text(r)[:200] if r.status is not None else None}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] == 401 and obs['body'] == REJECTION_BODY:
            return 'S_REJECTED_AS_EXPECTED', f'HTTP 401, body {obs["body"]!r}'
        if obs['status'] == 200:
            return 'S_ACCEPTED_UNEXPECTED', 'HTTP 200 for a wrong password'
        return 'S_OTHER', f'HTTP {obs["status"]}, body {obs["body"]!r}'


class Api02(Sut05):
    """Stimulus: GET /rest/captcha (F12). The projection keeps the presence of the three keys; captchaId (a counter), the operands, the
    operators and the answer are excluded because they vary by design."""
    KEYS = ('captchaId', 'captcha', 'answer')

    def stimulus(self, run):
        with run.observe('stimulus', 'GET /rest/captcha') as rec:
            run.mark_stimulus_sent()
            r = run.http('GET', f'{self.api()}/rest/captcha', label='sut05-stimulus-captcha')
            rec['evidence'].append(r.evidence)
            keys, parsed = None, None
            if r.status == 200:
                try:
                    body = r.json()
                    parsed = isinstance(body, dict)
                    keys = sorted(body) if parsed else None
                except ValueError:
                    parsed = False
            obs = {'status': r.status, 'error': r.error, 'parsed': parsed, 'keys': keys}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the stimulus: {obs["error"]}'
        if obs['status'] == 200 and obs['parsed'] is False:
            return 'S_OTHER', 'HTTP 200 with a body that is not a JSON object'
        if obs['status'] == 200 and all(k in (obs['keys'] or []) for k in self.KEYS):
            return 'S_CAPTCHA_ISSUED', f'HTTP 200 with the keys {obs["keys"]}'
        return 'S_CAPTCHA_NOT_ISSUED', f'HTTP {obs["status"]}, keys {obs["keys"]}'


REALIZATIONS = {'E05-SUT05-API-01': Api01, 'E05-SUT05-API-02': Api02}
