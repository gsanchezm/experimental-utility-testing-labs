"""E04 realizations on SUT-05 (api): E04-SUT05-API-01 and E04-SUT05-API-02 (establishment-only mirrors of E05-SUT05-API-01 and -02). DRAFT (operation OP-PREP-E04).

Blocks per attempt: reset = restart of the SUT process (ENVIRONMENT_RESTART; SIGTERM to the whole group, port refused, start in a new session and
group, readiness), starting-state check = the documented account's basket holds no item (declared starting state of the E03 SUT-05 realization,
executor README 4.7), establishment = one basket line (ProductId 1), verification = the basket shows ProductId 1. The restart is performed in
every attempt, the first included. The E05 stimuli (a wrong-password login for API-01; a captcha read for API-02) are removed, so the two E04
conditions run the same blocks; that is an open item of the START package.
"""
from . import attempt, common, instance

ACCOUNT = {'email': 'mc.safesearch@juice-sh.op', 'password': 'Mr. N00dles'}
SPEC = common.Spec('API', 'api', ['ENVIRONMENT_RESTART'], ['PREDEFINED_ACCOUNT', 'API_SEED'], [('api', 'api')], True)


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
            r, ids = self._basket(run, 'sut05-basket-target-state')
            rec['evidence'].append(r.evidence)
            rec['observation'] = {'status': r.status, 'product_ids': ids}
            if not ids or 1 not in ids:
                rec['outcome'] = 'FAILURE'


class Api01(Sut05):
    """E04-SUT05-API-01 (establishment-only): the blocks of E05-SUT05-API-01 without its stimulus (a wrong-password login)."""


class Api02(Sut05):
    """E04-SUT05-API-02 (establishment-only): the blocks of E05-SUT05-API-02 without its stimulus (a captcha read)."""


REALIZATIONS = {'E04-SUT05-API-01': Api01, 'E04-SUT05-API-02': Api02}
