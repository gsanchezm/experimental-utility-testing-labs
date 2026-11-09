# Second reset-side scenario for H2 -- options note (DRAFT)

| Field | Value |
|---|---|
| Status | **DRAFT.** Options only. Nothing is reopened, frozen, authorized, or dispatched. Every decision named here is a HUMAN DECISION. |
| Question | How could H2 get a second reset-side canonical scenario, given that E03-resetability is FROZEN? |
| Date | 2026-11-05 |
| Read | `protocol/change-control-v1.md` (sections 2, 5, 7, 8); `protocol/equivalent-scenario-mapping-v1.md` (sections 5, 6); `protocol/statistical-analysis-plan-v1.md` (sections 4.2, 4.3, 6); `experiments/E03-resetability/README.md`; `experiments/E03-resetability/ci-cd-execution-model.md` (section 3); `experiments/E03-resetability/canonical-scenario-catalogue.md`; `experiments/E03-resetability/executor/README.md` (sections 3, 4, 11); `experiments/scenario-mappings/CS-001.yaml`, `CS-003.yaml`; `protocol/agent-governance-v4.md` (section 3.5), `protocol/agent-governance-v5.md` (section 3.6); `manifests/campaign-resumption-v1.yaml`; E01 rows on the `audit/e01-sut0N-*` branches; companion `CS-004.yaml` and `design-brief-draft.md`. |
| Not read | `raw-data/`; the H2 reset-side result and analysis; `derived-data/` (the E01 matrix was not needed here). |
| Hygiene | English; the human research lead is the only person role; no local paths, assistant or vendor names, or conversation identifiers; the agent-instructions file is referred to by role. |

## 1. Facts that constrain every option (with sources)

1. **E03 is FROZEN.** The freeze was made on 2026-10-29 under `E03-FREEZE-AUTH-01` (`experiments/E03-resetability/README.md`, "Current status"; record `manifests/e03-campaign-freeze-v1.yaml`). The freeze is the moment-2 transition of `protocol/change-control-v1.md`, section 7. From that moment the campaign configuration is immutable (section 7, moment 2; section 8) and `raw-data/E03-resetability/` is append-only (section 7, moment 2).
2. **E03 has one canonical scenario.** CS-001 is the only accepted scenario of E03; CS-002 is EXCLUDED_FROM_CAMPAIGN by ruling `E03-CS002-EXCLUSION-RULING-01` (`experiments/E03-resetability/README.md`, "Canonical scenario and mapping record"; `manifests/e03-cs002-exclusion-v1.yaml`).
3. **The reset side of H2 is one scenario.** H2 names campaigns E02 and E03 and "Required Actions (establish; reset) per COMPARABLE canonical scenario" (`protocol/statistical-analysis-plan-v1.md`, section 4.3). E03 contributes only CS-001. The reset-side analysis on CS-001 was made descriptively on 2026-10-29 (`experiments/E03-resetability/README.md`, "Current status"; not read here).
4. **E03's measured data.** Seven web and API conditions, N = 50 each, 350 executions, dispatched between 2026-10-29T01:26Z and 2026-10-29T16:03Z UTC (`experiments/E03-resetability/README.md`, "Sample size per condition" and "Current status").
5. **The measured workflow refuses a frozen campaign.** Gate G-1 requires E03 to be IN_PROGRESS and "exactly one" `campaign NOT_STARTED -> IN_PROGRESS` change-log row for the E03 README carrying the authorization id (`experiments/E03-resetability/ci-cd-execution-model.md`, section 3, item 2). Gate G-3 checks CS-001 by name, and G-4 checks the CS-002 exclusion row (items 4 and 5 of the same section). The workflow's condition input lists the nine CS-001 conditions (`.github/workflows/e03-measured-execution.yml`, input choice list).
6. **The protocol defines no transition out of FROZEN.** The status vocabulary is "NOT_STARTED -> IN_PROGRESS -> FROZEN" (`protocol/change-control-v1.md`, section 7, last paragraph of the vocabulary note). Section 7 ends with "Reopening a frozen campaign follows section 5 in full". Section 5 concerns protocol documents: a new version file, a rationale, the affected campaigns, and a change-log row (section 5, items 1 to 4).
7. **"Campaign version" is not defined.** The phrase "current E03 campaign version" appears in `experiments/E03-resetability/canonical-scenario-catalogue.md` ("Active catalogue (current E03 campaign version)") and in the CS-001 notes. `protocol/change-control-v1.md` does not define it.
8. **Mapping freeze timing.** A mapping record must be FROZEN "before E02-E07 execution" and recorded "no later than the campaign-start row of the first campaign that uses it" (`protocol/equivalent-scenario-mapping-v1.md`, section 6; `protocol/change-control-v1.md`, section 5 mapping-record rows). E03's START row exists (2026-10-28; `manifests/e03-campaign-start-v1.yaml`). Read literally, a new reset scenario for E03 cannot satisfy this rule, because its freeze would come after that START row. The protocol is silent on whether a later freeze is allowed for a reopened campaign. HUMAN DECISION.
9. **Pre-registration of H2.** The concrete scenario and condition ids "are fixed in the campaign configuration before each campaign starts" (`protocol/statistical-analysis-plan-v1.md`, section 4.3). A confirmatory comparison "cannot be added, removed, or re-specified after the campaign has started except as a recorded protocol deviation" (section 6). A second reset scenario added to E03 therefore changes a pre-registered comparison.
10. **Dispatch authorization is per SUT and names the conditions.** The E03 dispatch authorization names "that SUT's executable conditions and the number N" (`protocol/agent-governance-v4.md`, section 3.5, as summarized in `experiments/E03-resetability/README.md`, "Execution"). A new condition for an existing SUT would need a new authorization. This note's reading, not stated verbatim.
11. **Workflow changes after the freeze have precedent under the CI grant.** The grant names IN_PROGRESS: while the campaign is IN_PROGRESS the ORCHESTRATOR does not edit a workflow "except as a CI correction under this authorization" (agent-instructions file, E03-CI-WRITE-AUTH-01). After the freeze, two CI corrections were made on approval: gate G-7 (operation OP-CI-14, 2026-11-03) and the dispatch-input correction of the measured workflow (operation OP-CI-15, 2026-11-05) (`experiments/E03-resetability/README.md`, "Current status"). Whether a gate-logic change that admits new conditions still counts as a "CI correction" is not stated. HUMAN DECISION.
12. **E03 preparation took about five weeks.** The human research lead's answer, recorded in `manifests/campaign-resumption-v1.yaml` (human_decision, answers, item 3), states that E03's preparation took about five weeks, from 2026-09-21 to 2026-10-28. It is the only repository statement of the cost of a campaign. Time estimates in this note are not derived from anything else.

## 2. What change-control requires, and where it is silent

| Topic | Stated rule (source) | Gap |
|---|---|---|
| Entry into a FROZEN campaign | Only NOT_STARTED -> IN_PROGRESS (moment 1) and IN_PROGRESS -> FROZEN (moment 2) are defined (section 7) | No transition FROZEN -> IN_PROGRESS; no "campaign version" |
| Changing a locked configuration | Locked from START; a change while IN_PROGRESS needs its own row; results before the change are analysed under the earlier configuration (section 7, moment 1); immutable after the freeze (moment 2; section 8) | Adding conditions or scenarios after the freeze is not described |
| Reopening | "Follows section 5 in full" (section 7) | Section 5 is written for protocol documents; a campaign configuration is not a protocol document |
| New mapping record | DRAFT -> FROZEN by a mapping row, no later than the first campaign's START row (equivalent-scenario-mapping, section 6) | Cannot be met by a scenario added to a campaign that already started |
| Raw data | Append-only after freeze; a further **run** may be appended with a "run appended after campaign freeze" row (section 7, moment 2) | The row is written for runs; it is not stated whether new conditions or a new scenario may be appended to the same directory |
| H2 specification | Scenario and condition ids fixed in the configuration before START (SAP, 4.3); no re-specification after START except as a recorded deviation (SAP, 6) | A recorded deviation for H2 is needed; the SAP has no rule for adding a scenario to a pre-registered comparison |
| Workflow | G-1 needs exactly one START row; G-3 names CS-001 | A reopened campaign has two or more such rows; the gates must change (a workflow change) |
| Dispatch | Per-SUT authorization naming conditions and N (agent-governance-v4, 3.5, for E03) | New conditions need a new authorization (section 1, item 10) |

**Closing rule for E03, stated so that any reopening can be checked against it:** E03 is FROZEN by the moment-2 freeze under `E03-FREEZE-AUTH-01` (`protocol/change-control-v1.md`, section 7). Its configuration is immutable (section 8) and its raw data are append-only (section 7). Nothing in the protocol removes that closure. A reopening therefore needs a new rule, which the text does not give (table above). This note does not invent one.

## 3. Options

Each option lists steps, approvals, and the main risk. "Approval" means an explicit human decision of that exact action.

### Option A -- Reopen E03 as a second campaign version, with a new change-control version

Requires a rule that does not yet exist. Steps:

1. Human decision: reopen E03 for a second reset scenario. (approval 1)
2. A protocol successor, `protocol/change-control-v2.md` (name a candidate), that defines reopening, campaign versions, and the lock point of a scenario frozen after START. Its freeze is a separate approval. Change-log row. (approval 2)
3. Protocol deviation or new SAP version for H2, because the reset-side comparison set changes after the 2026-10-29 analysis (SAP, sections 4.3 and 6; `protocol/change-control-v1.md`, section 5). (approval 3)
4. New reset-side mapping record `CS-00X.yaml`, DRAFT -> FROZEN, with its mapping row. (approval 4)
5. A new locked configuration record for the campaign version (a new file; the v1 record stays immutable). (approval 5)
6. Executor: new reset realizations for the seven conditions, a new implementation hash, and the embedded-digest list (`experiments/E03-resetability/executor/README.md`, section 9). Prompt copy if the prompt changes.
7. Workflow: a new revision of `.github/workflows/e03-measured-execution.yml` that reads the new configuration, names the new scenario in G-3, and accepts more than one START row (ci-cd-execution-model, section 3). A workflow change after FROZEN needs its own approval (section 1, item 11). (approval 6)
8. Controlled-instance verification for each new condition id on GitHub Actions (gate G-8 analogue), by new ENVIRONMENT_VERIFICATION dispatches (E03 ran this verification nine times in total; `experiments/E03-resetability/README.md`, "Controlled-instance verification"). (approvals 7 to 8 by dispatch)
9. Dispatch authorizations, one per SUT, naming the new conditions and N (five in E03). (approvals 9 to 13)
10. Executions: 7 conditions x N = 50 = 350 measured executions. Each dispatch is recorded before it runs (agent-governance-v5, section 3.6).
11. Import, with per-run change-log rows (section 2, raw-data row).

Approvals: about 13. Steps: 11 groups. Main risks: the reopening rule is new; the SAP deviation changes a confirmatory comparison after the reset-side analysis; the mapping freeze rule cannot be met as written; the workflow and executor change, so G-10 would lock a new hash. The data already collected stay valid only if the configuration history is kept (section 7, moment 1).

### Option B -- A new campaign for the second reset scenario, with H2 extended to it

Steps:

1. Human decision to add a campaign. (approval 1)
2. A protocol change to the campaign list. The campaign map is in `experiments/README.md`; whether the campaign set itself is protected by `protocol/study-design-v1.md` is not stated in the sections read (`protocol/change-control-v1.md`, section 8, names the dimensions and the ecosystems as protected). If it is, a new study-design version under section 5 is needed (approval 2). The text does not say whether a campaign may be added after data collection starts. HUMAN DECISION.
3. A SAP successor (or a recorded deviation), because H2 names E02 and E03 explicitly (SAP, 4.3) (approval 3).
4. The new campaign's full lifecycle: its own mapping record, its START package, a locked configuration, executor, workflow, controlled-instance verification, dispatch authorizations, and a freeze (`protocol/change-control-v1.md`, section 7, both moments) (approvals 4 to 12, as in E03).
5. The H2 pairs then compare E03 CS-001 with the new campaign's scenario, which is a different campaign id. The SAP pairs by canonical scenario id, so this would need a rule the SAP does not state.

Approvals: about 12 or more. Steps: 5 groups, each larger than Option A's. Main risks: the largest governance change; a new campaign id is not defined; the timing against the planned DATA FREEZE of 2027-01-05 (stated in the request; `manifests/planning-deadlines-v2.yaml`, not re-read) is tight, given the five-week precedent (section 1, item 12).

### Option C -- Keep E03 FROZEN; H2 keeps one reset scenario (descriptive)

Steps:

1. Human decision to keep H2's reset side at CS-001 and to report it as one scenario. (approval 1)
2. Record that H2's reset side remains n = 1 and descriptive (SAP, 4.3; the 2026-10-29 analysis). No protocol change.
3. Optionally study the second reset scenario as an EXPLORATORY question outside H2. `protocol/setup-effort-v2.md` (its "affected campaigns" paragraph) says E04 and E05 "sample Required Actions indirectly through E03's reset procedures"; whether those campaigns can host a reset scenario is not stated, and a new scenario there would need its own record and approval.

Approvals: 1 (plus any for option 3). Risk: H2 stays one reset scenario, so it cannot be tested beyond the single pair per SUT. The brief's aim is not met. No protocol gap is created.

## 4. Consequences for the frozen configuration and the raw data

- **Frozen configuration.** Under every option the v1 configuration of E03 stays as written (`experiments/E03-resetability/README.md`, "Campaign configuration", sha256 of the section recorded there). Options A and B add a new record; Option C changes nothing.
- **Raw data.** `raw-data/E03-resetability/` holds 350 immutable bundles (`experiments/E03-resetability/README.md`). Option A appends new bundles only with change-log rows; the protocol does not say whether they go in the same directory (section 2). Option B writes to a new directory. Option C writes nothing.
- **Pairing and results.** Results collected under CS-001 are analysed under the v1 configuration (`protocol/change-control-v1.md`, section 7, moment 1). A new scenario yields new results, not a re-analysis.

## 5. Consequences for the measured workflow's status gate

- G-1 requires the status IN_PROGRESS and exactly one START row. A FROZEN campaign fails G-1, which is the intended refusal (`experiments/E03-resetability/ci-cd-execution-model.md`, section 3, item 2). Option A needs G-1 to accept a reopening row; that requires a workflow change.
- G-2 locks the configuration by its record, and G-3 is written for CS-001 by name. Both change under Option A.
- Guard 1 (default branch and attempt 1) is independent of the campaign state and is reusable.
- A workflow change after the freeze has precedent under the CI grant (section 1, item 11). Whether a gate-logic change that admits new conditions qualifies is open. HUMAN DECISION.

## 6. Consequences for the H2 pairing

- **Current reset-side pairs.** With CS-001 only, the reset side has one scenario per pair: SUT-01 versus SUT-02 and SUT-01 versus SUT-03, WEB (SAP, 4.3; E03 README, "CONFIRMATORY comparisons"). The SAP pairs "per canonical scenario"; it does not state how an establish scenario is paired with a reset scenario. Propose: pair establish and reset separately, each by its own canonical_scenario_id. This needs a HUMAN DECISION, because the SAP does not state it.
- **Adequacy.** Derived here (not stated in the repository): with n non-tied pairs the smallest two-sided exact Wilcoxon p-value is 2 x 2^-n. Two scenarios give at least 0.5; six give at least 0.03125. The SAP applies Wilcoxon only where "the number of non-tied pairs is adequate", a term it does not define. Verify the arithmetic before relying on it.
- **Independence.** Two reset scenarios that use the same reset control on a SUT give correlated counts. Name it in the analysis: on SUT-03 the Sign-Out control serves both CS-001 (SUT03-EV-0030) and any identity reset; on SUT-01 the session reset serves CS-001 (SUT01-EV-0006) and any reset built on it; on SUT-02 "Reset App State" serves CS-001 (SUT02-EV-0002).

## 7. Draft reset-side intent (needed only for Option A)

Candidate `CS-00X (reset-side candidate, not allocated)` (DRAFT, not a record, not frozen). The intent is ecosystem-neutral and is chosen to differ from CS-001 on a named axis (target and actor state):

- precondition_class: AUTHENTICATED_SESSION, with the actor's business object holding one item (seeded by the actor's own route before the starting state; not counted).
- actor_state: AUTHENTICATED_STANDARD before the reset; ANONYMOUS after it.
- business_intent: an authenticated actor who holds a business object ends the session through the ecosystem's own control, and the ecosystem then holds neither the actor's identity nor the business object.
- target_state_or_transition: a protected route is refused or shows the unauthenticated view, and the business object is not presented.
- observable_oracle_class: UI_STATE.
- reset_requirement: SESSION_RESET.
- applicable_surfaces: WEB (for H2).

Evidence check against the repository (E01 rows, not a mapping):

| SUT | Reset control or route on the web surface | E01 row | Status |
|---|---|---|---|
| SUT-02 | Logout removes credentials, reachable from any authenticated screen | SUT02-EV-0002 | evidenced |
| SUT-03 | Sign-Out runs `store2.session.clearAll()` | SUT03-EV-0030, SUT03-EV-0031 | evidenced; the same control as CS-001 |
| SUT-01 | No logout row; the client token is written on login (SUT01-EV-0002). A text search of the SUT-01 evidence rows and of the SUT-01 audit tree on its branch (2026-11-05) found no logout or sign-out text | none | **evidence gap** |

Conclusion for the draft: no reset-side candidate is both independent of CS-001 and COMPARABLE on existing evidence for SUT-01, SUT-02, and SUT-03 on the web surface. This is the blocking finding for Option A, and it applies to any reset-side scenario built on the same controls. Closing it needs new E01-style evidence rows (for SUT-01, a logout or identity-reset row) or a scenario that uses other controls.

## 8. HUMAN DECISIONS (this note)

| ID | Decision | Options | Note |
|---|---|---|---|
| RS-1 | Whether H2 needs a second reset scenario before the DATA FREEZE | yes (A or B) / no (C) | A and B need protocol successors; C needs none |
| RS-2 | If A or B: the rule that reopens or extends E03 | a protocol successor that defines reopening / a new campaign id | the closing rule is in section 2 |
| RS-3 | Pairing of establish and reset scenarios in H2 | per canonical scenario id on each side / other | the SAP does not state it |
| RS-4 | Adequacy term for Wilcoxon (SAP, section 3) | keep descriptive / define a threshold in a SAP successor | derived minimum p-values in section 6 |
| RS-5 | Freeze after START of a new scenario for a reopened campaign | allow under the successor / disallow | section 2, mapping freeze row |
| RS-6 | Whether a gate-logic change that admits new conditions after FROZEN is a CI correction | yes, as a CI correction by approval / needs its own approval | precedent OP-CI-14 and OP-CI-15 (section 1, item 11) |
| RS-7 | Evidence for SUT-01 identity or logout (for any identity-reset scenario) | new evidence record / choose another scenario | section 7 |
| RS-8 | Whether "campaign version" is to be defined | define in the successor / avoid the term | section 1, item 7 |

## 9. Summary of the three options

| | A. Reopen E03 (second version) | B. New campaign | C. Keep E03 closed |
|---|---|---|---|
| Protocol change | yes (new change-control version; SAP deviation or successor) | yes (campaign list, SAP, change-control) | none |
| Approvals (approximate) | about 13 | about 12 or more, plus the campaign lifecycle | 1 |
| Steps (groups) | 11 | 5 larger groups | 1 to 3 |
| Measured executions | 350 (7 conditions x 50) | as E03 for its scenarios | 0 |
| Main risk | undefined reopening rule; a SAP deviation after the reset-side analysis | largest governance change; timing against the DATA FREEZE | H2 stays one reset scenario |
| Blocking gap | SUT-01 reset-side evidence (section 7) | same | none for H2; the aim is not met |
