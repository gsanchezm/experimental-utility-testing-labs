# Mobilewright Qualification

## Status

**INVALID / REQUIRES RE-EXECUTION** (protocol/unresolved.md, PROTO-U10, 2026-09-22; correction record manifests/mobile-qualification-authorization-correction-v1.yaml). The gate executed on 2026-09-22 ran on the ORCHESTRATOR's relay of MOBILE-QUALIFICATION-EXEC-AUTH-01, a record that no human had issued (the human research lead has determined by explicit corrective instruction that the text was a proposed draft never approved; no repository artifact predating the record carries a human authorization). protocol/mobile-runner-policy-v1.md, Section 2, requires an explicit instruction issued by a human; that prerequisite was not satisfied. Consequently: the executions below are preserved unchanged and classified **HISTORICAL_UNAUTHORIZED_EXECUTION** (observed but protocol-inadmissible for runner-selection authority; `output/QUARANTINE-RECORD.yaml`); the FAIL decision and the switch-rule selection of Appium 3 recorded that day are **superseded and have no authority** (Section 8 was not legitimately triggered; the observed technical failure does not independently authorize the switch); the **current valid state** is primary candidate Mobilewright 0.0.60, fallback Appium 3.7.0, **selected mobile runner none**, compatibility smoke NOT AUTHORIZED / NOT_STARTED; a protocol-valid gate is NOT_STARTED and requires a **NEW** human authorization issued after the correction (the retired id is refused by the workflow's readiness gate). **PREQUALIFICATION_OUTCOME_EXPOSURE = true** (see the correction section). Every section below that reports results is a historical record of the quarantined executions, kept verbatim as written on 2026-09-22 and re-labeled here, never a Section 7 result.

### Historical description of the quarantined executions (written 2026-09-22 before the correction; non-authoritative)

The gate was executed through `.github/workflows/e03-mobile-qualification.yml` on the pinned substrates as two sequential QUALIFICATION runs (Android: run 35763051534; iOS: run 35767911878; one run per platform because both platform jobs use the same documented test account whose server-side cart the MQ3 seed and session reset act on), 3 warm-ups and 30 measured executions per platform, 60 measured executions in total, no exclusion, no manual intervention. Mobilewright 0.0.60 passed MQ1 and MQ2 on both platforms and MQ3 on iOS (10/10 each) and failed MQ3 on the Android emulator (0/10, plus its warm-up): the runner's deep-link opening on Android delivers the route but not the query parameters (MC-07), so the seeded target state was never reached. Criteria 7.2.1, 7.2.2, and 7.2.3 are violated; 7.2.4 holds. Details, attribution, and the decision record follow. Every record and artifact is under `output/` (import records `output/import-record-run<id>-a1.json`).

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

Publication hygiene: every kept artifact is scrubbed by the orchestrator of host paths (workspace, temporary and home directories), of bearer tokens, and of the vendor and assistant terms prohibited by the validation workflow, before it is uploaded or imported; scrubbing changes no measurement. Replacements that actually fired in the imported gate artifacts (counted after import): host-path placeholders 464 occurrences in 148 files; bearer-token placeholders 46 (the MQ3 records and prechecks); generic-term placeholders 400 occurrences, all inside the eleven Android `device-log-failure.txt` files, where Android framework class names that contain a generic assistant term (for example the OatFile and notification-assistant services of the system log) were replaced by `<term-redacted>` — an over-broad match of the term list that altered those system-log lines only; no runner log, record, view tree, screenshot, intent line, or measurement was affected, and no attribution rests on the altered lines. The runner's usage telemetry is disabled (`MOBILEWRIGHT_DISABLE_TELEMETRY`, `DO_NOT_TRACK`). The emulator is provisioned by the pinned emulator-runner action with its default `disable-animations: true`; no device setting is changed through the runner; the SUT and its pinned build are never modified.

Local development of this implementation (mode DEVELOPMENT) writes outside the repository, labels every record DEVELOPMENT, and is summarized only in the section "Development runs" below; it is never a gate execution.

## Execution log

HISTORICAL — quarantined (PROTO-U10): every row below is a HISTORICAL_UNAUTHORIZED_EXECUTION, preserved as recorded; not a Section 7 gate execution.

One row per execution (warm-up, measured, or excluded). Fields per protocol/mobile-runner-policy-v1.md, Section 7.1. Generated from `output/<execution_id>/record.json` by `harness/summarize-results.mjs` (66 executions: per platform 3 warm-ups and 30 measured; no excluded execution). Every execution ran on the runner's scripted scenario without manual intervention; `duration` is the scenario time (first scripted runner action after reset/seed to terminal verification) and the total including reset. Artifact directories hold `record.json`, `runner.log`, `harness-precheck.json`, and `terminal.png` + `view-tree-terminal.json` (success) or `failure.png` + `view-tree-failure.json` + `device-log-failure.txt` (failure). The execution ids follow the package convention (MQ<n>-<AND|IOS>-<WARMUP|MEASURED>-<nn>).

| execution_id | combination (MQn × platform) | kind (WARMUP / MEASURED / EXCLUDED) | attempt | timestamp | environment_type | Mobilewright version | outcome (SUCCESS / FAILURE / EXCLUDED) | duration | artifacts | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| MQ1-AND-WARMUP-01 | MQ1 × Android emulator | WARMUP | 1 | 2026-09-22T17:50:47.335Z | EMULATED | 0.0.60 | SUCCESS | scenario 26.1 s; total 35.4 s | `output/MQ1-AND-WARMUP-01/` |  |
| MQ1-AND-MEASURED-01 | MQ1 × Android emulator | MEASURED | 1 | 2026-09-22T17:51:22.976Z | EMULATED | 0.0.60 | SUCCESS | scenario 23.3 s; total 32.3 s | `output/MQ1-AND-MEASURED-01/` |  |
| MQ1-AND-MEASURED-02 | MQ1 × Android emulator | MEASURED | 2 | 2026-09-22T17:51:55.447Z | EMULATED | 0.0.60 | SUCCESS | scenario 18.2 s; total 26.1 s | `output/MQ1-AND-MEASURED-02/` |  |
| MQ1-AND-MEASURED-03 | MQ1 × Android emulator | MEASURED | 3 | 2026-09-22T17:52:21.650Z | EMULATED | 0.0.60 | SUCCESS | scenario 15.1 s; total 21.0 s | `output/MQ1-AND-MEASURED-03/` |  |
| MQ1-AND-MEASURED-04 | MQ1 × Android emulator | MEASURED | 4 | 2026-09-22T17:52:42.745Z | EMULATED | 0.0.60 | SUCCESS | scenario 14.8 s; total 19.4 s | `output/MQ1-AND-MEASURED-04/` |  |
| MQ1-AND-MEASURED-05 | MQ1 × Android emulator | MEASURED | 5 | 2026-09-22T17:53:02.193Z | EMULATED | 0.0.60 | SUCCESS | scenario 14.4 s; total 18.7 s | `output/MQ1-AND-MEASURED-05/` |  |
| MQ1-AND-MEASURED-06 | MQ1 × Android emulator | MEASURED | 6 | 2026-09-22T17:53:21.014Z | EMULATED | 0.0.60 | SUCCESS | scenario 14.6 s; total 19.1 s | `output/MQ1-AND-MEASURED-06/` |  |
| MQ1-AND-MEASURED-07 | MQ1 × Android emulator | MEASURED | 7 | 2026-09-22T17:53:40.235Z | EMULATED | 0.0.60 | SUCCESS | scenario 14.3 s; total 19.2 s | `output/MQ1-AND-MEASURED-07/` |  |
| MQ1-AND-MEASURED-08 | MQ1 × Android emulator | MEASURED | 8 | 2026-09-22T17:53:59.748Z | EMULATED | 0.0.60 | SUCCESS | scenario 14.3 s; total 19.7 s | `output/MQ1-AND-MEASURED-08/` |  |
| MQ1-AND-MEASURED-09 | MQ1 × Android emulator | MEASURED | 9 | 2026-09-22T17:54:19.521Z | EMULATED | 0.0.60 | SUCCESS | scenario 13.2 s; total 18.4 s | `output/MQ1-AND-MEASURED-09/` |  |
| MQ1-AND-MEASURED-10 | MQ1 × Android emulator | MEASURED | 10 | 2026-09-22T17:54:37.991Z | EMULATED | 0.0.60 | SUCCESS | scenario 14.0 s; total 19.3 s | `output/MQ1-AND-MEASURED-10/` |  |
| MQ2-AND-WARMUP-01 | MQ2 × Android emulator | WARMUP | 1 | 2026-09-22T17:54:57.349Z | EMULATED | 0.0.60 | SUCCESS | scenario 9.0 s; total 28.3 s | `output/MQ2-AND-WARMUP-01/` |  |
| MQ2-AND-MEASURED-01 | MQ2 × Android emulator | MEASURED | 1 | 2026-09-22T17:55:25.727Z | EMULATED | 0.0.60 | SUCCESS | scenario 13.1 s; total 31.9 s | `output/MQ2-AND-MEASURED-01/` |  |
| MQ2-AND-MEASURED-02 | MQ2 × Android emulator | MEASURED | 2 | 2026-09-22T17:55:57.701Z | EMULATED | 0.0.60 | SUCCESS | scenario 8.9 s; total 27.0 s | `output/MQ2-AND-MEASURED-02/` |  |
| MQ2-AND-MEASURED-03 | MQ2 × Android emulator | MEASURED | 3 | 2026-09-22T17:56:24.809Z | EMULATED | 0.0.60 | SUCCESS | scenario 14.6 s; total 33.3 s | `output/MQ2-AND-MEASURED-03/` |  |
| MQ2-AND-MEASURED-04 | MQ2 × Android emulator | MEASURED | 4 | 2026-09-22T17:56:58.258Z | EMULATED | 0.0.60 | SUCCESS | scenario 7.5 s; total 25.7 s | `output/MQ2-AND-MEASURED-04/` |  |
| MQ2-AND-MEASURED-05 | MQ2 × Android emulator | MEASURED | 5 | 2026-09-22T17:57:24.049Z | EMULATED | 0.0.60 | SUCCESS | scenario 9.1 s; total 27.9 s | `output/MQ2-AND-MEASURED-05/` |  |
| MQ2-AND-MEASURED-06 | MQ2 × Android emulator | MEASURED | 6 | 2026-09-22T17:57:52.060Z | EMULATED | 0.0.60 | SUCCESS | scenario 9.8 s; total 28.8 s | `output/MQ2-AND-MEASURED-06/` |  |
| MQ2-AND-MEASURED-07 | MQ2 × Android emulator | MEASURED | 7 | 2026-09-22T17:58:20.950Z | EMULATED | 0.0.60 | SUCCESS | scenario 9.0 s; total 28.7 s | `output/MQ2-AND-MEASURED-07/` |  |
| MQ2-AND-MEASURED-08 | MQ2 × Android emulator | MEASURED | 8 | 2026-09-22T17:58:49.763Z | EMULATED | 0.0.60 | SUCCESS | scenario 8.9 s; total 28.3 s | `output/MQ2-AND-MEASURED-08/` |  |
| MQ2-AND-MEASURED-09 | MQ2 × Android emulator | MEASURED | 9 | 2026-09-22T17:59:18.174Z | EMULATED | 0.0.60 | SUCCESS | scenario 9.3 s; total 27.9 s | `output/MQ2-AND-MEASURED-09/` |  |
| MQ2-AND-MEASURED-10 | MQ2 × Android emulator | MEASURED | 10 | 2026-09-22T17:59:46.168Z | EMULATED | 0.0.60 | SUCCESS | scenario 8.5 s; total 27.4 s | `output/MQ2-AND-MEASURED-10/` |  |
| MQ3-AND-WARMUP-01 | MQ3 × Android emulator | WARMUP | 1 | 2026-09-22T18:00:13.673Z | EMULATED | 0.0.60 | FAILURE | total 95.5 s | `output/MQ3-AND-WARMUP-01/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-01 | MQ3 × Android emulator | MEASURED | 1 | 2026-09-22T18:01:49.317Z | EMULATED | 0.0.60 | FAILURE | total 95.0 s | `output/MQ3-AND-MEASURED-01/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-02 | MQ3 × Android emulator | MEASURED | 2 | 2026-09-22T18:03:24.518Z | EMULATED | 0.0.60 | FAILURE | total 95.0 s | `output/MQ3-AND-MEASURED-02/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-03 | MQ3 × Android emulator | MEASURED | 3 | 2026-09-22T18:04:59.678Z | EMULATED | 0.0.60 | FAILURE | total 94.9 s | `output/MQ3-AND-MEASURED-03/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-04 | MQ3 × Android emulator | MEASURED | 4 | 2026-09-22T18:06:34.841Z | EMULATED | 0.0.60 | FAILURE | total 95.0 s | `output/MQ3-AND-MEASURED-04/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-05 | MQ3 × Android emulator | MEASURED | 5 | 2026-09-22T18:08:10.028Z | EMULATED | 0.0.60 | FAILURE | total 95.0 s | `output/MQ3-AND-MEASURED-05/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-06 | MQ3 × Android emulator | MEASURED | 6 | 2026-09-22T18:09:45.143Z | EMULATED | 0.0.60 | FAILURE | total 95.0 s | `output/MQ3-AND-MEASURED-06/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-07 | MQ3 × Android emulator | MEASURED | 7 | 2026-09-22T18:11:20.423Z | EMULATED | 0.0.60 | FAILURE | total 95.0 s | `output/MQ3-AND-MEASURED-07/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-08 | MQ3 × Android emulator | MEASURED | 8 | 2026-09-22T18:12:55.582Z | EMULATED | 0.0.60 | FAILURE | total 94.9 s | `output/MQ3-AND-MEASURED-08/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-09 | MQ3 × Android emulator | MEASURED | 9 | 2026-09-22T18:14:30.701Z | EMULATED | 0.0.60 | FAILURE | total 95.0 s | `output/MQ3-AND-MEASURED-09/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ3-AND-MEASURED-10 | MQ3 × Android emulator | MEASURED | 10 | 2026-09-22T18:16:05.953Z | EMULATED | 0.0.60 | FAILURE | total 94.9 s | `output/MQ3-AND-MEASURED-10/` | failed step: checkout screen visible (MC-06, MC-08) |
| MQ1-IOS-WARMUP-01 | MQ1 × iOS Simulator | WARMUP | 1 | 2026-09-22T18:37:33.702Z | SIMULATED | 0.0.60 | SUCCESS | scenario 75.8 s; total 86.2 s | `output/MQ1-IOS-WARMUP-01/` |  |
| MQ1-IOS-MEASURED-01 | MQ1 × iOS Simulator | MEASURED | 1 | 2026-09-22T18:39:01.574Z | SIMULATED | 0.0.60 | SUCCESS | scenario 55.4 s; total 83.1 s | `output/MQ1-IOS-MEASURED-01/` |  |
| MQ1-IOS-MEASURED-02 | MQ1 × iOS Simulator | MEASURED | 2 | 2026-09-22T18:40:25.259Z | SIMULATED | 0.0.60 | SUCCESS | scenario 45.0 s; total 55.4 s | `output/MQ1-IOS-MEASURED-02/` |  |
| MQ1-IOS-MEASURED-03 | MQ1 × iOS Simulator | MEASURED | 3 | 2026-09-22T18:41:20.922Z | SIMULATED | 0.0.60 | SUCCESS | scenario 44.6 s; total 53.6 s | `output/MQ1-IOS-MEASURED-03/` |  |
| MQ1-IOS-MEASURED-04 | MQ1 × iOS Simulator | MEASURED | 4 | 2026-09-22T18:42:14.856Z | SIMULATED | 0.0.60 | SUCCESS | scenario 39.9 s; total 47.3 s | `output/MQ1-IOS-MEASURED-04/` |  |
| MQ1-IOS-MEASURED-05 | MQ1 × iOS Simulator | MEASURED | 5 | 2026-09-22T18:43:02.406Z | SIMULATED | 0.0.60 | SUCCESS | scenario 50.2 s; total 58.6 s | `output/MQ1-IOS-MEASURED-05/` |  |
| MQ1-IOS-MEASURED-06 | MQ1 × iOS Simulator | MEASURED | 6 | 2026-09-22T18:44:01.243Z | SIMULATED | 0.0.60 | SUCCESS | scenario 54.8 s; total 67.0 s | `output/MQ1-IOS-MEASURED-06/` |  |
| MQ1-IOS-MEASURED-07 | MQ1 × iOS Simulator | MEASURED | 7 | 2026-09-22T18:45:08.549Z | SIMULATED | 0.0.60 | SUCCESS | scenario 58.6 s; total 68.8 s | `output/MQ1-IOS-MEASURED-07/` |  |
| MQ1-IOS-MEASURED-08 | MQ1 × iOS Simulator | MEASURED | 8 | 2026-09-22T18:46:17.622Z | SIMULATED | 0.0.60 | SUCCESS | scenario 58.5 s; total 69.1 s | `output/MQ1-IOS-MEASURED-08/` |  |
| MQ1-IOS-MEASURED-09 | MQ1 × iOS Simulator | MEASURED | 9 | 2026-09-22T18:47:27.065Z | SIMULATED | 0.0.60 | SUCCESS | scenario 60.5 s; total 70.0 s | `output/MQ1-IOS-MEASURED-09/` |  |
| MQ1-IOS-MEASURED-10 | MQ1 × iOS Simulator | MEASURED | 10 | 2026-09-22T18:48:37.391Z | SIMULATED | 0.0.60 | SUCCESS | scenario 56.1 s; total 66.2 s | `output/MQ1-IOS-MEASURED-10/` |  |
| MQ2-IOS-WARMUP-01 | MQ2 × iOS Simulator | WARMUP | 1 | 2026-09-22T18:49:43.809Z | SIMULATED | 0.0.60 | SUCCESS | scenario 24.7 s; total 93.8 s | `output/MQ2-IOS-WARMUP-01/` |  |
| MQ2-IOS-MEASURED-01 | MQ2 × iOS Simulator | MEASURED | 1 | 2026-09-22T18:51:17.916Z | SIMULATED | 0.0.60 | SUCCESS | scenario 16.7 s; total 71.9 s | `output/MQ2-IOS-MEASURED-01/` |  |
| MQ2-IOS-MEASURED-02 | MQ2 × iOS Simulator | MEASURED | 2 | 2026-09-22T18:52:30.019Z | SIMULATED | 0.0.60 | SUCCESS | scenario 23.3 s; total 74.1 s | `output/MQ2-IOS-MEASURED-02/` |  |
| MQ2-IOS-MEASURED-03 | MQ2 × iOS Simulator | MEASURED | 3 | 2026-09-22T18:53:44.575Z | SIMULATED | 0.0.60 | SUCCESS | scenario 19.8 s; total 82.2 s | `output/MQ2-IOS-MEASURED-03/` |  |
| MQ2-IOS-MEASURED-04 | MQ2 × iOS Simulator | MEASURED | 4 | 2026-09-22T18:55:07.091Z | SIMULATED | 0.0.60 | SUCCESS | scenario 21.1 s; total 75.9 s | `output/MQ2-IOS-MEASURED-04/` |  |
| MQ2-IOS-MEASURED-05 | MQ2 × iOS Simulator | MEASURED | 5 | 2026-09-22T18:56:23.296Z | SIMULATED | 0.0.60 | SUCCESS | scenario 18.0 s; total 70.4 s | `output/MQ2-IOS-MEASURED-05/` |  |
| MQ2-IOS-MEASURED-06 | MQ2 × iOS Simulator | MEASURED | 6 | 2026-09-22T18:57:33.979Z | SIMULATED | 0.0.60 | SUCCESS | scenario 21.6 s; total 79.5 s | `output/MQ2-IOS-MEASURED-06/` |  |
| MQ2-IOS-MEASURED-07 | MQ2 × iOS Simulator | MEASURED | 7 | 2026-09-22T18:58:54.102Z | SIMULATED | 0.0.60 | SUCCESS | scenario 25.3 s; total 100.0 s | `output/MQ2-IOS-MEASURED-07/` |  |
| MQ2-IOS-MEASURED-08 | MQ2 × iOS Simulator | MEASURED | 8 | 2026-09-22T19:00:34.822Z | SIMULATED | 0.0.60 | SUCCESS | scenario 25.9 s; total 88.0 s | `output/MQ2-IOS-MEASURED-08/` |  |
| MQ2-IOS-MEASURED-09 | MQ2 × iOS Simulator | MEASURED | 9 | 2026-09-22T19:02:03.617Z | SIMULATED | 0.0.60 | SUCCESS | scenario 23.7 s; total 83.6 s | `output/MQ2-IOS-MEASURED-09/` |  |
| MQ2-IOS-MEASURED-10 | MQ2 × iOS Simulator | MEASURED | 10 | 2026-09-22T19:03:28.000Z | SIMULATED | 0.0.60 | SUCCESS | scenario 26.2 s; total 94.1 s | `output/MQ2-IOS-MEASURED-10/` |  |
| MQ3-IOS-WARMUP-01 | MQ3 × iOS Simulator | WARMUP | 1 | 2026-09-22T19:05:03.426Z | SIMULATED | 0.0.60 | SUCCESS | scenario 17.8 s; total 35.4 s | `output/MQ3-IOS-WARMUP-01/` | system open prompt accepted |
| MQ3-IOS-MEASURED-01 | MQ3 × iOS Simulator | MEASURED | 1 | 2026-09-22T19:05:39.659Z | SIMULATED | 0.0.60 | SUCCESS | scenario 22.9 s; total 37.3 s | `output/MQ3-IOS-MEASURED-01/` |  |
| MQ3-IOS-MEASURED-02 | MQ3 × iOS Simulator | MEASURED | 2 | 2026-09-22T19:06:17.618Z | SIMULATED | 0.0.60 | SUCCESS | scenario 22.3 s; total 35.4 s | `output/MQ3-IOS-MEASURED-02/` |  |
| MQ3-IOS-MEASURED-03 | MQ3 × iOS Simulator | MEASURED | 3 | 2026-09-22T19:06:53.605Z | SIMULATED | 0.0.60 | SUCCESS | scenario 22.8 s; total 33.3 s | `output/MQ3-IOS-MEASURED-03/` |  |
| MQ3-IOS-MEASURED-04 | MQ3 × iOS Simulator | MEASURED | 4 | 2026-09-22T19:07:27.267Z | SIMULATED | 0.0.60 | SUCCESS | scenario 20.5 s; total 29.9 s | `output/MQ3-IOS-MEASURED-04/` |  |
| MQ3-IOS-MEASURED-05 | MQ3 × iOS Simulator | MEASURED | 5 | 2026-09-22T19:07:57.636Z | SIMULATED | 0.0.60 | SUCCESS | scenario 21.6 s; total 30.4 s | `output/MQ3-IOS-MEASURED-05/` |  |
| MQ3-IOS-MEASURED-06 | MQ3 × iOS Simulator | MEASURED | 6 | 2026-09-22T19:08:28.933Z | SIMULATED | 0.0.60 | SUCCESS | scenario 21.0 s; total 31.4 s | `output/MQ3-IOS-MEASURED-06/` |  |
| MQ3-IOS-MEASURED-07 | MQ3 × iOS Simulator | MEASURED | 7 | 2026-09-22T19:09:00.776Z | SIMULATED | 0.0.60 | SUCCESS | scenario 21.1 s; total 30.3 s | `output/MQ3-IOS-MEASURED-07/` |  |
| MQ3-IOS-MEASURED-08 | MQ3 × iOS Simulator | MEASURED | 8 | 2026-09-22T19:09:31.335Z | SIMULATED | 0.0.60 | SUCCESS | scenario 19.8 s; total 27.5 s | `output/MQ3-IOS-MEASURED-08/` |  |
| MQ3-IOS-MEASURED-09 | MQ3 × iOS Simulator | MEASURED | 9 | 2026-09-22T19:09:59.349Z | SIMULATED | 0.0.60 | SUCCESS | scenario 19.9 s; total 26.9 s | `output/MQ3-IOS-MEASURED-09/` |  |
| MQ3-IOS-MEASURED-10 | MQ3 × iOS Simulator | MEASURED | 10 | 2026-09-22T19:10:26.552Z | SIMULATED | 0.0.60 | SUCCESS | scenario 21.0 s; total 28.7 s | `output/MQ3-IOS-MEASURED-10/` |  |

## Results per combination

HISTORICAL — quarantined (PROTO-U10): the table records what the quarantined executions produced; it is not a Section 7 result and confers no runner-selection authority.

| Combination | Warm-ups (count) | Measured successes / 10 | Excluded (count) | Runner-caused failures (count) | Manual intervention (count) | Result |
|---|---|---|---|---|---|---|
| MQ1 × Android emulator | 1 (SUCCESS) | 10 / 10 | 0 | 0 | 0 | PASS |
| MQ1 × iOS Simulator | 1 (SUCCESS) | 10 / 10 | 0 | 0 | 0 | PASS |
| MQ2 × Android emulator | 1 (SUCCESS) | 10 / 10 | 0 | 0 | 0 | PASS |
| MQ2 × iOS Simulator | 1 (SUCCESS) | 10 / 10 | 0 | 0 | 0 | PASS |
| MQ3 × Android emulator | 1 (FAILURE, runner-caused, MC-07) | 0 / 10 | 0 | 10 measured (MQ3-AND-MEASURED-01 … -10) + 1 warm-up, all attributed to MC-07 (see Capability support) | 0 | FAIL |
| MQ3 × iOS Simulator | 1 (SUCCESS; the system "Open in OmniPizza?" prompt appeared once, in the warm-up, and was accepted through the runner; it did not reappear in the ten measured executions) | 10 / 10 | 0 | 0 | 0 | PASS |

No execution was excluded: the harness precheck (backend health, MQ3 seed and verification) succeeded before every execution (backend health answered on the first attempt every time; last-attempt latency at most 526 ms). Manual intervention is structurally impossible in the scripted scenarios and none occurred. Criterion 7.2.2 (10 of 10 for every combination) is therefore violated by MQ3 × Android emulator only.

### Failed steps in executions of any kind (criterion 7.2.3 input, generated)

| execution_id | kind | failed step | capabilities carried by the step | error (first line) |
|---|---|---|---|---|
| MQ3-AND-WARMUP-01 | WARMUP | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-01 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-02 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-03 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-04 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-05 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-06 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-07 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-08 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-09 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |
| MQ3-AND-MEASURED-10 | MEASURED | checkout screen visible (MC-06, MC-08) | MC-06, MC-08 | ExpectError: Expected element to be visible, but it was not |

All eleven failures are the same step of the same combination: after the runner opened the MQ3 deep link, the Checkout route rendered in its empty-cart state (`screen-checkout-empty`, `text-cart-empty` in every failure view tree) and the pre-declared `screen-checkout` state never appeared within 90 s, while the harness's cart re-read after each failure still returned the seeded line (pizza_id p01, quantity 2, size large; `harness.cart_after_failure` in each record). Criterion 7.2.3 (no mandatory capability blocked by a runner-caused failure in two or more executions of any kind) is therefore violated for MC-07.

## Capability support

HISTORICAL — quarantined (PROTO-U10): the support classification below was recorded on 2026-09-22 for the quarantined executions; it is a technical observation, not a Section 7 determination. The MC-07 observation on Android is exposed knowledge (PREQUALIFICATION_OUTCOME_EXPOSURE).

Rule (policy 7.2.1): a capability is supported on a platform when it was exercised in at least one successful measured execution on that platform and no runner-caused failure of that capability occurred in any measured execution on that platform. Counts of successful measured executions exercising each capability come from the step-based tally generated from the records (Android / iOS); the attribution of the eleven Android MQ3 failures is recorded by QUALIFIER-MOBILE-01 below.

| Capability | Android emulator (SUPPORTED / UNSUPPORTED) | iOS Simulator (SUPPORTED / UNSUPPORTED) | Runner-caused failures (count, execution ids) | Notes |
|---|---|---|---|---|
| MC-01 Install and launch | SUPPORTED (20 successful measured executions) | SUPPORTED (30) | 0 | install of the pinned build through the runner at every execution (MQ3 launches through the deep link) |
| MC-02 Locate by stable identifier | SUPPORTED (20) | SUPPORTED (30) | 0 | the app's testIDs resolved as resource-id on Android and as accessibility identifier on iOS in every execution |
| MC-03 Text entry | SUPPORTED (20) | SUPPORTED (20) | 0 | fill (tap, select-all chord, backspace, type) of the two login fields; the read-back diagnostic matched the credentials in all 40 executions; the select-all flakiness seen once in the first development run did not recur |
| MC-04 Tap / press native control | SUPPORTED (20) | SUPPORTED (30) | 0 | market selector, keyboard-dismissing tap, Sign In, product open, size control; on iOS also the system prompt's Open button (warm-up of MQ3) |
| MC-05 Scroll / swipe | SUPPORTED (10) | SUPPORTED (10) | 0 | `screen.swipe('up')` plus scroll-into-view of the last catalog entry (MQ2) |
| MC-06 Screen navigation and verification | SUPPORTED (20) | SUPPORTED (30) | 0 attributed (see note) | the eleven Android MQ3 failures occurred at the step labeled "checkout screen visible (MC-06, MC-08)"; QUALIFIER-MOBILE-01 attributes them to MC-07, not MC-06/MC-08: the runner did navigate to the deep link's route (the Checkout route rendered, in its empty state) and did read that state correctly, and the same navigation-and-verification operations succeeded in all 20 MQ1/MQ2 measured executions on the same platform; the target state was missing because the link's parameters were not delivered. Applying the step label strictly instead would additionally mark MC-06 and MC-08 as failing on Android and would not change the gate outcome. |
| MC-07 Deep link with parameters | **UNSUPPORTED** (0 successful; 11 runner-caused failures) | SUPPORTED (10) | 11 (MQ3-AND-WARMUP-01, MQ3-AND-MEASURED-01 … MQ3-AND-MEASURED-10) | Android: `device.openUrl` (mobilecli `device.url`) delivered the route (`checkout`) but not the query parameters (market, hydrateCart, accessToken), so the app opened Checkout unauthenticated with an empty cart while the server-side cart held the seeded line (verified before and re-read after every failure). Demonstrating artifacts: `output/MQ3-AND-*/failure.png`, `view-tree-failure.json` (`screen-checkout-empty`), `harness-precheck.json` (seed verified), `record.json` (`harness.cart_after_failure`), `runner.log` (the full URL passed to the device server), and the deep-link attribution experiment of the "Development runs" section (same URL through adb delivers every parameter). iOS: the same links, opened through the same API from a cold state, landed on the seeded Checkout state in 10 of 10 measured executions. |
| MC-08 Read UI state | SUPPORTED (20) | SUPPORTED (30) | 0 attributed (see MC-06) | element presence and text oracles (`text-estimated-total-value` `$15.99` → `$19.99`; `2x Margherita`; `$33.98`) verified through the runner |
| MC-09 App state reset between executions | SUPPORTED (20) | SUPPORTED (30) | 0 | uninstall (when installed), install of the pinned build, and verification through the runner before every execution (median reset 3.3–3.4 s on Android, 5.2–5.8 s on iOS) |
| MC-10 Artifact capture | SUPPORTED (20) | SUPPORTED (30) | 0 | runner log and screenshot (plus view tree) for every execution, including the failed ones |

Criterion 7.2.1 (100% support of MC-01 … MC-10 on both platforms) is therefore violated: MC-07 is unsupported on the Android emulator under Mobilewright 0.0.60 as pinned. Criterion 7.2.4 (no manual intervention) holds.

## Attribution records (excluded executions)

One row per excluded execution. An exclusion without a complete row is invalid and the execution counts as a failed measured execution. Attributed cause is never RUNNER.

| execution_id | combination | timestamp | failure description | attributed cause (INFRASTRUCTURE / SUT_INSTANCE / API_SEED / OPERATOR / OTHER) | demonstrating artifacts | recorded_by |
|---|---|---|---|---|---|---|
| (none) | — | — | No execution was excluded: no infrastructure, SUT-instance, API-seed, network, or operator failure occurred before any scenario started. Every failure of the gate (the eleven Android MQ3 executions) is runner-caused and is recorded above, never excluded. | — | — | QUALIFIER-MOBILE-01 |

## Secondary evidence — duration

HISTORICAL — quarantined (PROTO-U10).

| Combination | Median duration | IQR | Notes |
|---|---|---|---|
| MQ1 × Android emulator | 14.5 s | 0.8 s (Q1 14.3 s, Q3 15.1 s) | n = 10 successful measured executions; scenario time only (reset and MQ2 precondition excluded) |
| MQ2 × Android emulator | 9.0 s | 0.9 s (Q1 8.9 s, Q3 9.8 s) | n = 10 successful measured executions; scenario time only (reset and MQ2 precondition excluded) |
| MQ3 × Android emulator | — | — | n = 0 successful measured executions (all failed); the failed executions ran 95 s in total each (median), dominated by the 90 s wait for the terminal state |
| MQ1 × iOS Simulator | 55.1 s | 13.5 s (Q1 45.0 s, Q3 58.5 s) | n = 10 successful measured executions; scenario time only (reset and MQ2 precondition excluded) |
| MQ2 × iOS Simulator | 22.4 s | 5.5 s (Q1 19.8 s, Q3 25.3 s) | n = 10 successful measured executions; scenario time only (reset and MQ2 precondition excluded) |
| MQ3 × iOS Simulator | 21.0 s | 1.8 s (Q1 20.5 s, Q3 22.3 s) | n = 10 successful measured executions; scenario time only (reset and MQ2 precondition excluded) |

Duration is secondary evidence only (policy 7.4); it entered no criterion and cannot offset the failed criteria. Whole-execution medians including the reset (Android / iOS): MQ1 19.3 s / 66.6 s; MQ2 28.1 s / 80.8 s (its login precondition alone: 14.3 s / 49.9 s); MQ3 (iOS) 30.3 s.

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
| Mobilewright version | pinned 0.0.60 (npm `mobilewright`, integrity sha512-c+aIg0FtMI6226xoVwXiO8Guqk9v5rT81zohz2Rs4WuZEaOgJidHoX9yd5Sqjpx3nTVYfmkFtqHoMFKMGVOuCg==, source tag v0.0.60, commit 2046d2d95e7db6383183bb6b116f81b1236cae42, engines node >= 22.12.0). Observed (`output/environment/<platform>-runner-install.json`): mobilewright 0.0.60 with mobilecli 1.0.13 (driver-mobilecli 0.0.60, core 0.0.60, playwright 1.63.0), installed 2026-09-22 by `npm ci` from the committed lockfile with Node.js v22.23.2 / npm 10.9.8 on both hosts: Linux x86_64 (GitHub ubuntu-24.04 image 20260907.300.1) for Android and Darwin arm64 (GitHub macos-15 image 20260907.0337.1) for iOS; on-device agent DeviceKit 0.0.27 (`com.mobilenext.devicekit-iosUITests.xctrunner`) on the simulator. Pin and observed version match on both platforms. |
| Appium 3 version (fallback pin) | 3.7.0 (npm `appium`, source commit b67de03966155ff052076c11c1c8f20cc2ba9134); not installed; used only if the switch rule fires; Appium 2 never |
| Android emulator identity (device profile, OS image) | pinned: `system-images;android-35;google_apis;x86_64`, API 35, profile pixel_7, provisioned by ReactiveCircus/android-emulator-runner v2.38.0 at commit a421e43855164a8197daf9d8d40fe71c6996bb0d on a GitHub-hosted ubuntu-24.04 runner (image 20260907.300.1 or later, KVM enabled); environment_type EMULATED; observed (`output/environment/android-environment.json`, run 35763051534): serial emulator-5554, AVD eus-qualification-pixel7-api35, Android 15 (API 35), model sdk_gphone64_x86_64, build fingerprint google/sdk_gphone64_x86_64/emu64xa:15/AE3A.240806.043/12960925:userdebug/dev-keys, adb 1.0.41, screen 1080 × 2400, image ubuntu24 20260907.300.1; the emulator binary version string was not captured by the environment step (empty field) — the emulator-runner action at the pinned commit provisioned it |
| iOS Simulator identity (device, OS version) | pinned: iPhone 16, iOS 18.5 simulator runtime, Xcode 16.4 build 16F6 (selected with xcode-select) on a GitHub-hosted macos-15 runner (image 20260824.0482.1 or later that still ships them); environment_type SIMULATED; observed (`output/environment/ios-environment.json`, run 35767911878): iPhone 16, UDID F0E646EF-4792-4F36-B48B-EC89B3A6B73B, iOS 18.5 runtime build 22F77, Xcode 16.4 build 16F6, macOS 15.7.9, image macos15 20260907.0337.1 |
| Host platform | GitHub-hosted runners: ubuntu-24.04, x86_64 (Android); macos-15, arm64 (iOS); the runner image version is recorded per execution (`github.image_version`) |
| Date of first run | 2026-09-22 (Android: first execution MQ1-AND-WARMUP-01 at 17:50:47Z, last ended 18:17:40Z, run 35763051534; iOS: first execution MQ1-IOS-WARMUP-01 at 18:37:33Z, last ended 19:10:55Z, run 35767911878; both on the workflow revision of public main 03e5360 / 26907f5, canonical c5bb7b2 / ab27919, which carry the identical realization) |
| Instruction to execute (date, human source, relaying role) | SUPERSEDED (PROTO-U10). Recorded on 2026-09-22 as: MOBILE-QUALIFICATION-EXEC-AUTH-01 (MOBILE_QUALIFICATION_EXECUTION), 2026-09-22, issued by gilbertosanchez, relayed by ORCHESTRATOR to QUALIFIER-MOBILE-01 (manifests/mobile-qualification-execution-auth-v1.yaml). Corrected: no human issued that authorization; the text was a proposed draft relayed into the ORCHESTRATOR's working session and never approved (human corrective instruction of 2026-09-22, verbatim in manifests/mobile-qualification-authorization-correction-v1.yaml). Human source: none. The launch under prompt version qualifier-mobile-01-mobilewright-gate-v1 was therefore unauthorized; the prompt itself is unchanged. |

## Development runs (not gate executions)

Harness development on the operator workstation, mode DEVELOPMENT, output kept outside the repository, never counted toward N and never a warm-up. Recorded here for transparency; any runner-caused blocker of a mandatory capability observed in such a run is disclosed and escalated in qualification/unresolved.md for the human to decide whether it counts under criterion 7.2.3, never decided by this role alone.

| Date | Platform (local identity, differences from the pins) | Scenarios | Outcome | Notes |
|---|---|---|---|---|
| 2026-09-22 | Android emulator on the operator workstation (AVD Pixel_API35_Test: system-images;android-35;google_apis;x86_64, API 35, hardware profile pixel_8 instead of the pinned pixel_7; emulator 36.4.9.0; Intel macOS host under a 1-minute load average of 70-270 from unrelated applications) | MQ1 (N = 1, no warm-up), four attempts while the harness was being written | No attempt reached the terminal state. Attempts 1-2 failed in the harness (runner device id must be the AVD name, not the adb serial; the runner's per-call RPC timeout of 30 s is shorter than the 81 MB install on the emulator) and were fixed in the harness. Attempts 3-4 failed at "login screen visible": the app had rendered its login screen (failure screenshots), but a system dialog ("Pixel Launcher isn't responding", "System UI isn't responding") from the starved emulator covered it, so the accessibility hierarchy held only the dialog. | Host resource exhaustion of the operator workstation; not a runner-caused failure and not a SUT behavior. The same runner readiness probe, reset (uninstall + install through the runner), and app launch succeeded on the emulator before the dialog appeared. Never counted. |
| 2026-09-22 | iOS Simulator on the operator workstation (iPhone 16, iOS 18.2 runtime 22C150 instead of the pinned iOS 18.5; Xcode 26.5 build 17F42 instead of the pinned 16.4; same overloaded host) | MQ1 (N = 1, no warm-up), three attempts | Attempt 1 failed in the script (`simctl list` accepts one type filter; fixed). Attempt 2 failed at connection: the runner's driver treats the non-zero exit of its own `mobilecli agent status` as an error instead of installing its on-device agent; the agent (DeviceKit 0.0.27, bundle com.mobilenext.devicekit-iosUITests.xctrunner) was then installed as a preparation step of the gate script (3 min 37 s). Attempt 3: connection, MC-09 reset (uninstall, install of the pinned .zip through the runner, verification) succeeded; "launch the app" failed with "timed out waiting for WebDriverAgent to be ready" when the runner started its agent on the starved host. | The agent-start timeout occurred on a host with a 1-minute load average above 100 and on a non-pinned runtime; it is disclosed here and re-examined on the pinned substrate (see the GitHub Actions DEVELOPMENT run below). Never counted. |
| 2026-09-22 | GitHub Actions, mode DEVELOPMENT, run 35758030920 (workflow revision of public main f93be54): the pinned substrates — ubuntu-24.04 image 20260907.300.1 with the emulator-runner action (API 35, google_apis, x86_64, pixel_7) and macos-15 image 20260907.0337.1 with Xcode 16.4 and the iOS 18.5 iPhone 16 simulator | MQ1, MQ2, MQ3 on both platforms, N = 1, no warm-up (6 executions) | Environment, pinned-build digests, runner install (mobilewright 0.0.60, mobilecli 1.0.13), readiness probe, MC-09 reset (uninstall + install through the runner) and app launch succeeded on both platforms. All six executions then failed: Android MQ1/MQ2 at "catalog screen visible" — both fields were filled but the software keyboard covered `btn-login`, so the tap landed on the keyboard (failure screenshot); iOS MQ1 at "enter password" and MQ2 at "enter username" — the keyboard raised after the username field covered the password field, the tap did not move focus, and the runner's clear step (select-all chord + backspace) then wiped the username / removed a single character ("standard_use"), so its clear verification failed; Android MQ3 at "checkout screen visible" — the app opened Checkout with an empty cart although the harness had seeded and verified the cart; iOS MQ3 at "checkout screen visible" — the system prompt "Open in OmniPizza?" was showing. | Realization refined before the first gate run (this table's date): password field first (while the keyboard is closed), then the username, a read-back of both fields for diagnosis, a tap on `text-welcome-title` to close the keyboard before Sign In; on iOS the system prompt is accepted through the runner; Android failure artifacts now include the activity-start intent lines. These are realization corrections (keyboard occlusion, platform prompt), not runner capabilities. The iOS select-all flakiness and the Android empty-cart result are left for the gate to measure; see the next row for the attribution experiment. Never counted. |
| 2026-09-22 | Android emulator on the operator workstation (same local identity as above), deep-link attribution experiment, no scenario executed | `omnipizza://pizza-builder?market=US&accessToken=<jwt>&pizzaId=p12&size=large` sent once through the runner's device server (`mobilecli url`, the mechanism behind `device.openUrl`) and once through `adb shell am start -a android.intent.action.VIEW -d '<url>'` with the URL quoted | Through the runner: the app opened the product screen route with an empty customizer (route delivered, no product, no size, no price). Through adb with the URL quoted: the product screen showed BBQ Chicken with Large selected and estimated total $19.99, i.e. every parameter delivered. The activity-manager log redacts query strings ("dat=omnipizza://checkout/..."), so it cannot show the delivered data; this UI-level comparison can. | Consistent with the CI MQ3 result (Checkout opened for market US with an empty cart): the runner's URL opening on Android delivers the path but drops the query parameters after the first `&` (or all of them), which is a runner-caused failure of MC-07 (deep link carrying parameters). Recorded as attribution support for the gate; no harness workaround is applied because the gate measures the runner as pinned. Never counted. |
| 2026-09-22 | GitHub Actions, mode DEVELOPMENT, run 35761803766 (workflow revision of public main 03e5360, the revised realization): ubuntu-24.04 image 20260920.314.1, emulator AVD eus-qualification-pixel7-api35 (API 35, Android 15, sdk_gphone64_x86_64); macos-15 image 20260907.0337.1, Xcode 16.4 build 16F6, iPhone 16 on iOS 18.5 (22F77); mobilewright 0.0.60, mobilecli 1.0.13, agent DeviceKit 0.0.27 | MQ1, MQ2, MQ3 on both platforms, N = 1, no warm-up (6 executions) | iOS: MQ1 SUCCESS (scenario 90.8 s), MQ2 SUCCESS (26.4 s), MQ3 SUCCESS (15.3 s; the system prompt appeared and was accepted through the runner; the seeded line was rendered, so the deep link's parameters were delivered on iOS). Android: MQ1 SUCCESS (30.7 s), MQ2 SUCCESS (12.9 s), MQ3 FAILURE at "checkout screen visible": Checkout opened with the empty-cart state (`screen-checkout-empty`) while the cart re-read after the failure still held the seeded line. The read-back of the entered fields matched the credentials on both platforms. | The harness and the realization are validated on both pinned substrates; the realization is frozen from this point for the gate. The Android MQ3 outcome is left for the gate to measure. Never counted. |

## Decision record

### Validity

**SUPERSEDED — NO AUTHORITY (PROTO-U10, 2026-09-22).** The table "Recorded decision (historical)" below is kept verbatim as recorded on 2026-09-22 before the correction. It was derived exclusively from executions whose authorization was invalid; it is not a Section 7 gate result and did not legitimately trigger Section 8. The current valid decision state is:

| Field | Current valid value |
|---|---|
| Date of the valid decision | none (no protocol-valid gate has been executed) |
| Gate result (PASS / FAIL) | none — INVALID_REQUIRES_VALID_REEXECUTION |
| Decision (one of: Mobilewright, Appium 3) | none (runner decision: none, policy Section 11 vocabulary); primary candidate Mobilewright 0.0.60, fallback Appium 3.7.0 |
| Appium 3 compatibility smoke | NOT AUTHORIZED / NOT_STARTED |
| What a valid re-execution requires | a NEW explicit human authorization issued after the correction (new id; MOBILE-QUALIFICATION-EXEC-AUTH-01 retired); the same frozen policy, Mobilewright 0.0.60, the same pinned build, the same MQ definitions, N = 10, acceptance criteria and attribution rules; the realization/harness hashes recorded in the correction record if the implementation is to be frozen for the repeat |
| Recorded by | QUALIFIER-MOBILE-01, on the human corrective instruction (PROTO-U10) |

### Recorded decision (historical; superseded)

| Field | Value |
|---|---|
| Date | 2026-09-22 |
| Gate result (PASS / FAIL) | FAIL |
| Failed criteria and capabilities (if FAIL) | 7.2.1 — capability MC-07 (deep link carrying parameters) unsupported on the Android emulator (0 successful measured executions, 11 runner-caused failures); 7.2.2 — MQ3 × Android emulator 0 of 10 successful measured executions (the other five combinations 10 of 10); 7.2.3 — the same mandatory capability (MC-07) blocked by a runner-caused failure in 11 executions of any kind (1 warm-up + 10 measured). 7.2.4 holds (no manual intervention). |
| Decision (one of: Mobilewright, Appium 3) | Appium 3 (pinned 3.7.0; manifests/toolchain-manifest.yaml `tools.mobile_fallback.pinned_candidate_version`) |
| Rationale | protocol/mobile-runner-policy-v1.md, Section 8: the gate failed because a required capability (MC-07) is unsupported under Mobilewright 0.0.60 on one of the two mandatory platforms and criterion 7.2.3 is violated; the switch to Appium 3 is therefore mandatory. The study uses one mobile runner for all ecosystems (Section 1), so Mobilewright's full support on iOS and its support of MC-01 … MC-06 and MC-08 … MC-10 on Android do not qualify it. Duration (secondary evidence) plays no role. The switch changes the study's tooling only. Appium 2 is never introduced. The per-SUT compatibility smoke (Section 9) then applies to Appium 3 and requires a separate explicit human authorization. |
| Recorded by | QUALIFIER-MOBILE-01, under prompt version qualifier-mobile-01-mobilewright-gate-v1, instruction MOBILE-QUALIFICATION-EXEC-AUTH-01 |

The decision is also recorded in manifests/toolchain-manifest.yaml and in the change log per protocol/change-control-v1.md (protocol/mobile-runner-policy-v1.md, Section 8), transcribed by the ORCHESTRATOR from this record. If the runner is Appium 3, the compatibility smoke (qualification/compatibility-smoke/) is executed with Appium 3. Appium 2 is never introduced.

## Authorization-provenance correction and quarantine (PROTO-U10)

| Item | Value |
|---|---|
| Correction record | manifests/mobile-qualification-authorization-correction-v1.yaml (ORCHESTRATOR); escalation rows protocol/unresolved.md PROTO-U10 and qualification/unresolved.md QUAL-U01 |
| Authorization provenance | INVALID — the executions ran on a relayed text that no human had issued (Section 2 prerequisite unmet) |
| Affected runs | qualification-labelled 35763051534 (Android) and 35767911878 (iOS): HISTORICAL_UNAUTHORIZED_EXECUTION; development runs 35758030920 and 35761803766: never counted, preserved; failed-closed dispatches 35756760994 and 35763331095: no execution, preserved |
| Preserved artifacts | `output/` (433 files, unchanged; per-file SHA-256 in the two import records; `output/QUARANTINE-RECORD.yaml` classifies all 66 executions) — nothing deleted or rewritten |
| Superseded decisions | the FAIL result and the Appium 3 selection of 2026-09-22 (manifests/toolchain-manifest.yaml `mobile_runner_selection.superseded_2026_09_22`; protocol/CHANGELOG.md supersession row) |
| Switch rule | Section 8 not legitimately triggered; the observed technical failure does not independently authorize the switch; no Appium 3 compatibility smoke may proceed |
| PREQUALIFICATION_OUTCOME_EXPOSURE | true — the Android MQ3 / MC-07 behavior of Mobilewright 0.0.60 (route delivered, query parameters not) was observed on 2026-09-22 and cannot be unobserved; from the correction forward the qualification SUT, the Mobilewright version, the qualification build, MQ1–MQ3, MC-01…MC-10, N, the pass criteria, the attribution rules and the fallback rule may not change in response to it |
| Realization and harness hashes (SHA-256 at the correction) | run-gate-android.sh a10c7b9f…7a4e; run-gate-ios.sh 708f2779…0879; gate-common.sh 1580c5c2…f59c; harness/execute.mjs da67f010…6e6a; harness/run-gate.mjs f9279631…b224; harness/backend.mjs 6e0af303…a9bd; harness/package.json f2b4f936…d390; harness/package-lock.json 5d235b55…08ef; harness/import-artifacts.mjs 6b28f0b6…1cdf; harness/summarize-results.mjs d6b56464…a1dc; this README's "Scenario realization" section f79acf63…9018 (full values in the correction record) |
| Commits used by the quarantined runs | Android run: canonical c5bb7b2 (public 03e5360); iOS run: canonical ab27919 (public 26907f5); realization identical in both (execute.mjs, both entry scripts, backend, lockfile, and the realization section byte-identical); only gate-common.sh differs (bash 3.2 portability idiom, no scenario or runner-call change) |
| Realization changes after outcome exposure (reported, not classified) | c5bb7b2 (after DEVELOPMENT run 35758030920, before any qualification-labelled run): login steps reordered around the keyboard, read-back diagnostic, iOS system-prompt acceptance, intent-log capture — the deep-link mechanism stayed `device.openUrl`, no parameter-delivery workaround; ab27919: shell portability only; after the Android failures: none |
| Outcome-responsive repair | prohibited and not performed: no substitution of `adb shell am start` or any other mechanism for the runner's own deep-link API |

## Local development preflight (LOCAL_DEVELOPMENT_PREFLIGHT; classification only — not executed)

The human research lead's intended next step before any formal gate was a local preflight. This section prepares only its classification; executing it requires a separate explicit human instruction.

| Item | Value |
|---|---|
| Class | LOCAL_DEVELOPMENT_PREFLIGHT — NON_QUALIFICATION, NON_MEASURED, NOT PART OF N, NOT PASS/FAIL EVIDENCE |
| Possible environments | Android physical device Samsung Galaxy Z Flip 6 (not a pinned identity; operability only); Android emulator (the pinned `system-images;android-35;google_apis;x86_64` or the closest locally available API 35 image); iOS Xcode Simulator on the operator's Mac |
| May verify | installation, connection, selectors, navigation, reset, screenshots, deep links, script operability (the gate scripts' DEVELOPMENT mode, output outside the repository) |
| Must not | change the frozen qualification criteria; redesign MQ3 to evade the known MC-07 behavior (PREQUALIFICATION_OUTCOME_EXPOSURE); be counted, reported as pass/fail evidence, or placed under `output/` |
| Records | summarized in "Development runs" above when executed; never gate executions |

## Warning

Do not execute qualification until explicitly instructed and until protocol/mobile-runner-policy-v1.md is frozen. Do not fill any result, attribution, or decision field before a run has actually occurred. Do not use anything recorded here as evidence about any SUT.
