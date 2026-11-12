"""Unit tests of the ground-truth decision, the detection judgment, the corroboration, and the outcome mapping.

DRAFT (operation OP-PREP-E09). Inputs are synthetic DOM snapshots and synthetic axe-shaped results (fixtures/). No SUT is
contacted and no scanner is run. Run: python3 -m unittest -v (from the tests directory or with discovery).
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

from executor import classify  # noqa: E402
from dom_records import dom_records  # noqa: E402

FIX = os.path.join(HERE, 'fixtures')


def fixture(name):
    with open(os.path.join(FIX, name), encoding='utf-8') as f:
        return f.read()


def axe(name):
    with open(os.path.join(FIX, name), encoding='utf-8') as f:
        return json.load(f)


class DomStateTests(unittest.TestCase):
    def test_all_empty_is_ground_truth(self):
        state, detail = classify.dom_state(dom_records(fixture('dom-all-empty.html')))
        self.assertEqual(state, 'ALL_EMPTY')
        self.assertEqual(detail, {'count': 3, 'empty': 3})

    def test_whitespace_only_heading_counts_as_empty(self):
        records = dom_records(fixture('dom-all-empty.html'))
        self.assertEqual(records[1]['text'], '   ')
        self.assertEqual(classify.dom_state(records)[0], 'ALL_EMPTY')

    def test_not_empty_is_no_ground_truth(self):
        self.assertEqual(classify.dom_state(dom_records(fixture('dom-not-empty.html')))[0], 'NOT_EMPTY')

    def test_mixed_is_not_classifiable(self):
        self.assertEqual(classify.dom_state(dom_records(fixture('dom-mixed.html')))[0], 'MIXED')

    def test_empty_but_aria_named_cannot_fire_the_rule(self):
        state, detail = classify.dom_state(dom_records(fixture('dom-aria-named.html')))
        self.assertEqual(state, 'EMPTY_ARIA_NAMED')
        self.assertEqual(detail['aria_named'], 1)

    def test_no_cards_is_not_a_ground_truth_state(self):
        self.assertEqual(classify.dom_state(dom_records(fixture('dom-no-cards.html')))[0], 'NO_CARDS')

    def test_other_test_ids_are_not_product_headings(self):
        records = dom_records(fixture('dom-no-cards.html'))
        self.assertEqual(records, [])


class MatchingNodeTests(unittest.TestCase):
    def test_pizza_name_node_matches(self):
        self.assertEqual(len(classify.matching_nodes(axe('axe-result-detect.json'))), 1)

    def test_other_heading_and_other_rule_do_not_match(self):
        fx = axe('axe-result-no-match.json')
        self.assertEqual(classify.matching_nodes(fx), [])
        self.assertEqual(classify.rule_node_total(fx), 1)

    def test_empty_result_has_no_match(self):
        self.assertEqual(classify.matching_nodes(axe('axe-result-empty.json')), [])
        self.assertEqual(classify.rule_node_total(axe('axe-result-empty.json')), 0)

    def test_rule_must_be_violation_of_empty_heading(self):
        fx = {'violations': [{'id': 'image-alt', 'nodes': [{'html': '<h2 data-testid="pizza-name-p01">x</h2>'}]}]}
        self.assertEqual(classify.matching_nodes(fx), [])


class CorroborationTests(unittest.TestCase):
    def test_body_classes(self):
        self.assertEqual(classify.body_class(json.dumps([{'name': ''}, {'name': ' '}])), 'MISSING_NAME_BODY')
        self.assertEqual(classify.body_class(json.dumps([{'name': 'Margherita'}])), 'NON_EMPTY_NAMES')
        self.assertEqual(classify.body_class(json.dumps([{'name': ''}, {'name': 'x'}])), 'MIXED_NAMES')
        self.assertEqual(classify.body_class('not json'), 'UNPARSEABLE')
        self.assertEqual(classify.body_class(json.dumps({'name': 'x'})), 'UNPARSEABLE')
        self.assertEqual(classify.body_class(None), 'UNPARSEABLE')
        # The real shape of the catalog response (observed on GitHub Actions, run 43326329851): an object with a pizzas list.
        self.assertEqual(classify.body_class(json.dumps({'pizzas': [{'id': 'p01', 'name': ''}, {'id': 'p02', 'name': ''}]})), 'MISSING_NAME_BODY')
        self.assertEqual(classify.body_class(json.dumps({'pizzas': [{'id': 'p01', 'name': 'Margarita'}]})), 'NON_EMPTY_NAMES')
        self.assertEqual(classify.body_class(json.dumps({'pizzas': [{'name': ''}, {'name': 'x'}]})), 'MIXED_NAMES')
        self.assertEqual(classify.body_class(json.dumps({'pizzas': []})), 'UNPARSEABLE')
        self.assertEqual(classify.body_class(json.dumps({'pizzas': 'x'})), 'UNPARSEABLE')
        self.assertEqual(classify.corroboration('ALL_EMPTY', [classify.body_class(json.dumps({'pizzas': [{'name': ''}]}))]), 'AGREES')

    def test_corroboration_matrix(self):
        self.assertEqual(classify.corroboration('ALL_EMPTY', ['MISSING_NAME_BODY']), 'AGREES')
        self.assertEqual(classify.corroboration('NOT_EMPTY', ['NON_EMPTY_NAMES']), 'AGREES')
        self.assertEqual(classify.corroboration('ALL_EMPTY', ['NON_EMPTY_NAMES']), 'DISAGREES')
        self.assertEqual(classify.corroboration('ALL_EMPTY', []), 'NO_RESPONSE_CAPTURED')
        self.assertEqual(classify.corroboration('ALL_EMPTY', ['UNPARSEABLE']), 'NOT_INTERPRETABLE')

    def test_draw_consistency(self):
        self.assertEqual(classify.draw_consistency(['MISSING_NAME_BODY', 'MISSING_NAME_BODY']), 'SINGLE_DRAW')
        self.assertEqual(classify.draw_consistency(['MISSING_NAME_BODY', 'NON_EMPTY_NAMES']), 'MULTIPLE_DRAWS')
        self.assertEqual(classify.draw_consistency([]), 'NO_RESPONSE_CAPTURED')


class ActivationTests(unittest.TestCase):
    def test_glitch_requires_the_activated_behavior(self):
        self.assertTrue(classify.activation_confirmed(classify.GLITCH, 'a11y_glitch'))
        self.assertFalse(classify.activation_confirmed(classify.GLITCH, 'standard'))
        self.assertFalse(classify.activation_confirmed(classify.GLITCH, None))

    def test_control_requires_a_non_glitch_behavior_to_be_named(self):
        self.assertTrue(classify.activation_confirmed(classify.CONTROL, 'standard'))
        self.assertFalse(classify.activation_confirmed(classify.CONTROL, 'a11y_glitch'))
        self.assertFalse(classify.activation_confirmed(classify.CONTROL, None))


class OutcomeTests(unittest.TestCase):
    def test_glitch_detected(self):
        v = classify.classify(classify.GLITCH, 'ALL_EMPTY', classify.matching_nodes(axe('axe-result-detect.json')))
        self.assertEqual((v['status'], v['outcome_category'], v['matches_expected'], v['realized_draw']),
                         ('SUCCESS', 'DETECTED', True, 'MISSING_NAME'))

    def test_glitch_not_detected(self):
        v = classify.classify(classify.GLITCH, 'ALL_EMPTY', classify.matching_nodes(axe('axe-result-no-match.json')))
        self.assertEqual((v['status'], v['outcome_category'], v['matches_expected']), ('FAILURE', 'NOT_DETECTED', False))

    def test_glitch_draw_without_ground_truth_is_recorded_not_counted(self):
        v = classify.classify(classify.GLITCH, 'NOT_EMPTY', classify.matching_nodes(axe('axe-result-empty.json')))
        self.assertEqual((v['status'], v['outcome_category'], v['matches_expected'], v['realized_draw']),
                         ('INCONCLUSIVE', 'NO_GROUND_TRUTH_INSTANCE', None, 'NOT_MISSING_NAME'))

    def test_undecidable_dom_states_are_inconclusive(self):
        for dom, category in (('NO_CARDS', 'INCONCLUSIVE_NO_PRODUCT_HEADINGS'), ('MIXED', 'INCONCLUSIVE_MIXED_DOM_STATE'),
                              ('EMPTY_ARIA_NAMED', 'INCONCLUSIVE_ARIA_NAME_PRESENT')):
            v = classify.classify(classify.GLITCH, dom, [])
            self.assertEqual((v['status'], v['outcome_category'], v['matches_expected']), ('INCONCLUSIVE', category, None), dom)

    def test_control_absent_and_present(self):
        absent = classify.classify(classify.CONTROL, 'NOT_EMPTY', [])
        self.assertEqual((absent['status'], absent['outcome_category'], absent['matches_expected']), ('SUCCESS', 'CONTROL_RULE_ABSENT', True))
        present = classify.classify(classify.CONTROL, 'NOT_EMPTY', classify.matching_nodes(axe('axe-result-detect.json')))
        self.assertEqual((present['status'], present['outcome_category'], present['matches_expected']), ('FAILURE', 'CONTROL_RULE_PRESENT', False))

    def test_control_with_empty_product_headings_is_inconclusive(self):
        v = classify.classify(classify.CONTROL, 'ALL_EMPTY', [])
        self.assertEqual(v['outcome_category'], 'INCONCLUSIVE_CONTROL_DOM_STATE')

    def test_unknown_kinds_fail_loudly(self):
        with self.assertRaises(ValueError):
            classify.classify('OTHER', 'ALL_EMPTY', [])
        with self.assertRaises(ValueError):
            classify.classify(classify.GLITCH, 'UNKNOWN', [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
