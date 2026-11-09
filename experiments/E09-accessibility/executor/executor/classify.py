"""E09 classifier: ground truth from the rendered DOM, detection from the scanner result, outcome mapping.

DRAFT (operation OP-PREP-E09). Not frozen, not locked. Standard library only and no browser import, so that every
decision is a pure function of the recorded DOM list and the recorded scanner result and can be replayed from the
bundle and from the unit tests in experiments/E09-accessibility/executor/tests/.
Design basis: experiments/E09-accessibility/design-brief-draft.md, sections 4.4, 4.5, 12 (HD-1, HD-3 to HD-5, HD-20).
"""
import json
import re

RULE_ID = 'empty-heading'
TARGET_TEST_ID_PREFIX = 'pizza-name-'
SELECTOR_TEXT = 'h2[data-testid^="pizza-name-"]'  # the predeclared target selector, as the DOM records read it
# A scanner node counts as a match when its HTML opens an h2 whose data-testid starts with the predeclared prefix.
# axe-core generates its own target selectors, which need not contain the test id, so the match is made on node.html.
NODE_HTML_MATCH = re.compile(r'^\s*<h2\b[^>]*?\bdata-testid="' + TARGET_TEST_ID_PREFIX, re.IGNORECASE)
ACTIVATED_BEHAVIOR = 'a11y_glitch'
GLITCH, CONTROL = 'GLITCH', 'CONTROL'


def dom_state(records):
    """Ground-truth state of the product headings, decided from the DOM records read at scan time.

    records: one dict per h2[data-testid^="pizza-name-"] element, with keys data_testid, text, aria_label,
    aria_labelledby, title (read in the page; see sut01_catalog.DOM_RECORDS_JS). States:
    NO_CARDS (no matching element: the catalog did not render, not a ground-truth state), NOT_EMPTY (no heading empty),
    MIXED (some empty, some not: not classifiable), EMPTY_ARIA_NAMED (every heading empty but at least one carries an
    ARIA name or title, so the predeclared rule cannot fire by its own definition), ALL_EMPTY (ground truth).
    """
    records = list(records or [])
    if not records:
        return 'NO_CARDS', {'count': 0}
    empty = [r for r in records if not str(r.get('text') or '').strip()]
    named = [r for r in records if any(str(r.get(k) or '').strip() for k in ('aria_label', 'aria_labelledby', 'title'))]
    detail = {'count': len(records), 'empty': len(empty)}
    if not empty:
        return 'NOT_EMPTY', detail
    if len(empty) != len(records):
        return 'MIXED', detail
    if named:
        detail['aria_named'] = len(named)
        return 'EMPTY_ARIA_NAMED', detail
    return 'ALL_EMPTY', detail


def matching_nodes(axe_result, rule_id=RULE_ID):
    """Nodes of the predeclared rule's violations whose HTML opens a pizza-name h2 (rule presence elsewhere is not counted)."""
    out = []
    for rule in (axe_result or {}).get('violations') or []:
        if rule.get('id') != rule_id:
            continue
        for node in rule.get('nodes') or []:
            html = node.get('html') or ''
            if NODE_HTML_MATCH.match(html):
                out.append({'target': node.get('target'), 'html_prefix': html[:200]})
    return out


def rule_node_total(axe_result, rule_id=RULE_ID):
    """Descriptive count only: every node of the predeclared rule in violations, whatever its element (never the judgment)."""
    rules = (axe_result or {}).get('violations') or []
    return sum(len(rule.get('nodes') or []) for rule in rules if rule.get('id') == rule_id)


def body_class(body_text):
    """Corroboration of the realized draw from a captured GET /api/pizzas response body (never the judgment)."""
    try:
        data = json.loads(body_text)
    except (TypeError, ValueError):
        return 'UNPARSEABLE'
    if not isinstance(data, list):
        return 'UNPARSEABLE'
    names = [str(p.get('name') or '') for p in data if isinstance(p, dict) and 'name' in p]
    if not names:
        return 'UNPARSEABLE'
    if all(not n.strip() for n in names):
        return 'MISSING_NAME_BODY'
    if all(n.strip() for n in names):
        return 'NON_EMPTY_NAMES'
    return 'MIXED_NAMES'


def corroboration(dom, body_classes):
    """AGREES, DISAGREES, NOT_INTERPRETABLE, or NO_RESPONSE_CAPTURED, from the DOM state and the captured body classes."""
    if not body_classes:
        return 'NO_RESPONSE_CAPTURED'
    if len(set(body_classes)) != 1 or body_classes[0] == 'UNPARSEABLE' or body_classes[0] == 'MIXED_NAMES':
        return 'NOT_INTERPRETABLE'
    body = body_classes[0]
    if (dom == 'ALL_EMPTY' and body == 'MISSING_NAME_BODY') or (dom == 'NOT_EMPTY' and body == 'NON_EMPTY_NAMES'):
        return 'AGREES'
    return 'DISAGREES'


def draw_consistency(body_classes):
    """Whether every captured catalog response of one page load carries the same draw (brief section 4.4)."""
    if not body_classes:
        return 'NO_RESPONSE_CAPTURED'
    return 'SINGLE_DRAW' if len(set(body_classes)) == 1 else 'MULTIPLE_DRAWS'


def activation_confirmed(kind, behavior):
    """Glitch: the login response names the activated behavior. Control: it names a behavior other than the activated one."""
    if kind == GLITCH:
        return behavior == ACTIVATED_BEHAVIOR
    return behavior is not None and behavior != ACTIVATED_BEHAVIOR


def classify(kind, dom, matches):
    """Outcome of one attempt.

    Returns outcome_category, status (run-level SUCCESS, FAILURE, INCONCLUSIVE), matches_expected (true, false, or None),
    and realized_draw (the class of the rendered draw; DOM-decided). Status mapping (HUMAN DECISION HD-E09-B, default
    used): DETECTED and CONTROL_RULE_ABSENT are SUCCESS; NOT_DETECTED and CONTROL_RULE_PRESENT are FAILURE; a draw
    without a ground-truth instance and every undecidable DOM state are INCONCLUSIVE.
    """
    def out(status, category, matches_expected, draw):
        return {'status': status, 'outcome_category': category, 'matches_expected': matches_expected, 'realized_draw': draw}

    if kind == GLITCH:
        if dom == 'NO_CARDS':
            return out('INCONCLUSIVE', 'INCONCLUSIVE_NO_PRODUCT_HEADINGS', None, 'UNDECIDED')
        if dom == 'MIXED':
            return out('INCONCLUSIVE', 'INCONCLUSIVE_MIXED_DOM_STATE', None, 'UNDECIDED')
        if dom == 'EMPTY_ARIA_NAMED':
            return out('INCONCLUSIVE', 'INCONCLUSIVE_ARIA_NAME_PRESENT', None, 'MISSING_NAME_ARIA_NAMED')
        if dom == 'NOT_EMPTY':
            return out('INCONCLUSIVE', 'NO_GROUND_TRUTH_INSTANCE', None, 'NOT_MISSING_NAME')
        if dom == 'ALL_EMPTY':
            if matches:
                return out('SUCCESS', 'DETECTED', True, 'MISSING_NAME')
            return out('FAILURE', 'NOT_DETECTED', False, 'MISSING_NAME')
        raise ValueError(f'unknown DOM state {dom!r}')
    if kind == CONTROL:
        if dom != 'NOT_EMPTY':
            return out('INCONCLUSIVE', 'INCONCLUSIVE_CONTROL_DOM_STATE', None, 'UNDECIDED')
        if matches:
            return out('FAILURE', 'CONTROL_RULE_PRESENT', False, 'NOT_MISSING_NAME')
        return out('SUCCESS', 'CONTROL_RULE_ABSENT', True, 'NOT_MISSING_NAME')
    raise ValueError(f'unknown condition kind {kind!r}')
