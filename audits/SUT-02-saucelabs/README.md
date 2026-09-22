# SUT-02 — Sauce Labs Demo Ecosystem — Audit Workspace

| Field | Value |
|---|---|
| SUT id | SUT-02 |
| Ecosystem name | Sauce Labs Demo Ecosystem |
| Role | general-purpose baseline |
| Auditor role | AUDITOR-SUT02-SAUCELABS |
| Audit status | NOT_STARTED |
| Protocol version | v1 |
| Protocol state | DRAFT |
| Rubric version | v1 |
| Evidence rules version | v1 |

This is the audit workspace for the system under test (SUT) SUT-02, Sauce Labs Demo Ecosystem, one of the six ecosystems evaluated in study EUS-2026-001. Directory-wide rules, the workspace table, and the evidence.csv header are in audits/README.md and are not repeated here.

## Files

| File | Purpose |
|---|---|
| README.md | This file: workspace status and instructions |
| audit.md | Structured audit template; all cells empty |
| evidence.csv | Evidence records; header row only, no records |
| limitations.md | Limitations template; nothing recorded |
| unresolved.md | Open questions template; no rows |
| verifications/ | Execution verification records (run manifests, one per EXECUTION_VERIFIED verification, file name = verification_id); created on first use, does not exist yet |
| artifacts/ | Retained artifacts referenced by verification records; created on first use, does not exist yet |

## Write boundary

Only AUDITOR-SUT02-SAUCELABS writes inside audits/SUT-02-saucelabs/. No other role writes here. ADJUDICATOR-EU-01 reads this workspace and writes its output outside audits/ (see protocol/agent-governance-v1.md); cells it disputes are cross-referenced by the auditor in unresolved.md.

## Provenance before evaluation

Before any evaluation, the component surfaces of SUT-02 (repository and commit SHA or release, or endpoint for a hosted surface) are pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml before E01 starts (sequence in manifests/README.md) and copied unchanged into audit.md section 2 by AUDITOR-SUT02-SAUCELABS. All provenance values are currently null / TBD. Only the pinned version is evaluated; the auditor never switches to another version because it exposes a more favorable capability; a mechanism claimed for score 3 must already be exposed by that version. A discrepancy between the manifest and what the auditor observes is recorded in unresolved.md; the auditor never edits the manifest.

## Do not start

Do not start this audit until the protocol is in state FROZEN-PRE-DATA (protocol/change-control-v1.md) and ORCHESTRATOR has issued an explicit start instruction. AUDITOR-SUT02-SAUCELABS updates the audit status in this file and in audit.md when the audit starts and when it is submitted.
