#!/usr/bin/env node
'use strict';
/*
 * analysis/e06-parity-analysis/compute-parity-e06.js
 *
 * Parity analysis of E06-cross-platform-parity for study EUS-2026-001: the loader and command-line driver that the "Analysis and what is not
 * computed" part of the campaign configuration promises after the freeze (experiments/E06-cross-platform-parity/README.md, "Campaign
 * configuration"). It reads the 200 frozen executions (four conditions, N = 50 each), pairs execution k of the WEB condition of an ecosystem with
 * execution k of its ANDROID condition, classifies every pair, and computes per ecosystem the parity proportion (pairs with parity over 50) with
 * the Wilson 95 percent interval, beside the category counts of each surface, the non-arrival and unreadable-identity counts and the attributed
 * counts. For SUT-01 versus SUT-02 it computes the risk difference with its 95 percent interval and Fisher's exact test, as the configuration
 * names them. Descriptive in weight: one canonical scenario gives one scenario pair per comparison (decision D-E06-7).
 *
 * Pre-registered rules applied here (none is chosen after seeing the data; decisions D-E06-7, D-E06-8 and D-E06-15,
 * manifests/campaign-execution-decisions-v17.yaml and -v18.yaml; the conditions file, "pairing_rule", "parity_rule" and "estimand"):
 *   - Pairing by index: execution k of the WEB condition with execution k of the ANDROID condition of the same ecosystem, k = 1 to 50.
 *   - Parity is present for a pair when both executions arrived with the category ARRIVED_IDENTITY_READ and the identity of the first catalogue
 *     position (the field `identity` of the evidence facts, the normalized identifier; `identity_raw` is recorded beside it) is the same on both
 *     surfaces (string equality). Every other pair is a non-parity. Each pair gets exactly one class, by this precedence: NOT_ARRIVED (at least one
 *     side did not arrive), IDENTITY_UNREADABLE (no side failed to arrive, at least one side arrived with an unreadable identity),
 *     ARRIVAL_ONLY (a side with the category ARRIVED_ARRIVAL_ONLY; the oracle switch of every condition is item_identity, so none is expected and
 *     one would be a violation), IDENTITY_DIFFERENT (both read, the identities differ), PARITY.
 *   - No execution is excluded from any denominator: the denominator is 50 pairs per ecosystem, a non-arrival is data, and the unreadable-identity
 *     pairs are reported as their own class beside the parity count. The first attempt of E06-CS007-SUT01-ANDROID (GitHub run 44984064912) left
 *     no execution record (it ended at the install step of its measured job before the executor ran), so its 50 executions are those of its
 *     attempt 2, which is the one imported (further-attempt approval E06-FURTHER-ATTEMPT-SUT01-APPROVAL-01); this is recorded in the result.
 *   - Attribution is the one the executor recorded mechanically (NONE, SUT, INFRASTRUCTURE, TOOLING, UNDETERMINED); it is reported beside the raw
 *     proportion and never changes it.
 *   - Risk difference SUT-01 minus SUT-02 in the parity proportion, with the Newcombe hybrid score interval (method 10 of Newcombe 1998, built
 *     from the two Wilson intervals; chosen here before any data was read because the configuration names an interval without a method and the
 *     Wilson interval is the repository convention) and the two-sided Fisher exact p-value on the 2 x 2 table (parity, no parity) by ecosystem
 *     (the sum of the hypergeometric probabilities not above that of the observed table). Both are descriptive: no support or non-support
 *     criterion is frozen for H4, and none is invented.
 *   - Not computed, not compared, not pooled: no pooled rate across ecosystems or surfaces, no composite score, no latency, no result for iOS.
 *     SUT-01 versus SUT-03 has no mobile data and is not estimable; SUT-03 and SUT-04 have no mobile surface and SUT-05 and SUT-06 no condition.
 *
 * The Wilson interval and the toolchain drift check come from the pure core analysis/h3-analysis/h3-metrics.js, which this script requires and
 * does not modify (rate() and distinctToolchain() only).
 *
 * Fails loudly on: pins that are not set; a raw-data tree that differs from the pinned tree of the freeze commit or has uncommitted changes; a
 * Campaign configuration section that differs from the pinned digest (at HEAD and at the START commit); a conditions file that differs from its
 * pinned digest; the pure core changed or uncommitted; E06 not FROZEN in the study manifest; a set of run or job directories that is not the
 * expected one (50 runs per condition, one job directory per condition, attempt 2 for E06-CS007-SUT01-ANDROID and attempt 1 for the others); a
 * run manifest, evidence facts file or condition summary that disagrees with the directory name, the condition, the category or the identity;
 * a category or reason outside the declared set; any violation of the consistency checks of evaluate().
 *
 * Usage: node analysis/e06-parity-analysis/compute-parity-e06.js [--check]    (--check recomputes and compares with the files on disk; writes nothing)
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only; no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');
const core = require('../h3-analysis/h3-metrics.js');

const REPO = path.resolve(__dirname, '..', '..');
const RAW = 'raw-data/E06-cross-platform-parity';
const OUT_JSON = 'derived-data/E06-cross-platform-parity/parity-e06-result.json';
const OUT_PAIRS = 'derived-data/E06-cross-platform-parity/parity-pairs.csv';
const OUT_EXEC = 'derived-data/E06-cross-platform-parity/outcomes-per-execution.csv';
const README = 'experiments/E06-cross-platform-parity/README.md';
const CONDITIONS = 'experiments/E06-cross-platform-parity/conditions-draft.json';
// Pins: from the recorded START and freeze records (manifests/e06-campaign-start-v1.yaml, manifests/e06-campaign-freeze-v1.yaml).
const START_COMMIT = '16ff3a6813ec8762fd19224e3c900c3ef009db98';                  // the E06 campaign START commit (E06-START-AUTH-01)
const FREEZE_COMMIT = 'cbe33b2a818f8c475ff5a8042d7c9065ea08909f';                 // the E06 campaign freeze commit (E06-FREEZE-AUTH-01)
const RAW_TREE = '61b282b866c7d478a2725295a91f7fa26ba0b687';                      // git tree of raw-data/E06-cross-platform-parity at the freeze commit
const CONFIG_SHA256 = '93ce98847a2c949be7baea80d6425fa17c3b2304a567de9ab71aa3c30e1feab2';   // sha256 of the Campaign configuration section of the E06 README, equal at the START commit and at HEAD
const CONDITIONS_SHA256 = 'b97c492af7c9be1f5716b05cf29666b7b7dff6588f9788b63499203dfa3a1fcd';   // sha256 of the conditions file
const CORE_BLOB = '72b1f74949cc76ce907ca2a162e5d5fbd28ef6a0';                      // git blob of the pure core, unchanged since the E05 analysis
const WILSON_Z = 1.959963984540054;   // 95 percent, the repository convention (experiments/E05-determinism/README.md, "Metrics")
const N = 50;
// The attempt that was imported for each condition (the first attempt of E06-CS007-SUT01-ANDROID left no bundle).
const ATTEMPT_OF = { 'E06-CS007-SUT01-ANDROID': 2 };
const ATTEMPTS_WITHOUT_BUNDLE = [
  { condition_id: 'E06-CS007-SUT01-ANDROID', attempt: 1, github_run_id: '44984064912', note: 'ended in failure at the install step of its measured job, before the executor ran; no execution record exists; its dispatch record (manifests/e06-measured-dispatch/e06-sut01.jsonl) keeps the event; the executions of this condition are those of its attempt 2' }
];
const PAIR_CLASSES = ['PARITY', 'IDENTITY_DIFFERENT', 'IDENTITY_UNREADABLE', 'NOT_ARRIVED', 'ARRIVAL_ONLY'];
const ATTRIBUTIONS = ['NONE', 'SUT', 'INFRASTRUCTURE', 'TOOLING', 'UNDETERMINED'];

const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const fail = (m) => { console.error('FAIL: ' + m); process.exit(2); };
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const csvCell = (v) => {
  const s = v === null || v === undefined ? '' : typeof v === 'string' ? v : JSON.stringify(v);
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

// The comparisons that are not estimable, with the reason of each (written from the configuration and the frozen mapping record CS-007, not from the data).
const COMPARISONS_NOT_ESTIMABLE = [
  { id: 'SUT-01 vs SUT-03', scenario: 'CS-007', estimable: false, reason: 'SUT-03 is COMPARABLE on WEB only in the frozen mapping record and has no mobile surface: it has no condition and no parity pair' },
  { id: 'SUT-01 vs SUT-04', scenario: 'CS-007', estimable: false, reason: 'SUT-04 is COMPARABLE on WEB only and has no mobile surface: no condition, no parity pair; a specialist reference, never a confirmatory comparison' },
  { id: 'SUT-01 vs SUT-05, SUT-06', scenario: 'CS-007', estimable: false, reason: 'SUT-05 and SUT-06 are NOT_COMPARABLE in the frozen mapping record: no condition' },
  { id: 'iOS', scenario: 'CS-007', estimable: false, reason: 'iOS is deferred and recorded untested (decision D-E06-5, DP-8): no condition, no result' }
];

/** Log-factorial table and the hypergeometric probability of a 2 x 2 table with fixed margins. */
function logFact(n) { let s = 0; for (let i = 2; i <= n; i += 1) s += Math.log(i); return s; }
function hyperP(a, b, c, d) {
  const n = a + b + c + d;
  return Math.exp(logFact(a + b) + logFact(c + d) + logFact(a + c) + logFact(b + d) - logFact(n) - logFact(a) - logFact(b) - logFact(c) - logFact(d));
}
/** Two-sided Fisher exact p-value of the table [[a, b], [c, d]]: the sum of the probabilities of the tables with the same margins that are not above that of the observed one. */
function fisherExact(a, b, c, d) {
  for (const v of [a, b, c, d]) if (!Number.isInteger(v) || v < 0) throw new Error('fisherExact: counts must be non-negative integers');
  const r1 = a + b; const c1 = a + c; const n = a + b + c + d;
  const pObs = hyperP(a, b, c, d);
  const lo = Math.max(0, c1 - (n - r1)); const hi = Math.min(r1, c1);
  let p = 0;
  for (let x = lo; x <= hi; x += 1) {
    const px = hyperP(x, r1 - x, c1 - x, n - r1 - c1 + x);
    if (px <= pObs * (1 + 1e-7)) p += px;
  }
  return Math.min(1, p);
}
/** Risk difference p1 - p2 with the Newcombe hybrid score interval (method 10), from the two Wilson intervals. */
function riskDifference(x1, n1, x2, n2, z) {
  if (!(n1 >= 1) || !(n2 >= 1)) return core.NOT_ESTIMABLE;
  const p1 = x1 / n1; const p2 = x2 / n2;
  const w1 = core.wilson(x1, n1, z); const w2 = core.wilson(x2, n2, z);
  const d = p1 - p2;
  return { value: d, interval: { lower: d - Math.sqrt((p1 - w1.lower) ** 2 + (w2.upper - p2) ** 2), upper: d + Math.sqrt((w1.upper - p1) ** 2 + (p2 - w2.lower) ** 2) },
           method: 'Newcombe hybrid score (method 10), z = ' + z };
}

/** The class of one pair. Pure. `web` and `and` are execution records {category, identity}. */
function classifyPair(web, and, successCategory) {
  const sides = [web, and];
  if (sides.some((s) => s.category.startsWith('NOT_ARRIVED'))) return 'NOT_ARRIVED';
  if (sides.some((s) => s.category === 'ARRIVED_IDENTITY_UNREADABLE')) return 'IDENTITY_UNREADABLE';
  if (sides.some((s) => s.category === 'ARRIVED_ARRIVAL_ONLY')) return 'ARRIVAL_ONLY';
  if (sides.every((s) => s.category === successCategory)) return web.identity === and.identity ? 'PARITY' : 'IDENTITY_DIFFERENT';
  return null; // a category outside the declared set; evaluate() reports it
}

/** Per-condition counts, pairs, parity proportions and the SUT-01 versus SUT-02 comparison, plus the consistency violations. Pure: reads no file. */
function evaluate(cfg, executions) {
  const declared = new Set(cfg.categories);
  const reasons = new Set([].concat(...Object.values(cfg.not_arrived_reasons)));
  const violations = [];
  const byCond = {};
  for (const e of executions) (byCond[e.condition_id] = byCond[e.condition_id] || []).push(e);
  const known = new Set(cfg.conditions.map((c) => c.condition_id));
  for (const id of Object.keys(byCond)) if (!known.has(id)) violations.push(`${id}: condition is not in the conditions table`);

  const surfaceStats = {}; const drift = {};
  for (const cond of cfg.conditions) {
    const list = (byCond[cond.condition_id] || []).slice().sort((a, b) => a.execution_index - b.execution_index);
    const counts = {}; for (const c of cfg.categories) counts[c] = 0;
    const reasonCounts = {}; const attribution = {};
    const seen = new Set();
    for (const e of list) {
      if (!declared.has(e.category)) violations.push(`${cond.condition_id}: ${e.run_id}: category ${JSON.stringify(e.category)} is not in the declared set`);
      else counts[e.category] += 1;
      if (e.category.startsWith('NOT_ARRIVED')) {
        if (!reasons.has(e.reason)) violations.push(`${cond.condition_id}: ${e.run_id}: reason ${JSON.stringify(e.reason)} is not in the declared set`);
        else reasonCounts[e.reason] = (reasonCounts[e.reason] || 0) + 1;
      } else if (e.reason !== null && e.reason !== undefined && e.category !== 'ARRIVED_IDENTITY_UNREADABLE') {
        violations.push(`${cond.condition_id}: ${e.run_id}: a reason on the category ${e.category}`);
      }
      if (!ATTRIBUTIONS.includes(e.attribution)) violations.push(`${cond.condition_id}: ${e.run_id}: attribution ${JSON.stringify(e.attribution)} is not in the declared set`);
      else { attribution[e.category] = attribution[e.category] || {}; attribution[e.category][e.attribution] = (attribution[e.category][e.attribution] || 0) + 1; }
      if (e.condition_id !== cond.condition_id) violations.push(`${cond.condition_id}: execution ${e.run_id} names condition ${e.condition_id}`);
      if (e.category === cfg.arrival_success_categories[0] && (typeof e.identity !== 'string' || e.identity === '')) violations.push(`${cond.condition_id}: ${e.run_id}: ${e.category} without an identity`);
      if (seen.has(e.execution_index)) violations.push(`${cond.condition_id}: repeated execution index ${e.execution_index}`);
      seen.add(e.execution_index);
    }
    for (let n = 1; n <= cond.n; n += 1) if (!seen.has(n)) violations.push(`${cond.condition_id}: no execution record for index ${n}`);
    const sum = Object.values(counts).reduce((x, y) => x + y, 0);
    if (sum !== list.length) violations.push(`${cond.condition_id}: the category counts sum to ${sum}, not ${list.length}`);
    const arrived = list.filter((e) => !e.category.startsWith('NOT_ARRIVED')).length;
    const dr = core.distinctToolchain(list);
    if (Object.keys(dr).length) drift[cond.condition_id] = dr;
    surfaceStats[cond.condition_id] = { condition_id: cond.condition_id, sut_id: cond.sut_id, surface: cond.surface, n_planned: cond.n, executions: list.length, arrived,
      not_arrived: list.length - arrived, identity_unreadable: counts.ARRIVED_IDENTITY_UNREADABLE, category_counts: counts, not_arrived_reason_counts: reasonCounts, attribution_by_category: attribution };
  }

  // ---- pairs by index, per ecosystem ----------------------------------------------------------------------------
  const ecosystems = []; const pairs = [];
  const suts = Array.from(new Set(cfg.conditions.map((c) => c.sut_id))).sort();
  for (const sut of suts) {
    const web = cfg.conditions.find((c) => c.sut_id === sut && c.surface === 'WEB');
    const and = cfg.conditions.find((c) => c.sut_id === sut && c.surface === 'ANDROID');
    if (!web || !and) { violations.push(`${sut}: a WEB and an ANDROID condition are both required`); continue; }
    const wl = byCond[web.condition_id] || []; const al = byCond[and.condition_id] || [];
    const classes = {}; for (const c of PAIR_CLASSES) classes[c] = 0;
    const attributedNonParity = {};
    let parity = 0; const own = [];
    for (let k = 1; k <= Math.min(web.n, and.n); k += 1) {
      const w = wl.find((e) => e.execution_index === k); const a = al.find((e) => e.execution_index === k);
      if (!w || !a) continue;
      if (!declared.has(w.category) || !declared.has(a.category)) continue;
      const cls = classifyPair(w, a, cfg.arrival_success_categories[0]);
      if (cls === null) { violations.push(`${sut}: pair ${k}: no class for the categories ${w.category} and ${a.category}`); continue; }
      if (cls === 'ARRIVAL_ONLY') violations.push(`${sut}: pair ${k}: a side with ARRIVED_ARRIVAL_ONLY although the oracle switch of every condition is item_identity`);
      classes[cls] += 1;
      if (cls === 'PARITY') parity += 1;
      else {
        const labels = [w, a].filter((s) => s.attribution !== 'NONE').map((s) => (s === w ? 'WEB' : 'ANDROID') + ':' + s.attribution);
        const key = cls + (labels.length ? ' (' + labels.join(', ') + ')' : ' (no side attributed)');
        attributedNonParity[key] = (attributedNonParity[key] || 0) + 1;
      }
      own.push({ sut_id: sut, pair_index: k, web: w, android: a, pair_class: cls, parity: cls === 'PARITY' });
    }
    const total = own.length;
    if (total !== web.n) violations.push(`${sut}: ${total} pairs, not ${web.n}`);
    if (Object.values(classes).reduce((x, y) => x + y, 0) !== total) violations.push(`${sut}: the pair classes do not sum to the pairs`);
    // the cross-tabulation of the two categories, a complete reading of the pairs
    const crosstab = {};
    for (const p of own) { const key = `${p.web.category} | ${p.android.category}`; crosstab[key] = (crosstab[key] || 0) + 1; }
    const identities = {};
    for (const p of own) for (const [surface, s] of [['WEB', p.web], ['ANDROID', p.android]]) {
      if (s.category === cfg.arrival_success_categories[0]) { identities[surface] = identities[surface] || {}; identities[surface][s.identity] = (identities[surface][s.identity] || 0) + 1; }
    }
    ecosystems.push({ sut_id: sut, web_condition_id: web.condition_id, android_condition_id: and.condition_id, pairs: total, parity_pairs: parity,
      parity_proportion: core.rate(parity, total, WILSON_Z), pair_class_counts: classes, non_parity_pairs_by_class_and_attribution: attributedNonParity,
      category_pairs_crosstab: crosstab, identity_counts_among_read: identities,
      web_surface: surfaceStats[web.condition_id], android_surface: surfaceStats[and.condition_id] });
    pairs.push(...own);
  }

  // ---- SUT-01 versus SUT-02 -----------------------------------------------------------------------------------------
  let comparison = null;
  const e1 = ecosystems.find((e) => e.sut_id === 'SUT-01'); const e2 = ecosystems.find((e) => e.sut_id === 'SUT-02');
  if (e1 && e2) {
    comparison = { id: 'SUT-01 vs SUT-02, CS-007, parity proportion (WEB and ANDROID)', classification: 'CONFIRMATORY (H4), cross-platform part, as pre-registered in the campaign configuration; descriptive in weight (one canonical scenario gives one scenario pair per comparison, D-E06-7)',
      sut_a: 'SUT-01', sut_b: 'SUT-02', parity_a: e1.parity_pairs, pairs_a: e1.pairs, parity_b: e2.parity_pairs, pairs_b: e2.pairs,
      table_parity_by_ecosystem: [[e1.parity_pairs, e1.pairs - e1.parity_pairs], [e2.parity_pairs, e2.pairs - e2.parity_pairs]],
      risk_difference: riskDifference(e1.parity_pairs, e1.pairs, e2.parity_pairs, e2.pairs, WILSON_Z),
      fisher_exact_two_sided_p: fisherExact(e1.parity_pairs, e1.pairs - e1.parity_pairs, e2.parity_pairs, e2.pairs - e2.parity_pairs),
      multiplicity: 'this is the only comparison under RQ4 with a p-value: the four candidate comparisons of E07 are not evaluable (decision DP-4), so the Holm-adjusted p-value equals the reported one',
      verdict: 'none: no support or non-support criterion is frozen for H4, and none is invented' };
  }
  return { surfaces: surfaceStats, ecosystems, pairs, comparison, toolchain_drift_confounds: drift, violations };
}

function main() {
  const pins = { START_COMMIT, FREEZE_COMMIT, RAW_TREE, CONFIG_SHA256, CONDITIONS_SHA256, CORE_BLOB };
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
  const manifestStatus = fs.readFileSync(path.join(REPO, 'manifests/study-manifest.yaml'), 'utf8').match(/- id: E06-cross-platform-parity\n\s+status: (\w+)/);
  if (!manifestStatus || manifestStatus[1] !== 'FROZEN') fail('E06 is not FROZEN in the study manifest');

  const cfg = JSON.parse(condBuf.toString('utf8'));
  if (cfg.n_per_condition !== N || cfg.conditions.length !== 4 || cfg.conditions.some((c) => c.n !== N)) fail('the conditions file is not the locked one (four conditions, N = 50 each)');
  const SUT_DIRS = Array.from(new Set(cfg.conditions.map((c) => c.sut_id))).sort();
  const attemptOf = (id) => ATTEMPT_OF[id] || 1;

  // ---- the run and job directories ---------------------------------------------------------------------------------
  const present = fs.readdirSync(path.join(REPO, RAW)).filter((d) => !d.startsWith('.')).sort();
  if (JSON.stringify(present) !== JSON.stringify(SUT_DIRS)) fail('the SUT directories are not ' + SUT_DIRS.join(', '));
  const expectedRuns = []; const expectedJobs = [];
  for (const c of cfg.conditions) {
    expectedJobs.push(`${c.sut_id}/${c.condition_id}__job__A${attemptOf(c.condition_id)}`);
    for (let n = 1; n <= N; n++) expectedRuns.push(`${c.sut_id}/${c.condition_id}__EX${String(n).padStart(4, '0')}__A${attemptOf(c.condition_id)}`);
  }
  const foundRuns = []; const foundJobs = [];
  for (const sut of SUT_DIRS) {
    for (const d of fs.readdirSync(path.join(REPO, RAW, sut)).filter((x) => !x.startsWith('.')).sort()) (/__job__A\d+$/.test(d) ? foundJobs : foundRuns).push(`${sut}/${d}`);
  }
  if (JSON.stringify([...foundRuns].sort()) !== JSON.stringify([...expectedRuns].sort())) fail(`the set of run directories is not the ${expectedRuns.length} expected`);
  if (JSON.stringify([...foundJobs].sort()) !== JSON.stringify([...expectedJobs].sort())) fail(`the set of job directories is not the ${expectedJobs.length} expected`);

  const executions = []; const rows = []; let filesRead = 0; const jobRecords = {};
  for (const c of cfg.conditions) {
    const att = attemptOf(c.condition_id);
    const jobBase = path.join(REPO, RAW, c.sut_id, `${c.condition_id}__job__A${att}`);
    const summary = readJson(path.join(jobBase, 'condition-summary.json'));
    const jobProv = readJson(path.join(jobBase, 'ci-provenance.json'));
    filesRead += 2;
    if (summary.condition !== c.condition_id || summary.sut_id !== c.sut_id || summary.surface !== c.surface || summary.attempt !== att || summary.record_class !== 'MEASURED_EXPERIMENT') fail(c.condition_id + ': the condition summary names another condition, surface, attempt or record class');
    if (summary.executions_run !== N || summary.executions_planned !== N || summary.first_execution !== 1 || (summary.executions || []).length !== N) fail(c.condition_id + ': the condition summary does not hold 50 executions from the first');
    if (summary.identity_oracle !== c.identity_oracle) fail(c.condition_id + ': the identity oracle of the summary is not the one of the conditions file');
    if (jobProv.condition_id !== c.condition_id || jobProv.attempt !== att || jobProv.campaign_id !== 'E06-cross-platform-parity') fail(c.condition_id + ': the job provenance names another condition or attempt');
    jobRecords[c.condition_id] = { attempt: att, github_run_id: jobProv.github && jobProv.github.run_id, workflow_file_sha256: jobProv.workflow && jobProv.workflow.file_sha256,
                                   further_attempt_approval_sha256: jobProv.frozen_input_hashes && jobProv.frozen_input_hashes.further_attempt_approval_sha256,
                                   condition_summary_sha256: sha(fs.readFileSync(path.join(jobBase, 'condition-summary.json'))) };
    for (let n = 1; n <= N; n++) {
      const ex = `EX${String(n).padStart(4, '0')}`;
      const d = `${c.condition_id}__${ex}__A${att}`;
      const base = path.join(REPO, RAW, c.sut_id, d);
      const man = readJson(path.join(base, 'run-manifest.json'));
      filesRead += 1;
      if (man.run_id !== d || man.condition !== c.condition_id || man.campaign_id !== 'E06-cross-platform-parity' || man.sut_id !== c.sut_id || man.attempt !== att || man.scenario !== 'CS-007') fail(d + ': identity fields of the run manifest disagree');
      const entry = summary.executions[n - 1];
      if (!entry || entry.run_id !== d || entry.execution_index !== n) fail(d + ': the condition summary has no matching entry at its position');
      if (!man.outcome || man.outcome.outcome_category !== entry.category) fail(d + ': the outcome category of the run manifest and of the condition summary disagree');
      if (typeof man.outcome.matches_expected !== 'boolean') fail(d + ': matches_expected is not a boolean');
      const m = /attribution=(\w+)/.exec(man.notes || '');
      if (!m || m[1] !== entry.attribution) fail(d + ': the attribution of the run manifest and of the condition summary disagree');
      let facts = null; const factsPath = path.join(base, 'evidence', '004-facts.json');
      if (fs.existsSync(factsPath)) { facts = readJson(factsPath); filesRead += 1; if (facts.surface !== c.platform || facts.sut_id !== c.sut_id) fail(d + ': the evidence facts name another surface or SUT'); }
      if (entry.category === 'ARRIVED_IDENTITY_READ') {
        if (!facts || facts.identity !== entry.identity || facts.identity_raw !== entry.identity_raw) fail(d + ': the identity of the evidence facts and of the condition summary disagree');
      }
      executions.push({ condition_id: c.condition_id, run_id: d, execution_index: n, category: entry.category, reason: entry.reason === undefined ? null : entry.reason,
                        attribution: entry.attribution, identity: entry.identity === undefined ? null : entry.identity, identity_raw: entry.identity_raw === undefined ? null : entry.identity_raw,
                        arrived: entry.arrived, status: man.outcome.status, toolchain: man.toolchain });
      rows.push({ run_id: d, condition_id: c.condition_id, sut_id: c.sut_id, surface: c.surface, execution_id: ex, attempt: att, outcome_category: entry.category,
                  reason: entry.reason === undefined ? null : entry.reason, attribution: entry.attribution, arrived: entry.arrived,
                  identity_raw: entry.identity_raw === undefined ? null : entry.identity_raw, identity: entry.identity === undefined ? null : entry.identity,
                  workflow_outcome_status: man.outcome.status, matches_expected: man.outcome.matches_expected });
    }
  }

  const evaluated = evaluate(cfg, executions);
  if (evaluated.violations.length) { console.error(evaluated.violations.join('\n')); fail(evaluated.violations.length + ' consistency violation(s)'); }
  const surfaces = evaluated.surfaces;
  const pairRows = evaluated.pairs.map((p) => ({ sut_id: p.sut_id, pair_index: p.pair_index, web_run_id: p.web.run_id, web_category: p.web.category, web_reason: p.web.reason, web_attribution: p.web.attribution,
    web_identity_raw: p.web.identity_raw, web_identity: p.web.identity, android_run_id: p.android.run_id, android_category: p.android.category, android_reason: p.android.reason,
    android_attribution: p.android.attribution, android_identity_raw: p.android.identity_raw, android_identity: p.android.identity, pair_class: p.pair_class, parity: p.parity }));
  const result = {
    record: 'Parity analysis, E06-cross-platform-parity (derived dataset; descriptive; produced by analysis/e06-parity-analysis/compute-parity-e06.js from the frozen raw-data/E06-cross-platform-parity)',
    campaign_id: 'E06-cross-platform-parity',
    hypothesis_note: 'H4, cross-platform part: the one comparison of the configuration, SUT-01 versus SUT-02 on CS-007, is computed with the risk difference and Fisher exact test the configuration names; it is descriptive in weight (one canonical scenario gives one scenario pair per comparison, D-E06-7) and no support or non-support criterion is frozen for H4, so this dataset states no verdict; SUT-01 versus SUT-03 is not estimable (no mobile data).',
    metric_source: 'experiments/E06-cross-platform-parity/README.md, "Campaign configuration", "Outcome categories, pairing and the parity proportion" and "Analysis and what is not computed"; conditions file, pairing_rule, parity_rule and estimand; manifests/campaign-execution-decisions-v17.yaml and -v18.yaml (D-E06-7, D-E06-8, D-E06-15); protocol/statistical-analysis-plan-v1.md, sections 3 and 4.3',
    estimators: { parity_proportion: 'pairs with parity over the 50 pairs of the ecosystem (execution k of the WEB condition with execution k of the ANDROID condition); parity: both ARRIVED_IDENTITY_READ and the same normalized identity',
                  interval: 'Wilson score interval without continuity correction, z = ' + WILSON_Z,
                  risk_difference: 'parity proportion of SUT-01 minus that of SUT-02, with the Newcombe hybrid score interval (method 10) built from the two Wilson intervals',
                  fisher_exact: 'two-sided, the sum of the hypergeometric probabilities of the tables with the same margins that are not above that of the observed table',
                  pair_class_precedence: 'NOT_ARRIVED, IDENTITY_UNREADABLE, ARRIVAL_ONLY, IDENTITY_DIFFERENT, PARITY', NOT_ESTIMABLE: 'the rate of an empty denominator; never reported as 0' },
    inputs: { raw_tree: RAW, raw_git_tree: treeHead, pinned_at_commit: FREEZE_COMMIT, campaign_state: 'FROZEN', run_bundles: rows.length, job_directories: foundJobs.length,
              imported_attempts: Object.fromEntries(cfg.conditions.map((c) => [c.condition_id, attemptOf(c.condition_id)])),
              attempts_without_bundle: ATTEMPTS_WITHOUT_BUNDLE, job_records: jobRecords,
              conditions_file: CONDITIONS, conditions_file_sha256: CONDITIONS_SHA256, campaign_configuration_sha256: CONFIG_SHA256 },
    totals: { ecosystems: evaluated.ecosystems.length, executions: rows.length, pairs: pairRows.length, parity_pairs: pairRows.filter((p) => p.parity).length,
              note: 'counts only; no pooling of rates across ecosystems or surfaces is computed' },
    ecosystems: evaluated.ecosystems,
    comparison_sut01_vs_sut02: evaluated.comparison,
    comparisons_not_estimable: COMPARISONS_NOT_ESTIMABLE,
    cells_without_condition: ['SUT-03 (WEB only: no mobile surface)', 'SUT-04 (WEB only: no mobile surface)', 'SUT-05 (NOT_COMPARABLE)', 'SUT-06 (NOT_COMPARABLE)', 'iOS (deferred, D-E06-5)'],
    toolchain_drift_confounds: evaluated.toolchain_drift_confounds,
    consistency_violations: evaluated.violations,
    not_computed: 'No pooled rate across ecosystems or surfaces, composite score, latency, ranking or result for iOS: the configuration lists them as not computed.'
  };
  const jsonText = JSON.stringify(result, null, 2) + '\n';
  const execHeader = ['run_id', 'condition_id', 'sut_id', 'surface', 'execution_id', 'attempt', 'outcome_category', 'reason', 'attribution', 'arrived', 'identity_raw', 'identity', 'workflow_outcome_status', 'matches_expected'];
  const execText = execHeader.join(',') + '\n' + rows.map((r) => execHeader.map((h) => csvCell(r[h])).join(',')).join('\n') + '\n';
  const pairHeader = ['sut_id', 'pair_index', 'web_run_id', 'web_category', 'web_reason', 'web_attribution', 'web_identity_raw', 'web_identity', 'android_run_id', 'android_category', 'android_reason',
                      'android_attribution', 'android_identity_raw', 'android_identity', 'pair_class', 'parity'];
  const pairText = pairHeader.join(',') + '\n' + pairRows.map((r) => pairHeader.map((h) => csvCell(r[h])).join(',')).join('\n') + '\n';
  const outputs = [[OUT_JSON, jsonText], [OUT_EXEC, execText], [OUT_PAIRS, pairText]];

  if (process.argv.includes('--check')) {
    const ok = outputs.every(([p, text]) => fs.existsSync(path.join(REPO, p)) && fs.readFileSync(path.join(REPO, p), 'utf8') === text);
    console.log(ok ? 'CHECK OK: the files on disk equal the recomputation' : 'CHECK FAILED: the files on disk differ from the recomputation');
    process.exit(ok ? 0 : 3);
  }
  fs.mkdirSync(path.dirname(path.join(REPO, OUT_JSON)), { recursive: true });
  for (const [p, text] of outputs) { fs.writeFileSync(path.join(REPO, p), text); console.log(`wrote ${p} (sha256 ${sha(Buffer.from(text))})`); }
  console.log(`run bundles ${rows.length}, files read ${filesRead}, pairs ${pairRows.length}; violations ${evaluated.violations.length}`);
}

module.exports = { evaluate, classifyPair, fisherExact, riskDifference, WILSON_Z, PAIR_CLASSES, COMPARISONS_NOT_ESTIMABLE };
if (require.main === module) main();
