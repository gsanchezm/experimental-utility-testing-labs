"""The web flows of executor/web.py against the fake page of tests/fake_page.py (no browser; virtual time).

DRAFT (operation OP-PREP-E06-EXECUTOR). Each test scripts one sign-in outcome and checks the selectors used, the facts returned, and the
reason that classify.not_arrived_reason gives for a non-arrival. The selectors are the ones of conditions-draft.json, which are not yet
verified against the hosted deployments (a DRY_RUN decides that).
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, EXEC)
sys.path.insert(0, HERE)

from executor import classify, web  # noqa: E402
from fake_page import FakePage  # noqa: E402

CREDS_01 = ('standard_user', 'pizza123')
CREDS_02 = ('standard_user', 'secret_sauce')


class Sut01WebFlowTests(unittest.TestCase):
    def run_flow(self, page_kwargs, width=1280, net=None):
        net = [] if net is None else net
        page = FakePage(net, sut='SUT-01', **page_kwargs)
        facts = web.sut01_web(page, net, CREDS_01, width)
        return page, facts

    def test_arrival_reads_the_first_pizza_id_with_the_desktop_suffix(self):
        page, facts = self.run_flow({'testids': ['pizza-name-p02-desktop', 'pizza-name-p05-desktop']})
        self.assertTrue(facts['arrived'])
        self.assertEqual(facts['identity'], 'p02')
        self.assertEqual(facts['identity_raw'], 'pizza-name-p02-desktop')
        self.assertEqual(facts['test_id_suffix'], '-desktop')
        self.assertEqual(facts['normalized_identifiers'], ['p02', 'p05'])
        # the sign-in went through the form, with the suffixed identifiers and the US market control; no token was injected
        selectors = [c[1] for c in page.calls if c[0] in ('click', 'fill')]
        self.assertIn('[data-testid="market-US"]', selectors)
        self.assertIn('[data-testid="username-desktop"]', selectors)
        self.assertIn('[data-testid="password-desktop"]', selectors)
        self.assertIn('[data-testid="login-button-desktop"]', selectors)
        self.assertFalse(any('localStorage' in str(c) for c in page.calls))

    def test_a_narrow_viewport_uses_the_responsive_suffix_and_the_identity_is_the_same(self):
        page, facts = self.run_flow({'testids': ['pizza-name-p02-responsive']}, width=700)
        self.assertEqual(facts['test_id_suffix'], '-responsive')
        self.assertEqual(facts['identity'], 'p02')
        self.assertIn('[data-testid="username-responsive"]', [c[1] for c in page.calls if c[0] == 'fill'])

    def test_user_limit_is_an_infrastructure_non_arrival(self):
        net = []
        _page, facts = self.run_flow({'outcome': 'user_limit'}, net=net)
        self.assertFalse(facts['arrived'])
        self.assertEqual(facts['login_status'], 429)
        self.assertEqual(classify.not_arrived_reason(facts), 'INFRA_USER_LIMIT_429')

    def test_a_refused_credential_is_a_sut_non_arrival(self):
        _page, facts = self.run_flow({'outcome': 'refused'})
        self.assertEqual(facts['error_text'], 'Sorry, this user has been locked out.')
        self.assertEqual(classify.not_arrived_reason(facts), 'SUT_SIGN_IN_REFUSED')

    def test_a_server_error_is_an_infrastructure_non_arrival(self):
        _page, facts = self.run_flow({'outcome': 'server_error'})
        self.assertEqual(facts['login_status'], 503)
        self.assertEqual(classify.not_arrived_reason(facts), 'INFRA_BACKEND_5XX')

    def test_a_sign_in_without_any_answer_is_an_infrastructure_non_arrival(self):
        _page, facts = self.run_flow({'outcome': 'no_response'})
        self.assertTrue(facts['login_request_seen'])
        self.assertIsNone(facts['login_status'])
        self.assertEqual(classify.not_arrived_reason(facts), 'INFRA_BACKEND_NO_RESPONSE')

    def test_an_accepted_sign_in_without_the_catalogue_is_a_sut_non_arrival(self):
        _page, facts = self.run_flow({'outcome': 'ok', 'catalogue_visible': False, 'testids': []})
        self.assertFalse(facts['arrived'])
        self.assertEqual(facts['login_status'], 200)
        self.assertEqual(facts['catalogue_status'], 200)
        self.assertEqual(classify.not_arrived_reason(facts), 'SUT_CATALOGUE_NOT_REACHED_AFTER_SIGN_IN')

    def test_a_page_that_never_shows_the_sign_in_screen_is_an_infrastructure_non_arrival(self):
        page, facts = self.run_flow({'loaded': False})
        self.assertFalse(facts['page_loaded'])
        self.assertFalse(facts['sign_in_submitted'])
        self.assertEqual(classify.not_arrived_reason(facts), 'INFRA_BACKEND_NO_RESPONSE')
        self.assertFalse(any(c[0] == 'click' for c in page.calls))

    def test_an_arrival_with_no_card_gives_an_unreadable_identity(self):
        _page, facts = self.run_flow({'testids': []})
        self.assertTrue(facts['arrived'])
        self.assertIsNone(facts['identity'])
        record = classify.classify(identity_oracle='item_identity', arrived=True, identity=facts['identity'])
        self.assertEqual(record['category'], 'ARRIVED_IDENTITY_UNREADABLE')


class Sut02WebFlowTests(unittest.TestCase):
    def test_arrival_reads_the_first_title_in_the_default_name_order(self):
        net = []
        page = FakePage(net, sut='SUT-02', titles=['Sauce Labs Backpack', 'Sauce Labs Bike Light'])
        facts = web.sut02_web(page, net, CREDS_02)
        self.assertTrue(facts['arrived'])
        self.assertEqual(facts['identity'], 'Sauce Labs Backpack')
        selectors = [c[1] for c in page.calls if c[0] in ('click', 'fill')]
        self.assertEqual(selectors, ['#user-name', '[data-test="password"]', '#login-button'])
        self.assertFalse(facts['backend_observed'])

    def test_a_locked_out_account_is_a_sut_non_arrival(self):
        net = []
        page = FakePage(net, sut='SUT-02', outcome='refused', titles=[])
        facts = web.sut02_web(page, net, ('locked_out_user', 'secret_sauce'))
        self.assertFalse(facts['arrived'])
        self.assertEqual(classify.not_arrived_reason(facts), 'SUT_SIGN_IN_REFUSED')

    def test_a_missing_title_gives_an_unreadable_identity(self):
        net = []
        page = FakePage(net, sut='SUT-02', titles=['   '])
        facts = web.sut02_web(page, net, CREDS_02)
        self.assertTrue(facts['arrived'])
        self.assertIsNone(facts['identity'])


class NetSummaryTests(unittest.TestCase):
    def test_request_seen_and_last_status(self):
        events = [{'event': 'request', 'url': 'https://x/api/auth/login'}, {'event': 'response', 'url': 'https://x/api/auth/login', 'status': 500},
                  {'event': 'response', 'url': 'https://x/api/auth/login', 'status': 200}]
        self.assertEqual(web.net_summary(events, '/api/auth/login'), (True, 200))

    def test_no_event_for_the_fragment(self):
        self.assertEqual(web.net_summary([{'event': 'response', 'url': 'https://x/other', 'status': 200}], '/api/auth/login'), (False, None))

    def test_failed_request_has_no_status(self):
        events = [{'event': 'request', 'url': 'https://x/api/pizzas'}, {'event': 'failed', 'url': 'https://x/api/pizzas'}]
        self.assertEqual(web.net_summary(events, '/api/pizzas'), (True, None))


if __name__ == '__main__':
    unittest.main()
