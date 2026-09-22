# Change Control

| Field | Value |
|---|---|
| Document | protocol/change-control-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | first iteration instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT); second iteration (issues (x), (xi), (xx), explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT); final pre-freeze checklist closure (scenario-mappings location reference, explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## 1. Purpose

This document defines how protocol documents in `protocol/` move through their lifecycle, how they are versioned, how changes are recorded, and what may never change without an explicit, recorded decision. It exists so that every comparison involving an evaluated system under test (SUT) can be traced to the exact protocol version under which it was produced, and so that no protocol change can be made silently after data collection begins.

It applies to every file under `protocol/` except `protocol/CHANGELOG.md` (see section 5), `protocol/unresolved.md` (escalation log, see `protocol/agent-governance-v1.md` section 6), and `protocol/README.md`, which are navigational or log files, carry no protocol state of their own, and are never versioned. It also defines the campaign freeze mechanism (section 7), which is distinct from the protocol freeze (section 6) and is recorded in the same change log.

## 2. Protocol state lifecycle

Every versioned protocol document is in exactly one of the following states, recorded in the `Protocol state` field of its header block.

| State | Definition |
|---|---|
| DRAFT | Editable in place before freeze. No data may be collected under a DRAFT protocol. Edits require no formal approval but are subject to human review at freeze. |
| FROZEN-PRE-DATA | Approved by an explicit human decision before any data is collected under this version. Immutable: the file content is never changed again, except for the header state field and successor pointer described in section 4, and the narrow non-substantive corrections described below. |
| AMENDED | A frozen document that has been superseded by a new version created after data collection began. The change carries a recorded rationale and a list of affected campaigns (section 5). The AMENDED file is retained unchanged apart from its header. |
| SUPERSEDED | An older version replaced by a newer version before data collection began under it. Retained, never deleted. |

Documents are never deleted, renamed, or moved once they have been frozen. AMENDED and SUPERSEDED are terminal states for the file that carries them.

### State-transition table

| From | To | Trigger | Who approves |
|---|---|---|---|
| (new file) | DRAFT | Document is created | No approval required; author recorded in provenance |
| DRAFT | DRAFT | In-place edit before freeze | No approval required |
| DRAFT | FROZEN-PRE-DATA | Freeze procedure in section 6 completed | Explicit human approval, recorded in `protocol/CHANGELOG.md` |
| FROZEN-PRE-DATA | SUPERSEDED | A successor version is created and frozen while `data_collection_started` is still false | Explicit human approval, recorded in `protocol/CHANGELOG.md` |
| FROZEN-PRE-DATA | AMENDED | A successor version is created and frozen after `data_collection_started` became true | Explicit human approval with rationale and affected campaigns, recorded in `protocol/CHANGELOG.md` |
| Any state | (deleted) | Never | Not permitted |

A successor version created from a frozen document starts in DRAFT and follows the same transitions. The "PRE-DATA" in FROZEN-PRE-DATA means that no data has been collected under that specific version at the moment it is frozen; it does not mean the whole study is pre-data.

### Non-substantive corrections to a frozen document

A document in state FROZEN-PRE-DATA, AMENDED, or SUPERSEDED is immutable in the sense of this section: its methodological content is never changed in place. This does not forbid a narrow class of non-substantive corrections, which touch no methodological content: fixing a spelling or grammar error; reformatting (for example a table's layout, without changing any value it carries); repairing a broken internal cross-reference (a path or section number that no longer resolves); and correcting non-semantic metadata (for example filling in a header field left blank in error, in a way that records a fact rather than asserting a new one). A non-substantive correction never changes anything that can affect eligibility, scoring, variables, evidence interpretation, denominators, hypotheses, statistical treatment, scenario equivalence, or an experimental conclusion; any change that could affect one of those is substantive and requires a new version file under section 4 regardless of how small it appears. A non-substantive correction is recorded in `protocol/CHANGELOG.md` with `state change` = `non-substantive correction` and a description of exactly what was corrected; it does not change the `Protocol state` field and does not require the freeze procedure of section 6.

## 3. Current state

At repository initialization (2026-09-15) every protocol document under `protocol/` is in state DRAFT. The pre-freeze hardening iteration of 2026-09-15 edited the DRAFT documents in place (DRAFT -> DRAFT, section 2) and created `protocol/equivalent-scenario-mapping-v1.md` in state DRAFT. A second pre-freeze hardening iteration on 2026-09-16, by explicit human decision, resolved the three remaining OPEN rows of the Open-Issue Register — (x) Score 3 confirmation, (xi) outcome-rate denominators (TSRR/CEOR/E2E-ROR), (xx) the H3 wording — again editing the DRAFT documents in place (DRAFT -> DRAFT); no new protocol document was created and no document's state changed. A final pre-freeze checklist closure, also on 2026-09-16 by explicit human decision, resolved or explicitly deferred the remaining step-3 freeze-checklist items under `protocol/` and `schemas/` (this section, step 3), again editing the DRAFT documents in place. The Open-Issue Register stood at RESOLVED 18, OPEN 0, DEFERRED-BEFORE-CAMPAIGN 2 (protocol/study-design-v1.md, section 13) at that point, and step 3 of the freeze checklist below was clear.

**Protocol v1 pre-data freeze.** On 2026-09-16, by explicit human decision, the freeze procedure of section 6 was completed for protocol v1: every protocol v1 document's `Protocol state` was set to FROZEN-PRE-DATA, `Freeze approval` was recorded as gilbertosanchez, 2026-09-16, in each document's header, `protocol_state` in `manifests/study-manifest.yaml` was set to FROZEN-PRE-DATA with `protocol_frozen: true`, and this freeze is recorded in `protocol/CHANGELOG.md` (created by this freeze) and in `manifests/protocol-freeze-v1.yaml`. Issues (xviii) and (xix) remained DEFERRED-BEFORE-CAMPAIGN and were not resolved by this freeze; they block only their named campaigns (E02/E03 and E04/E05 respectively), never E01. `data_collection_started` in `manifests/study-manifest.yaml` remains false: freezing the protocol is necessary but not sufficient for data collection (manifests/README.md, "Data-collection gate"), and no campaign in `experiments/` has left status NOT_STARTED. No SUT audit, qualification run, or experiment has been performed.

## 4. Versioning rule

Protocol documents are named `<topic>-v<N>.md`. Any modification to a document in state FROZEN-PRE-DATA must be made by creating a new version file, never by editing the frozen file.

Example: to change `protocol/capability-rubric-v1.md` after it is frozen, create `protocol/capability-rubric-v2.md`. Do not overwrite v1.

Rules for the old file after a successor is frozen:

- Its `Protocol state` field changes to SUPERSEDED or AMENDED according to section 2.
- One row is added to its header table: `| Superseded by | protocol/<successor filename> |`.
- Nothing else in the file changes.

Rules for the new file:

- It begins with the standard header block, `Protocol version` set to the new version number, `Protocol state` DRAFT until approved.
- It states, near the top, what changed relative to the previous version and why.
- References in other repository files are updated to the new version only by a recorded change (section 5); agents do not re-point references on their own initiative.

## 5. Post-data-collection changes

Once `data_collection_started` is true, any protocol change requires all of the following:

1. A new protocol version file (section 4).
2. A written rationale.
3. An explicit list of affected campaigns (E01–E12) and a statement for each of whether already-collected raw data remains valid, must be re-collected, or must be analysed under the old version.
4. An entry in the change log.

### Change log

Location: `protocol/CHANGELOG.md`. The file does not exist yet; it is created on the first recorded change, which is expected to be the initial freeze (section 6). It is append-only: entries are never edited or removed. It carries no protocol state and is not itself versioned.

Fixed entry format, one row per change, newest last:

| date | document | from-version | to-version | state change | rationale | affected campaigns | approved by |
|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | protocol/<filename>, experiments/<campaign-id>/README.md, or experiments/scenario-mappings/<canonical_scenario_id>.yaml (or <canonical_scenario_id>-v<N>.yaml for a record version N >= 2) | v<N> or none | v<M> or none | e.g. DRAFT -> FROZEN-PRE-DATA; FROZEN-PRE-DATA -> AMENDED; campaign IN_PROGRESS -> FROZEN; run appended after campaign freeze; mapping DRAFT -> FROZEN | short text | comma-separated campaign ids or none | human name or identifier |

Campaign rows (section 7) use `document` = `experiments/<campaign-id>/README.md`, `from-version` and `to-version` = none, and `state change` = `campaign NOT_STARTED -> IN_PROGRESS`, `campaign IN_PROGRESS -> FROZEN`, or `run appended after campaign freeze` with the reason in `rationale`.

Mapping-record rows (`protocol/equivalent-scenario-mapping-v1.md`, section 6) use `document` = `experiments/scenario-mappings/<canonical_scenario_id>.yaml` for version 1 or `experiments/scenario-mappings/<canonical_scenario_id>-v<N>.yaml` for a later record version N (`protocol/equivalent-scenario-mapping-v1.md`, section 6), `from-version` = none for a first freeze or the previous record version, `to-version` = the record version being frozen, `state change` = `mapping DRAFT -> FROZEN` or `mapping v<N> -> v<M>`, and `affected campaigns` = every campaign that uses the record. One row per frozen mapping record; a frozen mapping record is never edited.

Every row must be complete. A row with an empty `approved by` cell is invalid and the change it describes is not in force.

## 6. Freeze procedure

Freezing moves the whole protocol set from DRAFT to FROZEN-PRE-DATA in a single recorded decision. Checklist, in order:

1. A human reviews every `protocol/*.md` document in full.
2. Every issue in the Open-Issue Register of `protocol/study-design-v1.md` section 13 has status RESOLVED (with the resolution written into the relevant document) or DEFERRED-BEFORE-CAMPAIGN (with the campaign and the written reason); no issue with status OPEN may remain, and no issue may be left unaddressed.
3. Every item marked "TBD before freeze" or "candidate — not frozen" in any document under `protocol/` or `schemas/` is either resolved and recorded in that document, or explicitly deferred to the configuration of a named campaign with a written reason recorded in that document and in the Open-Issue Register; no such item may be left unaddressed.
4. The `Protocol state` field in the header of each protocol document is set to FROZEN-PRE-DATA, and its `Freeze approval` field is updated to record the approving human and the date.
5. `protocol_state` in `manifests/study-manifest.yaml` is set to FROZEN-PRE-DATA.
6. Every agent prompt that will be used in a campaign is copied from `prompts/working/` to `prompts/frozen/` with a version id, as described in `prompts/README.md`.
7. The freeze is recorded in `protocol/CHANGELOG.md` (creating the file if it does not exist), one row per protocol document.
8. Only after steps 1–7 are complete may `data_collection_started` in `manifests/study-manifest.yaml` become true.

Steps 4–8 are performed by the ORCHESTRATOR role (see `protocol/agent-governance-v1.md`) only after the human approval in steps 1–3 is given explicitly; the approval itself is never inferred from silence, from elapsed time, or from the completion of setup work.

## 7. Campaign freeze

Two freezes exist in this study and must not be confused:

| Freeze | Locks | When | Approver |
|---|---|---|---|
| PROTOCOL FREEZE (section 6) | The methodological definitions: every document under `protocol/`, the schemas under `schemas/`, and the frozen prompts. Study-wide; happens once per protocol version. | Before any data collection | Explicit human approval |
| CAMPAIGN FREEZE (this section) | For one campaign: its scenario mappings (`protocol/equivalent-scenario-mapping-v1.md`), the SUT versions it runs against, the toolchain versions, the agent prompt version(s), the campaign configuration, the sample size (N per condition), and the exclusion / attribution rules. Per campaign; happens once per campaign. | Locked at campaign start; closed at campaign end | Explicit human approval |

A *campaign freeze* applies per campaign under experiments/ and has two moments:

1. **Campaign start (NOT_STARTED -> IN_PROGRESS).** On explicit human instruction, the ORCHESTRATOR records the campaign configuration in `experiments/<campaign-id>/README.md` under a heading "Campaign configuration": the canonical scenario ids and the state (FROZEN) of their mapping records, each frozen by its own mapping-record row (section 5) no later than this campaign-start row; the pinned SUT versions from `manifests/sut-manifest.yaml`; the toolchain versions from `manifests/toolchain-manifest.yaml`; the prompt version id(s) from `prompts/frozen/`; the conditions, their environment_type and, where applicable, their NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE status (`protocol/study-design-v1.md`, section 10); the sample size per condition; the exclusion and attribution rules; and the list of CONFIRMATORY comparisons (`protocol/statistical-analysis-plan-v1.md`, section 4). A `campaign NOT_STARTED -> IN_PROGRESS` row is written to `protocol/CHANGELOG.md` and the campaign status in `manifests/study-manifest.yaml` becomes IN_PROGRESS. From that moment every listed item is locked for the campaign: a change to any of them while IN_PROGRESS requires its own change-log row with the reason, and results collected before the change are analyzed under the earlier configuration.
2. **Campaign freeze (IN_PROGRESS -> FROZEN).** Trigger: every planned run of the campaign (all ecosystems, all conditions, the recorded N) has been executed, or the ORCHESTRATOR proposes closing the campaign early with a written reason. Approver: explicit human decision; never inferred. Record: one row in `protocol/CHANGELOG.md` in the campaign-row form of section 5 (`document` = `experiments/<campaign-id>/README.md`, `state change` = `campaign IN_PROGRESS -> FROZEN`), plus the campaign status in `manifests/study-manifest.yaml` set to FROZEN. Effect: from that moment `raw-data/<campaign-id>/` is append-only in the sense defined in raw-data/README.md: every existing raw file is immutable, and a further run may be appended only with a `run appended after campaign freeze` row in the change log stating the reason (raw-data/README.md, rule 1). The campaign configuration record is immutable from this moment. Before the freeze, raw files are still never edited (raw-data/README.md, rule 2); the freeze makes the set closed.

Campaign status vocabulary: NOT_STARTED -> IN_PROGRESS -> FROZEN. In prose, a status token may be written with spaces (for example "NOT STARTED"); the recorded value in manifests, schemas, and audit records is always the token (NOT_STARTED).

Both moments are proposed by the ORCHESTRATOR and approved by a human (see also `protocol/study-design-v1.md`, section 13, issue (xvii)). Reopening a frozen campaign follows section 5 in full: new protocol version file where a protocol document is affected, rationale, affected campaigns, change-log row.

## 8. What never changes silently

The following may change only through the versioning rule (section 4) and, after data collection begins, the post-data-collection procedure (section 5). None of them may be edited in place once frozen, and none may be changed by an agent on its own initiative at any time.

| Item | Where defined |
|---|---|
| Research questions RQ1–RQ5 | `protocol/study-design-v1.md` |
| Provisional hypotheses H1–H5 | `protocol/study-design-v1.md` |
| Testing modality list | `protocol/study-design-v1.md` section 7 |
| Capability rubric | `protocol/capability-rubric-v1.md` |
| Evidence rules and evidence statuses | `protocol/evidence-rules-v1.md` |
| Cross-cutting properties | `protocol/cross-cutting-properties-v1.md` |
| Analysis plan | `protocol/statistical-analysis-plan-v1.md` |
| Repetition targets | `protocol/repeatability-determinism-v1.md` section 3 |
| Mobile runner policy, qualification gate criteria, and compatibility smoke | `protocol/mobile-runner-policy-v1.md` |
| Equivalent scenario mapping method | `protocol/equivalent-scenario-mapping-v1.md` |
| Frozen scenario mapping records | `experiments/scenario-mappings/` (location fixed; protocol/equivalent-scenario-mapping-v1.md, section 6) — frozen by a mapping-record row (section 5) before the first campaign that uses them (section 7) |
| Campaign configuration records | `experiments/<campaign-id>/README.md`, "Campaign configuration" — locked at campaign start, section 7 |
| Open-Issue Register | `protocol/study-design-v1.md` section 13 — rows are never removed |
| Frozen prompts | `prompts/frozen/` |
| Raw data | `raw-data/` — append-only after campaign freeze (section 7); never edited, never deleted |

The dimensions of the Experimental Utility profile and the list of evaluated ecosystems are part of `protocol/study-design-v1.md` and fall under the same rule.

## 9. Versioning

This is `protocol/change-control-v1.md`, version v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, section 6). It is itself subject to the rules it defines: it is never overwritten in place; any substantive change creates `protocol/change-control-v2.md`. The "Non-substantive corrections to a frozen document" subsection (section 2) was added during the protocol v1 pre-data freeze of 2026-09-16, to reconcile this document's own immutability rule with the freeze semantics adopted at that freeze; it narrows nothing else in this document and resolves no Open-Issue Register row.
