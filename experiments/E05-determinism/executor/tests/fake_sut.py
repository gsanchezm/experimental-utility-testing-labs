"""Fake systems under test for the static tests of the E05 executor (operation OP-PREP-E05). Not a SUT, never part of a run.

python3 -I fake_sut.py <sut01|sut04|sut05> <port>. State is in memory, so a restart of the process (as the executor does for SUT-01 and
SUT-05) clears it, like the real instances. FAKE_DELETE_MODE=fail makes DELETE /booking/{id} answer 500; =noop answers 202 and keeps the
booking (a reset that did not hold). FAKE_NO_MESSAGE=1 makes the booking service post no message."""
import http.server
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from executor import sut01_expected as ex  # noqa: E402

KIND, PORT = sys.argv[1], int(sys.argv[2])
S = {'logins': 0, 'sessions': {}, 'catalog_calls': 0, 'checkouts': 0, 'bookings': [], 'next_id': 1, 'messages': 0, 'captchas': 0, 'baskets': {}}
BEHAVIOR = {'standard_user': 'standard', 'locked_out_user': 'locked_out', 'performance_glitch_user': 'performance_glitch', 'error_user': 'error',
            'a11y_glitch_user': 'a11y_glitch'}
DATA = ex.load()
JWT_HEAD = 'ey' + 'J'  # built by concatenation: the export builder fails closed on a literal token-like prefix in a file


def a11y_catalog(call):
    mode = ('missing_name', 'extreme_text', 'wrong_lang')[call % 3]
    out = []
    for p in DATA['pizzas']:
        name, desc = p['name']['en'], p['description']['en']
        if mode == 'missing_name':
            name = ''
        elif mode == 'extreme_text':
            name, desc = ' '.join([name] * 15), ' '.join([desc] * 15)
        else:
            name, desc = p['name']['ja'], p['description']['ja']
        out.append({'id': p['id'], 'name': name, 'description': desc, 'price': 1.0, 'currency': 'MXN'})
    return {'pizzas': out}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, status, body=None, headers=None, raw=None):
        data = raw if raw is not None else (b'' if body is None else json.dumps(body).encode())
        self.send_response(status)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n) or b'{}') if n else {}

    def user(self):
        tok = (self.headers.get('Authorization') or '').replace('Bearer ', '')
        return tok, S['sessions'].get(tok)

    def do_GET(self):
        getattr(self, f'get_{KIND}')()

    def do_POST(self):
        getattr(self, f'post_{KIND}')()

    def do_DELETE(self):
        getattr(self, f'delete_{KIND}')()

    # ---------------- SUT-01
    def post_sut01(self):
        b, p = self.body(), self.path
        if p == '/api/auth/login':
            if b.get('password') != 'pizza123' or b.get('username') not in BEHAVIOR:
                return self.reply(401, {'error': 'Invalid username or password', 'status_code': 0, 'timestamp': 'x'})
            if BEHAVIOR[b['username']] == 'locked_out':
                return self.reply(403, {'error': ex.LOCKOUT_DETAIL, 'status_code': 0, 'timestamp': 'x'})
            S['logins'] += 1
            tok = f'{JWT_HEAD}hbGciOi.{JWT_HEAD}{b["username"]}{S["logins"]}.sig{S["logins"]}abc'
            S['sessions'][tok] = {'username': b['username'], 'behavior': BEHAVIOR[b['username']], 'cart': []}
            return self.reply(200, {'access_token': tok, 'username': b['username'], 'behavior': BEHAVIOR[b['username']]})
        tok, u = self.user()
        if u is None:
            return self.reply(401, {'error': 'Could not validate credentials', 'status_code': 0, 'timestamp': 'x'})
        if p == '/api/cart':
            u['cart'] = [dict(i) for i in b['items']]
            return self.reply(200, {'ok': True})
        if p == '/api/session/reset':
            u['cart'] = []
            return self.reply(200, {'ok': True})
        if p == '/api/checkout':
            S['checkouts'] += 1
            if u['behavior'] == 'error' and S['checkouts'] % 2 == 1:
                return self.reply(500, {'error': ex.ERROR_USER_DETAIL, 'status_code': 0, 'timestamp': 'x'})
            order = ex.expected_order(b['items'], float(b.get('propina') or 0.0))
            return self.reply(200, {**order, 'order_id': f'ORDER-{S["checkouts"]:04d}', 'status': 'confirmed', 'timestamp': 'x', 'currency_symbol': '$'})
        self.reply(404, {'error': 'not found', 'status_code': 0, 'timestamp': 'x'})

    def get_sut01(self):
        if self.path == '/health':
            return self.reply(200, {'ok': True})
        tok, u = self.user()
        if u is None:
            return self.reply(401, {'error': 'Could not validate credentials', 'status_code': 0, 'timestamp': 'x'})
        if self.path == '/api/session':
            return self.reply(200, {'cart_items': u['cart'], 'country_code': 'MX'})
        if self.path == '/api/pizzas':
            S['catalog_calls'] += 1
            if u['behavior'] == 'a11y_glitch':
                return self.reply(200, a11y_catalog(S['catalog_calls']))
            return self.reply(200, {'pizzas': ex.expected_catalog(DATA), 'country_code': 'MX', 'currency': 'MXN'})
        if self.path == '/health':
            return self.reply(200, {'ok': True})
        self.reply(404, {'error': 'not found', 'status_code': 0, 'timestamp': 'x'})

    # ---------------- SUT-05
    def post_sut05(self):
        b, p = self.body(), self.path
        if p == '/rest/user/login':
            if b.get('password') != 'Mr. N00dles':
                return self.reply(401, raw=b'Invalid email or password.')
            S['logins'] += 1
            bid = S['logins']
            S['baskets'][bid] = []
            return self.reply(200, {'authentication': {'token': f'{JWT_HEAD}hbGciOi.{JWT_HEAD}{bid}abcd.sig{bid}', 'bid': bid, 'umail': b['email']}})
        if p == '/api/BasketItems':
            S['baskets'].setdefault(b['BasketId'], []).append(b['ProductId'])
            return self.reply(200, {'status': 'success'})
        self.reply(404)

    def get_sut05(self):
        if self.path.startswith('/rest/basket/'):
            bid = int(self.path.rsplit('/', 1)[1])
            if bid not in S['baskets']:
                return self.reply(401, {'error': 'Invalid token'})
            return self.reply(200, {'status': 'success', 'data': {'id': bid, 'Products': [{'id': i} for i in S['baskets'][bid]]}})
        if self.path == '/rest/captcha':
            S['captchas'] += 1
            return self.reply(200, {'captchaId': S['captchas'], 'captcha': '1+2', 'answer': '3'})
        if self.path == '/rest/admin/application-version':
            return self.reply(200, {'version': 'fake'})
        self.reply(404)

    # ---------------- SUT-04 (auth, booking and message services on one port)
    def post_sut04(self):
        b, p = self.body(), self.path
        if p == '/auth/login':
            return self.reply(200, {}, {'Set-Cookie': 'to' + 'ken=Tk4Secret1234; Path=/'})
        if p.startswith('/booking/'):
            d = b['bookingdates']
            for k in S['bookings']:
                if k['roomid'] == b['roomid'] and not (d['checkout'] <= k['bookingdates']['checkin'] or d['checkin'] >= k['bookingdates']['checkout']):
                    return self.reply(409)
            bid = S['next_id']
            S['next_id'] += 1
            S['bookings'].append({**b, 'bookingid': bid})
            if b.get('email') and b.get('phone') and not os.environ.get('FAKE_NO_MESSAGE'):
                S['messages'] += 1
            return self.reply(201, {'bookingid': bid, 'booking': b})
        self.reply(404)

    def get_sut04(self):
        if self.path.startswith('/booking/?roomid='):
            return self.reply(200, {'bookings': S['bookings']})
        if self.path.startswith('/booking/'):
            bid = int(self.path.rsplit('/', 1)[1])
            hit = [k for k in S['bookings'] if k['bookingid'] == bid]
            return self.reply(200, hit[0]) if hit else self.reply(404)
        if self.path == '/message/count':
            return self.reply(200, {'count': S['messages']})
        if self.path == '/booking/actuator/health':
            return self.reply(200, {'status': 'UP'})
        self.reply(404)

    def delete_sut04(self):
        mode = os.environ.get('FAKE_DELETE_MODE')
        bid = int(self.path.rsplit('/', 1)[1])
        if mode == 'fail':
            return self.reply(500)
        if mode != 'noop':
            S['bookings'] = [k for k in S['bookings'] if k['bookingid'] != bid]
        self.reply(202)


if __name__ == '__main__':
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
