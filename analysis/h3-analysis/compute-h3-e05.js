#!/usr/bin/env node
'use strict';
/*
 * analysis/h3-analysis/compute-h3-e05.js
 *
 * H3 analysis, E05-determinism contribution only, for study EUS-2026-001, campaign E05-determinism (FROZEN, 650 imported
 * bundles of 13 conditions). It is the loader and command-line driver that the "Campaign configuration" of the campaign promised
 * "after the data freeze" (experiments/E05-determinism/README.md, "CONFIRMATORY comparisons and analysis"): it turns the bundles
 * into the attempt records that the pure core analysis/h3-analysis/h3-metrics.js takes, calls its evaluate(), and writes the result
 * and a per-attempt table. It computes nothing beyond what the core computes (TSRR, CEOR, E2E-ROR, H(Y) with k, Wilson 95% intervals
 * without continuity correction, the H3 rule of the configuration, the secondary attribution table, the toolchain drift report, the
 * consistency checks). The pure core is not modified by this loader and is run as committed.
 *
 * Pre-registered rules applied here (none is chosen after seeing the data):
 *   - H3 label: only the SUT-01 conditions classified a priori as deterministic (h3_labeled in the conditions file); for them H3 is
 *     satisfied when M = S with S at or above 45 of 50, falsified by any unexpected stimulus-phase category among S, and not evaluable
 *     below S = 45 (decision D-06). Every other condition carries DESCRIPTIVE (a deterministic condition of another ecosystem) or
 *     NOT_H3 (a stochastic or external-dependency condition, whose CEOR is descriptive, D-07).
 *   - No attempt is excluded from any denominator; no label is re-mapped by this loader (the label recorded by the executor is the
 *     label analyzed); TOOLING and SUT attributions are reported beside the raw rates and never change them (D-16, D-16b).
 *   - No test, p-value, effect size, pooling across conditions or across ecosystems, ranking or composite is computed: none is
 *     frozen for H3, which defines no between-ecosystem comparison (protocol/statistical-analysis-plan-v1.md, section 4.3).
 *   - The H3 variable of the plan spans E04 and E05; this script covers the E05 contribution only and says so in its output.
 *
 * Fails loudly on: a raw-data tree that differs from the pinned tree of the freeze commit or has uncommitted changes; a Campaign
 * configuration section that differs from the pinned digest (at HEAD and at the START commit); a conditions file that differs from
 * its pinned digest; E05 not FROZEN in the study manifest; a set of run directories that is not the 650 expected, or a job directory
 * set that is not the 13 expected; an attempt other than 1; a bundle whose directory name, run manifest and attempt record
 * disagree (identity, outcome category, expected category, behavior class); an attempt record whose sha256 differs from the one
 * listed in its run manifest; any violation returned by the consistency checks of the core.
 *
 * Usage: node analysis/h3-analysis/compute-h3-e05.js [--check]    (--check recomputes and compares with the files on disk; writes nothing)
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only; no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const core = require('./h3-metrics.js');

const REPO = path.resolve(__dirname, '..', '..');
const RAW = 'raw-data/E05-determinism';
const OUT_JSON = 'derived-data/h3-analysis/H3-e05-result.json';
const OUT_CSV = 'derived-data/E05-determinism/outcomes-per-attempt.csv';
const README = 'experiments/E05-determinism/README.md';
const CONDITIONS = 'experiments/E05-determinism/conditions-draft.json';
const START_COMMIT = '0269def116294197183a8635d527160422d84a9a';                  // the E05 campaign START commit (E05-START-AUTH-01)
const FREEZE_COMMIT = '7653ea2f3f7f81384871c4b8c84c53643d0827f0';                 // the E05 campaign freeze commit (E05-FREEZE-AUTH-01)
const RAW_TREE = '01276eab8c0dc750f5a03efefa213749fc8ef73f';                      // git tree of raw-data/E05-determinism at the freeze commit
const CONFIG_SHA256 = '51b9933ee49ab8a8ff77915dc741471e101b9c9c15b61d7368566731df9c2e90';
const CONDITIONS_SHA256 = '40b226610904f339a7e40d90ffeaf6e4d0ddb8862f6adba4cc2cf5efc2923eb8';
const SUT_DIRS = ['SUT-01', 'SUT-02', 'SUT-04', 'SUT-05'];
const N = 50;

const git = (...a) => execFileSync('git', ['-C', REPO, ...a], { encoding: 'utf8' }).replace(/\n$/, '');
const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const fail = (m) => { console.error('FAIL: ' + m); process.exit(2); };
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const csvCell = (v) => {
  const s = v === null || v === undefined ? '' : typeof v === 'string' ? v : JSON.stringify(v);
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

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
const manifestStatus = fs.readFileSync(path.join(REPO, 'manifests/study-manifest.yaml'), 'utf8').match(/- id: E05-determinism\n\s+status: (\w+)/);
if (!manifestStatus || manifestStatus[1] !== 'FROZEN') fail('E05 is not FROZEN in the study manifest');

const cfg = JSON.parse(condBuf.toString('utf8'));
if (cfg.conditions.length !== 13 || cfg.n_per_condition !== N || cfg.min_s_for_h3 !== 45) fail('the conditions file is not the locked one (13 conditions, N = 50, minimum S 45)');
const condById = Object.fromEntries(cfg.conditions.map((c) => [c.condition_id, c]));

// ---- the 650 bundles and the 13 job directories ------------------------------------------------------------------------
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
    if (man.run_id !== d || man.condition !== c.condition_id || man.campaign_id !== 'E05-determinism' || man.sut_id !== c.sut_id || man.attempt !== 1) fail(d + ': identity fields of the run manifest disagree');
    if (rec.run_id !== d || rec.condition !== c.condition_id || rec.execution_id !== ex || rec.attempt !== 1) fail(d + ': identity fields of the attempt record disagree');
    const listed = (man.artifacts || []).find((a) => a.path === `${RAW}/${c.sut_id}/${d}/attempt-record.json`);
    if (!listed || listed.sha256 !== sha(recBuf)) fail(d + ': the attempt record is not the one listed in the run manifest');
    if (!man.outcome || man.outcome.outcome_category !== rec.outcome_category) fail(d + ': the outcome category of the run manifest and of the attempt record disagree');
    if (man.outcome.expected !== c.expected_category) fail(d + ': the expected category of the run manifest is not the one of the conditions file');
    if (typeof man.outcome.matches_expected !== 'boolean') fail(d + ': matches_expected is not a boolean');
    if (man.behavior_class !== c.behavior_class) fail(d + ': the behavior class of the run manifest is not the one of the conditions file');
    attempts.push({ condition_id: c.condition_id, run_id: d, execution_id: ex, attempt: 1, outcome_category: rec.outcome_category,
                    matches_expected: man.outcome.matches_expected, attribution: rec.attribution === undefined ? null : rec.attribution,
                    behavior_class: man.behavior_class, toolchain: man.toolchain });
    rows.push({ run_id: d, condition_id: c.condition_id, sut_id: c.sut_id, execution_id: ex, attempt: 1, outcome_category: rec.outcome_category,
                phase: core.phaseOf(rec.outcome_category), expected_category: c.expected_category, matches_expected: man.outcome.matches_expected,
                attribution: rec.attribution === undefined ? null : rec.attribution, workflow_outcome_status: man.outcome.status,
                stimulus_request_sent: rec.stimulus_request_sent, last_phase: rec.last_phase, cause: rec.cause, note: rec.note || rec.notes || null });
  }
}

// ---- the pure core ---------------------------------------------------------------------------------------------------------
const evaluated = core.evaluate(cfg, attempts);
if (evaluated.violations.length) { console.error(evaluated.violations.join('\n')); fail(evaluated.violations.length + ' consistency violation(s) returned by the core'); }

const byCond = Object.fromEntries(evaluated.conditions.map((m) => [m.condition_id, m]));
const conditions = cfg.conditions.map((c) => {
  const m = byCond[c.condition_id];
  return { condition_id: c.condition_id, sut_id: c.sut_id, surface: c.surface, account: c.account, behavior_class: c.behavior_class, h3_labeled: c.h3_labeled,
           expected_category: c.expected_category, k: c.k, n_planned: c.n, T: m.T, S: m.S, M: m.M, TSRR: m.TSRR, CEOR: m.CEOR, E2E_ROR: m.E2E_ROR,
           H_Y: m.H_Y, category_counts_in_S: m.category_counts_in_S, pre_stage_counts: m.pre_stage_counts, h3: m.h3, attribution_in_S: m.attribution_in_S };
});
const h3c = conditions.filter((x) => x.h3_labeled);
const statusCount = (s) => h3c.filter((x) => x.h3.status === s).length;
const result = {
  record: 'H3 analysis, E05-determinism contribution (derived dataset; descriptive; produced by analysis/h3-analysis/compute-h3-e05.js from the frozen raw-data/E05-determinism)',
  scope: 'E05 contribution only: the H3 variable of protocol/statistical-analysis-plan-v1.md, section 4.3 spans E04 and E05, and E04 has no data',
  campaign_id: 'E05-determinism',
  hypothesis_id: 'H3',
  hypothesis_wording_source: 'protocol/statistical-analysis-plan-v1.md, section 4.3 (H3 row); experiments/E05-determinism/README.md, "Campaign configuration"',
  classification: 'H3 is a single-ecosystem prediction for the SUT-01 conditions classified a priori as deterministic; it defines no between-ecosystem comparison. The metrics of the other conditions are descriptive. The classification is written here from the configuration and is not derived from the data.',
  evaluation_rule: { satisfied: 'M = S with S >= 45 (of N = 50)', falsified: 'any unexpected stimulus-phase category among the S attempts (M < S) with S >= 45', not_evaluable: 'S < 45, with the reason (D-06)', min_s_for_h3: cfg.min_s_for_h3,
                     note: 'SATISFIED is not a proof of determinism: the core states the probability that all S attempts match as q^S for a per-attempt match probability q' },
  estimators: { interval: 'Wilson score interval without continuity correction (D-05)', wilson_z: cfg.wilson_z, entropy: 'Shannon entropy in bits over the declared stimulus categories, k stated, n = S',
                TSRR: 'S / T', CEOR: 'M / S', E2E_ROR: 'M / T', NOT_ESTIMABLE: 'the rate of an empty denominator; never reported as 0' },
  inputs: { raw_tree: RAW, raw_git_tree: treeHead, pinned_at_commit: FREEZE_COMMIT, campaign_state: 'FROZEN', bundles: rows.length, job_directories_ignored: foundJobs.length,
            conditions_file: CONDITIONS, conditions_file_sha256: CONDITIONS_SHA256, campaign_configuration_sha256: CONFIG_SHA256 },
  totals: { conditions: conditions.length, attempts_T: conditions.reduce((a, x) => a + x.T, 0), attempts_in_S: conditions.reduce((a, x) => a + x.S, 0), attempts_matching_expected_M: conditions.reduce((a, x) => a + x.M, 0),
            h3_labeled_conditions: h3c.length, h3_satisfied: statusCount('SATISFIED'), h3_falsified: statusCount('FALSIFIED'), h3_not_evaluable: statusCount('NOT_EVALUABLE'),
            note: 'counts of attempts and of statuses only; no pooling of rates across conditions or ecosystems is computed' },
  conditions,
  toolchain_drift_confounds: evaluated.toolchain_drift_confounds,
  consistency_violations: evaluated.violations,
  not_computed: 'No test, p-value, effect size, Holm correction, pooled rate, cross-ecosystem difference, ranking or composite: none is frozen for H3, and H3 defines no between-ecosystem comparison.'
};
const jsonText = JSON.stringify(result, null, 2) + '\n';
const header = ['run_id', 'condition_id', 'sut_id', 'execution_id', 'attempt', 'outcome_category', 'phase', 'expected_category', 'matches_expected', 'attribution', 'workflow_outcome_status', 'stimulus_request_sent', 'last_phase', 'cause', 'note'];
const csvText = header.join(',') + '\n' + rows.map((r) => header.map((h) => csvCell(r[h])).join(',')).join('\n') + '\n';

if (process.argv.includes('--check')) {
  const same = (p, text) => fs.existsSync(path.join(REPO, p)) && fs.readFileSync(path.join(REPO, p), 'utf8') === text;
  const ok = same(OUT_JSON, jsonText) && same(OUT_CSV, csvText);
  console.log(ok ? 'CHECK OK: the files on disk equal the recomputation' : 'CHECK FAILED: the files on disk differ from the recomputation');
  process.exit(ok ? 0 : 3);
}
fs.mkdirSync(path.dirname(path.join(REPO, OUT_JSON)), { recursive: true });
fs.mkdirSync(path.dirname(path.join(REPO, OUT_CSV)), { recursive: true });
fs.writeFileSync(path.join(REPO, OUT_JSON), jsonText);
fs.writeFileSync(path.join(REPO, OUT_CSV), csvText);
console.log(`wrote ${OUT_JSON} (sha256 ${sha(Buffer.from(jsonText))}) and ${OUT_CSV} (sha256 ${sha(Buffer.from(csvText))}); bundles ${rows.length}, files read ${filesRead}`);
console.log(`H3-labeled conditions ${h3c.length}: satisfied ${statusCount('SATISFIED')}, falsified ${statusCount('FALSIFIED')}, not evaluable ${statusCount('NOT_EVALUABLE')}; violations ${evaluated.violations.length}`);
