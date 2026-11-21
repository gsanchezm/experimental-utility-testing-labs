// E06-cross-platform-parity Android harness: one execution of CS-007 on one Android condition (DRAFT, operation OP-PREP-E06-EXECUTOR).
//
// Called once per execution by executor/android.py (a Node.js process per execution). It opens one Appium session on the verified APK,
// performs the sign-in of the condition, reads the catalogue identity (the page source and the labels/texts of the catalogue are read here
// and parsed again by the Python side), and writes one JSON record to --out. The record is written on every outcome, including a fault;
// only a process that cannot write it at all leaves no record (the Python side then records a RUNNER fault).
//
// The selectors are taken from the pinned sources named beside them. None is verified against a device until a non-measured DRY_RUN has
// run (conditions-draft.json, open items 3 to 9).

import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { createClient, waitFor, WebDriverError } from './wd.mjs';

const SCREEN_BUDGET_MS = 90000;
const SIGN_IN_BUDGET_MS = 60000;
const IDENTITY_BUDGET_MS = 60000;
const POLL_MS = 1000;
const SESSION_TIMEOUT_MS = 600000;
const SUT02_PACKAGE_ID = 'com.saucelabs.mydemoapp.android:id/';

// SUT-01 (OmniPizza release v1.1.8, commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a). Accessibility ids as in the SUT-01 smoke
// realization (qualification/compatibility-smoke-sut01/README.md): screen-login (LoginScreen.tsx line 112), Standard (lines 29, 219 to 225;
// qa.ts lines 58 to 72), Sign In (PrimaryButton of btn-login, LoginScreen.tsx line 206), screen-catalog (CatalogScreen.tsx line 52),
// text-login-error (LoginScreen.tsx line 198). The card labels: PizzaCard.tsx line 23 (card-pizza-<id>).
const SUT01 = {
  login_screen: { using: 'accessibility id', value: 'screen-login' },
  quick_login: { using: 'accessibility id', value: 'Standard' },
  sign_in: { using: 'accessibility id', value: 'Sign In' },
  catalogue: { using: 'accessibility id', value: 'screen-catalog' },
  // The error text node carries the testID text-login-error and the message as its accessibility label. On Android the testID may map to a
  // resource id instead (qa.ts comment; not verified on a device), so this locator matches the resource id; a DRY_RUN decides it.
  login_error: { using: '-android uiautomator', value: 'new UiSelector().resourceIdMatches(".*text-login-error.*")' },
  card_labels: { using: '-android uiautomator', value: 'new UiSelector().descriptionStartsWith("card-pizza-")' },
};

// SUT-02 (my-demo-app-android release 2.2.0, commit 36b012eecdf6a2b488b9504e16b3d0c3ca9a0e7b). Resource ids as in the SUT-02 smoke
// (qualification/compatibility-smoke/harness/smoke.mjs, productRV) and of the pinned layouts: menuIV (menu_header_layout.xml line 15),
// the drawer row with the content description Login Menu Item (MainActivity.java line 259; MenuAdapter.java lines 55 to 59), nameET,
// passwordET, loginBtn (fragment_login.xml lines 68, 129, 190), nameErrorTV and passwordErrorTV (fragment_login.xml lines 92, 153), and
// titleTV (item_products.xml; the static reading of experiments/E06-cross-platform-parity/static-reading-oracle-draft.md).
const SUT02 = {
  landing: { using: 'id', value: `${SUT02_PACKAGE_ID}productRV` },
  menu_icon: { using: 'id', value: `${SUT02_PACKAGE_ID}menuIV` },
  login_row: { using: 'accessibility id', value: 'Login Menu Item' },
  login_row_scroll: { using: '-android uiautomator', value: 'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().description("Login Menu Item"))' },
  name_field: { using: 'id', value: `${SUT02_PACKAGE_ID}nameET` },
  password_field: { using: 'id', value: `${SUT02_PACKAGE_ID}passwordET` },
  login_button: { using: 'id', value: `${SUT02_PACKAGE_ID}loginBtn` },
  name_error: { using: 'id', value: `${SUT02_PACKAGE_ID}nameErrorTV` },
  password_error: { using: 'id', value: `${SUT02_PACKAGE_ID}passwordErrorTV` },
  titles: { using: 'id', value: `${SUT02_PACKAGE_ID}titleTV` },
  // The second signal of the authenticated state (decision D-E06-13): the drawer row Logout Menu Item (MainActivity.java, MenuAdapter.java), which the
  // application shows only once a session exists; read by the same accessibility-id route as the Login Menu Item row, with the same scroll fallback.
  logout_row: { using: 'accessibility id', value: 'Logout Menu Item' },
  logout_row_scroll: { using: '-android uiautomator', value: 'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().description("Logout Menu Item"))' },
};

export function capabilitiesFor(input) {
  const caps = {
    platformName: 'Android',
    'appium:automationName': 'UiAutomator2',
    'appium:appPackage': input.app_package,
    'appium:app': input.apk_path,
    'appium:udid': input.udid,
    'appium:autoGrantPermissions': true,
    'appium:disableWindowAnimation': true,
    'appium:androidInstallTimeout': 300000,
    'appium:uiautomator2ServerInstallTimeout': 120000,
    'appium:uiautomator2ServerLaunchTimeout': 120000,
    'appium:adbExecTimeout': 120000,
    'appium:newCommandTimeout': 300,
  };
  if (input.sut_id === 'SUT-02') {
    caps['appium:appActivity'] = input.launch.appActivity;
    caps['appium:appWaitActivity'] = input.launch.appWaitActivity;
  }
  return caps;
}

async function isDisplayed(client, locator) {
  try {
    const id = await client.findElement(locator.using, locator.value);
    return (await client.displayed(id)) === true;
  } catch (e) {
    if (e instanceof WebDriverError && e.kind === 'response') return false;
    if (e instanceof WebDriverError && e.kind === 'not_reached') return false;
    throw e;
  }
}

async function present(client, locator) {
  try {
    await client.findElement(locator.using, locator.value);
    return true;
  } catch (e) {
    if (e instanceof WebDriverError && e.kind === 'response') return false;
    throw e;
  }
}

async function textOf(client, locator) {
  try {
    const id = await client.findElement(locator.using, locator.value);
    const label = await client.attribute(id, 'content-desc');
    if (label) return String(label);
    return String(await client.text(id) || '') || null;
  } catch (e) {
    if (e instanceof WebDriverError) return null;
    throw e;
  }
}

async function pollUntil(predicate, budgetMs, sleep, now) {
  const deadline = now() + budgetMs;
  for (;;) {
    const value = await predicate();
    if (value) return value;
    if (now() >= deadline) return value;
    await sleep(POLL_MS);
  }
}

function emptyRecord(input) {
  return {
    record_class: 'E06_ANDROID_HARNESS_RECORD',
    sut_id: input.sut_id,
    index: input.index,
    app_started: false,
    sign_in_submitted: false,
    arrived: false,
    arrival_detail: null,
    authenticated_signal: null,
    session_not_established: false,
    error_text: null,
    card_labels: [],
    titles: [],
    page_source: null,
    screenshot_png_base64: null,
    steps: [],
    fault: null,
    observed_versions: { node: process.version, appium: null, uiautomator2: null },
    session_capabilities: null,
    budget_ms: input.budget_ms ?? null,
  };
}

// The sign-in and the identity read of one execution. The client and the clock are injected so the tests drive it with a fake server.
export async function runExecution(input, { createClientFn = createClient, sleep = (ms) => new Promise((r) => setTimeout(r, ms)), now = () => Date.now() } = {}) {
  const record = emptyRecord(input);
  const client = createClientFn(input.appium_url);
  const step = async (name, fn) => {
    const entry = { name, status: 'OK', error: null };
    record.steps.push(entry);
    try {
      return await fn();
    } catch (e) {
      entry.status = 'FAILED';
      entry.error = String(e && e.message ? e.message : e).split('\n')[0];
      throw e;
    }
  };
  try {
    const caps = await step('create the Appium session on the verified APK (clean install)', () => client.newSession(capabilitiesFor(input), SESSION_TIMEOUT_MS));
    record.session_capabilities = Object.fromEntries(Object.entries(caps || {}).filter(([k]) => /platform|automation|package|activity|udid|deviceApiLevel|platformVersion/i.test(k)));
    if (input.sut_id === 'SUT-01') {
      await runSut01(client, input, record, sleep, now);
    } else if (input.sut_id === 'SUT-02') {
      await runSut02(client, input, record, sleep, now);
    } else {
      throw new Error(`no harness flow for ${input.sut_id}`);
    }
  } catch (e) {
    record.fault = { class: e && e.name ? e.name : 'Error', message: String(e && e.message ? e.message : e).split('\n')[0] };
  } finally {
    try {
      if (client.sessionId) {
        record.page_source = record.page_source ?? await client.source().catch(() => null);
        const png = await client.screenshot().catch(() => null);
        record.screenshot_png_base64 = png ? String(png) : null;
      }
    } catch (e) {
      record.steps.push({ name: 'capture the terminal artifacts', status: 'FAILED', error: String(e.message || e).split('\n')[0] });
    }
    try {
      await client.deleteSession();
    } catch (e) {
      record.steps.push({ name: 'delete the session', status: 'FAILED', error: String(e.message || e).split('\n')[0] });
    }
  }
  return record;
}

async function runSut01(client, input, record, sleep, now) {
  // The quick-login control Standard fills standard_user and its password (LoginScreen.tsx lines 29 and 106 to 109): this flow realizes
  // that account only, so any other account is refused here instead of being signed in as standard_user.
  if (input.username !== 'standard_user') {
    throw new Error('the SUT-01 quick login realizes the account standard_user only');
  }
  await step(record, 'screen-login displayed', () => waitFor(client, { sleep, now,  ...SUT01.login_screen, timeoutMs: SCREEN_BUDGET_MS, until: (id) => client.displayed(id) }));
  record.app_started = true;
  await step(record, 'quick login Standard', async () => {
    const id = await waitFor(client, { sleep, now,  ...SUT01.quick_login, timeoutMs: 30000 });
    await client.click(id);
  });
  await step(record, 'sign-in Sign In', async () => {
    const id = await waitFor(client, { sleep, now,  ...SUT01.sign_in, timeoutMs: 30000 });
    await client.click(id);
    record.sign_in_submitted = true;
  });
  const state = await step(record, 'screen-catalog or text-login-error within the sign-in budget', () => pollUntil(async () => {
    if (await isDisplayed(client, SUT01.catalogue)) return 'CATALOGUE';
    if (await isDisplayed(client, SUT01.login_error)) return 'ERROR';
    return null;
  }, SIGN_IN_BUDGET_MS, sleep, now));
  if (state === 'ERROR') {
    record.error_text = await textOf(client, SUT01.login_error);
  }
  record.arrived = state === 'CATALOGUE';
  record.arrival_detail = record.arrived ? 'screen-catalog displayed' : (state === 'ERROR' ? 'text-login-error displayed' : 'neither screen-catalog nor text-login-error within the sign-in budget');
  if (record.arrived) {
    const labels = await step(record, 'read the card labels of the catalogue', () => pollUntil(async () => {
      const ids = await client.findElements(SUT01.card_labels.using, SUT01.card_labels.value);
      if (!ids.length) return null;
      const out = [];
      for (const id of ids) {
        const label = await client.attribute(id, 'content-desc');
        if (label) out.push(String(label));
      }
      return out;
    }, IDENTITY_BUDGET_MS, sleep, now));
    record.card_labels = labels || [];
    record.page_source = await client.source();
  }
}

async function runSut02(client, input, record, sleep, now) {
  const { username, password } = input;
  await step(record, 'catalogue landing screen (productRV) displayed before any sign-in', () => waitFor(client, { sleep, now,  ...SUT02.landing, timeoutMs: SCREEN_BUDGET_MS, until: (id) => client.displayed(id) }));
  record.app_started = true;
  await step(record, 'open the menu (menuIV)', async () => {
    const id = await waitFor(client, { sleep, now,  ...SUT02.menu_icon, timeoutMs: 30000 });
    await client.click(id);
  });
  await step(record, 'open the drawer row Log In (accessibility id Login Menu Item)', async () => {
    let id;
    try {
      id = await waitFor(client, { sleep, now,  ...SUT02.login_row, timeoutMs: 10000 });
    } catch (e) {
      if (!(e instanceof WebDriverError)) throw e;
      id = await waitFor(client, { sleep, now,  ...SUT02.login_row_scroll, timeoutMs: 30000 });
    }
    await client.click(id);
  });
  await step(record, 'login screen (nameET) displayed', () => waitFor(client, { sleep, now,  ...SUT02.name_field, timeoutMs: 30000, until: (id) => client.displayed(id) }));
  await step(record, 'enter the username and the password', async () => {
    const nameId = await client.findElement(SUT02.name_field.using, SUT02.name_field.value);
    await client.click(nameId);
    await client.sendKeys(nameId, username);
    const passId = await client.findElement(SUT02.password_field.using, SUT02.password_field.value);
    await client.click(passId);
    await client.sendKeys(passId, password);
  });
  await step(record, 'tap Log In (loginBtn)', async () => {
    const id = await client.findElement(SUT02.login_button.using, SUT02.login_button.value);
    await client.click(id);
    record.sign_in_submitted = true;
  });
  const state = await step(record, 'landing displayed with the login screen gone, or a validation error, within the sign-in budget', () => pollUntil(async () => {
    if (!(await present(client, SUT02.name_field)) && (await isDisplayed(client, SUT02.landing))) return 'CATALOGUE';
    if ((await isDisplayed(client, SUT02.name_error)) || (await isDisplayed(client, SUT02.password_error))) return 'ERROR';
    return null;
  }, SIGN_IN_BUDGET_MS, sleep, now));
  if (state === 'ERROR') {
    record.error_text = (await textOf(client, SUT02.name_error)) || (await textOf(client, SUT02.password_error));
  }
  // Arrival on SUT-02 Android needs two signals (decision D-E06-13): the login screen gone with the catalogue landing displayed (the catalogue is
  // displayed before any sign-in, so this alone does not show a session) and the drawer row Logout Menu Item, read after the titles. The record
  // keeps arrived false until the second signal holds, so a fault of the second step is a harness fault of an execution that did not arrive.
  record.arrived = false;
  record.arrival_detail = state === 'CATALOGUE' ? 'login screen gone and the catalogue landing screen displayed' : (state === 'ERROR' ? 'a validation error is displayed on the login screen' : 'the login screen did not give way to the catalogue within the sign-in budget');
  if (state === 'CATALOGUE') {
    const titles = await step(record, 'read the titles of the catalogue in document order', () => pollUntil(async () => {
      const ids = await client.findElements(SUT02.titles.using, SUT02.titles.value);
      if (!ids.length) return null;
      const out = [];
      for (const id of ids) out.push(String((await client.text(id)) || ''));
      return out;
    }, IDENTITY_BUDGET_MS, sleep, now));
    record.titles = titles || [];
    record.page_source = await client.source();
    const signal = await step(record, 'open the menu and read the drawer row Logout Menu Item (second signal of the authenticated state)', async () => {
      const menu = await waitFor(client, { sleep, now, ...SUT02.menu_icon, timeoutMs: 30000 });
      await client.click(menu);
      for (const locator of [SUT02.logout_row, SUT02.logout_row_scroll]) {
        try {
          await waitFor(client, { sleep, now, ...locator, timeoutMs: locator === SUT02.logout_row ? 10000 : 30000 });
          return true;
        } catch (e) {
          if (!(e instanceof WebDriverError && e.kind === 'not_reached')) throw e;
        }
      }
      // absent: a session that is gone (a transport or protocol fault) must not read as an absent row
      await client.source();
      return false;
    });
    record.authenticated_signal = signal === true;
    record.arrived = record.authenticated_signal;
    if (!record.authenticated_signal) {
      record.session_not_established = true;
      record.arrival_detail = 'the catalogue landing screen is displayed after the sign-in but the drawer row Logout Menu Item is absent: no authenticated session';
    } else {
      record.arrival_detail = 'login screen gone, the catalogue landing screen displayed and the drawer row Logout Menu Item present';
    }
  }
}

// step() helper for the SUT-specific functions: they record into the same steps list.
function step(record, name, fn) {
  const entry = { name, status: 'OK', error: null };
  record.steps.push(entry);
  return Promise.resolve().then(fn).catch((e) => {
    entry.status = 'FAILED';
    entry.error = String(e && e.message ? e.message : e).split('\n')[0];
    throw e;
  });
}

async function main() {
  const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split(/=(.*)/s).slice(0, 2)));
  if (!args.input || !args.out) {
    console.error('e06-android: usage: node e06-android.mjs --input=<json> --out=<json>');
    process.exit(2);
  }
  const input = JSON.parse(readFileSync(args.input, 'utf8'));
  const record = await runExecution(input);
  writeFileSync(args.out, JSON.stringify(record));
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((e) => {
    console.error(`e06-android: harness error: ${String(e && e.message ? e.message : e).split('\n')[0]}`);
    process.exit(2);
  });
}
