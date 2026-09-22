# SUT-06 — WebdriverIO Native Demo App — Audit

Audit performed by AUDITOR-SUT06-WEBDRIVERIO under prompt E01-CAPABILITY-AUDITOR-V1 (rendered launch package `experiments/E01-capability-audit/launch/AUDITOR-SUT06-WEBDRIVERIO.md`, SHA-256 `5d8f917bf0d0e79c32aff9814c3772e0fce61af9c244d1aeab60dd98d932a917`, verified before starting). Rules: audits/README.md, protocol/capability-rubric-v1.md, protocol/evidence-rules-v1.md, protocol/cross-cutting-properties-v1.md.

## 1. Header

| Field | Value |
|---|---|
| ecosystem_id | SUT-06 |
| ecosystem_name | WebdriverIO Native Demo App |
| role | mobile specialist baseline |
| auditor_role | AUDITOR-SUT06-WEBDRIVERIO |
| protocol_version | v1 |
| rubric_version | v1 |
| evidence_rules_version | v1 |
| audit_status | SUBMITTED |
| started_at | 2026-09-17 |
| submitted_at | 2026-09-17 |
| environment_types_used | (none) |
| controlled_instance_available | null |

## 2. Components and provenance

Provenance copied unchanged from manifests/sut-manifest.yaml (SUT-06). `web` and `api` have no component pinned there ("no component named for this study"); presence below is this auditor's own verification, not assumed absent, per audits/README.md and manifests/sut-manifest.yaml notes.

| component | presence | repository | commit_sha_or_release | endpoint | verified_by | verified_at |
|---|---|---|---|---|---|---|
| web | ABSENT | | | | AUDITOR-SUT06-WEBDRIVERIO | 2026-09-17 |
| api | ABSENT | | | | AUDITOR-SUT06-WEBDRIVERIO | 2026-09-17 |
| android | CONFIRMED | https://github.com/webdriverio/native-demo-app | 470b89ec09afac8b28d32cb8ea953071fb7e138a | | AUDITOR-SUT06-WEBDRIVERIO | 2026-09-17 |
| ios | CONFIRMED | https://github.com/webdriverio/native-demo-app | 470b89ec09afac8b28d32cb8ea953071fb7e138a | | AUDITOR-SUT06-WEBDRIVERIO | 2026-09-17 |

Verification method: read-only clone of `https://github.com/webdriverio/native-demo-app` into the study's out-of-repository source workspace, checked out at the pinned identifier `470b89ec09afac8b28d32cb8ea953071fb7e138a` (release `v2.2.0`), read in full for the surfaces relevant to this audit. `git status` in that clone is clean throughout (no modification was made; see item 15 of the final return package). web/api absence: SUT06-EV-0001–0004. android/ios presence: the Android (`android/`) and iOS (`ios/`) native projects, the React Native/Expo application source (`src/`, `app/`), `app.json`, and the release workflow (`.github/workflows/publish.apps.yml`, which builds and uploads both an Android APK and an iOS Simulator zip) are all present and consistent at the pinned commit. A provenance-identifier discrepancy (the pinned value is a Git annotated-tag object, not a raw commit SHA) is recorded in unresolved.md, SUT-06-U01, and does not affect this verification (see that entry).

## 3. Modality assessments

| modality | provisional_score | confirmed_score | confirmation_state | evidence_status_summary | evidence_record_count | evidence_refs | verification_refs | rationale | structural_scope_note |
|---|---|---|---|---|---|---|---|---|---|
| Web UI Functional | 0 | | | DOCUMENTED: 1, SOURCE_VERIFIED: 1 | 2 | SUT06-EV-0001, SUT06-EV-0002 | | No Web surface exists in the evaluated version. README.md and docs/CONTRIBUTING.md document only Android/iOS; package.json, app.json, and the release CI workflow confirm no web build/export script, no web CI job or artifact, and no `.web.tsx` override file. `react-native-web` is present only as an unused Expo-scaffold transitive dependency; per protocol/capability-rubric-v1.md, local/potential buildability is not credited. | NO_WEB_SURFACE |
| API | 0 | | | DOCUMENTED: 1, SOURCE_VERIFIED: 1 | 2 | SUT06-EV-0003, SUT06-EV-0004 | | No programmatic API/service surface exists. README.md documents only client-side mobile screens; an exhaustive source search of src/ and app/ found no `fetch`/`axios`/HTTP client usage anywhere in the application. The app is fully local/offline. | NO_API_SURFACE |
| Android Native | 3 | | CONFIRMED | DOCUMENTED: 1, SOURCE_VERIFIED: 7 | 8 | SUT06-EV-0005, SUT06-EV-0006, SUT06-EV-0007, SUT06-EV-0008, SUT06-EV-0009, SUT06-EV-0010, SUT06-EV-0011, SUT06-EV-0012 | | Surface exists and is documented (SUT06-EV-0005) and automation-instrumented throughout (stable `accessibilityLabel`/`testID` on every screen read, SUT06-EV-0006). Decision procedure step 3 is answered "yes": the Data Management screen (SUT06-EV-0007) is a source-verified, in-app mechanism to establish a known value (Save) and reset it to a known state (Clear) across four storage tiers, each with a defined, testID-observable expected readout. This is fully implemented in the pinned commit's own committed source (no framework/vendor inference), so SOURCE_VERIFIED is the confirming evidence status and no evidence ceiling applies (this component is open source). This auditor considered and rejected the narrower reading under which a Save/Clear button pair is merely "the end-user path" (cross-cutting-properties-v1.md defines State Controllability as establishing state "rather than reaching it only by replaying the end-user path"): the mechanism is not a byproduct of normal app usage but a dedicated test-support screen whose in-screen text names Appium/`mobile: clearApp` expectations directly and labels the SecureStore action "Clear (test hook)" — the SUT documents this control as an experimental hook, not an incidental UI flow, and Score 3's own text imposes no particular channel (its own example list includes UI-reachable mechanisms such as "deep link into a prepared state"). This boundary call is nonetheless flagged for adjudication (unresolved.md, SUT-06-U05). Supporting Score-2 material beyond the Score-3 mechanism: permission grant flow (SUT06-EV-0008, reset side not app-exposed), deep-link scheme registration (SUT06-EV-0009, routing behavior not executed), tab-bar pin/unpin (SUT06-EV-0010), deterministic Login/Sign-up validation (SUT06-EV-0011), and the documented WebView context-switch scenario (SUT06-EV-0012). No EXECUTION_VERIFIED record was produced or needed. | |
| iOS Native | 3 | | CONFIRMED | DOCUMENTED: 1, SOURCE_VERIFIED: 7 | 8 | SUT06-EV-0013, SUT06-EV-0014, SUT06-EV-0015, SUT06-EV-0016, SUT06-EV-0017, SUT06-EV-0018, SUT06-EV-0019, SUT06-EV-0020 | | Same shared React Native/Expo codebase and same reasoning as Android Native (SUT06-EV-0013–0020 mirror SUT06-EV-0005–0012, including the same considered-and-rejected "end-user path" reading and the same SUT-06-U05 adjudication flag). The Data Management save/clear mechanism (SUT06-EV-0015) is not platform-branched and is confirmed by the same SOURCE_VERIFIED evidence; iOS-specific persistence nuances (Keychain `keychainAccessible` option, simulator-only distribution) are documented in-app and in README.md and do not change the mechanism. | |
| Performance | 1 | | | DOCUMENTED: 1, SOURCE_VERIFIED: 1 | 2 | SUT06-EV-0021, SUT06-EV-0022 | | No performance-specific instrumentation, budget, or controlled-degradation mechanism is documented or present in source. A built APK/iOS Simulator app remains technically reachable by a generic profiler (Android Studio Profiler, Xcode Instruments) or Appium-based timing measurement, which is the Score 1 definition itself, not evidence for a higher score. | |
| Accessibility — Web only | 0 | | | SOURCE_VERIFIED: 1 | 1 | SUT06-EV-0023 | | Per protocol/capability-rubric-v1.md's own worked example, a mobile-only ecosystem with no Web surface scores 0 on this modality. Derivative of the Web UI Functional absence (SUT06-EV-0001, SUT06-EV-0002); native mobile accessibility identifiers (SUT06-EV-0006/0014) are Automation Affordances, not evidence for this Web-scoped modality. | NO_WEB_SURFACE |
| Visual Testing | 2 | | | SOURCE_VERIFIED: 2 | 2 | SUT06-EV-0024, SUT06-EV-0025 | | Every screen/component read conditionally styles itself from `useColorScheme()` against a fixed palette (Colors.ts), producing a deterministic, repeatable visual difference between OS-level Dark and Light appearance (SUT06-EV-0024) — a meaningful, stable, testable visual condition (Score 2). No in-app visual-condition control, visual-regression baseline, or fixture ships with the evaluated version (SUT06-EV-0025); the trigger (OS appearance setting) is external to the SUT, not an SUT-exposed mechanism, so Decision procedure step 3 is answered "no" and the cell does not reach Score 3. | |
| Security Testing | 1 | | | DOCUMENTED: 1, SOURCE_VERIFIED: 1 | 2 | SUT06-EV-0026, SUT06-EV-0027 | | No documented intentional vulnerability or security-testing purpose exists (SUT06-EV-0026); source inspection found no intentionally insecure pattern — SecureStore usage follows a conventional, platform-appropriate pattern, and the one committed release-signing keystore is explicitly documented as filled with dummy data for a non-Play-Store demo, not a security-testing scenario (SUT06-EV-0027). A built APK/IPA remains technically reachable by a generic security scanner, which is the Score 1 definition. | |
| Localization / i18n | 0 | | | DOCUMENTED: 1, SOURCE_VERIFIED: 1 | 2 | SUT06-EV-0028, SUT06-EV-0029 | | No i18n/localization library is a dependency (SUT06-EV-0028); an exhaustive case-insensitive source search for locale/translation logic found nothing beyond one unrelated false-positive match (an animation property named `translateX`) (SUT06-EV-0029). This is a plain capability absence, not a missing-surface-type reason, so no `structural_scope_note` token applies. | |

No cell in this audit was capped by the tie-break rule; `confirmed_score` is left blank throughout because it coincides with `provisional_score` in every row (audits/README.md).

## 4. Cross-cutting properties

### State Controllability

The Data Management screen (SUT06-EV-0007, SUT06-EV-0015) lets the experimenter directly establish a known value in each of four storage tiers (in-memory, AsyncStorage-tier SQLite, explicit SQLite, SecureStore) via a testID-addressable Save action, independent of any end-user navigation path. Permission grants (SUT06-EV-0008, SUT06-EV-0016) can be established (activated) the same way, though not reset in-app. The Menu side-panel's star toggles (SUT06-EV-0010, SUT06-EV-0018) directly set which screens are pinned to the bottom tab bar. Login/Sign-up validation state (SUT06-EV-0011, SUT06-EV-0019) is driven by known, fixed input rules. There is no API or Web layer (SUT06-EV-0001–0004), so no server-side or browser-based state establishment exists; all controllable state is in-app/on-device.
Evidence refs: SUT06-EV-0007, SUT06-EV-0008, SUT06-EV-0010, SUT06-EV-0011, SUT06-EV-0015, SUT06-EV-0016, SUT06-EV-0018, SUT06-EV-0019.

### Resetability

The Data Management screen's four per-tier Clear controls (SUT06-EV-0007, SUT06-EV-0015) reset each tier independently to a defined, testID-observable placeholder state; scope is limited to those four tiers (no single app-wide "reset all" action was found in source). Permission grants have no in-app reset: revoking requires leaving the app for OS Settings (SUT06-EV-0008, SUT06-EV-0016). Form fields (Login, Forms screen) and the Menu's pinned-tab state were not found to have any dedicated reset control beyond component remount/navigation; no evidence record supports an app-wide reset beyond the Data Management tiers.
Evidence refs: SUT06-EV-0007, SUT06-EV-0008, SUT06-EV-0015, SUT06-EV-0016.

### Determinism

- deterministic: Data Management save/clear/readout (SUT06-EV-0007, SUT06-EV-0015); Login/Sign-up validation outcome (SUT06-EV-0011, SUT06-EV-0019, biometric branch); permission-switch state reflecting the OS grant result (SUT06-EV-0008, SUT06-EV-0016); dark/light styling response to `useColorScheme()` (SUT06-EV-0024).
- stochastic: none found. No random-data-generation or randomized-content mechanism was observed in any file read for this audit.
- time-dependent: Login/Sign-up's fixed 1500ms simulated delay before showing the deterministic success `Alert` (SUT06-EV-0011, SUT06-EV-0019) — the delay duration is time-dependent, the eventual outcome is not.
- external dependency: the WebView screen's content is the live external site `https://webdriver.io/`, outside the SUT's control (SUT06-EV-0012, SUT06-EV-0020); the OS-level dark/light appearance setting that drives visual styling is likewise external to the SUT itself (SUT06-EV-0024).

Evidence refs: SUT06-EV-0007, SUT06-EV-0008, SUT06-EV-0011, SUT06-EV-0012, SUT06-EV-0015, SUT06-EV-0016, SUT06-EV-0019, SUT06-EV-0020, SUT06-EV-0024.

### Observability

Every interactive element read for this audit carries a stable, platform-appropriate identifier (`accessibilityLabel` on Android, `testID` on iOS) via the shared `testProperties()` helper (SUT06-EV-0006, SUT06-EV-0014), including dedicated readout elements (for example `data-<tier>-readout`) whose text is the directly observable expected outcome for the Data Management mechanism (SUT06-EV-0007, SUT06-EV-0015). Permission state is observable via the same switches that control it (SUT06-EV-0008, SUT06-EV-0016). There is no API layer (SUT06-EV-0003, SUT06-EV-0004), so no OpenAPI/Swagger description, structured API response, or server-side log/health endpoint exists; all observability is in-app UI state, not an out-of-band channel.
Evidence refs: SUT06-EV-0003, SUT06-EV-0004, SUT06-EV-0006, SUT06-EV-0007, SUT06-EV-0008, SUT06-EV-0014, SUT06-EV-0015, SUT06-EV-0016.

### Automation Affordances

`testProperties()` is applied consistently across every screen/component read for this audit (SUT06-EV-0006, SUT06-EV-0014): Home, Data Management, Login/Sign-up form, Form components, Permission switches, Menu side-panel entries and stars. A native URL scheme (`wdio://`) is registered at both the Android intent-filter and iOS `CFBundleURLTypes` level, with Expo Router file-based routes for every tab screen (SUT06-EV-0009, SUT06-EV-0017), though the actual routing behavior was not executed in this audit. These affordances are documented in source (testID conventions, scheme registration) but not called out as such in README.md/CONTRIBUTING.md, so they are source-discoverable rather than officially documented as an automation API.
Evidence refs: SUT06-EV-0006, SUT06-EV-0009, SUT06-EV-0014, SUT06-EV-0017.

### Cross-platform Scenario Parity

Only Android and iOS surfaces exist (no Web surface: SUT06-EV-0001, SUT06-EV-0002), so parity is assessed between Android and iOS only. Both platforms run from one shared, non-platform-branched React Native/Expo TypeScript source tree (`src/`, `app/`); every mechanism cited above (Data Management, Permissions, Login validation, WebView, Menu/tab-bar) has an identical implementation on both platforms, differing only at the native-module boundary (documented platform-specific persistence semantics for SecureStore, SUT06-EV-0007/0015; iOS Simulator-only distribution, SUT06-EV-0013). Parity between Android and iOS is therefore complete for every scenario examined in this audit; no partial-parity case was found.
Evidence refs: SUT06-EV-0007, SUT06-EV-0008, SUT06-EV-0009, SUT06-EV-0011, SUT06-EV-0012, SUT06-EV-0015, SUT06-EV-0016, SUT06-EV-0017, SUT06-EV-0019, SUT06-EV-0020.

### Cross-layer State Continuity

No layer pairs exist to test: there is no API layer for an API→Android/API→iOS/Web→API relationship (SUT06-EV-0003, SUT06-EV-0004) and no Web layer (SUT06-EV-0001, SUT06-EV-0002). All state established in this ecosystem (Data Management, permissions, form/menu state) is on-device, within the mobile app itself; it is not verified through, or shared with, any separate layer.
Evidence refs: SUT06-EV-0001, SUT06-EV-0002, SUT06-EV-0003, SUT06-EV-0004.

### Functional Complexity

Entities/operations inventoried from source read for this audit: (1) four independently addressable local storage tiers with save/read/clear operations and tier-specific persistence rules (SUT06-EV-0007, SUT06-EV-0015); (2) a Login/Sign-up form with client-side validation rules (email format, minimum password length, sign-up password-confirmation match) and an optional biometric-authentication branch (SUT06-EV-0011, SUT06-EV-0019); (3) four OS-mediated permission grants (camera, microphone, location, photo library) with app-observable but not app-resettable state (SUT06-EV-0008, SUT06-EV-0016); (4) a configurable bottom tab bar (pin/unpin up to five of seven non-Home/Menu screens) via the Menu side-panel (SUT06-EV-0010, SUT06-EV-0018); (5) a native WebView embedding a fixed external site for context-switch testing (SUT06-EV-0012, SUT06-EV-0020); (6) generic form/gesture widgets (text input, switch, dropdown, buttons, horizontal/vertical swipe carousel, drag-and-drop puzzle) documented in README.md (SUT06-EV-0005, SUT06-EV-0013) but not independently source-cited beyond that inventory in this audit. No ranking by complexity is implied.
Evidence refs: SUT06-EV-0005, SUT06-EV-0007, SUT06-EV-0008, SUT06-EV-0010, SUT06-EV-0011, SUT06-EV-0012, SUT06-EV-0013, SUT06-EV-0015, SUT06-EV-0016, SUT06-EV-0018, SUT06-EV-0019, SUT06-EV-0020.

## 5. Documentation vs implementation contradictions

None found. README.md's screen inventory (SUT06-EV-0005, SUT06-EV-0013) does not mention the Data Management screen added in this exact release (v2.2.0; see git log message "feat: add Data management screen …"), but this is an omission (documentation not yet updated for the newest screen), not a disagreement — the app does not claim the screen doesn't exist, README.md is simply silent on it. Per protocol/capability-rubric-v1.md, "Evidence requirement," a contradiction is specifically a case where documentation and implementation *disagree*; an incomplete-but-not-false README entry does not meet that bar. Noted here for transparency, not recorded as a contradiction row.

| claim | documentation source | implementation observation | evidence refs |
|---|---|---|---|

## 6. Negative evidence summary

Negative evidence is retained in evidence.csv (not deleted) for every Score 0/1 cell and every absent mechanism checked: Web UI Functional absence (SUT06-EV-0001, SUT06-EV-0002), API absence (SUT06-EV-0003, SUT06-EV-0004), Accessibility — Web only structural absence (SUT06-EV-0023), no performance-specific mechanism (SUT06-EV-0021, SUT06-EV-0022), no in-app visual-condition control beyond OS-driven theming (SUT06-EV-0025), no intentional-vulnerability/security-testing mechanism (SUT06-EV-0026, SUT06-EV-0027), and no localization/i18n mechanism (SUT06-EV-0028, SUT06-EV-0029). See limitations.md for the corresponding evaluation-limitation entries.

## 7. Auditor declaration

- [x] The same rubric (protocol/capability-rubric-v1.md) was applied to every modality.
- [x] The SUT was not modified.
- [x] No capability was inferred from vendor commercial products.
- [x] All evidence has provenance (repository and commit SHA / release, or endpoint) against the pinned target.
- [x] Every evidence record has a unique evidence_id, and every reference uses evidence_id.
- [x] Every EXECUTION_VERIFIED record is linked to an execution verification record with environment_type. (N/A — no EXECUTION_VERIFIED record was produced in this audit.)
- [x] Negative evidence was retained, and structural absences carry a structural_scope_note.
- [x] No fault activation, active security testing, load, or state change visible to other users was performed against a PUBLIC_HOSTED instance. (N/A — no PUBLIC_HOSTED instance of SUT-06 exists or was used; all evaluation was documentation and source reading at the pinned commit in a local, read-only clone.)
