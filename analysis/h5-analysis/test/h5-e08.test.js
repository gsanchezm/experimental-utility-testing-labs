'use strict';
// Tests of the pure functions of analysis/h5-analysis/compute-h5-e08.js (no raw data is read).
// Run: node --test analysis/h5-analysis/test/h5-e08.test.js
const test = require('node:test');
const assert = require('node:assert');
const m = require('../compute-h5-e08.js');
const core = require('../../h3-analysis/h3-metrics.js');

test('median: the middle value, the mean of the two middle values for an even count, null for none', () => {
  assert.strictEqual(m.median([3, 1, 2]), 2);
  assert.strictEqual(m.median([4, 1, 3, 2]), 2.5);
  assert.strictEqual(m.median([7]), 7);
  assert.strictEqual(m.median([]), null);
  assert.deepStrictEqual(m.medianOf([1, 3]), { n: 2, median: 2 });
  assert.deepStrictEqual(m.medianOf([]), { n: 0, median: null });
});

test('deriveCategory reads the recorded flags of the detection evidence', () => {
  assert.strictEqual(m.deriveCategory({ detected: true }), 'DETECTED');
  assert.strictEqual(m.deriveCategory({ detected: false }), 'NOT_DETECTED');
  assert.strictEqual(m.deriveCategory({ detected: false, external_image: 'the delayed image was not painted' }), 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED');
  assert.strictEqual(m.deriveCategory({ detected: null, absent_reasons: { D: 'READY_SIGNAL_MISSING first_item' } }), 'INCONCLUSIVE_READY_SIGNAL_MISSING');
  assert.strictEqual(m.deriveCategory({ detected: null, absent_reasons: { Ba: 'READY_SIGNAL_MISSING' } }), 'INCONCLUSIVE_READY_SIGNAL_MISSING');
  assert.strictEqual(m.deriveCategory({ detected: null, absent_reasons: { D: 'METRIC_ABSENT' } }), 'INCONCLUSIVE_METRIC_ABSENT');
  assert.strictEqual(m.deriveCategory({ detected: null, absent_reasons: {} }), null);
  assert.strictEqual(m.deriveCategory({ detected: 'maybe' }), null);
  assert.strictEqual(m.deriveCategory(null), null);
});

// ---- evaluate() on a synthetic conditions file ---------------------------------------------------------------------------------
const ORDERS = [['D', 'Ba', 'Bb'], ['Ba', 'D', 'Bb'], ['Ba', 'Bb', 'D']];
const cfg = {
  n_per_condition: 6,
  load_orders: ORDERS,
  attribution_labels: ['TOOLING', 'SUT', 'EXTERNAL'],
  category_sets: { start: ['START_SURFACE_NOT_READY', 'START_ACTIVATION_NOT_CONFIRMED'],
                   method: ['DETECTED', 'NOT_DETECTED', 'INCONCLUSIVE_READY_SIGNAL_MISSING', 'INCONCLUSIVE_METRIC_ABSENT', 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED'],
                   any: ['INTERRUPTED_', 'STUB_NO_BUNDLE'] },
  conditions: [
    { condition_id: 'C-A', sut_id: 'SUT-01', behavior_class: 'deterministic', metric: 'first_item_ms', unit: 'ms', h5_counted: true, expected_category: 'DETECTED', rule: { comparison: 'delta_ge', threshold: 2500 } },
    { condition_id: 'C-B', sut_id: 'SUT-02', behavior_class: 'deterministic', metric: 'longest_longtask_ms', unit: 'ms', h5_counted: true, expected_category: 'DETECTED', rule: { comparison: 'delta_ge', threshold: 4500 } },
    { condition_id: 'C-C', sut_id: 'SUT-03', behavior_class: 'external dependency', metric: 'lcp_ms', unit: 'ms', h5_counted: true, expected_category: 'DETECTED', rule: { comparison: 'delta_ge', threshold: 2500 } },
    { condition_id: 'C-D', sut_id: 'SUT-03', behavior_class: 'deterministic', metric: 'cls', unit: 'score', h5_counted: true, expected_category: 'DETECTED',
      rule: { comparison: 'delta_gt', threshold: 0, also: { late_shift: { min_start_ms: 3500, target_element_id: 'target-text' } } } }
  ]
};
function rowsFor(cond, categories, extra) {
  return categories.map((c, i) => {
    const valid = c === 'DETECTED' || c === 'NOT_DETECTED';
    return Object.assign({ condition_id: cond.condition_id, run_id: `${cond.condition_id}__EX000${i + 1}__A1`, execution_index: i + 1, recorded_category: c, derived_category: c,
      status: c === 'DETECTED' ? 'SUCCESS' : c === 'NOT_DETECTED' ? 'FAILURE' : 'INCONCLUSIVE', matches_expected: valid ? c === cond.expected_category : null, attribution: 'SUT',
      order: ORDERS[i % 3], values: { D: 3100, Ba: 100, Bb: 105 }, delta_D: 3000, delta_Bb: 5, baseline_false_positive: false, late_shift_entries: 1, toolchain: { python: '3.12' } }, extra || {});
  });
}
const SIX = ['DETECTED', 'DETECTED', 'DETECTED', 'DETECTED', 'DETECTED', 'DETECTED'];
function allRows(over) {
  const by = Object.assign({ 'C-A': SIX, 'C-B': SIX, 'C-C': SIX, 'C-D': ['NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED'] }, over || {});
  return cfg.conditions.flatMap((c) => rowsFor(c, by[c.condition_id]));
}

test('evaluate: detection over the valid measurements with the Wilson interval from the core, a non-detection is data', () => {
  const r = m.evaluate(cfg, allRows());
  assert.deepStrictEqual(r.violations, []);
  const byId = Object.fromEntries(r.conditions.map((c) => [c.condition_id, c]));
  assert.strictEqual(byId['C-A'].detection_proportion.x, 6);
  assert.strictEqual(byId['C-A'].detection_proportion.n, 6);
  assert.deepStrictEqual(byId['C-A'].detection_proportion.interval, core.wilson(6, 6, m.WILSON_Z));
  assert.strictEqual(byId['C-D'].detection_proportion.x, 0);
  assert.strictEqual(byId['C-D'].detection_proportion.n, 6);                          // a NOT_DETECTED stays in the denominator
  assert.ok(byId['C-D'].non_detection_note);
  assert.ok(!byId['C-A'].non_detection_note);
  assert.deepStrictEqual(byId['C-D'].matches_expected_counts, { false: 6 });
});

test('evaluate: INCONCLUSIVE executions sit outside the detection denominator but appear in the table of counts (E08-D-18)', () => {
  const r = m.evaluate(cfg, allRows({ 'C-A': ['DETECTED', 'DETECTED', 'INCONCLUSIVE_READY_SIGNAL_MISSING', 'DETECTED', 'NOT_DETECTED', 'INCONCLUSIVE_METRIC_ABSENT'] }));
  const a = r.conditions.find((c) => c.condition_id === 'C-A');
  assert.strictEqual(a.n_executions, 6);
  assert.strictEqual(a.valid_measurements, 4);
  assert.strictEqual(a.excluded_from_detection_denominator, 2);
  assert.strictEqual(a.detection_proportion.x, 3);
  assert.strictEqual(a.detection_proportion.n, 4);
  assert.strictEqual(a.category_counts.INCONCLUSIVE_READY_SIGNAL_MISSING.x, 1);
  assert.strictEqual(a.category_counts.INCONCLUSIVE_READY_SIGNAL_MISSING.n, 6);       // counts are out of all N executions
  assert.deepStrictEqual(r.violations, []);
});

test('evaluate: the false-positive proportion is over the executions that have a baseline record, whatever the category of D', () => {
  const rows = allRows();
  const a = rows.filter((x) => x.condition_id === 'C-A');
  a[0].baseline_false_positive = true;                                                 // a false positive
  a[1].baseline_false_positive = null;                                                  // no record (a baseline load was not valid)
  a[2].recorded_category = a[2].derived_category = 'INCONCLUSIVE_READY_SIGNAL_MISSING'; a[2].status = 'INCONCLUSIVE'; a[2].matches_expected = null;   // D invalid, baseline record kept
  const r = m.evaluate(cfg, rows);
  assert.deepStrictEqual(r.violations, []);
  const fp = r.conditions.find((c) => c.condition_id === 'C-A').false_positive_proportion;
  assert.strictEqual(fp.x, 1);
  assert.strictEqual(fp.n, 5);
  assert.strictEqual(fp.executions_without_record, 1);
});

test('evaluate: medians are descriptive, over the recorded values only', () => {
  const rows = allRows();
  const a = rows.filter((x) => x.condition_id === 'C-A');
  a.forEach((x, i) => { x.values = { D: 3000 + i, Ba: 100, Bb: i === 0 ? null : 110 }; x.delta_D = 2900 + i; x.delta_Bb = i === 0 ? null : 10; });
  const med = m.evaluate(cfg, rows).conditions.find((c) => c.condition_id === 'C-A').medians_descriptive;
  assert.deepStrictEqual(med.metric_D, { n: 6, median: 3002.5 });
  assert.deepStrictEqual(med.metric_Bb, { n: 5, median: 110 });
  assert.deepStrictEqual(med.delta_Bb_minus_Ba, { n: 5, median: 10 });
});

test('evaluate: the late-shift component is reported only for the condition whose rule has it', () => {
  const r = m.evaluate(cfg, allRows());
  assert.ok(r.conditions.find((c) => c.condition_id === 'C-D').late_target_shift_entries);
  assert.ok(!r.conditions.find((c) => c.condition_id === 'C-A').late_target_shift_entries);
});

test('evaluate: the H5 count is taken from the conditions file, each condition once, whatever the outcome (E08-D-2)', () => {
  const h = m.evaluate(cfg, allRows()).h5_counts;
  assert.strictEqual(h['SUT-01'].count, 1);
  assert.strictEqual(h['SUT-02'].count, 1);
  assert.strictEqual(h['SUT-03'].count, 2);                                            // the CLS condition counts although it is never detected
  assert.match(h['SUT-01'].role, /H5 pair/);
  for (const s of ['SUT-04', 'SUT-05', 'SUT-06']) { assert.strictEqual(h[s].count, null); assert.match(h[s].reason, /no data: no ground-truth condition available/); }
  const other = m.evaluate(cfg, allRows({ 'C-A': ['NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED', 'NOT_DETECTED'] })).h5_counts;
  assert.deepStrictEqual(h, other);
});

test('evaluate: a recorded category that differs from the derived one is a violation', () => {
  const rows = allRows(); rows[0].derived_category = 'NOT_DETECTED';
  assert.ok(m.evaluate(cfg, rows).violations.some((v) => /recorded DETECTED, derived NOT_DETECTED/.test(v)));
});

test('evaluate: an underivable category, a wrong count, a gap and an undeclared category are violations', () => {
  const rows = allRows(); rows[1].derived_category = null;
  assert.ok(m.evaluate(cfg, rows).violations.some((v) => /cannot be derived/.test(v)));
  const short = allRows().filter((r) => !(r.condition_id === 'C-B' && r.execution_index === 6));
  assert.ok(m.evaluate(cfg, short).violations.some((v) => /C-B: 5 executions, not 6/.test(v)));
  const gap = allRows().filter((r) => !(r.condition_id === 'C-B' && r.execution_index === 2));
  assert.ok(m.evaluate(cfg, gap).violations.some((v) => /gap/.test(v)));
  const alien = allRows(); alien[2].recorded_category = alien[2].derived_category = 'SOMETHING_ELSE'; alien[2].matches_expected = null;
  assert.ok(m.evaluate(cfg, alien).violations.some((v) => /outside the declared set/.test(v)));
});

test('evaluate: matches_expected, the status, the attribution and the order of the loads are checked', () => {
  const a = allRows(); a[0].matches_expected = false;
  assert.ok(m.evaluate(cfg, a).violations.some((v) => /matches_expected disagrees/.test(v)));
  const b = allRows(); b[0].status = 'FAILURE';
  assert.ok(m.evaluate(cfg, b).violations.some((v) => /status FAILURE does not belong/.test(v)));
  const c = allRows(); c[0].attribution = 'ELSEWHERE';
  assert.ok(m.evaluate(cfg, c).violations.some((v) => /attribution ELSEWHERE is outside/.test(v)));
  const d = allRows(); d[0].order = ['Ba', 'D', 'Bb'];
  assert.ok(m.evaluate(cfg, d).violations.some((v) => /not the one of the rotation rule/.test(v)));
});

test('evaluate: a condition outside the conditions file is a violation', () => {
  const rows = allRows(); rows[0].condition_id = 'C-ZZ';
  assert.ok(m.evaluate(cfg, rows).violations.some((v) => /C-ZZ is not in the conditions file/.test(v)));
});

test('evaluate: no pooled rate, composite or ranking field is produced', () => {
  const text = JSON.stringify(m.evaluate(cfg, allRows()));
  for (const word of ['composite', 'ranking', 'pooled', 'winner', 'p_value', 'fisher']) assert.ok(!text.toLowerCase().includes(word), word);
});
