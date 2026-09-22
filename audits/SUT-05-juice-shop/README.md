# SUT-05 — OWASP Juice Shop — Audit Workspace

| Field | Value |
|---|---|
| SUT id | SUT-05 |
| Ecosystem name | OWASP Juice Shop |
| Role | security specialist baseline |
| Auditor role | AUDITOR-SUT05-JUICESHOP |
| Audit status | SUBMITTED |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Rubric version | v1 |
| Evidence rules version | v1 |

This is the audit workspace for the system under test (SUT) SUT-05, OWASP Juice Shop, one of the six ecosystems evaluated in study EUS-2026-001. Directory-wide rules, the workspace table, and the evidence.csv header are in audits/README.md and are not repeated here.

## Files

| File | Purpose |
|---|---|
| README.md | This file: workspace status and instructions |
| audit.md | Completed audit: header, component provenance, nine-modality assessment table, eight cross-cutting property descriptions, contradictions section (none found), negative-evidence summary, auditor declaration |
| evidence.csv | 29 evidence records (SUT05-EV-0001 … SUT05-EV-0029), DOCUMENTED and SOURCE_VERIFIED only |
| limitations.md | Populated: scope, evaluation, environment limitations, and environment considerations for this audit |
| unresolved.md | One non-blocking row (SUT-05-U01): a write-boundary incident outside this workspace, reported for ORCHESTRATOR/human remediation |
| verifications/ | Execution verification records (run manifests, one per EXECUTION_VERIFIED verification, file name = verification_id); created on first use, does not exist yet |
| artifacts/ | Retained artifacts referenced by verification records; created on first use, does not exist yet |

## Write boundary

Only AUDITOR-SUT05-JUICESHOP writes inside audits/SUT-05-juice-shop/. No other role writes here. ADJUDICATOR-EU-01 reads this workspace and writes its output outside audits/ (see protocol/agent-governance-v1.md); cells it disputes are cross-referenced by the auditor in unresolved.md.

## Provenance before evaluation

Before any evaluation, the component surfaces of SUT-05 (repository and commit SHA or release, or endpoint for a hosted surface) are pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml before E01 starts (sequence in manifests/README.md) and copied unchanged into audit.md section 2 by AUDITOR-SUT05-JUICESHOP. Provenance was pinned by the ORCHESTRATOR (web and api at https://github.com/juice-shop/juice-shop @ 1618a611b173b4bf114028e6e02549950606e29d; no android/ios component named) and copied into audit.md section 2, where this auditor also recorded its own presence verification (CONFIRMED for web/api, ABSENT for android/ios). Only the pinned version is evaluated; the auditor never switches to another version because it exposes a more favorable capability; a mechanism claimed for score 3 must already be exposed by that version. No discrepancy between the manifest and what the auditor observed was found.

## Status

This audit is SUBMITTED (audit.md section 1). It was performed entirely from documentation and source inspection of the pinned commit, cloned read-only outside this repository at `../e01-sut-sources/SUT-05-juice-shop/` (HEAD verified to equal the pinned commit SHA); no EXECUTION_VERIFIED evidence was produced or required. See limitations.md for what this audit could and could not verify, and unresolved.md for one non-blocking, out-of-workspace incident reported for ORCHESTRATOR/human attention.
