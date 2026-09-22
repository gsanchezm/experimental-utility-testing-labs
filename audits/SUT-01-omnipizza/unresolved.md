# SUT-01 — OmniPizza — Unresolved Questions

| Field | Value |
|---|---|
| SUT id | SUT-01 |
| Auditor role | AUDITOR-SUT01-OMNIPIZZA |
| Audit status | SUBMITTED |

## Purpose

Tracks questions raised during the audit of the system under test (SUT) SUT-01 that could not be settled from evidence: ambiguous rubric application, unverifiable provenance, a discrepancy between the pinned target and what is observed, contradictory documentation, or missing environment access. Column meanings: id is sequential in the form SUT-01-U01, SUT-01-U02, ...; cell or topic names the audit.md cell, the evidence record by evidence_id (never by row or line number), the verification record by verification_id, or the subject concerned; blocking? is YES when the affected cell cannot be submitted until the question is resolved, otherwise NO; raised_by is an agent role name (protocol/agent-governance-v1.md); dates as YYYY-MM-DD; resolution stays empty until resolved.

## Questions

| id | cell or topic | question | blocking? | raised_by | raised_at | resolution | resolved_at |
|---|---|---|---|---|---|---|---|
| SUT-01-U01 | prompts/frozen/e01-capability-auditor-v1.md (self-description) | The frozen auditor prompt's own body still reads "Status: WORKING. Not yet frozen. Do not use this prompt for a data-producing run" (and its title still reads "working prompt v1"), inherited byte-for-byte from prompts/working/ at freeze time (manifests/e01-prompt-freeze.yaml, `byte_equivalence_verified: true`). This prompt's own "Governing documents" section instructs: "Where this prompt and a frozen protocol document ever appear to disagree, the frozen protocol document governs; report the apparent conflict in unresolved.md rather than resolving it yourself." This auditor did not resolve it: it proceeded on the authority of manifests/e01-prompt-freeze.yaml (`status: FROZEN`, sha256 `b504b5f7...c358`, `freeze_approved_by: gilbertosanchez`), which the rendered launch package's own SHA-256 (`d71acf83...161b`) matched exactly, and on the fact that this self-description was already flagged as a known, non-blocking observation by the ORCHESTRATOR before campaign start (commit 637abe7, `experiments/E01-capability-audit/launch/launch-manifest.yaml`, `frozen_prompt_self_description_observation`), and the campaign was subsequently started (commit 89b23f2) after that flag was on record. Separately: the campaign-start provenance record (manifests/e01-campaign-start-v1.yaml) and `experiments/E01-capability-audit/README.md` both state that "each of the six independent audits still requires its own separate explicit instruction before it begins work" (protocol/agent-governance-v1.md section 2 rule 6; AGENT-INSTRUCTIONS.md rule 15) — this auditor treated the orchestrator's launch preamble that spawned this session (explicitly naming AUDITOR-SUT01-OMNIPIZZA, campaign E01-capability-audit, IN_PROGRESS as of commit 89b23f2) as that per-auditor explicit instruction. | NO | AUDITOR-SUT01-OMNIPIZZA | 2026-09-17 | | |

## Adjudication cross-references

Cells disputed by ADJUDICATOR-EU-01 are cross-referenced here by AUDITOR-SUT01-OMNIPIZZA as rows of the table above (raised_by = ADJUDICATOR-EU-01), each pointing to the adjudicator's record outside audits/ (protocol/agent-governance-v1.md). The adjudicator does not write in this file.
