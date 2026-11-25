#!/usr/bin/env node
'use strict';
/*
 * analysis/h5-analysis/compute-h5-e11.js
 *
 * H5 analysis, security contribution (E11) only, for study EUS-2026-001, campaign E11-security (FROZEN, 700 imported bundles in 14 cells).
 * It implements, and nothing beyond, the descriptive procedure that the campaign configuration locked at the START
 * (experiments/E11-security/README.md, "Campaign configuration": "Identity and START", "Cells" and its "Reporting" and "Matching rules"
 * bullets; the cells file experiments/E11-security/conditions-draft.json) and protocol/statistical-analysis-plan-v1.md, section 3 (Wilson 95%
 * interval for every reported proportion), section 4.3 (H5 row: "Number of controlled non-functional ground-truth conditions per ecosystem",
 * method "Descriptive count comparison; detection rates per condition are reported per Section 5") and section 5 (point estimate, interval, N,
 * classification; "no data" with its reason, never zero).
 *
 * Pre-registered rules applied here (none is chosen after seeing the data):
 *   - Per cell: the count of each category out of N = 50 with the Wilson 95% interval of each proportion, no continuity correction
 *     (z = 1.959963984540054, the repository convention of analysis/h3-analysis/h3-metrics.js, which this script requires and does not modify).
 *     No execution is excluded from any denominator: a category outside the expected one, an interruption or a reset failure is data.
 *   - M1 and M2 are reported separately and never combined (E11-D-3). The positive category of a CONDITION cell is the detection of its known
 *     ground-truth condition (M1_ORACLE_FLIPPED, M1_IDOR_BYPASS_OBSERVED, M2_EXPECTED_ALERT); the same category on a CONTROL cell is a false
 *     positive and is reported as such beside the control. A non-detection is a valid outcome: the expectation is not changed, and no cause is
 *     inferred. The rate of the expected category (matches_expected) is reported beside the positive category.
 *   - Matching rules of the configuration: an M2 alert counts only when its rule id, request method and normalized path (scheme, host, port,
 *     query and fragment removed, the path exact with the trailing slash) all equal the cell's expectation; every other alert is recorded in the
 *     bundle and never counted (here only its number per cell is reported). An M1 SUT-05 cell is decided by the solved flag of the oracle
 *     challenge in the last read of GET /api/Challenges; the SUT-01 cell is decided by the status of the GET of the order.
 *   - H5 count unit (E11-D-2b): each configured ground-truth condition counts once, the controls do not, and the two methods of one condition do
 *     not count it twice. The count is taken from the cells file (the distinct `condition` of the CONDITION cells of each ecosystem), never from
 *     the outcomes: SUT-01 contributes the conditions whose h5_count is "yes", the SUT-05 conditions are an EXPLORATORY specialist reference
 *     (E11-D-2) and stay in their own row. SUT-02 and SUT-03 have no cell: 0 with "no data, no ground-truth condition available" as the
 *     configuration states it; SUT-04 and SUT-06 have no cell and the configuration assigns them no count, so they are reported as no data
 *     with count null. The classification of each comparison is written below from the configuration and never derived from the data
 *     (analysis/README.md, rule 9). With SUT-02 and SUT-03 at zero conditions no pairwise detection comparison exists, and no Fisher table, risk
 *     difference, test, p-value, ranking, composite or support / non-support criterion is formed (none is frozen for H5).
 *   - The H5 variable of the plan spans E08, E09, E10 and E11; this script covers the E11 contribution only, says so in its output, and does not
 *     add it to the E09 contribution (derived-data/h5-analysis/H5-e09-result.json).
 *
 * The category recorded in each run manifest is compared with the one derived here from the evidence files of the bundle (the status of the GET
 * of the order; the solved flag of the oracle challenge in the last oracle read, which the evidence capture truncates at 65,519 characters but
 * which holds the flag of every oracle key; the ZAP alerts of the run); the sha256 of each evidence file read is checked against the one listed in
 * the run manifest. Any disagreement is listed and makes the script exit non-zero. Nothing is interpreted: the output is counts, proportions and
 * intervals.
 *
 * Fails loudly on: pins that are not set; a raw-data tree that differs from the pinned tree of the freeze commit or has uncommitted changes; a
 * Campaign configuration section that differs from the pinned digest (at HEAD and at the START commit); a cells file that differs from its pinned
 * digest; the pure core changed or uncommitted; E11 not FROZEN in the study manifest; a set of run or job directories that is not the expected one
 * (50 runs per cell at attempt 1, one job directory per cell); a run manifest or cell summary that disagrees with the directory
 * name, the cell, the category or the attribution; a job provenance record whose cell, SUT, attempt, GitHub run attempt or implementation hash disagrees with the locked one; an evidence file whose sha256 differs from the one listed in its run manifest; any violation of
 * the consistency checks of evaluate().
 *
 * Usage: node analysis/h5-analysis/compute-h5-e11.js [--check]    (--check recomputes and compares with the files on disk; writes nothing)
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only; no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const core = require('../h3-analysis/h3-metrics.js');

const REPO = path.resolve(__dirname, '..', '..');
const RAW = 'raw-data/E11-security';
const OUT_JSON = 'derived-data/h5-analysis/H5-e11-result.json';
const OUT_CSV = 'derived-data/E11-security/outcomes-per-attempt.csv';
const README = 'experiments/E11-security/README.md';
const CONDITIONS = 'experiments/E11-security/conditions-draft.json';
// Pins: from the recorded START and freeze records (manifests/e11-campaign-start-v1.yaml, manifests/e11-campaign-freeze-v1.yaml).
const START_COMMIT = 'cbf5b8e20a74a93fd3a39261173fd8cb8514e993';                  // the E11 campaign START commit (E11-START-AUTH-01)
const FREEZE_COMMIT = 'c7293c402b23f95238d010a965a5cac544f1c1be';                 // the E11 campaign freeze commit (E11-FREEZE-AUTH-01)
const RAW_TREE = 'cc0de160795c260920e0ac904c39c1838c022ea4';                       // git tree of raw-data/E11-security at the freeze commit
const CONFIG_SHA256 = '5b5e11b5cf7ec48977256c8598c4af16f816ee15355ed9337f26c40d41894a0a';      // sha256 of the Campaign configuration section of the E11 README, equal at the START commit and at HEAD
const CONDITIONS_SHA256 = '48beef74993b30b326a34c2f3844c38334bf61304f72a357a410f08fe21a5f48';   // sha256 of the cells file
const CORE_BLOB = '72b1f74949cc76ce907ca2a162e5d5fbd28ef6a0';                      // git blob of the pure core, unchanged since the E05 analysis
const IMPLEMENTATION_SHA256 = '0ce7625b72899523ea41b296425e1d0a144fbcf26ec0ea896d85013c5f2670fc';   // executor implementation hash locked at the START (README, Prompt version and implementation)
const WILSON_Z = 1.959963984540054;   // 95 percent, the repository convention
const N = 50;
const POSITIVE_CATEGORIES = ['M1_ORACLE_FLIPPED', 'M1_IDOR_BYPASS_OBSERVED', 'M2_EXPECTED_ALERT'];
const ATTRIBUTIONS = ['SUT', 'TOOLING'];

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
const CLASSIFICATION = 'CONFIRMATORY (H5), descriptive count comparison, SUT-01 versus SUT-02 and SUT-01 versus SUT-03 (written from the E11 campaign configuration, subsection Identity and START, which names the hypothesis label H5 and the two pairs, and from protocol/statistical-analysis-plan-v1.md, section 4.2, which classifies a comparison that tests H5 as CONFIRMATORY; never derived from the data); the SUT-05 cells are an EXPLORATORY specialist reference (E11-D-2; section 4.2: every comparison that involves a specialist baseline is EXPLORATORY unless pre-registered otherwise)';
const NO_CELL_REASON = {
  'SUT-02': 'no data: no ground-truth condition available (no cell configured; the configuration states the count of SUT-02 as 0 with this reason, E11-D-1)',
  'SUT-03': 'no data: no ground-truth condition available (no cell configured; the configuration states the count of SUT-03 as 0 with this reason, E11-D-1)',
  'SUT-04': 'no data: no ground-truth condition available (no cell configured, E11-D-1; SUT-04 by the ruling E01-HR-02); the frozen configuration assigns no count to this ecosystem, so none is invented',
  'SUT-06': 'no data: no ground-truth condition available (no cell configured, E11-D-1); the frozen configuration assigns no count to this ecosystem, so none is invented'
};
const COMPARISONS = {
  'SUT-01 vs SUT-02': 'CONFIRMATORY (H5), descriptive count comparison on the E11 contribution: SUT-01 and SUT-02 counts as in the table; no pairwise detection comparison exists (SUT-02 has no condition), no Fisher table and no risk difference is formed',
  'SUT-01 vs SUT-03': 'CONFIRMATORY (H5), descriptive count comparison on the E11 contribution: SUT-01 and SUT-03 counts as in the table; no pairwise detection comparison exists (SUT-03 has no condition), no Fisher table and no risk difference is formed',
  'SUT-01 vs SUT-05': 'EXPLORATORY specialist reference (E11-D-2): not computed; no pair shares a condition (the cells of SUT-05 test other known conditions with other targets), and E11 has no canonical scenario or mapping record; the SUT-05 cells are reported on their own'
};

// ---- pure functions (no file is read) ------------------------------------------------------------------------------------------
/** The path of an alert URL: scheme, host, port, query and fragment removed; the path exact, a trailing slash included. */
function normalizePath(url) { return new URL(url).pathname; }

/** Split "METHOD /path?query" into { method, path } with the query dropped; null when it has no method. */
function splitEndpoint(text) {
  const m = /^([A-Z]+) (\/[^?#]*)(?:[?#].*)?$/.exec(String(text || ''));
  return m ? { method: m[1], path: m[2] } : null;
}

/** The (rule id, method, path) that an M2 cell expects: a CONDITION cell from the matching rules of the cells file, a CONTROL cell from its control endpoint. */
function expectedTarget(cell, cfg) {
  const rule = String(cell.expected_m2_rule_id);
  if (cell.kind === 'CONTROL') {
    const e = splitEndpoint(cell.control_endpoint);
    if (!e) throw new Error(cell.cell_id + ': the control endpoint has no method and path');
    return { rule, method: e.method, path: e.path };
  }
  const mr = cfg.matching_rules;
  const method = mr.expected_m2_method[cell.condition]; const p = mr.expected_m2_path[cell.condition];
  if (!method || !p) throw new Error(cell.cell_id + ': the matching rules name no method or path for ' + cell.condition);
  if (cell.expected_m2_target && !cell.expected_m2_target.endsWith(p)) throw new Error(cell.cell_id + ': the expected target of the cell and the matching rules disagree');
  return { rule, method, path: p };
}

/** Counted and other alerts: an alert counts only when its pluginId, request method and normalized path all equal the expectation. */
function matchAlerts(alerts, target) {
  let counted = 0; let others = 0;
  for (const a of alerts) {
    if (String(a.pluginId) === target.rule && a.method === target.method && normalizePath(a.url || '') === target.path) counted += 1; else others += 1;
  }
  return { counted, others };
}

/** M1 of SUT-01: the status of the GET of the order decides (200 bypass, 403 blocked, anything else other). */
function deriveM1Sut01(evidence) {
  const s = evidence && evidence.response && evidence.response.status;
  if (s === 200) return 'M1_IDOR_BYPASS_OBSERVED';
  if (s === 403) return 'M1_IDOR_BLOCKED';
  return 'M1_RESPONSE_OTHER';
}

/** M1 of SUT-05: the solved flag of the oracle key in the last read of GET /api/Challenges (a body truncated by the evidence capture is read as text). */
function deriveM1Sut05(evidence, key) {
  if (!evidence || !evidence.response || evidence.response.status !== 200) return 'M1_RESPONSE_OTHER';
  const body = String(evidence.response.body || '');
  const m = new RegExp('"key":"' + key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '"[\\s\\S]*?"solved":(true|false)').exec(body);
  if (!m || body.slice(m.index + 8, m.index + m[0].length).includes('"key":"')) return null;   // the flag of the key is not readable in the evidence
  return m[1] === 'true' ? 'M1_ORACLE_FLIPPED' : 'M1_ORACLE_NOT_FLIPPED';
}

/** M2: the category from the alerts of the run. */
function deriveM2(alerts, target) {
  const { counted, others } = matchAlerts(alerts, target);
  return { category: counted > 0 ? 'M2_EXPECTED_ALERT' : 'M2_NO_EXPECTED_ALERT', counted, others };
}

/** Per-cell results, the per-condition table, the H5 counts and the consistency violations. Pure: reads no file. `rows` are execution records
 *  { cell_id, run_id, execution_index, recorded_category, derived_category, status, matches_expected, attribution, others, toolchain }. */
function evaluate(cfg, rows) {
  const violations = [];
  const cellIds = new Set(cfg.cells.map((c) => c.cell_id));
  for (const r of rows) if (!cellIds.has(r.cell_id)) violations.push(`${r.run_id}: the cell ${r.cell_id} is not in the cells file`);
  const cells = [];
  for (const cell of cfg.cells) {
    const own = rows.filter((r) => r.cell_id === cell.cell_id).sort((a, b) => a.execution_index - b.execution_index);
    const n = own.length;
    if (n !== cell.n) violations.push(`${cell.cell_id}: ${n} executions, not ${cell.n}`);
    own.forEach((r, i) => { if (r.execution_index !== i + 1) violations.push(`${cell.cell_id}: execution indexes have a gap or do not start at 1`); });
    const declared = new Set([].concat(cfg.category_sets[cell.method.toLowerCase()], cfg.category_sets.reset));
    for (const r of own) {
      if (r.derived_category === null || r.derived_category === undefined) { violations.push(`${r.run_id}: the category cannot be derived from the evidence`); continue; }
      if (r.derived_category !== r.recorded_category) violations.push(`${r.run_id}: recorded ${r.recorded_category}, derived ${r.derived_category}`);
      if (!declared.has(r.recorded_category) && !r.recorded_category.startsWith('INTERRUPTED_')) violations.push(`${r.run_id}: category ${r.recorded_category} is outside the declared set of ${cell.cell_id}`);
      if (r.matches_expected !== (r.recorded_category === cell.expected_category)) violations.push(`${r.run_id}: matches_expected disagrees with the cell's expected category`);
      if (!ATTRIBUTIONS.includes(r.attribution)) violations.push(`${r.run_id}: attribution ${r.attribution} is outside the declared labels`);
    }
    const counts = tally(own, (r) => r.recorded_category);
    const rec = (x) => core.rate(x, n, WILSON_Z);
    const positives = own.filter((r) => POSITIVE_CATEGORIES.includes(r.recorded_category)).length;
    const out = {
      cell_id: cell.cell_id, sut_id: cell.sut_id, condition: cell.condition, method: cell.method, kind: cell.kind, h5_count_class: cell.h5_count,
      expected_category: cell.expected_category, n_executions: n,
      category_counts: Object.fromEntries(Object.keys(sortedObject(counts)).map((k) => [k, rec(counts[k])])),
      positive_category_rate: { role: cell.kind === 'CONDITION' ? 'detection of the known ground-truth condition' : 'false positive on the control', ...rec(positives) },
      expected_category_rate: rec(own.filter((r) => r.matches_expected).length),
      attribution_counts: sortedObject(tally(own, (r) => r.attribution)),
      workflow_outcome_status_counts: sortedObject(tally(own, (r) => r.status)),
      derived_from_evidence_equals_recorded: own.every((r) => r.derived_category === r.recorded_category)
    };
    if (cell.method === 'M2') {
      out.other_alerts_not_counted = { executions_with_any: own.filter((r) => r.others > 0).length, total: own.reduce((s, r) => s + (r.others || 0), 0), note: 'descriptive; an alert that does not equal the cell expectation in rule, method and normalized path is never counted' };
    }
    if (cell.kind === 'CONDITION' && positives === 0) {
      out.non_detection_note = 'no execution recorded the positive category with this method; a non-detection is a valid outcome, the expectation of the configuration is not changed, and no cause is inferred';
    }
    const drift = core.distinctToolchain(own);
    if (Object.keys(drift).length) out.toolchain_drift_confounds = drift;
    cells.push(out);
  }
  // per-condition table: M1 and M2 stay separate, nothing is combined across methods
  const byCondition = new Map();
  for (const c of cells) {
    const key = c.sut_id + '|' + c.condition;
    if (!byCondition.has(key)) byCondition.set(key, { sut_id: c.sut_id, condition: c.condition, h5_count_class: null, methods: {} });
    const e = byCondition.get(key);
    const m = (e.methods[c.method] = e.methods[c.method] || {});
    if (c.kind === 'CONDITION') { e.h5_count_class = c.h5_count_class; m.condition_cell = c.cell_id; m.detections = c.positive_category_rate; }
    else { m.control_cell = c.cell_id; m.false_positives = c.positive_category_rate; }
  }
  const conditions = Array.from(byCondition.values());
  // H5 count: the distinct ground-truth conditions of the CONDITION cells, from the cells file (E11-D-2b); the outcomes never enter it
  const h5 = {};
  for (const c of cfg.cells.filter((x) => x.kind === 'CONDITION')) {
    const e = (h5[c.sut_id] = h5[c.sut_id] || { conditions: new Set(), classes: new Set() });
    e.conditions.add(c.condition); e.classes.add(c.h5_count);
  }
  const h5Counts = {};
  for (const sut of ['SUT-01', 'SUT-02', 'SUT-03', 'SUT-04', 'SUT-05', 'SUT-06']) {
    if (h5[sut]) {
      const classes = Array.from(h5[sut].classes).sort();
      h5Counts[sut] = { count: h5[sut].conditions.size, conditions: Array.from(h5[sut].conditions).sort(), h5_count_class_in_cells_file: classes,
        role: classes.length === 1 && classes[0] === 'yes' ? 'H5 pair: counts in the CONFIRMATORY (H5) comparisons' : 'EXPLORATORY specialist reference (E11-D-2): not part of an H5 pair',
        basis: 'E11-D-2b count unit: each configured ground-truth condition counts once; the controls do not count and the two methods of one condition do not count it twice' };
    } else if (NO_CELL_REASON[sut]) {
      h5Counts[sut] = { count: sut === 'SUT-02' || sut === 'SUT-03' ? 0 : null, reason: NO_CELL_REASON[sut] };
    } else violations.push(`${sut}: no H5 count rule`);
  }
  return { cells, conditions, h5_counts: h5Counts, violations };
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
  if (sha(condBuf) !== CONDITIONS_SHA256) fail('the cells file differs from its pinned digest');
  if (git('status', '--porcelain', '--', CONDITIONS, 'analysis/h3-analysis/h3-metrics.js')) fail('uncommitted changes in the cells file or the pure core');
  if (git('hash-object', 'analysis/h3-analysis/h3-metrics.js') !== CORE_BLOB) fail('the pure core is not the pinned blob ' + CORE_BLOB);
  const manifestStatus = fs.readFileSync(path.join(REPO, 'manifests/study-manifest.yaml'), 'utf8').match(/- id: E11-security\n\s+status: (\w+)/);
  if (!manifestStatus || manifestStatus[1] !== 'FROZEN') fail('E11 is not FROZEN in the study manifest');

  const cfg = JSON.parse(condBuf.toString('utf8'));
  if (cfg.n_per_cell !== N || cfg.cells.length !== 14 || cfg.cells.some((c) => c.n !== N)) fail('the cells file is not the locked one (fourteen cells, N = 50 each)');
  if (cfg.wilson_z !== WILSON_Z) fail('the z of the cells file is not the repository convention');
  const SUT_DIRS = Array.from(new Set(cfg.cells.map((c) => c.sut_id))).sort();

  // ---- the run and job directories ---------------------------------------------------------------------------------
  const present = fs.readdirSync(path.join(REPO, RAW)).filter((d) => !d.startsWith('.')).sort();
  if (JSON.stringify(present) !== JSON.stringify(SUT_DIRS)) fail('the SUT directories are not ' + SUT_DIRS.join(', '));
  const expectedRuns = []; const expectedJobs = [];
  for (const c of cfg.cells) {
    expectedJobs.push(`${c.sut_id}/${c.cell_id}__job__A1`);
    for (let n = 1; n <= N; n++) expectedRuns.push(`${c.sut_id}/${c.cell_id}__EX${String(n).padStart(4, '0')}__A1`);
  }
  const foundRuns = []; const foundJobs = [];
  for (const sut of SUT_DIRS) {
    for (const d of fs.readdirSync(path.join(REPO, RAW, sut)).filter((x) => !x.startsWith('.')).sort()) (/__job__A\d+$/.test(d) ? foundJobs : foundRuns).push(`${sut}/${d}`);
  }
  if (JSON.stringify([...foundRuns].sort()) !== JSON.stringify([...expectedRuns].sort())) fail(`the set of run directories is not the ${expectedRuns.length} expected`);
  if (JSON.stringify([...foundJobs].sort()) !== JSON.stringify([...expectedJobs].sort())) fail(`the set of job directories is not the ${expectedJobs.length} expected`);

  const rows = []; const csvRows = []; let filesRead = 0; const jobRecords = {};
  for (const c of cfg.cells) {
    const jobBase = path.join(REPO, RAW, c.sut_id, `${c.cell_id}__job__A1`);
    const summary = readJson(path.join(jobBase, 'condition-summary.json'));
    const jobProv = readJson(path.join(jobBase, 'ci-provenance.json'));
    filesRead += 2;
    if (summary.condition !== c.cell_id || summary.sut !== c.sut_id || summary.attempt !== 1 || summary.record_class !== 'MEASURED_EXPERIMENT') fail(c.cell_id + ': the cell summary names another cell, SUT, attempt or record class');
    if (summary.executions_run !== N || summary.executions_planned !== N || (summary.executions || []).length !== N) fail(c.cell_id + ': the cell summary does not hold 50 executions');
    if (jobProv.cell_id !== c.cell_id || jobProv.sut_id !== c.sut_id || jobProv.attempt !== 1 || jobProv.campaign_id !== 'E11-security') fail(c.cell_id + ': the job provenance names another cell, SUT or attempt');
    if (!jobProv.github || String(jobProv.github.run_attempt) !== '1') fail(c.cell_id + ': the GitHub run attempt is not 1');
    if (!jobProv.frozen_input_hashes || jobProv.frozen_input_hashes.executor_implementation_sha256 !== IMPLEMENTATION_SHA256) fail(c.cell_id + ': the implementation hash of the job is not the one locked at the START');
    jobRecords[c.cell_id] = { github_run_id: jobProv.github && jobProv.github.run_id, workflow_file_sha256: jobProv.workflow && jobProv.workflow.file_sha256, cell_summary_sha256: sha(fs.readFileSync(path.join(jobBase, 'condition-summary.json'))) };
    const target = c.method === 'M2' ? expectedTarget(c, cfg) : null;
    for (let n = 1; n <= N; n++) {
      const ex = `EX${String(n).padStart(4, '0')}`;
      const d = `${c.cell_id}__${ex}__A1`;
      const base = path.join(REPO, RAW, c.sut_id, d);
      const man = readJson(path.join(base, 'run-manifest.json'));
      filesRead += 1;
      if (man.run_id !== d || man.condition !== c.cell_id || man.campaign_id !== 'E11-security' || man.sut_id !== c.sut_id || man.attempt !== 1) fail(d + ': identity fields of the run manifest disagree');
      const entry = summary.executions[n - 1];
      if (!entry || entry.run_id !== d) fail(d + ': the cell summary has no matching entry at its position');
      if (!man.outcome || man.outcome.outcome_category !== entry.category) fail(d + ': the outcome category of the run manifest and of the cell summary disagree');
      if (typeof man.outcome.matches_expected !== 'boolean') fail(d + ': matches_expected is not a boolean');
      const am = /attribution=(\w+)/.exec(man.notes || '');
      if (!am || am[1] !== entry.attribution) fail(d + ': the attribution of the run manifest and of the cell summary disagree');
      const evDir = path.join(base, 'evidence');
      const evNames = fs.readdirSync(evDir).sort();
      const readEvidence = (name) => {
        const buf = fs.readFileSync(path.join(evDir, name)); filesRead += 1;
        const listed = (man.artifacts || []).find((a) => a.path === `${RAW}/${c.sut_id}/${d}/evidence/${name}`);
        if (!listed || listed.sha256 !== sha(buf)) fail(d + ': evidence/' + name + ' is not the file listed in the run manifest');
        return JSON.parse(buf.toString('utf8'));
      };
      const one = (suffix) => { const f = evNames.filter((x) => x.endsWith(suffix)); if (f.length !== 1) fail(d + ': expected exactly one evidence file ending ' + suffix); return f[0]; };
      let derived = null; let others = null; let basis;
      if (c.method === 'M2') {
        const name = one('-zap-alerts.json'); const alerts = readEvidence(name);
        if (!Array.isArray(alerts)) fail(d + ': the alerts file is not an array');
        const r = deriveM2(alerts, target); derived = r.category; others = r.others; basis = 'evidence/' + name + ' (rule ' + target.rule + ', ' + target.method + ' ' + target.path + ')';
      } else if (c.sut_id === 'SUT-01') {
        const name = one('-sut01-m1-get-order.json'); derived = deriveM1Sut01(readEvidence(name)); basis = 'evidence/' + name + ' (status of the GET)';
      } else {
        const reads = evNames.filter((x) => /-sut05-oracle-(first|last)-read\.json$/.test(x));
        if (!reads.length) fail(d + ': no oracle read');
        const name = reads[reads.length - 1];
        if (reads.length === 2 && !/last-read/.test(name)) fail(d + ': the last oracle read is not the last file');
        derived = deriveM1Sut05(readEvidence(name), c.oracle_challenge_key); basis = 'evidence/' + name + ' (solved flag of ' + c.oracle_challenge_key + ')';
      }
      rows.push({ cell_id: c.cell_id, run_id: d, execution_index: n, recorded_category: man.outcome.outcome_category, derived_category: derived, status: man.outcome.status,
                  matches_expected: man.outcome.matches_expected, attribution: entry.attribution, others, toolchain: man.toolchain });
      csvRows.push({ run_id: d, cell_id: c.cell_id, sut_id: c.sut_id, condition: c.condition, method: c.method, kind: c.kind, h5_count_class: c.h5_count, execution_id: ex, attempt: 1,
                     recorded_outcome_category: man.outcome.outcome_category, derived_outcome_category: derived, positive_category_recorded: POSITIVE_CATEGORIES.includes(man.outcome.outcome_category),
                     workflow_outcome_status: man.outcome.status, matches_expected: man.outcome.matches_expected, attribution: entry.attribution,
                     other_alerts_not_counted: others, derivation_basis: basis });
    }
  }

  const evaluated = evaluate(cfg, rows);
  if (evaluated.violations.length) { console.error(evaluated.violations.join('\n')); fail(evaluated.violations.length + ' consistency violation(s)'); }
  const result = {
    record_class: 'DERIVED_ANALYSIS_RESULT', study_id: 'EUS-2026-001', campaign_id: 'E11-security', hypothesis_id: 'H5',
    part: 'security (E11) contribution only; the H5 variable of protocol/statistical-analysis-plan-v1.md, section 4.3, spans E08, E09, E10 and E11; E08 and E10 have no data, and the E09 contribution is the separate dataset derived-data/h5-analysis/H5-e09-result.json; the contributions are not summed here',
    method: 'descriptive; Wilson 95% interval without continuity correction (z = ' + WILSON_Z + '); no test, no p-value, no Holm correction, no support or non-support criterion (none is frozen for H5); M1 and M2 reported separately',
    classification: CLASSIFICATION,
    inputs: { raw_data_tree: treeHead, pinned_at_commit: FREEZE_COMMIT, start_commit: START_COMMIT, bundles: rows.length, job_directories: foundJobs.length, cells: cfg.cells.length,
              configuration_section_sha256: CONFIG_SHA256, cells_file: CONDITIONS, cells_file_sha256: CONDITIONS_SHA256, executor_implementation_sha256: IMPLEMENTATION_SHA256, campaign_state: 'FROZEN', job_records: jobRecords },
    h5_count_of_controlled_non_functional_ground_truth_conditions: {
      scope: 'E11 contribution only',
      ecosystems: evaluated.h5_counts,
      comparisons: COMPARISONS,
      not_evaluated: 'E08 and E10 have not been executed (NOT_STARTED); the H5 count over all its campaigns does not exist yet'
    },
    conditions: evaluated.conditions,
    cells: evaluated.cells,
    totals: { executions: rows.length, cells: evaluated.cells.length, note: 'counts only; no rate is pooled across cells, methods or ecosystems' },
    consistency: { recorded_category_equals_the_one_derived_from_the_evidence: evaluated.violations.length === 0, disagreements: evaluated.violations },
    not_computed: 'No pooled rate, composite score, ranking, M1-versus-M2 combination, SUT-01-versus-SUT-05 comparison, Fisher table, risk difference, test, p-value or verdict: the configuration lists them as not computed and none is frozen for H5.',
    notes: 'Deterministic, non-interpretive computation: counts, proportions and intervals of recorded fields. E11-SUT05-DIRLIST-FTP-M2 expects rule 0 on /ftp/ although the source reading predicted and two DRY_RUN rounds observed no alert; its recorded outcome is reported as recorded, and its expectation is not changed.'
  };
  const jsonText = JSON.stringify(result, null, 2) + '\n';
  const header = ['run_id', 'cell_id', 'sut_id', 'condition', 'method', 'kind', 'h5_count_class', 'execution_id', 'attempt', 'recorded_outcome_category', 'derived_outcome_category',
                  'positive_category_recorded', 'workflow_outcome_status', 'matches_expected', 'attribution', 'other_alerts_not_counted', 'derivation_basis'];
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

module.exports = { evaluate, normalizePath, splitEndpoint, expectedTarget, matchAlerts, deriveM1Sut01, deriveM1Sut05, deriveM2, POSITIVE_CATEGORIES, WILSON_Z, COMPARISONS, NO_CELL_REASON };
if (require.main === module) main();
