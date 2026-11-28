#!/usr/bin/env node
'use strict';
/*
 * analysis/h5-analysis/compute-h5-e08.js
 *
 * H5 analysis, performance contribution (E08) only, for study EUS-2026-001, campaign E08-performance (FROZEN, 200 imported bundles in 4 conditions).
 * It implements, and nothing beyond, the descriptive procedure that the campaign configuration locked at the START
 * (experiments/E08-performance/README.md, "Campaign configuration": "Identity and START", "Conditions", "Metrics, rules, categories" and
 * "Order, records, reporting"; the conditions file experiments/E08-performance/conditions-draft.json) and
 * protocol/statistical-analysis-plan-v1.md, section 3 (Wilson 95% interval for every reported proportion), section 4.3 (H5 row: "Number of
 * controlled non-functional ground-truth conditions per ecosystem", method "Descriptive count comparison; detection rates per condition are
 * reported per Section 5") and section 5 (point estimate, interval, N, classification; "no data" with its reason, never zero).
 *
 * Pre-registered rules applied here (none is chosen after seeing the data):
 *   - Denominators (E08-D-18, fixed before any data): the detection proportion of a condition is the number of DETECTED executions over the
 *     number of executions that are valid measurements (DETECTED or NOT_DETECTED); every INCONCLUSIVE_, START_, INTERRUPTED_ and STUB_NO_BUNDLE
 *     execution is reported with its count and its attribution and sits outside that denominator. The false-positive proportion is the number
 *     of executions whose baseline-against-baseline record is true over the number of executions that have such a record (both baseline loads
 *     valid), whatever the category of the degraded load. All N = 50 executions of a condition appear in the table of counts. No minimum number
 *     of valid executions is invented.
 *   - Every reported proportion carries its Wilson 95% interval, no continuity correction (z = 1.959963984540054, the repository convention of
 *     analysis/h3-analysis/h3-metrics.js, which this script requires and does not modify). The medians of the metric values and of the two
 *     differences are descriptive (the mean of the two middle values for an even count).
 *   - A recorded outcome, whatever its category, is data: a NOT_DETECTED is a valid outcome, the expectation of the configuration is not
 *     changed (E08-D-8), and no cause is inferred.
 *   - H5 count unit (E08-D-2): each configured ground-truth condition counts once, whatever its detection result. The count is taken from the
 *     conditions file (the distinct condition_id with h5_counted true of each ecosystem), never from the outcomes. SUT-04, SUT-05 and SUT-06
 *     have no condition: no data, no ground-truth condition available, count null (the configuration assigns them no count, so none is
 *     invented). The classification of each comparison is written below from the configuration and never derived from the data
 *     (analysis/README.md, rule 9). No Fisher table, risk difference, test, p-value, ranking, composite or support / non-support criterion is
 *     formed (none is frozen for H5).
 *   - A near-certain result is stated as controllability evidence of the ground-truth condition and of the measurement, never as discriminating
 *     power (E08-D-7).
 *   - The H5 variable of the plan spans E08, E09, E10 and E11; this script covers the E08 contribution only, says so in its output, and does not
 *     add it to the E09 and E11 contributions (derived-data/h5-analysis/H5-e09-result.json, H5-e11-result.json).
 *
 * The category recorded in each run manifest is compared with the one derived here from the detection evidence file of the bundle
 * (evidence/015-detection.json: the flags detected and baseline_false_positive, the absent reasons and the external-image note), and with the
 * category of the attempt record and of the condition summary; the sha256 of each file read is checked against the one listed in the run
 * manifest. The order of the three loads is checked against the rotation rule of the conditions file. Any disagreement is listed and makes the
 * script exit non-zero. Nothing is interpreted: the output is counts, proportions, intervals and medians of recorded fields.
 *
 * Fails loudly on: pins that are not set; a raw-data tree that differs from the pinned tree of the freeze commit or has uncommitted changes; a
 * Campaign configuration section that differs from the pinned digest (at HEAD and at the START commit); a conditions file that differs from its
 * pinned digest; the pure core changed or uncommitted; E08 not FROZEN in the study manifest; a set of run or job directories that is not the
 * expected one (50 runs per condition at attempt 1, one job directory per condition); a run manifest, attempt record or condition summary that
 * disagrees with the directory name, the condition, the category or the attribution; a job provenance record whose condition, SUT, attempt,
 * GitHub run attempt or implementation hash disagrees with the locked one; a file whose sha256 differs from the one listed in its run manifest;
 * any violation of the consistency checks of evaluate().
 *
 * Usage: node analysis/h5-analysis/compute-h5-e08.js [--check]    (--check recomputes and compares with the files on disk; writes nothing)
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only; no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const core = require('../h3-analysis/h3-metrics.js');

const REPO = path.resolve(__dirname, '..', '..');
const RAW = 'raw-data/E08-performance';
const OUT_JSON = 'derived-data/h5-analysis/H5-e08-result.json';
const OUT_CSV = 'derived-data/E08-performance/outcomes-per-attempt.csv';
const README = 'experiments/E08-performance/README.md';
const CONDITIONS = 'experiments/E08-performance/conditions-draft.json';
// Pins: from the recorded START and freeze records (manifests/e08-campaign-start-v1.yaml, manifests/e08-campaign-freeze-v1.yaml).
const START_COMMIT = '0607f9a39309e601f3dfc11b009a6311c1a03b1e';                  // the E08 campaign START commit (E08-START-AUTH-01)
const FREEZE_COMMIT = 'b7ced46bd74d4228aaaafb1a42459bb551dfe538';                 // the E08 campaign freeze commit (E08-FREEZE-AUTH-01)
const RAW_TREE = '021c4d7bf687dcc466abb9b0cb210dcb834ddf6f';                       // git tree of raw-data/E08-performance at the freeze commit
const CONFIG_SHA256 = 'f3b081a66559e4f806754e576cbbd5885ed050d191fc7a4a3cf006910cfb8cd5';       // sha256 of the Campaign configuration section of the E08 README, equal at the START commit and at HEAD
const CONDITIONS_SHA256 = 'e4aaf35651d3b8e0d1abd6c29b9716b733756f2af0332ef90713ccc75b499a98';   // sha256 of the conditions file
const CORE_BLOB = '72b1f74949cc76ce907ca2a162e5d5fbd28ef6a0';                      // git blob of the pure core, unchanged since the E05 analysis
const IMPLEMENTATION_SHA256 = 'da24b1326d8ef55711fe077ac7363efccbf4c9d0277e6943e19649b9b1d7e4b2';   // executor implementation hash locked at the START (README, Prompt version and implementation)
const WILSON_Z = 1.959963984540054;   // 95 percent, the repository convention
const N = 50;
const VALID_CATEGORIES = ['DETECTED', 'NOT_DETECTED'];                              // the valid measurements (E08-D-18)
const STATUS_BY_CATEGORY = { DETECTED: 'SUCCESS', NOT_DETECTED: 'FAILURE' };

const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const fail = (m) => { console.error('FAIL: ' + m); process.exit(2); };
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const csvCell = (v) => {
  const s = v === null || v === undefined ? '' : typeof v === 'string' ? v : JSON.stringify(v);
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};
const tally = (arr, f) => arr.reduce((o, r) => { const k = f(r); o[k] = (o[k] || 0) + 1; return o; }, {});
const sortedObject = (o) => Object.fromEntries(Object.keys(o).sort().map((k) => [k, o[k]]));

// ---- the classification of the comparisons, written from the configuration (never derived from the data) ------------------------
const CLASSIFICATION = 'CONFIRMATORY (H5), descriptive count comparison, SUT-01 versus SUT-02 and SUT-01 versus SUT-03 (written from the E08 campaign configuration, subsection Identity and START, which names the hypothesis label H5 and the two pairs, and from protocol/statistical-analysis-plan-v1.md, section 4.2, which classifies a comparison that tests H5 as CONFIRMATORY; never derived from the data)';
const NO_CONDITION_REASON = {
  'SUT-04': 'no data: no ground-truth condition available (no condition configured, E08-D-1; SUT-04 has no controlled-degradation condition, SUT04-EV-0017); the frozen configuration assigns no count to this ecosystem, so none is invented',
  'SUT-05': 'no data: no ground-truth condition available (no condition configured, E08-D-1); the frozen configuration assigns no count to this ecosystem, so none is invented',
  'SUT-06': 'no data: no ground-truth condition available (no condition configured, E08-D-1); the frozen configuration assigns no count to this ecosystem, so none is invented'
};
const COMPARISONS = {
  'SUT-01 vs SUT-02': 'CONFIRMATORY (H5), descriptive count comparison on the E08 contribution: the two counts are side by side in the table of counts; the conditions measure different metrics of different pages (no canonical scenario, no mapping record, E08-D-10), so no pairwise detection comparison, Fisher table or risk difference is formed',
  'SUT-01 vs SUT-03': 'CONFIRMATORY (H5), descriptive count comparison on the E08 contribution: the two counts are side by side in the table of counts; the conditions measure different metrics of different pages (no canonical scenario, no mapping record, E08-D-10), so no pairwise detection comparison, Fisher table or risk difference is formed'
};
const LIMITS = 'The host-dependent CPU endpoint of SUT-01, its random latency spike (SUT01-EV-0016) and the 2G view of SUT-03 (SUT03-EV-0015) are not conditions of E08 (E08-D-2, E08-D-17 option A); the limit is stated in every report of E08: the instrument is a web-page measurement, the spike is an API endpoint, the 2G view needs a network emulation the instrument does not use, and none is excluded for being unfavorable to any SUT.';

// ---- pure functions (no file is read) ------------------------------------------------------------------------------------------
/** Median of an array of numbers (the mean of the two middle values for an even count); null for an empty array. */
function median(values) {
  if (!values.length) return null;
  const s = values.slice().sort((a, b) => a - b);
  const mid = s.length >> 1;
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
}

/** The descriptive summary of a list of recorded values: its count and its median. */
function medianOf(values) { return { n: values.length, median: median(values) }; }

/** The category that the detection evidence of one execution decides (the rule of the executor, read from its recorded flags); null when it cannot be derived. */
function deriveCategory(detection) {
  if (!detection || typeof detection !== 'object') return null;
  if (detection.detected === true) return 'DETECTED';
  if (detection.detected === false) return detection.external_image ? 'INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED' : 'NOT_DETECTED';
  if (detection.detected === null) {
    const reasons = ['D', 'Ba'].map((r) => String((detection.absent_reasons || {})[r] || ''));
    if (reasons.some((x) => x.startsWith('READY_SIGNAL_MISSING'))) return 'INCONCLUSIVE_READY_SIGNAL_MISSING';
    if (reasons.some((x) => x === 'METRIC_ABSENT')) return 'INCONCLUSIVE_METRIC_ABSENT';
  }
  return null;
}

/** Per-condition results, the H5 counts and the consistency violations. Pure: reads no file. `rows` are execution records
 *  { condition_id, run_id, execution_index, recorded_category, derived_category, status, matches_expected, attribution, order, values,
 *    delta_D, delta_Bb, baseline_false_positive, late_shift_entries, toolchain }. */
function evaluate(cfg, rows) {
  const violations = [];
  const ids = new Set(cfg.conditions.map((c) => c.condition_id));
  for (const r of rows) if (!ids.has(r.condition_id)) violations.push(`${r.run_id}: the condition ${r.condition_id} is not in the conditions file`);
  const declared = new Set([].concat(cfg.category_sets.start, cfg.category_sets.method, cfg.category_sets.any));
  const conditions = [];
  for (const cond of cfg.conditions) {
    const own = rows.filter((r) => r.condition_id === cond.condition_id).sort((a, b) => a.execution_index - b.execution_index);
    const n = own.length;
    if (n !== cfg.n_per_condition) violations.push(`${cond.condition_id}: ${n} executions, not ${cfg.n_per_condition}`);
    own.forEach((r, i) => { if (r.execution_index !== i + 1) violations.push(`${cond.condition_id}: execution indexes have a gap or do not start at 1`); });
    for (const r of own) {
      if (r.derived_category === null || r.derived_category === undefined) { violations.push(`${r.run_id}: the category cannot be derived from the evidence`); continue; }
      if (r.derived_category !== r.recorded_category) violations.push(`${r.run_id}: recorded ${r.recorded_category}, derived ${r.derived_category}`);
      if (!declared.has(r.recorded_category) && !r.recorded_category.startsWith('INTERRUPTED_')) violations.push(`${r.run_id}: category ${r.recorded_category} is outside the declared set`);
      const expectedMatch = VALID_CATEGORIES.includes(r.recorded_category) ? r.recorded_category === cond.expected_category : null;
      if (r.matches_expected !== expectedMatch) violations.push(`${r.run_id}: matches_expected disagrees with the comparison of the category with the expected category`);
      if (STATUS_BY_CATEGORY[r.recorded_category] && r.status !== STATUS_BY_CATEGORY[r.recorded_category]) violations.push(`${r.run_id}: status ${r.status} does not belong to the category ${r.recorded_category}`);
      if (!cfg.attribution_labels.includes(r.attribution)) violations.push(`${r.run_id}: attribution ${r.attribution} is outside the declared labels`);
      if (r.order) {
        const want = cfg.load_orders[(r.execution_index - 1) % cfg.load_orders.length];
        if (JSON.stringify(r.order) !== JSON.stringify(want)) violations.push(`${r.run_id}: the order of the loads ${JSON.stringify(r.order)} is not the one of the rotation rule ${JSON.stringify(want)}`);
      }
    }
    const counts = tally(own, (r) => r.recorded_category);
    const rec = (x, d) => core.rate(x, d, WILSON_Z);
    const valid = own.filter((r) => VALID_CATEGORIES.includes(r.recorded_category));
    const detections = valid.filter((r) => r.recorded_category === 'DETECTED').length;
    const fpRecords = own.filter((r) => r.baseline_false_positive === true || r.baseline_false_positive === false);
    const fps = fpRecords.filter((r) => r.baseline_false_positive === true).length;
    const withValues = (key) => own.map((r) => (r.values ? r.values[key] : null)).filter((v) => typeof v === 'number');
    const out = {
      condition_id: cond.condition_id, sut_id: cond.sut_id, behavior_class: cond.behavior_class, metric: cond.metric, unit: cond.unit, rule: cond.rule,
      expected_category: cond.expected_category, h5_counted: cond.h5_counted, n_executions: n,
      category_counts: Object.fromEntries(Object.keys(sortedObject(counts)).map((k) => [k, rec(counts[k], n)])),
      valid_measurements: valid.length,
      excluded_from_detection_denominator: n - valid.length,
      detection_proportion: { role: 'detection of the known ground-truth condition, over the valid measurements (E08-D-18)', ...rec(detections, valid.length) },
      false_positive_proportion: { role: 'baseline-against-baseline record true, over the executions that have such a record (E08-D-18)', executions_without_record: n - fpRecords.length, ...rec(fps, fpRecords.length) },
      matches_expected_counts: sortedObject(tally(own, (r) => String(r.matches_expected))),
      medians_descriptive: {
        metric_D: medianOf(withValues('D')), metric_Ba: medianOf(withValues('Ba')), metric_Bb: medianOf(withValues('Bb')),
        delta_D_minus_Ba: medianOf(own.map((r) => r.delta_D).filter((v) => typeof v === 'number')),
        delta_Bb_minus_Ba: medianOf(own.map((r) => r.delta_Bb).filter((v) => typeof v === 'number'))
      },
      position_of_D_in_the_order: sortedObject(tally(own.filter((r) => r.order), (r) => String(r.order.indexOf('D') + 1))),
      attribution_counts: sortedObject(tally(own, (r) => r.attribution)),
      workflow_outcome_status_counts: sortedObject(tally(own, (r) => r.status)),
      derived_from_evidence_equals_recorded: own.every((r) => r.derived_category === r.recorded_category)
    };
    if (cond.rule && cond.rule.also && cond.rule.also.late_shift) {
      const withEntry = valid.filter((r) => typeof r.late_shift_entries === 'number' && r.late_shift_entries > 0).length;
      out.late_target_shift_entries = { role: 'executions of the degraded load with at least one shift entry at or after ' + cond.rule.also.late_shift.min_start_ms + ' ms whose sources include the element #' + cond.rule.also.late_shift.target_element_id + ', over the valid measurements; descriptive, a component of the CLS rule', ...rec(withEntry, valid.length) };
    }
    if (valid.length > 0 && detections === 0) {
      out.non_detection_note = 'no execution recorded DETECTED; a non-detection is a valid outcome, the expectation of the configuration is not changed (E08-D-8), and no cause is inferred';
    }
    const drift = core.distinctToolchain(own);
    if (Object.keys(drift).length) out.toolchain_drift_confounds = drift;
    conditions.push(out);
  }
  // H5 count: the distinct ground-truth conditions with h5_counted true, from the conditions file (E08-D-2); the outcomes never enter it
  const h5 = {};
  for (const c of cfg.conditions.filter((x) => x.h5_counted === true)) (h5[c.sut_id] = h5[c.sut_id] || new Set()).add(c.condition_id);
  const h5Counts = {};
  for (const sut of ['SUT-01', 'SUT-02', 'SUT-03', 'SUT-04', 'SUT-05', 'SUT-06']) {
    if (h5[sut]) {
      h5Counts[sut] = { count: h5[sut].size, conditions: Array.from(h5[sut]).sort(), role: ['SUT-01', 'SUT-02', 'SUT-03'].includes(sut) ? 'H5 pair: counts in the CONFIRMATORY (H5) comparisons' : 'not part of an H5 pair',
        basis: 'E08-D-2 count unit: each configured ground-truth condition counts once, whatever its detection result; taken from the conditions file, never from the outcomes' };
    } else if (NO_CONDITION_REASON[sut]) {
      h5Counts[sut] = { count: null, reason: NO_CONDITION_REASON[sut] };
    } else violations.push(`${sut}: no H5 count rule (it has no counted condition and no declared reason)`);
  }
  return { conditions, h5_counts: h5Counts, violations };
}

function main() {
  const pins = { START_COMMIT, FREEZE_COMMIT, RAW_TREE, CONFIG_SHA256, CONDITIONS_SHA256, CORE_BLOB, IMPLEMENTATION_SHA256 };
  const unset = Object.keys(pins).filter((k) => !pins[k]);
  if (unset.length) fail('pins not set: ' + unset.join(', '));
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
  if (git('hash-object', 'analysis/h3-analysis/h3-metrics.js') !== CORE_BLOB) fail('the pure core is not the pinned blob ' + CORE_BLOB);
  const manifestStatus = fs.readFileSync(path.join(REPO, 'manifests/study-manifest.yaml'), 'utf8').match(/- id: E08-performance\n\s+status: (\w+)/);
  if (!manifestStatus || manifestStatus[1] !== 'FROZEN') fail('E08 is not FROZEN in the study manifest');

  const cfg = JSON.parse(condBuf.toString('utf8'));
  if (cfg.n_per_condition !== N || cfg.conditions.length !== 4 || cfg.campaign_id !== 'E08-performance') fail('the conditions file is not the locked one (four conditions, N = 50 each)');
  const SUT_DIRS = Array.from(new Set(cfg.conditions.map((c) => c.sut_id))).sort();

  // ---- the run and job directories ---------------------------------------------------------------------------------
  const present = fs.readdirSync(path.join(REPO, RAW)).filter((d) => !d.startsWith('.')).sort();
  if (JSON.stringify(present) !== JSON.stringify(SUT_DIRS)) fail('the SUT directories are not ' + SUT_DIRS.join(', '));
  const expectedRuns = []; const expectedJobs = [];
  for (const c of cfg.conditions) {
    expectedJobs.push(`${c.sut_id}/${c.condition_id}__job__A1`);
    for (let n = 1; n <= N; n++) expectedRuns.push(`${c.sut_id}/${c.condition_id}__EX${String(n).padStart(4, '0')}__A1`);
  }
  const foundRuns = []; const foundJobs = [];
  for (const sut of SUT_DIRS) {
    for (const d of fs.readdirSync(path.join(REPO, RAW, sut)).filter((x) => !x.startsWith('.')).sort()) (/__job__A\d+$/.test(d) ? foundJobs : foundRuns).push(`${sut}/${d}`);
  }
  if (JSON.stringify([...foundRuns].sort()) !== JSON.stringify([...expectedRuns].sort())) fail(`the set of run directories is not the ${expectedRuns.length} expected`);
  if (JSON.stringify([...foundJobs].sort()) !== JSON.stringify([...expectedJobs].sort())) fail(`the set of job directories is not the ${expectedJobs.length} expected`);

  const rows = []; const csvRows = []; let filesRead = 0; const jobRecords = {};
  for (const c of cfg.conditions) {
    const jobBase = path.join(REPO, RAW, c.sut_id, `${c.condition_id}__job__A1`);
    const summary = readJson(path.join(jobBase, 'condition-summary.json'));
    const jobProv = readJson(path.join(jobBase, 'ci-provenance.json'));
    filesRead += 2;
    if (summary.condition !== c.condition_id || summary.sut !== c.sut_id || summary.attempt !== 1 || summary.record_class !== 'MEASURED_EXPERIMENT') fail(c.condition_id + ': the condition summary names another condition, SUT, attempt or record class');
    if (summary.executions_run !== N || summary.executions_planned !== N || (summary.executions || []).length !== N) fail(c.condition_id + ': the condition summary does not hold 50 executions');
    if (jobProv.condition_id !== c.condition_id || jobProv.sut_id !== c.sut_id || jobProv.attempt !== 1 || jobProv.campaign_id !== 'E08-performance') fail(c.condition_id + ': the job provenance names another condition, SUT or attempt');
    if (!jobProv.github || String(jobProv.github.run_attempt) !== '1') fail(c.condition_id + ': the GitHub run attempt is not 1');
    if (!jobProv.frozen_input_hashes || jobProv.frozen_input_hashes.executor_implementation_sha256 !== IMPLEMENTATION_SHA256) fail(c.condition_id + ': the implementation hash of the job is not the one locked at the START');
    jobRecords[c.condition_id] = { github_run_id: jobProv.github && jobProv.github.run_id, github_run_number: jobProv.github && jobProv.github.run_number, workflow_file_sha256: jobProv.workflow && jobProv.workflow.file_sha256, condition_summary_sha256: sha(fs.readFileSync(path.join(jobBase, 'condition-summary.json'))) };
    for (let n = 1; n <= N; n++) {
      const ex = `EX${String(n).padStart(4, '0')}`;
      const d = `${c.condition_id}__${ex}__A1`;
      const base = path.join(REPO, RAW, c.sut_id, d);
      const man = readJson(path.join(base, 'run-manifest.json'));
      filesRead += 1;
      if (man.run_id !== d || man.condition !== c.condition_id || man.campaign_id !== 'E08-performance' || man.sut_id !== c.sut_id || man.attempt !== 1) fail(d + ': identity fields of the run manifest disagree');
      const entry = summary.executions[n - 1];
      if (!entry || entry.run_id !== d) fail(d + ': the condition summary has no matching entry at its position');
      if (!man.outcome || man.outcome.outcome_category !== entry.category) fail(d + ': the outcome category of the run manifest and of the condition summary disagree');
      const am = /attribution=(\w+)/.exec(man.notes || '');
      if (!am || am[1] !== entry.attribution) fail(d + ': the attribution of the run manifest and of the condition summary disagree');
      const listed = (rel) => (man.artifacts || []).find((a) => a.path === `${RAW}/${c.sut_id}/${d}/${rel}`);
      const readListed = (rel) => {
        const buf = fs.readFileSync(path.join(base, rel)); filesRead += 1;
        const l = listed(rel);
        if (!l || l.sha256 !== sha(buf)) fail(d + ': ' + rel + ' is not the file listed in the run manifest');
        return JSON.parse(buf.toString('utf8'));
      };
      const attempt = readListed('attempt-record.json');
      if (attempt.run_id !== d || attempt.condition !== c.condition_id || attempt.attempt !== 1 || attempt.outcome_category !== man.outcome.outcome_category || attempt.attribution !== entry.attribution) fail(d + ': the attempt record disagrees with the run manifest or the condition summary');
      const evNames = fs.readdirSync(path.join(base, 'evidence')).sort();
      const det = evNames.filter((x) => /^\d+-detection\.json$/.test(x));
      if (det.length > 1) fail(d + ': more than one detection evidence file');
      let detection = null; let derived; let basis;
      if (det.length === 1) { detection = readListed('evidence/' + det[0]); derived = deriveCategory(detection); basis = 'evidence/' + det[0]; }
      else if (!VALID_CATEGORIES.includes(man.outcome.outcome_category) && !man.outcome.outcome_category.startsWith('INCONCLUSIVE_')) { derived = man.outcome.outcome_category; basis = 'no detection evidence: the category is decided before or outside the classification of the three loads'; }
      else { derived = null; basis = 'no detection evidence file'; }
      const late = detection && typeof detection.late_target_shift_entries === 'number' ? detection.late_target_shift_entries : null;
      const row = { condition_id: c.condition_id, run_id: d, execution_index: n, recorded_category: man.outcome.outcome_category, derived_category: derived, status: man.outcome.status,
                    matches_expected: man.outcome.matches_expected, attribution: entry.attribution, order: detection ? detection.order : null, values: detection ? detection.values : null,
                    delta_D: detection ? detection.delta_D_minus_Ba : null, delta_Bb: detection ? detection.delta_Bb_minus_Ba : null,
                    baseline_false_positive: detection ? detection.baseline_false_positive : null, late_shift_entries: late, toolchain: man.toolchain };
      rows.push(row);
      const v = (k) => (detection && detection.values ? detection.values[k] : null);
      csvRows.push({ run_id: d, condition_id: c.condition_id, sut_id: c.sut_id, behavior_class: c.behavior_class, metric: c.metric, unit: c.unit, execution_id: ex, attempt: 1,
                     recorded_outcome_category: man.outcome.outcome_category, derived_outcome_category: derived, workflow_outcome_status: man.outcome.status, matches_expected: man.outcome.matches_expected,
                     attribution: entry.attribution, load_order: detection ? detection.order.join('>') : null, value_D: v('D'), value_Ba: v('Ba'), value_Bb: v('Bb'),
                     delta_D_minus_Ba: row.delta_D, delta_Bb_minus_Ba: row.delta_Bb, detected: detection ? detection.detected : null, baseline_false_positive: row.baseline_false_positive,
                     late_target_shift_entries: late, derivation_basis: basis });
    }
  }

  const evaluated = evaluate(cfg, rows);
  if (evaluated.violations.length) { console.error(evaluated.violations.join('\n')); fail(evaluated.violations.length + ' consistency violation(s)'); }
  const result = {
    record_class: 'DERIVED_ANALYSIS_RESULT', study_id: 'EUS-2026-001', campaign_id: 'E08-performance', hypothesis_id: 'H5',
    part: 'performance (E08) contribution only; the H5 variable of protocol/statistical-analysis-plan-v1.md, section 4.3, spans E08, E09, E10 and E11; E10 has not been started, and the E09 and E11 contributions are the separate datasets derived-data/h5-analysis/H5-e09-result.json and derived-data/h5-analysis/H5-e11-result.json; the contributions are not summed here',
    method: 'descriptive; Wilson 95% interval without continuity correction (z = ' + WILSON_Z + '); medians descriptive; no test, no p-value, no Holm correction, no support or non-support criterion (none is frozen for H5)',
    classification: CLASSIFICATION,
    inputs: { raw_data_tree: treeHead, pinned_at_commit: FREEZE_COMMIT, start_commit: START_COMMIT, bundles: rows.length, job_directories: foundJobs.length, conditions: cfg.conditions.length,
              configuration_section_sha256: CONFIG_SHA256, conditions_file: CONDITIONS, conditions_file_sha256: CONDITIONS_SHA256, executor_implementation_sha256: IMPLEMENTATION_SHA256, campaign_state: 'FROZEN', job_records: jobRecords },
    h5_count_of_controlled_non_functional_ground_truth_conditions: {
      scope: 'E08 contribution only',
      ecosystems: evaluated.h5_counts,
      comparisons: COMPARISONS,
      not_evaluated: 'E10 has not been started; the H5 count over all its campaigns does not exist yet; the E09 and E11 contributions are separate datasets and are not added here'
    },
    conditions: evaluated.conditions,
    totals: { executions: rows.length, conditions: evaluated.conditions.length, note: 'counts only; no rate is pooled across conditions or ecosystems' },
    consistency: { recorded_category_equals_the_one_derived_from_the_evidence: evaluated.violations.length === 0, disagreements: evaluated.violations },
    limits: LIMITS,
    not_computed: 'No pooled rate, composite score, ranking, cross-ecosystem detection comparison, Fisher table, risk difference, test, p-value or verdict: the configuration lists them as not computed and none is frozen for H5.',
    notes: 'Deterministic, non-interpretive computation: counts, proportions, intervals and medians of recorded fields. A near-certain detection result is controllability evidence of the ground-truth condition and of the measurement, never discriminating power (E08-D-7). The expectation of E08-SUT03-WEB-CLS (DETECTED; E01 record SUT03-EV-0012) is not changed by any outcome (E08-D-8); its recorded outcomes are reported as recorded and no cause is inferred. E08-SUT03-WEB-LCP depends on the host picsum.photos, outside the evaluated version (SUT03-EV-0013).'
  };
  const jsonText = JSON.stringify(result, null, 2) + '\n';
  const header = ['run_id', 'condition_id', 'sut_id', 'behavior_class', 'metric', 'unit', 'execution_id', 'attempt', 'recorded_outcome_category', 'derived_outcome_category', 'workflow_outcome_status',
                  'matches_expected', 'attribution', 'load_order', 'value_D', 'value_Ba', 'value_Bb', 'delta_D_minus_Ba', 'delta_Bb_minus_Ba', 'detected', 'baseline_false_positive',
                  'late_target_shift_entries', 'derivation_basis'];
  const csvText = header.join(',') + '\n' + csvRows.map((r) => header.map((h) => csvCell(r[h])).join(',')).join('\n') + '\n';
  const outputs = [[OUT_JSON, jsonText], [OUT_CSV, csvText]];

  if (process.argv.includes('--check')) {
    const ok = outputs.every(([p, text]) => fs.existsSync(path.join(REPO, p)) && fs.readFileSync(path.join(REPO, p), 'utf8') === text);
    console.log(ok ? 'CHECK OK: the files on disk equal the recomputation' : 'CHECK FAILED: the files on disk differ from the recomputation');
    process.exit(ok ? 0 : 3);
  }
  for (const [p] of outputs) fs.mkdirSync(path.dirname(path.join(REPO, p)), { recursive: true });
  for (const [p, text] of outputs) { fs.writeFileSync(path.join(REPO, p), text); console.log(`wrote ${p} (sha256 ${sha(Buffer.from(text))})`); }
  console.log(`run bundles ${rows.length}, files read ${filesRead}; violations ${evaluated.violations.length}`);
}

module.exports = { median, medianOf, deriveCategory, evaluate, WILSON_Z, COMPARISONS, NO_CONDITION_REASON, VALID_CATEGORIES };
if (require.main === module) main();
