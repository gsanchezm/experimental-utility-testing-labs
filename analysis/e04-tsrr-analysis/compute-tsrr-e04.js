#!/usr/bin/env node
'use strict';
/*
 * analysis/e04-tsrr-analysis/compute-tsrr-e04.js
 *
 * TSRR analysis of E04-repeatability for study EUS-2026-001 (campaign FROZEN, 650 imported bundles of 13 conditions). It is the
 * loader and command-line driver that the "Analysis (TSRR) and what is not computed" part of the campaign configuration promised
 * after the freeze (experiments/E04-repeatability/README.md, "Campaign configuration"): it turns the bundles into attempt records,
 * computes per condition T (valid measured attempts), S (TARGET_STATE_VERIFIED executions), TSRR = S / T with the Wilson 95 percent
 * interval without continuity correction, the category counts and the attributed counts (TOOLING and SUT per category) beside the
 * raw rate, and writes the result and a per-attempt table. Descriptive only.
 *
 * Pre-registered rules applied here (none is chosen after seeing the data):
 *   - TSRR = successful target-state establishments / all valid measured attempts (protocol/repeatability-determinism-v1.md,
 *     section 4); the numerator is the executions with the category TARGET_STATE_VERIFIED; the denominator is every valid measured
 *     attempt of the condition, including the ABORTED, ERROR and interrupted ones. An empty denominator gives NOT_ESTIMABLE, never 0.
 *   - No attempt is excluded from any denominator; no label is re-mapped (the category recorded by the executor is the one analyzed);
 *     TOOLING and SUT attributions are reported beside the raw TSRR and never change it.
 *   - Not computed, not compared, not pooled: no between-ecosystem comparison; no pooled rate across conditions or ecosystems; no
 *     composite score; no CEOR; no E2E-ROR; no Outcome Entropy; no H3 evaluation (H3 is an E05 hypothesis, and the E04 configuration
 *     attaches no hypothesis label). No test, p-value, effect size or ranking.
 *
 * The Wilson interval and the toolchain drift check come from the pure core analysis/h3-analysis/h3-metrics.js, which this script
 * requires and does not modify (rate() and distinctToolchain() only).
 *
 * Fails loudly on: a raw-data tree that differs from the pinned tree of the freeze commit or has uncommitted changes; a Campaign
 * configuration section that differs from the pinned digest (at HEAD and at the START commit); a conditions file that differs from
 * its pinned digest; E04 not FROZEN in the study manifest; a set of run directories that is not the 650 expected, or a job directory
 * set that is not the 13 expected; an attempt other than 1; a bundle whose directory name, run manifest and attempt record disagree
 * (identity, outcome category, expected category); an attempt record whose sha256 differs from the one listed in its run manifest;
 * a category outside the declared set; a recorded match flag that disagrees with the category; any violation of the consistency
 * checks below.
 *
 * Usage: node analysis/e04-tsrr-analysis/compute-tsrr-e04.js [--check]    (--check recomputes and compares with the files on disk; writes nothing)
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only; no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const core = require('../h3-analysis/h3-metrics.js');

const REPO = path.resolve(__dirname, '..', '..');
const RAW = 'raw-data/E04-repeatability';
const OUT_JSON = 'derived-data/E04-repeatability/TSRR-e04-result.json';
const OUT_CSV = 'derived-data/E04-repeatability/outcomes-per-attempt.csv';
const README = 'experiments/E04-repeatability/README.md';
const CONDITIONS = 'experiments/E04-repeatability/conditions-draft.json';
const START_COMMIT = '432b249688e177c95195593392a5e355e5b17002';                  // the E04 campaign START commit (E04-START-AUTH-01)
const FREEZE_COMMIT = '37fa93681e143f7ed575715727179b5e2749a338';                 // the E04 campaign freeze commit (E04-FREEZE-AUTH-01)
const RAW_TREE = '47dbb1dde7b0c429239517f174a698c3844f36a6';                      // git tree of raw-data/E04-repeatability at the freeze commit
const CONFIG_SHA256 = '8ebeb056e3c3fefc1e4d24252cd7bc6306d5880e552b9dec3171628d56b88344';
const CONDITIONS_SHA256 = '5964b23592174ce4fe3dea76c446db7eb3239afa1fef04875cb8dcfb3939d562';
const WILSON_Z = 1.959963984540054;                                               // 95 percent, the repository convention (experiments/E05-determinism/README.md, "Metrics")
const SUT_DIRS = ['SUT-01', 'SUT-02', 'SUT-04', 'SUT-05'];
const N = 50;

const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const fail = (m) => { console.error('FAIL: ' + m); process.exit(2); };
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const csvCell = (v) => {
  const s = v === null || v === undefined ? '' : typeof v === 'string' ? v : JSON.stringify(v);
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

/** Per-condition TSRR, counts and attribution table, plus the consistency violations. Pure: reads no file. */
function evaluate(cfg, attempts) {
  const declared = new Set([cfg.success_category, ...cfg.failure_categories]);
  const byCond = {};
  for (const a of attempts) (byCond[a.condition_id] = byCond[a.condition_id] || []).push(a);
  const violations = [];
  const known = new Set(cfg.conditions.map((c) => c.condition_id));
  for (const id of Object.keys(byCond)) if (!known.has(id)) violations.push(`${id}: condition is not in the conditions table`);

  const conditions = []; const drift = {};
  for (const cond of cfg.conditions) {
    const list = byCond[cond.condition_id] || [];
    const T = list.length;
    const S = list.filter((a) => a.outcome_category === cfg.success_category).length;
    const counts = {};
    for (const c of [cfg.success_category, ...cfg.failure_categories]) counts[c] = 0;
    const attribution = { TOOLING: {}, SUT: {}, unlabeled: {} };
    const seen = new Set();
    for (const a of list) {
      if (!declared.has(a.outcome_category)) violations.push(`${cond.condition_id}: ${a.run_id}: category ${JSON.stringify(a.outcome_category)} is not in the declared set`);
      else counts[a.outcome_category] += 1;
      const bucket = a.attribution === 'TOOLING' ? 'TOOLING' : a.attribution === 'SUT' ? 'SUT' : 'unlabeled';
      if (a.attribution !== null && a.attribution !== 'TOOLING' && a.attribution !== 'SUT') violations.push(`${cond.condition_id}: ${a.run_id}: attribution ${JSON.stringify(a.attribution)} is not TOOLING, SUT or null`);
      attribution[bucket][a.outcome_category] = (attribution[bucket][a.outcome_category] || 0) + 1;
      if (a.condition_id !== cond.condition_id) violations.push(`${cond.condition_id}: attempt ${a.run_id} names condition ${a.condition_id}`);
      if (a.attempt !== 1) violations.push(`${cond.condition_id}: ${a.run_id}: attempt ${a.attempt} is not 1`);
      if (a.matches_expected !== (a.outcome_category === cond.expected_category)) violations.push(`${cond.condition_id}: ${a.run_id}: matches_expected ${a.matches_expected} disagrees with the category ${a.outcome_category}`);
      const key = `${a.execution_id}/${a.attempt}`;
      if (seen.has(key)) violations.push(`${cond.condition_id}: repeated (execution_id, attempt) pair ${key}`);
      seen.add(key);
    }
    for (let n = 1; n <= cond.n; n += 1) if (!seen.has(`EX${String(n).padStart(4, '0')}/1`)) violations.push(`${cond.condition_id}: no attempt record for EX${String(n).padStart(4, '0')}`);
    if (cond.expected_category !== cfg.success_category) violations.push(`${cond.condition_id}: the expected category is not the success category`);
    const sum = Object.values(counts).reduce((x, y) => x + y, 0);
    if (sum !== T) violations.push(`${cond.condition_id}: the category counts sum to ${sum}, not T ${T}`);
    if (S > T) violations.push(`${cond.condition_id}: S ${S} exceeds T ${T}`);
    const d = core.distinctToolchain(list);
    if (Object.keys(d).length) drift[cond.condition_id] = d;
    conditions.push({ condition_id: cond.condition_id, sut_id: cond.sut_id, surface: cond.surface, account: cond.account, n_planned: cond.n,
                      T, S, TSRR: core.rate(S, T, WILSON_Z), category_counts: counts, attribution_by_category: attribution });
  }
  return { conditions, toolchain_drift_confounds: drift, violations };
}

function main() {
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
  const manifestStatus = fs.readFileSync(path.join(REPO, 'manifests/study-manifest.yaml'), 'utf8').match(/- id: E04-repeatability\n\s+status: (\w+)/);
  if (!manifestStatus || manifestStatus[1] !== 'FROZEN') fail('E04 is not FROZEN in the study manifest');

  const cfg = JSON.parse(condBuf.toString('utf8'));
  if (cfg.conditions.length !== 13 || cfg.n_per_condition !== N) fail('the conditions file is not the locked one (13 conditions, N = 50)');

  // ---- the 650 bundles and the 13 job directories --------------------------------------------------------------------------
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
  if (JSON.stringify([...foundRuns].sort()) !== JSON.stringify([...expectedRuns].sort())) fail('the set of run directories is not the 650 expected');
  if (JSON.stringify([...foundJobs].sort()) !== JSON.stringify([...expectedJobs].sort())) fail('the set of job directories is not the 13 expected');

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
      if (man.run_id !== d || man.condition !== c.condition_id || man.campaign_id !== 'E04-repeatability' || man.sut_id !== c.sut_id || man.attempt !== 1) fail(d + ': identity fields of the run manifest disagree');
      if (rec.run_id !== d || rec.condition !== c.condition_id || rec.execution_id !== ex || rec.attempt !== 1) fail(d + ': identity fields of the attempt record disagree');
      if (rec.record_class !== 'MEASURED_EXPERIMENT') fail(d + ': the attempt record is not a MEASURED_EXPERIMENT record');
      const listed = (man.artifacts || []).find((a) => a.path === `${RAW}/${c.sut_id}/${d}/attempt-record.json`);
      if (!listed || listed.sha256 !== sha(recBuf)) fail(d + ': the attempt record is not the one listed in the run manifest');
      if (!man.outcome || man.outcome.outcome_category !== rec.outcome_category) fail(d + ': the outcome category of the run manifest and of the attempt record disagree');
      if (man.outcome.expected !== c.expected_category) fail(d + ': the expected category of the run manifest is not the one of the conditions file');
      if (typeof man.outcome.matches_expected !== 'boolean') fail(d + ': matches_expected is not a boolean');
      attempts.push({ condition_id: c.condition_id, run_id: d, execution_id: ex, attempt: 1, outcome_category: rec.outcome_category,
                      matches_expected: man.outcome.matches_expected, attribution: rec.attribution === undefined ? null : rec.attribution, toolchain: man.toolchain });
      rows.push({ run_id: d, condition_id: c.condition_id, sut_id: c.sut_id, execution_id: ex, attempt: 1, outcome_category: rec.outcome_category,
                  expected_category: c.expected_category, matches_expected: man.outcome.matches_expected, attribution: rec.attribution === undefined ? null : rec.attribution,
                  workflow_outcome_status: man.outcome.status, last_phase: rec.last_phase, cause: rec.cause });
    }
  }

  const evaluated = evaluate(cfg, attempts);
  if (evaluated.violations.length) { console.error(evaluated.violations.join('\n')); fail(evaluated.violations.length + ' consistency violation(s)'); }
  const conditions = evaluated.conditions;
  const result = {
    record: 'TSRR analysis, E04-repeatability (derived dataset; descriptive; produced by analysis/e04-tsrr-analysis/compute-tsrr-e04.js from the frozen raw-data/E04-repeatability)',
    campaign_id: 'E04-repeatability',
    hypothesis_id: null,
    hypothesis_note: 'No hypothesis label applies: the E04 configuration attaches none (H3 is an E05 hypothesis). The H3 variable of protocol/statistical-analysis-plan-v1.md, section 4.3 spans E04 and E05; this analysis computes the E04 primary metric TSRR only and evaluates no hypothesis.',
    metric_source: 'protocol/repeatability-determinism-v1.md, section 4 (TSRR); experiments/E04-repeatability/README.md, "Campaign configuration", "Analysis (TSRR) and what is not computed"',
    estimators: { TSRR: 'S / T: executions with the category TARGET_STATE_VERIFIED over every valid measured attempt of the condition (ABORTED, ERROR and interrupted attempts stay in T)',
                  interval: 'Wilson score interval without continuity correction, z = ' + WILSON_Z, NOT_ESTIMABLE: 'the rate of an empty denominator; never reported as 0' },
    inputs: { raw_tree: RAW, raw_git_tree: treeHead, pinned_at_commit: FREEZE_COMMIT, campaign_state: 'FROZEN', bundles: rows.length, job_directories_ignored: foundJobs.length,
              conditions_file: CONDITIONS, conditions_file_sha256: CONDITIONS_SHA256, campaign_configuration_sha256: CONFIG_SHA256 },
    totals: { conditions: conditions.length, attempts_T: conditions.reduce((a, x) => a + x.T, 0), attempts_in_S: conditions.reduce((a, x) => a + x.S, 0),
              note: 'counts of attempts only; no pooling of rates across conditions or ecosystems is computed' },
    conditions,
    toolchain_drift_confounds: evaluated.toolchain_drift_confounds,
    consistency_violations: evaluated.violations,
    not_computed: 'No between-ecosystem comparison, pooled rate, composite score, CEOR, E2E-ROR, Outcome Entropy, H3 evaluation, test, p-value, effect size or ranking: none is frozen for E04, and the configuration lists them as not computed.'
  };
  const jsonText = JSON.stringify(result, null, 2) + '\n';
  const header = ['run_id', 'condition_id', 'sut_id', 'execution_id', 'attempt', 'outcome_category', 'expected_category', 'matches_expected', 'attribution', 'workflow_outcome_status', 'last_phase', 'cause'];
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
  console.log(`conditions ${conditions.length}: T ${result.totals.attempts_T}, S ${result.totals.attempts_in_S}; violations ${evaluated.violations.length}`);
}

module.exports = { evaluate, WILSON_Z };
if (require.main === module) main();
