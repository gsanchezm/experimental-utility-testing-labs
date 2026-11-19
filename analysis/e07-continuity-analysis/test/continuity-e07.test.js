'use strict';
// Unit tests of analysis/e07-continuity-analysis/compute-continuity-e07.js (evaluate) on synthetic attempt records (no raw data, no SUT).
// Run: node --test analysis/e07-continuity-analysis/test/continuity-e07.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const { evaluate, WILSON_Z, COMPARISONS_NOT_EVALUABLE } = require('../compute-continuity-e07.js');

const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'experiments', 'E07-cross-layer-continuity', 'conditions-draft.json'), 'utf8'));
const near = (a, b, tol = 1e-3) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);
const ex = (n) => `EX${String(n).padStart(4, '0')}`;
const LAST = { VERIFIED: 'verification', NOT_VERIFIED: 'verification', ESTABLISHMENT_FAILED: 'establishment-check', INTERRUPTED: 'reset', RUNNER_ERROR: 'verification' };

/** 50 attempts per condition; `overrides` maps a condition id to [execution number, category, attribution, interrupted cause, last phase] rows. */
function attemptsFor(overrides = {}, only = null) {
  const out = [];
  for (const c of cfg.conditions) {
    if (only && !only.includes(c.condition_id)) continue;
    const ov = Object.fromEntries((overrides[c.condition_id] || []).map((r) => [r[0], r.slice(1)]));
    for (let n = 1; n <= c.n; n++) {
      const [cat, attr, cause, phase] = ov[n] || [cfg.success_category, 'SUT', null, 'verification'];
      out.push({ condition_id: c.condition_id, run_id: `${c.condition_id}__${ex(n)}__A1`, execution_id: ex(n), attempt: 1, outcome_category: cat,
                 interrupted_cause: cause === undefined ? null : cause, last_phase: phase || LAST[cat], matches_expected: cat === c.expected_category, attribution: attr,
                 toolchain: { python3: '3.12.16' } });
    }
  }
  return out;
}

test('the conditions file is the locked draft: four conditions, N = 50, five categories, the expected category is the success category', () => {
  assert.equal(cfg.conditions.length, 4);
  assert.equal(cfg.n_per_condition, 50);
  assert.deepEqual(cfg.categories, ['VERIFIED', 'NOT_VERIFIED', 'ESTABLISHMENT_FAILED', 'INTERRUPTED', 'RUNNER_ERROR']);
  for (const c of cfg.conditions) { assert.equal(c.n, 50); assert.equal(c.expected_category, cfg.success_category); }
});

test('all verified: T = E = V = 50, both proportions are 1 with the Wilson lower bound about 0.929', () => {
  const r = evaluate(cfg, attemptsFor());
  assert.deepEqual(r.violations, []);
  for (const m of r.conditions) {
    assert.equal(m.T, 50); assert.equal(m.E, 50); assert.equal(m.V, 50);
    assert.equal(m.continuity_proportion_A.value, 1); near(m.continuity_proportion_A.interval.lower, 0.9285, 2e-3); assert.equal(m.continuity_proportion_A.interval.upper, 1);
    assert.equal(m.conditional_proportion_B.value, 1);
  }
});

test('option A keeps every attempt in the denominator; option B only the attempts that reached verification; counts, causes and attribution are reported beside', () => {
  const id = cfg.conditions[0].condition_id;
  const r = evaluate(cfg, attemptsFor({ [id]: [
    [1, 'NOT_VERIFIED', 'SUT', null, 'verification'], [2, 'NOT_VERIFIED', 'SUT', null, 'verification'],
    [3, 'ESTABLISHMENT_FAILED', 'SUT', null, 'establishment-check'],
    [4, 'INTERRUPTED', 'SUT', 'RESET_FAILED', 'reset'], [5, 'INTERRUPTED', 'TOOLING', 'WATCHDOG', 'verification'],
    [6, 'RUNNER_ERROR', 'TOOLING', null, 'establishment'], [7, 'RUNNER_ERROR', 'TOOLING', null, 'verification']] }));
  assert.deepEqual(r.violations, []);
  const m = r.conditions.find((x) => x.condition_id === id);
  assert.equal(m.T, 50); assert.equal(m.V, 43);
  assert.equal(m.E, 43 + 2 + 1 + 1); // VERIFIED 43, NOT_VERIFIED 2, INTERRUPTED/WATCHDOG at verification 1, RUNNER_ERROR at verification 1
  near(m.continuity_proportion_A.value, 43 / 50, 1e-12); near(m.conditional_proportion_B.value, 43 / 47, 1e-12);
  assert.equal(m.category_counts.NOT_VERIFIED, 2); assert.equal(m.category_counts.ESTABLISHMENT_FAILED, 1); assert.equal(m.category_counts.INTERRUPTED, 2); assert.equal(m.category_counts.RUNNER_ERROR, 2);
  assert.deepEqual(m.interrupted_cause_counts, { RESET_FAILED: 1, WATCHDOG: 1 });
  assert.equal(m.attribution_by_category.TOOLING.RUNNER_ERROR, 2); assert.equal(m.attribution_by_category.SUT.NOT_VERIFIED, 2); assert.equal(m.attribution_by_category.SUT.VERIFIED, 43);
});

test('an empty condition is NOT_ESTIMABLE in both proportions (never 0) and no attempt is reported by the consistency checks', () => {
  const r = evaluate(cfg, attemptsFor({}, cfg.conditions.slice(1).map((c) => c.condition_id)));
  const m = r.conditions[0];
  assert.equal(m.T, 0); assert.equal(m.continuity_proportion_A.value, 'NOT_ESTIMABLE'); assert.equal(m.continuity_proportion_A.interval, 'NOT_ESTIMABLE');
  assert.equal(m.conditional_proportion_B.value, 'NOT_ESTIMABLE');
  assert.ok(r.violations.some((v) => v.includes('no attempt record for EX0001')));
});

test('B is NOT_ESTIMABLE when no attempt reached verification, while A is a real 0', () => {
  const id = cfg.conditions[1].condition_id;
  const rows = []; for (let n = 1; n <= 50; n++) rows.push([n, 'ESTABLISHMENT_FAILED', 'SUT', null, 'establishment']);
  const m = evaluate(cfg, attemptsFor({ [id]: rows })).conditions.find((x) => x.condition_id === id);
  assert.equal(m.V, 0); assert.equal(m.E, 0); assert.equal(m.continuity_proportion_A.value, 0); assert.equal(m.conditional_proportion_B.value, 'NOT_ESTIMABLE');
});

test('violations: undeclared category, bad cause, cause on a non-interrupted category, repeated pair, wrong attempt, match flag, unknown condition, bad attribution, bad last phase', () => {
  const a = attemptsFor();
  a[0].outcome_category = 'S_SOMETHING';
  a[1].execution_id = a[2].execution_id;
  a[3].attempt = 2;
  a[4].matches_expected = false;
  a[5].attribution = 'HUMAN';
  a[6].outcome_category = 'INTERRUPTED'; a[6].interrupted_cause = 'OTHER'; a[6].matches_expected = false;
  a[7].interrupted_cause = 'WATCHDOG';
  a[8].last_phase = 'reset';
  a.push({ condition_id: 'E07-NOPE', run_id: 'x', execution_id: 'EX0001', attempt: 1, outcome_category: 'VERIFIED', interrupted_cause: null, last_phase: 'verification', matches_expected: true, attribution: null, toolchain: {} });
  const v = evaluate(cfg, a).violations.join('\n');
  for (const frag of ['is not in the declared set', 'repeated (execution_id, attempt) pair', 'is not 1', 'matches_expected', 'is not in the conditions table', 'is not TOOLING, SUT or null',
                      'INTERRUPTED with the cause', 'an interrupted cause on the category', 'with the last phase']) assert.ok(v.includes(frag), frag);
});

test('toolchain drift is reported per condition and per tool; the z of the interval is the 95 percent value; the four candidate comparisons are listed as not evaluable', () => {
  const a = attemptsFor();
  a[0].toolchain = { python3: '3.12.17' };
  const r = evaluate(cfg, a);
  assert.deepEqual(r.toolchain_drift_confounds[cfg.conditions[0].condition_id].python3, ['3.12.16', '3.12.17']);
  assert.equal(WILSON_Z, 1.959963984540054);
  assert.equal(COMPARISONS_NOT_EVALUABLE.length, 4);
  for (const c of COMPARISONS_NOT_EVALUABLE) { assert.equal(c.evaluable, false); assert.ok(c.reason.length > 0); }
});
