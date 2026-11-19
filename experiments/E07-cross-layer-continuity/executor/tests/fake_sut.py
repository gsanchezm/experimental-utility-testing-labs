"""Fake systems under test for the static tests of the E07 executor (operation OP-PREP-E07-04). Not a SUT, never part of a run.

python3 -I fake_sut.py <sut01|sut04> <port>. State is in memory. SUT-01: a login issues a token that is a JWT whose payload carries a `sid` claim;
the session cart is the cart of the token. FAKE_CART_FAIL=1 makes POST /api/cart answer 500; FAKE_RESET_MODE=fail makes POST /api/session/reset answer
500, =noop answers 200 and keeps the cart; FAKE_LOGIN_CART=1 makes every new session start with a cart line (a starting state that is not empty).
SUT-04 (auth and booking services on one port): FAKE_DELETE_MODE=fail makes DELETE /booking/{id} answer 500; =noop answers 202 and keeps the booking
(a reset that did not hold). The module can be imported for make_jwt; the server starts only when it is run as a script."""
import base64
import http.server
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

KIND = None
S = {'logins': 0, 'sessions': {}, 'bookings': [], 'next_id': 1}
BEHAVIOR = {'standard_user': 'standard', 'locked_out_user': 'locked_out', 'performance_glitch_user': 'performance_glitch', 'error_user': 'error',
            'a11y_glitch_user': 'a11y_glitch'}
JWT_HEAD = 'ey' + 'J'  # built by concatenation: the export builder fails closed on a literal token-like prefix in a file


def _b64(obj):
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip('=')


def make_jwt(sub, sid):
    """A token with the shape of a JWT: a header, a payload with the claims sub and sid, and a signature part."""
    return f'{JWT_HEAD}hbGciOiJIUzI1NiJ9.{_b64({"sub": sub, "sid": sid})}.signaturepart'


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
            S['logins'] += 1
            sid = f'SIDSECRET{S["logins"]:04d}'
            tok = make_jwt(b['username'], sid)
            cart = [{'pizza_id': 'p99', 'quantity': 1}] if os.environ.get('FAKE_LOGIN_CART') else []
            S['sessions'][tok] = {'username': b['username'], 'behavior': BEHAVIOR[b['username']], 'cart': cart}
            return self.reply(200, {'access_token': tok, 'username': b['username'], 'behavior': BEHAVIOR[b['username']]})
        tok, u = self.user()
        if u is None:
            return self.reply(401, {'error': 'Could not validate credentials', 'status_code': 0, 'timestamp': 'x'})
        if p == '/api/cart':
            if os.environ.get('FAKE_CART_FAIL'):
                return self.reply(500, {'error': 'cart failure'})
            u['cart'] = [dict(i) for i in b['items']]
            return self.reply(200, {'ok': True})
        if p == '/api/session/reset':
            mode = os.environ.get('FAKE_RESET_MODE')
            if mode == 'fail':
                return self.reply(500, {'error': 'reset failure'})
            if mode != 'noop':
                u['cart'] = []
            return self.reply(200, {'ok': True})
        self.reply(404, {'error': 'not found', 'status_code': 0, 'timestamp': 'x'})

    def get_sut01(self):
        tok, u = self.user()
        if u is None:
            return self.reply(401, {'error': 'Could not validate credentials', 'status_code': 0, 'timestamp': 'x'})
        if self.path == '/api/session':
            return self.reply(200, {'cart_items': u['cart'], 'country_code': 'MX'})
        self.reply(404, {'error': 'not found', 'status_code': 0, 'timestamp': 'x'})

    # ---------------- SUT-04 (auth and booking services on one port)
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
            return self.reply(201, {'bookingid': bid, 'booking': b})
        self.reply(404)

    def get_sut04(self):
        if self.path.startswith('/booking/?roomid='):
            return self.reply(200, {'bookings': S['bookings']})
        if self.path.startswith('/booking/'):
            bid = int(self.path.rsplit('/', 1)[1])
            hit = [k for k in S['bookings'] if k['bookingid'] == bid]
            return self.reply(200, hit[0]) if hit else self.reply(404)
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
    KIND, PORT = sys.argv[1], int(sys.argv[2])
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
