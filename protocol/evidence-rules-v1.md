# Evidence Rules

| Field | Value |
|---|---|
| Document | protocol/evidence-rules-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | first iteration instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT); second iteration (issue (x), explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT); final pre-freeze checklist closure (tie-break rule cross-reference, explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## Purpose

This document defines what counts as evidence for a capability score assigned under protocol/capability-rubric-v1.md, the statuses an evidence item may hold, the rules that bind auditors and the adjudicator, the record format and its stable identifier, the execution verification record required for EXECUTION_VERIFIED evidence, how absence and limitations are recorded, and how records are retained. It applies to every evaluated system under test (SUT-01 to SUT-06), to every auditor role (AUDITOR-SUT01-OMNIPIZZA through AUDITOR-SUT06-WEBDRIVERIO), and to ADJUDICATOR-EU-01 (protocol/agent-governance-v1.md). No evidence record exists at this time; the repository is in the SETUP phase.

## Evidence statuses

Every evidence record carries exactly one of four statuses.

| Status | Definition |
|---|---|
| DOCUMENTED | The capability is claimed in official documentation, a README, or release notes of the evaluated version. Not yet confirmed. |
| SOURCE_VERIFIED | The capability is confirmed by reading the source code of the evaluated component at the recorded commit SHA or release. |
| EXECUTION_VERIFIED | The capability is confirmed by executing against the evaluated version and observing the expected behavior, with artifacts retained and an execution verification record on file (see "Execution verification records"). |
| INFERRED | The capability is deduced from indirect signals such as UI hints, naming, or analogous behavior. Not directly confirmed. |

What each status can support:

| Status | Can support | Cannot support |
|---|---|---|
| DOCUMENTED | Identification of a candidate capability; provisional Score 1 or 2; a provisional Score 3 candidate recorded with `confirmation_state = UNCONFIRMED_SCORE_3` (protocol/capability-rubric-v1.md, "Score 3 confirmation") | A confirmed / adjudicated Score 3 on its own (protocol/study-design-v1.md, section 13, issue (x), RESOLVED) |
| SOURCE_VERIFIED | Provisional and adjudicated Score 1, 2, or 3 | — |
| EXECUTION_VERIFIED | Provisional and adjudicated Score 1, 2, or 3; confirmation of actual behavior | — |
| INFERRED | Provisional Score 1 or 2 | Score 3 on its own |

SOURCE_VERIFIED and EXECUTION_VERIFIED are both preferred; no ordering between them is defined in v1. When they disagree, the disagreement is recorded as a contradiction (see Rules).

Whether a given item of evidence, taken together with the rest of the record, *fully* supports a rubric level (as opposed to merely being admissible for it) is decided by protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores": when the auditor cannot answer a Decision procedure question with confidence, the recorded `confirmed_score` is the highest level whose complete requirements are fully supported, and the higher, unresolved level is retained only as `provisional_score` pending adjudication. `confirmation_state` (UNCONFIRMED_SCORE_3 / CONFIRMED, above) is that same rule's named special case for the 2/3 boundary once the mechanism and outcome are already decided to exist and only the evidence status is in question.

Evidence ceiling. For a closed-source or hosted-only component, SOURCE_VERIFIED is unobtainable; DOCUMENTED and EXECUTION_VERIFIED remain obtainable. An ecosystem is not penalized solely because SOURCE_VERIFIED evidence is unavailable for such a component. Its evidence status reflects the strongest evidence actually obtainable, the capability score is decided under protocol/capability-rubric-v1.md by what the evaluated version exposes, and the ceiling is recorded once in audits/<SUT>/limitations.md and referenced from the notes of the affected records (protocol/study-design-v1.md, section 10.4). Where the score in question is 3, EXECUTION_VERIFIED is then the required confirming status for `confirmation_state = CONFIRMED` (protocol/capability-rubric-v1.md, "Score 3 confirmation"); DOCUMENTED alone still only yields `UNCONFIRMED_SCORE_3`, ceiling or not. The same rule applies to every ecosystem.

## Rules

* Every non-zero capability score requires evidence.
* INFERRED evidence alone cannot justify score 3.
* DOCUMENTED evidence alone never confirms an adjudicated Score 3; it supports only a provisional Score 3 candidate with `confirmation_state = UNCONFIRMED_SCORE_3`. Confirmation requires SOURCE_VERIFIED or EXECUTION_VERIFIED evidence, EXECUTION_VERIFIED being the required confirming status where SOURCE_VERIFIED is unobtainable (Evidence ceiling, below). See protocol/capability-rubric-v1.md, "Score 3 confirmation" (resolves protocol/study-design-v1.md, section 13, issue (x)).
* Prefer SOURCE_VERIFIED or EXECUTION_VERIFIED, and record the strongest status actually obtainable.
* Documentation may identify a candidate capability.
* Execution can confirm actual behavior.
* If documentation contradicts implementation, record the contradiction.
* Do not silently choose whichever evidence favors a SUT.
* Negative evidence and limitations must be retained.

Additional rules:

* Never infer that a vendor's commercial testing product gives its demo SUT the same capability; only what the evaluated demo ecosystem itself exposes counts. A vendor platform, device cloud, or service is not part of the SUT unless the evaluated demo ecosystem itself ships and documents it as a mechanism of the demo.
* Local deployability is not a capability. That a component can be cloned, built, or run locally is environment provenance (protocol/study-design-v1.md, section 10) and supports no score by itself.
* Evidence must cite provenance — repository plus commit SHA or release — whenever a repository exists. Hosted-only components (no repository available for the evaluated component) record the endpoint and the observation date instead. When an official current component cannot be pinned by commit SHA, the strongest reproducible identifier available (release tag, version string, build number, or dated snapshot) is recorded by the ORCHESTRATOR in manifests/sut-manifest.yaml and cited verbatim, and the limitation is stated in audits/<SUT>/limitations.md.
* The auditor verifies the pinned target and records evidence against it. An auditor never switches to another version, branch, fork, or deployment because it exposes a more favorable capability (manifests/README.md; protocol/agent-governance-v1.md). A discrepancy between the pinned target and what is observed is recorded in audits/<SUT>/unresolved.md.
* Provenance values are never invented. A record whose repository, commit SHA, or release is unknown leaves the field empty and explains why in notes; the manifests in manifests/ are the authority for evaluated versions, and all such values are currently null.
* A contradiction is recorded as two or more records for the same cell, one per conflicting source, each with its own evidence_status, plus a notes entry on each naming the other by `evidence_id`. The cell is flagged for adjudication in audits/<SUT>/audit.md.
* An ecosystem composed of several repositories or artifacts (for example separate Web, Android, and iOS repositories) is ONE ecosystem; each record cites the specific repository and commit SHA or release it was taken from, and the ecosystem_id stays the same.
* The auditor of an ecosystem does not adjudicate its own evidence.

## Evidence identifiers

Every evidence record carries a stable identifier, `evidence_id`, which is the only permitted way to reference a record.

- Format: `SUT0n-EV-nnnn`, where `SUT0n` is the ecosystem id without the hyphen (SUT01 … SUT06) and `nnnn` is a four-digit sequence starting at 0001. Regular expression: `^SUT0[1-6]-EV-[0-9]{4}$`. The `SUT0n` part must correspond to the record's ecosystem_id (SUT01 ↔ SUT-01, and so on).
- Assignment: the auditor assigns the next unused number when the record is created. Numbers are sequential in creation order within one ecosystem, are never reused, and are never renumbered. A gap in the sequence is permitted only if explained in audits/<SUT>/limitations.md.
- Uniqueness: an evidence_id is unique across the study because it embeds the ecosystem id.
- References: audits/<SUT>/audit.md (evidence_refs), audits/<SUT>/unresolved.md, adjudication output, correction records, contradiction cross-references, execution verification records, campaign configurations, and any derived dataset reference evidence by evidence_id. CSV row numbers and file line numbers are never used as references, in any document.
- No evidence record exists yet; every audits/<SUT>/evidence.csv contains only the header line.

## Evidence record fields

Each record has the following thirteen fields, in this order.

| # | Field | Definition |
|---|---|---|
| 1 | evidence_id | Stable identifier of the record, format `SUT0n-EV-nnnn` (see "Evidence identifiers"). Required. |
| 2 | ecosystem_id | Identifier of the evaluated ecosystem: one of SUT-01, SUT-02, SUT-03, SUT-04, SUT-05, SUT-06. Must correspond to the evidence_id prefix. |
| 3 | modality | One of the nine frozen modality names exactly as written in protocol/study-design-v1.md: Web UI Functional; API; Android Native; iOS Native; Performance; Accessibility — Web only; Visual Testing; Security Testing; Localization / i18n. |
| 4 | provisional_score | Integer 0–3 that this record supports under protocol/capability-rubric-v1.md. Empty for negative-evidence and limitation records that do not support a specific score. This is the score the record supports, not necessarily the cell score. |
| 5 | evidence_type | Kind of artifact the record is based on: documentation, source-file, endpoint, execution-log, screenshot, configuration, test-data, or other. |
| 6 | repository | Repository the evidence was taken from (name or URL as recorded in manifests/). Empty for hosted-only components. |
| 7 | commit_sha_or_release | Commit SHA, release tag, or the strongest reproducible identifier pinned in manifests/ for the evaluated version the evidence refers to. Empty for hosted-only components. |
| 8 | file_path_or_endpoint | Path of the file within the repository, or the endpoint (URL, route, deep link, screen identifier) observed. |
| 9 | mechanism | What the SUT exposes: the feature, endpoint, account, dataset, flag, fault, or other mechanism the record describes. For negative evidence: what was searched for and not found. |
| 10 | expected_behavior | The observable outcome the mechanism should produce. Required for any record supporting Score 3; it carries the ground truth claim (protocol/capability-rubric-v1.md). |
| 11 | evidence_status | One of DOCUMENTED, SOURCE_VERIFIED, EXECUTION_VERIFIED, INFERRED. |
| 12 | structural_scope_note | Descriptive annotation for a structural absence or narrowness, using the vocabulary of protocol/capability-rubric-v1.md (NO_WEB_SURFACE, NO_MOBILE_SURFACE, NO_API_SURFACE, INTENTIONAL_SPECIALIST_SCOPE, OTHER_STRUCTURAL_REASON, each optionally followed by `: ` and free text; the free text is required for OTHER_STRUCTURAL_REASON). Empty for every record that does not document a structural reason. Never modifies provisional_score. |
| 13 | notes | Free text: observation date for hosted-only components (`observed=YYYY-MM-DD`), references to execution verification records (`verification=SUT0n-VR-nnnn`), references to retained artifacts, references to contradicting or corrected records by evidence_id (`contradicts=SUT0n-EV-nnnn`; `corrects=SUT0n-EV-nnnn`), the evidence-ceiling limitation where it applies, an unresolved tie-break verification requirement where the "Tie-break rule for undecidable adjacent scores" applies (protocol/capability-rubric-v1.md), and auditor remarks. |

The exact CSV header line is:

```
evidence_id,ecosystem_id,modality,provisional_score,evidence_type,repository,commit_sha_or_release,file_path_or_endpoint,mechanism,expected_behavior,evidence_status,structural_scope_note,notes
```

- audits/<SUT>/evidence.csv holds the records for one ecosystem, one record per line, header on line 1. The header line is identical in all six files.
- schemas/evidence.schema.json is the machine-readable form of this record definition. If the two disagree, this document is corrected through protocol/change-control-v1.md and the schema follows it.
- Fields containing commas, quotes, or line breaks are quoted per RFC 4180. An empty field means unknown or not applicable; nothing is invented to fill it.

## Execution verification records

Capability auditing does not by itself require a run manifest. The requirement depends on the evidence status:

| evidence_status | Execution provenance required |
|---|---|
| DOCUMENTED | none |
| SOURCE_VERIFIED | none |
| INFERRED | none |
| EXECUTION_VERIFIED | one execution verification record per verifying execution, referenced from the evidence record's notes |

An execution verification record is a run manifest conforming to schemas/run-manifest.schema.json, used with the following conventions so that no second execution framework exists:

| Provenance element | Run-manifest field | Convention for E01 |
|---|---|---|
| verification_id | run_id | Format `SUT0n-VR-nnnn` (regular expression `^SUT0[1-6]-VR-[0-9]{4}$`), sequential per ecosystem, never reused. |
| campaign | campaign_id | `E01-capability-audit`. |
| experiment | experiment_id | `verification`. |
| sut_id | sut_id | The ecosystem verified. |
| modality | modality | The frozen modality name the verification concerns. |
| environment_type | environment_type | One of PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, OTHER (protocol/study-design-v1.md, section 10). |
| timestamp | timestamp | RFC 3339 start time. |
| sut_provenance | sut_provenance | Components touched, each with repository, commit SHA or release, endpoint, and environment type. |
| toolchain / probe | toolchain | Every tool or probe used (HTTP client, browser runner, mobile runner, scanner) with its exact version; a null version only with a justification in notes. |
| scenario_or_probe | scenario | What was executed: the request, navigation, or probe, stated so that it can be repeated. |
| outcome | outcome | status plus expected, observed, and matches_expected. |
| artifact references | artifacts | Paths of retained artifacts (logs, responses, screenshots) under audits/<SUT>/artifacts/, with sha256 where computed. |
| related evidence_id | related_evidence_ids | The evidence_id(s) the verification supports or refutes. |
| platform | platform | The surface exercised (web, api, android, ios). |
| attempt | attempt | 1, unless the same probe is repeated, in which case each repetition is its own record with its own attempt number. |
| protocol_version, prompt_version, agent_role | same | As for any run (prompts/README.md, rule 5). |

Rules:

- Storage: audits/<SUT>/verifications/<verification_id>.json for the record and audits/<SUT>/artifacts/ for the retained artifacts, both inside the auditor's own workspace (protocol/agent-governance-v1.md). E01 verification records are not stored under raw-data/, which holds campaign data only (raw-data/README.md).
- Linkage: the evidence record's notes field carries `verification=<verification_id>`; the verification record's related_evidence_ids carries the evidence_id(s). A record with evidence_status EXECUTION_VERIFIED and no linked verification record is treated as DOCUMENTED or INFERRED, whichever fits, and flagged for adjudication.
- Environment discipline: verifications against a PUBLIC_HOSTED instance are limited to non-destructive, session-scoped interactions within documented or intended use (protocol/study-design-v1.md, section 10.2). Anything beyond that requires a controlled instance.
- A failed or inconclusive verification is retained as a record (outcome.status FAILURE or INCONCLUSIVE) and is negative evidence; it is never deleted.
- Verification records do not create scores. They support evidence records, which support scores under protocol/capability-rubric-v1.md.
- No verification record exists at this time.

## Negative evidence

Absence of a capability is evidence and is recorded, not omitted.

- An absence record uses the same thirteen fields. mechanism describes what was searched for and where it was not found; evidence_status reflects how the search was performed (DOCUMENTED for documentation searched, SOURCE_VERIFIED for source searched at the recorded commit SHA or release, EXECUTION_VERIFIED for an attempted execution that did not produce the behavior, INFERRED for an indirect signal of absence); provisional_score is empty or 0; expected_behavior states what would have been observed had the mechanism existed; structural_scope_note carries the structural reason when the absence is structural (protocol/capability-rubric-v1.md); notes records the search scope.
- Limitations of the audit itself — components that could not be reached or built, platforms not available to the auditor, tooling not yet installed, the evidence ceiling for closed-source components, contradictions awaiting adjudication, cells decided by the tie-break rule — are described in audits/<SUT>/limitations.md and referenced from the notes field of the affected records where one exists.
- Negative evidence and limitations are reported for every ecosystem under the same rules; no ecosystem is exempt and none is privileged.

## Retention

- Evidence records are never deleted and never renumbered. audits/<SUT>/evidence.csv is append-only: a record, once written, is not edited, and rows are not reordered.
- A correction is a new record appended to the file, with its own evidence_id, whose notes field references the corrected record by evidence_id (`corrects=SUT0n-EV-nnnn`) and states what was wrong. The corrected record remains in place unchanged.
- Execution verification records and the artifacts they reference are kept for the life of the study in audits/<SUT>/verifications/ and audits/<SUT>/artifacts/.
- Records gathered under one protocol version are not rewritten when a new protocol version is created; the audit states the protocol version it was performed under.

## Versioning

This document is evidence-rules v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6). The `evidence_id` field, the `structural_scope_note` field, and the execution verification record were added during the pre-freeze hardening iteration of 2026-09-15 while the document was DRAFT (protocol/change-control-v1.md, section 2, DRAFT -> DRAFT). The Score 3 confirmation rule (DOCUMENTED alone yields `UNCONFIRMED_SCORE_3`, never a confirmed Score 3) was added during the second pre-freeze hardening iteration of 2026-09-16, resolving protocol/study-design-v1.md, section 13, issue (x); the thirteen evidence record fields and the evidence.csv header are unchanged by this addition. The cross-reference to the general tie-break rule and the resolution of the `observed=YYYY-MM-DD` notes convention were added during the final pre-freeze checklist closure of 2026-09-16 (explicit human decision), while the document was still DRAFT (DRAFT -> DRAFT); the thirteen evidence record fields and their order are unchanged. Now that the document is frozen, any change to the statuses, the rules, the record fields, or their order creates protocol/evidence-rules-v2.md per protocol/change-control-v1.md; this frozen version is never overwritten in place, and schemas/evidence.schema.json is versioned alongside.
