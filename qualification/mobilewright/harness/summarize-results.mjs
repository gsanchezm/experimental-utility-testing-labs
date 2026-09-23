#!/usr/bin/env node
// qualification/mobilewright/harness/summarize-results.mjs
// Deterministic transformation of the gate's execution records (qualification/mobilewright/output/) into
// the Markdown tables of qualification/mobilewright/README.md: execution log, results per combination,
// a step-based capability tally per platform, blocker counts per capability, and duration median / IQR.
// It computes nothing that requires attribution: a FAILURE is listed with its failed step and that
// step's capabilities; QUALIFIER-MOBILE-01 attributes (policy 7.3) in the README, never this script.
// Imports nothing from the runner under qualification. Usage: node summarize-results.mjs --out=<dir>
// Authored by QUALIFIER-MOBILE-01 under prompt version qualifier-mobile-01-mobilewright-gate-v1.
// Revised 2026-09-23 under manifests/mobile-qualification-implementation-lock-v2.yaml (PROTO-U12): --out is
// required (no default pointing at the quarantined output/), and artifact paths are labeled relative to
// qualification/mobilewright/ from the directory actually summarized. The computed tables are unchanged.

import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')).map(([k, v]) => [k, v ?? 'true']));
if (!args.out) { console.error('missing --out (the formal namespace to summarize, e.g. qualification/mobilewright/formal/<authorization id>)'); process.exit(2); }
const out = args.out;
const outLabel = relative(resolve(fileURLToPath(new URL('.', import.meta.url)), '..'), resolve(out));
const N = 10;
const CAPS = ['MC-01', 'MC-02', 'MC-03', 'MC-04', 'MC-05', 'MC-06', 'MC-07', 'MC-08', 'MC-09', 'MC-10'];
const CAP_NAMES = { 'MC-01': 'Install and launch', 'MC-02': 'Locate by stable identifier', 'MC-03': 'Text entry', 'MC-04': 'Tap / press native control', 'MC-05': 'Scroll / swipe', 'MC-06': 'Screen navigation and verification', 'MC-07': 'Deep link with parameters', 'MC-08': 'Read UI state', 'MC-09': 'App state reset between executions', 'MC-10': 'Artifact capture' };
const PLATFORMS = [['android', 'Android emulator'], ['ios', 'iOS Simulator']];

const records = [];
for (const d of readdirSync(out)) {
  const p = join(out, d, 'record.json');
  if (statSync(join(out, d)).isDirectory() && existsSync(p)) records.push(JSON.parse(readFileSync(p, 'utf8')));
}
records.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
const q = (v) => String(v ?? '').replace(/\|/g, '\\|').replace(/\n/g, ' ');
const sec = (ms) => (ms === null || ms === undefined ? '' : (ms / 1000).toFixed(1) + ' s');
const median = (xs) => { if (!xs.length) return null; const s = [...xs].sort((a, b) => a - b); const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const quart = (xs) => { if (xs.length < 4) return null; const s = [...xs].sort((a, b) => a - b); const h = s.length >> 1; return { q1: median(s.slice(0, h)), q3: median(s.slice(s.length % 2 ? h + 1 : h)) }; };

let md = '';
md += '### Execution log (generated from the records)\n\n';
md += '| execution_id | combination (MQn × platform) | kind (WARMUP / MEASURED / EXCLUDED) | attempt | timestamp | environment_type | Mobilewright version | outcome (SUCCESS / FAILURE / EXCLUDED) | duration | artifacts | notes |\n|---|---|---|---|---|---|---|---|---|---|---|\n';
for (const r of records) {
  const dur = r.outcome === 'SUCCESS' ? `scenario ${sec(r.duration_ms.scenario)}; total ${sec(r.duration_ms.total)}` : `total ${sec(r.duration_ms.total)}`;
  const note = r.outcome === 'FAILURE' ? `failed step: ${r.failed_step ? r.failed_step.name : 'n/a'}` : r.outcome === 'EXCLUDED' ? `proposed cause: ${r.exclusion_proposal && r.exclusion_proposal.proposed_cause}` : (r.harness && r.harness.ios_open_prompt_shown === true ? 'system open prompt accepted' : '');
  md += `| ${r.execution_id} | ${q(r.combination)} | ${r.kind} | ${r.attempt} | ${r.timestamp} | ${r.environment_type} | ${r.runner.version} | ${r.outcome} | ${dur} | \`${outLabel}/${r.execution_id}/\` | ${q(note)} |\n`;
}

md += '\n### Results per combination (generated)\n\n| Combination | Warm-ups (count) | Measured successes / 10 | Excluded (count) | Measured failures (count; runner-caused unless attributed) | Manual intervention (count) | Result |\n|---|---|---|---|---|---|---|\n';
const durRows = [];
const capTally = {};
for (const [plat, label] of PLATFORMS) {
  capTally[plat] = Object.fromEntries(CAPS.map((c) => [c, { success: 0, failed: [] }]));
  for (const sc of ['MQ1', 'MQ2', 'MQ3']) {
    const combo = `${sc} × ${label}`;
    const rs = records.filter((r) => r.combination === combo);
    if (!rs.length) continue;
    const warm = rs.filter((r) => r.kind === 'WARMUP');
    const meas = rs.filter((r) => r.kind === 'MEASURED' && r.outcome !== 'EXCLUDED');
    const excl = rs.filter((r) => r.outcome === 'EXCLUDED');
    const succ = meas.filter((r) => r.outcome === 'SUCCESS');
    const fail = meas.filter((r) => r.outcome === 'FAILURE');
    const result = succ.length === N && fail.length === 0 ? 'PASS (10/10)' : `FAIL (${succ.length}/${N})`;
    md += `| ${combo} | ${warm.length} (${warm.map((w) => w.outcome).join(', ') || '—'}) | ${succ.length} / ${N} | ${excl.length} | ${fail.length}${fail.length ? ' (' + fail.map((f) => f.execution_id).join(', ') + ')' : ''} | 0 (no manual step exists in the scripted scenarios) | ${result} |\n`;
    const xs = succ.map((r) => r.duration_ms.scenario).filter((x) => typeof x === 'number');
    const qq = quart(xs);
    durRows.push(`| ${combo} | ${xs.length ? sec(median(xs)) : '—'} | ${qq ? `${sec(qq.q3 - qq.q1)} (Q1 ${sec(qq.q1)}, Q3 ${sec(qq.q3)})` : '—'} | n = ${xs.length} successful measured executions; scenario time only (reset and MQ2 precondition excluded) |`);
    for (const r of meas) {
      if (r.outcome === 'SUCCESS') for (const c of r.capabilities_exercised) if (capTally[plat][c]) capTally[plat][c].success += 1;
      if (r.outcome === 'FAILURE' && r.failed_step) for (const c of r.failed_step.capabilities || []) if (capTally[plat][c]) capTally[plat][c].failed.push(r.execution_id);
    }
  }
}

md += '\n### Capability tally per platform (generated, step-based; attribution is recorded by QUALIFIER-MOBILE-01 in the Capability support table)\n\n| Capability | Android: successful measured executions exercising it | Android: measured failures at a step carrying it | iOS: successful measured executions exercising it | iOS: measured failures at a step carrying it |\n|---|---|---|---|---|\n';
for (const c of CAPS) {
  const a = capTally.android[c], i = capTally.ios[c];
  md += `| ${c} ${CAP_NAMES[c]} | ${a.success} | ${a.failed.length}${a.failed.length ? ' (' + a.failed.join(', ') + ')' : ''} | ${i.success} | ${i.failed.length}${i.failed.length ? ' (' + i.failed.join(', ') + ')' : ''} |\n`;
}

md += '\n### Failed steps in executions of any kind (criterion 7.2.3 input, generated)\n\n| execution_id | kind | failed step | capabilities carried by the step | error (first line) |\n|---|---|---|---|---|\n';
for (const r of records) if (r.outcome === 'FAILURE' && r.failed_step) md += `| ${r.execution_id} | ${r.kind} | ${q(r.failed_step.name)} | ${(r.failed_step.capabilities || []).join(', ')} | ${q((r.failed_step.error || '').split('\n')[0].slice(0, 160))} |\n`;

md += '\n### Secondary evidence — duration (generated)\n\n| Combination | Median duration | IQR | Notes |\n|---|---|---|---|\n' + durRows.join('\n') + '\n';
process.stdout.write(md);
