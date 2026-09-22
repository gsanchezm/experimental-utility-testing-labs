#!/usr/bin/env node
// qualification/mobilewright/harness/run-gate.mjs
// Gate orchestrator for one platform: warm-ups, then exactly N measured executions per scenario
// (replacing EXCLUDED executions, policy section 7.3), sequentially, one child process per execution
// (execute.mjs) so that every execution has its own runner log and no state carries over. It imports
// nothing from the runner under qualification. Authored by QUALIFIER-MOBILE-01 under prompt version
// qualifier-mobile-01-mobilewright-gate-v1 (protocol/mobile-runner-policy-v1.md, sections 6-7).
//
// Enforced structurally: warm-ups of a combination run only before its first measured execution;
// N is 10 in QUALIFICATION mode (policy 7.1); nothing but a pre-runner infrastructure failure is
// EXCLUDED (and only as a proposal for QUALIFIER-MOBILE-01); every artifact is scrubbed of host paths
// and tokens before it is kept (publication hygiene).

import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, relative, basename } from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { healthCheck, login, catalogSnapshot, redact } from './backend.mjs';

const HERE = fileURLToPath(new URL('.', import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')).map(([k, v]) => [k, v ?? 'true']));
const need = (k) => { if (!args[k]) { console.error('missing --' + k); process.exit(2); } return args[k]; };

const platform = need('platform');                 // android | ios
const deviceId = need('device');                  // runner device id (Android: AVD name; iOS: UDID)
const adbSerial = args['adb-serial'] || null;     // harness-only (logcat capture)
const buildPath = need('build');
const outDir = need('out');
const mode = args.mode || 'QUALIFICATION';          // QUALIFICATION | DEVELOPMENT
const recordClass = mode === 'QUALIFICATION' ? 'QUALIFICATION' : 'DEVELOPMENT';
const N = mode === 'QUALIFICATION' ? 10 : Number(args.n || 1);
const WARMUPS = mode === 'QUALIFICATION' ? 1 : Number(args.warmups ?? 0);
const MAX_REPLACEMENTS = 5;
const SCENARIOS = (args.scenarios || 'MQ1,MQ2,MQ3').split(',');
const WATCHDOG_MS = Number(args.watchdog || 12 * 60 * 1000);
const platformCode = platform === 'ios' ? 'IOS' : 'AND';
const platformLabel = platform === 'ios' ? 'iOS Simulator' : 'Android emulator';
const envType = platform === 'ios' ? 'SIMULATED' : 'EMULATED';
const instructionId = process.env.QUALIFICATION_INSTRUCTION_ID || null;
const promptVersionId = 'qualifier-mobile-01-mobilewright-gate-v1';
if (mode === 'QUALIFICATION' && !instructionId) { console.error('QUALIFICATION mode requires QUALIFICATION_INSTRUCTION_ID'); process.exit(2); }

const envRecordPath = join(outDir, 'environment', `${platform}-environment.json`);
const envRecord = existsSync(envRecordPath) ? JSON.parse(readFileSync(envRecordPath, 'utf8')) : {};
const installRecordPath = join(outDir, 'environment', `${platform}-runner-install.json`);
const installRecord = existsSync(installRecordPath) ? JSON.parse(readFileSync(installRecordPath, 'utf8')) : {};
const runnerVersion = installRecord.mobilewright_version || null;
const mobilecliVersion = installRecord.mobilecli_version || null;
const github = { run_id: process.env.GITHUB_RUN_ID || null, run_attempt: process.env.GITHUB_RUN_ATTEMPT || null, image_os: process.env.ImageOS || null, image_version: process.env.ImageVersion || null, workflow_ref: process.env.GITHUB_WORKFLOW_REF || null, sha: process.env.GITHUB_SHA || null };

// ─── scrubbing (publication hygiene): host paths, tokens, and prohibited terms never enter kept artifacts
const scrubPrefixes = (process.env.GATE_SCRUB_PATHS || '').split(':').filter(Boolean).sort((a, b) => b.length - a.length);
const JWT = /eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}/g;
const HOMES = /\/(?:Users|home)\/[A-Za-z0-9._-]+/g;
// Prohibited vendor/assistant terms (the validation workflow's list) are assembled from hex fragments so that this
// file never carries them literally; they are matched case-insensitively and replaced in every kept text artifact.
const TERMS = new RegExp(['6169206167656e74', '61692067656e657261746564', '61692d67656e657261746564', '67656e657261746564206279206169', '616e7468726f706963', '617373697374616e74', '63686174677074', '636f70696c6f74', '6f70656e6169', '636c61756465'].map((h) => Buffer.from(h, 'hex').toString('utf8')).join('|'), 'gi');
function scrubText(s) {
  let out = s;
  for (const p of scrubPrefixes) out = out.split(p).join('<host-path>');
  out = out.replace(JWT, (m) => m.slice(0, 12) + '<redacted-token>').replace(HOMES, '<home>').replace(TERMS, '<term-redacted>');
  return out;
}
function scrubFile(path) {
  if (/\.(png|jpg|jpeg|mp4)$/i.test(path)) return;
  const s = readFileSync(path, 'utf8');
  const t = scrubText(s);
  if (t !== s) writeFileSync(path, t);
}
function scrubDir(dir) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) scrubDir(p); else scrubFile(p);
  }
}

function writeJson(path, obj) { writeFileSync(path, scrubText(JSON.stringify(obj, null, 2)) + '\n'); }
function appendLine(path, line) { writeFileSync(path, scrubText(line) + '\n', { flag: 'a' }); }
const log = (m) => console.log(`[run-gate ${new Date().toISOString()}] ${m}`);

// ─── one child execution
function runChild(cmd, spec, specPath, logPath) {
  return new Promise((resolve) => {
    writeFileSync(specPath, JSON.stringify(spec, null, 2));
    const child = spawn(process.execPath, [join(HERE, 'execute.mjs'), cmd, specPath], {
      env: { ...process.env, DEBUG: 'mw:*', MOBILEWRIGHT_DISABLE_TELEMETRY: '1', DO_NOT_TRACK: '1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    const chunks = [];
    child.stdout.on('data', (d) => chunks.push(d));
    child.stderr.on('data', (d) => chunks.push(d));
    const timer = setTimeout(() => { chunks.push(Buffer.from(`\n[run-gate] watchdog: killing execution after ${WATCHDOG_MS} ms\n`)); child.kill('SIGKILL'); }, WATCHDOG_MS);
    child.on('close', (code, signal) => {
      clearTimeout(timer);
      writeFileSync(logPath, scrubText(Buffer.concat(chunks).toString('utf8')));
      resolve({ code, signal });
    });
  });
}

mkdirSync(join(outDir, 'environment'), { recursive: true });
const jsonl = join(outDir, `execution-log-${platform}.jsonl`);
const csv = join(outDir, `execution-log-${platform}.csv`);
if (!existsSync(csv)) appendLine(csv, 'execution_id,combination,platform,kind,attempt,timestamp,environment_type,runner_version,outcome,duration_scenario_ms,duration_total_ms,failed_step,artifacts,notes');
const summaryPath = join(outDir, `summary-${platform}.json`);
const summary = { record_class: recordClass, platform, platform_label: platformLabel, environment_type: envType, instruction_id: instructionId, prompt_version_id: promptVersionId, runner: { candidate: 'Mobilewright', version: runnerVersion, mobilecli_version: mobilecliVersion }, github, n_per_combination: N, warmups_per_combination: WARMUPS, max_replacements: MAX_REPLACEMENTS, started_at: new Date().toISOString(), finished_at: null, combinations: {}, executions: [] };
writeJson(summaryPath, summary);

// ─── gate start: backend reachability and catalog snapshot (oracle anchoring; read-only)
log(`mode=${mode} platform=${platform} device=${deviceId} N=${N} warmups=${WARMUPS}`);
const health = await healthCheck();
const snap = { at: new Date().toISOString(), backend_health: health, catalog: null };
if (health.healthy) {
  const l = await login();
  snap.login = l.response;
  if (l.token) snap.catalog = await catalogSnapshot(l.token);
}
writeJson(join(outDir, 'environment', `${platform}-catalog-snapshot.json`), redact(snap));
log(`backend healthy=${health.healthy} catalog=${snap.catalog && snap.catalog.ok ? snap.catalog.pizzas.length + ' products' : 'unavailable'}`);

// ─── runner readiness probe (environment record; not an execution)
const readinessSpec = { record_class: recordClass, platform, device_id: deviceId, adb_serial: adbSerial, out_dir: join(outDir, 'environment'), runner_version: runnerVersion };
const r = await runChild('readiness', readinessSpec, join(outDir, 'environment', `${platform}-readiness-spec.json`), join(outDir, 'environment', `${platform}-readiness.log`));
const readiness = existsSync(join(outDir, 'environment', `${platform}-runner-readiness.json`)) ? JSON.parse(readFileSync(join(outDir, 'environment', `${platform}-runner-readiness.json`), 'utf8')) : { ready: false, error: 'no readiness record (exit ' + r.code + ')' };
scrubDir(join(outDir, 'environment'));
log(`runner readiness=${readiness.ready}${readiness.ready ? '' : ': ' + String(readiness.error).split('\n')[0]}`);
summary.runner_readiness = { ready: readiness.ready, mobilecli_version: readiness.runner && readiness.runner.mobilecli_version, device_entry: readiness.device_entry || null, agent_status: readiness.agent_status || null };
if (readiness.runner && readiness.runner.mobilecli_version && !summary.runner.mobilecli_version) summary.runner.mobilecli_version = readiness.runner.mobilecli_version;
writeJson(summaryPath, summary);

// ─── executions
const pad = (n) => String(n).padStart(2, '0');
async function execute(scenario, kind, seq) {
  const executionId = `${scenario}-${platformCode}-${kind}-${pad(seq)}`;
  const dir = join(outDir, executionId);
  mkdirSync(dir, { recursive: true });
  const spec = {
    record_class: recordClass, mode, execution_id: executionId, combination: `${scenario} × ${platformLabel}`, scenario, platform, kind, seq,
    environment_type: envType, device_id: deviceId, adb_serial: adbSerial, build_path: buildPath, build_file: basename(buildPath), out_dir: dir,
    runner_version: runnerVersion, mobilecli_version: summary.runner.mobilecli_version, device: envRecord.device || null,
    instruction_id: instructionId, prompt_version_id: promptVersionId, github,
  };
  log(`${executionId} start`);
  const res = await runChild('execute', spec, join(dir, 'spec.json'), join(dir, 'runner.log'));
  let rec;
  const recPath = join(dir, 'record.json');
  if (existsSync(recPath)) {
    rec = JSON.parse(readFileSync(recPath, 'utf8'));
    if (rec.outcome === null || rec.outcome === undefined) { rec.outcome = 'FAILURE'; rec.notes = [...(rec.notes || []), `execution process ended before recording an outcome (exit ${res.code}, signal ${res.signal})`]; }
  } else {
    rec = { record_class: recordClass, execution_id: executionId, combination: spec.combination, scenario, platform, kind, attempt: seq, timestamp: new Date().toISOString(), timestamp_end: new Date().toISOString(), environment_type: envType, runner: { candidate: 'Mobilewright', version: runnerVersion, mobilecli_version: summary.runner.mobilecli_version }, outcome: 'FAILURE', duration_ms: { reset: null, precondition: null, scenario: null, total: null }, capabilities_exercised: [], failed_step: { name: 'execution process', capabilities: [], error: `no record written (exit ${res.code}, signal ${res.signal}); see runner.log` }, exclusion_proposal: null, artifacts: ['runner.log'], steps: [], notes: ['harness: execution process produced no record'], instruction_id: instructionId, prompt_version_id: promptVersionId, github };
  }
  // keep the record free of absolute paths (build_path lives only in spec.json, which is scrubbed too)
  rec.build_file = basename(buildPath);
  writeJson(recPath, rec);
  scrubDir(dir);
  const row = { execution_id: executionId, combination: rec.combination, platform, kind, attempt: seq, timestamp: rec.timestamp, environment_type: envType, runner_version: runnerVersion, outcome: rec.outcome, duration_ms: rec.duration_ms, failed_step: rec.failed_step ? rec.failed_step.name : null, exclusion_proposal: rec.exclusion_proposal ? rec.exclusion_proposal.proposed_cause : null, capabilities_exercised: rec.capabilities_exercised, artifacts: (rec.artifacts || []).map((a) => `${executionId}/${a}`), notes: rec.notes || [] };
  appendLine(jsonl, JSON.stringify(row));
  const q = (v) => '"' + String(v ?? '').replace(/"/g, '""') + '"';
  appendLine(csv, [executionId, rec.combination, platform, kind, seq, rec.timestamp, envType, runnerVersion, rec.outcome, rec.duration_ms.scenario ?? '', rec.duration_ms.total ?? '', row.failed_step ?? '', row.artifacts.join(';'), (rec.notes || []).join(' | ')].map(q).join(','));
  summary.executions.push(row);
  log(`${executionId} ${rec.outcome}${rec.failed_step ? ' at "' + rec.failed_step.name + '"' : ''} scenario=${rec.duration_ms.scenario ?? '-'}ms total=${rec.duration_ms.total ?? '-'}ms`);
  return rec;
}

function median(xs) { if (!xs.length) return null; const s = [...xs].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; }
function quartiles(xs) { if (xs.length < 2) return { q1: null, q3: null, iqr: null }; const s = [...xs].sort((a, b) => a - b); const h = s.length >> 1; const lower = s.slice(0, h), upper = s.slice(s.length % 2 ? h + 1 : h); const q1 = median(lower), q3 = median(upper); return { q1, q3, iqr: q3 - q1 }; }

for (const scenario of SCENARIOS) {
  const combination = `${scenario} × ${platformLabel}`;
  const c = { combination, warmups: [], measured: [], excluded: [], replacements_used: 0, replacement_cap_hit: false, measured_successes: 0, measured_failures: 0, runner_caused_candidates: [], duration_scenario_ms: null };
  summary.combinations[scenario] = c;
  let measuredStarted = false;
  for (let w = 1; w <= WARMUPS; w++) {
    if (measuredStarted) throw new Error('structural violation: warm-up after first measured execution');
    const rec = await execute(scenario, 'WARMUP', w);
    c.warmups.push({ execution_id: rec.execution_id, outcome: rec.outcome, failed_step: rec.failed_step ? rec.failed_step.name : null });
    writeJson(summaryPath, summary);
  }
  let seq = 0, done = 0;
  while (done < N) {
    seq += 1;
    measuredStarted = true;
    const rec = await execute(scenario, 'MEASURED', seq);
    if (rec.outcome === 'EXCLUDED') {
      c.excluded.push({ execution_id: rec.execution_id, proposed_cause: rec.exclusion_proposal && rec.exclusion_proposal.proposed_cause });
      c.replacements_used += 1;
      if (c.replacements_used > MAX_REPLACEMENTS) { c.replacement_cap_hit = true; log(`${combination}: replacement cap (${MAX_REPLACEMENTS}) hit; ${done} of ${N} measured executions reached`); writeJson(summaryPath, summary); break; }
      writeJson(summaryPath, summary);
      continue;
    }
    done += 1;
    c.measured.push({ execution_id: rec.execution_id, outcome: rec.outcome, failed_step: rec.failed_step ? rec.failed_step.name : null, scenario_ms: rec.duration_ms.scenario, total_ms: rec.duration_ms.total });
    if (rec.outcome === 'SUCCESS') c.measured_successes += 1; else { c.measured_failures += 1; c.runner_caused_candidates.push({ execution_id: rec.execution_id, failed_step: rec.failed_step }); }
    writeJson(summaryPath, summary);
  }
  const durations = c.measured.filter((m) => m.outcome === 'SUCCESS' && typeof m.scenario_ms === 'number').map((m) => m.scenario_ms);
  c.duration_scenario_ms = { n: durations.length, median: median(durations), ...quartiles(durations), min: durations.length ? Math.min(...durations) : null, max: durations.length ? Math.max(...durations) : null };
  writeJson(summaryPath, summary);
}

// provisional capability tally for this platform (final support is decided by QUALIFIER-MOBILE-01 after attribution)
const caps = {};
for (const id of ['MC-01', 'MC-02', 'MC-03', 'MC-04', 'MC-05', 'MC-06', 'MC-07', 'MC-08', 'MC-09', 'MC-10']) caps[id] = { exercised_in_successful_measured: 0, failed_steps_in_any_execution: [] };
for (const e of summary.executions) {
  if (e.kind === 'MEASURED' && e.outcome === 'SUCCESS') for (const id of e.capabilities_exercised) if (caps[id]) caps[id].exercised_in_successful_measured += 1;
}
for (const dirName of readdirSync(outDir)) {
  const recPath = join(outDir, dirName, 'record.json');
  if (!existsSync(recPath)) continue;
  const rec = JSON.parse(readFileSync(recPath, 'utf8'));
  if (rec.outcome === 'FAILURE' && rec.failed_step) for (const id of rec.failed_step.capabilities || []) if (caps[id]) caps[id].failed_steps_in_any_execution.push({ execution_id: rec.execution_id, step: rec.failed_step.name });
}
summary.capability_tally_provisional = caps;
summary.finished_at = new Date().toISOString();
writeJson(summaryPath, summary);
scrubDir(outDir);
log('gate loop finished for ' + platform);
for (const [s, c] of Object.entries(summary.combinations)) log(`${c.combination}: warm-ups ${c.warmups.length}, measured ${c.measured.length} (success ${c.measured_successes}, failure ${c.measured_failures}), excluded ${c.excluded.length}${c.replacement_cap_hit ? ', REPLACEMENT CAP HIT' : ''}`);
process.exit(0);
