# SUT-03 — BrowserStack Demo Ecosystem — Audit Workspace

| Field | Value |
|---|---|
| SUT id | SUT-03 |
| Ecosystem name | BrowserStack Demo Ecosystem |
| Role | general-purpose / Web / API baseline |
| Auditor role | AUDITOR-SUT03-BROWSERSTACK |
| Audit status | SUBMITTED |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Rubric version | v1 |
| Evidence rules version | v1 |

This is the audit workspace for the system under test (SUT) SUT-03, BrowserStack Demo Ecosystem, one of the six ecosystems evaluated in study EUS-2026-001. Directory-wide rules, the workspace table, and the evidence.csv header are in audits/README.md and are not repeated here.

## Files

| File | Purpose |
|---|---|
| README.md | This file: workspace status and instructions |
| audit.md | Completed audit: header, provenance, nine-modality table, eight cross-cutting properties, one documentation-vs-implementation contradiction, negative evidence summary, auditor declaration |
| evidence.csv | 32 evidence records, SUT03-EV-0001 – SUT03-EV-0032, DOCUMENTED and SOURCE_VERIFIED only |
| limitations.md | Recorded: no EXECUTION_VERIFIED evidence obtained (tool-permission denial on installing pinned-commit dependencies), api provenance reasoning, controlled_instance_available basis |
| unresolved.md | 3 non-blocking rows (api provenance discrepancy, a Security Testing score judgment call, controlled_instance_available basis) |
| verifications/ | Not created — no EXECUTION_VERIFIED evidence was produced in this audit |
| artifacts/ | Not created — no EXECUTION_VERIFIED evidence was produced in this audit |

## Write boundary

Only AUDITOR-SUT03-BROWSERSTACK writes inside audits/SUT-03-browserstack/. No other role writes here. ADJUDICATOR-EU-01 reads this workspace and writes its output outside audits/ (see protocol/agent-governance-v1.md); cells it disputes are cross-referenced by the auditor in unresolved.md.

## Provenance before evaluation

Before any evaluation, the component surfaces of SUT-03 (repository and commit SHA or release, or endpoint for a hosted surface) are pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml before E01 starts (sequence in manifests/README.md) and copied unchanged into audit.md section 2 by AUDITOR-SUT03-BROWSERSTACK. All provenance values are currently null / TBD. Only the pinned version is evaluated; the auditor never switches to another version because it exposes a more favorable capability; a mechanism claimed for score 3 must already be exposed by that version. A discrepancy between the manifest and what the auditor observes is recorded in unresolved.md; the auditor never edits the manifest.

## Do not start

Do not start this audit until the protocol is in state FROZEN-PRE-DATA (protocol/change-control-v1.md) and ORCHESTRATOR has issued an explicit start instruction. AUDITOR-SUT03-BROWSERSTACK updates the audit status in this file and in audit.md when the audit starts and when it is submitted.
