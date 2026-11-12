"""E09 probe (ENVIRONMENT_VERIFICATION only; never measured, never imported): the verification items of the design brief, section 13, item 1.

DRAFT (operation OP-PREP-E09; added after the first environment-verification DRY_RUN of 2026-11-12, run 43292830947, whose single
Catalog load of the glitch account drew a mode other than missing_name and so could not show the scanner behavior). The activation
mode is drawn at random per catalog call, so the probe loads the Catalog page of the glitch account up to PROBE_MAX_LOADS times,
with a new browser context each time and one explicit-rule scan per load, until one load renders an ALL_EMPTY draw. On that load
it also runs the explicit rule set empty-heading plus image-alt and the default rule set. The decisions of the probe are the pure
functions of this module (summarize), replayable from the per-load records; the browser part only collects them.

The probe decides nothing about the campaign: HUMAN DECISIONs HD-3 and HD-4 stay as decided, and a FAIL here is a finding that
the human research lead reads before any lock.
"""
from . import classify, config, scanner, sut01_catalog, web

PROBE_MAX_LOADS = 30
IMAGE_ALT_RULE = 'image-alt'
EXPLICIT_PAIR_OPTIONS = {'runOnly': {'type': 'rule', 'values': [classify.RULE_ID, IMAGE_ALT_RULE]}}
DEFAULT_OPTIONS = {}
REPORTED_LISTS = ('violations', 'passes', 'incomplete', 'inapplicable')


def rule_reported(axe_result, rule_id):
    """Whether the rule appears in any of the four result lists (the rule ran, whatever its verdict)."""
    return any(r.get('id') == rule_id for key in REPORTED_LISTS for r in ((axe_result or {}).get(key) or []))


def rule_violation_nodes(axe_result, rule_id):
    """Number of nodes of the rule in violations (any element)."""
    return sum(len(r.get('nodes') or []) for r in ((axe_result or {}).get('violations') or []) if r.get('id') == rule_id)


def summarize(loads):
    """Checks (name, result, detail) from the per-load records of one probe.

    A load record has: load (1-based), dom_state, catalog_requests, draw_consistency, corroboration, explicit_matches, and, for
    the load that rendered ALL_EMPTY and was scanned further, pair_empty_heading_matches, image_alt_violation_nodes,
    default_matches, default_empty_heading_reported.
    """
    checks = []
    n = len(loads)
    counts = {}
    for r in loads:
        counts[r['dom_state']] = counts.get(r['dom_state'], 0) + 1
    first = next((r for r in loads if r['dom_state'] == 'ALL_EMPTY'), None)
    agree = sum(1 for r in loads if r.get('corroboration') == 'AGREES')
    checks.append((f'probe: realized draws over {n} Catalog loads of the glitch account (stop at the first ALL_EMPTY draw)',
                   'PASS' if first else 'NOT_VERIFIED',
                   f'DOM states {dict(sorted(counts.items()))}; corroboration by the response body AGREES in {agree} of {n}; '
                   + (f'first ALL_EMPTY draw at load {first["load"]}' if first else f'no ALL_EMPTY draw in {n} loads')))
    bad = [r['load'] for r in loads if r.get('catalog_requests') != 1 or r.get('draw_consistency') != 'SINGLE_DRAW']
    checks.append(('probe: one GET of the catalog API per page load, one draw per load',
                   'PASS' if loads and not bad else 'FAIL',
                   f'{n} loads; requests per load {sorted({r.get("catalog_requests") for r in loads})}; loads that differ {bad}'))
    other = [r for r in loads if r['dom_state'] != 'ALL_EMPTY']
    stray = [r['load'] for r in other if r.get('explicit_matches')]
    if other:  # when the first load is ALL_EMPTY there is no such load and the check is not made (the control account covers it)
        checks.append(('probe: no matching node of empty-heading at a draw that is not ALL_EMPTY',
                       'PASS' if not stray else 'FAIL', f'{len(other)} such loads; loads with a matching node {stray}'))
    if not first:
        for name in ('probe: empty-heading (explicit rule set) reports the affected h2 at an ALL_EMPTY draw',
                     'probe: image-alt (explicit pair of rules) reports no node at an ALL_EMPTY draw',
                     'probe: the default rule set reports empty-heading for the affected h2 at an ALL_EMPTY draw'):
            checks.append((name, 'NOT_VERIFIED', 'no ALL_EMPTY draw was rendered'))
        return checks
    checks.append(('probe: empty-heading (explicit rule set) reports the affected h2 at an ALL_EMPTY draw',
                   'PASS' if first.get('explicit_matches', 0) >= 1 and first.get('pair_empty_heading_matches', 0) >= 1 else 'FAIL',
                   f'explicit single rule: {first.get("explicit_matches")} matching node(s); explicit pair: {first.get("pair_empty_heading_matches")}; '
                   f'sample test ids {first.get("target_test_ids")}'))
    alt = first.get('image_alt_violation_nodes')
    checks.append(('probe: image-alt (explicit pair of rules) reports no node at an ALL_EMPTY draw',
                   'PASS' if alt == 0 else 'FAIL', f'image-alt violation nodes: {alt} (the pinned source passes an empty alt attribute)'))
    checks.append(('probe: the default rule set reports empty-heading for the affected h2 at an ALL_EMPTY draw',
                   'PASS' if first.get('default_matches', 0) >= 1 and first.get('default_empty_heading_reported') else 'FAIL',
                   f'default rule set: {first.get("default_matches")} matching node(s); rule reported {first.get("default_empty_heading_reported")}'))
    return checks


def run_probe(run, site, token, login_body, axe_source, max_loads=PROBE_MAX_LOADS):
    """Collect the per-load records in a browser (the only part that needs Playwright). Returns the list of records."""
    loads = []
    for i in range(1, max_loads + 1):
        b = web.Browser(run)
        rec = {'load': i}
        try:
            b.goto(site + '/')
            sut01_catalog.seed_client_state(b, token, login_body)
            b.goto(site + config.CATALOG_PATH)
            try:
                b.page.locator('h2[data-testid^="pizza-name-"]').first.wait_for(state='attached', timeout=config.ACTION_TIMEOUT_MS)
            except Exception:  # noqa: BLE001 - no heading rendered: the DOM state records NO_CARDS
                pass
            b.settle()
            records = b.page.evaluate(sut01_catalog.DOM_RECORDS_JS)
            dom, detail = classify.dom_state(records)
            bodies = b.catalog_bodies()
            classes = [classify.body_class(x['body']) for x in bodies if x.get('status') == 200 and x.get('body') is not None]
            rec.update({'dom_state': dom, 'dom_detail': detail, 'catalog_requests': len(bodies), 'body_classes': classes,
                        'draw_consistency': classify.draw_consistency(classes), 'corroboration': classify.corroboration(dom, classes)})
            version, result = sut01_catalog.read_scan(b, run, axe_source, scanner.AXE_VERSION)
            rec['explicit_matches'] = len(classify.matching_nodes(result))
            if dom == 'ALL_EMPTY':
                pair = b.page.evaluate(sut01_catalog.AXE_RUN_JS, EXPLICIT_PAIR_OPTIONS)
                run.jsonfile('probe-axe-explicit-pair', pair)
                default = b.page.evaluate(sut01_catalog.AXE_RUN_JS, DEFAULT_OPTIONS)
                run.jsonfile('probe-axe-default', default)
                rec.update({'pair_empty_heading_matches': len(classify.matching_nodes(pair)),
                            'image_alt_violation_nodes': rule_violation_nodes(pair, IMAGE_ALT_RULE),
                            'default_matches': len(classify.matching_nodes(default)),
                            'default_empty_heading_reported': rule_reported(default, classify.RULE_ID),
                            'target_test_ids': [r.get('data_testid') for r in records][:3]})
                run.text('probe-dom-snapshot', b.content(), 'html')
        finally:
            b.close()
        loads.append(rec)
        run.log('probe-load', **{k: v for k, v in rec.items() if k in ('load', 'dom_state', 'catalog_requests', 'explicit_matches')})
        if rec.get('dom_state') == 'ALL_EMPTY':
            break
    run.jsonfile('probe-loads', loads)
    return loads
