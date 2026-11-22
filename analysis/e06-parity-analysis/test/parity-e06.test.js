'use strict';
// Unit tests of analysis/e06-parity-analysis/compute-parity-e06.js (evaluate, classifyPair, fisherExact, riskDifference) on synthetic execution records (no raw data, no SUT).
// Run: node --test analysis/e06-parity-analysis/test/parity-e06.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const { evaluate, classifyPair, fisherExact, riskDifference, WILSON_Z, PAIR_CLASSES, COMPARISONS_NOT_ESTIMABLE } = require('../compute-parity-e06.js');

const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'experiments', 'E06-cross-platform-parity', 'conditions-draft.json'), 'utf8'));
const near = (a, b, tol = 1e-3) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);
const IDENT = { 'SUT-01': 'p01', 'SUT-02': 'Sauce Labs Backpack' };

/** 50 executions per condition, all ARRIVED_IDENTITY_READ with the same identity; `overrides` maps a condition id to rows [index, fields]. */
function executionsFor(overrides = {}) {
  const out = [];
  for (const c of cfg.conditions) {
    const ov = Object.fromEntries((overrides[c.condition_id] || []).map((r) => [r[0], r[1]]));
    for (let n = 1; n <= c.n; n++) {
      const base = { condition_id: c.condition_id, run_id: `${c.condition_id}__EX${String(n).padStart(4, '0')}__A1`, execution_index: n, category: 'ARRIVED_IDENTITY_READ', reason: null,
                     attribution: 'NONE', identity: IDENT[c.sut_id], identity_raw: IDENT[c.sut_id], arrived: true, status: 'SUCCESS', toolchain: { python3: '3.12.16' } };
      out.push({ ...base, ...(ov[n] || {}) });
    }
  }
  return out;
}
const NOT_ARRIVED_5XX = { category: 'NOT_ARRIVED_INFRASTRUCTURE', reason: 'INFRA_BACKEND_5XX', attribution: 'INFRASTRUCTURE', identity: null, identity_raw: null, arrived: false, status: 'ABORTED' };
const UNREADABLE = { category: 'ARRIVED_IDENTITY_UNREADABLE', reason: 'IDENTITY_NOT_READABLE', attribution: 'UNDETERMINED', identity: null, identity_raw: null };

test('the conditions file is the locked draft: four conditions (WEB and ANDROID of SUT-01 and SUT-02), N = 50, six categories, oracle item_identity', () => {
  assert.equal(cfg.conditions.length, 4);
  assert.equal(cfg.n_per_condition, 50);
  assert.equal(cfg.categories.length, 6);
  assert.deepEqual(cfg.conditions.map((c) => c.condition_id), ['E06-CS007-SUT01-WEB', 'E06-CS007-SUT01-ANDROID', 'E06-CS007-SUT02-WEB', 'E06-CS007-SUT02-ANDROID']);
  for (const c of cfg.conditions) { assert.equal(c.n, 50); assert.equal(c.identity_oracle, 'item_identity'); }
  assert.deepEqual(PAIR_CLASSES, ['PARITY', 'IDENTITY_DIFFERENT', 'IDENTITY_UNREADABLE', 'NOT_ARRIVED', 'ARRIVAL_ONLY']);
});

test('every pair in parity: 50 of 50 per ecosystem, the Wilson lower bound about 0.929, risk difference 0 and Fisher p 1, no violation', () => {
  const r = evaluate(cfg, executionsFor());
  assert.deepEqual(r.violations, []);
  assert.equal(r.ecosystems.length, 2);
  for (const e of r.ecosystems) {
    assert.equal(e.pairs, 50); assert.equal(e.parity_pairs, 50);
    assert.equal(e.parity_proportion.value, 1);
    near(e.parity_proportion.interval.lower, 0.9287); assert.equal(e.parity_proportion.interval.upper, 1);
    assert.equal(e.pair_class_counts.PARITY, 50);
    assert.deepEqual(e.non_parity_pairs_by_class_and_attribution, {});
  }
  assert.equal(r.pairs.length, 100);
  assert.equal(r.comparison.risk_difference.value, 0);
  near(r.comparison.risk_difference.interval.lower, -0.0714); near(r.comparison.risk_difference.interval.upper, 0.0714);
  near(r.comparison.fisher_exact_two_sided_p, 1, 1e-9);
  assert.match(r.comparison.verdict, /^none: no support or non-support criterion/);
});

test('a non-arrival, an unreadable identity and a different identity are non-parity, each its own class, with the attributed counts beside the raw proportion', () => {
  const r = evaluate(cfg, executionsFor({
    'E06-CS007-SUT01-WEB': [[3, NOT_ARRIVED_5XX]],
    'E06-CS007-SUT01-ANDROID': [[4, UNREADABLE], [5, { identity: 'p02', identity_raw: 'p02' }]]
  }));
  assert.deepEqual(r.violations, []);
  const e = r.ecosystems.find((x) => x.sut_id === 'SUT-01');
  assert.equal(e.parity_pairs, 47); assert.equal(e.pairs, 50);
  assert.deepEqual(e.pair_class_counts, { PARITY: 47, IDENTITY_DIFFERENT: 1, IDENTITY_UNREADABLE: 1, NOT_ARRIVED: 1, ARRIVAL_ONLY: 0 });
  assert.equal(e.non_parity_pairs_by_class_and_attribution['NOT_ARRIVED (WEB:INFRASTRUCTURE)'], 1);
  assert.equal(e.non_parity_pairs_by_class_and_attribution['IDENTITY_UNREADABLE (ANDROID:UNDETERMINED)'], 1);
  assert.equal(e.non_parity_pairs_by_class_and_attribution['IDENTITY_DIFFERENT (no side attributed)'], 1);
  assert.equal(e.web_surface.not_arrived, 1); assert.equal(e.android_surface.identity_unreadable, 1);
  assert.equal(e.web_surface.not_arrived_reason_counts.INFRA_BACKEND_5XX, 1);
  near(e.parity_proportion.value, 0.94, 1e-12);
  assert.equal(e.category_pairs_crosstab['NOT_ARRIVED_INFRASTRUCTURE | ARRIVED_IDENTITY_READ'], 1);
  const e2 = r.ecosystems.find((x) => x.sut_id === 'SUT-02');
  assert.equal(e2.parity_pairs, 50);
  near(r.comparison.risk_difference.value, -0.06, 1e-12);
});

test('classifyPair: the precedence is NOT_ARRIVED, then IDENTITY_UNREADABLE, then ARRIVAL_ONLY, then the identity comparison', () => {
  const read = (id) => ({ category: 'ARRIVED_IDENTITY_READ', identity: id });
  assert.equal(classifyPair(read('p01'), read('p01'), 'ARRIVED_IDENTITY_READ'), 'PARITY');
  assert.equal(classifyPair(read('p01'), read('p02'), 'ARRIVED_IDENTITY_READ'), 'IDENTITY_DIFFERENT');
  assert.equal(classifyPair({ category: 'NOT_ARRIVED_SUT', identity: null }, { category: 'ARRIVED_IDENTITY_UNREADABLE', identity: null }, 'ARRIVED_IDENTITY_READ'), 'NOT_ARRIVED');
  assert.equal(classifyPair(read('p01'), { category: 'ARRIVED_IDENTITY_UNREADABLE', identity: null }, 'ARRIVED_IDENTITY_READ'), 'IDENTITY_UNREADABLE');
  assert.equal(classifyPair(read('p01'), { category: 'ARRIVED_ARRIVAL_ONLY', identity: null }, 'ARRIVED_IDENTITY_READ'), 'ARRIVAL_ONLY');
  assert.equal(classifyPair(read('p01'), { category: 'SOMETHING_ELSE', identity: 'p01' }, 'ARRIVED_IDENTITY_READ'), null);
  // the identity comparison is exact string equality of the normalized identity, case and spaces included
  assert.equal(classifyPair(read('Sauce Labs Backpack'), read('Sauce Labs backpack'), 'ARRIVED_IDENTITY_READ'), 'IDENTITY_DIFFERENT');
});

test('violations: an undeclared category, an undeclared reason or attribution, a missing or repeated execution, an arrival-only side, an identity missing on a read execution', () => {
  const bad = (ov) => evaluate(cfg, executionsFor(ov)).violations;
  assert.ok(bad({ 'E06-CS007-SUT01-WEB': [[1, { category: 'MADE_UP' }]] }).some((v) => /not in the declared set/.test(v)));
  assert.ok(bad({ 'E06-CS007-SUT01-WEB': [[1, { ...NOT_ARRIVED_5XX, reason: 'MADE_UP' }]] }).some((v) => /reason/.test(v)));
  assert.ok(bad({ 'E06-CS007-SUT01-WEB': [[1, { attribution: 'MADE_UP' }]] }).some((v) => /attribution/.test(v)));
  assert.ok(bad({ 'E06-CS007-SUT01-WEB': [[1, { reason: 'INFRA_BACKEND_5XX' }]] }).some((v) => /a reason on the category/.test(v)));
  assert.ok(bad({ 'E06-CS007-SUT02-WEB': [[2, { identity: null }]] }).some((v) => /without an identity/.test(v)));
  assert.ok(bad({ 'E06-CS007-SUT02-ANDROID': [[7, { category: 'ARRIVED_ARRIVAL_ONLY', identity: null }]] }).some((v) => /ARRIVED_ARRIVAL_ONLY/.test(v)));
  const missing = executionsFor().filter((e) => !(e.condition_id === 'E06-CS007-SUT01-ANDROID' && e.execution_index === 9));
  assert.ok(evaluate(cfg, missing).violations.some((v) => /no execution record for index 9/.test(v)));
  const repeated = executionsFor(); repeated.push({ ...repeated[0] });
  assert.ok(evaluate(cfg, repeated).violations.some((v) => /repeated execution index/.test(v)));
  const unknownCond = executionsFor(); unknownCond.push({ ...unknownCond[0], condition_id: 'E06-CS007-SUT09-WEB' });
  assert.ok(evaluate(cfg, unknownCond).violations.some((v) => /not in the conditions table/.test(v)));
});

test('the toolchain drift check reports a tool whose version differs inside a condition', () => {
  const ex = executionsFor(); ex[0].toolchain = { python3: '3.12.17' };
  assert.deepEqual(evaluate(cfg, ex).toolchain_drift_confounds['E06-CS007-SUT01-WEB'].python3, ['3.12.16', '3.12.17']);
  assert.deepEqual(evaluate(cfg, executionsFor()).toolchain_drift_confounds, {});
});

test('fisherExact: the two-sided p-values of known tables (R fisher.test) and the extremes', () => {
  near(fisherExact(8, 2, 1, 5), 0.03497, 1e-4);
  near(fisherExact(3, 1, 1, 3), 0.4857, 1e-4);
  near(fisherExact(50, 0, 50, 0), 1, 1e-9);
  assert.ok(fisherExact(50, 0, 0, 50) < 1e-25);
  near(fisherExact(0, 0, 0, 0), 1, 1e-12);
  assert.throws(() => fisherExact(-1, 1, 1, 1));
  assert.throws(() => fisherExact(1.5, 1, 1, 1));
});

test('riskDifference: the Newcombe example (56/70 against 48/80), the symmetry and the empty denominators', () => {
  const r = riskDifference(56, 70, 48, 80, WILSON_Z);
  near(r.value, 0.2, 1e-12); near(r.interval.lower, 0.0524, 1e-3); near(r.interval.upper, 0.3339, 1e-3);
  const s = riskDifference(48, 80, 56, 70, WILSON_Z);
  near(s.value, -0.2, 1e-12); near(s.interval.lower, -r.interval.upper, 1e-9); near(s.interval.upper, -r.interval.lower, 1e-9);
  assert.equal(riskDifference(1, 0, 1, 5, WILSON_Z), 'NOT_ESTIMABLE');
});

test('the comparisons that are not estimable name SUT-03, SUT-04, SUT-05 and SUT-06 and iOS, with a reason and no estimate', () => {
  assert.equal(COMPARISONS_NOT_ESTIMABLE.length, 4);
  for (const c of COMPARISONS_NOT_ESTIMABLE) { assert.equal(c.estimable, false); assert.ok(c.reason.length > 20); }
});
