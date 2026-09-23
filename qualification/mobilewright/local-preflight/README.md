# Local development preflight (LOCAL_DEVELOPMENT_PREFLIGHT)

| Field | Value |
|---|---|
| Workspace | qualification/mobilewright/local-preflight/ (QUALIFIER-MOBILE-01; isolated from `../output/`, which holds the quarantined qualification-labelled executions) |
| Record class of everything here | LOCAL_DEVELOPMENT_PREFLIGHT — `qualification_evidence: false`, `measured_experiment: false`, `counts_toward_N: false`; NON_QUALIFICATION, NON_MEASURED, NOT_PART_OF_N, NOT_A_WARMUP, NOT_PASS_FAIL_EVIDENCE, NOT_RUNNER_SELECTION_EVIDENCE, NOT_E03_DATA |
| Instruction | LOCAL DEVELOPMENT PREFLIGHT instruction of the human research lead, 2026-09-22, entered directly in the ORCHESTRATOR session (verbatim, with its SHA-256, in manifests/mobile-qualification-implementation-lock-v1.yaml) |
| Implementation baseline | manifests/mobile-qualification-implementation-lock-v1.yaml (MOBILE-QUALIFICATION-IMPLEMENTATION-LOCK-01): every locked artifact recomputed at its locked hash before and after the executions; nothing under `../` was edited |
| Executed | 2026-09-22 local (2026-09-23 01:55–02:03 UTC), on the operator's Mac (MacBookPro16,2, x86_64, macOS 26.5.2) |
| Android | **COMPLETE** — Samsung Galaxy Z Flip 6 (physical device), one execution of each of MQ1, MQ2, MQ3: `android-zflip6/` |
| iOS | **BLOCKED** — host simulator service unresponsive (HOST_SIMULATOR_SERVICE_UNRESPONSIVE); no scenario started: `ios-simulator/` |
| Runner | Mobilewright 0.0.60 exactly as pinned (mobilecli 1.0.13, driver-mobilecli 0.0.60, core 0.0.60, playwright 1.63.0), installed by `npm ci` from the locked lockfile |
| Build | OmniPizza release v1.1.8, `omnipizza-release.apk`, sha256 1059e946…cda6a4 verified before use (`android-zflip6/environment/android-build-verification.json`); the iOS build was not downloaded because no iOS execution started |

These records are observations from a diagnostic preflight. They are not the qualification gate of protocol/mobile-runner-policy-v1.md, not warm-ups, not measured executions, not pass/fail evidence, not runner-selection evidence, and not E03 data; they may not be used in H2 or any campaign analysis; they are not evidence about any system under test. The Z Flip 6 is not the frozen Android qualification substrate (API 35 x86_64 emulator, profile pixel_7); a physical-device outcome supports no inference about the correctness of the quarantined emulator observation of 2026-09-22 (instruction, section 15).

## Layout

| Path | Content |
|---|---|
| `android-zflip6/PREFLIGHT-SUMMARY.yaml` | Platform summary: observed device, runner, build verification, readiness, the three executions, driver provenance, harness-unchanged verification |
| `android-zflip6/<harness execution id>/preflight-record.yaml` | Sidecar record per execution with the mandated classification fields and the observation (terminal UI state; for MQ3 the deep link supplied, the runner API used, route delivery, whether the parameters were observed in the UI) |
| `android-zflip6/<harness execution id>/` (other files) | The locked harness's own output for that execution, imported unchanged except for the redactions in `IMPORT-RECORD.yaml`: `record.json`, `spec.json`, `runner.log`, `harness-precheck.json`, `terminal.png` + `view-tree-terminal.json` (success) or `failure.png` + `view-tree-failure.json` + `device-log-failure.txt` (failure) |
| `android-zflip6/environment/` | Build verification, runner install, environment, catalog snapshot, runner readiness (probe log, screenshot, device entry) |
| `android-zflip6/summary-android.json`, `execution-log-android.{jsonl,csv}` | The harness's own per-platform summary and execution log |
| `android-zflip6/driver/` | The scratchpad driver that ran the locked harness against the physical device (verbatim copy; sha256 in the summary), its log, start/finish timestamps |
| `android-zflip6/IMPORT-RECORD.yaml`, `ios-simulator/IMPORT-RECORD.yaml` | Per file: raw sha256 (scratchpad original, untouched), imported sha256, transformation (UNCHANGED / DEVICE_IDENTIFIER_REDACTED / PRIVATE_PATH_SCRUBBED / TOKEN_FRAGMENT_REDACTED) |
| `ios-simulator/PREFLIGHT-SUMMARY.yaml` | The BLOCKED record: observed environment, the read-only probes that timed out, what was not done, retry policy |
| `ios-simulator/probes/` | Probe outputs (simctl listing timeouts, process states, runtime volumes, the runner device server's device listing, Xcode/macOS versions) |

## Harness labels that are wrong for this preflight by construction (disclosed, not edited)

The locked harness (`../harness/run-gate.mjs`, `../gate-common.sh`) was used unchanged, so its own files carry labels fixed in code: `record_class: DEVELOPMENT` (the library's non-qualification mode), execution ids and `kind: MEASURED` (the harness's word for a non-warm-up execution), combination `"… × Android emulator"` and `environment_type: EMULATED` (fixed for any non-iOS platform), and `record_class: QUALIFICATION_ENVIRONMENT` in the build-verification record. None of these is true of this preflight: the executions are LOCAL_DEVELOPMENT_PREFLIGHT diagnostics on a physical device (environment_type OTHER per protocol/study-design-v1.md, section 10). The sidecar records and summaries carry the true classification; the harness files were not edited because editing them would rewrite the harness's own output. Whether the human wants the mandated fields injected into the harness files at import is a decision listed in the return package.

## Android Z Flip 6 — observations (one execution per scenario, no retry)

| Scenario | Outcome as recorded by the harness | Observation |
|---|---|---|
| MQ1 | SUCCESS (scenario 46.0 s, total 70.4 s) | Runner connected on the first attempt; MC-09 reset (uninstall, install of the pinned APK through the runner, verification) worked; login reached the catalog screen with the bottom navigation visible (`terminal.png`) |
| MQ2 | SUCCESS (scenario 31.7 s, total 99.8 s) | After the login precondition, the catalog scrolled to the target product, the product screen opened, the estimated total changed from $15.99 to $19.99 after selecting Large (`terminal.png`) |
| MQ3 | FAILURE at "checkout screen visible" (total 122.9 s) | API seed applied and verified before the first runner action; the locked deep link `omnipizza://checkout?market=US&hydrateCart=true&accessToken=<token>` was passed to the runner's `device.openUrl` (device-server RPC `device.url`, `runner.log`); the device log shows the resulting `android.intent.action.VIEW` activity start with `dat=omnipizza://checkout/...` (Android redacts the query string). **Route delivered**: the app opened the Checkout route from the cold state. **Query parameters not observed in the UI**: the Checkout opened in its empty-cart state (`screen-checkout-empty`, "Your cart is empty."; `failure.png`) although the server-side cart still held the seeded line after the failure; delivery of the parameters can be neither confirmed nor excluded from the redacted device log. Same terminal UI state as the quarantined emulator executions; no inference about them is drawn (section 15). |

`OPTIONAL_EXTERNAL_DIAGNOSTIC_AVAILABLE`: an adb-level `android.intent.action.VIEW` start of the identical URI outside the runner would show whether the app hydrates the cart when the parameters do arrive. Not performed inside this preflight (instruction, section 11); adb was used only for device properties (driver) and for the locked failure-time log capture (harness).

Android substrate differences from the pin: physical arm64-v8a Samsung device on Android 16 / API 36 (pinned: x86_64 emulator image API 35, pixel_7, ubuntu-24.04); Node.js v23.6.1 on macOS 26.5.2 Intel (pinned CI: Node.js 22, Linux x86_64); 1-minute load average 770–920 on the host throughout. No result is invalid because of these differences, and none is qualification evidence.

How the locked harness was driven: `../run-gate-android.sh` is emulator-only by construction (it fails closed on any adb serial that does not start with `emulator-` and derives the runner device id from `ro.boot.qemu.avd_name`), so it cannot drive a physical device. A driver kept outside the repository (`android-zflip6/driver/preflight-android-driver.sh`) sourced the locked `../gate-common.sh` unchanged (mode DEVELOPMENT; pinned-build download and digest verification; runner install exactly as pinned; environment record) and invoked the locked `../harness/run-gate.mjs` unchanged with the device's adb serial as the runner device id (the runner's device server identifies a real Android device by that serial, `type: real`). Whether this counts as an implementation change for the purpose of the future valid gate is a human decision (return package); the gate itself will still use `run-gate-android.sh` on the frozen emulator substrate.

## iOS Simulator — BLOCKED

No scenario started. Every `xcrun simctl list` probe on the operator's Mac timed out (300 s, 300 s, 900 s, 900 s, 300 s; a 90 s probe only returned after 1985 s), the runner's own `mobilecli agent status` probe timed out (120 s), and the killed simctl processes stayed in uninterruptible kernel states, while the host ran under a 1-minute load average of 770–920 from unrelated applications. The locked `../run-gate-ios.sh` calls simctl before the first runner action (device lookup, boot, bootstatus, environment record, agent status/install), so it would block before any scenario. The runner's device server did list the booted simulator (iPhone 16, iOS 18.2, `ios-simulator/probes/mobilecli-devices.json`). Observed environment: Xcode 26.5 build 17F42; macOS 26.5.2; x86_64; the only iOS 18 runtime installed is 18.2 (22C150) — iOS 18.5 (22F77) is not installed and was not installed. Nothing was restarted, killed, installed, or edited. A later re-attempt under the same instruction, once the host simulator service responds, is a separately recorded pre-scenario infrastructure retry (instruction, section 9), left to the human.

## Redactions and hygiene

Device identifiers are redacted at import (`<android-serial-redacted>`, `usb:<port-redacted>`, `E83DB502-<udid-redacted>`); one truncated bearer-token fragment in the MQ3 runner log was replaced by the harness convention (first 12 characters + `<redacted-token>`); no private absolute path, secret, or attribution term is present. Raw originals stay outside the repository (session scratchpad); `IMPORT-RECORD.yaml` makes every imported file verifiable against its raw sha256.
