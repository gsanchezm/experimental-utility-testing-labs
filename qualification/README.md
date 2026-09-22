# Qualification

Tool-qualification records for study EUS-2026-001 (Experimental Utility of Software-Testing Laboratory Ecosystems).

## Purpose

This directory holds qualification of study tooling. Tool qualification is separate from evaluation of any system under test (SUT): it establishes whether a tool is fit for use in the study's experimental campaigns, and nothing else. Nothing in this directory audits, scores, or characterizes an evaluated ecosystem.

## Contents

| Path | Content | Governing policy |
|---|---|---|
| qualification/mobilewright/ | Mobilewright qualification gate (MQ1 Login → Catalog; MQ2 Catalog → Product Interaction; MQ3 API State Seed → Deep Link → Target UI State; on Android emulator and iOS Simulator; qualification SUT OmniPizza; N = 10 measured executions per combination) and the runner decision record | protocol/mobile-runner-policy-v1.md, Sections 2–8 |
| qualification/compatibility-smoke/ | Per-SUT compatibility smoke of the selected runner on every mobile-capable ecosystem before mobile campaigns | protocol/mobile-runner-policy-v1.md, Section 9 |
| qualification/unresolved.md | Escalations raised in this workspace, same table format as the audit unresolved.md files; created 2026-09-22 (first use) with QUAL-U01, the execution-authorization conflict of the 2026-09-22 gate (mirrored as protocol/unresolved.md PROTO-U10) | protocol/agent-governance-v1.md, section 6 |

The gate definition, mandatory capabilities, pass criteria, exclusion and attribution rules, switch rule to Appium 3, compatibility smoke, and scope limit are defined in protocol/mobile-runner-policy-v1.md and are not restated here. Execution of the gate or the smoke requires an explicit instruction issued by a human and relayed by the ORCHESTRATOR (protocol/agent-governance-v1.md, section 2, rule 6).

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
| Qualification gate | INVALID / REQUIRES RE-EXECUTION (PROTO-U10, 2026-09-22): the gate executed on 2026-09-22 ran without a valid human authorization; its executions are preserved and quarantined (qualification/mobilewright/output/QUARANTINE-RECORD.yaml); the FAIL decision and the Appium 3 selection derived from it are superseded; a protocol-valid gate is NOT STARTED and requires a NEW human authorization (qualification/mobilewright/README.md; manifests/mobile-qualification-authorization-correction-v1.yaml) |
| Compatibility smoke | NOT AUTHORIZED / NOT STARTED (no runner is selected) |
| Runs executed | protocol-valid gate: none. Quarantined HISTORICAL_UNAUTHORIZED_EXECUTION: 60 measured executions + 6 warm-ups (Android run 35763051534, iOS run 35767911878), preserved under qualification/mobilewright/output/; historical, non-authoritative observation: MQ1/MQ2 10/10 on both platforms, MQ3 10/10 on iOS, MQ3 0/10 on the Android emulator (MC-07) |
| Tool versions | none installed for study use (manifests/toolchain-manifest.yaml: Mobilewright 0.0.60 pinned candidate, Appium 3.7.0 pinned fallback; the versions observed during the quarantined executions are kept as historical observations) |
| Selected mobile runner | none (primary candidate Mobilewright 0.0.60; fallback Appium 3.7.0; Appium 2 never) |
| Escalations | qualification/unresolved.md QUAL-U01 (RESOLVED, PROTO-U10) |
