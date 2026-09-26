// Appium 3 per-SUT compatibility smoke (protocol/mobile-runner-policy-v2.md, section 9) for SUT-02 (Sauce Labs
// Demo Ecosystem), one clean execution per platform. REALIZATION below is the executable form of the
// "Concrete realization" section of qualification/compatibility-smoke/README.md, recorded before any execution;
// both are locked by manifests/compatibility-smoke-implementation-lock-v2.yaml. Tool qualification only: nothing
// recorded here is evidence about any system under test. The harness records what happened and proposes a
// result with its attribution; QUALIFIER-MOBILE-01 records the result. Proposals (policy v2, 9.1-9.4): PASS when
// every step completed; after the first runner action (the session request) every failure is proposed as
// FAIL_RUNNER, labeled with what the runner did (see attributeFailure), because NOT_EXECUTED needs a cause
// outside the runner that only the inspection of the preserved artifacts can demonstrate; a harness exception
// before any runner action is proposed as NOT_EXECUTED / HARNESS_ORCHESTRATION. Nothing is retried or repeated.
// Duration is recorded as information only and is no criterion.

import { createHash } from 'node:crypto';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { createClient, waitFor, WebDriverError } from './wd.mjs';

const POLICY = 'protocol/mobile-runner-policy-v2.md, section 9';
const RECORDING_ROLE = 'proposal by the harness; QUALIFIER-MOBILE-01 records the result (policy v2, section 9: NOT_EXECUTED only on a positively demonstrated cause outside the runner; uncertain attribution is FAIL_RUNNER)';

export const REALIZATION = {
  android: {
    sut_id: 'SUT-02',
    component: 'SUT-02-android',
    environment_type: 'EMULATED',
    app_identity: 'com.saucelabs.mydemoapp.android (versionName 2.2.0, versionCode 25)',
    capabilities: {
      platformName: 'Android',
      'appium:automationName': 'UiAutomator2',
      'appium:appPackage': 'com.saucelabs.mydemoapp.android',
      'appium:appActivity': 'com.saucelabs.mydemoapp.android.view.activities.SplashActivity',
      'appium:appWaitActivity': 'com.saucelabs.mydemoapp.android.view.activities.MainActivity',
      'appium:appWaitDuration': 60000,
      'appium:autoGrantPermissions': true,
      'appium:disableWindowAnimation': true,
      'appium:androidInstallTimeout': 300000,
      'appium:uiautomator2ServerInstallTimeout': 120000,
      'appium:uiautomator2ServerLaunchTimeout': 120000,
      'appium:adbExecTimeout': 120000,
      'appium:newCommandTimeout': 300,
    },
    session_timeout_ms: 600000,
    screen_timeout_ms: 90000,
    assertion_timeout_ms: 30000,
    steps: {
      mc02: { using: 'id', value: 'com.saucelabs.mydemoapp.android:id/productRV' },
      navigate: { using: '-android uiautomator', value: 'new UiSelector().resourceId("com.saucelabs.mydemoapp.android:id/titleTV").text("Sauce Labs Backpack")' },
      arrival: [
        { using: 'id', value: 'com.saucelabs.mydemoapp.android:id/productTV', text: 'Sauce Labs Backpack' },
        { using: 'id', value: 'com.saucelabs.mydemoapp.android:id/plusIV' },
      ],
      state: { using: 'id', value: 'com.saucelabs.mydemoapp.android:id/noTV', before: '1', after: '2', read: 'text' },
      control: { using: 'id', value: 'com.saucelabs.mydemoapp.android:id/plusIV' },
    },
    expected_final_state: 'product detail of "Sauce Labs Backpack" (productTV text) with quantity noTV text "2"',
  },
  ios: {
    sut_id: 'SUT-02',
    component: 'SUT-02-ios',
    environment_type: 'SIMULATED',
    app_identity: 'com.saucelabs.mydemo.app.ios (CFBundleShortVersionString 2.2.2, CFBundleVersion 1)',
    capabilities: {
      platformName: 'iOS',
      'appium:automationName': 'XCUITest',
      'appium:platformVersion': '18.5',
      'appium:deviceName': 'iPhone 16',
      'appium:bundleId': 'com.saucelabs.mydemo.app.ios',
      'appium:enforceAppInstall': true,
      'appium:simulatorStartupTimeout': 600000,
      'appium:wdaLaunchTimeout': 600000,
      'appium:wdaConnectionTimeout': 600000,
      'appium:showXcodeLog': true,
      'appium:newCommandTimeout': 300,
    },
    session_timeout_ms: 1200000,
    screen_timeout_ms: 90000,
    assertion_timeout_ms: 30000,
    steps: {
      mc02: { using: 'accessibility id', value: 'Catalog-screen' },
      navigate: { using: '-ios predicate string', value: 'type == "XCUIElementTypeStaticText" AND name == "Product Name"' },
      arrival: [
        { using: 'accessibility id', value: 'ProductDetails-screen' },
        { using: '-ios predicate string', value: 'type == "XCUIElementTypeStaticText" AND label == "Sauce Labs Backpack - Black"', within: 'ProductDetails-screen' },
      ],
      state: { using: '-ios predicate string', within: 'ProductDetails-screen', before: '1', after: '2', read: 'label',
               valueFor: (v) => `type == "XCUIElementTypeStaticText" AND label == "${v}"` },
      control: { using: 'accessibility id', value: 'AddPlus Icons' },
    },
    expected_final_state: 'ProductDetails-screen of "Sauce Labs Backpack - Black" with the quantity label reading "2"',
  },
};

export function realizationSha256() {
  const plain = JSON.parse(JSON.stringify(REALIZATION, (k, v) => (typeof v === 'function' ? v.toString() : v)));
  return createHash('sha256').update(JSON.stringify(plain)).digest('hex');
}

const iso = (d = new Date()) => d.toISOString();

const excerpt = (e) => ({
  class: (e && e.name) || typeof e,
  message: String(e && e.message !== undefined ? e.message : e).split('\n')[0],
  stack: String((e && e.stack) || '').split('\n').slice(0, 20),
});

// Attribution proposal for a failure after the first runner action (policy v2, 9.2-9.4). Always FAIL_RUNNER: the
// basis records what the runner did; a harness exception is attached as candidate HARNESS_ORCHESTRATION evidence
// for QUALIFIER-MOBILE-01, who may record NOT_EXECUTED only if the preserved artifacts positively demonstrate it.
export function attributeFailure(cause) {
  if (cause instanceof WebDriverError) {
    const basis = {
      response: 'RUNNER_ANSWERED_WITH_AN_ERROR',
      protocol: 'RUNNER_ANSWER_WITHOUT_REQUIRED_REFERENCE',
      not_reached: 'REQUIRED_ELEMENT_OR_STATE_NOT_REACHED',
      transport: 'NO_RUNNER_ANSWER_ATTRIBUTION_UNCERTAIN',
    }[cause.kind] || 'UNCLASSIFIED_ATTRIBUTION_UNCERTAIN';
    return { proposed_result: 'FAIL_RUNNER', proposed_category: 'SELECTED_RUNNER_STACK', basis, failure_kind: cause.kind || null, harness_exception: null };
  }
  return {
    proposed_result: 'FAIL_RUNNER',
    proposed_category: 'SELECTED_RUNNER_STACK',
    basis: 'HARNESS_EXCEPTION_AFTER_RUNNER_ACTION_ATTRIBUTION_UNCERTAIN',
    failure_kind: 'harness_exception',
    harness_exception: { ...excerpt(cause), candidate_category: 'HARNESS_ORCHESTRATION',
      note: 'candidate evidence for QUALIFIER-MOBILE-01; NOT_EXECUTED only if the preserved artifacts positively demonstrate the harness defect (policy v2, 9.3-9.4)' },
  };
}

// Record for a harness failure before any runner action (argument, context, or realization lookup): the runner was
// never contacted, so the proposal is NOT_EXECUTED with cause HARNESS_ORCHESTRATION (policy v2, 9.3).
export function preRunnerHarnessRecord({ platform = null, error, context = {} }) {
  return {
    record_class: 'COMPATIBILITY_SMOKE',
    study_id: 'EUS-2026-001',
    policy: POLICY,
    instruction_id: context.instruction_id || null,
    prompt_version_id: context.prompt_version_id || null,
    sut_id: 'SUT-02',
    platform,
    outcome: 'NOT_RUN',
    proposed_result: 'NOT_EXECUTED',
    attribution: {
      proposed_category: 'HARNESS_ORCHESTRATION',
      basis: 'HARNESS_EXCEPTION_BEFORE_ANY_RUNNER_ACTION',
      failure_kind: 'harness_exception',
      failed_phase: 'HARNESS_STARTUP',
      failed_capabilities: [],
      description: excerpt(error).message,
      runner_action_started: false,
      harness_exception: excerpt(error),
      evidence: ['record.json', 'harness.log'],
    },
    recording_role: RECORDING_ROLE,
    automatic_repeat: 'none (policy v2, 9.5)',
    steps: [],
    capabilities_exercised: [],
    at: iso(),
  };
}

export async function runSmoke({ platform, client, appPath, udid, outDir, context = {}, io = defaultIo(), clock = Date }) {
  const R = REALIZATION[platform];
  if (!R) throw new Error(`unknown platform ${platform}`);
  const started = clock.now();
  const steps = [];
  const artifacts = [];
  let failed = null;
  let cause = null;
  let runnerActionStarted = false;
  const capsUsed = { ...R.capabilities, 'appium:app': appPath, 'appium:udid': udid };

  async function step(name, capabilities, fn) {
    const s = { name, capabilities, started_at: iso(new Date(clock.now())), status: 'OK', detail: null };
    steps.push(s);
    io.log(`step: ${name}`);
    try {
      const detail = await fn();
      if (detail !== undefined) s.detail = detail;
    } catch (e) {
      s.status = 'FAILED';
      s.error = String(e && e.message ? e.message : e).split('\n')[0];
      throw Object.assign(new Error(s.error), { step: s, cause: e });
    } finally {
      s.ended_at = iso(new Date(clock.now()));
    }
  }
  // Runner-side capture (a WebDriverError) and the harness's own file write (any other error) are kept apart.
  async function capture(label) {
    const errors = {};
    for (const [kind, fn, file, enc] of [['screenshot', () => client.screenshot(), `${label}.png`, 'base64'], ['page source', () => client.source(), `source-${label}.xml`, 'utf8']]) {
      let data;
      try {
        data = await fn();
      } catch (e) {
        errors[kind] = e;
        io.log(`could not capture ${kind} (${label}): ${e.message}`);
        continue;
      }
      try {
        io.write(join(outDir, file), enc === 'base64' ? Buffer.from(String(data), 'base64') : String(data));
        artifacts.push(file);
      } catch (e) {
        errors[kind] = e;
        io.log(`could not write ${kind} (${label}): ${e.message}`);
      }
    }
    return errors;
  }
  const T = R.steps;
  const within = async (spec) => (spec.within ? client.findElement('accessibility id', spec.within) : null);

  try {
    await step('install and launch the pinned build (MC-01)', ['MC-01'], async () => {
      runnerActionStarted = true;
      const caps = await client.newSession(capsUsed, R.session_timeout_ms);
      return { session_capabilities: pick(caps, ['platformName', 'appium:automationName', 'appium:platformVersion', 'appium:deviceName', 'appium:udid']) };
    });
    await step(`locate "${T.mc02.value}" by stable identifier (MC-02, MC-08)`, ['MC-02', 'MC-08'], async () => {
      await waitFor(client, { using: T.mc02.using, value: T.mc02.value, timeoutMs: R.screen_timeout_ms, until: async (id) => (await client.displayed(id)) === true });
    });
    await step('open the product from the catalog (MC-04, MC-06)', ['MC-04', 'MC-06'], async () => {
      const id = await waitFor(client, { using: T.navigate.using, value: T.navigate.value, timeoutMs: R.assertion_timeout_ms });
      await client.click(id);
    });
    await step('product detail screen reached (MC-06, MC-08)', ['MC-06', 'MC-08'], async () => {
      for (const a of T.arrival) {
        const from = await within(a);
        await waitFor(client, {
          using: a.using, value: a.value, from, timeoutMs: a.within ? R.assertion_timeout_ms : R.screen_timeout_ms,
          until: a.text ? async (id) => (await client.text(id)) === a.text : null,
        });
      }
    });
    const readState = async (expected) => {
      const spec = T.state;
      const value = spec.valueFor ? spec.valueFor(expected) : spec.value;
      const from = await within(spec);
      let observed = null;
      await waitFor(client, {
        using: spec.using, value, from, timeoutMs: R.assertion_timeout_ms,
        until: async (id) => {
          observed = spec.read === 'text' ? await client.text(id) : await client.attribute(id, spec.read);
          return observed === expected;
        },
      });
      return { read: spec.read, observed };
    };
    await step(`quantity reads "${T.state.before}" before the interaction (MC-08)`, ['MC-08'], () => readState(T.state.before));
    await step(`tap the native control "${T.control.value}" (MC-04)`, ['MC-04'], async () => {
      const id = await waitFor(client, { using: T.control.using, value: T.control.value, timeoutMs: R.assertion_timeout_ms });
      await client.click(id);
    });
    await step(`quantity reads "${T.state.after}" after the interaction (MC-08)`, ['MC-08'], () => readState(T.state.after));
    await step('capture the terminal artifacts (MC-10)', ['MC-10'], async () => {
      const errors = await capture('terminal');
      if (!artifacts.includes('terminal.png')) throw errors.screenshot || new WebDriverError('terminal screenshot not captured', { kind: 'not_reached' });
    });
  } catch (e) {
    failed = e.step || { name: 'harness', capabilities: [], error: String(e.message || e) };
    cause = e.step ? e.cause : e;
    if (client.sessionId) await capture('failure');
  } finally {
    try { await client.deleteSession(); } catch (e) { io.log(`session deletion failed: ${e.message}`); }
  }
  const ended = clock.now();
  const exercised = [...new Set(steps.filter((s) => s.status === 'OK').flatMap((s) => s.capabilities))].sort();
  const attribution = failed ? {
    ...attributeFailure(cause),
    failed_phase: failed.name,
    failed_capabilities: failed.capabilities,
    description: failed.error,
    runner_action_started: runnerActionStarted,
    evidence: [...artifacts, 'record.json', 'harness.log', 'appium-server.log', 'environment/'],
  } : null;
  const record = {
    record_class: 'COMPATIBILITY_SMOKE',
    study_id: 'EUS-2026-001',
    policy: POLICY,
    instruction_id: context.instruction_id || null,
    prompt_version_id: context.prompt_version_id || null,
    sut_id: R.sut_id,
    component: R.component,
    platform,
    environment_type: R.environment_type,
    app_identity: R.app_identity,
    build: context.build || null,
    runner: context.runner || { name: 'Appium', core_pin: '3.7.0' },
    device: context.device || null,
    realization_sha256: realizationSha256(),
    capabilities_requested: capsUsed,
    steps,
    capabilities_exercised: exercised,
    expected_final_state: R.expected_final_state,
    outcome: failed ? 'FAILURE' : 'SUCCESS',
    failed_step: failed ? { name: failed.name, capabilities: failed.capabilities, error: failed.error } : null,
    proposed_result: failed ? attribution.proposed_result : 'PASS',
    attribution: attribution ? { ...attribution, proposed_result: undefined } : null,
    recording_role: RECORDING_ROLE,
    automatic_repeat: 'none (policy v2, 9.5)',
    started_at: iso(new Date(started)),
    ended_at: iso(new Date(ended)),
    duration_ms: ended - started,
    duration_note: 'information only; not a criterion (policy section 9)',
    artifacts,
    github: context.github || null,
  };
  try {
    io.write(join(outDir, 'record.json'), JSON.stringify(record, null, 2) + '\n');
  } catch (e) {
    throw Object.assign(e, { runnerActionStarted });
  }
  return record;
}

function pick(obj, keys) {
  const out = {};
  for (const k of keys) if (obj && obj[k] !== undefined) out[k] = obj[k];
  return out;
}

function defaultIo() {
  return {
    write: (path, data) => { mkdirSync(join(path, '..'), { recursive: true }); writeFileSync(path, data); },
    log: (msg) => console.log(`[smoke ${iso()}] ${msg}`),
  };
}

// CLI: node smoke.mjs --platform=android|ios --server=URL --app=PATH --udid=ID --out=DIR --context=JSONFILE
// Exit code: 0 only for outcome SUCCESS; 1 for any recorded failure or pre-runner stop; 2 when no record was written.
async function main() {
  const args = Object.fromEntries(process.argv.slice(2).map((a) => a.replace(/^--/, '').split(/=(.*)/s).slice(0, 2)));
  let context = {};
  let record;
  try {
    for (const k of ['platform', 'server', 'app', 'udid', 'out']) if (!args[k]) throw new Error(`missing --${k}`);
    const { readFileSync } = await import('node:fs');
    context = args.context ? JSON.parse(readFileSync(args.context, 'utf8')) : {};
    const client = createClient(args.server);
    record = await runSmoke({ platform: args.platform, client, appPath: args.app, udid: args.udid, outDir: args.out, context });
  } catch (e) {
    if (e && e.runnerActionStarted || !args.out) throw e;
    record = preRunnerHarnessRecord({ platform: args.platform || null, error: e, context });
    defaultIo().write(join(args.out, 'record.json'), JSON.stringify(record, null, 2) + '\n');
  }
  console.log(`[smoke] outcome=${record.outcome} proposed_result=${record.proposed_result}${record.failed_step ? ` failed_step="${record.failed_step.name}"` : ''}`);
  process.exitCode = record.outcome === 'SUCCESS' ? 0 : 1;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((e) => { console.error(`[smoke] harness error: ${e.message}`); process.exit(2); });
}
