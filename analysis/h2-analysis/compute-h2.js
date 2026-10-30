#!/usr/bin/env node
'use strict';
/*
 * analysis/h2-analysis/compute-h2.js
 *
 * H2 analysis, reset side only, for study EUS-2026-001, campaign E03-resetability (FROZEN, 350 imported bundles).
 *
 * Implements the H2 procedure frozen in protocol/statistical-analysis-plan-v1.md, section 4.3:
 *   "Required Actions (establish; reset) per COMPARABLE canonical scenario" -- ecosystem pairs SUT-01 vs SUT-02 and
 *   SUT-01 vs SUT-03 -- "Paired per-scenario differences; Wilcoxon signed-rank where pairing is adequate, otherwise
 *   descriptive; effect size per Section 3."
 * and the confirmatory comparisons locked at the campaign START (experiments/E03-resetability/README.md, "Campaign
 * configuration", subsection "CONFIRMATORY comparisons"): SUT-01 versus SUT-02 and SUT-01 versus SUT-03, on Required
 * Actions (reset) per COMPARABLE canonical scenario, paired on the WEB surface; "this campaign contributes the reset
 * side only"; SUT-04 and SUT-05 stay EXPLORATORY and no comparison involving them is made here. The classification of
 * the two comparisons is written below from that section; it is never derived from the data (analysis/README.md,
 * rule 9).
 *
 * Variable: Required Actions (reset) of one execution = the number of entries of `actions[]` of its bundle
 * (experiments/E03-resetability/executor/README.md, section 3, item 1: only the reset-side Required Actions enter
 * `actions[]`; the precondition, the establishment, and the pre-reset verification are never counted). Statistics are
 * computed over the attempts that reached the reset action (at least one action record); the run outcome.status
 * frequencies (SUCCESS, FAILURE, INCONCLUSIVE, ABORTED, ERROR) are reported beside them and nothing is dropped
 * (campaign configuration, "Sample size per condition"). The count does not depend on outcome.status.
 *
 * Pairing unit: canonical_scenario_id (statistical-analysis-plan-v1.md, sections 3 and 4.1). The campaign has one
 * canonical scenario, CS-001, so each confirmatory comparison is exactly one pair: the per-scenario count of an
 * ecosystem is the median of the Required Actions (reset) over the executions of its WEB condition. One pair does not
 * justify the Wilcoxon signed-rank test (section 3: "number of non-tied pairs adequate"), so the comparison is reported
 * descriptively, which is the plan's own fallback branch; no bootstrap and no rank-biserial correlation is computed
 * (the bootstrap is prescribed for duration variables; the rank-biserial is reported only where Wilcoxon is applied).
 * Executions of different ecosystems are independent dispatches and are never paired by execution id.
 *
 * No support/non-support criterion is frozen for H2 (contrast H3); none is computed or emitted.
 *
 * Fails loudly on: a raw-data tree that differs from the pinned tree or has uncommitted changes; a missing, extra, or
 * duplicated execution; a bundle whose directory name, run manifest, or actions.json disagree; an actions.json whose
 * sha256 differs from the one listed in its run manifest; any action with is_retry true (none observed; no branch is
 * implemented for it); a condition other than the seven expected.
 *
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only (fs, path, crypto,
 * child_process) -- no package manager, no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

const REPO_ROOT = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();

const RAW_DIR = 'raw-data/E03-resetability';
const EXPECTED_RAW_TREE = 'e4f09366ad9e9ee58304e8096ff38f783259abef';
const FREEZE_COMMIT = '8640b173bbdb0a2d8eba6be5c54f6ccb26fd978b';
const START_COMMIT = '58f08964b4bd8879d3f8f29005a734f63e5f954f';
const CONFIG_SECTION_SHA256 = 'dba46253092d8d8c66861f584677655841192d683e1954dbc53e51d10956f3cc';

const EXECUTIONS_PER_CONDITION = 50;
const SCENARIO_ID = 'CS-001';
const OMNIPIZZA = 'SUT-01';

// Conditions table of the locked configuration (the seven executable conditions); predeclared = predeclared reset-side count.
const CONDITIONS = [
  { condition_id: 'E03-CS001-SUT01-WEB', sut_id: 'SUT-01', surface: 'WEB', reset_mechanism: 'API_RESET / SESSION_RESET', predeclared: 2 },
  { condition_id: 'E03-CS001-SUT01-API', sut_id: 'SUT-01', surface: 'API', reset_mechanism: 'API_RESET / SESSION_RESET', predeclared: 2 },
  { condition_id: 'E03-CS001-SUT02-WEB', sut_id: 'SUT-02', surface: 'WEB', reset_mechanism: 'APP_DATA_CLEAR', predeclared: 2 },
  { condition_id: 'E03-CS001-SUT03-WEB', sut_id: 'SUT-03', surface: 'WEB', reset_mechanism: 'SESSION_RESET', predeclared: 2 },
  { condition_id: 'E03-CS001-SUT04-WEB', sut_id: 'SUT-04', surface: 'WEB', reset_mechanism: 'API_RESET', predeclared: 2 },
  { condition_id: 'E03-CS001-SUT04-API', sut_id: 'SUT-04', surface: 'API', reset_mechanism: 'API_RESET', predeclared: 2 },
  { condition_id: 'E03-CS001-SUT05-API', sut_id: 'SUT-05', surface: 'API', reset_mechanism: 'ENVIRONMENT_RESTART', predeclared: 2 },
];

// CONFIRMATORY (H2): written from the campaign configuration, subsection "CONFIRMATORY comparisons".
const CONFIRMATORY_BASELINES = [
  { baseline_sut: 'SUT-02', baseline_condition: 'E03-CS001-SUT02-WEB' },
  { baseline_sut: 'SUT-03', baseline_condition: 'E03-CS001-SUT03-WEB' },
];
const OMNIPIZZA_CONDITION = 'E03-CS001-SUT01-WEB';

// Dispatched attempts that left no bundle (both failed before the executor ran); their dispatch records name the runs.
const ATTEMPTS_WITHOUT_BUNDLE = [
  { condition_id: 'E03-CS001-SUT01-WEB', execution_id: 'EX0001', attempt: 1, github_run_id: 40800423112, dispatch_record: 'manifests/e03-measured-dispatch/E03-CS001-SUT01-WEB.yaml' },
  { condition_id: 'E03-CS001-SUT04-API', execution_id: 'EX0003', attempt: 1, github_run_id: 40827272226, dispatch_record: 'manifests/e03-measured-dispatch/E03-CS001-SUT04-API.yaml' },
];

const BUNDLE_NAME = /^(E03-CS001-SUT0[1-5]-(?:WEB|API))__(EX\d{4})__A(\d+)$/;

function fail(msg) {
  console.error('FAIL: ' + msg);
  process.exit(1);
}

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function git(args) {
  return execFileSync('git', ['--no-optional-locks', ...args], { cwd: REPO_ROOT, encoding: 'utf8' }).trim();
}

// Quantile, linear interpolation between order statistics (type 7); xs sorted ascending.
function quantile(xs, p) {
  const h = (xs.length - 1) * p;
  const lo = Math.floor(h);
  const hi = Math.min(lo + 1, xs.length - 1);
  return xs[lo] + (h - lo) * (xs[hi] - xs[lo]);
}

function frequency(values) {
  const out = {};
  for (const v of values) out[v] = (out[v] || 0) + 1;
  return Object.fromEntries(Object.entries(out).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)));
}

function readBundle(sutDirName, bundleName) {
  const m = bundleName.match(BUNDLE_NAME);
  if (!m) fail(`unexpected bundle name ${bundleName}`);
  const [, conditionId, executionId, attemptText] = m;
  const cond = CONDITIONS.find((c) => c.condition_id === conditionId);
  if (!cond) fail(`${bundleName}: condition ${conditionId} is not one of the seven expected conditions`);
  if (cond.sut_id !== sutDirName) fail(`${bundleName}: stored under ${sutDirName}, condition belongs to ${cond.sut_id}`);

  const relDir = `${RAW_DIR}/${sutDirName}/${bundleName}`;
  const manifestBuf = fs.readFileSync(path.join(REPO_ROOT, relDir, 'run-manifest.json'));
  const actionsBuf = fs.readFileSync(path.join(REPO_ROOT, relDir, 'actions.json'));
  const manifest = JSON.parse(manifestBuf.toString('utf8'));
  const record = JSON.parse(actionsBuf.toString('utf8'));
  const attempt = Number(attemptText);

  if (manifest.campaign_id !== 'E03-resetability' || manifest.condition !== conditionId) fail(`${bundleName}: run manifest campaign/condition mismatch`);
  if (manifest.attempt !== attempt) fail(`${bundleName}: run manifest attempt ${manifest.attempt} differs from the directory`);
  if (manifest.sut_id !== sutDirName) fail(`${bundleName}: run manifest sut_id ${manifest.sut_id}`);
  if (manifest.scenario !== SCENARIO_ID) fail(`${bundleName}: run manifest scenario ${manifest.scenario}`);
  if (record.run_id !== bundleName) fail(`${bundleName}: actions.json run_id ${record.run_id}`);

  const listed = (manifest.artifacts || []).filter((a) => a.path === `${relDir}/actions.json`);
  if (listed.length !== 1) fail(`${bundleName}: run manifest lists actions.json ${listed.length} times`);
  const actionsSha = sha256(actionsBuf);
  if (listed[0].sha256 !== actionsSha) fail(`${bundleName}: actions.json sha256 ${actionsSha} differs from the run manifest ${listed[0].sha256}`);

  const actions = record.actions;
  if (!Array.isArray(actions) || !Array.isArray(manifest.actions)) fail(`${bundleName}: actions[] missing`);
  const key = (a) => [a.position, a.class, a.outcome, a.is_retry, a.description].join('\u0000');
  if (actions.map(key).join('\u0001') !== manifest.actions.map(key).join('\u0001')) fail(`${bundleName}: actions.json and run manifest actions[] disagree`);
  if (actions.some((a) => a.is_retry === true)) fail(`${bundleName}: is_retry true observed -- no branch implemented, do not guess`);
  actions.forEach((a, i) => { if (a.position !== i + 1) fail(`${bundleName}: action positions are not 1..n`); });

  return {
    condition: cond,
    execution_id: executionId,
    attempt,
    run_id: bundleName,
    run_status: manifest.outcome.status,
    n_actions: actions.length,
    n_retries: 0,
    classes: actions.map((a) => a.class),
    outcomes: actions.map((a) => a.outcome),
    run_manifest_sha256: sha256(manifestBuf),
    actions_json_sha256: actionsSha,
  };
}

function describe(values) {
  const xs = [...values].sort((a, b) => a - b);
  return {
    n: xs.length,
    min: xs[0],
    q1: quantile(xs, 0.25),
    median: quantile(xs, 0.5),
    q3: quantile(xs, 0.75),
    max: xs[xs.length - 1],
    frequency: frequency(xs),
  };
}

function main() {
  const tree = git(['rev-parse', `HEAD:${RAW_DIR}`]);
  if (tree !== EXPECTED_RAW_TREE) fail(`raw-data tree ${tree} differs from the pinned ${EXPECTED_RAW_TREE}`);
  if (git(['status', '--porcelain', '--untracked-files=all', '--', RAW_DIR]) !== '') fail(`${RAW_DIR} has uncommitted changes`);
  for (const a of ATTEMPTS_WITHOUT_BUNDLE) {
    const rec = fs.readFileSync(path.join(REPO_ROOT, a.dispatch_record), 'utf8');
    if (!rec.includes(String(a.github_run_id))) fail(`${a.dispatch_record} does not name run ${a.github_run_id}`);
  }

  const runs = [];
  for (const sutDirName of fs.readdirSync(path.join(REPO_ROOT, RAW_DIR)).sort()) {
    if (sutDirName === '.gitattributes') continue; // "* -text": byte-exact storage, the only file at the root of the campaign tree
    const sutPath = path.join(REPO_ROOT, RAW_DIR, sutDirName);
    if (!fs.statSync(sutPath).isDirectory()) fail(`unexpected file ${sutDirName} in ${RAW_DIR}`);
    for (const bundleName of fs.readdirSync(sutPath).sort()) runs.push(readBundle(sutDirName, bundleName));
  }
  if (runs.length !== CONDITIONS.length * EXECUTIONS_PER_CONDITION) fail(`expected ${CONDITIONS.length * EXECUTIONS_PER_CONDITION} bundles, got ${runs.length}`);

  const perCondition = {};
  for (const cond of CONDITIONS) {
    const own = runs.filter((r) => r.condition.condition_id === cond.condition_id);
    const ids = own.map((r) => r.execution_id).sort();
    const expectedIds = Array.from({ length: EXECUTIONS_PER_CONDITION }, (_, i) => 'EX' + String(i + 1).padStart(4, '0'));
    if (ids.join() !== expectedIds.join()) fail(`${cond.condition_id}: executions are not exactly EX0001..EX0050 once each`);

    const reached = own.filter((r) => r.n_actions > 0);
    const sequences = frequency(reached.map((r) => `${r.classes.join(' | ')} || ${r.outcomes.join(' | ')}`));
    perCondition[cond.condition_id] = {
      sut_id: cond.sut_id,
      surface: cond.surface,
      reset_mechanism: cond.reset_mechanism,
      predeclared_reset_side_required_actions: cond.predeclared,
      n_bundles: own.length,
      n_reached_reset_action: reached.length,
      n_without_reset_action: own.length - reached.length,
      attempt_frequency: frequency(own.map((r) => r.attempt)),
      run_outcome_status_frequency: frequency(own.map((r) => r.run_status)),
      required_actions_reset: describe(reached.map((r) => r.n_actions)),
      action_class_and_outcome_sequences: sequences,
      n_retries: own.reduce((s, r) => s + r.n_retries, 0),
    };
  }

  const comparisons = CONFIRMATORY_BASELINES.map((b) => {
    const omni = perCondition[OMNIPIZZA_CONDITION];
    const base = perCondition[b.baseline_condition];
    const omniCount = omni.required_actions_reset.median;
    const baseCount = base.required_actions_reset.median;
    const diff = omniCount - baseCount;
    return {
      comparison_id: `H2 reset side (${OMNIPIZZA} vs ${b.baseline_sut}), ${SCENARIO_ID}, WEB`,
      classification: 'CONFIRMATORY (H2)',
      omnipizza_condition: OMNIPIZZA_CONDITION,
      baseline: b.baseline_sut,
      baseline_condition: b.baseline_condition,
      pairing_unit: 'canonical_scenario_id',
      canonical_scenario_id: SCENARIO_ID,
      n_pairs: 1,
      n_executions_per_arm: { [OMNIPIZZA]: omni.required_actions_reset.n, [b.baseline_sut]: base.required_actions_reset.n },
      per_scenario_count_omnipizza: omniCount,
      per_scenario_count_baseline: baseCount,
      paired_difference_original_unit: diff,
      paired_difference_definition: 'per-scenario count of SUT-01 minus per-scenario count of the baseline, in Required Actions (reset)',
      direction: diff < 0 ? 'OMNIPIZZA_FEWER' : diff > 0 ? 'OMNIPIZZA_MORE' : 'EQUAL',
      wilcoxon_signed_rank_applied: false,
      wilcoxon_reason: 'one canonical scenario gives one pair; the plan applies the test only where the number of non-tied pairs is adequate and otherwise reports the comparison descriptively (statistical-analysis-plan-v1.md, sections 3 and 4.3)',
      confidence_interval: null,
      confidence_interval_reason: 'not estimable from one pair; the executions within a condition are repetitions of one scenario, not pairs',
      rank_biserial_correlation: null,
      rank_biserial_reason: 'reported only where the Wilcoxon signed-rank test is applied (statistical-analysis-plan-v1.md, section 3, effect sizes)',
    };
  });

  const result = {
    study_id: 'EUS-2026-001',
    hypothesis_id: 'H2',
    part: 'reset side (E03 contribution); the establish side has no data',
    frozen_hypothesis_text_verbatim: 'H2: OmniPizza will require fewer preparation/reset actions to establish equivalent target states than the general-purpose baselines. (protocol/study-design-v1.md, section 6)',
    campaign_id: 'E03-resetability',
    campaign_state_at_analysis: 'FROZEN',
    raw_data: {
      path: RAW_DIR,
      git_tree: EXPECTED_RAW_TREE,
      pinned_at_commit: FREEZE_COMMIT,
      n_bundles: runs.length,
      n_conditions: CONDITIONS.length,
      executions_per_condition: EXECUTIONS_PER_CONDITION,
      per_run_table: 'derived-data/E03-resetability/required-actions-reset-per-attempt.csv',
      attempts_without_bundle: ATTEMPTS_WITHOUT_BUNDLE,
    },
    configuration: {
      source: 'experiments/E03-resetability/README.md, "Campaign configuration", subsection "CONFIRMATORY comparisons"',
      campaign_start_commit: START_COMMIT,
      section_sha256_at_start: CONFIG_SECTION_SHA256,
      canonical_scenario: SCENARIO_ID,
      confirmatory_pairs: comparisons.map((c) => `${OMNIPIZZA} vs ${c.baseline}`),
      exploratory_not_computed: 'comparisons involving SUT-04 or SUT-05 stay EXPLORATORY and are not computed here; their conditions appear only in the per-condition descriptives',
    },
    variable_definition: 'Required Actions (reset) per execution = number of entries of actions[] of the bundle (experiments/E03-resetability/executor/README.md, section 3, item 1), computed over the attempts that reached the reset action; run outcome.status frequencies are reported beside; the count does not depend on outcome.status.',
    method: 'Descriptive branch of the plan (statistical-analysis-plan-v1.md, sections 3 and 4.3): per-condition count distribution with median and interquartile range (quantile type 7); paired per-scenario difference in the original unit for each confirmatory pair; no test, no bootstrap, no standardized effect size. The branch is the plan\'s own fallback for a design with one canonical scenario, fixed in the frozen plan and not chosen after seeing the data.',
    per_condition: perCondition,
    comparisons,
    support_determination: null,
    support_determination_note: 'Not computed: protocol/statistical-analysis-plan-v1.md and protocol/study-design-v1.md define no support/non-support satisfaction criterion for H2 (contrast H3).',
    limitations: [
      'Reset side only: H2 concerns preparation and reset actions to establish equivalent target states (E02 establish, E03 reset); E02 is NOT_STARTED, so the establish side has no data and this output is not an evaluation of H2.',
      'One canonical scenario (CS-001) gives one pair per comparison: no Wilcoxon signed-rank test, no interval, and no rank-biserial correlation can be computed. Under statistical-analysis-plan-v1.md, section 5, a comparison that lacks an interval is not reported as a result; the two comparison rows are the descriptive observations that the plan\'s fallback branch yields, with the interval stated as not estimable, and they are not offered as inferential results.',
      'Within every condition the count of Required Actions (reset) is the same in all executions, so the median and the interquartile range summarize a constant; the repetitions carry no information about the spread of the count.',
      'The count is of the actions performed by the reset procedure whatever the run outcome.status; the status frequencies are reported beside it. The count is the realized count of the locked implementation: the web conditions of SUT-01 and SUT-02 include a navigation action under the uniform navigation rule and the surface-control rule (executor README, section 3, items 3 and 10; sections 4.2 and 4.3), and the predeclared count of every condition is carried through for reference.',
      'Counts come from the locked implementation of one canonical scenario on the seven web/api conditions (SUT-02 and SUT-03 on the web surface only); the two mobile conditions are blocked and have no data; SUT-06 is NOT_COMPARABLE on CS-001 and has no condition. The study has six ecosystems, a disclosed small-N design limitation (statistical-analysis-plan-v1.md, section 4.1).',
      'Dispatched attempts: 352 (350 bundles and the two attempts of attempts_without_bundle, which failed before the executor ran and left no run manifest); the two corresponding executions are represented by their imported attempt 2.',
    ],
  };

  const tableHeader = ['condition_id', 'sut_id', 'surface', 'execution_id', 'attempt', 'run_id', 'run_outcome_status', 'required_actions_reset', 'n_retries', 'action_classes', 'action_outcomes', 'run_manifest_sha256', 'actions_json_sha256'];
  const tableRows = runs
    .slice()
    .sort((a, b) => (a.run_id < b.run_id ? -1 : a.run_id > b.run_id ? 1 : 0))
    .map((r) => [r.condition.condition_id, r.condition.sut_id, r.condition.surface, r.execution_id, r.attempt, r.run_id, r.run_status, r.n_actions, r.n_retries, r.classes.join('|'), r.outcomes.join('|'), r.run_manifest_sha256, r.actions_json_sha256].join(','));
  const tableText = [tableHeader.join(','), ...tableRows].join('\n') + '\n';

  const tableDir = path.join(REPO_ROOT, 'derived-data/E03-resetability');
  const resultDir = path.join(REPO_ROOT, 'derived-data/h2-analysis');
  fs.mkdirSync(tableDir, { recursive: true });
  fs.mkdirSync(resultDir, { recursive: true });
  const tablePath = path.join(tableDir, 'required-actions-reset-per-attempt.csv');
  const resultPath = path.join(resultDir, 'H2-reset-result.json');
  fs.writeFileSync(tablePath, tableText);
  fs.writeFileSync(resultPath, JSON.stringify(result, null, 2) + '\n');

  console.log('OK: wrote ' + tablePath);
  console.log('OK: wrote ' + resultPath);
  console.log('per-run table sha256: ' + sha256(fs.readFileSync(tablePath)));
  console.log('result file sha256: ' + sha256(fs.readFileSync(resultPath)));
}

main();
