# Qualification

Tool-qualification records for study EUS-2026-001 (Experimental Utility of Software-Testing Laboratory Ecosystems).

## Purpose

This directory holds qualification of study tooling. Tool qualification is separate from evaluation of any system under test (SUT): it establishes whether a tool is fit for use in the study's experimental campaigns, and nothing else. Nothing in this directory audits, scores, or characterizes an evaluated ecosystem.

## Contents

| Path | Content | Governing policy |
|---|---|---|
| qualification/mobilewright/ | Mobilewright qualification gate (MQ1 Login → Catalog; MQ2 Catalog → Product Interaction; MQ3 API State Seed → Deep Link → Target UI State; on Android emulator and iOS Simulator; qualification SUT OmniPizza; N = 10 measured executions per combination) and the runner decision record | protocol/mobile-runner-policy-v1.md, Sections 2–8 |
| qualification/compatibility-smoke/ | Per-SUT compatibility smoke of the selected runner on every mobile-capable ecosystem before mobile campaigns | protocol/mobile-runner-policy-v2.md, Section 9 (v1 AMENDED 2026-09-26) |
| qualification/unresolved.md | Escalations raised in this workspace, same table format as the audit unresolved.md files; created 2026-09-22 (first use) with QUAL-U01, the execution-authorization conflict of the 2026-09-22 gate (mirrored as protocol/unresolved.md PROTO-U10); QUAL-U02, the pre-dispatch execution-integrity defects (PROTO-U12); QUAL-U03, the post-run MQ3 `runner.log` token-fragment hygiene deviation (PROTO-U13, RESOLVED 2026-09-24: publication-only redaction defined) | protocol/agent-governance-v1.md, section 6 |

The gate definition, mandatory capabilities, pass criteria, exclusion and attribution rules, switch rule to Appium 3, compatibility smoke, and scope limit are defined in protocol/mobile-runner-policy-v2.md (FROZEN-PRE-DATA; its Sections 1–8 and 10 carry v1's text verbatim, and the gate was executed under v1, AMENDED 2026-09-26 — the Mobilewright qualification is not reinterpreted) and are not restated here. Execution of the gate or the smoke requires an explicit instruction issued by a human and relayed by the ORCHESTRATOR (protocol/agent-governance-v1.md, section 2, rule 6).

## Ownership

Owner role: QUALIFIER-MOBILE-01 (protocol/agent-governance-v1.md). This role executes the gate and the smoke, records their outputs, and records the runner decision. It never selects or changes the qualification SUT build (the ORCHESTRATOR pins it under `qualification_build` in manifests/toolchain-manifest.yaml; QUALIFIER-MOBILE-01 copies the record into qualification/mobilewright/README.md) and may not extend qualification into a runner-comparison research question (protocol/mobile-runner-policy-v1.md, Section 10).

## Provenance and scope of outputs

Every qualification output records its provenance:

- tool name and version
- platform (Android emulator or iOS Simulator) and environment_type (EMULATED or SIMULATED)
- emulator/simulator identity
- pinned build identity of the app driven
- date of the run

Qualification outputs are NOT experimental data about any SUT. They are not placed under raw-data/, derived-data/, or audits/; they are never cited in an audit evidence record; and they never contribute to any capability score or to any dimension of the Experimental Utility profile. The qualification SUT is OmniPizza (SUT-01); this confers no evidence, familiarity advantage, or privileged interpretation on that ecosystem and is disclosed as a study limitation (protocol/mobile-runner-policy-v1.md, Section 3).

## Status

| Item | State |
|---|---|
| Qualification gate | COMPLETE — FAIL (2026-09-24): the protocol-valid gate ran once under MOBILE-QUALIFICATION-EXEC-AUTH-03 (GitHub Actions run 35938250936, attempt 1); records in qualification/mobilewright/formal/MOBILE-QUALIFICATION-EXEC-AUTH-03/; results and decision record in qualification/mobilewright/README.md ("AUTH-03 formal gate"). The run's workflow conclusion "success" is not a gate PASS. The gate executed on 2026-09-22 remains INVALID and quarantined (PROTO-U10; qualification/mobilewright/output/QUARANTINE-RECORD.yaml) |
| Compatibility smoke | EXECUTED TWICE, FALLBACK EXHAUSTED (2026-09-29). Under APPIUM3-COMPAT-SMOKE-AUTH-02 (issued 2026-09-28; one formal dispatch 2026-09-29, GitHub Actions run 36539790536, attempt 1, lock v3): SUT-02 android PASS; SUT-02 ios FAIL_RUNNER by the conservative tie-break of protocol/mobile-runner-policy-v2.md, 9.4 (attribution uncertain between the study-authored WebDriver transport and the Appium 3 / XCUITest stack; not a demonstrated runner root cause). Because Appium 3 is the Section 8 fallback, the fallback is exhausted (9.5): study-level mobile-runner status UNRESOLVED_AFTER_FALLBACK_FAILURE; every campaign requiring mobile execution is blocked until a new explicit protocol amendment. Earlier, under APPIUM3-COMPAT-SMOKE-AUTH-01 (run 36340774530, 2026-09-27, lock v2): SUT-02 android NOT_EXECUTED (HARNESS_ORCHESTRATION, QUAL-U04), ios not attempted. Records: qualification/compatibility-smoke/README.md, formal/APPIUM3-COMPAT-SMOKE-AUTH-01/ and formal/APPIUM3-COMPAT-SMOKE-AUTH-02/. Both authorizations are consumed |
| Runs executed | protocol-valid gate (run 35938250936): 6 warm-ups + 60 measured executions, 0 excluded, no manual intervention — MQ1/MQ2 10/10 on both platforms, MQ3 10/10 on the iOS Simulator, MQ3 0/10 on the Android emulator (warm-up also FAILURE). Compatibility smoke (run 36340774530, attempt 1): one SUT-02 Android execution (NOT_EXECUTED), no iOS execution. Compatibility smoke (run 36539790536, attempt 1): one SUT-02 Android execution (PASS) and one SUT-02 iOS execution (FAIL_RUNNER, tie-break). Quarantined HISTORICAL_UNAUTHORIZED_EXECUTION: 60 measured executions + 6 warm-ups (Android run 35763051534, iOS run 35767911878), preserved under qualification/mobilewright/output/ |
| Tool versions | none installed for study use (manifests/toolchain-manifest.yaml): Mobilewright 0.0.60 was installed only on the GitHub-hosted gate hosts of each run (observations recorded there); Appium 3.7.0 pinned; installed only on the GitHub-hosted hosts of the compatibility-smoke runs 36340774530 (Appium 3.7.0 and appium-uiautomator2-driver 8.7.0 observed, equal to their pins; formal/APPIUM3-COMPAT-SMOKE-AUTH-01/SUT-02-android/environment/toolchain-install.json) and 36539790536 (Appium 3.7.0 with appium-uiautomator2-driver 8.7.0 and with appium-xcuitest-driver 12.13.2 observed, equal to their pins; formal/APPIUM3-COMPAT-SMOKE-AUTH-02/SUT-02-*/environment/toolchain-install.json) |
| Selected mobile runner | Appium 3, pinned 3.7.0 — by the frozen switch rule (protocol/mobile-runner-policy-v1.md, section 8) after the gate FAIL (criteria 7.2.1 with MC-07, 7.2.2, 7.2.3; 7.2.4 held); decision recorded here, transcribed by the ORCHESTRATOR into manifests/toolchain-manifest.yaml and protocol/CHANGELOG.md (commit e027ef4); executed only in the compatibility smokes of 2026-09-27 (SUT-02 android NOT_EXECUTED) and 2026-09-29 (SUT-02 android PASS; SUT-02 ios FAIL_RUNNER, tie-break); FALLBACK EXHAUSTED (policy v2, 9.5): study-level status UNRESOLVED_AFTER_FALLBACK_FAILURE; Section 8 is not applied again, no other runner is selected; Appium 2 never |
| Escalations | qualification/unresolved.md: QUAL-U01 (RESOLVED, PROTO-U10), QUAL-U02 (RESOLVED, PROTO-U12), QUAL-U03 (RESOLVED 2026-09-24, PROTO-U13: incomplete token fragments in every MQ3 `runner.log` of both lineages; handled by the public-export-only QUALIFICATION_TOKEN_FRAGMENT_REDACTION, canonical artifacts unchanged; publication of the formal artifacts not yet authorized), QUAL-U04 (2026-09-27, compatibility-smoke Android navigation realization targeted a non-navigation SUT element; result NOT_EXECUTED / HARNESS_ORCHESTRATION; implementation correction prepared under lock v3 on 2026-09-28; the SUT-02 android requirement satisfied by the PASS under APPIUM3-COMPAT-SMOKE-AUTH-02, 2026-09-29), QUAL-U05 (2026-09-27, import commit stored one text artifact end-of-line normalized; corrected forward, RESOLVED), QUAL-U06 (2026-09-29, OPEN: WebDriver transport timeout/diagnostic mismatch in the compatibility-smoke harness, observed after AUTH-02; causal role not established; does not override the 9.4 FAIL_RUNNER), QUAL-U07 (2026-09-29; RESOLVED 2026-10-03 as to publication handling, option A: QUALIFICATION_HOST_PATH_REDACTION and DETERMINISTIC_SANITIZED_ARCHIVE; canonical evidence unchanged; applied by the next authorized export) |
