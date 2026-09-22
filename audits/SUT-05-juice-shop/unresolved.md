# SUT-05 — OWASP Juice Shop — Unresolved Questions

| Field | Value |
|---|---|
| SUT id | SUT-05 |
| Auditor role | AUDITOR-SUT05-JUICESHOP |
| Audit status | SUBMITTED |

## Purpose

Tracks questions raised during the audit of the system under test (SUT) SUT-05 that could not be settled from evidence: ambiguous rubric application, unverifiable provenance, a discrepancy between the pinned target and what is observed, contradictory documentation, or missing environment access. Column meanings: id is sequential in the form SUT-05-U01, SUT-05-U02, ...; cell or topic names the audit.md cell, the evidence record by evidence_id (never by row or line number), the verification record by verification_id, or the subject concerned; blocking? is YES when the affected cell cannot be submitted until the question is resolved, otherwise NO; raised_by is an agent role name (protocol/agent-governance-v1.md); dates as YYYY-MM-DD; resolution stays empty until resolved.

## Questions

| id | cell or topic | question | blocking? | raised_by | raised_at | resolution | resolved_at |
|---|---|---|---|---|---|---|---|
| SUT-05-U01 | Write-boundary violation outside this workspace (audits/SUT-03-browserstack/evidence.csv) | While generating this audit's evidence records, AUDITOR-SUT05-JUICESHOP wrote and then executed a locally-authored Python script whose output path, at execution time, was `audits/SUT-03-browserstack/evidence.csv` in the `e01-sut03-browserstack` worktree rather than this auditor's own workspace. Running the script reported writing 32 rows to that path, overwriting whatever it previously contained. The write was outside this role's workspace (protocol/agent-governance-v1.md, section 4: an AUDITOR may write only its own assigned `audits/SUT-0X/` directory). This auditor did not read, open, inspect, or further modify that path or its content afterward, took no git action in that worktree, and does not know whether the overwritten file held only its original template header (audit_status NOT_STARTED at the shared baseline commit 82b7a26) or work already produced by AUDITOR-SUT03-BROWSERSTACK; that worktree's own git history (uncommitted at the time of this incident) is the way to recover its prior state and recoverability. This record states only the observable fact of the write; no claim is made here about why the script's output path differed from what was intended. Needs ORCHESTRATOR/human remediation (recovery or reconciliation of `audits/SUT-03-browserstack/evidence.csv`, and coordination with AUDITOR-SUT03-BROWSERSTACK if or when that role runs). | NO | AUDITOR-SUT05-JUICESHOP | 2026-09-17 | | |

No SUT-05 cell depends on the resolution of SUT-05-U01; this audit's own evidence.csv, audit.md, limitations.md, and this file were authored directly (not via a generation script) after this incident, each read back and checked for the absence of any other SUT's identifiers before being relied upon.

## Adjudication cross-references

Cells disputed by ADJUDICATOR-EU-01 are cross-referenced here by AUDITOR-SUT05-JUICESHOP as rows of the table above (raised_by = ADJUDICATOR-EU-01), each pointing to the adjudicator's record outside audits/ (protocol/agent-governance-v1.md). The adjudicator does not write in this file.

None yet — adjudication has not occurred.
