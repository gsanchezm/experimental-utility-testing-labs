"""Unit tests of executor/classify.py: categories, reasons, attribution, outcome status, and the non-arrival precedence (pure).

DRAFT (operation OP-PREP-E06-EXECUTOR). Every case of not_arrived_reason is covered once, and the precedence is checked where two signals
could both apply.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..')))

from executor import classify, config  # noqa: E402


def facts(**kw):
    base = {'sign_in_submitted': True, 'page_loaded': True, 'backend_observed': True, 'error_text': None, 'login_request_seen': False,
            'login_status': None, 'catalogue_seen': False, 'catalogue_status': None}
    base.update(kw)
    return base


class ReasonPrecedenceTests(unittest.TestCase):
    def test_user_limit_by_status_or_by_message(self):
        self.assertEqual(classify.not_arrived_reason(facts(login_status=429)), 'INFRA_USER_LIMIT_429')
        self.assertEqual(classify.not_arrived_reason(facts(error_text='Too many users', login_status=200)), 'INFRA_USER_LIMIT_429')

    def test_user_limit_wins_over_a_refusal_message(self):
        self.assertEqual(classify.not_arrived_reason(facts(login_status=429, error_text='Invalid credentials')), 'INFRA_USER_LIMIT_429')

    def test_a_5xx_answer_is_infrastructure(self):
        self.assertEqual(classify.not_arrived_reason(facts(login_status=503)), 'INFRA_BACKEND_5XX')
        self.assertEqual(classify.not_arrived_reason(facts(login_status=200, catalogue_status=502)), 'INFRA_BACKEND_5XX')

    def test_an_unanswered_request_is_infrastructure_for_sign_in_and_for_catalogue(self):
        self.assertEqual(classify.not_arrived_reason(facts(login_request_seen=True)), 'INFRA_BACKEND_NO_RESPONSE')
        self.assertEqual(classify.not_arrived_reason(facts(login_status=200, catalogue_seen=True)), 'INFRA_BACKEND_NO_RESPONSE')

    def test_a_front_end_that_never_showed_the_sign_in_screen_is_infrastructure(self):
        self.assertEqual(classify.not_arrived_reason(facts(page_loaded=False, sign_in_submitted=False)), 'INFRA_BACKEND_NO_RESPONSE')

    def test_a_refusal_is_sut(self):
        self.assertEqual(classify.not_arrived_reason(facts(login_status=403)), 'SUT_SIGN_IN_REFUSED')
        self.assertEqual(classify.not_arrived_reason(facts(login_status=401)), 'SUT_SIGN_IN_REFUSED')
        self.assertEqual(classify.not_arrived_reason(facts(error_text='Sorry, this user has been locked out.', login_status=403)), 'SUT_SIGN_IN_REFUSED')

    def test_an_accepted_sign_in_with_a_catalogue_below_500_that_is_not_shown_is_sut(self):
        self.assertEqual(classify.not_arrived_reason(facts(login_status=200, catalogue_status=200)), 'SUT_CATALOGUE_NOT_REACHED_AFTER_SIGN_IN')
        self.assertEqual(classify.not_arrived_reason(facts(login_status=200, catalogue_status=404)), 'SUT_CATALOGUE_NOT_REACHED_AFTER_SIGN_IN')

    def test_a_sign_in_with_no_refusal_and_no_catalogue_is_a_timeout_of_infrastructure(self):
        self.assertEqual(classify.not_arrived_reason(facts(login_status=200)), 'INFRA_CATALOGUE_TIMEOUT')
        self.assertEqual(classify.not_arrived_reason(facts(login_status=None, backend_observed=False)), 'INFRA_CATALOGUE_TIMEOUT')

    def test_a_catalogue_without_the_second_signal_of_a_session_is_a_refusal_of_the_system(self):
        # SUT-02 Android (decision D-E06-13): the application showed the catalogue after the sign-in but not the drawer row Logout Menu Item
        self.assertEqual(classify.not_arrived_reason(facts(session_not_established=True, backend_observed=False)), 'SUT_SIGN_IN_REFUSED')
        self.assertEqual(classify.reason_category('SUT_SIGN_IN_REFUSED'), 'NOT_ARRIVED_SUT')

    def test_the_infrastructure_signals_win_over_a_missing_second_signal(self):
        self.assertEqual(classify.not_arrived_reason(facts(session_not_established=True, login_status=503)), 'INFRA_BACKEND_5XX')
        self.assertEqual(classify.not_arrived_reason(facts(session_not_established=True, error_text='Too many users')), 'INFRA_USER_LIMIT_429')

    def test_a_sign_in_that_was_never_submitted_is_a_runner_fault(self):
        self.assertEqual(classify.not_arrived_reason(facts(sign_in_submitted=False)), 'RUNNER_FAULT')


class ClassifyTests(unittest.TestCase):
    def test_an_identity_read_on_an_arrival(self):
        r = classify.classify(identity_oracle='item_identity', arrived=True, identity='p02')
        self.assertEqual((r['category'], r['outcome_status'], r['attribution'], r['arrived'], r['identity_read'], r['matches_expected']),
                         ('ARRIVED_IDENTITY_READ', 'SUCCESS', 'NONE', True, 'p02', True))

    def test_an_arrival_with_an_unreadable_identity_is_inconclusive_and_undetermined(self):
        r = classify.classify(identity_oracle='item_identity', arrived=True, identity=None)
        self.assertEqual((r['category'], r['reason'], r['outcome_status'], r['attribution'], r['matches_expected']),
                         ('ARRIVED_IDENTITY_UNREADABLE', 'IDENTITY_UNREADABLE', 'INCONCLUSIVE', 'UNDETERMINED', None))
        self.assertIsNone(r['identity_read'])

    def test_the_arrival_only_switch_records_arrival_and_never_an_identity(self):
        r = classify.classify(identity_oracle='arrival_only', arrived=True, identity='p02')
        self.assertEqual(r['category'], 'ARRIVED_ARRIVAL_ONLY')
        self.assertIsNone(r['identity_read'])
        self.assertEqual(r['outcome_status'], 'SUCCESS')

    def test_each_non_arrival_category_has_its_status_and_attribution(self):
        cases = [('INFRA_USER_LIMIT_429', 'NOT_ARRIVED_INFRASTRUCTURE', 'ABORTED', 'INFRASTRUCTURE', None),
                 ('SUT_SIGN_IN_REFUSED', 'NOT_ARRIVED_SUT', 'FAILURE', 'SUT', False),
                 ('RUNNER_FAULT', None, None, None, None)]
        for reason, category, status, attribution, matches in cases:
            if reason == 'RUNNER_FAULT':
                continue
            r = classify.classify(identity_oracle='item_identity', arrived=False, reason=reason)
            self.assertEqual((r['category'], r['outcome_status'], r['attribution'], r['matches_expected']), (category, status, attribution, matches))

    def test_a_runner_fault_overrides_everything(self):
        r = classify.classify(identity_oracle='item_identity', arrived=True, identity='p02', runner_fault='TimeoutError: boom')
        self.assertEqual((r['category'], r['reason'], r['attribution'], r['outcome_status']), ('NOT_ARRIVED_RUNNER', 'RUNNER_FAULT', 'TOOLING', 'ERROR'))

    def test_an_undeclared_reason_is_refused(self):
        with self.assertRaises(ValueError):
            classify.classify(identity_oracle='item_identity', arrived=False, reason='MADE_UP_REASON')

    def test_an_unknown_identity_oracle_is_refused(self):
        with self.assertRaises(ValueError):
            classify.classify(identity_oracle='visual', arrived=True, identity='p02')

    def test_every_category_of_the_vocabulary_has_a_status_and_an_attribution(self):
        self.assertEqual(set(classify.OUTCOME_STATUS), set(config.CATEGORIES))
        self.assertEqual(set(classify.ATTRIBUTION_OF), set(config.CATEGORIES))

    def test_the_manifest_outcome_carries_the_schema_enum_and_the_category(self):
        r = classify.classify(identity_oracle='item_identity', arrived=False, reason='SUT_SIGN_IN_REFUSED')
        m = classify.manifest_outcome('expected text', r)
        self.assertEqual(m['status'], 'FAILURE')
        self.assertEqual(m['outcome_category'], 'NOT_ARRIVED_SUT')
        self.assertEqual(m['observed'], 'NOT_ARRIVED_SUT: SUT_SIGN_IN_REFUSED')
        self.assertFalse(m['matches_expected'])


if __name__ == '__main__':
    unittest.main()
