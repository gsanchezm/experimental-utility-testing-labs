"""Fake systems under test for the static tests of the E11 executor (operation OP-PREP-E11). Not a SUT, never part of a run.

python3 -I fake_sut.py <sut01|sut05> <port>. State is in memory, so a restart of the process (as the executor does at the start of every
execution) clears it, like the real instances. Environment switches: FAKE_SOLVED_AT_START=1 (every challenge starts solved: a reset that did
not hold), FAKE_NO_FLIP=1 (no request flips a challenge: an oracle that never moves), FAKE_ORACLE_500=1 (GET /api/Challenges answers 500),
FAKE_IDOR_FIXED=1 (SUT-01 enforces the ownership check for every user), FAKE_DELAYED_FLIP=1 (the union challenge flips 1 s after the response)."""
import http.server
import json
import os
import sys
import threading
import urllib.parse

KIND, PORT = sys.argv[1], int(sys.argv[2])
JWT_HEAD = 'ey' + 'J'  # built by concatenation: the export builder fails closed on a literal token-like prefix in a file
SOLVED0 = os.environ.get('FAKE_SOLVED_AT_START') == '1'
S = {'logins': 0, 'sessions': {}, 'orders': {}, 'next_order': 1,
     'challenges': {k: SOLVED0 for k in ('loginAdminChallenge', 'unionSqlInjectionChallenge', 'directoryListingChallenge', 'loginRapperChallenge')}}
BEHAVIOR = {'standard_user': 'standard', 'performance_glitch_user': 'performance_glitch', 'security_glitch_user': 'security_glitch',
            'locked_out_user': 'locked_out'}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, status, body=None, raw=None, ctype='application/json'):
        data = raw if raw is not None else (b'' if body is None else json.dumps(body).encode())
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n) or b'{}') if n else {}

    def flip(self, key):
        if os.environ.get('FAKE_NO_FLIP') == '1':
            return
        if os.environ.get('FAKE_DELAYED_FLIP') == '1' and key == 'unionSqlInjectionChallenge':
            threading.Timer(1.0, lambda: S['challenges'].__setitem__(key, True)).start()  # the real flag is written after the response
            return
        S['challenges'][key] = True

    def do_GET(self):
        getattr(self, f'get_{KIND}')()

    def do_POST(self):
        getattr(self, f'post_{KIND}')()

    # ---------------- SUT-05
    def post_sut05(self):
        b, p = self.body(), self.path
        if p == '/rest/user/login':
            email = b.get('email') or ''
            if "'" in email and '--' in email:
                self.flip('loginAdminChallenge')
                return self.reply(200, {'authentication': {'token': f'{JWT_HEAD}hbGciOi.{JWT_HEAD}admin.sig', 'bid': 1, 'umail': 'admin'}})
            if email == 'mc.safesearch@juice-sh.op' and b.get('password') == 'Mr. N00dles':
                self.flip('loginRapperChallenge')
                return self.reply(200, {'authentication': {'token': f'{JWT_HEAD}hbGciOi.{JWT_HEAD}rapper.sig', 'bid': 2, 'umail': email}})
            return self.reply(401, raw=b'Invalid email or password.', ctype='text/plain')
        if p == '/api/Users':
            return self.reply(201, {'status': 'success', 'data': {'id': 99}})
        self.reply(404, {'error': 'not found'})

    def get_sut05(self):
        u = urllib.parse.urlsplit(self.path)
        p, q = u.path, urllib.parse.parse_qs(u.query)
        if p == '/rest/admin/application-version':
            return self.reply(200, {'version': '20.2.0'})
        if p == '/api/Challenges':
            if os.environ.get('FAKE_ORACLE_500') == '1':
                return self.reply(500, {'error': 'oracle unavailable'})
            return self.reply(200, {'status': 'success', 'data': [{'key': k, 'solved': v} for k, v in S['challenges'].items()]})
        if p == '/rest/products/search':
            term = (q.get('q') or [''])[0]
            if 'UNION SELECT' in term.upper():
                self.flip('unionSqlInjectionChallenge')
            return self.reply(200, {'status': 'success', 'data': []})
        if p == '/ftp/' or p == '/ftp':
            return self.reply(200, raw=b'<html><title>listing directory /ftp</title></html>', ctype='text/html')
        if p == '/ftp/acquisitions.md':
            self.flip('directoryListingChallenge')
            return self.reply(200, raw=b'# acquisitions', ctype='text/markdown')
        if p == '/ftp/legal.md':
            return self.reply(200, raw=b'# legal', ctype='text/markdown')
        if p == '/rest/user/security-question':
            return self.reply(200, {})
        if p == '/assets/':
            return self.reply(200, raw=b'<html></html>', ctype='text/html')
        self.reply(404, {'error': 'not found'})

    # ---------------- SUT-01
    def user(self):
        tok = (self.headers.get('Authorization') or '').replace('Bearer ', '')
        return S['sessions'].get(tok)

    def post_sut01(self):
        b, p = self.body(), self.path
        if p == '/api/auth/login':
            if b.get('password') != 'pizza123' or b.get('username') not in BEHAVIOR or BEHAVIOR[b['username']] == 'locked_out':
                return self.reply(401, {'error': 'Invalid username or password'})
            S['logins'] += 1
            tok = f'{JWT_HEAD}hbGciOi.{JWT_HEAD}{b["username"]}{S["logins"]}.sig{S["logins"]}abc'
            S['sessions'][tok] = {'username': b['username'], 'behavior': BEHAVIOR[b['username']], 'cart': []}
            return self.reply(200, {'access_token': tok, 'username': b['username'], 'behavior': BEHAVIOR[b['username']]})
        u = self.user()
        if u is None:
            return self.reply(401, {'error': 'Could not validate credentials'})
        if p == '/api/cart':
            u['cart'] = [dict(i) for i in b['items']]
            return self.reply(200, {'ok': True})
        if p == '/api/checkout':
            oid = f'ORDER-{S["next_order"]:04d}'
            S['next_order'] += 1
            S['orders'][oid] = {'username': u['username'], 'items': b['items']}
            return self.reply(200, {'order_id': oid, 'status': 'confirmed', 'total': 1.0})
        self.reply(404, {'error': 'not found'})

    def get_sut01(self):
        if self.path == '/health':
            return self.reply(200, {'ok': True})
        u = self.user()
        if u is None:
            return self.reply(401, {'error': 'Could not validate credentials'})
        if self.path.startswith('/api/orders/'):
            order = S['orders'].get(self.path.rsplit('/', 1)[1])
            if order is None:
                return self.reply(404, {'error': 'Order not found'})
            exempt = u['behavior'] == 'security_glitch' and os.environ.get('FAKE_IDOR_FIXED') != '1'
            if order['username'] != u['username'] and not exempt:
                return self.reply(403, {'error': 'Not authorized to view this order'})
            return self.reply(200, {'order_id': self.path.rsplit('/', 1)[1], 'username': order['username']})
        self.reply(404, {'error': 'not found'})


if __name__ == '__main__':
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
