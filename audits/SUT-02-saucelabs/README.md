# SUT-02 — Sauce Labs Demo Ecosystem — Audit Workspace

| Field | Value |
|---|---|
| SUT id | SUT-02 |
| Ecosystem name | Sauce Labs Demo Ecosystem |
| Role | general-purpose baseline |
| Auditor role | AUDITOR-SUT02-SAUCELABS |
| Audit status | SUBMITTED |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Rubric version | v1 |
| Evidence rules version | v1 |

This is the audit workspace for the system under test (SUT) SUT-02, Sauce Labs Demo Ecosystem, one of the six ecosystems evaluated in study EUS-2026-001. Directory-wide rules, the workspace table, and the evidence.csv header are in audits/README.md and are not repeated here.

## Files

| File | Purpose |
|---|---|
| README.md | This file: workspace status and instructions |
| audit.md | Structured audit; all nine modalities assessed, provenance in section 2 filled |
| evidence.csv | 21 evidence records (SUT02-EV-0001 … SUT02-EV-0021), all SOURCE_VERIFIED |
| limitations.md | Filled: scope, evaluation, environment limitations recorded |
| unresolved.md | 3 non-blocking questions recorded (SUT-02-U01 … SUT-02-U03) |
| verifications/ | Not created: this audit produced zero EXECUTION_VERIFIED records |
| artifacts/ | Not created: this audit produced zero EXECUTION_VERIFIED records |

## Write boundary

Only AUDITOR-SUT02-SAUCELABS writes inside audits/SUT-02-saucelabs/. No other role writes here. ADJUDICATOR-EU-01 reads this workspace and writes its output outside audits/ (see protocol/agent-governance-v1.md); cells it disputes are cross-referenced by the auditor in unresolved.md.

## Provenance before evaluation

Before any evaluation, the component surfaces of SUT-02 (repository and commit SHA or release, or endpoint for a hosted surface) are pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml before E01 starts (sequence in manifests/README.md) and copied unchanged into audit.md section 2 by AUDITOR-SUT02-SAUCELABS. Provenance was copied from manifests/sut-manifest.yaml and verified by checking out each of the three pinned repositories (web, android, ios) in a read-only sibling workspace at the exact pinned commit/tag; web and android matched the pinned commit SHA exactly, and ios's pinned identifier (an annotated tag object) dereferenced to the commit actually read (recorded as SUT-02-U01 in unresolved.md, non-blocking). Only the pinned version was evaluated; no version switch occurred. A discrepancy between the manifest and what the auditor observes is recorded in unresolved.md; the auditor never edits the manifest.

## Do not start

Do not start this audit until the protocol is in state FROZEN-PRE-DATA (protocol/change-control-v1.md) and ORCHESTRATOR has issued an explicit start instruction. This audit was started and submitted on 2026-09-17 under an explicit ORCHESTRATOR-relayed instruction, with the protocol already FROZEN-PRE-DATA.
