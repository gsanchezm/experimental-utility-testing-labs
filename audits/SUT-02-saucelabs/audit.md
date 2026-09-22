# SUT-02 — Sauce Labs Demo Ecosystem — Audit

Template only. Audit status: NOT_STARTED. No cell below is populated. Do not populate until the protocol is FROZEN-PRE-DATA (protocol/change-control-v1.md) and ORCHESTRATOR has issued an explicit start instruction. Rules: audits/README.md, protocol/capability-rubric-v1.md, protocol/evidence-rules-v1.md, protocol/cross-cutting-properties-v1.md.

## 1. Header

| Field | Value |
|---|---|
| ecosystem_id | SUT-02 |
| ecosystem_name | Sauce Labs Demo Ecosystem |
| role | general-purpose baseline |
| auditor_role | AUDITOR-SUT02-SAUCELABS |
| protocol_version | v1 |
| rubric_version | v1 |
| evidence_rules_version | v1 |
| audit_status | NOT_STARTED |
| started_at | |
| submitted_at | |
| environment_types_used | |
| controlled_instance_available | |

Allowed values for audit_status: NOT_STARTED, IN_PROGRESS, SUBMITTED, ADJUDICATED. environment_types_used lists the distinct environment types (PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, OTHER; protocol/study-design-v1.md section 10) under which EXECUTION_VERIFIED evidence was collected; empty if none. controlled_instance_available is true or false once verified: true when every component surface that E01 confirmed present can be run by the study, from the pinned evaluated version, in a controlled environment (SELF_HOSTED or LOCAL for web and api service components; EMULATED or SIMULATED for android and ios application builds); false otherwise, naming the components that cannot in limitations.md (protocol/study-design-v1.md, sections 10.1 and 10.5); it is an experimental-control fact, never a score input. Dates as YYYY-MM-DD. Machine-readable form: schemas/sut-audit.schema.json.

## 2. Components and provenance

Each row is one surface to verify for the system under test (SUT); every ecosystem lists the same four surfaces so that presence and absence are verified identically. Provenance is copied from manifests/sut-manifest.yaml, where the ORCHESTRATOR pins the evaluated version before E01 starts (sequence in manifests/README.md): repository and endpoint verbatim, and commit_sha or release (whichever is non-null; or the strongest reproducible identifier the ORCHESTRATOR recorded) into commit_sha_or_release. It must be filled before section 3 is touched. The auditor verifies the pinned target and records evidence against it only; switching to another version, branch, fork, or deployment because it exposes a more favorable capability is prohibited. verified_by and verified_at in this table record the auditor's presence verification; the ORCHESTRATOR's pin keeps its own verified_by and verified_at in the manifest. A discrepancy observed during the audit is recorded in unresolved.md, never corrected here or in the manifest. presence values: CONFIRMED, ABSENT, UNCONFIRMED.

| component | presence | repository | commit_sha_or_release | endpoint | verified_by | verified_at |
|---|---|---|---|---|---|---|
| web | UNCONFIRMED | | | | | |
| api | UNCONFIRMED | | | | | |
| android | UNCONFIRMED | | | | | |
| ios | UNCONFIRMED | | | | | |

## 3. Modality assessments

One row per frozen modality (protocol/study-design-v1.md), in the frozen order. provisional_score uses the 0–3 scale of protocol/capability-rubric-v1.md; there is no N/A level, and a structurally absent surface is Score 0. confirmed_score is filled only when the tie-break rule caps it below provisional_score (protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores": the highest rubric level whose complete requirements are fully supported by the evidence); it is the value used by every count, frequency table, and comparison. evidence_refs list the evidence_id values (SUT0n-EV-nnnn) of the supporting records in evidence.csv, per protocol/evidence-rules-v1.md; row or line numbers are never used. verification_refs list the verification_id values (SUT0n-VR-nnnn) of the execution verification records in verifications/ that support EXECUTION_VERIFIED evidence. structural_scope_note is filled, neutrally, when the modality is absent or narrow for a structural reason (NO_WEB_SURFACE, NO_MOBILE_SURFACE, NO_API_SURFACE, INTENTIONAL_SPECIALIST_SCOPE, OTHER_STRUCTURAL_REASON, optionally followed by a colon and free text, the free text being required for OTHER_STRUCTURAL_REASON; protocol/capability-rubric-v1.md); it never modifies the score (see limitations.md). confirmation_state is filled only when provisional_score is 3, derived from the evidence_status of the supporting records: UNCONFIRMED_SCORE_3 when the only supporting evidence is DOCUMENTED (confirmed_score is then 2); CONFIRMED when at least one SOURCE_VERIFIED or EXECUTION_VERIFIED record supports the mechanism (confirmed_score is then 3; protocol/capability-rubric-v1.md, "Score 3 confirmation").

| modality | provisional_score | confirmed_score | confirmation_state | evidence_status_summary | evidence_record_count | evidence_refs | verification_refs | rationale | structural_scope_note |
|---|---|---|---|---|---|---|---|---|---|
| Web UI Functional | | | | | | | | | |
| API | | | | | | | | | |
| Android Native | | | | | | | | | |
| iOS Native | | | | | | | | | |
| Performance | | | | | | | | | |
| Accessibility — Web only | | | | | | | | | |
| Visual Testing | | | | | | | | | |
| Security Testing | | | | | | | | | |
| Localization / i18n | | | | | | | | | |

Scores are provisional until adjudicated by ADJUDICATOR-EU-01. Every non-zero score requires evidence records in evidence.csv; every Score 0 cell has at least one negative-evidence record. INFERRED evidence alone cannot justify score 3. Generic tool reachability never justifies a score >= 2. Local deployability never justifies any score. The evaluated version must already expose any mechanism claimed for score 3. Every EXECUTION_VERIFIED record has an execution verification record in verifications/ (protocol/evidence-rules-v1.md). A Score 3 cell resting only on DOCUMENTED evidence is recorded with confirmation_state UNCONFIRMED_SCORE_3 and is not a confirmed / adjudicated Score 3 (protocol/study-design-v1.md, section 13, issue (x), RESOLVED). Undecidable adjacent scores of any kind apply the tie-break rule (protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores"): confirmed_score is the highest fully-supported level; the auditor never averages, rounds up, or decides by plausibility.

## 4. Cross-cutting properties

Descriptive only; no property is scored (protocol/cross-cutting-properties-v1.md).

### State Controllability

Description (descriptive only, no score): 
Evidence refs (evidence_id): 

### Resetability

Description (descriptive only, no score): 
Evidence refs (evidence_id): 

### Determinism

Description (descriptive only, no score): 
- deterministic: 
- stochastic: 
- time-dependent: 
- external dependency: 
Evidence refs (evidence_id): 

### Observability

Description (descriptive only, no score): 
Evidence refs (evidence_id): 

### Automation Affordances

Description (descriptive only, no score): 
Evidence refs (evidence_id): 

### Cross-platform Scenario Parity

Description (descriptive only, no score): 
Evidence refs (evidence_id): 

### Cross-layer State Continuity

Description (descriptive only, no score): 
Evidence refs (evidence_id): 

### Functional Complexity

Description (descriptive only, no score): 
Evidence refs (evidence_id): 

## 5. Documentation vs implementation contradictions

One row per claim where documentation and the evaluated implementation disagree.

| claim | documentation source | implementation observation | evidence refs |
|---|---|---|---|

## 6. Negative evidence summary

Negative evidence (mechanisms looked for and not found, executions attempted and failed) is retained as evidence.csv records and is not deleted. Summarize here by pointing to those records by evidence_id and to the relevant entries in limitations.md. Nothing recorded yet.

## 7. Auditor declaration

- [ ] The same rubric (protocol/capability-rubric-v1.md) was applied to every modality.
- [ ] The SUT was not modified.
- [ ] No capability was inferred from vendor commercial products.
- [ ] All evidence has provenance (repository and commit SHA / release, or endpoint) against the pinned target.
- [ ] Every evidence record has a unique evidence_id, and every reference uses evidence_id.
- [ ] Every EXECUTION_VERIFIED record is linked to an execution verification record with environment_type.
- [ ] Negative evidence was retained, and structural absences carry a structural_scope_note.
- [ ] No fault activation, active security testing, load, or state change visible to other users was performed against a PUBLIC_HOSTED instance.
