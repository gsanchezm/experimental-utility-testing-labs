#!/usr/bin/env node
// qualification/mobilewright/harness/import-artifacts.mjs
// Imports the artifacts of one GitHub Actions run of .github/workflows/e03-mobile-qualification.yml
// into a destination directory with an import record (run id, attempt, artifact ids, per-file SHA-256),
// mirroring the import discipline of experiments/E03-resetability/ci-cd-execution-model.md, section 7,
// but under qualification/ (QUALIFICATION artifacts only). Authored by QUALIFIER-MOBILE-01 under prompt
// version qualifier-mobile-01-mobilewright-gate-v1. Imports nothing from the runner under qualification.
//
// Usage: node import-artifacts.mjs --run=<run id> --repo=<owner/name> --dest=<dir> [--allow-development]
// QUALIFICATION artifacts (E03-QUALIFICATION-*) may be imported under qualification/mobilewright/output;
// DEVELOPMENT artifacts (E03-DEVELOPMENT-*) are refused unless --allow-development is given AND the
// destination is outside the repository (they are never gate executions and never enter the repository).

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync, cpSync, rmSync } from 'node:fs';
import { join, relative, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split('=')).map(([k, v]) => [k, v ?? 'true']));
const need = (k) => { if (!args[k]) { console.error('missing --' + k); process.exit(2); } return args[k]; };
const runId = need('run');
const repo = need('repo');
const dest = resolve(need('dest'));
const allowDev = args['allow-development'] === 'true';
const repoRoot = resolve(fileURLToPath(new URL('.', import.meta.url)), '..', '..', '..');
const insideRepo = dest.startsWith(repoRoot + '/');

const gh = (a) => execFileSync('gh', a, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
const run = JSON.parse(gh(['api', `repos/${repo}/actions/runs/${runId}`]));
const artifacts = JSON.parse(gh(['api', `repos/${repo}/actions/runs/${runId}/artifacts`])).artifacts;
const jobs = JSON.parse(gh(['api', `repos/${repo}/actions/runs/${runId}/jobs`])).jobs;

const record = {
  record_class: 'QUALIFICATION_IMPORT',
  imported_at: new Date().toISOString(),
  imported_by: 'QUALIFIER-MOBILE-01',
  prompt_version_id: 'qualifier-mobile-01-mobilewright-gate-v1',
  workflow: { repository: repo, name: run.name, path: run.path, run_id: run.id, run_number: run.run_number, run_attempt: run.run_attempt, event: run.event, head_sha: run.head_sha, head_branch: run.head_branch, created_at: run.created_at, updated_at: run.updated_at, status: run.status, conclusion: run.conclusion, html_url: run.html_url },
  jobs: jobs.map((j) => ({ id: j.id, name: j.name, status: j.status, conclusion: j.conclusion, started_at: j.started_at, completed_at: j.completed_at, runner_name: j.runner_name, labels: j.labels })),
  artifacts: [],
  files: [],
};

function sha256(path) { return createHash('sha256').update(readFileSync(path)).digest('hex'); }
function walk(dir, out = []) { for (const f of readdirSync(dir)) { const p = join(dir, f); if (statSync(p).isDirectory()) walk(p, out); else out.push(p); } return out; }

mkdirSync(dest, { recursive: true });
const stage = join(tmpdir(), `eus-qualification-import-${runId}`);
rmSync(stage, { recursive: true, force: true });
mkdirSync(stage, { recursive: true });

for (const a of artifacts) {
  const isQual = a.name.startsWith('E03-QUALIFICATION-');
  const isDev = a.name.startsWith('E03-DEVELOPMENT-');
  if (!isQual && !isDev) { console.log(`skipping artifact of another class: ${a.name}`); continue; }
  if (isDev && (!allowDev || insideRepo)) { console.log(`refusing DEVELOPMENT artifact ${a.name} (never imported into the repository)`); continue; }
  if (isQual && !insideRepo) { console.log(`note: QUALIFICATION artifact ${a.name} imported outside the repository (inspection copy)`); }
  const adir = join(stage, a.name);
  gh(['run', 'download', String(runId), '-R', repo, '-n', a.name, '-D', adir]);
  const entry = { id: a.id, name: a.name, size_in_bytes: a.size_in_bytes, created_at: a.created_at, expires_at: a.expires_at, expired: a.expired, workflow_run_head_sha: a.workflow_run && a.workflow_run.head_sha, files: 0 };
  for (const p of walk(adir)) {
    const rel = relative(adir, p);
    const target = join(dest, rel);
    mkdirSync(dirname(target), { recursive: true });
    if (existsSync(target) && sha256(target) !== sha256(p)) { console.error(`conflict: ${rel} already exists with different content; refusing to overwrite`); process.exit(1); }
    cpSync(p, target);
    record.files.push({ artifact: a.name, path: rel, sha256: sha256(target), size_bytes: statSync(target).size });
    entry.files += 1;
  }
  record.artifacts.push(entry);
  console.log(`imported ${a.name}: ${entry.files} files`);
}
record.file_count = record.files.length;
writeFileSync(join(dest, `import-record-run${runId}-a${run.run_attempt}.json`), JSON.stringify(record, null, 2) + '\n');
rmSync(stage, { recursive: true, force: true });
console.log(`import record written: import-record-run${runId}-a${run.run_attempt}.json (${record.file_count} files from ${record.artifacts.length} artifacts)`);
