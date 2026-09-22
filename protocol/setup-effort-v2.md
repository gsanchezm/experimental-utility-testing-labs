# Setup Effort

| Field | Value |
|---|---|
| Document | protocol/setup-effort-v2.md |
| Protocol version | v2 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-21 |
| Supersedes | protocol/setup-effort-v1.md (transitions to AMENDED by this freeze, per protocol/change-control-v1.md, section 2 — `data_collection_started` is already true) |
| Freeze approval | gilbertosanchez, 2026-09-21 (explicit human ruling on Issue (xviii); authorization id `ISSUE-XVIII-RULING-01`; protocol/change-control-v1.md, section 5, post-data-collection change) |

## What changed relative to v1, and why

`protocol/study-design-v1.md`, section 13, issue (xviii) — the two Setup Effort counting rules left open at v1's own freeze (whether verification counts as a Required Action; how a partially successful action is counted) — was classified `HUMAN_RULING_REQUIRED` after independent source-backed ambiguity analysis (`experiments/E03-resetability/issue-xviii-analysis.md`, 2026-09-21) and put to the human research lead. The human research lead ruled:

- **Verification-as-action = A2.** A post-reset/post-establish verification counts as a Required Action when its underlying mechanism satisfies the frozen Required Action definition (Section 5, rule 1). It is not excluded merely because its purpose is verification or observation; it is classified by its actual mechanism/action class (Section 4), exactly like any other action.
- **Partial-success counting = B1.** A partially successful experimenter-initiated action contributes exactly one Required Action, the same as a fully successful one. Its success/partial-success/failure outcome is recorded separately from the count (new Section 5, rule 8, below) and must not be converted into a retry unless another actual attempt of that action occurs (Section 5, rule 4, unchanged).

This is a **narrow operational resolution**, not a new methodological decision: it fixes how two previously-open boundary cases are counted under the already-frozen Required Actions definition (Section 3) and action-class taxonomy (Section 4), which are otherwise unchanged. It does not create a new metric, modify H2, modify any research question, alter the comparison population, alter E01, reinterpret any historical E01 evidence, privilege any system under test (SUT), or introduce post-hoc scoring.

**Only Section 5 changes in substance** (the "Items still open" block is removed and replaced by the ruling, as new rule 8, with a worked example as rule 9). Sections 1–4 and 6–11 are carried forward from v1 verbatim in substance; this document restates them in full because a frozen document is never edited in place and a successor version must be a complete, standalone document (protocol/change-control-v1.md, section 4).

**Affected campaigns (protocol/change-control-v1.md, section 5, item 3):** E02-state-establishment and E04/E05 (E04/E05 sample Required Actions indirectly through E03's reset procedures for repeatability conditions) are unaffected in substance since neither has collected any data; **E03-resetability is the campaign this ruling directly operationalizes.** No campaign has any already-collected Required Actions data: v1's own Section 5 explicitly forbade recording any such count for analysis ("No Required Actions count may be recorded for analysis until these rules are frozen"), and E02/E03 remain NOT_STARTED. There is therefore nothing to re-collect and nothing to re-analyze under the old version — v1 governed zero recorded counts for its entire existence. E01's data is wholly unaffected: E01 does not use Setup Effort or Required Actions (protocol/study-design-v1.md, section 4, dimension-to-campaign mapping: Setup Effort informs only E02, E03).

## 1. Purpose

Setup Effort is dimension 6 of the Experimental Utility profile and informs RQ2 (Controllability, Observability, Automation Affordances, and Setup Effort). Both are defined in protocol/study-design-v1.md.

This document defines how Setup Effort is measured for a testing laboratory ecosystem, the system under test (SUT) of this study. The measurement applies identically to every evaluated ecosystem (SUT-01 through SUT-06). Setup Effort is reported per ecosystem and per target state; it is never combined with other dimensions into an aggregate score.

## 2. Two effort concepts

Setup Effort distinguishes two concepts that are recorded separately and never mixed.

| Concept | Definition | Examples | Recorded as |
|---|---|---|---|
| ONE-TIME PROVISIONING | Work performed once to make an instance of the ecosystem available in a given environment before any run. It precedes the declared starting state of every run. | installing dependencies; building an application; first emulator or simulator setup; downloading binaries; starting services; obtaining or configuring a hosted account | A descriptive provisioning record (Section 8), for reproducibility only |
| PER-RUN / PER-CONDITION SETUP | Actions performed within a run to move the ecosystem from the declared starting state to the declared target state, and back. | login; seed state; navigate; create cart; reset session; set locale; activate condition | Required Actions (Section 3), the primary metric |

The primary Setup Effort measure for RQ2 concerns PER-RUN / PER-CONDITION SETUP only. One-time provisioning is recorded descriptively so that an instance can be reproduced, but it never enters the primary setup-effort comparison, is never counted in Required Actions, and is never converted into a score. Whether an ecosystem is easy or hard to provision is not part of the Experimental Utility construct (protocol/study-design-v1.md, section 10).

## 3. Primary metric — Required Actions

**Required Actions** is the count of discrete per-run / per-condition actions an experimenter must perform to establish a defined target state in an ecosystem, starting from a defined starting state. The count for resetting the ecosystem back to the starting state is recorded separately, under the same rules.

Two counts therefore exist for each (ecosystem, target state) pair:

| Count | From | To |
|---|---|---|
| Required Actions — establish | declared starting state | declared target state |
| Required Actions — reset | declared target state (or any modified state reached from it) | declared starting state |

A lower count indicates lower setup effort for that target state. Required Actions is a count, not a rate and not a score; it is not mapped onto the capability rubric of protocol/capability-rubric-v1.md.

## 4. Action classes

Each required action is classified as exactly one of the following six classes.

| Class | Definition | Neutral example |
|---|---|---|
| API action | A request sent to a programmatic interface of the ecosystem to create, modify, or read state. | Sending a request that creates a user account. |
| UI action | An interaction with a graphical interface element, such as a click, tap, key entry, or selection. | Typing a password into a login form field. |
| navigation action | Moving to a page, screen, route, or deep link without changing business state. | Opening a deep link that lands on an item detail screen. |
| state/configuration action | Changing configuration, feature flags, environment variables, seed data, or fixtures that determine how the ecosystem behaves, within a run. | Setting a locale or activating a documented condition before the stimulus. |
| reset action | An operation whose purpose is to return the ecosystem, or part of it, to the declared starting state. | Calling a documented reset endpoint so that seeded data is discarded. |
| manual action | An action that cannot be scripted or that requires human judgement or physical intervention. | Clearing an application's stored data through a device's settings screen because no programmatic reset exists. |

An action that could fit more than one class is classified by its purpose, not by its mechanism: an API call whose purpose is reset is a reset action; a UI interaction whose purpose is only to reach a screen is a navigation action. **A verification/observation action is classified the same way: by the mechanism that carries it** (for example a read-only `GET` used to confirm a reset is an API action; reading UI text to confirm a reset is a UI action), never by a separate "verification" class — no seventh class is created (Section 5, rule 8).

## 5. Counting rules

These rules are **FROZEN-PRE-DATA as of this version.** No Required Actions count may be recorded for analysis until a run is executed under this version or later.

1. **One action = one experimenter-initiated operation with an observable effect.** An operation with no observable effect on the ecosystem or the experimenter's position in it is not an action.
2. **A scripted sequence counts each constituent action.** Running a script that performs five operations counts five actions, not one. Scripting reduces manual effort but does not reduce the count.
3. **Authentication counts.** Every login, token acquisition, session renewal, or credential entry required to reach the target state is counted.
4. **Retries caused by failure are counted and tagged.** A retried action is counted each time it is performed and each repetition is tagged as a retry, so that the count with and without retries can both be derived. A partially successful action (rule 8) is never itself converted into a retry: a retry exists only when the experimenter performs another actual attempt of that action; a single partially successful attempt is one action, not a retry of itself.
5. **Manual actions are recorded with a reason.** Each manual action carries the reason why it could not be scripted.
6. **The starting state must be declared, and provisioning precedes it.** The count begins at a declared, reproducible starting state. One-time provisioning (Section 2) is complete before the starting state exists; provisioning operations are never counted. Actions performed before reaching the starting state are not counted.
7. **The same canonical scenario is used across ecosystems.** A target state is defined once, in ecosystem-neutral terms, as a canonical experimental intent under protocol/equivalent-scenario-mapping-v1.md (business intent, precondition class, actor state, target state or transition, observable oracle class, reset requirement, applicable surfaces, allowed domain mapping). Each ecosystem realizes it through its own frozen mapping record; the domain object, vocabulary, selectors, endpoint names, and number of workflow steps may differ, but the semantic intent may not. A count is comparable between two ecosystems only when both are marked COMPARABLE in the frozen mapping record; a NOT_COMPARABLE ecosystem has no count for that scenario and is reported as such, not as zero.
8. **Verification/observation counts, classified by mechanism (resolves issue (xviii), part 1 — human ruling A2, 2026-09-21).** An operation whose purpose is to verify or observe that a target state (or a reset state) has been reached counts as a Required Action under rule 1 exactly like any other experimenter-initiated operation with an observable effect (the experimenter's position — what they now know and can next do — is itself the observable effect; Section 4's plain-text test does not require an effect on the ecosystem's own state). It is never excluded merely because its purpose is verification rather than establishment or reset, and it receives no separate "verification" action class: it is classified under Section 4 by its actual underlying mechanism (an API call used only to verify is an API action; a UI read used only to verify is a UI action; and so on). This rule applies identically to establish-side and reset-side verification, and identically to every ecosystem — an ecosystem whose realization requires an explicit post-action check (for example, the documented pattern in a mapping record's `oracle_realization`) is counted accordingly; this is not a penalty, it is the measurement.
9. **Partial success counts as one action; its outcome is recorded separately (resolves issue (xviii), part 2 — human ruling B1, 2026-09-21).** A partially successful experimenter-initiated action (one that produces some but not the full intended observable effect on a single attempt) contributes exactly one Required Action, the same as a fully successful attempt of the same action — Section 3's count is of discrete operations performed, not of operations that fully succeeded. Its outcome — SUCCESS, PARTIAL_SUCCESS, or FAILURE — is recorded per action, separately from the count itself, so that success rate and Required Actions remain distinct, uncombined observations (consistent with Section 1's prohibition on combining metrics). Recording this outcome is a schema-level concern; where the current run-manifest schema (schemas/run-manifest.schema.json) has no field for it, this is reported as a schema gap under protocol/agent-governance-v1.md's ordinary escalation path, not resolved by inventing an unrecorded convention. **Worked example (neutral, illustrative only):** an experimenter submits a form with three required fields; the ecosystem accepts and applies two of the three (partial success). This is one UI action, outcome PARTIAL_SUCCESS. If the experimenter then submits the form again to correct the third field, that second submission is a second, separate action — a retry only if it repeats the identical prior operation after a failure (rule 4); if it is a different, corrective operation (for example, submitting only the one previously-rejected field), it is a new action in its own right, not a retry.

## 6. Secondary metric — Duration

Duration may be recorded as a secondary metric, subordinate to Required Actions (Section 3), which remains the primary Setup Effort metric. Duration never replaces Required Actions; it is reported alongside the count, not instead of it, and it is not combined with the count into a derived quantity. Frozen by explicit human decision, 2026-09-16 (carried forward unchanged from v1).

### 6.1 Per-condition / per-run setup duration (establish)

- **START:** immediately before the first action required to establish the frozen experimental target state (the same action that Required Actions — establish begins counting from, Section 3).
- **STOP:** when the target-state postcondition has been independently verified and the SUT is ready for execution of the experimental oracle / stimulus. The verification that establishes readiness marks the end boundary; the duration includes the time to perform that verification, not merely to attempt the state change. (This duration boundary is independent of whether the verification action itself is counted as a Required Action under Section 5, rule 8 — Duration and Required Actions remain two distinct, never-combined metrics, Section 1.)
- **Excluded** from this duration (they belong to one-time provisioning, Section 2, and are recorded, if at all, only in the provisioning record, Section 8): dependency installation; source checkout; first build; emulator or simulator creation; initial application installation; first-time infrastructure startup; tool installation; researcher preparation.

### 6.2 Reset duration

- **START:** immediately before the first action whose purpose is to restore the frozen reset state.
- **STOP:** when the reset postcondition has been independently verified. The same exclusions as 6.1 apply (provisioning is never counted in reset duration).

### 6.3 Setup failure

If the target state (or, for reset, the reset state) is not successfully established, the measured elapsed duration to the point of failure is retained, the outcome is recorded as a failure (per the run manifest's `outcome.status`, schemas/run-manifest.schema.json), and no successful setup duration is fabricated. A failed attempt therefore still produces a duration observation — one that ended in failure, not one that is silently discarded. This run-level `outcome.status` (SUCCESS/FAILURE/ERROR/INCONCLUSIVE/ABORTED) is distinct from the per-action outcome of Section 5, rule 9 (SUCCESS/PARTIAL_SUCCESS/FAILURE): a run can carry an overall FAILURE while containing individual actions that each fully succeeded, and a run can succeed overall while containing one or more PARTIAL_SUCCESS actions along the way. Neither is inferred from the other.

### 6.4 Campaign-specific counting

Superseded by Section 5, rules 8–9, above: the partial-success counting rule this section previously deferred (as issue (xviii)) is now resolved. This section is retained, with its substantive content removed, only so that a cross-reference to "Section 6.4" in an earlier record is not silently orphaned.

## 7. Excluded metrics

The following must NOT be used as primary metrics for Setup Effort:

- lines of code written to establish or reset a state;
- implementation hours;
- subjective developer difficulty ratings;
- any provisioning quantity (provisioning step count, provisioning duration, build time, download size).

They may appear only as descriptive context, clearly labeled as such, and they do not enter the quantitative comparison defined in protocol/statistical-analysis-plan-v1.md.

## 8. Provisioning record

One provisioning record is written per ecosystem per environment instance used by a campaign (for example one SELF_HOSTED backend instance, one EMULATED Android instance). It is descriptive reproducibility metadata, not part of the primary Setup Effort comparison, and exists so that the instance can be reproduced. Frozen by explicit human decision, 2026-09-16 (carried forward unchanged from v1).

| Field | Content |
|---|---|
| provisioning_id | `SUT0n-PROV-nnnn`, sequential per ecosystem |
| sut_id | SUT-01 … SUT-06 |
| environment_type | PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, or OTHER (protocol/study-design-v1.md, section 10) |
| instance_identifier | Host, container, emulator or simulator identity, or hosted endpoint |
| sut_provenance | Repository and commit SHA or release, or endpoint, as pinned in manifests/sut-manifest.yaml |
| steps | Ordered, descriptive list of provisioning operations (install, build, download, configure, start), each following the per-step template of manifests/provisioning/README.md (component, operating_system, prerequisite, installation/build step, required external dependency, estimated or observed duration if recorded, automation/manual classification, provenance, notes — no field required when not applicable) |
| duration | Optional wall-clock duration of provisioning; descriptive only; never added to the Duration secondary metric of Section 6 |
| performed_by | Agent role or human operator |
| date | YYYY-MM-DD |
| campaigns_served | Campaign ids that used this instance |
| notes | Deviations, retries, and anything needed to reproduce the instance |

Storage: manifests/provisioning/<sut-id>/<provisioning_id>.yaml (manifests/provisioning/README.md), authored by the ORCHESTRATOR from the provisioning facts relayed by the role that performed the provisioning — the same manifests/-authorship pattern already used for `sut-manifest.yaml` and `toolchain-manifest.yaml` (manifests/README.md); no other role writes under manifests/ (protocol/agent-governance-v1.md). A provisioning record is referenced from the run manifests of the runs executed on that instance (run manifest notes, convention `provisioning=<provisioning_id>`). E01 execution verifications require no provisioning record: the verification record's sut_provenance, environment, and toolchain fields carry the provenance of the instance used (protocol/evidence-rules-v1.md). Because a provisioning record is keyed by instance rather than by campaign, it is written once per instance and referenced by every campaign that reuses that instance (`campaigns_served`), rather than being filed under one campaign's directory.

## 9. Recording

- Each establish run and each reset run produces one per-run record in raw-data/, written through the run manifest defined by schemas/run-manifest.schema.json, carrying `environment_type`.
- The run manifest carries the ordered action list for the run. For each action it must be possible to record the action class (Section 4), its position in the sequence, whether it is a retry, its per-action outcome (Section 5, rule 9), and, for a manual action, the reason. Field names are defined by the schema, not by this document; where the schema cannot represent a required field (for example the per-action outcome of rule 9, as of this version), that is a schema gap reported and resolved under ordinary change control, not worked around informally.
- The declared starting state and the canonical scenario id (protocol/equivalent-scenario-mapping-v1.md) are referenced from the run record so that every count is interpretable without the run log.
- Analysis of Required Actions and Duration follows protocol/statistical-analysis-plan-v1.md. The number of runs per condition follows the campaign definitions in experiments/E02-state-establishment and experiments/E03-resetability.

## 10. Establishment and reset mechanism vocabulary

Frozen by explicit human decision, 2026-09-16 (carried forward unchanged from v1). These vocabularies describe HOW the experimental condition was established or reset in a run; they say nothing about quality, and no mechanism is inferred to be better than another.

**Establishment mechanisms** (run manifest field `establishment_mechanisms`, schemas/run-manifest.schema.json; mandatory and non-empty for E02 runs):

`UI_FLOW`, `API_SEED`, `DIRECT_ROUTE`, `DEEP_LINK`, `FIXTURE`, `PREDEFINED_ACCOUNT`, `CONFIGURATION`, `APP_STATE_CONTROL`, `NONE`, `OTHER` (requires descriptive notes stating the mechanism).

**Reset mechanisms** (run manifest field `reset_mechanisms`, schemas/run-manifest.schema.json; mandatory and non-empty for E03 runs):

`API_RESET`, `SESSION_RESET`, `APP_RELAUNCH`, `APP_DATA_CLEAR`, `FIXTURE_RESTORE`, `ENVIRONMENT_RESTART`, `REDEPLOY`, `MANUAL`, `NONE`, `OTHER` (requires descriptive notes stating the mechanism).

Rules:

- A run may record one or more mechanisms from the applicable list (for example `PREDEFINED_ACCOUNT` + `API_SEED` + `DEEP_LINK` for one establishment); the field is an array, never a single forced choice.
- `MANUAL` is valid evidence for a reset and must not be hidden; it is not automatically penalized beyond the Setup Effort / automation-affordance observations already defined by this document (Sections 3–5) and protocol/cross-cutting-properties-v1.md (Automation Affordances).
- `OTHER` requires descriptive notes naming the actual mechanism; it is never left unexplained.
- These per-run mechanism vocabularies are distinct from, and must not be conflated with, the scenario-level `reset_requirement` vocabulary of protocol/equivalent-scenario-mapping-v1.md (NONE, SESSION_RESET, DATA_RESET, APP_RESET, ENVIRONMENT_RESET, OTHER): `reset_requirement` states what a canonical scenario requires to be restorable, in ecosystem-neutral terms, before any ecosystem realizes it; `reset_mechanisms` records, per run, which concrete mechanism(s) a given ecosystem actually used to satisfy that requirement. The two vocabularies share some token names deliberately (for example `SESSION_RESET`) but are recorded in different fields for different purposes and are never merged into one list.
- Recording no mechanism used (nothing was needed) is `NONE`, not an empty or omitted field.

## 11. Versioning

This is v2, state FROZEN-PRE-DATA (frozen 2026-09-21, approved by gilbertosanchez, authorization id `ISSUE-XVIII-RULING-01`, protocol/change-control-v1.md, section 5 — a post-data-collection protocol change, since `data_collection_started` was already true when this version was created and frozen). It supersedes protocol/setup-effort-v1.md, which transitions to AMENDED (not SUPERSEDED, per the same section 2 rule) and is retained unchanged apart from its header state field and a `Superseded by` row; no other content of v1 changes. Relative to v1: Section 5's two "Items still open" (issue (xviii)) are resolved as rules 8 and 9; Section 4 gains one clarifying sentence on verification-action classification; Section 6.1 and 6.3 gain one cross-referencing sentence each; Section 6.4 is retained as a redirect only, its substance moved to Section 5. No other section changes in substance from v1. This version is itself now FROZEN-PRE-DATA and is never overwritten in place; any further modification creates protocol/setup-effort-v3.md.
