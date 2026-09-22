# Mobilewright Qualification

## Status

AUTHORIZED — PRE-RUN PREPARATION RECORDED; no gate execution has occurred yet.

Owner: QUALIFIER-MOBILE-01 (protocol/agent-governance-v2.md, section 3.4, unchanged from v1), acting under frozen prompt version `qualifier-mobile-01-mobilewright-gate-v1` (prompts/frozen/qualifier-mobile-01-mobilewright-gate-v1.md). Governing policy: protocol/mobile-runner-policy-v1.md (FROZEN-PRE-DATA). Frozen inputs: manifests/mobile-qualification-package-v1.yaml; pins in manifests/toolchain-manifest.yaml. Nothing recorded here is evidence about any system under test (SUT); every record produced under this directory carries `record_class: QUALIFICATION` (or `DEVELOPMENT` for the harness development runs of the section "Development runs", which are not gate executions). No result, attribution, or decision field below is filled before a run has actually occurred.

## Gate definition

Mobilewright must pass this gate before use in any experimental campaign for the Android Native or iOS Native modalities. The gate consists of the scenarios defined in protocol/mobile-runner-policy-v1.md, Section 4, each exercised on both platforms of Section 6:

| ID | Scenario | Purpose |
|---|---|---|
| MQ1 | Login → Catalog | Navigation and selector compatibility |
| MQ2 | Catalog → Product Interaction | Native control interaction |
| MQ3 | API State Seed → Deep Link → Target UI State | Direct controlled mobile state establishment |

Platforms: Android emulator (environment_type EMULATED) and iOS Simulator (environment_type SIMULATED). Six scenario × platform combinations. The purpose of the gate is to determine whether Mobilewright supports the mobile capabilities this study requires (mandatory capabilities MC-01 … MC-10, protocol/mobile-runner-policy-v1.md, Section 5). It is not a benchmark against Appium 3.

## Qualification SUT

The qualification SUT is OmniPizza (SUT-01), designated in protocol/mobile-runner-policy-v1.md, Section 3. Results obtained on it qualify the runner only; they are not evidence about OmniPizza or any other evaluated ecosystem, confer no familiarity advantage and no privileged interpretation, and are disclosed as a study limitation. The build is pinned by the ORCHESTRATOR under `qualification_build` in manifests/toolchain-manifest.yaml before the first run and copied verbatim into the table below by QUALIFIER-MOBILE-01, which never selects or changes it; a discrepancy between the pinned record and the build obtained is recorded in qualification/unresolved.md (created on first use), never corrected here or in the manifest.

| Field | Value |
|---|---|
| Qualification SUT | OmniPizza (SUT-01) |
| Repository | https://github.com/gsanchezm/OmniPizza |
| Commit SHA or release (or strongest reproducible identifier) | release v1.1.8 (tag commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a, published 2026-07-22T02:00:52Z) — the same pinned identity as manifests/sut-manifest.yaml SUT-01 android/ios |
| Android build identity | omnipizza-release.apk, 84930726 bytes, sha256 1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4 (release asset of v1.1.8) |
| iOS build identity | OmniPizza-Simulator.zip, 26921522 bytes, sha256 de2e8c21b0788cef1ba4654378449d16e958574b33a2b4ef8a07cb698dbc6eb1 (release asset of v1.1.8; simulator-only build per the repository README) |
| Pinned by / date (from the manifest) | ORCHESTRATOR / 2026-09-22 |
| Copied by / date | QUALIFIER-MOBILE-01 / 2026-09-22 |

Build identities observed while realizing the scenarios (pre-run, on the operator workstation; both digests matched the pins): Android package `com.omnipizza.app`, versionName 1.1.8, launchable activity `com.omnipizza.app.MainActivity`, minSdk 29, native code arm64-v8a / armeabi-v7a / x86 / x86_64; iOS bundle `com.omnipizza.app`, CFBundleShortVersionString 1.1.8, URL scheme `omnipizza`, universal binary (x86_64, arm64) built against the iphonesimulator 26.5 SDK with MinimumOSVersion 15.1. The gate re-downloads both assets at every gate start and fails closed on a digest mismatch (`output/environment/<platform>-build-verification.json`).

## Scenario realization (recorded before the first run)

The concrete realization of each scenario on the qualification SUT is recorded here before any run and is identical for every execution. It is implemented verbatim by `harness/execute.mjs` (constant `REALIZATION`). Identifiers are the app's stable `testID`s (exposed as the accessibility identifier on iOS and as the resource-id on Android, per the E01 evidence pointers SUT01-EV-0009/0010/0011/0012, read for identifiers only). Documented test account `standard_user` / `pizza123`, market US (currency USD), UI language English. Product oracles were anchored on 2026-09-22 in both the pinned source (`backend/constants.py`, PIZZA_CATALOG) and the hosted catalog (`GET /api/pizzas`, X-Country-Code US): p01 Margherita base price 12.99; p12 BBQ Chicken base price 15.99; size add-ons (`frontend-mobile/src/constants/pizza.ts`): large +4 USD; the mobile client computes unit price = price + ceil(size_usd × price/base_price).

| Scenario | Start state | Concrete steps (screens, identifiers, controls) | API seed (MQ3 only) | Deep link (MQ3 only) | Pre-declared terminal UI state |
|---|---|---|---|---|---|
| MQ1 | Clean reset (MC-09: the app is uninstalled if present and the pinned build is installed and verified as installed; the app is not running). The runner launches `com.omnipizza.app` (MC-01) and the initial screen `screen-login` is visible. | 1. `screen-login` visible (MC-02, MC-06, MC-08). 2. tap `btn-market-US` (MC-04). 3. fill `input-password` with `pizza123` (MC-03; the lower field first, while the keyboard is closed). 4. fill `input-username` with `standard_user` (MC-03; the upper field stays visible above the keyboard). 5. read back both fields (MC-08; diagnostic record only, no oracle). 6. tap `text-welcome-title`, a non-interactive text above the inputs, which closes the keyboard (MC-04). 7. scroll `btn-login` into view if needed and tap it (MC-04). | — | — | `screen-catalog` visible (within 90 s) AND `view-bottom-nav` visible. |
| MQ2 | Catalog screen, reached from a clean reset by the MQ1 steps (recorded as the precondition, timed separately, executed by the runner). | 1. `card-pizza-p01` visible (catalog list loaded; MC-02, MC-08). 2. `screen.swipe('up')` in the catalog (MC-05). 3. scroll `btn-add-pizza-p12` (product BBQ Chicken, the last catalog entry, outside the initial viewport) into view (MC-05) and tap it (MC-04). 4. `screen-pizza-builder` visible (MC-06). 5. `text-estimated-total-value` has text `$15.99` (MC-08). 6. tap the native size control `btn-size-large` (MC-04). | — | — | `screen-pizza-builder` visible AND `text-estimated-total-value` has text `$19.99` (observable UI state change caused by the native control: 15.99 + 4). |
| MQ3 | Clean reset (MC-09) with the pinned build installed and not running (cold state). Before the first runner action the harness (outside the runner) verifies backend health, logs in as `standard_user`, applies the seed, and verifies it by `GET /api/cart`. | 1. runner opens the deep link (MC-07; the app starts cold). 2. iOS only: the system confirmation "Open in OmniPizza?" shown for a custom-scheme link opened from a cold state is accepted by tapping its `Open` button through the runner (MC-02, MC-04); whether it appeared is recorded. 3. `screen-checkout` visible (MC-06, MC-08). 4. text `2x Margherita` visible (MC-08). 5. text `$33.98` visible (MC-08). | `POST /api/cart` with `{"items":[{"pizza_id":"p01","quantity":2,"size":"large","toppings":[]}]}` (Bearer token of the documented test account), then `GET /api/cart` with `X-Country-Code: US` must return exactly one line: pizza_id p01, quantity 2, size large. After the execution the harness calls `POST /api/session/reset` (documented session endpoint) so the shared test account's server-side cart is left empty. | `omnipizza://checkout?market=US&hydrateCart=true&accessToken=<jwt>` (universal params documented in the SUT README; the token is redacted in every kept artifact). | `screen-checkout` visible (within 90 s) AND the seeded line title `2x Margherita` visible AND the seeded line total `$33.98` visible (2 × (12.99 + 4)), i.e. the target UI state reflects the seeded state. |

Timeouts (identical for every execution; generous on purpose because duration is secondary evidence only): screen arrival 90 s; other assertions 30 s; locator actions 30 s; app launch 60 s; install 300 s; a per-execution watchdog of 12 min kills a hung execution, which is then recorded as FAILURE. Backend health before every execution: up to 6 attempts of `GET /health` (45 s each, 5 s apart), because the hosted backend is cold-started (32 s observed on 2026-09-22).

## Pass criteria (protocol/mobile-runner-policy-v1.md, Section 7)

- N = 10 clean measured executions per scenario × platform combination (60 in total).
- Pass requires all four: (1) 100% support of MC-01 … MC-10 on both platforms; (2) 10/10 successful measured executions for every combination; (3) no repeated runner-caused blocker for any mandatory capability; (4) no manual intervention inside any measured scenario.
- Warm-up executions may precede the measured executions of a combination and never count toward N; a runner-caused warm-up failure is still recorded and counts under the repeated-blocker criterion (3).
- Infrastructure failures unrelated to Mobilewright are recorded as EXCLUDED with an attribution record and replaced by an additional measured execution; a failure whose attribution is uncertain is runner-caused.
- Execution duration is secondary evidence only. Mobilewright must NOT be selected solely because it is faster.

## Gate implementation (authored before the first run)

| Path | Role |
|---|---|
| `run-gate-android.sh`, `run-gate-ios.sh` | Platform entry points executed by `.github/workflows/e03-mobile-qualification.yml` (Android inside the pinned emulator-runner step; iOS after Xcode 16.4 is selected). They download and digest-verify the pinned build, install the runner exactly as pinned, record the environment (`output/environment/`), select the device by explicit identifier only (auto-discovery is never used), and start the orchestrator. |
| `gate-common.sh` | Shared library: pins (copied from manifests/toolchain-manifest.yaml), modes, output location, hygiene prefixes. |
| `harness/package.json`, `harness/package-lock.json` | The runner under qualification pinned exactly (`mobilewright@0.0.60`, npm integrity sha512-c+aIg0…, resolving `mobilecli@1.0.13` and `playwright@1.63.0`); installed with `npm ci` at gate start; the observed versions are recorded in `output/environment/<platform>-runner-install.json`. Mobilewright's dependency `mobilecli` (the device control server and, on iOS, the on-device agent) is treated as part of the runner under qualification: a failure inside it is a runner failure. |
| `harness/run-gate.mjs` | Orchestrator (imports nothing from the runner): backend reachability and read-only catalog snapshot at gate start; runner readiness probe (connect, list devices, screenshot; on iOS the agent status); then, per scenario in the order MQ1, MQ2, MQ3: the warm-ups (exactly one in QUALIFICATION mode), then measured executions until N = 10 non-excluded ones exist, replacing EXCLUDED executions (cap 5 replacements per combination; a hit cap is logged and leaves fewer than 10, recorded honestly). Structurally forbids a warm-up after the first measured execution of a combination. One child process per execution; watchdog; execution log (`output/execution-log-<platform>.jsonl` and `.csv`); `output/summary-<platform>.json` with per-combination results, duration median/IQR, and a provisional capability tally. |
| `harness/execute.mjs` | One execution: harness preconditions (health; MQ3 login + seed + verification) — only a failure here may propose EXCLUDED (SUT_INSTANCE or API_SEED) and it happens before the first runner action; then, through the runner: connect to the pinned device by id, MC-09 reset (uninstall if installed, install the pinned build, verify installed), the scenario steps above, and MC-10 artifacts (`terminal.png`, `view-tree-terminal.json`, `runner.log` with the runner's debug output). Any failure after the first runner action is FAILURE with `failed_step` (name, capabilities, error), `failure.png`, `view-tree-failure.json`, and `device-log-failure.txt` (Android: the activity-start intent lines, which show the deep-link data the app actually received, plus the logcat tail; iOS: the simulator log) as attribution artifacts; for MQ3 the cart is re-read after a failure. |
| `harness/backend.mjs` | Harness-side backend calls (health, login, catalog snapshot, seed + verify, cart re-read, session reset); tokens redacted from every record. |

Execution id convention (package): `MQ<n>-<AND|IOS>-<WARMUP|MEASURED>-<nn>`; an excluded execution keeps kind MEASURED with outcome EXCLUDED and is followed by a replacement. Execution record fields (policy 7.1): execution_id, combination, platform, attempt, timestamp, environment_type, runner version, outcome (SUCCESS / FAILURE / EXCLUDED), duration, artifact paths, notes — plus the steps with their capabilities, the capabilities exercised, the failed step, the exclusion proposal, the harness precheck, the instruction id, the prompt version id, and the GitHub run id / attempt / image version.

Duration definition: `duration_ms.scenario` runs from the first scripted runner action of the scenario (MQ1: app launch; MQ2: after the catalog precondition is verified; MQ3: opening the deep link) to the verification of the terminal state; `reset`, `precondition` (MQ2 only), and `total` are recorded separately. The per-combination median and IQR of `scenario` over successful measured executions are the secondary evidence of Section 7.4.

Publication hygiene: every kept artifact is scrubbed by the orchestrator of host paths (workspace, temporary and home directories), of bearer tokens, and of the vendor and assistant terms prohibited by the validation workflow, before it is uploaded or imported; scrubbing changes no measurement. The runner's usage telemetry is disabled (`MOBILEWRIGHT_DISABLE_TELEMETRY`, `DO_NOT_TRACK`). The emulator is provisioned by the pinned emulator-runner action with its default `disable-animations: true`; no device setting is changed through the runner; the SUT and its pinned build are never modified.

Local development of this implementation (mode DEVELOPMENT) writes outside the repository, labels every record DEVELOPMENT, and is summarized only in the section "Development runs" below; it is never a gate execution.

## Execution log

One row per execution (warm-up, measured, or excluded). Fields per protocol/mobile-runner-policy-v1.md, Section 7.1. No row exists.

| execution_id | combination (MQn × platform) | kind (WARMUP / MEASURED / EXCLUDED) | attempt | timestamp | environment_type | Mobilewright version | outcome (SUCCESS / FAILURE / EXCLUDED) | duration | artifacts | notes |
|---|---|---|---|---|---|---|---|---|---|---|

## Results per combination

| Combination | Warm-ups (count) | Measured successes / 10 | Excluded (count) | Runner-caused failures (count) | Manual intervention (count) | Result |
|---|---|---|---|---|---|---|
| MQ1 × Android emulator | | | | | | |
| MQ1 × iOS Simulator | | | | | | |
| MQ2 × Android emulator | | | | | | |
| MQ2 × iOS Simulator | | | | | | |
| MQ3 × Android emulator | | | | | | |
| MQ3 × iOS Simulator | | | | | | |

## Capability support

| Capability | Android emulator (SUPPORTED / UNSUPPORTED) | iOS Simulator (SUPPORTED / UNSUPPORTED) | Runner-caused failures (count, execution ids) | Notes |
|---|---|---|---|---|
| MC-01 Install and launch | | | | |
| MC-02 Locate by stable identifier | | | | |
| MC-03 Text entry | | | | |
| MC-04 Tap / press native control | | | | |
| MC-05 Scroll / swipe | | | | |
| MC-06 Screen navigation and verification | | | | |
| MC-07 Deep link with parameters | | | | |
| MC-08 Read UI state | | | | |
| MC-09 App state reset between executions | | | | |
| MC-10 Artifact capture | | | | |

## Attribution records (excluded executions)

One row per excluded execution. An exclusion without a complete row is invalid and the execution counts as a failed measured execution. Attributed cause is never RUNNER.

| execution_id | combination | timestamp | failure description | attributed cause (INFRASTRUCTURE / SUT_INSTANCE / API_SEED / OPERATOR / OTHER) | demonstrating artifacts | recorded_by |
|---|---|---|---|---|---|---|

## Secondary evidence — duration

| Combination | Median duration | IQR | Notes |
|---|---|---|---|
| MQ1 × Android emulator | | | |
| MQ1 × iOS Simulator | | | |
| MQ2 × Android emulator | | | |
| MQ2 × iOS Simulator | | | |
| MQ3 × Android emulator | | | |
| MQ3 × iOS Simulator | | | |

## Prerequisites

All items must be satisfied before the first run.

- [x] protocol/mobile-runner-policy-v1.md is in state FROZEN-PRE-DATA with human approval recorded per protocol/change-control-v1.md (frozen 2026-09-16; manifests/protocol-freeze-v1.yaml)
- [x] Mobilewright and Appium 3 versions are pinned in manifests/toolchain-manifest.yaml (`pinned_candidate_version`: mobilewright 0.0.60; appium 3.7.0); the observed install record (`version`, `install_date`, `platform`) stays null there until the ORCHESTRATOR transcribes the values this gate records
- [x] Qualification SUT build is pinned by the ORCHESTRATOR in manifests/toolchain-manifest.yaml and copied verbatim above by QUALIFIER-MOBILE-01
- [x] Scenario realization is recorded above
- [x] Environment is recorded in manifests/toolchain-manifest.yaml by the ORCHESTRATOR and copied below
- [x] Explicit instruction to execute the gate, issued by a human and relayed by the ORCHESTRATOR, has been received and is recorded below

### Environment record

| Field | Value |
|---|---|
| Mobilewright version | pinned 0.0.60 (npm `mobilewright`, integrity sha512-c+aIg0FtMI6226xoVwXiO8Guqk9v5rT81zohz2Rs4WuZEaOgJidHoX9yd5Sqjpx3nTVYfmkFtqHoMFKMGVOuCg==, source tag v0.0.60, commit 2046d2d95e7db6383183bb6b116f81b1236cae42, engines node >= 22.12.0); observed installed version, install date, and host platform: recorded at gate start in `output/environment/<platform>-runner-install.json` (pending — no gate run yet) |
| Appium 3 version (fallback pin) | 3.7.0 (npm `appium`, source commit b67de03966155ff052076c11c1c8f20cc2ba9134); not installed; used only if the switch rule fires; Appium 2 never |
| Android emulator identity (device profile, OS image) | pinned: `system-images;android-35;google_apis;x86_64`, API 35, profile pixel_7, provisioned by ReactiveCircus/android-emulator-runner v2.38.0 at commit a421e43855164a8197daf9d8d40fe71c6996bb0d on a GitHub-hosted ubuntu-24.04 runner (image 20260907.300.1 or later, KVM enabled); environment_type EMULATED; observed serial, Android release, AVD name, build fingerprint, emulator and adb versions: `output/environment/android-environment.json` (pending) |
| iOS Simulator identity (device, OS version) | pinned: iPhone 16, iOS 18.5 simulator runtime, Xcode 16.4 build 16F6 (selected with xcode-select) on a GitHub-hosted macos-15 runner (image 20260824.0482.1 or later that still ships them); environment_type SIMULATED; observed UDID, runtime build, Xcode and macOS versions: `output/environment/ios-environment.json` (pending) |
| Host platform | GitHub-hosted runners: ubuntu-24.04, x86_64 (Android); macos-15, arm64 (iOS); the runner image version is recorded per execution (`github.image_version`) |
| Date of first run | pending — no gate run yet |
| Instruction to execute (date, human source, relaying role) | MOBILE-QUALIFICATION-EXEC-AUTH-01 (MOBILE_QUALIFICATION_EXECUTION), 2026-09-22, issued by gilbertosanchez, relayed by ORCHESTRATOR to QUALIFIER-MOBILE-01; provenance record with the verbatim text: manifests/mobile-qualification-execution-auth-v1.yaml; launched under prompt version qualifier-mobile-01-mobilewright-gate-v1 |

## Development runs (not gate executions)

Harness development on the operator workstation, mode DEVELOPMENT, output kept outside the repository, never counted toward N and never a warm-up. Recorded here for transparency; any runner-caused blocker of a mandatory capability observed in such a run is disclosed and escalated in qualification/unresolved.md for the human to decide whether it counts under criterion 7.2.3, never decided by this role alone.

| Date | Platform (local identity, differences from the pins) | Scenarios | Outcome | Notes |
|---|---|---|---|---|
| 2026-09-22 | Android emulator on the operator workstation (AVD Pixel_API35_Test: system-images;android-35;google_apis;x86_64, API 35, hardware profile pixel_8 instead of the pinned pixel_7; emulator 36.4.9.0; Intel macOS host under a 1-minute load average of 70-270 from unrelated applications) | MQ1 (N = 1, no warm-up), four attempts while the harness was being written | No attempt reached the terminal state. Attempts 1-2 failed in the harness (runner device id must be the AVD name, not the adb serial; the runner's per-call RPC timeout of 30 s is shorter than the 81 MB install on the emulator) and were fixed in the harness. Attempts 3-4 failed at "login screen visible": the app had rendered its login screen (failure screenshots), but a system dialog ("Pixel Launcher isn't responding", "System UI isn't responding") from the starved emulator covered it, so the accessibility hierarchy held only the dialog. | Host resource exhaustion of the operator workstation; not a runner-caused failure and not a SUT behavior. The same runner readiness probe, reset (uninstall + install through the runner), and app launch succeeded on the emulator before the dialog appeared. Never counted. |
| 2026-09-22 | iOS Simulator on the operator workstation (iPhone 16, iOS 18.2 runtime 22C150 instead of the pinned iOS 18.5; Xcode 26.5 build 17F42 instead of the pinned 16.4; same overloaded host) | MQ1 (N = 1, no warm-up), three attempts | Attempt 1 failed in the script (`simctl list` accepts one type filter; fixed). Attempt 2 failed at connection: the runner's driver treats the non-zero exit of its own `mobilecli agent status` as an error instead of installing its on-device agent; the agent (DeviceKit 0.0.27, bundle com.mobilenext.devicekit-iosUITests.xctrunner) was then installed as a preparation step of the gate script (3 min 37 s). Attempt 3: connection, MC-09 reset (uninstall, install of the pinned .zip through the runner, verification) succeeded; "launch the app" failed with "timed out waiting for WebDriverAgent to be ready" when the runner started its agent on the starved host. | The agent-start timeout occurred on a host with a 1-minute load average above 100 and on a non-pinned runtime; it is disclosed here and re-examined on the pinned substrate (see the GitHub Actions DEVELOPMENT run below). Never counted. |
| 2026-09-22 | GitHub Actions, mode DEVELOPMENT, run 35758030920 (workflow revision of public main f93be54): the pinned substrates — ubuntu-24.04 image 20260907.300.1 with the emulator-runner action (API 35, google_apis, x86_64, pixel_7) and macos-15 image 20260907.0337.1 with Xcode 16.4 and the iOS 18.5 iPhone 16 simulator | MQ1, MQ2, MQ3 on both platforms, N = 1, no warm-up (6 executions) | Environment, pinned-build digests, runner install (mobilewright 0.0.60, mobilecli 1.0.13), readiness probe, MC-09 reset (uninstall + install through the runner) and app launch succeeded on both platforms. All six executions then failed: Android MQ1/MQ2 at "catalog screen visible" — both fields were filled but the software keyboard covered `btn-login`, so the tap landed on the keyboard (failure screenshot); iOS MQ1 at "enter password" and MQ2 at "enter username" — the keyboard raised after the username field covered the password field, the tap did not move focus, and the runner's clear step (select-all chord + backspace) then wiped the username / removed a single character ("standard_use"), so its clear verification failed; Android MQ3 at "checkout screen visible" — the app opened Checkout with an empty cart although the harness had seeded and verified the cart; iOS MQ3 at "checkout screen visible" — the system prompt "Open in OmniPizza?" was showing. | Realization refined before the first gate run (this table's date): password field first (while the keyboard is closed), then the username, a read-back of both fields for diagnosis, a tap on `text-welcome-title` to close the keyboard before Sign In; on iOS the system prompt is accepted through the runner; Android failure artifacts now include the activity-start intent lines. These are realization corrections (keyboard occlusion, platform prompt), not runner capabilities. The iOS select-all flakiness and the Android empty-cart result are left for the gate to measure; see the next row for the attribution experiment. Never counted. |
| 2026-09-22 | Android emulator on the operator workstation (same local identity as above), deep-link attribution experiment, no scenario executed | `omnipizza://pizza-builder?market=US&accessToken=<jwt>&pizzaId=p12&size=large` sent once through the runner's device server (`mobilecli url`, the mechanism behind `device.openUrl`) and once through `adb shell am start -a android.intent.action.VIEW -d '<url>'` with the URL quoted | Through the runner: the app opened the product screen route with an empty customizer (route delivered, no product, no size, no price). Through adb with the URL quoted: the product screen showed BBQ Chicken with Large selected and estimated total $19.99, i.e. every parameter delivered. The activity-manager log redacts query strings ("dat=omnipizza://checkout/..."), so it cannot show the delivered data; this UI-level comparison can. | Consistent with the CI MQ3 result (Checkout opened for market US with an empty cart): the runner's URL opening on Android delivers the path but drops the query parameters after the first `&` (or all of them), which is a runner-caused failure of MC-07 (deep link carrying parameters). Recorded as attribution support for the gate; no harness workaround is applied because the gate measures the runner as pinned. Never counted. |

## Decision record

| Field | Value |
|---|---|
| Date | |
| Gate result (PASS / FAIL) | |
| Failed criteria and capabilities (if FAIL) | |
| Decision (one of: Mobilewright, Appium 3) | |
| Rationale | |
| Recorded by | |

The decision is also recorded in manifests/toolchain-manifest.yaml and in the change log per protocol/change-control-v1.md (protocol/mobile-runner-policy-v1.md, Section 8), transcribed by the ORCHESTRATOR from this record. If the runner is Appium 3, the compatibility smoke (qualification/compatibility-smoke/) is executed with Appium 3. Appium 2 is never introduced.

## Warning

Do not execute qualification until explicitly instructed and until protocol/mobile-runner-policy-v1.md is frozen. Do not fill any result, attribution, or decision field before a run has actually occurred. Do not use anything recorded here as evidence about any SUT.
