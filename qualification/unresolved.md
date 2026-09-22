# Qualification — Unresolved Questions

| Field | Value |
|---|---|
| Workspace | qualification/ |
| Role | QUALIFIER-MOBILE-01 |
| Created | 2026-09-22 (first use; protocol/agent-governance-v1.md, section 6, unchanged in v2) |

## Purpose

Tracks escalations raised in the qualification workspace: conflicts between an instruction and the frozen policy, discrepancies between pinned inputs and obtained artifacts, write-boundary questions. Same table format as the audit unresolved.md files. Never resolved by an agent on its own authority; the ORCHESTRATOR mirrors protocol-level items into protocol/unresolved.md; humans decide.

## Questions

| id | cell or topic | question | blocking? | raised_by | raised_at | resolution | resolved_at |
|---|---|---|---|---|---|---|---|
| QUAL-U01 | Mobilewright qualification gate of 2026-09-22 — execution authorization | The gate (runs 35763051534 Android, 35767911878 iOS) was executed on the ORCHESTRATOR's relay of MOBILE-QUALIFICATION-EXEC-AUTH-01, a record that no human had issued (the human research lead has determined the text was a proposed draft never approved; no repository artifact predating the record carries a human authorization). protocol/mobile-runner-policy-v1.md section 2 requires an explicit instruction issued by a human. Are the executions, the FAIL decision, and the switch-rule selection valid? | yes (for the runner decision and any compatibility smoke) | human research lead (recorded by QUALIFIER-MOBILE-01); mirrored as PROTO-U10 by ORCHESTRATOR | 2026-09-22 | RESOLVED by explicit human corrective instruction (PROTO-U10; manifests/mobile-qualification-authorization-correction-v1.yaml): AUTHORIZATION_PROVENANCE INVALID; the executions are preserved and quarantined as HISTORICAL_UNAUTHORIZED_EXECUTION (output/QUARANTINE-RECORD.yaml) — observed but protocol-inadmissible for runner-selection authority; the decision record is superseded (INVALID_REQUIRES_VALID_REEXECUTION); no runner is selected; Appium 3 compatibility smoke NOT AUTHORIZED; PREQUALIFICATION_OUTCOME_EXPOSURE true; a future valid gate needs a NEW human authorization; a LOCAL_DEVELOPMENT_PREFLIGHT class is prepared for separate authorization. | 2026-09-22 |
