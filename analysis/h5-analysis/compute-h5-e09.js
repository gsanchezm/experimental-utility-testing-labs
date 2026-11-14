#!/usr/bin/env node
'use strict';
/*
 * analysis/h5-analysis/compute-h5-e09.js
 *
 * H5 analysis, accessibility contribution (E09) only, for study EUS-2026-001, campaign E09-accessibility (FROZEN, 100 imported
 * bundles). It implements, and nothing beyond, the descriptive procedure that the campaign configuration locked at the START
 * (experiments/E09-accessibility/README.md, "Campaign configuration": subsections "Conditions", "Exclusion and attribution
 * rules", "CONFIRMATORY comparisons", "Setup effort, data and analysis") and protocol/statistical-analysis-plan-v1.md, section 3
 * (Wilson 95% interval for every reported proportion), section 4.3 (H5 row: "Number of controlled non-functional ground-truth
 * conditions per ecosystem", method "Descriptive count comparison; detection rates per condition are reported per Section 5") and
 * section 5 (point estimate, interval, N, classification).
 *
 * Pre-registered rules applied here (none is chosen after seeing the data):
 *   - Detection rate of the glitch condition = detections / count of ground-truth instances, a ground-truth instance being a draw
 *     whose DOM state at scan time is ALL_EMPTY (every h2 whose data-testid starts with pizza-name- is empty). The other draws are
 *     reported beside it and never enter the denominator. The count of ground-truth instances is a result, not a configuration.
 *   - Detection (HD-5): the predeclared rule empty-heading reports at least one node whose HTML opens an h2 whose data-testid
 *     starts with pizza-name- (the -desktop suffix matches). Non-detection (HD-20) is recorded as such and no cause is inferred.
 *   - Scanner failure or page failure: INCONCLUSIVE or ERROR, excluded from the detection denominator and reported; ABORTED:
 *     reported. No execution is excluded after the fact. The total violation count is descriptive only.
 *   - Proportions carry a Wilson 95% interval without continuity correction (z = 1.959963984540054), the formula of
 *     analysis/h3-analysis/h3-metrics.js (decision D-05).
 *   - H5 count unit (HD-2): the count of controlled non-functional ground-truth conditions of SUT-01 contributed by E09 is 1;
 *     SUT-02 to SUT-05 have no condition (count 0, "no data: no ground-truth condition available"); SUT-06: "no data: modality rated
 *     Score 0 in E01 (NO_WEB_SURFACE)". Classification CONFIRMATORY (H5), descriptive; it is written below from the configuration and
 *     never derived from the data (analysis/README.md, rule 9). With SUT-02 and SUT-03 at zero conditions no pairwise detection
 *     comparison exists, and no Fisher table, risk difference, test, p-value, or support / non-support criterion is formed (none is
 *     frozen for H5).
 *   - The H5 variable of the plan spans E08, E09, E10 and E11; this script covers the E09 contribution only and says so in its output.
 *
 * The recorded classification of each bundle (run-manifest outcome) is compared with the one derived here from the evidence; any
 * disagreement is listed and makes the script exit non-zero. Nothing is interpreted: the output is counts, proportions and intervals.
 *
 * Fails loudly on: a raw-data tree that differs from the pinned tree or has uncommitted changes; a Campaign configuration section
 * that differs from the pinned digest (at HEAD and at the START commit); a missing, extra or duplicated execution; an attempt other
 * than 1; a bundle whose directory name, run manifest, or detection record disagree; a detection record whose sha256 differs from the
 * one listed in its run manifest; a predeclared rule, selector or axe-core version that differs from the configuration; a condition
 * other than the two expected.
 *
 * Usage: node analysis/h5-analysis/compute-h5-e09.js [--check]    (--check recomputes and compares with the files on disk; writes nothing)
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only; no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

const REPO = path.resolve(__dirname, '..', '..');
const RAW = 'raw-data/E09-accessibility';
const SUT_DIR = path.join(RAW, 'SUT-01');
const OUT_JSON = 'derived-data/h5-analysis/H5-e09-result.json';
const OUT_CSV = 'derived-data/E09-accessibility/detections-per-attempt.csv';
const README = 'experiments/E09-accessibility/README.md';
const START_COMMIT = 'd362b8edaf263613d80b82d7f153dd57a93b9049';                    // the E09 campaign START commit (E09-START-AUTH-01)
const FREEZE_COMMIT = '0ad90f64d156e87e02c0293dd62fe73600222bc3';                   // the E09 campaign freeze commit (E09-FREEZE-AUTH-01)
const CONFIG_SHA256 = 'a9a6fc5377ff0ab796196e20aa7b73db8c49c82f4606705b6590c2da4b51a2c4';
const Z = 1.959963984540054;
const GLITCH = 'E09-A11Y-SUT01-MISSING-NAME';
const CTRL = 'E09-CTRL-SUT01-STANDARD';
const N = 50;
const RULE = 'empty-heading';
const SELECTOR = 'h2[data-testid^="pizza-name-"]';
const AXE = '4.14.0';
const NODE_OPENS_PRODUCT_H2 = /^<h2 data-testid="pizza-name-/;   // HD-5: the HTML of the node opens an h2 whose data-testid starts with pizza-name-

const git = (...a) => execFileSync('git', ['-C', REPO, ...a], { encoding: 'utf8' }).replace(/\n$/, '');
const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const fail = (m) => { console.error('FAIL: ' + m); process.exit(2); };

function wilson(x, n) {
  if (!(n >= 1)) return null;
  const p = x / n, z2 = Z * Z, den = 1 + z2 / n;
  const c = (p + z2 / (2 * n)) / den, h = (Z * Math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))) / den;
  return [x === 0 ? 0 : Math.max(0, c - h), x === n ? 1 : Math.min(1, c + h)];   // exact bounds at x = 0 and x = n (no floating-point residue)
}
const rate = (x, n) => ({ x, n, point: n >= 1 ? x / n : null, wilson95: wilson(x, n) });

// ---- pinned inputs -------------------------------------------------------------------------------------------------
if (git('status', '--porcelain', '--', RAW)) fail('uncommitted changes under ' + RAW);
const treeHead = git('rev-parse', 'HEAD:' + RAW);
const treeFreeze = git('rev-parse', FREEZE_COMMIT + ':' + RAW);
if (treeHead !== treeFreeze) fail('the raw-data tree differs from the tree of the freeze commit');
const cfgOf = (txt) => { const i = txt.indexOf('## Campaign configuration'); if (i < 0) fail('no Campaign configuration section'); return sha(Buffer.from(txt.slice(i), 'utf8')); };
if (cfgOf(fs.readFileSync(path.join(REPO, README), 'utf8')) !== CONFIG_SHA256) fail('Campaign configuration differs from the pinned digest at HEAD');
if (cfgOf(execFileSync('git', ['-C', REPO, 'show', START_COMMIT + ':' + README], { encoding: 'utf8' })) !== CONFIG_SHA256) fail('Campaign configuration differs from the pinned digest at the START commit');
const manifestStatus = fs.readFileSync(path.join(REPO, 'manifests/study-manifest.yaml'), 'utf8').match(/- id: E09-accessibility\n\s+status: (\w+)/);
if (!manifestStatus || manifestStatus[1] !== 'FROZEN') fail('E09 is not FROZEN in the study manifest');

// ---- the 100 bundles -----------------------------------------------------------------------------------------------------
const dirs = fs.readdirSync(path.join(REPO, SUT_DIR)).filter((d) => !d.startsWith('.')).sort();
const expected = [];
for (const c of [GLITCH, CTRL]) for (let n = 1; n <= N; n++) expected.push(`${c}__EX${String(n).padStart(4, '0')}__A1`);
if (JSON.stringify(dirs) !== JSON.stringify([...expected].sort())) fail('the set of run directories is not the 100 expected');

const rows = [];
for (const d of dirs) {
  const [cond, ex, att] = d.split('__');
  const base = path.join(REPO, SUT_DIR, d);
  const man = JSON.parse(fs.readFileSync(path.join(base, 'run-manifest.json'), 'utf8'));
  const detPath = path.join(base, 'evidence/011-detection.json');
  const detBuf = fs.readFileSync(detPath);
  const det = JSON.parse(detBuf.toString('utf8'));
  if (att !== 'A1' || man.attempt !== 1) fail(d + ': attempt is not 1');
  if (man.run_id !== d || man.condition !== cond || man.campaign_id !== 'E09-accessibility' || man.sut_id !== 'SUT-01') fail(d + ': identity fields of the run manifest disagree');
  const listed = (man.artifacts || []).find((a) => a.path.endsWith('/' + d + '/evidence/011-detection.json'));
  if (!listed || listed.sha256 !== sha(detBuf)) fail(d + ': the detection record is not the one listed in the run manifest');
  if (det.predeclared_rule !== RULE || det.predeclared_selector !== SELECTOR || det.axe_version !== AXE) fail(d + ': rule, selector or axe-core version differs from the configuration');
  const nodes = Array.isArray(det.matching_nodes) ? det.matching_nodes : fail(d + ': matching_nodes is not an array');
  const productNodes = nodes.filter((n) => NODE_OPENS_PRODUCT_H2.test(n.html_prefix || '')).length;
  rows.push({
    run_id: d, condition_id: cond, execution_id: ex, workflow_outcome_status: man.outcome.status, recorded_outcome_category: man.outcome.outcome_category,
    recorded_matches_expected: man.outcome.matches_expected, dom_state: det.dom_state, body_classes: (det.body_classes || []).join('|'),
    corroboration: det.corroboration, draw_consistency: det.draw_consistency, catalog_status: det.catalog_status,
    matching_nodes: nodes.length, product_h2_nodes: productNodes, rule_nodes_total_descriptive: det.rule_nodes_total_descriptive,
  });
}

// ---- classification derived from the evidence, compared with the recorded one --------------------------------------------
const mismatches = [];
for (const r of rows) {
  const detected = r.product_h2_nodes >= 1;
  let derived;
  if (r.condition_id === GLITCH) {
    if (r.dom_state === 'ALL_EMPTY') derived = detected ? 'DETECTED' : 'NOT_DETECTED_ON_CONFIRMED_INSTANCE';
    else if (r.dom_state === 'NOT_EMPTY') derived = 'NO_GROUND_TRUTH_INSTANCE';
    else derived = 'OTHER_DRAW_' + r.dom_state;
  } else {
    derived = detected ? 'CONTROL_RULE_PRESENT' : 'CONTROL_RULE_ABSENT';
  }
  r.derived_class = derived;
  r.ground_truth_instance = r.condition_id === GLITCH && r.dom_state === 'ALL_EMPTY';
  r.detected = r.condition_id === GLITCH ? r.ground_truth_instance && detected : detected;
  const same = derived === r.recorded_outcome_category || (derived === 'NOT_DETECTED_ON_CONFIRMED_INSTANCE' && r.recorded_outcome_category !== 'DETECTED');
  if (!same) mismatches.push({ run_id: r.run_id, derived, recorded: r.recorded_outcome_category });
}

// ---- per-condition results -----------------------------------------------------------------------------------------------
const glitch = rows.filter((r) => r.condition_id === GLITCH);
const ctrl = rows.filter((r) => r.condition_id === CTRL);
const count = (arr, f) => arr.filter(f).length;
const tally = (arr, f) => arr.reduce((o, r) => { const k = f(r); o[k] = (o[k] || 0) + 1; return o; }, {});
const gt = glitch.filter((r) => r.ground_truth_instance);
const detections = count(gt, (r) => r.detected);
const glitchResult = {
  condition_id: GLITCH, n_executions: glitch.length, behavior_class_declared: 'stochastic',
  realized_draws_by_dom_state: tally(glitch, (r) => r.dom_state),
  realized_draws_by_recorded_body_class: tally(glitch, (r) => r.body_classes),
  ground_truth_instances: rate(gt.length, glitch.length),                       // the share of the 50 draws that were ground-truth instances (a result, not a configuration)
  detection_rate: rate(detections, gt.length),                                   // detections / ground-truth instances (the pre-registered denominator)
  non_detections_on_confirmed_instances: count(gt, (r) => !r.detected),
  excluded_from_denominator_other_draws: glitch.length - gt.length,
  recorded_outcome_status: tally(glitch, (r) => r.workflow_outcome_status),
  recorded_outcome_category: tally(glitch, (r) => r.recorded_outcome_category),
  corroboration_of_the_draw: tally(glitch, (r) => r.corroboration),
  draw_consistency: tally(glitch, (r) => r.draw_consistency),
  matching_nodes_per_ground_truth_instance: gt.map((r) => r.matching_nodes).sort((a, b) => a - b).reduce((o, v) => { o[v] = (o[v] || 0) + 1; return o; }, {}),
  rule_nodes_total_descriptive_sum: glitch.reduce((s, r) => s + (r.rule_nodes_total_descriptive || 0), 0),
};
const ctrlResult = {
  condition_id: CTRL, n_executions: ctrl.length,
  executions_in_which_the_rule_reports_a_product_heading: rate(count(ctrl, (r) => r.product_h2_nodes >= 1), ctrl.length),
  realized_dom_state: tally(ctrl, (r) => r.dom_state), recorded_outcome_status: tally(ctrl, (r) => r.workflow_outcome_status),
  recorded_outcome_category: tally(ctrl, (r) => r.recorded_outcome_category), corroboration_of_the_draw: tally(ctrl, (r) => r.corroboration),
};

const result = {
  record_class: 'DERIVED_ANALYSIS_RESULT', study_id: 'EUS-2026-001', campaign_id: 'E09-accessibility', hypothesis_id: 'H5',
  part: 'accessibility (E09) contribution only; the H5 variable of protocol/statistical-analysis-plan-v1.md, section 4.3, spans E08, E09, E10 and E11, and E08, E10 and E11 have no data',
  method: 'descriptive; Wilson 95% interval without continuity correction; no test, no p-value, no Holm correction, no support or non-support criterion (none is frozen for H5)',
  classification: 'CONFIRMATORY (H5), descriptive count comparison (written from the E09 campaign configuration, subsection CONFIRMATORY comparisons; never derived from the data)',
  inputs: { raw_data_tree: treeHead, pinned_at_commit: FREEZE_COMMIT, bundles: rows.length, configuration_section_sha256: CONFIG_SHA256, campaign_state: 'FROZEN' },
  h5_count_of_controlled_non_functional_ground_truth_conditions: {
    scope: 'E09 contribution only',
    'SUT-01': { count: 1, basis: 'HD-2 count unit: the stochastic condition ' + GLITCH + ' (the control condition ' + CTRL + ' is not a ground-truth condition)' },
    'SUT-02': { count: 0, reason: 'no data: no ground-truth condition available (no condition configured)' },
    'SUT-03': { count: 0, reason: 'no data: no ground-truth condition available (no condition configured)' },
    'SUT-04': { count: 0, reason: 'no data: no ground-truth condition available (no condition configured)' },
    'SUT-05': { count: 0, reason: 'no data: no ground-truth condition available (no condition configured)' },
    'SUT-06': { count: null, reason: 'no data: modality rated Score 0 in E01 (NO_WEB_SURFACE)' },
    comparisons: {
      'SUT-01 vs SUT-02': 'CONFIRMATORY (H5), descriptive count comparison on the E09 contribution: 1 versus 0; no pairwise detection comparison exists (SUT-02 has no condition), no Fisher table and no risk difference is formed',
      'SUT-01 vs SUT-03': 'CONFIRMATORY (H5), descriptive count comparison on the E09 contribution: 1 versus 0; no pairwise detection comparison exists (SUT-03 has no condition), no Fisher table and no risk difference is formed',
    },
    not_evaluated: 'E08, E10 and E11 have not been executed; the H5 count over all its campaigns does not exist yet',
  },
  conditions: { [GLITCH]: glitchResult, [CTRL]: ctrlResult },
  consistency: { recorded_classification_equals_the_one_derived_from_the_evidence: mismatches.length === 0, disagreements: mismatches },
  notes: 'Deterministic, non-interpretive computation: counts, proportions and intervals of recorded fields. A non-detection would be recorded as a non-detection of the predeclared rule set on the DOM condition confirmed at scan time, with no cause inferred (HD-20). The ground-truth is weak by design: the rule empty-heading is a best-practice, minor-impact rule (HD-3, HD-4).',
};

const csvHead = ['run_id', 'condition_id', 'execution_id', 'workflow_outcome_status', 'recorded_outcome_category', 'dom_state', 'body_classes', 'corroboration', 'draw_consistency', 'catalog_status', 'matching_nodes', 'product_h2_nodes', 'rule_nodes_total_descriptive', 'ground_truth_instance', 'detected', 'derived_class'];
const csv = [csvHead.join(',')].concat(rows.map((r) => csvHead.map((k) => { const v = r[k]; return v === undefined || v === null ? '' : String(v); }).join(','))).join('\n') + '\n';
const json = JSON.stringify(result, null, 2) + '\n';

if (process.argv.includes('--check')) {
  const same = fs.readFileSync(path.join(REPO, OUT_JSON), 'utf8') === json && fs.readFileSync(path.join(REPO, OUT_CSV), 'utf8') === csv;
  console.log(same ? 'CHECK PASS: the files on disk equal the recomputation' : 'CHECK FAIL: the files on disk differ from the recomputation');
  process.exit(same && mismatches.length === 0 ? 0 : 1);
}
fs.mkdirSync(path.join(REPO, path.dirname(OUT_JSON)), { recursive: true });
fs.mkdirSync(path.join(REPO, path.dirname(OUT_CSV)), { recursive: true });
fs.writeFileSync(path.join(REPO, OUT_JSON), json);
fs.writeFileSync(path.join(REPO, OUT_CSV), csv);
console.log('written', OUT_JSON, sha(Buffer.from(json)), OUT_CSV, sha(Buffer.from(csv)));
if (mismatches.length) { console.error('DISAGREEMENTS', JSON.stringify(mismatches)); process.exit(1); }
