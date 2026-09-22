# SUT-02 — Sauce Labs Demo Ecosystem — Limitations

| Field | Value |
|---|---|
| SUT id | SUT-02 |
| Auditor role | AUDITOR-SUT02-SAUCELABS |
| Audit status | SUBMITTED |

## Purpose

Records, neutrally and descriptively, what bounds the audit of the system under test (SUT) SUT-02: what the ecosystem intentionally does not cover, what the auditor could not verify and why, environment constraints, and environment considerations. Entries are cross-referenced from audit.md (structural_scope_note column and section 6) and from evidence.csv notes. Nothing here is a score, a finding, or a ranking input.

Intentionally narrow scope is not a penalty. An ecosystem that deliberately does not cover a modality is described here in neutral terms; the corresponding row in audit.md section 3 carries a structural_scope_note, the score remains the rubric score (Score 0 for a structurally absent surface; no N/A level), and the capability rubric (protocol/capability-rubric-v1.md) is applied unchanged. Experimental Breadth and Modality Depth answer different questions (protocol/study-design-v1.md, section 11).

## Scope limitations of the ecosystem (intentional)

None documented by the vendor. The three READMEs (web, android, ios) describe the ecosystem only as a general demo built "to showcase product capabilities of the Sauce Labs mobile devices cloud, The Sauce Labs mobile beta testing platform, TestFairy, and more" — a general-purpose statement, not a stated intentional narrowing to a specific modality or surface. The absence of a business-data API surface (audit.md, API modality, Score 0, NO_API_SURFACE) is a structural finding produced by this audit's search (evidence.csv SUT02-EV-0004, SUT02-EV-0005, SUT02-EV-0006), not a scope decision Sauce Labs documented anywhere in the three repositories.

## Evaluation limitations (what the auditor could not verify and why)

Includes the evidence ceiling where SOURCE_VERIFIED is unobtainable for a closed-source or hosted-only component (protocol/evidence-rules-v1.md): the ecosystem is not penalized; the strongest obtainable status is recorded.

- **No evidence ceiling applies to this SUT.** All three pinned components (web, android, ios) are open-source and were read directly at the pinned commit/tag; every evidence.csv record reached SOURCE_VERIFIED. The one hosted-only surface identified (the `my-demo-app.net/api/analytics/collect/` telemetry endpoint android calls, SUT02-EV-0005) was recorded from the calling source code itself, not probed by execution — probing it would not change the API modality score (it is write-only, undocumented telemetry, not a business-data surface) and would risk a state-changing interaction against a PUBLIC_HOSTED endpoint outside this audit's execution-safety rules.
- **No execution was performed.** Every record in evidence.csv is SOURCE_VERIFIED from static reading of the three read-only local checkouts under `../e01-sut-sources/SUT-02-saucelabs/{web,android,ios}/`; no local build, no Android emulator, no iOS Simulator, and no interaction with a PUBLIC_HOSTED instance (saucedemo.com or otherwise) was attempted. This audit therefore contains zero EXECUTION_VERIFIED records and no `verifications/`/`artifacts/` directories were created.
- **`controlled_instance_available` is left null.** protocol/study-design-v1.md, section 10.5, requires this to be null until verified and never inferred. Verifying it would require actually building/running web (Dockerfile present, not exercised), android (Gradle project, not built), and ios (Xcode project, not built) — none of which this audit attempted.
- **Search was targeted, not exhaustive.** Given three separate multi-hundred-file codebases, source reading was directed at the mechanisms named as Score-3 examples in protocol/capability-rubric-v1.md (deterministic test accounts, reset/logout, deep links, locale selection, documented intentional vulnerabilities/faults, API calls) rather than a line-by-line read of every file. A modality-relevant mechanism outside that targeted search could exist unfound; none is asserted absent beyond what was actually searched and recorded as negative evidence (evidence.csv; audit.md section 6).
- **Automation Affordances on android/ios not specifically searched.** web's `data-test` attribute convention was confirmed in source (SUT02-EV-0001). Whether android and ios use an equivalent stable-identifier convention (`android:contentDescription` / Espresso resource-id patterns; `accessibilityIdentifier`) was not specifically checked during this audit; their presence or absence is not asserted in audit.md section 4.
- **Documentation-vs-implementation contradiction (ios locked-out account).** audit.md section 5: ios's `Authentication.storyboard` implies alice@example.com is a distinguished account, but the pinned `LoginViewController` does not enforce a lock-out for it (unlike android). This does not lower iOS Native's confirmed_score, since the Reset App State and visual@example.com mechanisms independently satisfy Score 3 (SUT02-EV-0009, SUT02-EV-0017).
- **android ambient resource-churn confound.** `DeviceVitalsDemo.memorySawtooth` (SUT02-EV-0012) runs unconditionally from app launch, allocating/releasing memory on a fixed timer with no activation control; it is not used to support the Performance score (it cannot be "established, activated, configured, seeded, or reset" by the experimenter), but is recorded here as a known confound for any future E08 performance measurement taken on the android surface.

## Environment limitations

No local, emulated, or simulated environment was established for any of the three components. android requires an Android SDK/emulator toolchain; ios requires Xcode and an iOS Simulator; neither was installed or exercised. web has a Dockerfile in the pinned repository (`60fdd634…`) suggesting a straightforward SELF_HOSTED/LOCAL path exists, but it was not attempted. All findings in this audit are from static source reading of the three pinned, read-only local checkouts only.

## Environment considerations

Environment types used (PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, OTHER; protocol/study-design-v1.md, section 10), whether a controlled instance of the pinned version could be established, and any constraint of a shared public instance on what could be verified. Environment is provenance, not utility.

None used. `environment_types_used` in audit.md section 1 is empty because this audit produced no EXECUTION_VERIFIED evidence at any environment type — not because an environment was tried and found unavailable. No interaction of any kind (documented, non-destructive, or otherwise) was made with any PUBLIC_HOSTED deployment (for example saucedemo.com) during this audit.
