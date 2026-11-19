"""The web legs of the executor (Sut01Ui in executor/sut01.py, Sut04Ui in executor/sut04.py) against a recording stand-in for the browser
(operation OP-PREP-E07-04). No Playwright is installed in the static tests: the stand-in implements only the calls the web legs make, and records them, so that
the order of the interactions, the selectors, the data the methods return and the read-only property of the reads are checked. It does not prove that
the selectors exist on the pages: that is verified by the non-measured DRY_RUN rounds on GitHub Actions."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import common, sut01, sut04, web  # noqa: E402
from test_attempt import C5_S1, C5_S4, make_job  # noqa: E402


class Locator:
    def __init__(self, page, selector, text=None):
        self.page, self.selector, self.text = page, selector, text

    @property
    def first(self):
        return self

    def click(self, **kw):
        self.page.log.append(('click', self.selector))

    def fill(self, value):
        self.page.log.append(('fill', self.selector, value))

    def count(self):
        return self.page.present.get(self.selector, 0)

    def inner_text(self, timeout=None):
        return self.page.texts.get(self.selector)

    def all_inner_texts(self):
        return self.page.rows if self.selector == 'div.detail.booking-1' else []


class Page:
    def __init__(self):
        self.log, self.storage, self.present, self.texts, self.rows, self.order_ids = [], {}, {}, {}, [], []

    def locator(self, selector):
        return Locator(self, selector)

    def get_by_role(self, role, name=None):
        return Locator(self, f'role={role}[{name}]')

    def get_by_text(self, text):
        return Locator(self, f'text={text}')

    def evaluate(self, script, arg=None):
        if script.startswith('(k) => window.localStorage.getItem'):
            return self.storage.get(arg)
        if script.startswith('(seed) =>'):
            self.storage.update({k: v for k, v in arg.items()})
            self.log.append(('seed', sorted(arg)))
            return None
        if script == sut01.ORDER_LINES:
            return list(self.order_ids)
        raise AssertionError(f'unexpected script {script!r}')

    def wait_for_url(self, pattern, timeout=None):
        self.log.append(('wait_for_url', pattern))


class Context:
    def __init__(self, cookies):
        self._cookies = cookies

    def cookies(self):
        return self._cookies


class Browser:
    """Stand-in for web.Browser."""
    status, visible_selectors, cookies = {}, set(), []

    def __init__(self, job):
        self.page, self.context, self.urls, self.bound = Page(), Context(list(type(self).cookies)), [], 0

    def bind(self, run):
        self.bound += 1

    def goto(self, url):
        self.urls.append(url)
        return type(self).status.get(url.split('//', 1)[-1].split('/', 1)[-1], 200)

    def visible(self, locator, timeout_ms=None):
        return locator.selector in type(self).visible_selectors

    def settle(self):
        return {'network_quiet': True}

    def flush(self):
        pass

    def close(self):
        pass


class UiCase(unittest.TestCase):
    def setUp(self):
        self.original = web.Browser
        web.Browser = Browser
        Browser.status, Browser.visible_selectors, Browser.cookies = {}, set(), []
        self.addCleanup(setattr, web, 'Browser', self.original)


class Sut01UiTests(UiCase):
    def ui(self):
        job = make_job(C5_S1, 1, 1)
        ui = sut01.Sut01Ui(job)
        run = common.Run(job, 1)
        self.addCleanup(run.close)
        ui.bind(run)
        return ui, ui.b.page

    def test_inject_session_loads_the_site_then_writes_the_client_state_once_with_an_empty_cart(self):
        ui, page = self.ui()
        obs, status = ui.inject_session('TOKEN-VALUE-1234', {'username': 'standard_user', 'behavior': 'standard'})
        self.assertEqual(status, 200)
        self.assertTrue(ui.b.urls[0].endswith(':%s/' % ui.site.rsplit(':', 1)[1]) or ui.b.urls[0].rstrip('/') == ui.site)
        self.assertEqual([e[0] for e in page.log], ['seed'])
        self.assertEqual(json.loads(page.storage['omnipizza-cart']), {'state': {'items': []}, 'version': 0})
        self.assertEqual(ui.client_cart(), [])
        self.assertEqual(ui.client_token(), 'TOKEN-VALUE-1234')
        self.assertEqual(obs['keys_injected'], sorted(page.storage))

    def test_client_cart_and_token_are_none_when_they_cannot_be_read(self):
        ui, page = self.ui()
        self.assertIsNone(ui.client_cart())
        self.assertIsNone(ui.client_token())
        page.storage['omnipizza-cart'] = '{not json'
        self.assertIsNone(ui.client_cart())

    def test_add_through_ui_clicks_the_desktop_add_control_then_the_confirm_control(self):
        ui, page = self.ui()
        Browser.visible_selectors = {'[data-testid="screen-catalog"]', '[data-testid="add-to-cart-p02-desktop"]', '[data-testid="confirm-add-to-cart"]'}
        obs = ui.add_through_ui('p02')
        self.assertEqual([e for e in page.log if e[0] == 'click'], [('click', '[data-testid="add-to-cart-p02-desktop"]'), ('click', '[data-testid="confirm-add-to-cart"]')])
        self.assertTrue(obs['confirmed'])
        self.assertTrue(ui.b.urls[0].endswith('/catalog'))

    def test_add_through_ui_stops_where_a_control_is_not_shown(self):
        ui, page = self.ui()
        Browser.visible_selectors = {'[data-testid="screen-catalog"]'}
        obs = ui.add_through_ui('p02')
        self.assertNotIn('confirmed', obs)
        self.assertEqual(page.log, [])
        Browser.visible_selectors = {'[data-testid="screen-catalog"]', '[data-testid="add-to-cart-p02-desktop"]'}
        obs = ui.add_through_ui('p02')
        self.assertNotIn('confirmed', obs)
        self.assertEqual(len(page.log), 1)

    def test_checkout_lines_reads_the_order_lines_and_their_details_without_clicking(self):
        ui, page = self.ui()
        page.order_ids = ['order-item-p02']
        page.present['[data-testid="order-item-details-p02"]'] = 1
        page.texts['[data-testid="order-item-details-p02"]'] = '1x • Small'
        self.assertEqual(ui.checkout_lines(), [{'pizza_id': 'p02', 'details': '1x • Small'}])
        self.assertEqual(page.log, [])
        self.assertEqual(ui.open_checkout(), 200)
        self.assertTrue(ui.b.urls[-1].endswith('/checkout'))

    def test_a_line_without_details_is_reported_without_a_quantity(self):
        ui, page = self.ui()
        page.order_ids = ['order-item-p02']
        self.assertEqual(ui.checkout_lines(), [{'pizza_id': 'p02', 'details': None}])
        self.assertIsNone(sut01.QUANTITY.match(''))

    def test_the_order_line_filter_keeps_only_the_line_test_ids(self):
        # the filter of the E03 module sut01_web.py, applied in the browser: a test id with a second dash group is not a line
        import re
        pattern = re.compile(r'^order-item-[A-Za-z0-9]+$')
        self.assertTrue(pattern.match('order-item-p02'))
        for other in ('order-item-details-p02', 'order-item-image-p02', 'order-item-name-p02', 'order-item-edit-p02', 'order-item-remove-p02'):
            self.assertFalse(pattern.match(other), other)
        self.assertEqual(sut01.QUANTITY.match('3x • Small').group(1), '3')


class Sut04UiTests(UiCase):
    def ui(self):
        job = make_job(C5_S4, 1, 1)
        ui = sut04.Sut04Ui(job)
        run = common.Run(job, 1)
        self.addCleanup(run.close)
        ui.bind(run)
        return ui, ui.b.page, sut04.unique(C5_S4, run.run_id)

    def test_admin_login_fills_the_form_and_returns_the_token_cookie(self):
        ui, page, _ = self.ui()
        page.present['#username'] = 1
        Browser.cookies = []
        ui.b.context._cookies = [{'name': 'token', 'value': 'COOKIE-VALUE-1234'}]
        status, token = ui.admin_login()
        self.assertEqual((status, token), (200, 'COOKIE-VALUE-1234'))
        self.assertEqual([e for e in page.log if e[0] in ('fill', 'click')],
                         [('fill', '#username', 'admin'), ('fill', '#password', 'password'), ('click', '#doLogin')])
        self.assertEqual(ui.b.urls, [ui.site + '/admin'])

    def test_a_session_that_is_already_logged_in_is_not_logged_in_again(self):
        ui, page, _ = self.ui()
        ui.b.context._cookies = [{'name': 'token', 'value': 'COOKIE-VALUE-1234'}]
        ui.admin_login()
        self.assertEqual(page.log, [])

    def test_submit_reservation_goes_to_the_reservation_route_and_fills_the_form_in_order(self):
        ui, page, u = self.ui()
        out = ui.submit_reservation(u)
        self.assertEqual(out, {'status': 200, 'submitted': True})
        self.assertEqual(ui.b.urls, [f"{ui.site}/reservation/1?checkin={u['checkin']}&checkout={u['checkout']}"])
        self.assertEqual(page.log, [('click', '#doReservation'), ('fill', '.room-firstname', u['firstname']), ('fill', '.room-lastname', u['lastname']),
                                    ('fill', '.room-email', u['email']), ('fill', '.room-phone', u['phone']), ('click', 'role=button[Reserve Now]')])

    def test_a_reservation_page_that_does_not_answer_200_submits_nothing(self):
        ui, page, u = self.ui()
        Browser.status = {f"reservation/1?checkin={u['checkin']}&checkout={u['checkout']}": 404}
        self.assertEqual(ui.submit_reservation(u), {'status': 404, 'submitted': False})
        self.assertEqual(page.log, [])

    def test_the_confirmation_and_the_admin_rows_are_read_without_clicking(self):
        ui, page, _ = self.ui()
        self.assertFalse(ui.confirmation_visible())
        Browser.visible_selectors = {'text=Booking Confirmed'}
        self.assertTrue(ui.confirmation_visible())
        page.rows = ['Ealpha Rbeta 2031-01-01']
        self.assertEqual(ui.admin_room_rows(), (200, ['Ealpha Rbeta 2031-01-01']))
        self.assertEqual(page.log, [])
        self.assertTrue(ui.b.urls[-1].endswith('/admin/room/1'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
