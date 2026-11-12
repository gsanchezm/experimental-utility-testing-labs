'use strict';
// Unit tests of analysis/h3-analysis/h3-metrics.js on synthetic attempt records (no raw data, no SUT). Run: node --test analysis/h3-analysis/test
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const m = require('../h3-metrics.js');

const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'experiments', 'E05-determinism', 'conditions-draft.json'), 'utf8'));
const byId = (id) => cfg.conditions.find((c) => c.condition_id === id);
const near = (a, b, tol = 1e-3) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);

function attempts(condId, specs) {
  // specs: array of [category, extra]; execution EX0001.. in order, attempt 1
  return specs.map(([category, extra], i) => Object.assign({
    condition_id: condId, run_id: `${condId}__EX${String(i + 1).padStart(4, '0')}__A1`, execution_id: `EX${String(i + 1).padStart(4, '0')}`,
    attempt: 1, outcome_category: category, matches_expected: null, attribution: null, toolchain: { chromium: '153.0.8010.12' } }, extra || {}));
}
function repeat(cat, n, extra) { return Array.from({ length: n }, () => [cat, extra]); }

test('wilson without continuity correction matches reference values', () => {
  const w = m.wilson(5, 10, cfg.wilson_z); near(w.lower, 0.2366); near(w.upper, 0.7634);
  const a = m.wilson(10, 10, cfg.wilson_z); near(a.lower, 0.7225); near(a.upper, 1);
  const b = m.wilson(0, 10, cfg.wilson_z); near(b.lower, 0); near(b.upper, 0.2775);
  assert.equal(m.wilson(0, 0, cfg.wilson_z), m.NOT_ESTIMABLE);
});

test('entropy: uniform over 4 is 2 bits, a single category is 0, empty is NOT_ESTIMABLE', () => {
  assert.equal(m.entropy({ a: 3, b: 3, c: 3, d: 3 }), 2);
  assert.equal(m.entropy({ a: 7, b: 0 }), 0);
  assert.equal(m.entropy({ a: 0 }), m.NOT_ESTIMABLE);
});

test('a clean deterministic SUT-01 condition: 50 matching attempts satisfy H3', () => {
  const id = 'E05-SUT01-API-02';
  const r = m.evaluate(cfg, attempts(id, repeat('S_CATALOG_MATCH', 50)));
  const c = r.conditions.find((x) => x.condition_id === id);
  assert.equal(c.T, 50); assert.equal(c.S, 50); assert.equal(c.M, 50);
  assert.equal(c.TSRR.value, 1); assert.equal(c.CEOR.value, 1); assert.equal(c.E2E_ROR.value, 1);
  assert.equal(c.H_Y.value, 0); assert.equal(c.H_Y.k, 4);
  assert.equal(c.h3.status, 'SATISFIED'); assert.equal(c.nominal_stimulus, true);
  assert.deepEqual(r.violations.filter((v) => v.startsWith(id)), []);
});

test('three failed starting states and two no-bundle attempts (S = 45) keep H3 evaluable at the minimum; the rates count every attempt', () => {
  const id = 'E05-SUT01-API-02';
  const specs = [...repeat('S_CATALOG_MATCH', 45), ...repeat('RESET_STARTING_STATE_NOT_REACHED', 3), ...repeat('STUB_NO_BUNDLE', 2)];
  const c = m.evaluate(cfg, attempts(id, specs)).conditions.find((x) => x.condition_id === id);
  assert.equal(c.T, 50); assert.equal(c.S, 45); near(c.TSRR.value, 0.9); assert.equal(c.CEOR.value, 1); near(c.E2E_ROR.value, 0.9);
  assert.equal(c.h3.status, 'SATISFIED');
  assert.deepEqual(c.pre_stage_counts, { RESET_STARTING_STATE_NOT_REACHED: 3, STUB_NO_BUNDLE: 2 });
});

test('S = 44 is below the minimum: not evaluable, with the reason (D-06)', () => {
  const id = 'E05-SUT01-API-02';
  const specs = [...repeat('S_CATALOG_MATCH', 44), ...repeat('ESTABLISHMENT_FAILED', 6)];
  const c = m.evaluate(cfg, attempts(id, specs)).conditions.find((x) => x.condition_id === id);
  assert.equal(c.h3.status, 'NOT_EVALUABLE'); assert.match(c.h3.reason, /below the minimum 45/);
});

test('one unexpected category in S falsifies H3 and makes H(Y) positive', () => {
  const id = 'E05-SUT01-API-02';
  const specs = [...repeat('S_CATALOG_MATCH', 49), ['S_CATALOG_MISMATCH']];
  const c = m.evaluate(cfg, attempts(id, specs)).conditions.find((x) => x.condition_id === id);
  assert.equal(c.h3.status, 'FALSIFIED'); assert.equal(c.h3.unexpected_in_S, 1); assert.ok(c.H_Y.value > 0); near(c.CEOR.value, 0.98);
});

test('D-16b: a TOOLING interruption after establishment is an INTERRUPTED_ category in S, falsifies H3, and is reported with its label while the raw rates count it', () => {
  const id = 'E05-SUT01-API-02';
  const specs = [...repeat('S_CATALOG_MATCH', 49), ['INTERRUPTED_', { attribution: 'TOOLING' }]];
  const c = m.evaluate(cfg, attempts(id, specs)).conditions.find((x) => x.condition_id === id);
  assert.equal(c.S, 50); assert.equal(c.M, 49); assert.equal(c.h3.status, 'FALSIFIED');
  assert.deepEqual(c.attribution_in_S.TOOLING, { INTERRUPTED_: 1 }); assert.equal(c.attribution_in_S.SUT.INTERRUPTED_, undefined);
  near(c.CEOR.value, 0.98);
});

test('S = 0: CEOR and H(Y) are NOT_ESTIMABLE, TSRR and E2E-ROR are 0', () => {
  const id = 'E05-SUT01-API-02';
  const c = m.evaluate(cfg, attempts(id, repeat('ESTABLISHMENT_FAILED', 50))).conditions.find((x) => x.condition_id === id);
  assert.equal(c.CEOR.value, m.NOT_ESTIMABLE); assert.equal(c.H_Y.value, m.NOT_ESTIMABLE); assert.equal(c.CEOR.interval, m.NOT_ESTIMABLE);
  assert.equal(c.TSRR.value, 0); assert.equal(c.E2E_ROR.value, 0); assert.equal(c.h3.status, 'NOT_EVALUABLE');
});

test('no attempt records at all: T = 0, every rate is NOT_ESTIMABLE', () => {
  const c = m.evaluate(cfg, []).conditions[0];
  assert.equal(c.T, 0); assert.equal(c.TSRR.value, m.NOT_ESTIMABLE); assert.equal(c.E2E_ROR.value, m.NOT_ESTIMABLE);
});

test('a stochastic condition carries no H3 label; its H(Y) is the descriptive measure', () => {
  const id = 'E05-SUT01-API-05';
  const specs = [...repeat('S_MODE_MISSING_NAME', 17), ...repeat('S_MODE_WRONG_LANG', 17), ...repeat('S_MODE_EXTREME_TEXT', 16)];
  const c = m.evaluate(cfg, attempts(id, specs)).conditions.find((x) => x.condition_id === id);
  assert.equal(c.h3.label, 'NOT_H3'); near(c.H_Y.value, 1.5846, 1e-3); near(c.H_Y.max, Math.log2(5)); assert.equal(c.k, 5);
});

test('a deterministic condition of another ecosystem is descriptive, with the same metrics', () => {
  const id = 'E05-SUT04-API-01';
  const c = m.evaluate(cfg, attempts(id, repeat('S_CONFLICT_REJECTED', 50))).conditions.find((x) => x.condition_id === id);
  assert.equal(c.h3.label, 'DESCRIPTIVE'); assert.equal(c.CEOR.value, 1);
});

test('consistency checks: unknown label, repeated pair, attempt gap, execution id out of range, matches_expected disagreement, missing execution', () => {
  const id = 'E05-SUT01-API-02';
  const good = attempts(id, repeat('S_CATALOG_MATCH', 50));
  const bad = good.slice();
  bad[0] = Object.assign({}, bad[0], { outcome_category: 'S_WHAT' });
  bad[1] = Object.assign({}, bad[1], { execution_id: 'EX0007' });            // repeated (EX0007, 1); EX0002 is missing
  bad[2] = Object.assign({}, bad[2], { attempt: 3 });                          // EX0003 has only attempt 3: a gap
  bad[3] = Object.assign({}, bad[3], { execution_id: 'EX0099' });             // out of range
  bad[4] = Object.assign({}, bad[4], { matches_expected: false });            // disagrees with S_CATALOG_MATCH
  const v = m.evaluate(cfg, bad).violations.filter((x) => x.startsWith(id));
  for (const needle of ['not in the declared set', 'repeated (execution_id, attempt) pair', 'have a gap', 'outside EX0001', 'disagrees with the category', 'no attempt record for EX0002']) {
    assert.ok(v.some((x) => x.includes(needle)), `${needle} not reported in ${JSON.stringify(v)}`);
  }
});

test('a record of an unknown condition is reported', () => {
  const r = m.evaluate(cfg, [{ condition_id: 'E05-NOPE', run_id: 'x', execution_id: 'EX0001', attempt: 1, outcome_category: 'S_X' }]);
  assert.ok(r.violations.some((x) => x.includes('not in the conditions table')));
});

test('toolchain drift inside one condition is reported as a confound, never excluded', () => {
  const id = 'E05-SUT01-API-02';
  const list = attempts(id, repeat('S_CATALOG_MATCH', 50));
  list[10].toolchain = { chromium: '154.0.0.0' };
  const r = m.evaluate(cfg, list);
  assert.deepEqual(r.toolchain_drift_confounds[id], { chromium: ['153.0.8010.12', '154.0.0.0'] });
  assert.equal(r.conditions.find((x) => x.condition_id === id).T, 50);
});

test('the conditions table is internally consistent', () => {
  assert.equal(cfg.conditions.length, 14); assert.equal(cfg.min_s_for_h3, 45);
  for (const c of cfg.conditions) {
    assert.ok(cfg.schema_class_values.includes(c.behavior_class), c.condition_id);
    assert.ok(c.stimulus_categories.includes(c.expected_category), c.condition_id);
    assert.ok(c.stimulus_categories.includes('INTERRUPTED_'), c.condition_id);
    assert.equal(c.k, c.stimulus_categories.length, c.condition_id);
    assert.equal(new Set(c.stimulus_categories).size, c.k, c.condition_id);
    for (const cat of c.stimulus_categories) assert.equal(m.phaseOf(cat), 'S', `${c.condition_id} ${cat}`);
    assert.equal(c.h3_labeled, c.sut_id === 'SUT-01' && c.behavior_class === 'deterministic', c.condition_id);
  }
  for (const cat of cfg.non_stimulus_categories) assert.equal(m.phaseOf(cat), 'PRE', cat);
  assert.equal(cfg.conditions.filter((c) => c.behavior_class === 'deterministic').length, 9);
  assert.equal(cfg.conditions.filter((c) => c.h3_labeled).length, 5);
});
