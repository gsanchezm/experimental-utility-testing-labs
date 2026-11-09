# Per-SUT Compatibility Smoke: SUT-01 (OmniPizza) Android, Appium 3 (DRAFT)

## Status

DRAFT. Prepared, not issued, not executed. Nothing in this folder authorizes, locks, dispatches, or records a result. The authorization record `manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml` (authorization id APPIUM3-COMPAT-SMOKE-AUTH-04) is PREPARED, NOT ISSUED, with dispatch_eligibility NOT_ELIGIBLE_UNTIL_ISSUED. The implementation lock `manifests/compatibility-smoke-implementation-lock-v5.draft.yaml` is a draft and is not an execution baseline. No row of the Smoke records table below is filled. A dispatch needs an issued authorization, its publication, and a separate explicit human dispatch instruction. Open items and human decisions are in `IMPLEMENTATION-NOTES.md`.

Scenario and governance references. The scenario reference is CS-007 (DRAFT; reference only). The governance route is protocol/agent-governance-v6.md, Section 3.4 (FROZEN-PRE-DATA 2026-11-06, carried from v5): the ORCHESTRATOR performs the qualifier tasks, and every dispatch needs the human research lead's explicit approval of that exact dispatch. Section 3.7 of v6 does not cover this smoke. The sentence of Section 3.4 that called the compatibility smoke closed by the exhausted fallback, stale after the 2026-11-02 restoration, was updated as representation only at the freeze of v6 (open decision HD-8, approved 2026-11-06); protocol/mobile-runner-policy-v3.md, section 9, applies to SUT-01 as well (IMPLEMENTATION-NOTES.md, section 8, conflicts A and C: resolved).

## Purpose and scope

The compatibility smoke of protocol/mobile-runner-policy-v3.md, section 9, applies to every mobile-capable ecosystem, SUT-01 included. It establishes only that the selected runner (Appium 3, pinned 3.7.0) can drive the pinned Android build of SUT-01. It is not a duration comparison, not a benchmark, and not evidence about any ecosystem (section 9, and section 3 of the policy). Its result is a tool-qualification record.

Topology: one job for Android on the GitHub-hosted emulator (API 35, google_apis x86_64, pixel_7). There is no iOS job. The SUT-01 iOS simulator build exists (release v1.1.8 asset OmniPizza-Simulator.zip) but iOS is deferred (HUMAN DECISION HD-1). There is no Android-to-iOS ordering to enforce. The smoke runs once per dispatch, with no automatic repeat (policy 9.5).

Study state at drafting: the study-level mobile-runner status is SELECTED (manifests/toolchain-manifest.yaml, mobile_runner_selection, restored 2026-11-02 under policy 9.7.9 and 9.7.10). The SUT-02 iOS FAIL_RUNNER of APPIUM3-COMPAT-SMOKE-AUTH-02 stays preserved and is named by the lineage record manifests/mobile-runner-remediation-v1.yaml. Any FAIL_RUNNER of this smoke would return the study to UNRESOLVED_AFTER_FALLBACK_FAILURE and block every mobile condition, including the SUT-02 PASSes (policy 9.5 and 9.7.11). That consequence is the central risk of this draft (HUMAN DECISION HD-2).

## Source finding: where the pinned build's backend endpoint is configured

Pinned revision: tag v1.1.8 is a lightweight tag that resolves directly to commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a (GitHub API, `git/ref/tags/v1.1.8`, retrieved 2026-11-06T02:23Z UTC). That equals the android and ios `commit_sha` of manifests/sut-manifest.yaml. The release record (GitHub API `releases/tags/v1.1.8`, same retrieval) lists omnipizza-release.apk at 84930726 bytes with digest sha256:1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4, and OmniPizza-Simulator.zip at 26921522 bytes with digest sha256:de2e8c21b0788cef1ba4654378449d16e958574b33a2b4ef8a07cb698dbc6eb1. Both equal the pins in manifests/toolchain-manifest.yaml (`qualification_build`). The APK was not downloaded or executed.

Finding: the backend origin is a compile-time constant of the mobile source. `frontend-mobile/src/api/client.ts` line 27 at the pinned commit reads `const API_ORIGIN = "https://omnipizza-backend.onrender.com";`, and lines 29 to 32 use it as the axios `baseURL`. No `process.env` or `EXPO_PUBLIC_*` reference, no `expo.extra` entry in `frontend-mobile/app.json`, no settings screen, no launch argument other than the country code (client.ts lines 5 to 25 read only `detoxCountryCode`), and no deep-link parameter (SUT01-EV-0010 lists accessToken, market, lang, hydrateCart, orderId, resetSession) changes the origin. The only other origins in the source are image URLs (LoginScreen.tsx lines 118 and 141, LocationHeader, PizzaCard, ProfileScreen, OrderSuccessScreen). A search of the whole mobile source tree (80 files fetched at the pinned commit) found no second API origin.

Consequence: the endpoint is fixed in the release APK. A controlled backend on the runner would require a changed build or a changed network path (for example DNS or TLS interception at the emulator). Both alter the system as found (protocol rule 3, the agent-instructions file), so neither is the default (HUMAN DECISION HD-3). The default classification is therefore a hosted, read-only sign-in against `https://omnipizza-backend.onrender.com`, environment_type PUBLIC_HOSTED, with the HOSTED_MAPPING_UNVERIFIED caveat of manifests/sut-manifest.yaml (SUT-01 api notes) disclosed. The hosted deployment's commit is not verified: the probe in `smoke-common.sh` records `/api/version`, but no pin governs it.

Not determinable from the pinned source: the Android launch activity. `frontend-mobile/android/` is generated by prebuild and is absent from the pinned tree, so no `appActivity` value can be read from source. The realization sets none and leaves the launcher resolution to the driver (HUMAN DECISION HD-16).

## Concrete realization (DRAFT, not yet locked)

The lock covers this section by SHA-256. Every value is traced to the pinned source at commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a, or it is TBD.

| Item | SUT-01 × Android × Appium 3 |
|---|---|
| Pinned build consumed | `omnipizza-release.apk` (release v1.1.8, asset of tag v1.1.8), 84930726 bytes, SHA-256 1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4, verified against the pin before any runner action; the release record publishes the same digest |
| Application identity | package `com.omnipizza.app` (frontend-mobile/app.json, android.package, line 20), version 1.1.8 (app.json, line 6); minSdkVersion 29 (app.json, expo-build-properties plugin) |
| Clean-start procedure | freshly created AVD; digest verified before any runner action; `adb uninstall com.omnipizza.app` before the session (no-op when absent); the application state is in memory only (frontend-mobile/src/store/useAppStore.ts has no persistence middleware, line 1 imports only zustand), so the reinstall is a clean start |
| Scenario reference (reference only) | CS-007 (experiments/scenario-mappings/CS-007.yaml, DRAFT, not an input): this smoke realizes its Android precondition (quick login of the documented account standard_user, then the sign-in control), sign-in, and arrival at the catalogue. The catalogue item-identity oracle is not realized (DP-3 fallback). The market and language are the application defaults, US and en (LoginScreen.tsx line 51; useAppStore.ts lines 88 to 89), which matches CS-007 DP-9 (one market with its default language) |
| Pre-runner backend probe | before the session: `GET https://omnipizza-backend.onrender.com/health` must answer HTTP 200 (client.ts line 27 for the origin; `/health` per SUT01-EV-0029, backend/main.py); `GET /api/version` is recorded, not evaluated; a probe that does not answer 200 stops the smoke before any runner action as NOT_EXECUTED / INFRASTRUCTURE, demonstrated by environment/backend-probe.json (HUMAN DECISION HD-15) |
| Launch (MC-01) | one Appium session: `appium:automationName` UiAutomator2, `appium:app` = the verified APK, `appium:udid` = the emulator serial, `appium:appPackage` com.omnipizza.app, `appium:autoGrantPermissions` true, `appium:disableWindowAnimation` true, `appium:androidInstallTimeout` 300000, `appium:uiautomator2ServerInstallTimeout` 120000, `appium:uiautomator2ServerLaunchTimeout` 120000, `appium:adbExecTimeout` 120000, `appium:newCommandTimeout` 300; session start limit 600 s. Launch activity: TBD (driver-resolved; HUMAN DECISION HD-16) |
| Stable identifier located (MC-02) | accessibility id `screen-login`: the root View of the login screen, which sets `accessibilityLabel="screen-login"` and `testID="screen-login"` (frontend-mobile/src/screens/LoginScreen.tsx, line 112); displayed |
| Quick-login control (MC-04) | accessibility id `Standard`: the pill of standard_user, built by `getReadableControlProps("btn-user-standard_user", "Standard")` (LoginScreen.tsx lines 29 and 219 to 225; qa.ts lines 58 to 72 set accessibilityLabel on Android); one tap fills the username `standard_user` and the password (fillUser, lines 106 to 109). The label is shared with the text node of the same pill (line 226): the first match in the driver's hierarchy order is used and the match count is recorded (HUMAN DECISION HD-17) |
| Sign-in control (MC-04) | accessibility id `Sign In`: the title of `PrimaryButton testID="btn-login"` (LoginScreen.tsx line 206; PrimaryButton.tsx line 21 sets accessibilityLabel to the title on Android); the label is shared with the text node (PrimaryButton.tsx line 33); first match and count recorded (HUMAN DECISION HD-17). Defaults at LoginScreen.tsx lines 47 and 48 (username standard_user, password pizza123) are not relied on because the quick-login tap precedes this step |
| Arrival (MC-06) | accessibility id `screen-catalog`, displayed within 90 s: the root SafeAreaView of the catalogue screen (CatalogScreen.tsx line 52, accessibilityLabel and testID "screen-catalog"); reached by `navigation.replace("Catalog")` after `setToken` (LoginScreen.tsx lines 57 to 66, 83) |
| State read (MC-08) | element presence: `screen-login` displayed before the sign-in control, `screen-catalog` displayed after sign-in. The catalogue item identity is NOT read: no mobile item identifier is evidenced in E01 and the item set comes from the hosted backend, which no pin governs (DP-3 fallback; the item identity is TBD) |
| Expected final state | `screen-catalog` displayed after the sign-in of standard_user; default market US and language en (LoginScreen.tsx line 51; useAppStore.ts line 88 to 89); no market change |
| Failure evidence | on a failed sign-in the page source and the screenshot are kept (MC-10); a backend refusal shows its message in the `text-login-error` node (LoginScreen.tsx line 198), whose accessibility label is the message (qa.ts); the messages "Too many users" (status 429 or users_limit, LoginScreen.tsx lines 92 and 93) and the locked-out message (lines 94 to 97) are backend responses |
| Artifacts (MC-10) | `terminal.png` and `source-terminal.xml` (or `failure.png` and `source-failure.xml`), `record.json`, `harness.log`, `appium-server.log`, `environment/` (device, build verification, toolchain install, npm ci log, backend probe) |
| Timeouts | screen arrival 90 s; other element look-ups and state reads 30 s (polling every 1 s); Appium server readiness 120 s; harness watchdog 45 min; job limit 60 min |
| Static evidence basis | `frontend-mobile/src/screens/LoginScreen.tsx` (testIDs, accessibility labels, defaults, quick login, error handling), `frontend-mobile/src/components/PrimaryButton.tsx`, `frontend-mobile/src/utils/qa.ts`, `frontend-mobile/src/screens/CatalogScreen.tsx`, `frontend-mobile/src/api/client.ts`, `frontend-mobile/app.json`, `frontend-mobile/App.tsx` (initialRouteName "Login", line 83), `frontend-mobile/src/store/useAppStore.ts`; all at commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a |

Cross-check references, never evidence (policy section 3): the qualification realization of the Mobilewright gate uses the identifiers `screen-login` and `btn-login`, which match the source above. The formal Mobilewright outputs record only the identifiers the harness was given, not the Android accessibility tree, so the mapping of testID to resource-id on Android is not evidenced by any artifact and is not used here. The chosen strategy is the accessibility id, which the source sets explicitly.

Unresolved by static reading alone (only a run can show them): whether the Android accessibility tree exposes each label as content-description with the expected match count; whether the release APK installs on the API 35 emulator; and whether the hosted backend answers in time. Each is a risk of the first and only execution, which is why the realization is a DRAFT and the consequence of a FAIL_RUNNER is central (HD-2).

## Implementation

| Path | Role | Status |
|---|---|---|
| `run-smoke-android.sh` | platform entry point: emulator checks, clean start, pre-runner backend probe, harness run | DRAFT, copy of the SUT-02 Android entry adapted; not run |
| `smoke-common.sh` | pins (SUT-01 build URL and digest, toolchain pins), output namespace `formal/<authorization id>/SUT-01-android`, build verification, toolchain check, backend probe, Appium server start, harness run, host-path scrubbing | DRAFT, adapted from the SUT-02 copy; the SUT-02 file is unchanged |
| `harness/smoke.mjs` | the realization above (REALIZATION.android), the step runner, the record writer | DRAFT, generated from the SUT-02 harness; iOS removed |
| `harness/wd.mjs` | minimal W3C WebDriver client (shared client; byte-identical to the SUT-02 copy of lock v4) | copy |
| `harness/package.json`, `harness/package-lock.json` | exact Appium core 3.7.0 and appium-uiautomator2-driver 8.7.0 (xcuitest driver present in the lockfile as the SUT-02 copy has it; not used on Android); byte-identical | copy |
| `.github/workflows/e06-compatibility-smoke-sut01.yml` | dispatch-only, fail-closed gate, then one Android job | DRAFT, not merged into the tracked tree (HUMAN DECISION HD-7) |
| `manifests/compatibility-smoke-implementation-lock-v5.draft.yaml` | successor implementation lock for this smoke (new scope; supersedes nothing) | DRAFT, hashes computed by script |
| `manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml` | authorization APPIUM3-COMPAT-SMOKE-AUTH-04 | PREPARED, NOT ISSUED |
| `tests/` | static tests: gate matrix, syntax and lint outputs, length estimate | run, outputs recorded |
| `patches/compatibility-smoke-status.draft.patch` | mirror entry for SUT-01 Android (NOT_STARTED); not applied | DRAFT |
| `IMPLEMENTATION-NOTES.md` | what is done, not done, blocked, approvals, decisions | DRAFT |

Pins and substrate (unchanged from the SUT-02 smoke of lock v4): appium 3.7.0 (npm, integrity recorded in the lock), appium-uiautomator2-driver 8.7.0, Node.js 22.23.2, Android emulator system-images;android-35;google_apis;x86_64, profile pixel_7, ReactiveCircus/android-emulator-runner pinned at commit a421e43855164a8197daf9d8d40fe71c6996bb0d, GitHub-hosted ubuntu-24.04. Output namespace: `qualification/compatibility-smoke-sut01/formal/APPIUM3-COMPAT-SMOKE-AUTH-04/SUT-01-android/`, absent until an execution.

## Smoke records

One row per ecosystem × platform. No row exists: this draft is not executed. A row is appended only after an execution under an issued authorization, and the mirror entry is transcribed only from that row (manifests/compatibility-smoke-status.yaml, transcription rule).

| sut_id | platform (android / ios) | environment_type (EMULATED / SIMULATED) | pinned build identity | timestamp | runner version | steps executed (MC ids) | result | artifacts | notes / reason |
|---|---|---|---|---|---|---|---|---|---|

## Attribution records

No row exists (no execution).

## Outcome

Not executed. The draft is not an outcome. Recorded by no one.

## Warning

Do not execute until an explicit human authorization of this smoke has been issued, published, and followed by a separate explicit dispatch instruction. Do not fill any result field before an execution has actually occurred. Record NOT_EXECUTED only with positively demonstrating artifacts; record FAIL_RUNNER when in doubt. Never repair and continue; never re-run. Nothing recorded here is evidence about any system under test.
