#!/usr/bin/env node
'use strict';
/*
 * analysis/h2-analysis/compute-h2-establish.js
 *
 * H2 analysis, establish side only, for study EUS-2026-001, campaign E02-state-establishment (FROZEN, 500 imported
 * bundles). Sibling of analysis/h2-analysis/compute-h2.js (reset side, E03), which is not edited: it is pinned by blob
 * sha in its provenance sidecar.
 *
 * Implements the H2 procedure frozen in protocol/statistical-analysis-plan-v1.md, section 4.3:
 *   "Required Actions (establish; reset) per COMPARABLE canonical scenario" -- ecosystem pairs SUT-01 vs SUT-02 and
 *   SUT-01 vs SUT-03 -- "Paired per-scenario differences; Wilcoxon signed-rank where pairing is adequate, otherwise
 *   descriptive; effect size per Section 3."
 * and the confirmatory comparisons locked at the campaign START (experiments/E02-state-establishment/README.md,
 * "Campaign configuration", subsection "CONFIRMATORY comparisons"): SUT-01 versus SUT-02 and SUT-01 versus SUT-03, on
 * Required Actions (establish) per COMPARABLE canonical scenario, paired on the WEB surface; the pairs are CS-003 and
 * CS-004 (two pairs per comparison); "this campaign contributes the establish side only"; the method is descriptive,
 * without a significance test; "No comparison involving SUT-04 or SUT-05, and no API comparison, is pre-registered
 * CONFIRMATORY; they stay EXPLORATORY." The classification of the two comparisons is written below from that section;
 * it is never derived from the data (analysis/README.md, rule 9).
 *
 * Variable: Required Actions (establish) of one execution = the number of entries of `actions[]` of its bundle, as
 * recorded (experiments/E02-state-establishment/executor/README.md, section 3: authentication and the verification read
 * are counted actions; the precondition, the starting-state check, provisioning, and evidence capture are not). The
 * recorded `counted_action_count` of actions.json must equal that number (checked, never substituted). Statistics are
 * computed over the attempts that reached the verification, defined operationally as: at least one entry of `actions[]`
 * has `verification` true. Run outcome.status frequencies (SUCCESS, FAILURE, INCONCLUSIVE, ABORTED, ERROR) are reported
 * beside them and nothing is dropped (campaign configuration, "Sample size per condition"). The count does not depend on
 * outcome.status.
 *
 * Pairing unit: canonical_scenario_id (statistical-analysis-plan-v1.md, sections 3 and 4.1). Each WEB comparison has two
 * pairs, CS-003 and CS-004: the per-scenario count of an ecosystem is the median of the Required Actions (establish)
 * over the executions of its WEB condition for that scenario. Two pairs do not justify the Wilcoxon signed-rank test
 * (the smallest two-sided exact p-value with n non-tied pairs is 2 x 2^-n, 0.5 at n = 2, derived in the campaign
 * configuration), so the comparison is reported descriptively, the plan's own fallback branch, pre-registered in the
 * configuration; no p-value, no Holm correction, no bootstrap, and no rank-biserial correlation is computed. Executions
 * of different ecosystems are independent dispatches and are never paired by execution id.
 *
 * No support/non-support criterion is frozen for H2 (contrast H3); none is computed or emitted.
 *
 * Duration (`establishment_duration_s`) is a secondary variable of the setup-effort protocol, not the H2 variable
 * (statistical-analysis-plan-v1.md, section 4.3); it is not read here.
 *
 * Fails loudly on: a raw-data tree that differs from the pinned tree or has uncommitted changes; a "Campaign
 * configuration" section that differs from the pinned digest (at HEAD and at the START commit); a missing, extra, or
 * duplicated execution; an attempt number other than 1 (except the three executions whose attempt 1 left no bundle); a
 * bundle whose directory name, run manifest, or actions.json disagree; an actions.json whose sha256 differs from the one
 * listed in its run manifest; a run-level field that differs from the configuration (campaign, scenario, environment
 * type, prompt version, declared establishment mechanisms); any action with is_retry true (none observed; no branch is
 * implemented for it); a condition other than the ten expected; a dispatch record that does not name an attempt without
 * bundle.
 *
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only (fs, path, crypto,
 * child_process) -- no package manager, no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

const REPO_ROOT = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();

const RAW_DIR = 'raw-data/E02-state-establishment';
const EXPECTED_RAW_TREE = 'c7beaebe6b290c23e0f5ae49af7fbcd95828ae5b';
const FREEZE_COMMIT = '1b0442f740e8059ede681fe6a0fa21a31bcf73dd';
const START_COMMIT = '1e308f440e2a7cb29c3467a8738dd2bd881f3430';
const CONFIG_SECTION_SHA256 = 'f8f090e3d81237eda87f78fcecadd89cb58525b4b662cadd0bdfffb1260d1094';
const CAMPAIGN_README = 'experiments/E02-state-establishment/README.md';

const CAMPAIGN_ID = 'E02-state-establishment';
const PROMPT_VERSION = 'ORCHESTRATOR-E02-state-establishment-v1';
const EXECUTIONS_PER_CONDITION = 50;
const OMNIPIZZA = 'SUT-01';
const RUN_STATUSES = ['SUCCESS', 'FAILURE', 'INCONCLUSIVE', 'ABORTED', 'ERROR'];

// Conditions table of the locked configuration (the ten executable conditions); mechanisms = the column "Establishment
// mechanisms declared by the realization".
const CONDITIONS = [
  { condition_id: 'E02-CS003-SUT01-WEB', sut_id: 'SUT-01', surface: 'WEB', scenario: 'CS-003', starting_state: 'CLEAN_SESSION', mechanisms: ['PREDEFINED_ACCOUNT', 'API_SEED', 'APP_STATE_CONTROL', 'DIRECT_ROUTE'] },
  { condition_id: 'E02-CS003-SUT01-API', sut_id: 'SUT-01', surface: 'API', scenario: 'CS-003', starting_state: 'CLEAN_SESSION', mechanisms: ['PREDEFINED_ACCOUNT', 'API_SEED'] },
  { condition_id: 'E02-CS004-SUT01-WEB', sut_id: 'SUT-01', surface: 'WEB', scenario: 'CS-004', starting_state: 'SEEDED_BUSINESS_STATE', mechanisms: ['PREDEFINED_ACCOUNT', 'API_SEED', 'APP_STATE_CONTROL', 'DIRECT_ROUTE'] },
  { condition_id: 'E02-CS003-SUT02-WEB', sut_id: 'SUT-02', surface: 'WEB', scenario: 'CS-003', starting_state: 'CLEAN_SESSION', mechanisms: ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'] },
  { condition_id: 'E02-CS004-SUT02-WEB', sut_id: 'SUT-02', surface: 'WEB', scenario: 'CS-004', starting_state: 'SEEDED_BUSINESS_STATE', mechanisms: ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'] },
  { condition_id: 'E02-CS003-SUT03-WEB', sut_id: 'SUT-03', surface: 'WEB', scenario: 'CS-003', starting_state: 'CLEAN_SESSION', mechanisms: ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'] },
  { condition_id: 'E02-CS004-SUT03-WEB', sut_id: 'SUT-03', surface: 'WEB', scenario: 'CS-004', starting_state: 'SEEDED_BUSINESS_STATE', mechanisms: ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'] },
  { condition_id: 'E02-CS003-SUT04-WEB', sut_id: 'SUT-04', surface: 'WEB', scenario: 'CS-003', starting_state: 'CLEAN_SESSION', mechanisms: ['PREDEFINED_ACCOUNT', 'DIRECT_ROUTE', 'UI_FLOW'] },
  { condition_id: 'E02-CS003-SUT04-API', sut_id: 'SUT-04', surface: 'API', scenario: 'CS-003', starting_state: 'CLEAN_SESSION', mechanisms: ['PREDEFINED_ACCOUNT', 'API_SEED'] },
  { condition_id: 'E02-CS003-SUT05-API', sut_id: 'SUT-05', surface: 'API', scenario: 'CS-003', starting_state: 'CLEAN_SESSION', mechanisms: ['PREDEFINED_ACCOUNT', 'API_SEED'] },
];

// CONFIRMATORY (H2): written from the campaign configuration, subsection "CONFIRMATORY comparisons".
const CONFIRMATORY_BASELINES = ['SUT-02', 'SUT-03'];
const CONFIRMATORY_SCENARIOS = ['CS-003', 'CS-004'];

// Dispatched attempts that left no bundle; their dispatch records name the runs. The attempt-2 import of each of the
// three executions is the only bundle of that execution.
const ATTEMPTS_WITHOUT_BUNDLE = [
  { condition_id: 'E02-CS003-SUT01-WEB', execution_id: 'EX0008', attempt: 1, github_run_id: 43095065967 },
  { condition_id: 'E02-CS003-SUT02-WEB', execution_id: 'EX0007', attempt: 1, github_run_id: 43094844376 },
  { condition_id: 'E02-CS003-SUT03-WEB', execution_id: 'EX0005', attempt: 1, github_run_id: 43094956611 },
];

const BUNDLE_NAME = /^(E02-CS00[34]-SUT0[1-5]-(?:WEB|API))__(EX\d{4})__A(\d+)$/;

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

// "## Campaign configuration" up to (not including) "## Current status", right-trimmed plus one newline.
function configSectionSha256(text) {
  const i = text.indexOf('## Campaign configuration');
  const j = text.indexOf('## Current status');
  if (i < 0 || j < i) fail(`${CAMPAIGN_README}: configuration section boundaries not found`);
  return sha256(Buffer.from(text.slice(i, j).replace(/\s+$/, '') + '\n', 'utf8'));
}

function readBundle(sutDirName, bundleName) {
  const m = bundleName.match(BUNDLE_NAME);
  if (!m) fail(`unexpected bundle name ${bundleName}`);
  const [, conditionId, executionId, attemptText] = m;
  const cond = CONDITIONS.find((c) => c.condition_id === conditionId);
  if (!cond) fail(`${bundleName}: condition ${conditionId} is not one of the ten expected conditions`);
  if (cond.sut_id !== sutDirName) fail(`${bundleName}: stored under ${sutDirName}, condition belongs to ${cond.sut_id}`);

  const relDir = `${RAW_DIR}/${sutDirName}/${bundleName}`;
  const manifestBuf = fs.readFileSync(path.join(REPO_ROOT, relDir, 'run-manifest.json'));
  const actionsBuf = fs.readFileSync(path.join(REPO_ROOT, relDir, 'actions.json'));
  const manifest = JSON.parse(manifestBuf.toString('utf8'));
  const record = JSON.parse(actionsBuf.toString('utf8'));
  const attempt = Number(attemptText);

  const wasAttempt1WithoutBundle = ATTEMPTS_WITHOUT_BUNDLE.some((a) => a.condition_id === conditionId && a.execution_id === executionId);
  if (attempt !== (wasAttempt1WithoutBundle ? 2 : 1)) fail(`${bundleName}: attempt ${attempt} is not the expected one`);

  if (manifest.campaign_id !== CAMPAIGN_ID || manifest.condition !== conditionId) fail(`${bundleName}: run manifest campaign/condition mismatch`);
  if (manifest.experiment_id !== conditionId.split('-SUT')[0]) fail(`${bundleName}: run manifest experiment_id ${manifest.experiment_id}`);
  if (manifest.attempt !== attempt) fail(`${bundleName}: run manifest attempt ${manifest.attempt} differs from the directory`);
  if (manifest.sut_id !== sutDirName) fail(`${bundleName}: run manifest sut_id ${manifest.sut_id}`);
  if (manifest.scenario !== cond.scenario) fail(`${bundleName}: run manifest scenario ${manifest.scenario}, expected ${cond.scenario}`);
  if (manifest.environment_type !== 'SELF_HOSTED') fail(`${bundleName}: run manifest environment_type ${manifest.environment_type}`);
  if (manifest.prompt_version !== PROMPT_VERSION) fail(`${bundleName}: run manifest prompt_version ${manifest.prompt_version}`);
  if (manifest.run_id !== bundleName || record.run_id !== bundleName) fail(`${bundleName}: run_id mismatch (manifest ${manifest.run_id}, actions.json ${record.run_id})`);
  if ([...manifest.establishment_mechanisms].sort().join() !== [...cond.mechanisms].sort().join()) fail(`${bundleName}: establishment_mechanisms ${manifest.establishment_mechanisms} differ from the configuration`);
  if (!RUN_STATUSES.includes(manifest.outcome.status)) fail(`${bundleName}: unexpected outcome.status ${manifest.outcome.status}`);

  const listed = (manifest.artifacts || []).filter((a) => a.path === `${relDir}/actions.json`);
  if (listed.length !== 1) fail(`${bundleName}: run manifest lists actions.json ${listed.length} times`);
  const actionsSha = sha256(actionsBuf);
  if (listed[0].sha256 !== actionsSha) fail(`${bundleName}: actions.json sha256 ${actionsSha} differs from the run manifest ${listed[0].sha256}`);

  const actions = record.actions;
  if (!Array.isArray(actions) || !Array.isArray(manifest.actions)) fail(`${bundleName}: actions[] missing`);
  // The run-manifest action records carry no mechanism field; compare the fields that both carry.
  const key = (a) => [a.position, a.class, a.outcome, a.is_retry, a.description].join('\u0000');
  if (actions.map(key).join('\u0001') !== manifest.actions.map(key).join('\u0001')) fail(`${bundleName}: actions.json and run manifest actions[] disagree`);
  if (actions.some((a) => a.is_retry === true)) fail(`${bundleName}: is_retry true observed -- no branch implemented, do not guess`);
  if (actions.some((a) => typeof a.verification !== 'boolean')) fail(`${bundleName}: an action has a non-boolean verification flag`);
  actions.forEach((a, i) => { if (a.position !== i + 1) fail(`${bundleName}: action positions are not 1..n`); });
  if (record.counted_action_count !== actions.length) fail(`${bundleName}: counted_action_count ${record.counted_action_count} differs from the ${actions.length} entries of actions[]`);
  for (const f of [conditionId, executionId, bundleName, ...actions.map((a) => a.class), ...actions.map((a) => a.outcome)]) {
    if (/[",\r\n]/.test(f)) fail(`${bundleName}: a field of the per-run table contains a comma, a quote, or a line break`);
  }

  return {
    condition: cond,
    execution_id: executionId,
    attempt,
    run_id: bundleName,
    run_status: manifest.outcome.status,
    n_actions: actions.length,
    n_verification_actions: actions.filter((a) => a.verification).length,
    n_retries: 0,
    classes: actions.map((a) => a.class),
    outcomes: actions.map((a) => a.outcome),
    run_manifest_sha256: sha256(manifestBuf),
    actions_json_sha256: actionsSha,
  };
}

// Reads the dispatch record of an attempt without bundle and returns what the record itself says about it.
function readAttemptWithoutBundle(a) {
  const rel = `manifests/e02-measured-dispatch/${a.condition_id}.jsonl`;
  const events = fs.readFileSync(path.join(REPO_ROOT, rel), 'utf8').split('\n').filter((l) => l.trim() !== '').map((l) => JSON.parse(l));
  const identity = events.find((e) => e.event === 'RUN_IDENTITY_RECORDED' && e.execution_id === a.execution_id && e.attempt === a.attempt && e.run_id === a.github_run_id);
  const concluded = events.find((e) => e.event === 'RUN_CONCLUDED_WITHOUT_BUNDLE_NOT_IMPORTED' && e.execution_id === a.execution_id && e.attempt === a.attempt);
  if (!identity) fail(`${rel} has no RUN_IDENTITY_RECORDED event for run ${a.github_run_id}`);
  if (!concluded) fail(`${rel} has no RUN_CONCLUDED_WITHOUT_BUNDLE_NOT_IMPORTED event for ${a.execution_id} attempt ${a.attempt}`);
  return {
    ...a,
    dispatch_record: rel,
    workflow_conclusion: concluded.workflow_conclusion,
    frozen_executor_step_of_the_measured_job: concluded.frozen_executor_step_of_the_measured_job,
    bundle_artifact: concluded.bundle_artifact,
  };
}

function main() {
  const tree = git(['rev-parse', `HEAD:${RAW_DIR}`]);
  if (tree !== EXPECTED_RAW_TREE) fail(`raw-data tree ${tree} differs from the pinned ${EXPECTED_RAW_TREE}`);
  if (git(['status', '--porcelain', '--untracked-files=all', '--', RAW_DIR]) !== '') fail(`${RAW_DIR} has uncommitted changes`);
  const shaNow = configSectionSha256(fs.readFileSync(path.join(REPO_ROOT, CAMPAIGN_README), 'utf8'));
  const shaStart = configSectionSha256(git(['show', `${START_COMMIT}:${CAMPAIGN_README}`]));
  if (shaNow !== CONFIG_SECTION_SHA256) fail(`campaign configuration section sha256 ${shaNow} differs from the pinned ${CONFIG_SECTION_SHA256}`);
  if (shaStart !== CONFIG_SECTION_SHA256) fail(`campaign configuration section at the START commit has sha256 ${shaStart}`);
  const attemptsWithoutBundle = ATTEMPTS_WITHOUT_BUNDLE.map(readAttemptWithoutBundle);

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

    const reached = own.filter((r) => r.n_verification_actions > 0);
    const sequences = frequency(reached.map((r) => `${r.classes.join(' | ')} || ${r.outcomes.join(' | ')}`));
    perCondition[cond.condition_id] = {
      sut_id: cond.sut_id,
      surface: cond.surface,
      canonical_scenario_id: cond.scenario,
      starting_state: cond.starting_state,
      declared_establishment_mechanisms: cond.mechanisms,
      n_bundles: own.length,
      n_reached_verification: reached.length,
      n_without_verification: own.length - reached.length,
      attempt_frequency: frequency(own.map((r) => r.attempt)),
      run_outcome_status_frequency: frequency(own.map((r) => r.run_status)),
      required_actions_establish: describe(reached.map((r) => r.n_actions)),
      verification_flagged_actions_per_run_frequency: frequency(own.map((r) => r.n_verification_actions)),
      action_class_and_outcome_sequences: sequences,
      n_retries: own.reduce((s, r) => s + r.n_retries, 0),
    };
  }

  const comparisons = CONFIRMATORY_BASELINES.map((baselineSut) => {
    const pairs = CONFIRMATORY_SCENARIOS.map((scenario) => {
      const omniCondition = CONDITIONS.find((c) => c.sut_id === OMNIPIZZA && c.surface === 'WEB' && c.scenario === scenario).condition_id;
      const baseCondition = CONDITIONS.find((c) => c.sut_id === baselineSut && c.surface === 'WEB' && c.scenario === scenario).condition_id;
      const omni = perCondition[omniCondition].required_actions_establish;
      const base = perCondition[baseCondition].required_actions_establish;
      const diff = omni.median - base.median;
      return {
        canonical_scenario_id: scenario,
        omnipizza_condition: omniCondition,
        baseline_condition: baseCondition,
        n_executions_per_arm: { [OMNIPIZZA]: omni.n, [baselineSut]: base.n },
        per_scenario_count_omnipizza: omni.median,
        per_scenario_count_baseline: base.median,
        paired_difference_original_unit: diff,
        direction: diff < 0 ? 'OMNIPIZZA_FEWER' : diff > 0 ? 'OMNIPIZZA_MORE' : 'EQUAL',
      };
    });
    const diffs = pairs.map((p) => p.paired_difference_original_unit).sort((a, b) => a - b);
    const medianDiff = quantile(diffs, 0.5);
    return {
      comparison_id: `H2 establish side (${OMNIPIZZA} vs ${baselineSut}), ${CONFIRMATORY_SCENARIOS.join(' and ')}, WEB`,
      classification: 'CONFIRMATORY (H2)',
      baseline: baselineSut,
      pairing_unit: 'canonical_scenario_id',
      n_pairs: pairs.length,
      pairs,
      paired_difference_definition: 'per-scenario count of SUT-01 minus per-scenario count of the baseline, in Required Actions (establish); the per-scenario count of an ecosystem is the median over the executions of its WEB condition for that scenario',
      median_paired_difference_original_unit: medianDiff,
      direction_of_median_difference: medianDiff < 0 ? 'OMNIPIZZA_FEWER' : medianDiff > 0 ? 'OMNIPIZZA_MORE' : 'EQUAL',
      wilcoxon_signed_rank_applied: false,
      wilcoxon_reason: `two canonical scenarios give two pairs; the smallest two-sided exact p-value of the test with n non-tied pairs is 2 x 2^-n, ${2 * Math.pow(2, -pairs.length)} at n = ${pairs.length}, derived in the campaign configuration; the method is descriptive by the plan's own fallback branch (statistical-analysis-plan-v1.md, sections 3 and 4.3) and was pre-registered in the configuration before the first dispatch`,
      min_two_sided_exact_p_at_n_pairs: 2 * Math.pow(2, -pairs.length),
      confidence_interval: null,
      confidence_interval_reason: 'not estimable from two pairs; the executions within a condition are repetitions of one scenario, not pairs',
      rank_biserial_correlation: null,
      rank_biserial_reason: 'reported only where the Wilcoxon signed-rank test is applied (statistical-analysis-plan-v1.md, section 3, effect sizes)',
    };
  });

  const result = {
    study_id: 'EUS-2026-001',
    hypothesis_id: 'H2',
    part: 'establish side (E02 contribution); the reset side is in derived-data/h2-analysis/H2-reset-result.json',
    frozen_hypothesis_text_verbatim: 'H2: OmniPizza will require fewer preparation/reset actions to establish equivalent target states than the general-purpose baselines. (protocol/study-design-v1.md, section 6)',
    campaign_id: CAMPAIGN_ID,
    campaign_state_at_analysis: 'FROZEN',
    raw_data: {
      path: RAW_DIR,
      git_tree: EXPECTED_RAW_TREE,
      pinned_at_commit: FREEZE_COMMIT,
      n_bundles: runs.length,
      n_conditions: CONDITIONS.length,
      executions_per_condition: EXECUTIONS_PER_CONDITION,
      per_run_table: 'derived-data/E02-state-establishment/required-actions-establish-per-attempt.csv',
      attempts_without_bundle: attemptsWithoutBundle,
    },
    configuration: {
      source: `${CAMPAIGN_README}, "Campaign configuration", subsection "CONFIRMATORY comparisons"`,
      campaign_start_commit: START_COMMIT,
      section_sha256_at_start: CONFIG_SECTION_SHA256,
      canonical_scenarios_in_confirmatory_pairs: CONFIRMATORY_SCENARIOS,
      confirmatory_pairs: comparisons.map((c) => `${OMNIPIZZA} vs ${c.baseline}`),
      exploratory_not_computed: 'comparisons involving SUT-04 or SUT-05, and every API comparison, stay EXPLORATORY and are not computed here; their conditions appear only in the per-condition descriptives',
    },
    variable_definition: 'Required Actions (establish) per execution = number of entries of actions[] of the bundle as recorded (experiments/E02-state-establishment/executor/README.md, section 3; authentication and the verification read are counted actions), computed over the attempts that reached the verification, defined operationally as at least one actions[] entry with verification true; run outcome.status frequencies are reported beside; the count does not depend on outcome.status; the recorded counted_action_count equals the count in every bundle.',
    method: 'Descriptive branch of the plan (statistical-analysis-plan-v1.md, sections 3 and 4.3), pre-registered in the campaign configuration, "CONFIRMATORY comparisons": per-condition count distribution with median and interquartile range (quantile type 7); for each of the two CONFIRMATORY (H2) comparisons, SUT-01 vs SUT-02 and SUT-01 vs SUT-03 on the WEB surface, the per-scenario counts of CS-003 and CS-004, their paired differences in the original unit, and the median of the two differences; no test, no p-value (so no Holm correction), no bootstrap, no standardized effect size. The branch is fixed by the plan and the configuration, not chosen after seeing the data.',
    per_condition: perCondition,
    comparisons,
    support_determination: null,
    support_determination_note: 'Not computed: protocol/statistical-analysis-plan-v1.md and protocol/study-design-v1.md define no support/non-support satisfaction criterion for H2 (contrast H3).',
    limitations: [
      'Establish side only: H2 concerns preparation and reset actions to establish equivalent target states (E02 establish, E03 reset). The reset side is in H2-reset-result.json on a different canonical scenario (CS-001); the two sides cover different scenarios, cannot be paired with one another, and are not combined, added, or averaged here; each campaign contributes one side. This output alone is not an evaluation of H2.',
      'Two canonical scenarios (CS-003 and CS-004) give two pairs per comparison: no Wilcoxon signed-rank test, interval, or rank-biserial correlation can be computed. Under statistical-analysis-plan-v1.md, section 5, a comparison that lacks an interval is not reported as a result; the two comparison rows are the descriptive observations that the plan\'s fallback branch yields, with the interval stated as not estimable, and they are not offered as inferential results.',
      'The count is the realized count of the locked implementation (run-condition.sh sha256 d0b1bbb9d3014fedb0edaa58186b1cfb2d52759dfd67c2bc1c218c7f45db5200, which locks the whole implementation), whose counting conventions follow protocol/setup-effort-v2.md and the executor README, section 3: it counts the first page load of the run (HD-15), the authentication, and the verification read; it does not count the precondition, the starting-state check, or provisioning. The per-condition sequences of action classes and outcomes show the composition of each count; this analysis does not interpret them.',
      'Required Actions (establish) counts per execution, whatever the run outcome.status; every run outcome.status is reported beside it. The count is a count of counted operations, not of effort, time, or difficulty; duration (establishment_duration_s) is a secondary variable of the setup-effort protocol, is not the H2 variable, and is not analyzed here (it would need the BCa bootstrap of the plan, with a recorded seed).',
      'A fresh controlled instance was provisioned for every run (HD-R, disclosed in the configuration), so the between-run reset is not a counted action in any condition.',
      'Counts come from the locked implementation of two canonical scenarios on the ten web/api conditions (SUT-02 and SUT-03 on the web surface only; SUT-04 on the web and API surfaces; SUT-05 on the API surface only); SUT-06 is NOT_COMPARABLE on CS-003 and CS-004 and has no condition; the two mobile surfaces have no condition. The study has six ecosystems, a disclosed small-N design limitation (statistical-analysis-plan-v1.md, section 4.1).',
      'Dispatched attempts: 503 (500 bundles and the three attempts of attempts_without_bundle, which left no bundle); the three corresponding executions are represented by their imported attempt 2, each admitted by its own further-attempt approval (manifests/e02-op-ci-18-v1.yaml).',
    ],
  };

  const tableHeader = ['condition_id', 'sut_id', 'surface', 'scenario_id', 'execution_id', 'attempt', 'run_id', 'run_outcome_status', 'required_actions_establish', 'verification_flagged_actions', 'n_retries', 'action_classes', 'action_outcomes', 'run_manifest_sha256', 'actions_json_sha256'];
  const tableRows = runs
    .slice()
    .sort((a, b) => (a.run_id < b.run_id ? -1 : a.run_id > b.run_id ? 1 : 0))
    .map((r) => [r.condition.condition_id, r.condition.sut_id, r.condition.surface, r.condition.scenario, r.execution_id, r.attempt, r.run_id, r.run_status, r.n_actions, r.n_verification_actions, r.n_retries, r.classes.join('|'), r.outcomes.join('|'), r.run_manifest_sha256, r.actions_json_sha256].join(','));
  const tableText = [tableHeader.join(','), ...tableRows].join('\n') + '\n';

  const tableDir = path.join(REPO_ROOT, 'derived-data/E02-state-establishment');
  const resultDir = path.join(REPO_ROOT, 'derived-data/h2-analysis');
  fs.mkdirSync(tableDir, { recursive: true });
  fs.mkdirSync(resultDir, { recursive: true });
  const tablePath = path.join(tableDir, 'required-actions-establish-per-attempt.csv');
  const resultPath = path.join(resultDir, 'H2-establish-result.json');
  fs.writeFileSync(tablePath, tableText);
  fs.writeFileSync(resultPath, JSON.stringify(result, null, 2) + '\n');

  console.log('OK: wrote ' + tablePath);
  console.log('OK: wrote ' + resultPath);
  console.log('per-run table sha256: ' + sha256(fs.readFileSync(tablePath)));
  console.log('result file sha256: ' + sha256(fs.readFileSync(resultPath)));
}

main();
