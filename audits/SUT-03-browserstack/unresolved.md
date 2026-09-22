# SUT-03 — BrowserStack Demo Ecosystem — Unresolved Questions

| Field | Value |
|---|---|
| SUT id | SUT-03 |
| Auditor role | AUDITOR-SUT03-BROWSERSTACK |
| Audit status | SUBMITTED |

## Purpose

Tracks questions raised during the audit of the system under test (SUT) SUT-03 that could not be settled from evidence: ambiguous rubric application, unverifiable provenance, a discrepancy between the pinned target and what is observed, contradictory documentation, or missing environment access. Column meanings: id is sequential in the form SUT-03-U01, SUT-03-U02, ...; cell or topic names the audit.md cell, the evidence record by evidence_id (never by row or line number), the verification record by verification_id, or the subject concerned; blocking? is YES when the affected cell cannot be submitted until the question is resolved, otherwise NO; raised_by is an agent role name (protocol/agent-governance-v1.md); dates as YYYY-MM-DD; resolution stays empty until resolved.

None of the three rows below are blocking: every cell in audit.md section 3 was scored with confidence from available evidence. They are recorded for adjudicator visibility and, where noted, because they touch a file only the ORCHESTRATOR may edit.

## Questions

| id | cell or topic | question | blocking? | raised_by | raised_at | resolution | resolved_at |
|---|---|---|---|---|---|---|---|
| SUT-03-U01 | audit.md section 2, api component provenance | `manifests/sut-manifest.yaml` and `manifests/e01-source-provenance.yaml` pin no independent provenance artifact for SUT-03-api (repository/commit fields null, `eligibility_basis: "No component named for this study."`), yet source inspection at the pinned SUT-03-web commit (`7ab934d733f2f74d4b912e94e86f59ae0f6b7609`) shows `pages/api/**.js` implementing a real, substantial API surface within that same repository. This audit recorded api presence as CONFIRMED in audit.md section 2, citing the SUT-03-web provenance artifact, per `manifests/e01-source-provenance.yaml`'s own terminology note that "one provenance artifact may back more than one logical surface." Should the ORCHESTRATOR additionally populate the api component_id row's repository/commit fields in `manifests/sut-manifest.yaml` and `manifests/e01-source-provenance.yaml` to reflect this discrepancy (both remain null there; this auditor cannot edit those files — protocol/agent-governance-v1.md, section 3.2)? | NO | AUDITOR-SUT03-BROWSERSTACK | 2026-09-17 | | |
| SUT-03-U02 | audit.md section 3, Security Testing score (2) | Real-but-ordinary authentication/authorization logic exists at the pinned commit (a fixed account allowlist, a permanently-locked test account with its own error message, an API-level `userName` gate on checkout — SUT03-EV-0024), but no documented or source-verified *intentional* vulnerability was found (SUT03-EV-0025). This audit scored the cell 2 rather than 1, reasoning that the behavior is SUT-specific and stable rather than merely generically reachable (capability-rubric-v1.md Decision procedure, step 2). A different auditor could reasonably read the same evidence as Score 1, since none of it is security-vulnerability ground truth. Recorded for adjudicator visibility; the underlying evidence itself is not in doubt, only which side of the Score 1 / Score 2 line it falls on. | NO | AUDITOR-SUT03-BROWSERSTACK | 2026-09-17 | | |
| SUT-03-U03 | audit.md section 1, controlled_instance_available | Left `null / TBD` per protocol/study-design-v1.md section 10.5 ("null until verified and is never inferred"), because installing dependencies for the pinned commit in this session's read-only source workspace (`../e01-sut-sources/SUT-03-browserstack/`) was denied by this session's own tool-permission policy (see limitations.md, Evaluation limitations item 1), so no local run was executed. Source analysis (standard `package.json` scripts; README.md's documented Docker/Node.js local-run instructions; no external database dependency found in source) suggests a controlled instance is achievable, but is deliberately not converted into a verified value. A future session able to actually execute the install should confirm this before the ORCHESTRATOR transcribes a value into `manifests/sut-manifest.yaml`. | NO | AUDITOR-SUT03-BROWSERSTACK | 2026-09-17 | | |

## Adjudication cross-references

Cells disputed by ADJUDICATOR-EU-01 are cross-referenced here by AUDITOR-SUT03-BROWSERSTACK as rows of the table above (raised_by = ADJUDICATOR-EU-01), each pointing to the adjudicator's record outside audits/ (protocol/agent-governance-v1.md). The adjudicator does not write in this file. None recorded yet.
