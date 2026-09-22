# SUT-02 — Sauce Labs Demo Ecosystem — Unresolved Questions

| Field | Value |
|---|---|
| SUT id | SUT-02 |
| Auditor role | AUDITOR-SUT02-SAUCELABS |
| Audit status | SUBMITTED |

## Purpose

Tracks questions raised during the audit of the system under test (SUT) SUT-02 that could not be settled from evidence: ambiguous rubric application, unverifiable provenance, a discrepancy between the pinned target and what is observed, contradictory documentation, or missing environment access. Column meanings: id is sequential in the form SUT-02-U01, SUT-02-U02, ...; cell or topic names the audit.md cell, the evidence record by evidence_id (never by row or line number), the verification record by verification_id, or the subject concerned; blocking? is YES when the affected cell cannot be submitted until the question is resolved, otherwise NO; raised_by is an agent role name (protocol/agent-governance-v1.md); dates as YYYY-MM-DD; resolution stays empty until resolved.

## Questions

| id | cell or topic | question | blocking? | raised_by | raised_at | resolution | resolved_at |
|---|---|---|---|---|---|---|---|
| SUT-02-U01 | manifests/sut-manifest.yaml, SUT-02 ios `commit_sha` field; audit.md section 2, ios row | The ios provenance pinned by the ORCHESTRATOR as `commit_sha: 031358f56903742103a02d086f8af76735bb31a7` (`release: "2.2.2"`) is, on inspection of the checked-out repository, a git *annotated tag* object, not a raw commit SHA. `git checkout` of it correctly dereferences to commit `ede6fa4b7f57a75bc31f626b6ca531339e83d5c0`. Is this intentional (the manifest's `commit_sha` field is meant to also accept a tag object id when paired with a `release` value), or should a future manifest correction record the underlying commit SHA directly? | NO | AUDITOR-SUT02-SAUCELABS | 2026-09-17 | | |
| SUT-02-U02 | This launch package itself (experiments/E01-capability-audit/launch/AUDITOR-SUT02-SAUCELABS.md), line 3 | The rendered launch package's own frozen text states: "Status: WORKING. Not yet frozen. Do not use this prompt for a data-producing run" — yet this package is the frozen, rendered launch package under which this audit was explicitly instructed to run, for a campaign (E01-capability-audit) already IN_PROGRESS per the repository's commit history. Per this prompt's own line 5 ("Where this prompt and a frozen protocol document ever appear to disagree, the frozen protocol document governs... report the apparent conflict... rather than resolve it yourself"), this apparent self-contradiction is reported here rather than resolved by the auditor. | NO | AUDITOR-SUT02-SAUCELABS | 2026-09-17 | | |
| SUT-02-U03 | "Final auditor return package," item 4 (audit commit SHA) vs. the operational preamble's rule 5 (no git commit in this worktree) | The prompt's "Final auditor return package" asks for "the audit commit SHA (the commit you produced your output under)," while the operational preamble under which this session was launched explicitly forbids `git commit` (and any other git write/history operation) in this worktree, leaving output as uncommitted changes for the ORCHESTRATOR to review and commit. This auditor followed the operational preamble (no commit was made) and reports item 4 in the structured return as "no commit — output left uncommitted for ORCHESTRATOR per launch instruction" rather than fabricating a commit SHA. | NO | AUDITOR-SUT02-SAUCELABS | 2026-09-17 | | |

## Adjudication cross-references

Cells disputed by ADJUDICATOR-EU-01 are cross-referenced here by AUDITOR-SUT02-SAUCELABS as rows of the table above (raised_by = ADJUDICATOR-EU-01), each pointing to the adjudicator's record outside audits/ (protocol/agent-governance-v1.md). The adjudicator does not write in this file.

None yet — adjudication has not occurred.
