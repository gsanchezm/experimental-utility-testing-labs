"""E11 realizations on SUT-01 (OmniPizza backend, pinned commit): the two M1 cells of the IDOR on GET /api/orders/{id} (SUT01-EV-0023).

DRAFT (operation OP-PREP-E11). Blocks per execution: reset = restart of the backend process (the E05 reset of decision D-03 b: orders persist
beyond a session reset), starting-state check = the owner and the requester log in and the owner has created one order (POST /api/cart, then
POST /api/checkout, keeping `order_id`), method = the requester's GET /api/orders/{order_id} (the GET decides, E11-D-15; the PATCH is not
executed), classification = 200 is M1_IDOR_BYPASS_OBSERVED, 403 is M1_IDOR_BLOCKED, any other status is M1_RESPONSE_OTHER. The CONDITION cell
uses `security_glitch_user` as the requester and expects 200; the CONTROL cell uses `standard_user` and expects 403; the owner is
`performance_glitch_user` (its only documented effect is a 3 s delay per call, and it is not the account whose checkout can fail at random).
No M2 exists for SUT-01 (E11-D-9).
"""
from . import attempt, common, instance

PASSWORD = 'pizza123'  # the password of every documented test account of the SUT-01 README (backend/constants.py)
LINE = {'pizza_id': 'p02', 'quantity': 1, 'size': 'small', 'toppings': []}
CHECKOUT_BODY = {'country_code': 'MX', 'items': [LINE], 'name': 'E11 Tester', 'address': 'Calle Uno 123', 'phone': '5512345678',
                 'colonia': 'Centro', 'propina': 0}
SPEC = common.Spec('Security Testing', 'api', ['ENVIRONMENT_RESTART'], None, [('api', 'api')], True)


class IdorOrder(attempt.Realization):
    SPEC = SPEC

    def __init__(self, job):
        super().__init__(job)
        self.owner, self.requester = job.c['owner_account'], job.c['requester_account']

    def api(self):
        return instance.base(self.job.instance, 'api')

    def login(self, run, username, label):
        run.scrub.secret(PASSWORD)
        r = run.http('POST', f'{self.api()}/api/auth/login', {'username': username, 'password': PASSWORD}, label=label)
        try:
            body = r.json() if r.status == 200 else {}
        except ValueError:
            body = {}
        token = body.get('access_token')
        run.scrub.secret(token)
        return r, token

    def reset(self, run):
        with run.step('reset', 'restart the backend process (SIGTERM to the process group, port refused, start in a new session and group, readiness)',
                      ['ENVIRONMENT_RESTART']) as rec:
            instance.restart(run, rec)
        self.carry = {}

    def check_start(self, run):
        with run.step('starting-state', 'the owner and the requester log in; the owner creates one order (POST /api/cart, POST /api/checkout)') as rec:
            obs = rec['observation'] = {}
            r, owner_token = self.login(run, self.owner, 'sut01-login-owner')
            rec['evidence'].append(r.evidence)
            obs['owner_login_status'] = r.status
            r, req_token = self.login(run, self.requester, 'sut01-login-requester')
            rec['evidence'].append(r.evidence)
            obs['requester_login_status'] = r.status
            if not (owner_token and req_token):
                rec['outcome'] = 'FAILURE'
                return
            auth = {'Authorization': f'Bearer {owner_token}'}
            r = run.http('POST', f'{self.api()}/api/cart', {'items': [LINE]}, headers=auth, label='sut01-owner-cart')
            rec['evidence'].append(r.evidence)
            obs['cart_status'] = r.status
            if r.status != 200:
                rec['outcome'] = 'FAILURE'
                return
            r = run.http('POST', f'{self.api()}/api/checkout', CHECKOUT_BODY, headers=auth, label='sut01-owner-checkout')
            rec['evidence'].append(r.evidence)
            obs['checkout_status'] = r.status
            try:
                order_id = r.json().get('order_id') if r.status == 200 else None
            except ValueError:
                order_id = None
            obs['order_id_received'] = bool(order_id)
            if not order_id:
                rec['outcome'] = 'FAILURE'
                return
            self.carry = {'order_id': order_id, 'requester_token': req_token}

    def method(self, run):
        with run.observe('method', f'GET /api/orders/{{order_id}} as {self.requester}') as rec:
            run.mark_stimulus_sent()
            r = run.http('GET', f'{self.api()}/api/orders/{self.carry["order_id"]}', headers={'Authorization': f'Bearer {self.carry["requester_token"]}'},
                         label='sut01-m1-get-order')
            rec['evidence'].append(r.evidence)
            obs = {'status': r.status, 'error': r.error, 'requester': self.requester}
            rec['observation'] = obs
        return obs

    def classify(self, run, obs):
        if obs['status'] is None:
            return 'INTERRUPTED_', f'no response to the GET: {obs["error"]}'
        if obs['status'] == 200:
            return 'M1_IDOR_BYPASS_OBSERVED', f'HTTP 200 for the order of another user, requested as {obs["requester"]}'
        if obs['status'] == 403:
            return 'M1_IDOR_BLOCKED', f'HTTP 403 for the order of another user, requested as {obs["requester"]}'
        return 'M1_RESPONSE_OTHER', f'HTTP {obs["status"]}'


REALIZATIONS = {'E11-SUT01-IDOR-ORDER-M1': IdorOrder, 'E11-SUT01-IDOR-ORDER-M1-CTRL': IdorOrder}
