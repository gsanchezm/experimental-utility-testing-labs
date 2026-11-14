"""The classifiers of the web realizations, on synthetic observations (no browser; operation OP-PREP-E05).

The first DRY_RUN showed the real observables; the classifiers read an observation dict only, so they are tested without a page."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

from executor import config, sut01, sut02, sut04  # noqa: E402


class Sut04WebClassify(unittest.TestCase):
    def label(self, **obs):
        base = {'post_status': None, 'confirmation_visible': False, 'form_remains': False, 'page_state': 'other'}
        return sut04.Web01.classify(None, None, {**base, **obs})[0]

    def test_categories(self):
        self.assertEqual(self.label(confirmation_visible=True, post_status=201), 'S_BOOKING_CONFIRMED')
        self.assertEqual(self.label(post_status=409, page_state='error_page'), 'S_NO_CONFIRMATION_SHOWN')
        self.assertEqual(self.label(post_status=409, form_remains=True, page_state='form_remains'), 'S_NO_CONFIRMATION_SHOWN')
        self.assertEqual(self.label(post_status=None), 'S_OTHER')
        self.assertEqual(self.label(post_status=500), 'S_OTHER')

    def test_every_label_is_declared_for_the_condition(self):
        cfg = config.load()
        c = config.condition(cfg, 'E05-SUT04-WEB-01')
        self.assertEqual(c['expected_category'], 'S_NO_CONFIRMATION_SHOWN')
        for obs in ({'confirmation_visible': True}, {'post_status': 409}, {}):
            self.assertIn(self.label(**obs), c['stimulus_categories'])


class Sut02WebClassify(unittest.TestCase):
    def label(self, badge):
        return sut02.Web01.classify(None, None, {'badge_text': badge, 'badge_count': 0 if badge is None else 1, 'clicked_control': 'add-to-cart-x'})[0]

    def test_categories(self):
        self.assertEqual(self.label('2'), 'S_BADGE_2')
        self.assertEqual(self.label('1'), 'S_NO_CHANGE')
        self.assertEqual(self.label('3'), 'S_BADGE_OTHER')
        self.assertEqual(self.label(None), 'S_BADGE_OTHER')


class Sut01WebClassify(unittest.TestCase):
    def label(self, **obs):
        base = {'order_success_route': False, 'modal_shown': True, 'invalid_fields': 0, 'post_status': None, 'url': 'http://x/checkout'}
        return sut01.Web01.classify(None, None, {**base, **obs})[0]

    def test_categories(self):
        self.assertEqual(self.label(order_success_route=True, post_status=200), 'S_ORDER_CONFIRMED')
        self.assertEqual(self.label(modal_shown=False, invalid_fields=2), 'S_VALIDATION_MESSAGE')
        self.assertEqual(self.label(post_status=500), 'S_HTTP_ERROR_VISIBLE')
        self.assertEqual(self.label(), 'S_OTHER_VIEW')


class Sut01ApiErrorBody(unittest.TestCase):
    def test_lockout_message_is_read_from_the_error_key(self):
        a3 = sut01.Api03
        ok = {'status': 403, 'error': None, 'detail': 'Sorry, this user has been locked out.'}
        self.assertEqual(a3.classify(None, None, ok)[0], 'S_LOCKOUT_403_EXACT_MESSAGE')
        self.assertEqual(a3.classify(None, None, {**ok, 'detail': None})[0], 'S_OTHER_STATUS_OR_BODY')
        self.assertEqual(a3.classify(None, None, {**ok, 'status': 401})[0], 'S_OTHER_STATUS_OR_BODY')


if __name__ == '__main__':
    unittest.main()
