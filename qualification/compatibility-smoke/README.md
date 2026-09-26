# Per-SUT Compatibility Smoke

## Status

PREPARED, NOT EXECUTED; RE-LOCKED UNDER POLICY V2 (2026-09-26). The Appium 3 compatibility smoke of SUT-02 (Android and iOS) was first prepared and locked on 2026-09-24 under protocol/mobile-runner-policy-v1.md (manifests/compatibility-smoke-implementation-lock-v1.yaml, now historical and never the execution baseline). After the post-data amendment resolving PROTO-U17 (protocol/mobile-runner-policy-v2.md, FROZEN-PRE-DATA; human approval 2026-09-25), the result-writing logic was adapted to the v2 attribution rules, and the implementation was re-locked before any execution (manifests/compatibility-smoke-implementation-lock-v2.yaml, the active baseline). Its execution authorization APPIUM3-COMPAT-SMOKE-AUTH-01 is PREPARED and NOT ISSUED (manifests/compatibility-smoke-execution-auth-v1-prepared.yaml). No smoke has been executed, and no result field below has been filled. Nothing recorded here is evidence about any system under test (SUT). Governing policy: protocol/mobile-runner-policy-v2.md, Section 9 (FROZEN-PRE-DATA; v1 AMENDED; this line read "DRAFT" in the template of 2026-09-16, before the protocol freeze). Owner: QUALIFIER-MOBILE-01 (protocol/agent-governance-v2.md, section 3.4).

## Purpose

After the study mobile runner is selected (Mobilewright by passing the qualification gate, or Appium 3 by the switch rule) and after E01 has verified which ecosystems have an Android or iOS surface, each mobile-capable ecosystem receives one lightweight compatibility smoke per platform before it participates in E06, E07, or any other campaign exercising its Android Native or iOS Native modality. The smoke establishes only that the selected runner can drive that ecosystem's pinned mobile build. It is not Mobilewright-versus-Appium benchmarking, records no duration comparison, and produces no evidence about any ecosystem.

## Scope per ecosystem × platform

One execution from a clean state that: installs and launches the pinned build (MC-01); locates one element by stable identifier (MC-02); performs one navigation (MC-06); performs one native control interaction (MC-04); reads one UI state (MC-08); captures artifacts (MC-10). One successful execution passes the smoke for that ecosystem × platform.

Current scope (human instruction of 2026-09-24, PREPARE AND FREEZE APPIUM 3 COMPATIBILITY SMOKE): SUT-02 × Android × Appium 3 and SUT-02 × iOS × Appium 3, required before the E03-resetability conditions E03-CS001-SUT02-ANDROID and E03-CS001-SUT02-IOS. The two results are independent: an Android PASS never implies an iOS PASS, nor the reverse. Other mobile-capable ecosystems receive their own smokes before a campaign requires them. The scope rests on the completed E01 result: SUT-02 Android Native and iOS Native are CONFIRMED with effective confirmed score 3 in derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json, and the SUT-02 auditor recorded both surfaces CONFIRMED (audits/SUT-02-saucelabs/audit.md, section 2, 2026-09-17).

## Prerequisites

- [x] The study mobile runner has been selected and recorded in manifests/toolchain-manifest.yaml and in the change log (Appium 3, pinned 3.7.0, by the frozen section 8 switch; 2026-09-24)
- [x] E01 has verified the mobile surfaces of SUT-02 (adjudicated matrix and audit section 2; the `presence` fields of manifests/sut-manifest.yaml still read UNCONFIRMED because the post-E01 transcription of manifests/README.md, provenance-sequence step 3, has not been performed for any SUT; protocol/unresolved.md PROTO-U16)
- [x] The mobile builds of SUT-02 are pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml; the exact release artifacts and their SHA-256 are recorded in manifests/compatibility-smoke-implementation-lock-v2.yaml
- [x] The attribution rules are frozen: protocol/mobile-runner-policy-v2.md, Section 9 (PROTO-U17 resolved; decided before any smoke outcome existed)
- [ ] Explicit instruction to execute the smoke, issued by a human and relayed by the ORCHESTRATOR, has been received and is recorded below — NOT YET (authorization PREPARED, NOT ISSUED)

| Field | Value |
|---|---|
| Selected runner and version | Appium 3, pinned 3.7.0 (npm appium@3.7.0); drivers appium-uiautomator2-driver@8.7.0 (Android) and appium-xcuitest-driver@12.13.2 (iOS); Node.js 22.23.2; no client library (the harness speaks the W3C WebDriver protocol). Pins only: nothing has been installed for the study |
| Android emulator identity | system-images;android-35;google_apis;x86_64, API 35, profile pixel_7, on the GitHub-hosted ubuntu-24.04 runner through the pinned emulator-runner action (manifests/toolchain-manifest.yaml, environments.android_emulator); EMULATED |
| iOS Simulator identity | iPhone 16, iOS 18.5 runtime, Xcode 16.4 build 16F6, on the GitHub-hosted macos-15 runner (manifests/toolchain-manifest.yaml, environments.ios_simulator); SIMULATED |
| Host platform | GitHub-hosted runners: ubuntu-24.04 (Android, x86_64), macos-15 (iOS, arm64); the image version is recorded per execution |
| Instruction to execute (date, human source, relaying role) | null / TBD (APPIUM3-COMPAT-SMOKE-AUTH-01 is PREPARED, NOT ISSUED) |

## Concrete realization (recorded before any execution)

Recorded by QUALIFIER-MOBILE-01 on 2026-09-24 from static evidence only, before any execution: the pinned release artifacts (inspected, never installed or launched), the SUT-02 source at the pinned commits (Android 36b012eecdf6a2b488b9504e16b3d0c3ca9a0e7b; iOS tag object 031358f56903742103a02d086f8af76735bb31a7, commit ede6fa4b7f57a75bc31f626b6ca531339e83d5c0), and the vendors' own UI tests at those commits. It is implemented verbatim by `harness/smoke.mjs` (constant `REALIZATION`) and is identical for any execution under the authorization. No locator, step, or expected state is changed after an execution result is seen. Timeouts are identical for both platforms except the session start: screen arrival 90 s; other element look-ups and state reads 30 s (polling every 1 s); Appium server readiness 120 s; harness watchdog 45 min; job limit 60 min.

| Item | SUT-02 × Android × Appium 3 | SUT-02 × iOS × Appium 3 |
|---|---|---|
| Pinned build consumed | `mda-2.2.0-25.apk` (release 2.2.0), 17931946 bytes, SHA-256 318ef64bdcaff18e576d962ab1f557e0a2683b9b5210a6bb6b25cb0caeef62b4 (computed from the download of 2026-09-24; the release record carries no publisher digest for this asset) | `SauceLabs-Demo-App.Simulator.zip` (release 2.2.2), SHA-256 96b08d5ac74dd817d95fbd8332ae9385bb076af38d56d13d8465345cb1797139 (equal to the release record's published digest); the harness installs the unpacked `Payload/My Demo App.app` |
| Application identity | package `com.saucelabs.mydemoapp.android`, versionName 2.2.0, versionCode 25, minSdk 21, targetSdk 31 | bundle `com.saucelabs.mydemo.app.ios`, version 2.2.2 (build 1), CFBundleSupportedPlatforms iPhoneSimulator, arm64 and x86_64 simulator slices, minimum iOS 16.6 |
| Clean-start procedure | freshly created AVD; digest verified before any runner action; `adb uninstall com.saucelabs.mydemoapp.android` before the session (no-op when absent); the runner installs the pinned APK at session start | fresh simulator on a fresh runner; digest and bundle identity verified before any runner action; `xcrun simctl uninstall <udid> com.saucelabs.mydemo.app.ios` before the session (no-op when absent); the runner installs the pinned app at session start (`appium:enforceAppInstall` true) |
| Launch procedure (MC-01) | one Appium session: `appium:automationName` UiAutomator2, `appium:app` = the verified APK, `appium:udid` = the emulator serial, `appium:appPackage` com.saucelabs.mydemoapp.android, `appium:appActivity` com.saucelabs.mydemoapp.android.view.activities.SplashActivity, `appium:appWaitActivity` com.saucelabs.mydemoapp.android.view.activities.MainActivity, `appium:appWaitDuration` 60000, `appium:autoGrantPermissions` true, `appium:disableWindowAnimation` true, `appium:androidInstallTimeout` 300000, `appium:uiautomator2ServerInstallTimeout` 120000, `appium:uiautomator2ServerLaunchTimeout` 120000, `appium:adbExecTimeout` 120000, `appium:newCommandTimeout` 300; session start limit 600 s | one Appium session: `appium:automationName` XCUITest, `appium:app` = the verified `.app`, `appium:udid` = the simulator selected by explicit identity (the single available iPhone 16 with the iOS 18.5 runtime), `appium:platformVersion` 18.5, `appium:deviceName` iPhone 16, `appium:bundleId` com.saucelabs.mydemo.app.ios, `appium:enforceAppInstall` true, `appium:simulatorStartupTimeout` 600000, `appium:wdaLaunchTimeout` 600000, `appium:wdaConnectionTimeout` 600000, `appium:showXcodeLog` true, `appium:newCommandTimeout` 300; session start limit 1200 s |
| Stable identifier located (MC-02) | resource-id `com.saucelabs.mydemoapp.android:id/productRV` (the catalog list) present and displayed | accessibility identifier `Catalog-screen` (the catalog screen) present and displayed |
| Navigation (MC-06) | tap the catalog entry located by `new UiSelector().resourceId("com.saucelabs.mydemoapp.android:id/titleTV").text("Sauce Labs Backpack")`; arrival: `com.saucelabs.mydemoapp.android:id/productTV` has text `Sauce Labs Backpack` and `com.saucelabs.mydemoapp.android:id/plusIV` is present | tap the first static text whose identifier is `Product Name` (the name label of the first catalog cell; the catalog is sorted by name ascending); arrival: accessibility identifier `ProductDetails-screen` present, containing a static text labelled `Sauce Labs Backpack - Black` |
| Native control interaction (MC-04) | tap `com.saucelabs.mydemoapp.android:id/plusIV` (content description "Increase item quantity") once | tap the button `AddPlus Icons` (its accessibility name, from the button image) once |
| UI state read (MC-08) | text of `com.saucelabs.mydemoapp.android:id/noTV`: `1` before the tap, `2` after it | label of the static text inside `ProductDetails-screen` that shows the quantity: `1` before the tap, `2` after it (the label has no accessibility identifier; it is located by its value, as the vendor's own UI tests do) |
| Expected final state | product detail of `Sauce Labs Backpack` with `noTV` text `2` | `ProductDetails-screen` of `Sauce Labs Backpack - Black` with the quantity label `2` |
| Artifacts (MC-10) | `terminal.png` and `source-terminal.xml` (or `failure.png` and `source-failure.xml`), `record.json`, `harness.log`, `appium-server.log`, `environment/` (build verification, toolchain install, device) | same set |
| Static evidence basis | `ProductDetailFragment.java` (`int cartNo = 1`; `plusIV` adds 1 and sets `noTV`), `fragment_product_detail.xml`, `fragment_product_catalog.xml`, `ProductsAdapter.java` (title text), the vendor Espresso test `DashboardToCheckout.java` (first catalog item `Sauce Labs Backpack`, `plusIV`); `MainActivity.java` (the startup permission request is commented out) | `ProductPageDetailViewController.swift` (`productQuantity = 1`; `addButton` adds 1 and sets the count label), `CatalogViewController.swift` (name-ascending sort), `TabBar.storyboard` (identifiers `Catalog-screen`, `Product Name`, `ProductItem`, `ProductDetails-screen`; button image `AddPlus Icons`), `Localizable.strings` (product names), the vendor UI tests `ProductDetailsTest.swift` and `PageObject.swift` |

## Implementation (authored before any execution)

| Path | Role |
|---|---|
| `run-smoke-android.sh`, `run-smoke-ios.sh` | Platform entry points of the dispatch-only workflow `.github/workflows/e03-compatibility-smoke.yml` (Android inside the pinned emulator-runner step; iOS after Xcode 16.4 is selected). They select the device by explicit identity, record it, verify the pinned substrate (emulator boot, API level, Xcode, simulator), and run the steps below. |
| `smoke-common.sh` | Pins (builds and toolchain), output namespace, build download and digest verification, toolchain installation (`npm ci` from the lockfile, output kept in `environment/npm-ci.log`; Appium core and driver versions verified against their pins), Appium server start, harness run, and host-path scrubbing of kept text artifacts (scrubbing changes no observation). Every stop writes `record.json` with outcome NOT_RUN and a v2 attribution proposal (`smoke_stop`): NOT_EXECUTED / SUT_BUILD when the pinned build cannot be obtained, verified, or unpacked; NOT_EXECUTED / INFRASTRUCTURE when the substrate or the host runtime outside the runner fails its check; FAIL_RUNNER (conservative tie-break) when the installation, version check, or server start of the pinned Appium stack fails, or when the harness process ends without a record. |
| `harness/package.json`, `harness/package-lock.json` | appium@3.7.0, appium-uiautomator2-driver@8.7.0, appium-xcuitest-driver@12.13.2, exactly; installed with `npm ci`; `APPIUM_HOME` is the harness directory. |
| `harness/wd.mjs` | Minimal W3C WebDriver client (session, element look-up, click, text, attribute, screenshot, page source) over Node.js fetch. Every runner-related error carries its kind: the runner answered with an error, no answer, an answer without the required reference, or the required element or state not reached in time; any other exception is harness code and is never retried. |
| `harness/smoke.mjs` | The realization above (`REALIZATION`), the step runner, and the per-platform `record.json` (steps with capabilities, outcome SUCCESS or FAILURE, proposed result, attribution proposal, artifacts, build, runner, device, GitHub run identity). After the first runner action (the session request) every failure is proposed as FAIL_RUNNER with the basis of what the runner did; a harness exception is attached as candidate HARNESS_ORCHESTRATION evidence. A harness exception before any runner action is proposed as NOT_EXECUTED / HARNESS_ORCHESTRATION. Nothing is retried or repeated; the exit code is 0 only for outcome SUCCESS. |

Output namespace: `formal/APPIUM3-COMPAT-SMOKE-AUTH-01/SUT-02-android/` and `formal/APPIUM3-COMPAT-SMOKE-AUTH-01/SUT-02-ios/`, absent until an execution under that authorization; each platform writes only its own directory and is uploaded as its own artifact, so the two results carry independent hashes. Nothing is written to the Mobilewright `formal/` or quarantine trees, or to raw-data/. The iOS job starts only after the Android job has ended with outcome SUCCESS (proposed PASS); any other Android outcome stops the authorized smoke before iOS (protocol/mobile-runner-policy-v2.md, 9.5).

Result recording rule (protocol/mobile-runner-policy-v2.md, Section 9): the harness proposes a result and an attribution; QUALIFIER-MOBILE-01 records the result from the preserved artifacts, using only PASS, FAIL_RUNNER, or NOT_EXECUTED.

- PASS — the execution completed MC-01, MC-02, MC-06, MC-04, MC-08, and MC-10 and read the expected final state.
- FAIL_RUNNER — the failure belongs to the selected Appium 3 execution stack (the pinned core, the platform driver, the WebDriver-protocol behavior they implement) while the smoke capabilities were being attempted; a dependency or version incompatibility inside that stack is runner/toolchain evidence.
- NOT_EXECUTED — only when the artifacts positively demonstrate that the runner was not fairly exercised because of a cause outside it: SUT_BUILD, INFRASTRUCTURE, or HARNESS_ORCHESTRATION (a defect of the study-authored workflow, scripts, WebDriver client, harness, artifact plumbing, or configuration; a failed runner command alone is never enough). Every NOT_EXECUTED result has a row in the attribution records below.
- Uncertain attribution after the artifacts have been inspected is FAIL_RUNNER, never NOT_EXECUTED.
- After a NOT_EXECUTED or a FAIL_RUNNER the authorized smoke stops: nothing is repaired and continued, nothing is re-run. A further attempt after NOT_EXECUTED needs the preserved record, the corrected cause, a new explicit human authorization, and — because the workflow's gate admits only a first attempt with no recorded result — a successor implementation lock. A FAIL_RUNNER while Appium 3 is the selected runner exhausts the fallback (study-level status UNRESOLVED_AFTER_FALLBACK_FAILURE): Appium 3 is not executed again and no other runner is selected.

The ORCHESTRATOR mirrors a recorded result into manifests/compatibility-smoke-status.yaml only after it is recorded here.

## Smoke records

One row per ecosystem × platform for which E01 confirmed a surface. Result values (protocol/mobile-runner-policy-v2.md, Section 9): PASS; FAIL_RUNNER (failure of the selected runner's execution stack, or uncertain attribution); NOT_EXECUTED (a cause outside the runner positively demonstrated by the artifacts; attribution record required). A platform whose surface E01 recorded as ABSENT has no row. Every ecosystem, SUT-01 included, is recorded under the same definition. Cell format: sut_id exactly as in manifests/sut-manifest.yaml; platform `android` or `ios`; result exactly one of the three values; no `|` inside a cell.

| sut_id | platform (android / ios) | environment_type (EMULATED / SIMULATED) | pinned build identity | timestamp | runner version | steps executed (MC ids) | result | artifacts | notes / reason |
|---|---|---|---|---|---|---|---|---|---|

## Attribution records

One row per NOT_EXECUTED result (mandatory, protocol/mobile-runner-policy-v2.md, 9.3) and per FAIL_RUNNER result (naming the failed capability and whether the attribution was demonstrated or reached by the conservative tie-break).

| sut_id | platform | timestamp | result | failed phase | attributed category | basis (demonstrated / conservative tie-break) | concrete description | artifact pointers | recording role |
|---|---|---|---|---|---|---|---|---|---|

## Outcome

| Field | Value |
|---|---|
| Date | |
| Results (SUT-02 android; SUT-02 ios) | |
| Runner-caused failures (sut_id, platform, capability) | |
| Study-level mobile-runner status after this smoke (SELECTED / UNRESOLVED_AFTER_FALLBACK_FAILURE) | |
| Recorded by | |

Under protocol/mobile-runner-policy-v2.md, 9.5: a FAIL_RUNNER while Mobilewright is the selected runner triggers the Section 8 switch to Appium 3 for the whole study; a FAIL_RUNNER while Appium 3 is the selected runner — the current case — exhausts the fallback: Section 8 is not applied again, Appium 3 is not executed again, Appium 2 is never introduced, no other runner is selected, and every campaign requiring mobile execution stays blocked until a new protocol amendment. A NOT_EXECUTED passes nothing and fails nothing.

## Warning

Do not execute until an explicit human authorization of the smoke has been issued and a separate explicit dispatch instruction has been given. Do not fill any result field before an execution has actually occurred. Record NOT_EXECUTED only with positively demonstrating artifacts; record FAIL_RUNNER when in doubt. Never repair and continue, never re-run. Do not use anything recorded here as evidence about any SUT.
