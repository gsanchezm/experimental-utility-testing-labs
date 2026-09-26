# Mobile Runner Policy

| Field | Value |
|---|---|
| Document | protocol/mobile-runner-policy-v2.md |
| Protocol version | v2 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-26 |
| Supersedes | protocol/mobile-runner-policy-v1.md (transitions to AMENDED by this freeze, per protocol/change-control-v1.md, section 2 — `data_collection_started` is already true) |
| Freeze approval | gilbertosanchez, 2026-09-25 (explicit human approval of the post-data amendment decision resolving protocol/unresolved.md PROTO-U17, instruction "RESOLVE PROTO-U17 THROUGH MOBILE-RUNNER-POLICY-V2 AND RE-LOCK THE APPIUM 3 COMPATIBILITY SMOKE", which authorized creating and freezing this document; text written by the ORCHESTRATOR from the approved rules and frozen on 2026-09-26 under that instruction; post-data-collection change under protocol/change-control-v1.md, section 5; record manifests/mobile-runner-policy-v2-amendment-v1.yaml) |

This policy governs which mobile test runner the study uses for the Android Native and iOS Native modalities and the conditions under which it may be used. It applies to every evaluated ecosystem (system under test, SUT) identically.

## What changed relative to v1, and why

protocol/unresolved.md, PROTO-U17 (raised 2026-09-24 while the Appium 3 compatibility smoke for SUT-02 was being prepared, before any smoke outcome existed) showed that v1's Section 9 left the terminal and failure behavior of the compatibility smoke undefined once Appium 3 itself is the selected runner: v1 knew only NOT_EXECUTED for a build that cannot be obtained or installed, gave no result for an execution prevented by infrastructure or by a defect of the study-authored harness, and on a runner-caused failure required the smoke to be "repeated with the fallback runner", although after the Section 8 switch no further fallback exists. On 2026-09-25 the human research lead approved the amendment decision recorded here.

**Only Section 9 changes in substance.** Its result vocabulary is unchanged (PASS, FAIL_RUNNER, NOT_EXECUTED) and PASS keeps its v1 criterion. New: the explicit definition of the selected runner's execution stack and of FAIL_RUNNER (9.2); NOT_EXECUTED extended from the build cause to three positively demonstrated causes outside the runner — SUT_BUILD, INFRASTRUCTURE, HARNESS_ORCHESTRATION — with a mandatory record (9.3); the conservative tie-break, uncertain attribution → FAIL_RUNNER (9.4); the effects of each result, including no automatic replacement attempt and the exhausted-fallback rule with the study-level mobile-runner status UNRESOLVED_AFTER_FALLBACK_FAILURE (9.5); per-platform independence (9.6). Section 11 (status) and Section 12 (versioning) are updated. The introductory paragraph, Sections 1–8, and Section 10 are carried over from v1 byte for byte, so the Mobilewright primary-candidate role, the Appium 3 fallback, the prohibition of Appium 2, the qualification SUT, MQ1–MQ3, MC-01 … MC-10, N, the Section 7 exclusion and attribution rules, the pass gate, and the Section 8 switch are unchanged; their status phrases ("Not executed at this time", "null / TBD now", "null / TBD until pinned") describe the state at v1's freeze of 2026-09-16 and are historical (current status: Section 11).

**Prior data validity (protocol/change-control-v1.md, section 5, item 3).** E01-capability-audit: unaffected; all collected data and results remain valid. The H1 analysis: unaffected. The Mobilewright formal qualification (MOBILE-QUALIFICATION-EXEC-AUTH-03, 2026-09-24) is a tool-qualification record, not a campaign: unaffected, and valid under the v1 criteria used for that execution; it is not reinterpreted through this version, and the Section 8 selection of Appium 3 made under v1 stands. No compatibility-smoke data existed under v1. No experimental data requires re-collection or re-analysis.

**Affected campaigns (prospectively; none has collected data):** E03-resetability (its SUT-02 Android and iOS conditions depend on the compatibility smoke); E06-cross-platform-parity and E07-cross-layer-continuity (Android and iOS surfaces); E12-localization-i18n for any mobile execution; and any future campaign exercising Android Native or iOS Native.

## 1. Decision

| Role | Runner |
|---|---|
| Primary candidate | Mobilewright |
| Fallback | Appium 3 |

Appium 2 must NOT be used as the fallback or in any other role in this study. That runner is named in this protocol only to prohibit it.

Mobilewright is a candidate, not a selected runner. It becomes the study's mobile runner only after passing the qualification gate in Sections 2–7. The study uses one mobile runner for all ecosystems in all mobile campaigns; runners are never mixed across ecosystems within a campaign.

## 2. Qualification gate

Mobilewright must pass a separate qualification gate before it is used in any experimental campaign under experiments/ that involves the Android Native or iOS Native modalities.

- Executed by: QUALIFIER-MOBILE-01 (protocol/agent-governance-v1.md), only after an explicit instruction issued by a human and relayed by the ORCHESTRATOR (protocol/agent-governance-v1.md, section 2, rule 6). The instruction, its date, and its source are recorded in qualification/mobilewright/README.md before the first run.
- Recorded under: qualification/mobilewright/ (see qualification/README.md).
- Object of qualification: the runner, not any evaluated ecosystem. Gate records are tool-qualification records and are not evidence about any SUT.
- Purpose: to determine whether Mobilewright supports the mobile capabilities this study's campaigns require (Section 5). The gate is not a benchmark of Mobilewright against Appium 3 (Section 10).
- Not executed at this time. No qualification run has occurred (Section 11).

## 3. Qualification SUT

The initial qualification SUT is explicitly **OmniPizza (SUT-01)**, on the two platforms of Section 6 (Android emulator, iOS Simulator). The designation was made by explicit human instruction to the ORCHESTRATOR, as part of the pre-freeze hardening instruction of 2026-09-15, and is a tooling decision.

Neutrality statement (binding; also disclosed as a study limitation in every report):

- Qualification runs on OmniPizza produce no evidence about OmniPizza or any other ecosystem. No qualification artifact may be cited in any audits/ evidence record, adjudication output, campaign result, or analysis.
- Qualification confers no familiarity advantage and no privileged interpretation on OmniPizza. The auditors, the adjudicator, and the analysis treat SUT-01 exactly as SUT-02 … SUT-06 (protocol/study-design-v1.md, section 3).
- The concrete OmniPizza build used for qualification is pinned by the ORCHESTRATOR (repository, commit SHA or release, Android and iOS build identities, pinned_by, pinned_at) under `qualification_build` in manifests/toolchain-manifest.yaml before the first run and is identical for every gate execution. QUALIFIER-MOBILE-01 copies the pinned record verbatim into qualification/mobilewright/README.md, records any discrepancy between the record and the build it obtains in qualification/unresolved.md (created on first use; protocol/agent-governance-v1.md, section 6), and never selects or changes the build. The ORCHESTRATOR never writes under qualification/ (protocol/agent-governance-v1.md, section 4). These provenance fields are null / TBD until pinned.
- The qualification SUT is not modified for qualification (AGENT-INSTRUCTIONS.md, rule 3).

## 4. Qualification scenarios

| ID | Scenario | Purpose |
|---|---|---|
| MQ1 | Login → Catalog | Navigation and selector compatibility |
| MQ2 | Catalog → Product Interaction | Native control interaction |
| MQ3 | API State Seed → Deep Link → Target UI State | Direct controlled mobile state establishment |

The scenario names are generic flows. The concrete screens, identifiers, seed request, deep link, and terminal UI state used to realize each scenario on the qualification SUT are recorded by QUALIFIER-MOBILE-01 in qualification/mobilewright/README.md before the first run; they are null / TBD now. Each scenario has a pre-declared terminal UI state that the runner must verify (MC-08); a scenario execution is successful only when that state is verified.

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

Each of MQ1–MQ3 is exercised on each platform: six scenario × platform combinations. Emulator and simulator identities (device profile, OS image or runtime, host platform) are null / TBD; the ORCHESTRATOR records them in manifests/toolchain-manifest.yaml and QUALIFIER-MOBILE-01 copies them into qualification/mobilewright/README.md before runs. The same identities are used for every execution of the gate.

## 7. Pass gate

The following criteria are the pass criteria of the gate. They were fixed while this document was DRAFT and are now frozen with the protocol (state FROZEN-PRE-DATA); they are not adjusted after any run.

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
- **FAIL_RUNNER while Appium 3 is the selected runner** (selected under Section 8): the fallback is exhausted. Section 8 is not applied recursively to Appium 3; Appium 3 is not executed again to seek another result; Appium 2 is never introduced (Section 1); no other runner is selected, silently or otherwise. The affected ecosystem × platform result remains FAIL_RUNNER, and the ORCHESTRATOR records the study-level mobile-runner status UNRESOLVED_AFTER_FALLBACK_FAILURE in manifests/toolchain-manifest.yaml and in the change log (while the selected runner remains usable, that status is SELECTED). From that moment every experimental campaign that requires mobile execution is blocked from START and from measurement until a new explicit protocol amendment decides the mobile-runner strategy. The failure alters no E01 evidence or capability score and is not evidence about any SUT.

A runner-caused failure of a mandatory capability for any ecosystem × platform in the experimental SUT set is a study-runner failure: one FAIL_RUNNER is sufficient for the two FAIL_RUNNER rules above.

### 9.6 Per-platform independence

The Android and iOS smokes of an ecosystem are distinct observations. A PASS on one platform never makes the other platform PASS; a NOT_EXECUTED on one platform does not alter the other platform's result. Results are never averaged, merged, or compensated across platforms or ecosystems. A FAIL_RUNNER on a single ecosystem × platform is nevertheless sufficient for 9.5.

## 10. Scope limit

Mobilewright vs Appium is NOT a primary research question of this study. The gate and the smoke select a fit-for-purpose runner; they do not compare runners as a study outcome. QUALIFIER-MOBILE-01 cannot turn the runner comparison into a research question unless explicitly authorized through the change-control process in protocol/change-control-v1.md, which requires human approval.

## 11. Status

Snapshot at the freeze of this version (2026-09-26); not updated in place. Live status: manifests/toolchain-manifest.yaml and manifests/compatibility-smoke-status.yaml.

| Item | State |
|---|---|
| Qualification runs executed | Under v1: one protocol-valid gate (MOBILE-QUALIFICATION-EXEC-AUTH-03, GitHub Actions run 35938250936, 2026-09-24), result FAIL (qualification/mobilewright/README.md); an earlier execution of 2026-09-22 is preserved and quarantined (protocol/unresolved.md, PROTO-U10). Neither is reinterpreted under this version. |
| Compatibility smokes executed | none |
| Mobile runner installed | none |
| Mobilewright version | 0.0.60 pinned (manifests/toolchain-manifest.yaml); qualification FAILED |
| Appium 3 version | 3.7.0 pinned (manifests/toolchain-manifest.yaml); not installed |
| Qualification SUT | OmniPizza (SUT-01); build pinned under `qualification_build` in manifests/toolchain-manifest.yaml |
| Runner decision | Appium 3, pinned 3.7.0, selected by the Section 8 switch under v1 on 2026-09-24; study-level mobile-runner status SELECTED |

## 12. Versioning

This document is protocol version v2 of the mobile runner policy, state FROZEN-PRE-DATA (frozen 2026-09-26 under the explicit human approval of 2026-09-25 recorded in its header; no data had been collected under this version when it was frozen), and follows the protocol state lifecycle (DRAFT, FROZEN-PRE-DATA, AMENDED, SUPERSEDED) defined in protocol/change-control-v1.md. It supersedes protocol/mobile-runner-policy-v1.md, which is AMENDED and retained unchanged apart from its header. The introductory paragraph, Sections 1–8, and Section 10 are carried over from v1 verbatim; only Section 9 changed in substance, and Sections 11 and 12 were updated. It is never overwritten in place; any modification creates protocol/mobile-runner-policy-v3.md.
