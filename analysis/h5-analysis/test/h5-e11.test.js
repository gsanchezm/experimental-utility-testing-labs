'use strict';
// Tests of the pure functions of analysis/h5-analysis/compute-h5-e11.js (no raw data is read).
// Run: node --test analysis/h5-analysis/test/h5-e11.test.js
const test = require('node:test');
const assert = require('node:assert');
const m = require('../compute-h5-e11.js');
const core = require('../../h3-analysis/h3-metrics.js');

const MATCHING = { expected_m2_method: { 'SQLI-LOGIN': 'POST', 'DIRLIST-FTP': 'GET' }, expected_m2_path: { 'SQLI-LOGIN': '/rest/user/login', 'DIRLIST-FTP': '/ftp/' } };

test('normalizePath drops scheme, host, port, query and fragment and keeps the trailing slash', () => {
  assert.strictEqual(m.normalizePath('http://127.0.0.1:3000/ftp/?a=1#x'), '/ftp/');
  assert.strictEqual(m.normalizePath('http://127.0.0.1:3000/ftp'), '/ftp');
  assert.strictEqual(m.normalizePath('http://127.0.0.1:3000/rest/user/login'), '/rest/user/login');
});

test('expectedTarget: a CONDITION cell takes the matching rules, a CONTROL cell its control endpoint without the query', () => {
  const cfg = { matching_rules: MATCHING };
  assert.deepStrictEqual(m.expectedTarget({ cell_id: 'a', kind: 'CONDITION', condition: 'DIRLIST-FTP', expected_m2_rule_id: '0', expected_m2_target: '/ftp/' }, cfg), { rule: '0', method: 'GET', path: '/ftp/' });
  assert.deepStrictEqual(m.expectedTarget({ cell_id: 'b', kind: 'CONTROL', condition: 'SQLI-SEARCH', expected_m2_rule_id: '40018', control_endpoint: 'GET /rest/user/security-question?email=' }, cfg), { rule: '40018', method: 'GET', path: '/rest/user/security-question' });
  assert.throws(() => m.expectedTarget({ cell_id: 'c', kind: 'CONDITION', condition: 'SQLI-LOGIN', expected_m2_rule_id: '40018', expected_m2_target: 'POST /somewhere/else' }, cfg));
});

test('matchAlerts counts an alert only when rule, method and normalized path all equal the expectation', () => {
  const target = { rule: '40018', method: 'POST', path: '/rest/user/login' };
  const alerts = [
    { pluginId: '40018', method: 'POST', url: 'http://127.0.0.1:3000/rest/user/login' },          // counted
    { pluginId: 40018, method: 'POST', url: 'http://127.0.0.1:3000/rest/user/login?x=1' },        // counted (number rule id, query dropped)
    { pluginId: '40018', method: 'GET', url: 'http://127.0.0.1:3000/rest/user/login' },           // other: method
    { pluginId: '40018', method: 'POST', url: 'http://127.0.0.1:3000/rest/user/login/' },         // other: trailing slash
    { pluginId: '10021', method: 'POST', url: 'http://127.0.0.1:3000/rest/user/login' },          // other: rule
    { pluginId: '40018', method: 'POST', url: 'http://127.0.0.1:3000/rest/products/search' }       // other: path
  ];
  assert.deepStrictEqual(m.matchAlerts(alerts, target), { counted: 2, others: 4 });
  assert.deepStrictEqual(m.matchAlerts([], target), { counted: 0, others: 0 });
});

test('deriveM2 gives the expected-alert category only for a counted alert', () => {
  const target = { rule: '0', method: 'GET', path: '/ftp/' };
  assert.strictEqual(m.deriveM2([{ pluginId: '0', method: 'GET', url: 'http://h/ftp/' }], target).category, 'M2_EXPECTED_ALERT');
  assert.strictEqual(m.deriveM2([{ pluginId: '10096', method: 'GET', url: 'http://h/ftp/' }], target).category, 'M2_NO_EXPECTED_ALERT');
});

test('deriveM1Sut01 decides by the status of the GET', () => {
  assert.strictEqual(m.deriveM1Sut01({ response: { status: 200 } }), 'M1_IDOR_BYPASS_OBSERVED');
  assert.strictEqual(m.deriveM1Sut01({ response: { status: 403 } }), 'M1_IDOR_BLOCKED');
  assert.strictEqual(m.deriveM1Sut01({ response: { status: 500 } }), 'M1_RESPONSE_OTHER');
  assert.strictEqual(m.deriveM1Sut01({ response: { status: null } }), 'M1_RESPONSE_OTHER');
});

test('deriveM1Sut05 reads the solved flag of the oracle key in a possibly truncated body and never borrows the flag of another challenge', () => {
  const body = '{"status":"success","data":[{"id":1,"key":"aChallenge","solved":false},{"id":2,"key":"loginAdminChallenge","name":"x","solved":true},{"id":3,"key":"other","solved":false}';
  assert.strictEqual(m.deriveM1Sut05({ response: { status: 200, body } }, 'loginAdminChallenge'), 'M1_ORACLE_FLIPPED');
  assert.strictEqual(m.deriveM1Sut05({ response: { status: 200, body } }, 'aChallenge'), 'M1_ORACLE_NOT_FLIPPED');
  // the key is present but its flag was cut off before the next key: not readable, never the next challenge's flag
  const cut = '{"data":[{"id":1,"key":"loginAdminChallenge","name":"x"},{"id":2,"key":"next","solved":true}';
  assert.strictEqual(m.deriveM1Sut05({ response: { status: 200, body: cut } }, 'loginAdminChallenge'), null);
  assert.strictEqual(m.deriveM1Sut05({ response: { status: 200, body } }, 'absentChallenge'), null);
  assert.strictEqual(m.deriveM1Sut05({ response: { status: 503, body } }, 'loginAdminChallenge'), 'M1_RESPONSE_OTHER');
});

// ---- evaluate() on a synthetic cells file -----------------------------------------------------------------------------------
const cfg = {
  n_per_cell: 3, wilson_z: m.WILSON_Z,
  category_sets: { reset: ['RESET_FAILED', 'RESET_STARTING_STATE_NOT_REACHED'], m1: ['M1_ORACLE_FLIPPED', 'M1_ORACLE_NOT_FLIPPED', 'M1_IDOR_BYPASS_OBSERVED', 'M1_IDOR_BLOCKED', 'M1_RESPONSE_OTHER'],
                   m2: ['M2_EXPECTED_ALERT', 'M2_NO_EXPECTED_ALERT', 'ZAP_START_FAILED', 'ZAP_API_ERROR', 'ZAP_SCAN_TIMEOUT'], any: ['INTERRUPTED_'] },
  cells: [
    { cell_id: 'A-M1', sut_id: 'SUT-01', condition: 'IDOR', method: 'M1', kind: 'CONDITION', h5_count: 'yes', n: 3, expected_category: 'M1_IDOR_BYPASS_OBSERVED' },
    { cell_id: 'A-M1-CTRL', sut_id: 'SUT-01', condition: 'IDOR', method: 'M1', kind: 'CONTROL', h5_count: 'no', n: 3, expected_category: 'M1_IDOR_BLOCKED' },
    { cell_id: 'B-M1', sut_id: 'SUT-05', condition: 'SQLI', method: 'M1', kind: 'CONDITION', h5_count: 'specialist_reference', n: 3, expected_category: 'M1_ORACLE_FLIPPED' },
    { cell_id: 'B-M2', sut_id: 'SUT-05', condition: 'SQLI', method: 'M2', kind: 'CONDITION', h5_count: 'specialist_reference', n: 3, expected_category: 'M2_EXPECTED_ALERT' },
    { cell_id: 'B-M2-CTRL', sut_id: 'SUT-05', condition: 'SQLI', method: 'M2', kind: 'CONTROL', h5_count: 'no', n: 3, expected_category: 'M2_NO_EXPECTED_ALERT' }
  ]
};
function rowsFor(cell, categories, extra) {
  return categories.map((c, i) => Object.assign({ cell_id: cell.cell_id, run_id: `${cell.cell_id}__EX000${i + 1}__A1`, execution_index: i + 1, recorded_category: c, derived_category: c, status: 'SUCCESS',
    matches_expected: c === cell.expected_category, attribution: 'SUT', others: cell.method === 'M2' ? 1 : null, toolchain: { python: '3.12' } }, extra || {}));
}
function allRows(over) {
  const by = Object.assign({
    'A-M1': ['M1_IDOR_BYPASS_OBSERVED', 'M1_IDOR_BYPASS_OBSERVED', 'M1_IDOR_BYPASS_OBSERVED'],
    'A-M1-CTRL': ['M1_IDOR_BLOCKED', 'M1_IDOR_BLOCKED', 'M1_IDOR_BLOCKED'],
    'B-M1': ['M1_ORACLE_FLIPPED', 'M1_ORACLE_FLIPPED', 'M1_ORACLE_FLIPPED'],
    'B-M2': ['M2_NO_EXPECTED_ALERT', 'M2_NO_EXPECTED_ALERT', 'M2_NO_EXPECTED_ALERT'],
    'B-M2-CTRL': ['M2_NO_EXPECTED_ALERT', 'M2_NO_EXPECTED_ALERT', 'M2_NO_EXPECTED_ALERT']
  }, over || {});
  return cfg.cells.flatMap((c) => rowsFor(c, by[c.cell_id]));
}

test('evaluate: detection on a CONDITION cell, false positive on a CONTROL cell, Wilson interval from the core, a non-detection is data', () => {
  const r = m.evaluate(cfg, allRows());
  assert.deepStrictEqual(r.violations, []);
  const byId = Object.fromEntries(r.cells.map((c) => [c.cell_id, c]));
  assert.strictEqual(byId['A-M1'].positive_category_rate.x, 3);
  assert.strictEqual(byId['A-M1-CTRL'].positive_category_rate.x, 0);
  assert.strictEqual(byId['B-M2'].positive_category_rate.x, 0);
  assert.strictEqual(byId['B-M2'].positive_category_rate.n, 3);                       // no execution leaves the denominator
  assert.ok(byId['B-M2'].non_detection_note);
  assert.deepStrictEqual(byId['A-M1'].positive_category_rate.interval, core.wilson(3, 3, m.WILSON_Z));
  assert.strictEqual(byId['B-M2'].other_alerts_not_counted.total, 3);
  assert.strictEqual(byId['B-M2'].expected_category_rate.x, 0);
});

test('evaluate: the H5 count is taken from the cells file, each condition once (M1 and M2 of one condition, controls excluded)', () => {
  const r = m.evaluate(cfg, allRows());
  const h = r.h5_counts;
  assert.strictEqual(h['SUT-01'].count, 1);
  assert.strictEqual(h['SUT-05'].count, 1);                                           // SQLI counted once although it has M1 and M2 cells
  assert.match(h['SUT-01'].role, /H5 pair/);
  assert.match(h['SUT-05'].role, /EXPLORATORY specialist reference/);
  assert.strictEqual(h['SUT-02'].count, 0);
  assert.strictEqual(h['SUT-03'].count, 0);
  assert.strictEqual(h['SUT-04'].count, null);                                        // no count is invented for an ecosystem the configuration assigns none
  assert.strictEqual(h['SUT-06'].count, null);
  assert.match(h['SUT-02'].reason, /no data: no ground-truth condition available/);
});

test('evaluate: the counts do not depend on the outcomes', () => {
  const a = m.evaluate(cfg, allRows()).h5_counts;
  const b = m.evaluate(cfg, allRows({ 'B-M2': ['M2_EXPECTED_ALERT', 'M2_EXPECTED_ALERT', 'M2_EXPECTED_ALERT'] })).h5_counts;
  assert.deepStrictEqual(a, b);
});

test('evaluate: the per-condition table keeps M1 and M2 apart', () => {
  const r = m.evaluate(cfg, allRows());
  const sqli = r.conditions.find((c) => c.condition === 'SQLI');
  assert.deepStrictEqual(Object.keys(sqli.methods).sort(), ['M1', 'M2']);
  assert.strictEqual(sqli.methods.M1.detections.x, 3);
  assert.strictEqual(sqli.methods.M2.detections.x, 0);
  assert.strictEqual(sqli.methods.M2.false_positives.x, 0);
  assert.ok(!('detections_either_method' in sqli));
});

test('evaluate: a recorded category that differs from the derived one is a violation', () => {
  const rows = allRows();
  rows[0].derived_category = 'M1_IDOR_BLOCKED';
  assert.ok(m.evaluate(cfg, rows).violations.some((v) => /recorded M1_IDOR_BYPASS_OBSERVED, derived M1_IDOR_BLOCKED/.test(v)));
});

test('evaluate: an underivable category, a wrong count, a gap and a category outside the declared set are violations', () => {
  const rows = allRows(); rows[1].derived_category = null;
  assert.ok(m.evaluate(cfg, rows).violations.some((v) => /cannot be derived/.test(v)));
  const short = allRows().filter((r) => !(r.cell_id === 'B-M1' && r.execution_index === 3));
  assert.ok(m.evaluate(cfg, short).violations.some((v) => /B-M1: 2 executions, not 3/.test(v)));
  const gap = allRows().filter((r) => !(r.cell_id === 'B-M1' && r.execution_index === 2));
  assert.ok(m.evaluate(cfg, gap).violations.some((v) => /gap/.test(v)));
  const alien = allRows(); alien[2].recorded_category = 'M2_EXPECTED_ALERT'; alien[2].derived_category = 'M2_EXPECTED_ALERT'; alien[2].matches_expected = false;
  assert.ok(m.evaluate(cfg, alien).violations.some((v) => /outside the declared set/.test(v)));
});

test('evaluate: matches_expected must equal the comparison with the expected category', () => {
  const rows = allRows(); rows[0].matches_expected = false;
  assert.ok(m.evaluate(cfg, rows).violations.some((v) => /matches_expected disagrees/.test(v)));
});

test('evaluate: no pooled rate, composite or ranking field is produced', () => {
  const r = m.evaluate(cfg, allRows());
  const text = JSON.stringify(r);
  for (const word of ['composite', 'ranking', 'pooled', 'winner', 'p_value', 'fisher']) assert.ok(!text.toLowerCase().includes(word), word);
});
