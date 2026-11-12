'use strict';
/*
 * analysis/h3-analysis/h3-metrics.js -- the pure core of the E05 analysis (H3), DRAFT (operation OP-DISP-07, 2026-11-12).
 *
 * Implements the metric specification of experiments/E05-determinism/design-brief-draft.md, section 5 (TSRR, CEOR, E2E-ROR,
 * H(Y), Wilson intervals, NOT_ESTIMABLE, the H3 rule, the consistency checks), with the decisions of
 * manifests/campaign-execution-decisions-v4.yaml, -v5.yaml and -v6.yaml: D-05 Wilson without continuity correction; D-06 a
 * deterministic condition is evaluable for H3 only when S >= min_s_for_h3 (45 of N = 50); D-07 CEOR of stochastic and external
 * conditions is descriptive; D-09 a no-bundle attempt is an interrupted attempt in T that is never in S; D-16 option B and D-16b
 * (a TOOLING interruption after establishment is an INTERRUPTED_ category in S, reported with its label); D-19 identifiers.
 *
 * It reads no file and no raw data: it takes the conditions table (experiments/E05-determinism/conditions-draft.json, locked with
 * the configuration at START) and an array of normalized attempt records, and returns a result object. A separate loader (written
 * after the campaign configuration is locked, with the pinned raw-data tree) turns bundles into attempt records. No random number
 * is used anywhere (no bootstrap, so no seed). Standard library only; no third-party dependency.
 *
 * Attempt record: { condition_id, run_id, execution_id, attempt, outcome_category, matches_expected, attribution, behavior_class, toolchain }
 *   attribution: 'TOOLING', 'SUT' or null. toolchain: an object of tool -> version strings (drift check).
 * Phase of an attempt, from its outcome_category: 'S' (S_ and INTERRUPTED_: inside S, the TSRR numerator and the CEOR denominator)
 * or 'PRE' (RESET_, ESTABLISHMENT_, STUB_: T only). A label of neither kind is reported by the consistency checks.
 */

const NOT_ESTIMABLE = 'NOT_ESTIMABLE';
const EXEC_ID = /^EX(\d{4})$/;

function phaseOf(category) {
  if (typeof category !== 'string') return 'UNKNOWN';
  if (category === 'INTERRUPTED_' || category.startsWith('S_')) return 'S';
  if (category.startsWith('RESET_') || category.startsWith('ESTABLISHMENT_') || category.startsWith('STUB_')) return 'PRE';
  return 'UNKNOWN';
}

/** Wilson score interval for x successes of n (n >= 1), no continuity correction (D-05). */
function wilson(x, n, z) {
  if (!(n >= 1)) return NOT_ESTIMABLE;
  const p = x / n;
  const z2 = z * z;
  const denom = 1 + z2 / n;
  const centre = (p + z2 / (2 * n)) / denom;
  const half = (z * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n))) / denom;
  return { lower: Math.max(0, centre - half), upper: Math.min(1, centre + half) };
}

/** Shannon entropy in bits of the counts (terms with a zero count contribute 0). */
function entropy(counts) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  if (total < 1) return NOT_ESTIMABLE;
  let h = 0;
  for (const c of Object.values(counts)) {
    if (c > 0) h -= (c / total) * Math.log2(c / total);
  }
  return h === 0 ? 0 : h;
}

function rate(x, n, z) {
  if (!(n >= 1)) return { value: NOT_ESTIMABLE, x, n, interval: NOT_ESTIMABLE };
  return { value: x / n, x, n, interval: wilson(x, n, z) };
}

/** Metrics, the H3 evaluation and the attribution table of one condition. */
function conditionMetrics(cond, attempts, cfg) {
  const z = cfg.wilson_z;
  const T = attempts.length;
  const inS = attempts.filter((a) => phaseOf(a.outcome_category) === 'S');
  const S = inS.length;
  const M = inS.filter((a) => a.outcome_category === cond.expected_category).length;
  const counts = {};
  for (const c of cond.stimulus_categories) counts[c] = 0;
  for (const a of inS) counts[a.outcome_category] = (counts[a.outcome_category] || 0) + 1;
  const H = entropy(counts);
  const tsrr = rate(S, T, z);
  const ceor = rate(M, S, z);
  const e2e = rate(M, T, z);
  const unexpected = S - M;

  let h3;
  if (!cond.h3_labeled) {
    h3 = { label: cond.behavior_class === 'deterministic' ? 'DESCRIPTIVE' : 'NOT_H3', status: null,
           note: cond.behavior_class === 'deterministic' ? 'deterministic condition of an ecosystem other than SUT-01: the metrics are computed identically and stay descriptive' : 'ceor is descriptive for this class (D-07)' };
  } else if (S === 0 || S < cfg.min_s_for_h3) {
    h3 = { label: 'H3', status: 'NOT_EVALUABLE', reason: S === 0 ? 'S = 0' : `S = ${S} is below the minimum ${cfg.min_s_for_h3} (D-06)`, unexpected_in_S: unexpected };
  } else if (unexpected > 0) {
    h3 = { label: 'H3', status: 'FALSIFIED', unexpected_in_S: unexpected };
  } else {
    h3 = { label: 'H3', status: 'SATISFIED', unexpected_in_S: 0,
           note: 'no unexpected outcome in S executions; not a proof of determinism: the probability that all S attempts match is q^S for a per-attempt match probability q' };
  }

  // Secondary table (D-16): the TOOLING- and SUT-labeled counts per category inside S; the primary rates above count every attempt.
  const attribution = { TOOLING: {}, SUT: {}, unlabeled: {} };
  for (const a of inS) {
    const bucket = a.attribution === 'TOOLING' ? 'TOOLING' : a.attribution === 'SUT' ? 'SUT' : 'unlabeled';
    attribution[bucket][a.outcome_category] = (attribution[bucket][a.outcome_category] || 0) + 1;
  }
  const preStages = {};
  for (const a of attempts) if (phaseOf(a.outcome_category) === 'PRE') preStages[a.outcome_category] = (preStages[a.outcome_category] || 0) + 1;

  return { condition_id: cond.condition_id, behavior_class: cond.behavior_class, k: cond.k, expected_category: cond.expected_category,
           T, S, M, category_counts_in_S: counts, pre_stage_counts: preStages,
           TSRR: tsrr, CEOR: ceor, E2E_ROR: e2e,
           H_Y: { value: H, k: cond.k, max: Math.log2(cond.k), n: S },
           h3, attribution_in_S: attribution, nominal_stimulus: !!cond.nominal_stimulus };
}

function distinctToolchain(attempts) {
  const tools = {};
  for (const a of attempts) {
    for (const [tool, value] of Object.entries(a.toolchain || {})) {
      (tools[tool] = tools[tool] || new Set()).add(typeof value === 'string' ? value : JSON.stringify(value));
    }
  }
  const drift = {};
  for (const [tool, set] of Object.entries(tools)) if (set.size > 1) drift[tool] = Array.from(set).sort();
  return drift;
}

/** Fail-closed consistency checks of the brief, section 5.7. Returns an array of violation strings (empty when consistent). */
function consistencyChecks(cfg, conditionsById, attemptsByCondition, metricsById) {
  const v = [];
  const declaredAll = new Set(cfg.non_stimulus_categories);
  for (const id of Object.keys(attemptsByCondition)) {
    const cond = conditionsById[id];
    if (!cond) { v.push(`${id}: condition is not in the conditions table`); continue; }
    if (!cfg.schema_class_values.includes(cond.behavior_class)) v.push(`${id}: behavior_class ${JSON.stringify(cond.behavior_class)} is not one of the schema values`);
    const declared = new Set([...cond.stimulus_categories, ...declaredAll]);
    const seen = new Set();
    const byExec = {};
    for (const a of attemptsByCondition[id]) {
      if (a.condition_id !== id) v.push(`${id}: attempt ${a.run_id} names condition ${a.condition_id}`);
      if (!declared.has(a.outcome_category)) v.push(`${id}: ${a.run_id}: label ${JSON.stringify(a.outcome_category)} is not in the declared set`);
      const m = EXEC_ID.exec(a.execution_id || '');
      if (!m) v.push(`${id}: ${a.run_id}: execution_id ${JSON.stringify(a.execution_id)} is not EXnnnn`);
      else if (Number(m[1]) < 1 || Number(m[1]) > cond.n) v.push(`${id}: ${a.run_id}: execution_id ${a.execution_id} is outside EX0001..EX${String(cond.n).padStart(4, '0')}`);
      const key = `${a.execution_id}/${a.attempt}`;
      if (seen.has(key)) v.push(`${id}: repeated (execution_id, attempt) pair ${key}`);
      seen.add(key);
      (byExec[a.execution_id] = byExec[a.execution_id] || []).push(a.attempt);
      if (phaseOf(a.outcome_category) === 'S' && typeof a.matches_expected === 'boolean' && a.matches_expected !== (a.outcome_category === cond.expected_category)) {
        v.push(`${id}: ${a.run_id}: matches_expected ${a.matches_expected} disagrees with the category ${a.outcome_category}`);
      }
    }
    for (const [ex, idx] of Object.entries(byExec)) {
      const sorted = idx.slice().sort((a, b) => a - b);
      sorted.forEach((n, i) => { if (n !== i + 1) v.push(`${id}: ${ex}: attempt indices ${JSON.stringify(sorted)} have a gap or do not start at 1`); });
    }
    for (let n = 1; n <= cond.n; n += 1) {
      const ex = `EX${String(n).padStart(4, '0')}`;
      if (!byExec[ex]) v.push(`${id}: no attempt record for ${ex}`);
    }
    const m = metricsById[id];
    if (m.S > m.T) v.push(`${id}: S ${m.S} exceeds T ${m.T}`);
    if (m.M > m.S) v.push(`${id}: M ${m.M} exceeds S ${m.S}`);
    const sum = Object.values(m.category_counts_in_S).reduce((x, y) => x + y, 0);
    if (sum !== m.S) v.push(`${id}: the category counts sum to ${sum}, not S ${m.S}`);
    if (m.S >= 1 && m.T >= 1 && Math.abs(m.E2E_ROR.value - m.TSRR.value * m.CEOR.value) > 1e-12) v.push(`${id}: E2E-ROR differs from TSRR x CEOR`);
    if (m.h3.status === 'SATISFIED' && m.H_Y.value !== 0) v.push(`${id}: H3 is satisfied but H(Y) is ${m.H_Y.value}, not 0`);
  }
  return v;
}

/** Evaluate every condition of the table against the attempt records. */
function evaluate(cfg, attempts) {
  const conditionsById = Object.fromEntries(cfg.conditions.map((c) => [c.condition_id, c]));
  const byCond = {};
  for (const a of attempts) (byCond[a.condition_id] = byCond[a.condition_id] || []).push(a);
  const metricsById = {};
  const drift = {};
  for (const cond of cfg.conditions) {
    const list = byCond[cond.condition_id] || [];
    metricsById[cond.condition_id] = conditionMetrics(cond, list, cfg);
    const d = distinctToolchain(list);
    if (Object.keys(d).length) drift[cond.condition_id] = d;
  }
  const violations = consistencyChecks(cfg, conditionsById, byCond, metricsById);
  return { conditions: cfg.conditions.map((c) => metricsById[c.condition_id]), toolchain_drift_confounds: drift, violations };
}

module.exports = { NOT_ESTIMABLE, phaseOf, wilson, entropy, rate, conditionMetrics, distinctToolchain, consistencyChecks, evaluate };
