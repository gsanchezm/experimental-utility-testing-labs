#!/usr/bin/env node
// qualification/mobilewright/harness/execute.mjs
// One execution of the Mobilewright qualification gate (or the runner readiness probe), for one
// scenario x platform combination, entirely driven by the runner under qualification once the harness
// preconditions are met. Authored by QUALIFIER-MOBILE-01 under prompt version
// qualifier-mobile-01-mobilewright-gate-v1 (protocol/mobile-runner-policy-v1.md, sections 4-7).
//
// Usage: node execute.mjs execute <spec.json>   |   node execute.mjs readiness <spec.json>
// The spec is written by run-gate.mjs. Every execution writes <spec.out_dir>/record.json plus its
// artifacts (MC-10). Exit code 0 means "record written"; the outcome lives in the record.
//
// The scenario realization below is FIXED and identical for every execution; it is the executable
// form of the "Scenario realization" table in qualification/mobilewright/README.md.

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, basename } from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { android, ios, expect } from 'mobilewright';
import { healthCheck, login, seedCart, readCart, resetSession, redact, ACCOUNT, MARKET } from './backend.mjs';

const REALIZATION = {
  bundle_id: 'com.omnipizza.app',
  scheme: 'omnipizza',
  account: ACCOUNT.username,
  market: MARKET,
  MQ1: {
    login_screen: 'screen-login', username: 'input-username', password: 'input-password',
    market_control: 'btn-market-US', login_button: 'btn-login',
    terminal: ['screen-catalog', 'view-bottom-nav'],
  },
  MQ2: {
    first_card: 'card-pizza-p01', target_product: 'p12', target_open_control: 'btn-add-pizza-p12',
    product_screen: 'screen-pizza-builder', total_text: 'text-estimated-total-value',
    initial_total: '$15.99', size_control: 'btn-size-large', total_after: '$19.99',
  },
  MQ3: {
    seed: { pizza_id: 'p01', quantity: 2, size: 'large', toppings: [] },
    deep_link_path: 'checkout', deep_link_params: { market: MARKET, hydrateCart: 'true' },
    checkout_screen: 'screen-checkout', expected_title: '2x Margherita', expected_line_total: '$33.98',
  },
};

const T = { screen: 90000, expect: 30000, action: 30000, appLaunch: 60000, install: 300000, rpc: 300000 };

const iso = () => new Date().toISOString();
const errText = (e) => (e && e.stack ? String(e.stack) : String(e)).split('\n').slice(0, 12).join('\n');

const mode = process.argv[2];
const spec = JSON.parse(readFileSync(process.argv[3], 'utf8'));
const OUT = spec.out_dir;
mkdirSync(OUT, { recursive: true });
const launcher = spec.platform === 'ios' ? ios : android;

function writeJson(name, obj) {
  writeFileSync(join(OUT, name), JSON.stringify(obj, null, 2) + '\n');
  return name;
}

function mobilecliBinary() {
  try {
    const req = createRequire(import.meta.url);
    const pkg = req.resolve('mobilecli/package.json');
    const reqFromCli = createRequire(pkg);
    const p = process.platform, a = process.arch;
    const name = `mobilecli-${p}-${a === 'x64' ? 'amd64' : a}`;
    const plat = reqFromCli.resolve(`@mobilenext/${name}/package.json`);
    return join(plat, '..', name);
  } catch (e) {
    return null;
  }
}

function mobilecliVersion() {
  const bin = mobilecliBinary();
  if (!bin) return null;
  for (const args of [['--version'], ['version']]) {
    try { return execFileSync(bin, args, { encoding: 'utf8', timeout: 20000 }).trim(); } catch { /* try next */ }
  }
  return null;
}

function agentStatus(deviceId) {
  const bin = mobilecliBinary();
  if (!bin) return null;
  try { return JSON.parse(execFileSync(bin, ['agent', 'status', '--device', deviceId], { encoding: 'utf8', timeout: 60000 })); }
  catch (e) { return { error: errText(e) }; }
}

function deviceLog(platform, deviceId) {
  const serial = spec.adb_serial || deviceId;
  // Demonstrating artifact on failure (attribution support, policy section 7.3); harness-side, outside the runner.
  try {
    if (platform === 'android') {
      return execFileSync('adb', ['-s', serial, 'logcat', '-d', '-t', '600'], { encoding: 'utf8', timeout: 60000, maxBuffer: 16 * 1024 * 1024 });
    }
    return execFileSync('xcrun', ['simctl', 'spawn', deviceId, 'log', 'show', '--last', '3m', '--style', 'compact', '--predicate', 'process == "OmniPizza" OR eventMessage CONTAINS "omnipizza"'], { encoding: 'utf8', timeout: 90000, maxBuffer: 16 * 1024 * 1024 });
  } catch (e) {
    return 'device log capture failed: ' + errText(e);
  }
}

async function connect() {
  return launcher.launch({
    deviceId: spec.device_id,           // explicit id only; auto-discovery is never used
    autoAppLaunch: false,
    timeout: T.rpc,                     // per-call RPC timeout of the runner's device server (an install of the 81 MB build exceeds the 30 s default)
    actionTimeout: T.action,
    expectTimeout: T.expect,
    appLaunchTimeout: T.appLaunch,
    installTimeout: T.install,
  });
}

// ─── readiness probe (environment record; not an execution) ─────────────────────────────────────
if (mode === 'readiness') {
  const out = { record_class: spec.record_class, kind: 'RUNNER_READINESS', platform: spec.platform, device_id: spec.device_id, at: iso(), runner: { candidate: 'Mobilewright', version: spec.runner_version, mobilecli_version: mobilecliVersion() } };
  let device = null;
  out.attempts = [];
  try {
    // The device server is started on demand by the runner; on a cold emulator its first start can exceed the
    // runner's own 5 s start timeout, so the readiness probe (not an execution) retries up to three times.
    let lastErr = null;
    for (let attempt = 1; attempt <= 3 && !device; attempt++) {
      try { device = await connect(); await device.listApps(); out.attempts.push({ attempt, ok: true }); }
      catch (e) { lastErr = e; out.attempts.push({ attempt, ok: false, error: errText(e).split('\n')[0] }); if (device) { try { await device.close(); } catch { /* ignore */ } device = null; } await new Promise((r) => setTimeout(r, 10000)); }
    }
    if (!device) throw lastErr;
    const devices = await device.driver.listDevices({ platform: spec.platform });
    out.device_entry = devices.find((d) => d.id === spec.device_id) || null;
    out.screen_size = await device.screenSize();
    out.installed_apps_count = (await device.listApps()).length;
    const png = await device.screen.screenshot();
    writeFileSync(join(OUT, `${spec.platform}-readiness.png`), png);
    out.screenshot = `${spec.platform}-readiness.png`;
    out.agent_status = spec.platform === 'ios' ? agentStatus(spec.device_id) : { note: 'no on-device agent is needed on Android' };
    out.ready = true;
  } catch (e) {
    out.ready = false;
    out.error = errText(e);
  } finally {
    if (device) { try { await device.close(); } catch { /* ignore */ } }
  }
  writeJson(`${spec.platform}-runner-readiness.json`, out);
  process.exit(0);
}

// ─── one execution ──────────────────────────────────────────────────────────────────────────────
const rec = {
  record_class: spec.record_class,
  execution_id: spec.execution_id,
  combination: spec.combination,
  scenario: spec.scenario,
  platform: spec.platform,
  kind: spec.kind,
  attempt: spec.seq,
  timestamp: iso(),
  timestamp_end: null,
  environment_type: spec.environment_type,
  runner: { candidate: 'Mobilewright', version: spec.runner_version, mobilecli_version: spec.mobilecli_version || null },
  device: spec.device || null,
  instruction_id: spec.instruction_id,
  prompt_version_id: spec.prompt_version_id,
  github: spec.github || null,
  realization: REALIZATION,
  outcome: null,
  duration_ms: { reset: null, precondition: null, scenario: null, total: null },
  capabilities_exercised: [],
  failed_step: null,
  exclusion_proposal: null,
  harness: {},
  artifacts: [],
  steps: [],
  notes: [],
};
const t0 = Date.now();

async function step(name, capabilities, fn) {
  const s = { name, capabilities, started_at: iso(), status: 'RUNNING', duration_ms: null };
  rec.steps.push(s);
  const ts = Date.now();
  try {
    const r = await fn();
    s.status = 'OK'; s.duration_ms = Date.now() - ts;
    return r;
  } catch (err) {
    s.status = 'FAILED'; s.duration_ms = Date.now() - ts; s.error = errText(err);
    rec.failed_step = { name, capabilities, error: s.error };
    throw err;
  }
}

function finish(outcome) {
  rec.outcome = outcome;
  rec.timestamp_end = iso();
  rec.duration_ms.total = Date.now() - t0;
  const caps = new Set();
  for (const s of rec.steps) if (s.status === 'OK') for (const c of s.capabilities) caps.add(c);
  if (outcome === 'SUCCESS') { caps.add('MC-10'); }
  rec.capabilities_exercised = [...caps].sort();
  writeJson('record.json', rec);
}

function excluded(cause, description, artifacts) {
  rec.exclusion_proposal = { proposed_cause: cause, description, demonstrating_artifacts: artifacts, proposed_by: 'harness (pre-runner check); confirmed or rejected by QUALIFIER-MOBILE-01 in the README attribution table' };
  finish('EXCLUDED');
}

// Phase 0 — harness preconditions, BEFORE the first runner action (only these may propose EXCLUDED).
const precheck = { at: iso() };
precheck.backend_health = await healthCheck();
let token = null;
if (spec.scenario === 'MQ3' && precheck.backend_health.healthy) {
  const l = await login();
  precheck.login = l.response;
  token = l.token;
  if (token) {
    precheck.seed = await seedCart(token, REALIZATION.MQ3.seed);
  }
}
rec.artifacts.push(writeJson('harness-precheck.json', redact(precheck)));
if (!precheck.backend_health.healthy) {
  excluded('SUT_INSTANCE', 'hosted backend health check failed before the first runner action (SUT instance unavailability)', ['harness-precheck.json']);
  process.exit(0);
}
if (spec.scenario === 'MQ3' && !(precheck.seed && precheck.seed.verified)) {
  excluded('API_SEED', 'MQ3 API seed was not applied and verified by the harness before the first runner action', ['harness-precheck.json']);
  process.exit(0);
}
rec.harness = { backend_health_attempts: precheck.backend_health.attempts.length, backend_health_last_latency_ms: precheck.backend_health.attempts.at(-1).latency_ms, seed_verified: spec.scenario === 'MQ3' ? true : null };

// Phase 1..4 — runner-driven.
let device = null;
let failureCaptured = false;
async function captureFailure(screen) {
  if (failureCaptured) return;
  failureCaptured = true;
  try { writeFileSync(join(OUT, 'failure.png'), await screen.screenshot()); rec.artifacts.push('failure.png'); } catch (e) { rec.notes.push('failure screenshot unavailable: ' + errText(e).split('\n')[0]); }
  try { rec.artifacts.push(writeJson('view-tree-failure.json', await screen.viewTree())); } catch (e) { rec.notes.push('failure view tree unavailable: ' + errText(e).split('\n')[0]); }
  writeFileSync(join(OUT, 'device-log-failure.txt'), deviceLog(spec.platform, spec.device_id)); rec.artifacts.push('device-log-failure.txt');
  if (spec.scenario === 'MQ3' && token) { rec.harness.cart_after_failure = await readCart(token); }
}

try {
  device = await step('connect the runner to the pinned device (explicit id)', [], connect);
  const { screen } = device;
  const B = REALIZATION.bundle_id;

  // MC-09: reset app state by uninstall + reinstall of the pinned build, verified.
  const tReset = Date.now();
  await step('reset: uninstall any previous install (MC-09)', ['MC-09'], async () => {
    const apps = await device.listApps();
    if (apps.some((a) => a.bundleId === B)) {
      await device.uninstallApp(B);
      const after = await device.listApps();
      if (after.some((a) => a.bundleId === B)) throw new Error('app still listed after uninstall');
    } else {
      rec.notes.push('reset: app was not installed before this execution');
    }
  });
  await step('reset: install the pinned build (MC-09, MC-01)', ['MC-09', 'MC-01'], () => device.installApp(spec.build_path));
  await step('reset: verify the pinned build is installed (MC-09)', ['MC-09'], async () => {
    const apps = await device.listApps();
    if (!apps.some((a) => a.bundleId === B)) throw new Error('installed app not listed');
  });
  rec.duration_ms.reset = Date.now() - tReset;

  const loginToCatalog = async () => {
    await step('launch the app (MC-01)', ['MC-01'], () => device.launchApp(B));
    await step('login screen visible (MC-02, MC-06, MC-08)', ['MC-02', 'MC-06', 'MC-08'], () => expect(screen.getByTestId(REALIZATION.MQ1.login_screen)).toBeVisible({ timeout: T.screen }));
    await step('select market US (MC-02, MC-04)', ['MC-02', 'MC-04'], () => screen.getByTestId(REALIZATION.MQ1.market_control).tap());
    await step('enter username (MC-02, MC-03)', ['MC-02', 'MC-03'], () => screen.getByTestId(REALIZATION.MQ1.username).fill(ACCOUNT.username));
    await step('enter password (MC-02, MC-03)', ['MC-02', 'MC-03'], () => screen.getByTestId(REALIZATION.MQ1.password).fill(ACCOUNT.password));
    await step('tap Sign In (MC-02, MC-04)', ['MC-02', 'MC-04'], async () => {
      const b = screen.getByTestId(REALIZATION.MQ1.login_button);
      await b.scrollIntoViewIfNeeded({ maxSwipes: 5 });
      await b.tap();
    });
    await step('catalog screen visible (MC-06, MC-08)', ['MC-06', 'MC-08'], () => expect(screen.getByTestId(REALIZATION.MQ1.terminal[0])).toBeVisible({ timeout: T.screen }));
    await step('bottom navigation visible (MC-02, MC-08)', ['MC-02', 'MC-08'], () => expect(screen.getByTestId(REALIZATION.MQ1.terminal[1])).toBeVisible({ timeout: T.expect }));
  };

  if (spec.scenario === 'MQ1') {
    const tS = Date.now();
    await loginToCatalog();
    rec.duration_ms.scenario = Date.now() - tS;
  } else if (spec.scenario === 'MQ2') {
    const tP = Date.now();
    await loginToCatalog();                       // precondition: start state = catalog screen
    rec.duration_ms.precondition = Date.now() - tP;
    const tS = Date.now();
    const R = REALIZATION.MQ2;
    await step('catalog list loaded: first card visible (MC-02, MC-08)', ['MC-02', 'MC-08'], () => expect(screen.getByTestId(R.first_card)).toBeVisible({ timeout: T.screen }));
    await step('swipe up in the catalog (MC-05)', ['MC-05'], () => screen.swipe('up'));
    await step('scroll the target product control into view (MC-02, MC-05)', ['MC-02', 'MC-05'], () => screen.getByTestId(R.target_open_control).scrollIntoViewIfNeeded({ maxSwipes: 20 }));
    await step('open the target product (MC-02, MC-04)', ['MC-02', 'MC-04'], () => screen.getByTestId(R.target_open_control).tap());
    await step('product screen visible (MC-06, MC-08)', ['MC-06', 'MC-08'], () => expect(screen.getByTestId(R.product_screen)).toBeVisible({ timeout: T.screen }));
    await step(`initial estimated total is ${R.initial_total} (MC-02, MC-08)`, ['MC-02', 'MC-08'], () => expect(screen.getByTestId(R.total_text)).toHaveText(R.initial_total, { timeout: T.expect }));
    await step('tap the size control Large (MC-02, MC-04)', ['MC-02', 'MC-04'], () => screen.getByTestId(R.size_control).tap());
    await step(`estimated total changed to ${R.total_after} (MC-08)`, ['MC-08'], () => expect(screen.getByTestId(R.total_text)).toHaveText(R.total_after, { timeout: T.expect }));
    rec.duration_ms.scenario = Date.now() - tS;
  } else if (spec.scenario === 'MQ3') {
    const R = REALIZATION.MQ3;
    const params = new URLSearchParams({ ...R.deep_link_params, accessToken: token });
    const url = `${REALIZATION.scheme}://${R.deep_link_path}?${params.toString()}`;
    rec.harness.deep_link = redact(url);
    const tS = Date.now();
    await step('open the deep link from a cold state (MC-07)', ['MC-07'], () => device.openUrl(url));
    await step('checkout screen visible (MC-06, MC-08)', ['MC-06', 'MC-08'], () => expect(screen.getByTestId(R.checkout_screen)).toBeVisible({ timeout: T.screen }));
    await step(`seeded line "${R.expected_title}" visible (MC-08)`, ['MC-08'], () => expect(screen.getByText(R.expected_title)).toBeVisible({ timeout: T.expect }));
    await step(`seeded line total "${R.expected_line_total}" visible (MC-08)`, ['MC-08'], () => expect(screen.getByText(R.expected_line_total)).toBeVisible({ timeout: T.expect }));
    rec.duration_ms.scenario = Date.now() - tS;
  } else {
    throw new Error('unknown scenario ' + spec.scenario);
  }

  // MC-10: artifacts at the verified terminal state.
  await step('capture terminal screenshot and view tree (MC-10)', ['MC-10'], async () => {
    writeFileSync(join(OUT, 'terminal.png'), await screen.screenshot()); rec.artifacts.push('terminal.png');
    rec.artifacts.push(writeJson('view-tree-terminal.json', await screen.viewTree()));
  });
  finish('SUCCESS');
} catch (e) {
  rec.notes.push('failed: ' + errText(e).split('\n')[0]);
  if (device) await captureFailure(device.screen);
  finish('FAILURE');
} finally {
  if (device) { try { await device.close(); } catch (e) { rec.notes.push('close: ' + errText(e).split('\n')[0]); } }
  if (spec.scenario === 'MQ3' && token) {
    rec.harness.cleanup_session_reset = await resetSession(token);
    writeJson('record.json', rec);
  }
}
rec.artifacts.push('record.json', 'runner.log');
writeJson('record.json', rec);
process.exit(0);
