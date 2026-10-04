# Mobile Runner Policy

| Field | Value |
|---|---|
| Document | protocol/mobile-runner-policy-v3.md |
| Protocol version | v3 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-29 |
| Supersedes | protocol/mobile-runner-policy-v2.md (transitions to AMENDED by this freeze, per protocol/change-control-v1.md, section 2 — `data_collection_started` is already true) |
| Freeze approval | gilbertosanchez, 2026-10-02 (explicit human approval of the post-data amendment resolving protocol/unresolved.md PROTO-U19: decision APPROVE on the decision package manifests/mobile-runner-policy-v3-amendment-proposal-v3.yaml; this document was prepared by the ORCHESTRATOR as a DRAFT on 2026-09-29 under the preparation-only human instructions PREPARE MOBILE-RUNNER-POLICY-V3 AFTER APPIUM FALLBACK EXHAUSTION, HARDEN MOBILE-RUNNER-POLICY-V3 DRAFT BEFORE HUMAN APPROVAL, and FINALIZE MOBILE-RUNNER-POLICY-V3 DRAFT FREEZE READINESS, and frozen on 2026-10-02 under that approval with every rule unchanged; post-data-collection change under protocol/change-control-v1.md, section 5; approval provenance and record: manifests/mobile-runner-policy-v3-amendment-v1.yaml) |

This policy governs which mobile test runner the study uses for the Android Native and iOS Native modalities and the conditions under which it may be used. It applies to every evaluated ecosystem (system under test, SUT) identically.

**POST-DATA SUCCESSOR OF protocol/mobile-runner-policy-v2.md — IN FORCE FROM ITS FREEZE.**

- It supersedes protocol/mobile-runner-policy-v2.md, which is AMENDED and retained unchanged apart from its header; v2 was the policy in force until this version was explicitly approved and frozen by a human decision.
- It was prepared, approved, and frozen after data collection began (`data_collection_started` has been true since 2026-09-17, manifests/study-manifest.yaml); it is a post-data change under protocol/change-control-v1.md, section 5.
- It does not reinterpret any observation collected under v1 or v2.
- It exists to define prospective behavior after the fallback exhaustion already recorded under v2 on 2026-09-29.

## What changed relative to v2, and why

Under v2 the selected runner Appium 3 (chosen by the Section 8 switch after the formal Mobilewright gate FAILED under MOBILE-QUALIFICATION-EXEC-AUTH-03) received its per-SUT compatibility smoke for SUT-02. Under APPIUM3-COMPAT-SMOKE-AUTH-01 SUT-02 × Android was recorded NOT_EXECUTED / HARNESS_ORCHESTRATION. Under APPIUM3-COMPAT-SMOKE-AUTH-02 (GitHub Actions run 36539790536, attempt 1) SUT-02 × Android was recorded PASS and SUT-02 × iOS FAIL_RUNNER by the conservative tie-break of 9.4 (basis CONSERVATIVE_TIE_BREAK_ATTRIBUTION_UNCERTAIN: attribution remained uncertain between the study-authored WebDriver transport and the selected Appium 3 / XCUITest execution stack). Under 9.5 that FAIL_RUNNER exhausted the fallback: the study-level mobile-runner status is UNRESOLVED_AFTER_FALLBACK_FAILURE and every campaign requiring mobile execution is blocked until a new explicit protocol amendment decides the mobile-runner strategy. The post-run review also identified a concrete study-authored WebDriver transport and diagnostic defect (qualification/unresolved.md, QUAL-U06: the transport does not explicitly align its underlying HTTP timeouts with the declared 1200 s iOS session-start budget and discards the underlying error cause), whose causal role in that run was not demonstrated sufficiently to change the 9.4 result. These records are unchanged and are not reinterpreted here.

This version introduces exactly one narrow mechanism, the **post-fallback remediation qualification** (new 9.7): one prospective Appium 3 qualification of SUT-02 × iOS only, after a correction restricted to QUAL-U06, with the result vocabulary and attribution rules of 9.1–9.4 unchanged and single-attempt terminal effects. It does not state that the historical FAIL_RUNNER was wrong, does not state that Appium 3 would pass on iOS, and does not remove the fallback exhaustion from the v2 record: the v2 result remains historically valid, and a remediation observation would be a new prospective record under this version.

**Substantive changes:** 9.5 gains one bounded exception clause pointing to 9.7 (the exhaustion itself, the FAIL_RUNNER, and every other element of 9.5 are unchanged); 9.7 is new. Within 9.7, admission is governed by an explicit effective-admissibility rule (9.7.9) that separates the immutable historical observation from the current prospective admissibility state, by a normative remediation lineage record (9.7.10), and by a post-restoration rule (9.7.11); no rule selects the latest table row for a SUT × platform, and 9.7.12 records why the SUT-02 × Android PASS stays valid after a correction of the shared WebDriver client. Sections 11 and 12 and the header are updated. The introductory paragraph, 9.1–9.4, 9.6, and Section 10 are carried over from v2 verbatim. Sections 1–8 are carried over with non-substantive status and provenance corrections only, in Sections 1, 2, 3, 4, 6, and 7: their narration of what had not yet happened when v1 was written (Mobilewright as a not-yet-qualified candidate, no qualification run, qualification provenance, scenario realization, and platform identities null / TBD, pass criteria "now frozen") is brought in line with the completed history; no criterion, N, capability, attribution rule, result rule, or historical outcome changes. The v1 -> v2 changes are recorded in protocol/mobile-runner-policy-v2.md and are carried into this version unchanged.

**Prior data validity (protocol/change-control-v1.md, section 5, item 3).** This version invalidates, re-collects, and reinterprets nothing. E01-capability-audit (FROZEN; collected under protocol v1) and the H1 analysis: unaffected and valid under the versions that governed them. The formal Mobilewright qualification (MOBILE-QUALIFICATION-EXEC-AUTH-03) and the Section 8 selection of Appium 3: unaffected, valid under v1. APPIUM3-COMPAT-SMOKE-AUTH-01 (SUT-02 × Android NOT_EXECUTED / HARNESS_ORCHESTRATION) and APPIUM3-COMPAT-SMOKE-AUTH-02 (SUT-02 × Android PASS; SUT-02 × iOS FAIL_RUNNER, 9.4 tie-break): unaffected, preserved, valid under v2; the AUTH-02 Android PASS remains an immutable valid compatibility observation, and the AUTH-02 iOS FAIL_RUNNER remains permanently present as a valid v2 observation. The v2 fallback exhaustion (UNRESOLVED_AFTER_FALLBACK_FAILURE, 2026-09-29) remains a valid historical state. This version introduces a prospective state transition only. Qualification and compatibility-smoke records are tool-qualification records, not campaign data. No campaign of E02–E12 has collected raw data, so nothing requires re-collection or re-analysis. A remediation observation, if later authorized, is a separate prospective record under this version.

**Affected campaigns (prospectively; none has collected campaign data):** MOBILE_REQUIRED_CONFIGURED: E03-resetability (its configured conditions E03-CS001-SUT02-ANDROID and E03-CS001-SUT02-IOS). MOBILE_DECLARED_OR_CANDIDATE, only for their Android or iOS conditions: E02-state-establishment, E04-repeatability, E06-cross-platform-parity, E07-cross-layer-continuity, E12-localization-i18n. MOBILE_CONDITIONAL, only if a verification method drives a mobile build through the study runner: E11-security. UNDETERMINED, only if their configurations later include Android or iOS: E05-determinism, E10-visual. NO_MOBILE, not affected: E01-capability-audit (FROZEN; no runner-dependent execution), E08-performance (no mobile execution declared), E09-accessibility (Web only by the frozen modality list). The per-campaign impact matrix is in manifests/mobile-runner-policy-v3-amendment-proposal-v3.yaml.

## 1. Decision

| Role | Runner |
|---|---|
| Primary candidate | Mobilewright |
| Fallback | Appium 3 |

Appium 2 must NOT be used as the fallback or in any other role in this study. That runner is named in this protocol only to prohibit it.

Mobilewright was the primary candidate, not a selected runner: it could become the study's mobile runner only after passing the qualification gate in Sections 2–7. It did not pass: the protocol-valid gate, executed under v1 (MOBILE-QUALIFICATION-EXEC-AUTH-03, GitHub Actions run 35938250936, 2026-09-24), FAILED, and the frozen switch rule of Section 8 selected Appium 3, pinned 3.7.0, on 2026-09-24 (qualification/mobilewright/README.md; manifests/toolchain-manifest.yaml, mobile_runner_selection). The study uses one mobile runner for all ecosystems in all mobile campaigns; runners are never mixed across ecosystems within a campaign.

## 2. Qualification gate

Mobilewright must pass a separate qualification gate before it is used in any experimental campaign under experiments/ that involves the Android Native or iOS Native modalities.

- Executed by: QUALIFIER-MOBILE-01 (protocol/agent-governance-v1.md), only after an explicit instruction issued by a human and relayed by the ORCHESTRATOR (protocol/agent-governance-v1.md, section 2, rule 6). The instruction, its date, and its source are recorded in qualification/mobilewright/README.md before the first run.
- Recorded under: qualification/mobilewright/ (see qualification/README.md).
- Object of qualification: the runner, not any evaluated ecosystem. Gate records are tool-qualification records and are not evidence about any SUT.
- Purpose: to determine whether Mobilewright supports the mobile capabilities this study's campaigns require (Section 5). The gate is not a benchmark of Mobilewright against Appium 3 (Section 10).
- Status: executed under v1. The protocol-valid gate ran once under MOBILE-QUALIFICATION-EXEC-AUTH-03 (GitHub Actions run 35938250936, attempt 1, 2026-09-24; 6 warm-ups and 60 measured executions) and FAILED (qualification/mobilewright/README.md, "AUTH-03 formal gate"); an earlier execution of 2026-09-22 without a valid human authorization is preserved and quarantined (protocol/unresolved.md, PROTO-U10). Neither is reinterpreted (Section 11).

## 3. Qualification SUT

The initial qualification SUT is explicitly **OmniPizza (SUT-01)**, on the two platforms of Section 6 (Android emulator, iOS Simulator). The designation was made by explicit human instruction to the ORCHESTRATOR, as part of the pre-freeze hardening instruction of 2026-09-15, and is a tooling decision.

Neutrality statement (binding; also disclosed as a study limitation in every report):

- Qualification runs on OmniPizza produce no evidence about OmniPizza or any other ecosystem. No qualification artifact may be cited in any audits/ evidence record, adjudication output, campaign result, or analysis.
- Qualification confers no familiarity advantage and no privileged interpretation on OmniPizza. The auditors, the adjudicator, and the analysis treat SUT-01 exactly as SUT-02 … SUT-06 (protocol/study-design-v1.md, section 3).
- The concrete OmniPizza build used for qualification is pinned by the ORCHESTRATOR (repository, commit SHA or release, Android and iOS build identities, pinned_by, pinned_at) under `qualification_build` in manifests/toolchain-manifest.yaml before the first run and is identical for every gate execution. QUALIFIER-MOBILE-01 copies the pinned record verbatim into qualification/mobilewright/README.md, records any discrepancy between the record and the build it obtains in qualification/unresolved.md (created on first use; protocol/agent-governance-v1.md, section 6), and never selects or changes the build. The ORCHESTRATOR never writes under qualification/ (protocol/agent-governance-v1.md, section 4). These provenance fields were pinned by the ORCHESTRATOR on 2026-09-22, before the formal gate (manifests/toolchain-manifest.yaml, `qualification_build`: OmniPizza release v1.1.8, Android and iOS build identities with their SHA-256).
- The qualification SUT is not modified for qualification (AGENT-INSTRUCTIONS.md, rule 3).

## 4. Qualification scenarios

| ID | Scenario | Purpose |
|---|---|---|
| MQ1 | Login → Catalog | Navigation and selector compatibility |
| MQ2 | Catalog → Product Interaction | Native control interaction |
| MQ3 | API State Seed → Deep Link → Target UI State | Direct controlled mobile state establishment |

The scenario names are generic flows. The concrete screens, identifiers, seed request, deep link, and terminal UI state used to realize each scenario on the qualification SUT were recorded by QUALIFIER-MOBILE-01 in qualification/mobilewright/README.md (section "Scenario realization") before the first gate run and stayed identical for every execution (section SHA-256 f79acf6380cb82acabd1971e90a5fcfc339bee54146a239501d6b53b57239018, locked by manifests/mobile-qualification-implementation-lock-v1.yaml and, unchanged, by manifests/mobile-qualification-implementation-lock-v2.yaml). Each scenario has a pre-declared terminal UI state that the runner must verify (MC-08); a scenario execution is successful only when that state is verified.

- MQ1 starts from the app's initial screen after a clean reset, performs a login with a documented test account, and reaches the catalog screen.
- MQ2 starts at the catalog screen, includes at least one scroll or swipe gesture in the catalog, opens a product, and interacts with at least one native control on the product screen (for example a stepper, toggle, or button) such that a UI state change is observable.
- MQ3 establishes state through the SUT's API (the seed is performed by the harness, not by the runner), opens the app through a deep link that targets the seeded state, and verifies that the target UI state reflects the seeded state.

Atomic Helix Model and Atomic Testing are not research subjects of this study; no scenario or criterion in this policy is defined in those terms.

## 5. Mandatory runner capabilities

The following capabilities are mandatory. Each is exercised by at least one scenario on each platform. Support is assessed per capability per platform.

| ID | Capability | Exercised by |
|---|---|---|
| MC-01 | Install and launch the pinned app build on the target emulator or simulator | MQ1, MQ2, MQ3 |
| MC-02 | Locate UI elements by stable identifier (accessibility identifier, test id, resource id) | MQ1, MQ2, MQ3 |
| MC-03 | Enter text into native input controls | MQ1 |
| MC-04 | Tap or press native controls (buttons, list items, toggles) | MQ1, MQ2, MQ3 |
| MC-05 | Scroll or swipe within a native list or scroll view | MQ2 |
| MC-06 | Navigate between screens and verify arrival on the destination screen | MQ1, MQ2, MQ3 |
| MC-07 | Open the app through a deep link carrying parameters, from a cold or warm state, landing on the targeted screen | MQ3 |
| MC-08 | Read UI state (element presence, text, enabled or selected state) for oracle assertions | MQ1, MQ2, MQ3 |
| MC-09 | Reset app state between executions (clear app data or reinstall) so that each measured execution is clean | all (precondition) |
| MC-10 | Capture execution artifacts (log and screenshot) per execution | all |

The API seed step of MQ3 is performed outside the runner. A seed failure is an infrastructure or SUT-instance failure for attribution purposes (Section 7), never a runner failure and never evidence about the SUT.

## 6. Platform coverage

Qualification must cover both platforms:

- Android emulator (environment_type EMULATED)
- iOS Simulator (environment_type SIMULATED)

Each of MQ1–MQ3 is exercised on each platform: six scenario × platform combinations. Emulator and simulator identities (device profile, OS image or runtime, host platform) were recorded by the ORCHESTRATOR on 2026-09-22 in manifests/toolchain-manifest.yaml (`environments`: Android emulator system-images;android-35;google_apis;x86_64, profile pixel_7, on GitHub-hosted ubuntu-24.04; iOS Simulator iPhone 16 with the iOS 18.5 runtime of Xcode 16.4, on GitHub-hosted macos-15) and copied by QUALIFIER-MOBILE-01 into qualification/mobilewright/README.md before the formal gate. The same identities are used for every execution of the gate.

## 7. Pass gate

The following criteria are the pass criteria of the gate. They were fixed while protocol/mobile-runner-policy-v1.md was DRAFT, frozen with it on 2026-09-16 (FROZEN-PRE-DATA), applied unchanged to the formal gate of 2026-09-24, and are carried forward unchanged in v2 and in this version; they are not adjusted after any run.

### 7.1 Measured executions

- N = 10 clean measured executions per scenario × platform combination (6 combinations; 60 measured executions in total).
- A clean measured execution: starts from the declared reset state (MC-09 performed; for MQ3 the API seed applied and verified by the harness); is executed entirely by the runner under its scripted scenario; contains no manual intervention; and ends with the scenario's pre-declared terminal UI state verified by the runner (MC-08). An execution that does not meet every element is not clean; it is recorded as a failed measured execution unless it is excluded under 7.3.
- Warm-up: before the measured executions of a combination, any number of warm-up executions may be performed. Warm-ups are recorded (count, outcomes, notes) but never count toward N, neither as successes nor as failures under criterion 7.2.2. A runner-caused failure observed in a warm-up is nevertheless recorded and counts under criterion 7.2.3, because a repeated blocker of a mandatory capability is evidence about capability support whatever the kind of execution in which it occurs. Once the first measured execution of a combination starts, no further warm-up of that combination is permitted.
- Measured executions are sequential and each is recorded with: execution id, combination, platform, attempt number, timestamp, environment_type, Mobilewright version, outcome (SUCCESS, FAILURE, EXCLUDED), duration, artifact paths, and notes.

### 7.2 Pass criteria (all required)

1. **Capability support:** 100% support for all mandatory capabilities MC-01 … MC-10 on both platforms. A capability is supported on a platform when it was exercised in at least one successful measured execution on that platform and no runner-caused failure of that capability occurred in any measured execution on that platform.
2. **Reliability:** 10 of 10 successful measured executions for every one of the six scenario × platform combinations.
3. **No repeated runner-caused blocker:** the same mandatory capability is not blocked by a runner-caused failure in two or more executions of any kind (warm-up or measured, any combination).
4. **No manual intervention** inside any measured scenario. A measured execution that required manual intervention is a failed measured execution.

The gate passes only when all four criteria hold. It fails otherwise.

### 7.3 Exclusions and attribution

- Infrastructure failures unrelated to Mobilewright (emulator or simulator boot failure or crash, host resource exhaustion, SUT instance unavailability, API seed failure, network outage, operator error before the scenario started) are recorded separately and do not automatically fail the runner. An execution ended by such a failure is marked EXCLUDED and is replaced by an additional measured execution so that N = 10 measured executions are reached.
- Every excluded execution requires an explicit attribution record with: execution id; combination; timestamp; description of the failure; attributed cause, one of INFRASTRUCTURE, SUT_INSTANCE, API_SEED, OPERATOR, OTHER (never RUNNER); the artifacts that demonstrate the cause; and the recording role. An exclusion without a complete attribution record is invalid and the execution counts as a failed measured execution.
- A failure is runner-caused unless the attribution record demonstrates, with artifacts, a cause outside the runner. When attribution is uncertain, the failure is treated as runner-caused. This conservative rule mirrors the tie-break rule of protocol/capability-rubric-v1.md.
- Runner-caused failures are never excluded.

### 7.4 Secondary evidence

- Execution duration per measured execution is recorded and reported as secondary evidence only. It enters no pass criterion. Mobilewright must NOT be selected solely because it is faster, and duration cannot offset a deficit in any criterion of 7.2.

## 8. Switch rule

If the gate fails because a required capability (MC-01 … MC-10) is unsupported or unreliable under Mobilewright, or because criterion 7.2.3 or 7.2.4 is violated, the study's mobile runner switches to Appium 3. QUALIFIER-MOBILE-01 documents the reason, naming the failed criterion and capability. The switch is recorded in three places:

1. the decision record in qualification/mobilewright/README.md;
2. manifests/toolchain-manifest.yaml (mobile runner selection and version);
3. the change log, per protocol/change-control-v1.md.

A switch changes the study's tooling only. It does not change the evaluated ecosystems, the modality list, the research questions, or any hypothesis. The compatibility smoke of Section 9 then applies to Appium 3.

## 9. Per-SUT compatibility smoke

After the study mobile runner is selected (Mobilewright by passing the gate, or Appium 3 by the switch rule), and after E01 has verified which ecosystems have an Android or iOS surface, each mobile-capable ecosystem receives a lightweight compatibility smoke before it participates in E06, E07, or any other campaign that exercises its Android Native or iOS Native modality.

- Executed by: QUALIFIER-MOBILE-01, on explicit instruction (as in Section 2). Recorded under qualification/compatibility-smoke/ (template in qualification/compatibility-smoke/README.md).
- Scope per ecosystem × platform (each platform for which E01 confirmed a surface): install and launch the pinned build (MC-01); locate one element by stable identifier (MC-02); perform one navigation (MC-06); perform one native control interaction (MC-04); read one UI state (MC-08); capture artifacts (MC-10). One successful execution from a clean state passes the smoke for that ecosystem × platform.
- The smoke is not Mobilewright-versus-Appium benchmarking, produces no duration comparison, and produces no evidence about any ecosystem. It establishes only that the selected runner can drive that ecosystem's mobile build. Whether the ecosystem has a mobile surface is an E01 matter, never decided here.
- The same smoke definition applies to every ecosystem, SUT-01 included, even though SUT-01 was the qualification SUT.

### 9.1 Results

Each smoke of one ecosystem × platform has exactly one of three results; no other execution result exists.

| Result | Definition |
|---|---|
| PASS | One clean execution using the selected runner completed all six smoke capabilities: MC-01 (install and launch), MC-02 (stable-identifier location), MC-06 (navigation), MC-04 (native-control interaction), MC-08 (UI-state read), and MC-10 (artifact capture). |
| FAIL_RUNNER | The failure belongs to the selected runner's execution stack while the smoke capabilities were being attempted (9.2), or its attribution remains uncertain (9.4). |
| NOT_EXECUTED | Artifacts positively demonstrate that the selected runner was not fairly exercised because execution was prevented by a cause outside the runner (9.3). |

### 9.2 Runner and toolchain failures

The selected runner's execution stack is its pinned core, its pinned platform driver where the runner uses one, and the WebDriver-protocol behavior implemented by that stack. A failure belongs to that stack — result FAIL_RUNNER — when, on an otherwise valid pinned substrate and build, for example:

- the runner server or driver cannot establish the required session;
- a required stable-locator operation is unsupported or fails;
- a required navigation cannot be driven;
- a required native control cannot be driven;
- a required UI state cannot be read;
- runner-side artifact capture required by MC-10 cannot be completed.

A dependency or version incompatibility inside the pinned runner execution stack is runner/toolchain evidence, not automatically infrastructure.

### 9.3 Causes outside the runner

A smoke is NOT_EXECUTED only when artifacts positively demonstrate one of the following causes.

| Category | Demonstrated cause |
|---|---|
| SUT_BUILD | The pinned build cannot be obtained, verified, or installed, or is not executable on the predeclared compatible target despite the pinned artifact provenance (the v1 rule, preserved). |
| INFRASTRUCTURE | For example: the emulator or simulator fails to boot or crashes before the runner is exercised; a CI host or resource failure; a network or package-registry outage; a platform service outage; a host tool outside the selected runner fails before the selected runner can exercise the smoke. |
| HARNESS_ORCHESTRATION | A defect in the study-authored workflow, shell scripts, WebDriver client or harness, artifact plumbing, or configuration prevents the selected runner from being fairly exercised. This category requires positive artifacts demonstrating that defect; a failed runner command alone is never enough. |

The study-authored workflow, scripts, WebDriver client, and harness are not the runner. Every NOT_EXECUTED record includes: SUT; platform; timestamp; failed phase; attributed category; concrete description; artifact pointers; recording role. If the artifacts do not demonstrate an allowed cause, the attempt is not eligible for NOT_EXECUTED.

### 9.4 Conservative tie-break

When attribution remains uncertain after the preserved artifacts have been inspected, the result is FAIL_RUNNER, not NOT_EXECUTED. Uncertainty is never used to exclude an unfavorable runner outcome. This mirrors Section 7.3 and the tie-break rule of protocol/capability-rubric-v1.md. In particular, when the evidence cannot distinguish a defect of the study-authored harness from a failure of the runner stack, the result is FAIL_RUNNER.

### 9.5 Effects of each result

- **PASS** satisfies the compatibility requirement of that ecosystem × platform only.
- **NOT_EXECUTED** does not pass the smoke, does not fail the selected runner, and does not trigger the selection of another runner. The compatibility requirement of that exact ecosystem × platform remains unresolved, so every campaign condition that depends on it stays blocked. The authorized smoke stops there: nothing is repaired and continued within the same authorized smoke, and the next platform is not started when that would violate the prepared execution topology or make provenance ambiguous. A further attempt is never automatic; it requires the prior NOT_EXECUTED record and its artifacts preserved unchanged, the demonstrated cause corrected, and a new explicit human authorization. A continuous-integration re-run never substitutes for that authorization. If the correction changes execution-critical harness, workflow, or code, a successor implementation lock is created and approved before the new attempt.
- **FAIL_RUNNER while Mobilewright is the selected runner:** the runner cannot reliably support that capability for the experimental SUT set; the switch rule (Section 8) applies to the whole study and selects Appium 3. Any Appium 3 execution then requires its own preparation and explicit authorization. This general rule is carried from v1; it does not revisit any completed selection.
- **FAIL_RUNNER while Appium 3 is the selected runner** (selected under Section 8): the fallback is exhausted. Section 8 is not applied recursively to Appium 3; Appium 3 is not executed again to seek another result, except in the single post-fallback remediation qualification of 9.7 when all of its eligibility conditions hold; Appium 2 is never introduced (Section 1); no other runner is selected, silently or otherwise. The affected ecosystem × platform result remains FAIL_RUNNER, and the ORCHESTRATOR records the study-level mobile-runner status UNRESOLVED_AFTER_FALLBACK_FAILURE in manifests/toolchain-manifest.yaml and in the change log (while the selected runner remains usable, that status is SELECTED). From that moment every experimental campaign that requires mobile execution is blocked from START and from measurement until a new explicit protocol amendment decides the mobile-runner strategy. The failure alters no E01 evidence or capability score and is not evidence about any SUT. Section 9.7 is the only exception this version makes to this effect; it neither removes the exhaustion nor changes the FAIL_RUNNER.

A runner-caused failure of a mandatory capability for any ecosystem × platform in the experimental SUT set is a study-runner failure: one FAIL_RUNNER is sufficient for the two FAIL_RUNNER rules above.

### 9.6 Per-platform independence

The Android and iOS smokes of an ecosystem are distinct observations. A PASS on one platform never makes the other platform PASS; a NOT_EXECUTED on one platform does not alter the other platform's result. Results are never averaged, merged, or compensated across platforms or ecosystems. A FAIL_RUNNER on a single ecosystem × platform is nevertheless sufficient for 9.5.

### 9.7 Post-fallback remediation qualification (new in v3)

**9.7.1 Principle.** The historical FAIL_RUNNER of SUT-02 × iOS under APPIUM3-COMPAT-SMOKE-AUTH-02 was produced by the mandatory conservative tie-break of 9.4, while the post-run review also identified a concrete study-authored implementation and observability defect (qualification/unresolved.md, QUAL-U06). This section allows one prospective observation of that exact requirement after a correction restricted to that defect. It does not state that the historical FAIL_RUNNER was wrong, does not state that Appium 3 would pass on iOS, and does not remove the fallback exhaustion from the v2 record. The historical result stays valid under v2; a remediation observation is a new record under this version.

**9.7.2 Eligibility.** The mechanism may be used only when all of the following hold:

1. the selected fallback runner produced FAIL_RUNNER under the previous policy version;
2. that FAIL_RUNNER remains immutable;
3. its attribution was resolved through the previous version's conservative tie-break (9.4);
4. preserved post-run evidence identified a concrete study-authored implementation or observability defect relevant to fair runner exercise;
5. that defect was insufficiently demonstrated as the historical run's cause, so the historical result was not reclassified;
6. the affected campaigns have not yet collected experimental measurements requiring the repaired execution path;
7. explicit human approval of this post-data amendment occurred before any new qualification execution.

The only requirement that can meet these conditions under this version is SUT-02 × iOS × Appium 3 (APPIUM3-COMPAT-SMOKE-AUTH-02, run 36539790536: FAIL_RUNNER, basis CONSERVATIVE_TIE_BREAK_ATTRIBUTION_UNCERTAIN; defect QUAL-U06). No other FAIL_RUNNER, ecosystem, platform, or runner is eligible. The mechanism is not a generic retry rule.

**9.7.3 Scope.** One remediation qualification of SUT-02 × iOS × Appium 3 only. SUT-02 × Android is not executed again: its official PASS under APPIUM3-COMPAT-SMOKE-AUTH-02 remains an immutable valid compatibility observation, per-platform independence (9.6) remains binding, and a successful iOS remediation may combine prospectively with that already-recorded Android PASS for per-platform compatibility admission (9.7.9, 9.7.12); this does not reinterpret AUTH-02. The remediation qualification is not a re-run or continuation of APPIUM3-COMPAT-SMOKE-AUTH-02, not a repeat of Android, not a Mobilewright comparison, and not a new research question. The smoke scope of Section 9 (MC-01, MC-02, MC-06, MC-04, MC-08, MC-10) and the PASS definition of 9.1 are unchanged.

**9.7.4 Permitted correction.** Any implementation correction for the remediation qualification is restricted to QUAL-U06. The corrected study-authored WebDriver transport:

1. coordinates the effective HTTP transport timeout with the predeclared iOS session-start budget;
2. cannot silently impose a shorter timeout than the explicit session timeout;
3. preserves the underlying transport error cause in formal evidence, including where available the error name, error code, and error message and the cause name, cause code, and cause message;
4. leaves the Appium 3 and XCUITest driver pins unchanged;
5. leaves the SUT build unchanged;
6. leaves the iOS Simulator and Xcode substrate unchanged;
7. leaves the smoke capability definition unchanged;
8. leaves the semantic iOS realization unchanged;
9. leaves the WebDriverAgent launch and connection limits unchanged, unless an independent pre-execution compatibility reason requires otherwise and is separately approved.

No other execution-critical change is authorized merely because this version exists.

**9.7.5 Exactly one attempt.** At most one formal remediation qualification attempt exists under this version. It requires, each separately: the corrected implementation; a successor implementation lock (lock v4); static validation; a new authorization id; explicit human issuance; public publication of the frozen baseline; and a separate explicit human dispatch. No GitHub re-run, no automatic retry, and no second remediation attempt under this version: a run attempt greater than 1, a second dispatch, or a second remediation execution is never an attempt under 9.7 and invalidates the remediation lineage (9.7.9, condition 3).

**9.7.6 Results and attribution.** The result vocabulary and attribution rules of 9.1–9.4 apply unchanged: PASS, FAIL_RUNNER, or NOT_EXECUTED; NOT_EXECUTED only on a positively demonstrated cause outside the runner (9.3); uncertain attribution is FAIL_RUNNER (9.4). No new result category exists.

**9.7.7 Effects (single-attempt, terminal).**

| Remediation result | Historical records | SUT-02 × iOS | Study-level mobile-runner status | Mobile execution |
|---|---|---|---|---|
| PASS | the APPIUM3-COMPAT-SMOKE-AUTH-02 iOS FAIL_RUNNER and the v2 exhaustion stay preserved and valid under v2 | PASS, recorded as a new observation under this version | SELECTED, recorded prospectively by the ORCHESTRATOR only through the effective-admissibility rule (9.7.9) and the remediation lineage record (9.7.10), with the basis "restored under mobile-runner-policy-v3 after one successful post-fallback remediation qualification" (recorded in tools.mobile_runner_selection.restoration_basis of manifests/toolchain-manifest.yaml, a field created only after a remediation PASS and only on an explicit human restoration instruction) | admissible prospectively for campaigns governed by this version, subject to every other gate; the existing SUT-02 × Android PASS may satisfy its platform-specific requirement provided all provenance and G-7 checks remain valid |
| FAIL_RUNNER | unchanged | FAIL_RUNNER | UNRESOLVED_AFTER_FALLBACK_FAILURE (unchanged) | blocked; no second remediation qualification under this version |
| NOT_EXECUTED | unchanged | NOT_EXECUTED | UNRESOLVED_AFTER_FALLBACK_FAILURE (unchanged) | blocked; no automatic retry; a further attempt requires another explicit post-data protocol amendment |

The restoration applies only prospectively to campaigns governed by this version and alters no record made under v1 or v2.

**9.7.8 Records.** QUALIFIER-MOBILE-01 records the remediation attempt as new rows (a smoke-record row and, where 9.3 or the attribution rule requires it, an attribution row) in qualification/compatibility-smoke/README.md, and imports its artifacts byte-exact under its own authorization namespace. The historical rows and imported artifacts are never edited, moved, removed, downgraded, or reclassified. The ORCHESTRATOR transcribes the new result into the SUT-02 × iOS entry of manifests/compatibility-smoke-status.yaml, keeping the previous value in its comments. Table position never decides admissibility: admission is governed only by 9.7.9 and 9.7.10.

**9.7.9 Historical observation and prospective admissibility.** This version distinguishes:

- **Historical observation:** the immutable result produced under the protocol version that governed its execution. It is never deleted, overwritten, downgraded, or reclassified. The APPIUM3-COMPAT-SMOKE-AUTH-02 iOS FAIL_RUNNER remains permanently present as a valid v2 observation.
- **Current prospective admissibility state:** the state allowed to govern future campaign admission, including admission after a protocol-authorized remediation.

The effective compatibility observation of an ecosystem × platform for admission is determined as follows: a PASS is an effective PASS; a NOT_EXECUTED is a non-result (it neither passes nor fails, 9.5) and is superseded by the result of any later authorized attempt of the same ecosystem × platform, as under v2; a FAIL_RUNNER is never superseded by a later row or by table order, and ceases to block only as follows.

A historical FAIL_RUNNER may cease to block future mobile execution only when every requirement below holds:

1. it is the exact FAIL_RUNNER named as the trigger of the approved v3 remediation (APPIUM3-COMPAT-SMOKE-AUTH-02, run 36539790536, SUT-02 × iOS);
2. this version, approved and frozen, explicitly authorizes remediation of that exact observation (9.7.2);
3. exactly one remediation execution exists (one authorization, one dispatch, run attempt 1);
4. the remediation uses a new authorization id;
5. the remediation uses the approved successor implementation lock;
6. the remediation targets only the affected ecosystem × platform;
7. its official QUALIFIER-MOBILE-01 result is PASS;
8. its artifact provenance is complete and valid (imported byte-exact, digests equal to the recorded digests);
9. its mirror transcription is PASS;
10. the study-level restoration record, the remediation lineage record of 9.7.10, references the historical FAIL_RUNNER, the remediation authorization, the remediation run id, protocol v3, the implementation lock, and the PASS source record; its verification includes that the named historical FAIL_RUNNER still exists unchanged (its smoke-record row with the recorded authorization, run, and result, and its imported artifacts byte-exact against their import record);
11. mobile_runner_status is explicitly restored to SELECTED under this version;
12. no other unresolved FAIL_RUNNER exists for the selected runner on any ecosystem × platform.

If any requirement is absent or cannot be verified, the state fails closed: every mobile condition stays blocked. When all hold, the named historical FAIL_RUNNER is retained but no longer counted as an unresolved current blocker; every other FAIL_RUNNER keeps blocking; admission then evaluates each ecosystem × platform's effective compatibility observation.

**9.7.10 Remediation lineage record.** After a remediation PASS, and only on an explicit human restoration instruction, the ORCHESTRATOR writes one remediation lineage record, manifests/mobile-runner-remediation-v1.yaml, and records the restoration basis of 9.7.7 in tools.mobile_runner_selection.restoration_basis of manifests/toolchain-manifest.yaml; neither the record nor the field exists before then. It is the normative provenance of the restoration for G-7 of the measured-execution workflow; admission never relies on table ordering alone. It carries at least: the prior policy (v2) and the new policy (v3); the historical failing authorization (APPIUM3-COMPAT-SMOKE-AUTH-02), run (36539790536), ecosystem × platform (SUT-02 × iOS), and result (FAIL_RUNNER), with historical_result_immutable true; the remediation authorization id; the remediation run id and run attempt; the remediation implementation lock id and SHA-256; the remediation official result and its QUALIFIER-MOBILE-01 source record; the restoration eligibility (each requirement of 9.7.9 with its evidence); the restored runner status; and the human approval provenance (the approval of this version and the instruction authorizing the restoration). It is written once and never edited; it never covers a second remediation.

**9.7.11 After restoration.** A restoration under 9.7.9 is not a new selection and is not permanent immunity. Any FAIL_RUNNER of the selected runner recorded after the restoration, on any ecosystem × platform, applies 9.5 again: the study-level status returns to UNRESOLVED_AFTER_FALLBACK_FAILURE and every campaign requiring mobile execution is blocked. No second remediation exists under this version, and the lineage record of 9.7.10 never extends to another observation. A FAIL_RUNNER that arises only after a valid restoration does not invalidate the lineage record of the restored observation; that later FAIL_RUNNER is itself unresolved and blocks under 9.5. A FAIL_RUNNER that already existed when the status was to be restored makes the restoration invalid (9.7.9, condition 12).

**9.7.12 SUT-02 × Android PASS and the shared WebDriver client.** The correction permitted by 9.7.4 may change the study-authored WebDriver client (qualification/compatibility-smoke/harness/wd.mjs), which the Android smoke also uses, although Android is not executed again. The AUTH-02 Android PASS remains valid for the following reasons, which are its methodological basis:

1. The object of the compatibility smoke is the selected runner's execution stack (9.2): Appium 3.7.0 with its pinned platform driver and the WebDriver-protocol behavior they implement. The study-authored workflow, scripts, WebDriver client, and harness are not the runner (9.3).
2. The Android PASS consists of the runner's answers to W3C WebDriver commands whose endpoints, payloads, locators, realization, and oracle (expected product detail, quantity 1 then 2) the QUAL-U06 correction does not change. The correction only lets the client wait up to the declared budget instead of a shorter implicit transport limit, and records the underlying cause of transport failures.
3. The recorded Android session request completed in 24.9 s and every recorded Android command received a normal response, so no transport limit bore on any recorded Android exchange; a longer permitted wait and a richer failure record cannot change the classification of an exchange that completed normally.
4. The Android PASS is therefore evidence that Appium 3.7.0 with appium-uiautomator2-driver 8.7.0 exercises MC-01, MC-02, MC-06, MC-04, MC-08, and MC-10 on the pinned SUT-02 Android build; the remediation exists to exercise iOS session establishment fairly, not to change the Android capability definition.
5. Conditions: the successor lock must show that the Android realization (REALIZATION.android of qualification/compatibility-smoke/harness/smoke.mjs) and the Android command sequence are byte-unchanged; if any Android-relevant realization byte changed, the Android PASS could no longer be combined under 9.7.9 and this basis would not hold. The compatibility smoke qualifies the runner for an ecosystem × platform; it does not qualify a campaign executor, which is governed by its own campaign gates.

**9.7.13 No other runner.** The runner of the remediation qualification is Appium 3, pinned 3.7.0, with its pinned XCUITest driver. This version introduces no other runner: Appium 2 is never introduced (Section 1); Mobilewright is not re-qualified; no other third-party runner (for example Maestro or Detox) is introduced. Choosing another runner would require its own separate protocol decision.

## 10. Scope limit

Mobilewright vs Appium is NOT a primary research question of this study. The gate and the smoke select a fit-for-purpose runner; they do not compare runners as a study outcome. QUALIFIER-MOBILE-01 cannot turn the runner comparison into a research question unless explicitly authorized through the change-control process in protocol/change-control-v1.md, which requires human approval.

## 11. Status

Snapshot at the freeze of this version (2026-10-02); not updated in place. Live status: manifests/toolchain-manifest.yaml and manifests/compatibility-smoke-status.yaml.

| Item | State |
|---|---|
| This version | FROZEN-PRE-DATA: approved by gilbertosanchez on 2026-10-02 and frozen on 2026-10-02; in force; its freeze authorizes no execution |
| Qualification runs executed | Under v1: one protocol-valid gate (MOBILE-QUALIFICATION-EXEC-AUTH-03, GitHub Actions run 35938250936, 2026-09-24), result FAIL (qualification/mobilewright/README.md); an earlier execution of 2026-09-22 is preserved and quarantined (protocol/unresolved.md, PROTO-U10). Neither is reinterpreted under this version. |
| Compatibility smokes executed | Under v2: APPIUM3-COMPAT-SMOKE-AUTH-01 (run 36340774530, 2026-09-27): SUT-02 × Android NOT_EXECUTED / HARNESS_ORCHESTRATION, SUT-02 × iOS not attempted; APPIUM3-COMPAT-SMOKE-AUTH-02 (run 36539790536, 2026-09-29): SUT-02 × Android PASS, SUT-02 × iOS FAIL_RUNNER (9.4 tie-break). Neither is reinterpreted under this version. |
| Mobile runner installed | none for study use; Appium 3.7.0 installed only on the GitHub-hosted runners of the two compatibility smokes |
| Mobilewright version | 0.0.60 pinned (manifests/toolchain-manifest.yaml); qualification FAILED |
| Appium 3 version | 3.7.0 pinned; 3.7.0 formally observed in both compatibility smokes and recorded as tools.mobile_fallback.version on 2026-09-29 (manifests/toolchain-manifest.yaml; manifests/appium3-toolchain-version-transcription-v1.yaml) |
| Qualification SUT | OmniPizza (SUT-01); build pinned under `qualification_build` in manifests/toolchain-manifest.yaml |
| Runner decision | Appium 3, pinned 3.7.0, selected by the Section 8 switch under v1 on 2026-09-24; study-level mobile-runner status UNRESOLVED_AFTER_FALLBACK_FAILURE since 2026-09-29 (v2, 9.5) |
| Post-fallback remediation qualification (9.7) | in force as a rule; not authorized for execution: no corrected implementation, successor implementation lock, authorization, publication, or dispatch exists; effective-admissibility rule (9.7.9) in force; remediation lineage record (9.7.10) defined, not created |

## 12. Versioning

This document is protocol version v3 of the mobile runner policy, state FROZEN-PRE-DATA (prepared as a DRAFT on 2026-09-29, hardened in place and corrected for freeze readiness the same day; frozen 2026-10-02 under the explicit human approval of 2026-10-02 recorded in its header; no data had been collected under this version when it was frozen), and follows the protocol state lifecycle (DRAFT, FROZEN-PRE-DATA, AMENDED, SUPERSEDED) defined in protocol/change-control-v1.md. It supersedes protocol/mobile-runner-policy-v2.md, which is AMENDED and retained unchanged apart from its header; the approval and freeze are recorded in protocol/CHANGELOG.md with rationale and affected campaigns (protocol/change-control-v1.md, section 5). The introductory paragraph, 9.1–9.4, 9.6, and Section 10 are carried over from v2 verbatim; Sections 1–8 are carried over with status and provenance corrections only (in Sections 1, 2, 3, 4, 6, and 7; no methodological change); 9.5 gains one bounded exception clause; 9.7 is new; Sections 11 and 12 and the header are updated. It is never overwritten in place; any modification creates protocol/mobile-runner-policy-v4.md.
