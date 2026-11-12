"""Unit tests of the probe decisions (executor/probe.py, summarize and the rule readers). No browser, no SUT, no scanner.

DRAFT (operation OP-PREP-E09). The browser part of the probe is exercised only by the environment verification on GitHub Actions.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

from executor import probe  # noqa: E402


def load(i, dom, **kw):
    base = {'load': i, 'dom_state': dom, 'catalog_requests': 1, 'draw_consistency': 'SINGLE_DRAW',
            'corroboration': 'AGREES', 'explicit_matches': 0}
    base.update(kw)
    return base


GOOD_EMPTY = dict(explicit_matches=12, pair_empty_heading_matches=12, image_alt_violation_nodes=0, default_matches=12,
                  default_empty_heading_reported=True, target_test_ids=['pizza-name-1-desktop'])


def results(checks):
    return {name.split(':', 1)[1].strip(): res for name, res, _ in checks}


class SummarizeTests(unittest.TestCase):
    def test_all_pass_after_two_other_draws_and_one_empty_draw(self):
        checks = probe.summarize([load(1, 'NOT_EMPTY'), load(2, 'NOT_EMPTY'), load(3, 'ALL_EMPTY', **GOOD_EMPTY)])
        self.assertEqual({r for _, r, _ in checks}, {'PASS'})
        self.assertEqual(len(checks), 6)

    def test_first_load_empty_skips_the_check_of_other_draws(self):
        checks = probe.summarize([load(1, 'ALL_EMPTY', **GOOD_EMPTY)])
        self.assertEqual({r for _, r, _ in checks}, {'PASS'})
        self.assertEqual(len(checks), 5)
        self.assertFalse(any('not ALL_EMPTY' in name for name, _, _ in checks))

    def test_no_empty_draw_is_not_verified_and_the_dependent_checks_are_not_verified(self):
        checks = probe.summarize([load(i, 'NOT_EMPTY') for i in range(1, 31)])
        res = results(checks)
        self.assertEqual(res[next(k for k in res if k.startswith('realized draws'))], 'NOT_VERIFIED')
        self.assertEqual(sum(1 for r in res.values() if r == 'NOT_VERIFIED'), 4)
        self.assertNotIn('FAIL', res.values())

    def test_a_second_catalog_request_in_one_load_fails_the_single_fetch_check(self):
        checks = probe.summarize([load(1, 'NOT_EMPTY', catalog_requests=2, draw_consistency='MULTIPLE_DRAWS'), load(2, 'ALL_EMPTY', **GOOD_EMPTY)])
        self.assertEqual(results(checks)['one GET of the catalog API per page load, one draw per load'], 'FAIL')

    def test_image_alt_reporting_a_node_fails_that_check_only(self):
        bad = dict(GOOD_EMPTY, image_alt_violation_nodes=3)
        checks = probe.summarize([load(1, 'ALL_EMPTY', **bad)])
        res = results(checks)
        self.assertEqual(res['image-alt (explicit pair of rules) reports no node at an ALL_EMPTY draw'], 'FAIL')
        self.assertEqual(sum(1 for r in res.values() if r == 'FAIL'), 1)

    def test_empty_heading_not_reported_at_an_empty_draw_fails(self):
        bad = dict(GOOD_EMPTY, explicit_matches=0, pair_empty_heading_matches=0, default_matches=0, default_empty_heading_reported=True)
        res = results(probe.summarize([load(1, 'ALL_EMPTY', **bad)]))
        self.assertEqual(res['empty-heading (explicit rule set) reports the affected h2 at an ALL_EMPTY draw'], 'FAIL')
        self.assertEqual(res['the default rule set reports empty-heading for the affected h2 at an ALL_EMPTY draw'], 'FAIL')

    def test_a_matching_node_at_a_draw_that_is_not_empty_fails(self):
        res = results(probe.summarize([load(1, 'NOT_EMPTY', explicit_matches=1), load(2, 'ALL_EMPTY', **GOOD_EMPTY)]))
        self.assertEqual(res['no matching node of empty-heading at a draw that is not ALL_EMPTY'], 'FAIL')


class RuleReaderTests(unittest.TestCase):
    RESULT = {'violations': [{'id': 'empty-heading', 'nodes': [{}, {}]}, {'id': 'image-alt', 'nodes': [{}]}],
              'passes': [{'id': 'x', 'nodes': []}], 'incomplete': [], 'inapplicable': [{'id': 'y'}]}

    def test_rule_reported_looks_in_all_four_lists(self):
        self.assertTrue(probe.rule_reported(self.RESULT, 'empty-heading'))
        self.assertTrue(probe.rule_reported(self.RESULT, 'x'))
        self.assertTrue(probe.rule_reported(self.RESULT, 'y'))
        self.assertFalse(probe.rule_reported(self.RESULT, 'z'))
        self.assertFalse(probe.rule_reported(None, 'z'))

    def test_rule_violation_nodes_counts_only_violations(self):
        self.assertEqual(probe.rule_violation_nodes(self.RESULT, 'empty-heading'), 2)
        self.assertEqual(probe.rule_violation_nodes(self.RESULT, 'x'), 0)
        self.assertEqual(probe.rule_violation_nodes({}, 'x'), 0)

    def test_the_explicit_pair_names_both_rules(self):
        self.assertEqual(probe.EXPLICIT_PAIR_OPTIONS['runOnly']['values'], ['empty-heading', 'image-alt'])


if __name__ == '__main__':
    unittest.main()
