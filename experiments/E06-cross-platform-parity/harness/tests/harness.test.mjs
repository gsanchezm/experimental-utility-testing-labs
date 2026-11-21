// Tests of harness/e06-android.mjs against the fake WebDriver server of tests/fake_appium.mjs (DRAFT, operation OP-PREP-E06-EXECUTOR).
// No device, no emulator, no Appium: the server answers the W3C commands the flows use. Budgets run on a virtual clock.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runExecution, capabilitiesFor } from '../e06-android.mjs';
import { startFakeAppium } from './fake_appium.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const HARNESS = join(HERE, '..', 'e06-android.mjs');

// An asynchronous child process: the fake server lives in this process, so a synchronous spawn would block it.
function runNode(args, timeoutMs) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    let stderr = '';
    child.stderr.on('data', (d) => { stderr += d; });
    const timer = setTimeout(() => { child.kill(); resolve({ status: null, stderr: `timeout after ${timeoutMs} ms` }); }, timeoutMs);
    child.on('close', (code) => { clearTimeout(timer); resolve({ status: code, stderr }); });
  });
}

function virtualClock() {
  let t = 0;
  return () => (t += 1000);
}
const noSleep = async () => {};

function input(sut, url, overrides = {}) {
  const base = sut === 'SUT-01'
    ? { sut_id: 'SUT-01', app_package: 'com.omnipizza.app', username: 'standard_user', password: 'pizza123', launch: {} }
    : { sut_id: 'SUT-02', app_package: 'com.saucelabs.mydemoapp.android', username: 'standard_user', password: 'secret_sauce',
        launch: { appActivity: 'com.saucelabs.mydemoapp.android.view.activities.SplashActivity', appWaitActivity: 'com.saucelabs.mydemoapp.android.view.activities.MainActivity' } };
  return { ...base, index: 1, apk_path: '/fixture/app.apk', udid: 'emulator-5554', appium_url: url, budget_ms: 180000, ...overrides };
}

async function execute(sut, server, overrides) {
  return runExecution(input(sut, server.url, overrides), { sleep: noSleep, now: virtualClock() });
}

test('SUT-01: the quick login and the sign-in reach the catalogue and the card labels are read in document order', async () => {
  const server = await startFakeAppium({ sut: 'SUT-01', signIn: 'ok', cards: ['p07', 'p02'] });
  try {
    const record = await execute('SUT-01', server);
    assert.equal(record.fault, null);
    assert.equal(record.app_started, true);
    assert.equal(record.sign_in_submitted, true);
    assert.equal(record.arrived, true);
    assert.equal(record.arrival_detail, 'screen-catalog displayed');
    assert.deepEqual(record.card_labels, ['card-pizza-p07', 'card-pizza-p02']);
    assert.ok(record.page_source.includes('card-pizza-p07'));
    assert.ok(record.screenshot_png_base64);
    assert.ok(record.steps.every((s) => s.status === 'OK'), JSON.stringify(record.steps));
    assert.ok(server.requests.some((r) => r.method === 'DELETE'), 'the session is deleted');
  } finally {
    await server.close();
  }
});

test('SUT-01: a backend user limit shown on the login screen is recorded as the error text, not as an arrival', async () => {
  const server = await startFakeAppium({ sut: 'SUT-01', signIn: 'error', errorText: 'Too many users' });
  try {
    const record = await execute('SUT-01', server);
    assert.equal(record.arrived, false);
    assert.equal(record.error_text, 'Too many users');
    assert.equal(record.arrival_detail, 'text-login-error displayed');
    assert.equal(record.fault, null);
  } finally {
    await server.close();
  }
});

test('SUT-01: a sign-in that shows neither the catalogue nor an error is not an arrival (the budget is spent)', async () => {
  const server = await startFakeAppium({ sut: 'SUT-01', signIn: 'stay' });
  try {
    const record = await execute('SUT-01', server);
    assert.equal(record.arrived, false);
    assert.equal(record.error_text, null);
    assert.match(record.arrival_detail, /neither screen-catalog nor text-login-error/);
  } finally {
    await server.close();
  }
});

test('SUT-01: an account other than standard_user is refused before any tap, as a fault of the harness', async () => {
  const server = await startFakeAppium({ sut: 'SUT-01', signIn: 'ok' });
  try {
    const record = await execute('SUT-01', server, { username: 'locked_out_user' });
    assert.ok(record.fault, 'a fault is recorded');
    assert.match(record.fault.message, /realizes the account standard_user only/);
    assert.equal(record.sign_in_submitted, false);
    assert.equal(server.requests.some((r) => r.method === 'POST' && r.path.endsWith('/click')), false);
  } finally {
    await server.close();
  }
});

test('SUT-02: the menu, the Log In row, and the credentials reach the catalogue and the titles are read in document order', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02', signIn: 'ok', titles: ['Sauce Labs Backpack', 'Sauce Labs Bike Light'] });
  try {
    const record = await execute('SUT-02', server);
    assert.equal(record.fault, null, JSON.stringify(record.steps));
    assert.equal(record.arrived, true);
    assert.deepEqual(record.titles, ['Sauce Labs Backpack', 'Sauce Labs Bike Light']);
    const typed = server.requests.filter((r) => r.method === 'POST' && r.path.endsWith('/value')).map((r) => r.body.text);
    assert.deepEqual(typed, ['standard_user', 'secret_sauce']);
    assert.equal(record.error_text, null);
    assert.equal(record.authenticated_signal, true);
    assert.equal(record.session_not_established, false);
    assert.ok(record.steps.some((s) => s.name.includes('Logout Menu Item') && s.status === 'OK'), 'the second signal is a recorded step');
    assert.equal(record.arrival_detail, 'login screen gone, the catalogue landing screen displayed and the drawer row Logout Menu Item present');
  } finally {
    await server.close();
  }
});

test('SUT-02: the catalogue after the sign-in without the Logout Menu Item row is not an arrival (no authenticated session), and the titles are still kept', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02', signIn: 'ok', logout: 'absent' });
  try {
    const record = await execute('SUT-02', server);
    assert.equal(record.fault, null, JSON.stringify(record.steps));
    assert.equal(record.arrived, false);
    assert.equal(record.authenticated_signal, false);
    assert.equal(record.session_not_established, true);
    assert.deepEqual(record.titles, ['Sauce Labs Backpack', 'Sauce Labs Bike Light']);
    assert.match(record.arrival_detail, /Logout Menu Item is absent: no authenticated session/);
  } finally {
    await server.close();
  }
});

test('SUT-02: a session that is lost while the Logout Menu Item is searched is a fault of the record, never an absent row', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02', signIn: 'ok', logout: 'absent', sourceFailsWhenMenuOpen: true });
  try {
    const record = await execute('SUT-02', server);
    assert.ok(record.fault, 'a fault is recorded');
    assert.equal(record.arrived, false);
    assert.equal(record.session_not_established, false);
    assert.equal(record.authenticated_signal, null);
  } finally {
    await server.close();
  }
});

test('SUT-02: a validation error on the login screen is recorded as the error text', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02', signIn: 'error' });
  try {
    const record = await execute('SUT-02', server);
    assert.equal(record.arrived, false);
    assert.equal(record.error_text, 'Username is required');
    assert.equal(record.arrival_detail, 'a validation error is displayed on the login screen');
    assert.equal(record.authenticated_signal, null);
    assert.equal(record.steps.some((s) => s.name.includes('Logout Menu Item')), false, 'the second signal is read only when the catalogue is shown after the sign-in');
  } finally {
    await server.close();
  }
});

test('a session that cannot be created is a fault of the record, and no step runs after it', async () => {
  const server = await startFakeAppium({ sut: 'SUT-01', failSession: true });
  try {
    const record = await execute('SUT-01', server);
    assert.ok(record.fault);
    assert.equal(record.arrived, false);
    assert.equal(record.session_capabilities, null);
    assert.equal(record.app_started, false);
  } finally {
    await server.close();
  }
});

test('the password typed into the application never appears in the record the harness writes', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02', signIn: 'ok' });
  try {
    const record = await execute('SUT-02', server);
    assert.equal(JSON.stringify(record).includes('secret_sauce'), false);
  } finally {
    await server.close();
  }
});

test('the capabilities name the launch activities for SUT-02 only (the SUT-01 smoke realization sets none)', () => {
  const sut2 = capabilitiesFor(input('SUT-02', 'http://x'));
  assert.equal(sut2['appium:appActivity'], 'com.saucelabs.mydemoapp.android.view.activities.SplashActivity');
  assert.equal(sut2['appium:appWaitActivity'], 'com.saucelabs.mydemoapp.android.view.activities.MainActivity');
  const sut1 = capabilitiesFor(input('SUT-01', 'http://x'));
  assert.equal('appium:appActivity' in sut1, false);
  assert.equal(sut1['appium:automationName'], 'UiAutomator2');
  assert.equal(sut1['appium:app'], '/fixture/app.apk');
});

test('the entry point writes the record on success and refuses a missing argument with status 2', async () => {
  const server = await startFakeAppium({ sut: 'SUT-02', signIn: 'ok' });
  const dir = mkdtempSync(join(tmpdir(), 'e06-harness-'));
  try {
    const inputPath = join(dir, 'input.json');
    const outPath = join(dir, 'record.json');
    const { writeFileSync } = await import('node:fs');
    writeFileSync(inputPath, JSON.stringify(input('SUT-02', server.url)));
    const ok = await runNode([HARNESS, `--input=${inputPath}`, `--out=${outPath}`], 120000);
    assert.equal(ok.status, 0, ok.stderr);
    const record = JSON.parse(readFileSync(outPath, 'utf8'));
    assert.equal(record.record_class, 'E06_ANDROID_HARNESS_RECORD');
    assert.equal(record.arrived, true);
    const refused = await runNode([HARNESS], 30000);
    assert.equal(refused.status, 2);
  } finally {
    await server.close();
    rmSync(dir, { recursive: true, force: true });
  }
});
