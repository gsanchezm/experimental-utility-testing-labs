#!/usr/bin/env node
'use strict';
/*
 * analysis/e07-continuity-analysis/compute-continuity-e07.js
 *
 * Continuity analysis of E07-cross-layer-continuity for study EUS-2026-001: the loader and command-line driver that the "Analysis and what is
 * not computed" part of the campaign configuration promises after the freeze (experiments/E07-cross-layer-continuity/README.md, "Campaign
 * configuration"). It turns the frozen bundles into attempt records and computes, per condition, T (valid measured attempts), V (VERIFIED
 * executions), E (attempts whose establishment succeeded: those that reached the verification block, last_phase 'verification'), the
 * continuity proportion V / T (option A, primary) and the conditional proportion V / E (option B, reported apart), each with the Wilson 95
 * percent interval without continuity correction, the category counts, the interrupted-cause counts and the attributed counts (TOOLING and SUT
 * per category) beside the raw rates. Descriptive only.
 *
 * Pre-registered rules applied here (none is chosen after seeing the data; decision D-E07-10, manifests/campaign-execution-decisions-v12.yaml):
 *   - Option A: V / all valid measured attempts of the condition (ESTABLISHMENT_FAILED, INTERRUPTED and RUNNER_ERROR stay in T). Option B: V / E;
 *     NOT_ESTIMABLE (never 0) when E is 0. No interval is computed for a NOT_ESTIMABLE rate.
 *   - No attempt is excluded from any denominator; no label is re-mapped; attributions are reported beside the raw rates and never change them.
 *   - Not computed, not compared, not pooled: no between-ecosystem comparison, no pooled rate across conditions, directions or ecosystems, no
 *     composite, no latency, no test, p-value, risk difference or effect size, no Holm family. The four candidate CONFIRMATORY (H4) comparisons of
 *     the configuration are listed with their reasons as not evaluable (SUT-02 and SUT-03 are NOT_COMPARABLE in the frozen mapping records); this is
 *     written from the configuration and is not derived from the data. No support or non-support criterion is frozen for H4, and none is invented.
 *
 * The Wilson interval and the toolchain drift check come from the pure core analysis/h3-analysis/h3-metrics.js, which this script requires and
 * does not modify (rate() and distinctToolchain() only).
 *
 * Fails loudly on: pins that are not set (the pins below are filled at the campaign freeze from the recorded START and freeze commits); a raw-data
 * tree that differs from the pinned tree of the freeze commit or has uncommitted changes; a Campaign configuration section that differs from the
 * pinned digest (at HEAD and at the START commit); a conditions file that differs from its pinned digest; E07 not FROZEN in the study manifest; a
 * set of run directories that is not the expected one (50 per condition of the conditions file) or a job-directory set that is not the expected
 * one; an attempt other than 1; a bundle whose directory name, run manifest and attempt record disagree (identity, scenario, layers, outcome
 * category, expected category); an attempt record whose sha256 differs from the one listed in its run manifest; a category or cause outside the
 * declared set; any violation of the consistency checks of evaluate().
 *
 * Usage: node analysis/e07-continuity-analysis/compute-continuity-e07.js [--check]    (--check recomputes and compares with the files on disk; writes nothing)
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only; no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const core = require('../h3-analysis/h3-metrics.js');

const REPO = path.resolve(__dirname, '..', '..');
const RAW = 'raw-data/E07-cross-layer-continuity';
const OUT_JSON = 'derived-data/E07-cross-layer-continuity/continuity-e07-result.json';
const OUT_CSV = 'derived-data/E07-cross-layer-continuity/outcomes-per-attempt.csv';
const README = 'experiments/E07-cross-layer-continuity/README.md';
const CONDITIONS = 'experiments/E07-cross-layer-continuity/conditions-draft.json';
// Pins: filled at the campaign freeze from the recorded START and freeze records (manifests/e07-campaign-start-v1.yaml, manifests/e07-campaign-freeze-v1.yaml).
const START_COMMIT = null;        // the E07 campaign START commit (E07-START-AUTH-01)
const FREEZE_COMMIT = null;       // the E07 campaign freeze commit (E07-FREEZE-AUTH-01)
const RAW_TREE = null;            // git tree of raw-data/E07-cross-layer-continuity at the freeze commit
const CONFIG_SHA256 = null;       // sha256 of the Campaign configuration section of the E07 README, equal at the START commit and at HEAD
const CONDITIONS_SHA256 = null;   // sha256 of the conditions file
const WILSON_Z = 1.959963984540054;   // 95 percent, the repository convention (experiments/E05-determinism/README.md, "Metrics")
const N = 50;

const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const fail = (m) => { console.error('FAIL: ' + m); process.exit(2); };
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const csvCell = (v) => {
  const s = v === null || v === undefined ? '' : typeof v === 'string' ? v : JSON.stringify(v);
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

// The four candidate CONFIRMATORY (H4) comparisons of the configuration, with the reason each is not evaluable (written from the configuration,
// campaign-configuration-draft.md section 13; the reasons are mapping decisions, not data).
const COMPARISONS_NOT_EVALUABLE = [
  { id: 'CONFIRMATORY (H4), E07-A', pair: 'SUT-01 vs SUT-02', scenario: 'CS-005 (API to WEB)', evaluable: false, reason: 'SUT-02 is NOT_COMPARABLE: no API surface (NO_APPLICABLE_SURFACE)' },
  { id: 'CONFIRMATORY (H4), E07-B', pair: 'SUT-01 vs SUT-03', scenario: 'CS-005 (API to WEB)', evaluable: false, reason: 'SUT-03 is NOT_COMPARABLE under DP-4 strict (D-E07-1): no API-established persistent state' },
  { id: 'CONFIRMATORY (H4), E07-C', pair: 'SUT-01 vs SUT-02', scenario: 'CS-006 (WEB to API)', evaluable: false, reason: 'SUT-02 is NOT_COMPARABLE: no API surface (NO_APPLICABLE_SURFACE)' },
  { id: 'CONFIRMATORY (H4), E07-D', pair: 'SUT-01 vs SUT-03', scenario: 'CS-006 (WEB to API)', evaluable: false, reason: 'SUT-03 is NOT_COMPARABLE under DP-4 strict (D-E07-1): the client-side cart never reaches the API' }
];

/** Per-condition proportions, counts and attribution table, plus the consistency violations. Pure: reads no file. */
function evaluate(cfg, attempts) {
  const declared = new Set(cfg.categories);
  const causes = new Set(cfg.interrupted_causes);
  const byCond = {};
  for (const a of attempts) (byCond[a.condition_id] = byCond[a.condition_id] || []).push(a);
  const violations = [];
  const known = new Set(cfg.conditions.map((c) => c.condition_id));
  for (const id of Object.keys(byCond)) if (!known.has(id)) violations.push(`${id}: condition is not in the conditions table`);

  const conditions = []; const drift = {};
  for (const cond of cfg.conditions) {
    const list = byCond[cond.condition_id] || [];
    const T = list.length;
    const V = list.filter((a) => a.outcome_category === cfg.success_category).length;
    const E = list.filter((a) => a.last_phase === 'verification').length;
    const counts = {};
    for (const c of cfg.categories) counts[c] = 0;
    const interruptedCauses = {};
    const attribution = { TOOLING: {}, SUT: {}, unlabeled: {} };
    const seen = new Set();
    for (const a of list) {
      if (!declared.has(a.outcome_category)) violations.push(`${cond.condition_id}: ${a.run_id}: category ${JSON.stringify(a.outcome_category)} is not in the declared set`);
      else counts[a.outcome_category] += 1;
      if (a.outcome_category === 'INTERRUPTED') {
        if (!causes.has(a.interrupted_cause)) violations.push(`${cond.condition_id}: ${a.run_id}: INTERRUPTED with the cause ${JSON.stringify(a.interrupted_cause)}, not in the declared set`);
        else interruptedCauses[a.interrupted_cause] = (interruptedCauses[a.interrupted_cause] || 0) + 1;
      } else if (a.interrupted_cause !== null && a.interrupted_cause !== undefined) {
        violations.push(`${cond.condition_id}: ${a.run_id}: an interrupted cause on the category ${a.outcome_category}`);
      }
      if (a.attribution !== null && a.attribution !== 'TOOLING' && a.attribution !== 'SUT') violations.push(`${cond.condition_id}: ${a.run_id}: attribution ${JSON.stringify(a.attribution)} is not TOOLING, SUT or null`);
      const bucket = a.attribution === 'TOOLING' ? 'TOOLING' : a.attribution === 'SUT' ? 'SUT' : 'unlabeled';
      attribution[bucket][a.outcome_category] = (attribution[bucket][a.outcome_category] || 0) + 1;
      if (a.condition_id !== cond.condition_id) violations.push(`${cond.condition_id}: attempt ${a.run_id} names condition ${a.condition_id}`);
      if (a.attempt !== 1) violations.push(`${cond.condition_id}: ${a.run_id}: attempt ${a.attempt} is not 1`);
      if (a.matches_expected !== (a.outcome_category === cond.expected_category)) violations.push(`${cond.condition_id}: ${a.run_id}: matches_expected ${a.matches_expected} disagrees with the category ${a.outcome_category}`);
      if ((a.outcome_category === 'VERIFIED' || a.outcome_category === 'NOT_VERIFIED') && a.last_phase !== 'verification') violations.push(`${cond.condition_id}: ${a.run_id}: ${a.outcome_category} with the last phase ${JSON.stringify(a.last_phase)}`);
      if (a.outcome_category === 'ESTABLISHMENT_FAILED' && a.last_phase !== 'establishment' && a.last_phase !== 'establishment-check') violations.push(`${cond.condition_id}: ${a.run_id}: ESTABLISHMENT_FAILED with the last phase ${JSON.stringify(a.last_phase)}`);
      const key = `${a.execution_id}/${a.attempt}`;
      if (seen.has(key)) violations.push(`${cond.condition_id}: repeated (execution_id, attempt) pair ${key}`);
      seen.add(key);
    }
    for (let n = 1; n <= cond.n; n += 1) if (!seen.has(`EX${String(n).padStart(4, '0')}/1`)) violations.push(`${cond.condition_id}: no attempt record for EX${String(n).padStart(4, '0')}`);
    if (cond.expected_category !== cfg.success_category) violations.push(`${cond.condition_id}: the expected category is not the success category`);
    const sum = Object.values(counts).reduce((x, y) => x + y, 0);
    if (sum !== T) violations.push(`${cond.condition_id}: the category counts sum to ${sum}, not T ${T}`);
    if (V > E || E > T) violations.push(`${cond.condition_id}: V ${V}, E ${E}, T ${T} are not ordered V <= E <= T`);
    const d = core.distinctToolchain(list);
    if (Object.keys(d).length) drift[cond.condition_id] = d;
    conditions.push({ condition_id: cond.condition_id, canonical_scenario_id: cond.canonical_scenario_id, sut_id: cond.sut_id, source_layer: cond.source_layer,
                      verification_layer: cond.verification_layer, account: cond.account, n_planned: cond.n, T, V, E,
                      continuity_proportion_A: core.rate(V, T, WILSON_Z), conditional_proportion_B: core.rate(V, E, WILSON_Z),
                      category_counts: counts, interrupted_cause_counts: interruptedCauses, attribution_by_category: attribution });
  }
  return { conditions, toolchain_drift_confounds: drift, violations };
}

function main() {
  const pins = { START_COMMIT, FREEZE_COMMIT, RAW_TREE, CONFIG_SHA256, CONDITIONS_SHA256 };
  const unset = Object.keys(pins).filter((k) => !pins[k]);
  if (unset.length) fail('pins not set (they are filled at the campaign freeze from the recorded records): ' + unset.join(', '));
  const git = (...a) => execFileSync('git', ['-C', REPO, ...a], { encoding: 'utf8' }).replace(/\n$/, '');
  // ---- pinned inputs -------------------------------------------------------------------------------------------------
  if (git('status', '--porcelain', '--', RAW)) fail('uncommitted changes under ' + RAW);
  const treeHead = git('rev-parse', 'HEAD:' + RAW);
  const treeFreeze = git('rev-parse', FREEZE_COMMIT + ':' + RAW);
  if (treeHead !== treeFreeze) fail('the raw-data tree differs from the tree of the freeze commit');
  if (treeHead !== RAW_TREE) fail('the raw-data tree is not the pinned tree ' + RAW_TREE);
  const cfgOf = (txt) => { const i = txt.indexOf('## Campaign configuration'); if (i < 0) fail('no Campaign configuration section'); return sha(Buffer.from(txt.slice(i), 'utf8')); };
  if (cfgOf(fs.readFileSync(path.join(REPO, README), 'utf8')) !== CONFIG_SHA256) fail('Campaign configuration differs from the pinned digest at HEAD');
  if (cfgOf(execFileSync('git', ['-C', REPO, 'show', START_COMMIT + ':' + README], { encoding: 'utf8' })) !== CONFIG_SHA256) fail('Campaign configuration differs from the pinned digest at the START commit');
  const condBuf = fs.readFileSync(path.join(REPO, CONDITIONS));
  if (sha(condBuf) !== CONDITIONS_SHA256) fail('the conditions file differs from its pinned digest');
  if (git('status', '--porcelain', '--', CONDITIONS, 'analysis/h3-analysis/h3-metrics.js')) fail('uncommitted changes in the conditions file or the pure core');
  const manifestStatus = fs.readFileSync(path.join(REPO, 'manifests/study-manifest.yaml'), 'utf8').match(/- id: E07-cross-layer-continuity\n\s+status: (\w+)/);
  if (!manifestStatus || manifestStatus[1] !== 'FROZEN') fail('E07 is not FROZEN in the study manifest');

  const cfg = JSON.parse(condBuf.toString('utf8'));
  if (cfg.n_per_condition !== N || !cfg.conditions.length || cfg.conditions.some((c) => c.n !== N)) fail('the conditions file is not the locked one (N = 50 per condition)');
  const SUT_DIRS = Array.from(new Set(cfg.conditions.map((c) => c.sut_id))).sort();

  // ---- the bundles and the job directories ---------------------------------------------------------------------------------
  const present = fs.readdirSync(path.join(REPO, RAW)).filter((d) => !d.startsWith('.')).sort();
  if (JSON.stringify(present) !== JSON.stringify(SUT_DIRS)) fail('the SUT directories are not ' + SUT_DIRS.join(', '));
  const expectedRuns = []; const expectedJobs = [];
  for (const c of cfg.conditions) {
    expectedJobs.push(`${c.sut_id}/${c.condition_id}__job__A1`);
    for (let n = 1; n <= N; n++) expectedRuns.push(`${c.sut_id}/${c.condition_id}__EX${String(n).padStart(4, '0')}__A1`);
  }
  const foundRuns = []; const foundJobs = [];
  for (const sut of SUT_DIRS) {
    for (const d of fs.readdirSync(path.join(REPO, RAW, sut)).filter((x) => !x.startsWith('.')).sort()) {
      (/__job__A\d+$/.test(d) ? foundJobs : foundRuns).push(`${sut}/${d}`);
    }
  }
  if (JSON.stringify([...foundRuns].sort()) !== JSON.stringify([...expectedRuns].sort())) fail(`the set of run directories is not the ${expectedRuns.length} expected`);
  if (JSON.stringify([...foundJobs].sort()) !== JSON.stringify([...expectedJobs].sort())) fail(`the set of job directories is not the ${expectedJobs.length} expected`);

  const attempts = []; const rows = []; let filesRead = 0;
  for (const c of cfg.conditions) {
    for (let n = 1; n <= N; n++) {
      const ex = `EX${String(n).padStart(4, '0')}`;
      const d = `${c.condition_id}__${ex}__A1`;
      const base = path.join(REPO, RAW, c.sut_id, d);
      const man = readJson(path.join(base, 'run-manifest.json'));
      const recBuf = fs.readFileSync(path.join(base, 'attempt-record.json'));
      const rec = JSON.parse(recBuf.toString('utf8'));
      filesRead += 2;
      if (man.run_id !== d || man.condition !== c.condition_id || man.campaign_id !== 'E07-cross-layer-continuity' || man.sut_id !== c.sut_id || man.attempt !== 1) fail(d + ': identity fields of the run manifest disagree');
      if (rec.run_id !== d || rec.condition !== c.condition_id || rec.execution_id !== ex || rec.attempt !== 1) fail(d + ': identity fields of the attempt record disagree');
      if (rec.record_class !== 'MEASURED_EXPERIMENT') fail(d + ': the attempt record is not a MEASURED_EXPERIMENT record');
      if (man.scenario !== c.canonical_scenario_id || rec.scenario !== c.canonical_scenario_id) fail(d + ': the scenario of the run manifest or of the attempt record is not the one of the conditions file');
      if (man.source_layer !== c.source_layer || man.verification_layer !== c.verification_layer || rec.source_layer !== c.source_layer || rec.verification_layer !== c.verification_layer) fail(d + ': the layers of the run manifest or of the attempt record are not the ones of the conditions file');
      const listed = (man.artifacts || []).find((a) => a.path === `${RAW}/${c.sut_id}/${d}/attempt-record.json`);
      if (!listed || listed.sha256 !== sha(recBuf)) fail(d + ': the attempt record is not the one listed in the run manifest');
      if (!man.outcome || man.outcome.outcome_category !== rec.outcome_category) fail(d + ': the outcome category of the run manifest and of the attempt record disagree');
      if (man.outcome.expected !== c.expected_category) fail(d + ': the expected category of the run manifest is not the one of the conditions file');
      if (typeof man.outcome.matches_expected !== 'boolean') fail(d + ': matches_expected is not a boolean');
      const attribution = rec.attribution === undefined ? null : rec.attribution;
      const cause = rec.interrupted_cause === undefined ? null : rec.interrupted_cause;
      attempts.push({ condition_id: c.condition_id, run_id: d, execution_id: ex, attempt: 1, outcome_category: rec.outcome_category, interrupted_cause: cause,
                      last_phase: rec.last_phase, matches_expected: man.outcome.matches_expected, attribution, toolchain: man.toolchain });
      rows.push({ run_id: d, condition_id: c.condition_id, sut_id: c.sut_id, canonical_scenario_id: c.canonical_scenario_id, source_layer: c.source_layer,
                  verification_layer: c.verification_layer, execution_id: ex, attempt: 1, outcome_category: rec.outcome_category, interrupted_cause: cause,
                  expected_category: c.expected_category, matches_expected: man.outcome.matches_expected, attribution, workflow_outcome_status: man.outcome.status,
                  last_phase: rec.last_phase, cause: rec.cause });
    }
  }

  const evaluated = evaluate(cfg, attempts);
  if (evaluated.violations.length) { console.error(evaluated.violations.join('\n')); fail(evaluated.violations.length + ' consistency violation(s)'); }
  const conditions = evaluated.conditions;
  const result = {
    record: 'Continuity analysis, E07-cross-layer-continuity (derived dataset; descriptive; produced by analysis/e07-continuity-analysis/compute-continuity-e07.js from the frozen raw-data/E07-cross-layer-continuity)',
    campaign_id: 'E07-cross-layer-continuity',
    hypothesis_note: 'H4, continuity part: no CONFIRMATORY comparison is evaluable (SUT-02 and SUT-03 are NOT_COMPARABLE in the frozen mapping records), so this dataset evaluates no hypothesis; every figure is descriptive, and the SUT-04 conditions are a specialist reference (EXPLORATORY).',
    metric_source: 'experiments/E07-cross-layer-continuity/README.md, "Campaign configuration", "Blocks, outcome categories and the continuity proportion" and "Analysis and what is not computed"; manifests/campaign-execution-decisions-v12.yaml (D-E07-10)',
    estimators: { continuity_proportion_A: 'V / T: VERIFIED executions over every valid measured attempt of the condition (ESTABLISHMENT_FAILED, INTERRUPTED and RUNNER_ERROR stay in T)',
                  conditional_proportion_B: 'V / E: VERIFIED executions over the attempts whose establishment succeeded (those that reached the verification block, last_phase verification)',
                  interval: 'Wilson score interval without continuity correction, z = ' + WILSON_Z, NOT_ESTIMABLE: 'the rate of an empty denominator; never reported as 0' },
    inputs: { raw_tree: RAW, raw_git_tree: treeHead, pinned_at_commit: FREEZE_COMMIT, campaign_state: 'FROZEN', bundles: rows.length, job_directories_ignored: foundJobs.length,
              conditions_file: CONDITIONS, conditions_file_sha256: CONDITIONS_SHA256, campaign_configuration_sha256: CONFIG_SHA256 },
    totals: { conditions: conditions.length, attempts_T: conditions.reduce((a, x) => a + x.T, 0), attempts_verified_V: conditions.reduce((a, x) => a + x.V, 0),
              note: 'counts of attempts only; no pooling of rates across conditions, directions or ecosystems is computed' },
    conditions,
    cells_without_condition: cfg.no_condition,
    comparisons_not_evaluable: COMPARISONS_NOT_EVALUABLE,
    toolchain_drift_confounds: evaluated.toolchain_drift_confounds,
    consistency_violations: evaluated.violations,
    not_computed: 'No between-ecosystem comparison, pooled rate, composite score, latency, test, p-value, risk difference, effect size, Holm family or ranking: none is frozen for E07, and the configuration lists them as not computed.'
  };
  const jsonText = JSON.stringify(result, null, 2) + '\n';
  const header = ['run_id', 'condition_id', 'sut_id', 'canonical_scenario_id', 'source_layer', 'verification_layer', 'execution_id', 'attempt', 'outcome_category', 'interrupted_cause',
                  'expected_category', 'matches_expected', 'attribution', 'workflow_outcome_status', 'last_phase', 'cause'];
  const csvText = header.join(',') + '\n' + rows.map((r) => header.map((h) => csvCell(r[h])).join(',')).join('\n') + '\n';

  if (process.argv.includes('--check')) {
    const same = (p, text) => fs.existsSync(path.join(REPO, p)) && fs.readFileSync(path.join(REPO, p), 'utf8') === text;
    const ok = same(OUT_JSON, jsonText) && same(OUT_CSV, csvText);
    console.log(ok ? 'CHECK OK: the files on disk equal the recomputation' : 'CHECK FAILED: the files on disk differ from the recomputation');
    process.exit(ok ? 0 : 3);
  }
  fs.mkdirSync(path.dirname(path.join(REPO, OUT_JSON)), { recursive: true });
  fs.writeFileSync(path.join(REPO, OUT_JSON), jsonText);
  fs.writeFileSync(path.join(REPO, OUT_CSV), csvText);
  console.log(`wrote ${OUT_JSON} (sha256 ${sha(Buffer.from(jsonText))}) and ${OUT_CSV} (sha256 ${sha(Buffer.from(csvText))}); bundles ${rows.length}, files read ${filesRead}`);
  console.log(`conditions ${conditions.length}: T ${result.totals.attempts_T}, V ${result.totals.attempts_verified_V}; violations ${evaluated.violations.length}`);
}

module.exports = { evaluate, WILSON_Z, COMPARISONS_NOT_EVALUABLE };
if (require.main === module) main();
