'use strict';
// Unit tests of analysis/e04-tsrr-analysis/compute-tsrr-e04.js (evaluate) on synthetic attempt records (no raw data, no SUT).
// Run: node --test analysis/e04-tsrr-analysis/test
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const { evaluate, WILSON_Z } = require('../compute-tsrr-e04.js');

const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'experiments', 'E04-repeatability', 'conditions-draft.json'), 'utf8'));
const near = (a, b, tol = 1e-3) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);
const ex = (n) => `EX${String(n).padStart(4, '0')}`;

/** 50 attempts per condition; `overrides` maps a condition id to a list of [execution number, category, attribution]. */
function attemptsFor(overrides = {}, only = null) {
  const out = [];
  for (const c of cfg.conditions) {
    if (only && !only.includes(c.condition_id)) continue;
    const ov = Object.fromEntries((overrides[c.condition_id] || []).map(([n, cat, attr]) => [n, [cat, attr]]));
    for (let n = 1; n <= c.n; n++) {
      const [cat, attr] = ov[n] || [cfg.success_category, 'SUT'];
      out.push({ condition_id: c.condition_id, run_id: `${c.condition_id}__${ex(n)}__A1`, execution_id: ex(n), attempt: 1, outcome_category: cat,
                 matches_expected: cat === c.expected_category, attribution: attr, toolchain: { python3: '3.12.16' } });
    }
  }
  return out;
}

test('the conditions file is the locked one: 13 conditions, N = 50, every expected category is the success category', () => {
  assert.equal(cfg.conditions.length, 13);
  assert.equal(cfg.n_per_condition, 50);
  for (const c of cfg.conditions) { assert.equal(c.n, 50); assert.equal(c.expected_category, cfg.success_category); }
});

test('all attempts verified: T = S = 50, TSRR = 1 with the Wilson lower bound about 0.929', () => {
  const r = evaluate(cfg, attemptsFor());
  assert.deepEqual(r.violations, []);
  for (const m of r.conditions) {
    assert.equal(m.T, 50); assert.equal(m.S, 50);
    assert.equal(m.TSRR.value, 1); near(m.TSRR.interval.lower, 0.9285, 2e-3); assert.equal(m.TSRR.interval.upper, 1);
    assert.equal(m.category_counts[cfg.success_category], 50);
  }
});

test('failures stay in the denominator and are counted by category and by attribution; the raw rate is not recomputed on attribution', () => {
  const id = cfg.conditions[0].condition_id;
  const r = evaluate(cfg, attemptsFor({ [id]: [[3, 'RESET_FAILED', 'SUT'], [7, 'ESTABLISHMENT_INTERRUPTED', 'TOOLING'], [9, 'STUB_NO_BUNDLE', 'SUT']] }));
  assert.deepEqual(r.violations, []);
  const m = r.conditions.find((x) => x.condition_id === id);
  assert.equal(m.T, 50); assert.equal(m.S, 47); near(m.TSRR.value, 0.94, 1e-12);
  assert.equal(m.category_counts.RESET_FAILED, 1); assert.equal(m.category_counts.ESTABLISHMENT_INTERRUPTED, 1); assert.equal(m.category_counts.STUB_NO_BUNDLE, 1);
  assert.equal(m.attribution_by_category.TOOLING.ESTABLISHMENT_INTERRUPTED, 1);
  assert.equal(m.attribution_by_category.SUT.RESET_FAILED, 1);
  assert.equal(m.attribution_by_category.SUT.TARGET_STATE_VERIFIED, 47);
});

test('an empty condition is NOT_ESTIMABLE (never 0) and is reported by the consistency checks', () => {
  const r = evaluate(cfg, attemptsFor({}, cfg.conditions.slice(1).map((c) => c.condition_id)));
  const m = r.conditions[0];
  assert.equal(m.T, 0); assert.equal(m.TSRR.value, 'NOT_ESTIMABLE'); assert.equal(m.TSRR.interval, 'NOT_ESTIMABLE');
  assert.ok(r.violations.some((v) => v.includes('no attempt record for EX0001')));
});

test('violations: undeclared category, repeated pair, wrong attempt, match flag disagreeing, unknown condition, bad attribution', () => {
  const a = attemptsFor();
  a[0].outcome_category = 'S_SOMETHING';
  a[1].execution_id = a[2].execution_id;
  a[3].attempt = 2;
  a[4].matches_expected = false;
  a.push({ condition_id: 'E04-NOPE', run_id: 'x', execution_id: 'EX0001', attempt: 1, outcome_category: cfg.success_category, matches_expected: true, attribution: null, toolchain: {} });
  a[5].attribution = 'HUMAN';
  const v = evaluate(cfg, a).violations.join('\n');
  for (const frag of ['is not in the declared set', 'repeated (execution_id, attempt) pair', 'is not 1', 'matches_expected', 'is not in the conditions table', 'is not TOOLING, SUT or null']) assert.ok(v.includes(frag), frag);
});

test('toolchain drift is reported per condition and per tool, and the z of the interval is the 95 percent value', () => {
  const a = attemptsFor();
  a[0].toolchain = { python3: '3.12.17' };
  const r = evaluate(cfg, a);
  assert.deepEqual(r.toolchain_drift_confounds[cfg.conditions[0].condition_id].python3, ['3.12.16', '3.12.17']);
  assert.equal(WILSON_Z, 1.959963984540054);
});
