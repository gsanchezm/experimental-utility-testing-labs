# SUT-01 — OmniPizza — Audit Workspace

| Field | Value |
|---|---|
| SUT id | SUT-01 |
| Ecosystem name | OmniPizza |
| Role | general-purpose candidate |
| Auditor role | AUDITOR-SUT01-OMNIPIZZA |
| Audit status | SUBMITTED |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Rubric version | v1 |
| Evidence rules version | v1 |

This is the audit workspace for the system under test (SUT) SUT-01, OmniPizza, one of the six ecosystems evaluated in study EUS-2026-001. Directory-wide rules, the workspace table, and the evidence.csv header are in audits/README.md and are not repeated here.

## Files

| File | Purpose |
|---|---|
| README.md | This file: workspace status and instructions |
| audit.md | Structured audit: eight of nine modalities scored Score 3 / CONFIRMED, one (Visual Testing) tie-break-capped at confirmed_score 2 (provisional_score 3 unresolved, flagged for adjudication); see audit.md section 3 |
| evidence.csv | 30 evidence records (SUT01-EV-0001..0030): 8 DOCUMENTED, 22 SOURCE_VERIFIED, 0 EXECUTION_VERIFIED, 0 INFERRED |
| limitations.md | Populated: evaluation, environment, and evidence-status limitations recorded |
| unresolved.md | One non-blocking question recorded (SUT-01-U01) |
| verifications/ | Not created — this audit produced zero EXECUTION_VERIFIED records (limitations.md) |
| artifacts/ | Not created — this audit produced zero EXECUTION_VERIFIED records (limitations.md) |

## Write boundary

Only AUDITOR-SUT01-OMNIPIZZA writes inside audits/SUT-01-omnipizza/. No other role writes here. ADJUDICATOR-EU-01 reads this workspace and writes its output outside audits/ (see protocol/agent-governance-v1.md); cells it disputes are cross-referenced by the auditor in unresolved.md.

## Provenance before evaluation

Before any evaluation, the component surfaces of SUT-01 (repository and commit SHA or release, or endpoint for a hosted surface) are pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml before E01 starts (sequence in manifests/README.md) and copied unchanged into audit.md section 2 by AUDITOR-SUT01-OMNIPIZZA. Provenance values were pinned by the ORCHESTRATOR on 2026-09-16 (manifests/sut-manifest.yaml) and copied into audit.md section 2, then verified by this auditor against actual source read at both pinned commits (2026-09-17). Only the pinned version was evaluated; this auditor did not switch to any other version. No discrepancy was found between the manifest's pins and the pinned-commit source.

## Status

This audit is SUBMITTED (audit.md, header and section 7). All nine modalities were scored; no cell was structurally absent; no execution was performed (limitations.md). One non-blocking question is recorded in unresolved.md (SUT-01-U01).
