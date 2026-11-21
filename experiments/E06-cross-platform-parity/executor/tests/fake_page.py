"""A fake page for the web flows of executor/web.py: it answers the page interface from a scripted state, with no browser.

DRAFT (operation OP-PREP-E06-EXECUTOR). The fake reads the JavaScript text it is given by its substrings (the expressions of web.py are
fixed strings), records every fill and click, and appends the network events of the scripted answer to the list the flow reads.
Virtual time: wait_for_timeout advances a counter and never sleeps.
"""

PNG = b'\x89PNG\r\n\x1a\n-fake-'


class FakePage:
    def __init__(self, net, *, sut='SUT-01', loaded=True, outcome='ok', testids=None, titles=None, error_text=None,
                 login_status=200, catalogue_status=200, catalogue_visible=True):
        self.net = net
        self.sut = sut
        self.loaded = loaded
        self.outcome = outcome            # 'ok' | 'user_limit' | 'refused' | 'no_response' | 'server_error' | 'no_catalogue' | 'error_text'
        self.testids = list(testids or [])
        self.titles = list(titles or [])
        self.error_text = error_text
        self.login_status = login_status
        self.catalogue_status = catalogue_status
        self.catalogue_visible = catalogue_visible
        self.calls = []
        self.virtual_ms = 0
        self.screen = 'login' if loaded else None
        self.signed_in = False
        self.on_inventory = False

    # the page interface of web.py
    def goto(self, url):
        self.calls.append(('goto', url))
        return 200

    def click(self, selector):
        self.calls.append(('click', selector))
        if selector.startswith('[data-testid="login-button') or selector == '#login-button':
            self._submit()

    def fill(self, selector, value):
        self.calls.append(('fill', selector, value))

    def evaluate(self, expression):
        if 'pizza-name-' in expression and 'map' in expression:
            return list(self.testids) if self.signed_in and self.catalogue_visible else []
        if 'inventory-item-name' in expression and 'map' in expression:
            return list(self.titles) if self.on_inventory else []
        if 'login-error' in expression:
            return self.error_text if self.screen == 'login' and self.error_text else None
        if 'data-test="error"' in expression:
            return self.error_text if self.sut == 'SUT-02' and self.error_text else None
        if 'screen-catalog' in expression:
            return self.signed_in and self.catalogue_visible
        if 'inventory.html' in expression:
            return self.on_inventory
        if 'screen-login' in expression:
            return bool(self.loaded)
        if '#user-name' in expression:
            return bool(self.loaded)
        if 'inventory-item-name' in expression:
            return bool(self.titles) and self.on_inventory
        if 'pizza-name-' in expression:
            return bool(self.testids) and self.signed_in
        raise AssertionError(f'the fake page has no answer for the expression: {expression[:80]}')

    def wait_for_timeout(self, ms):
        self.virtual_ms += ms

    def settle(self):
        return {'network_quiet': True, 'elapsed_s': 0.0}

    def content(self):
        return '<html><body>fake dom</body></html>'

    def screenshot(self):
        return PNG

    # the scripted sign-in answer
    def _submit(self):
        login_url = '/api/auth/login' if self.sut == 'SUT-01' else None
        if login_url:
            self.net.append({'event': 'request', 'url': 'https://fake.invalid' + login_url, 'method': 'POST'})
        if self.outcome == 'no_response':
            return
        if self.outcome == 'user_limit':
            self._answer(login_url, 429)
            self.screen, self.error_text = 'login', 'Too many users'
            return
        if self.outcome == 'server_error':
            self._answer(login_url, 503)
            self.screen, self.error_text = 'login', None
            return
        if self.outcome == 'refused':
            self._answer(login_url, 403)
            self.screen = 'login'
            self.error_text = self.error_text or ('Sorry, this user has been locked out.' if self.sut == 'SUT-01' else 'Epic sadface: Sorry, this user has been locked out.')
            return
        if self.outcome == 'error_text':
            self._answer(login_url, 200)
            self.screen, self.error_text = 'login', self.error_text or 'Something went wrong'
            return
        # ok, or no_catalogue (accepted, catalogue not shown)
        self._answer(login_url, self.login_status)
        self.error_text = None
        self.signed_in = True
        if self.sut == 'SUT-01':
            self.screen = 'catalog' if self.catalogue_visible else 'login-loading'
            self.net.append({'event': 'request', 'url': 'https://fake.invalid/api/pizzas', 'method': 'GET'})
            self.net.append({'event': 'response', 'url': 'https://fake.invalid/api/pizzas', 'status': self.catalogue_status, 'method': 'GET'})
        else:
            self.on_inventory = True

    def _answer(self, url, status):
        if url is None:
            return
        self.net.append({'event': 'response', 'url': 'https://fake.invalid' + url, 'status': status, 'method': 'POST'})
