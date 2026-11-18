# E04-repeatability: design notes of the minimal version (DRAFT, operation OP-PREP-E04)

| Field | Value |
|---|---|
| State | DRAFT, preparation only. Not a campaign configuration, not locked, not hashed, not an authorization. The campaign stays NOT_STARTED (manifests/study-manifest.yaml). Nothing here starts E04, dispatches anything, or freezes a file. |
| Decision it implements | D-20, option (b): "E04 mínimo después de E05" (manifests/campaign-execution-decisions-v4.yaml, decision D-20-E04-DISPOSITION). E04 is establishment-only, runs after E05, and stays outside the H3 critical path. |
| Source of the design | The E05 determinism campaign, frozen on 2026-11-16 (local date; 2026-11-17 UTC; manifests/e05-campaign-freeze-v1.yaml; experiments/E05-determinism/README.md, "Campaign configuration"). E04 derives its executor from the E05 executor by copying and removing the stimulus and classification blocks (experiments/E04-repeatability/executor/IMPLEMENTATION-NOTES.md). |
| Protocol | protocol/repeatability-determinism-v1.md, sections 4 (TSRR) and 5 (execution rules, applied unchanged). Attribution: issue (xix), decision D-16 option B, adapted (section 2.3 below). |
| Companion files | conditions-draft.json (the 13 conditions), executor/ (the draft executor), ../../prompts/working/ORCHESTRATOR-E04-repeatability-v1.md (the working dispatch procedure, NOT DISPATCHABLE), ../../.github/workflows/e04-environment-verification.yml and e04-measured-execution.yml (dispatch-only, fail-closed). |

## 1. Shape of E04 minimal

- **What an execution is.** Reset, starting-state check, establishment, target-state verification, record. No stimulus is sent and no outcome is classified. The target state is the one that E05 establishes for the same condition (scenario CS-001, experiments/scenario-mappings/CS-001.yaml, FROZEN).
- **Primary metric.** TSRR = successful target-state establishments / all valid measured attempts (protocol/repeatability-determinism-v1.md, section 4). Every attempt counts in the denominator: an attempt whose starting-state check fails, whose establishment fails, or which is interrupted, is counted. No attempt leaves a denominator. CEOR, E2E-ROR and Outcome Entropy are E05 metrics and are not computed for E04.
- **Conditions.** Thirteen, mirroring the thirteen configured E05 conditions one to one (identifiers E04-SUT0N-(API|WEB)-NN; the mirror of each is recorded in the condition's `mirrors` field, checked against the E05 conditions file by a test).
- **Size.** N = 50 per condition, 650 executions in all (the same plan as E05), one job per condition, attempt 1 only. Dispatch, START, and authorization follow the same governance as E05 and need their own approvals (section 5).
- **Target-state equivalence with E05.** Same SUT, same surface, same account, same reset kind, same starting-state check, same establishment, same verification (the realization code of E05 with the stimulus and classification blocks removed; the AST comparison of the reused methods is in IMPLEMENTATION-NOTES.md, point 6).

## 2. The five working defaults (PENDING the human research lead's confirmation at the START package)

Each default below is a working choice of this draft. None is decided, and none is a human decision. Each becomes a campaign configuration field only if the human research lead confirms it at the E04 START package.

### 2.1 Conditions: the mirror of E05 (pending)

The thirteen E04 conditions use the E05 realizations of the same condition with the stimulus removed. Three groups of conditions run identical blocks, derived from the executor code by comparing, for each condition, the four block methods as resolved through inheritance, the mechanisms and components of the realization, and the reset kind (conditions-draft.json, fields block_group and identical_blocks_with): {E04-SUT01-API-01, E04-SUT01-API-06} (restart of the backend process; the accounts standard_user and error_user differ); {E04-SUT01-API-02, E04-SUT01-API-03, E04-SUT01-API-04, E04-SUT01-API-05} (session clear through the API; the accounts standard_user, standard_user, performance_glitch_user and a11y_glitch_user differ); {E04-SUT05-API-01, E04-SUT05-API-02} (restart of the SUT process; the same documented account). The SUT-01 API conditions share one inherited code path; the reset kind selects the restart or the session-clear branch, so each group is a set of conditions with the same reset kind. No other pair of conditions runs identical blocks: E04-SUT04-API-01 and -02 share the code of the reset, starting-state check and establishment (their reset labels differ) but differ in the verification block (the message-count read); E04-SUT01-WEB-01, E04-SUT02-WEB-01, E04-SUT04-API-01, E04-SUT04-API-02 and E04-SUT04-WEB-01 are alone in their block sets. All thirteen conditions are kept as separate conditions, as the one-to-one mirror requires. E05-SUT02-WEB-02 has no mirror, because it was retired before the E05 START.

### 2.2 Outcome categories (pending)

| Category | Phase | Status in the manifest | Meaning |
|---|---|---|---|
| TARGET_STATE_VERIFIED | verified | SUCCESS | Every block of the execution held; the target state was verified. The only success category; the expected category of every condition. |
| RESET_FAILED | reset | ABORTED | The reset did not hold, or could not run (E05 category, unchanged). |
| RESET_STARTING_STATE_NOT_REACHED | reset | ABORTED | The declared starting state was not reached after the reset, with its cause recorded (E05 category, unchanged). |
| ESTABLISHMENT_FAILED | establishment | ABORTED | The establishment did not hold (E05 category, unchanged). |
| ESTABLISHMENT_VERIFICATION_FAILED | establishment (verification block) | ABORTED | The target-state verification did not hold (E05 category, unchanged). |
| ESTABLISHMENT_INTERRUPTED | establishment or verification | ABORTED | A harness or client exception in the block; the interruption category of E04 (there is no stimulus block, so no INTERRUPTED_ category exists). |
| STUB_NO_BUNDLE | stub | ERROR | An execution began and left no bundle (E05 decision D-09). |

The prefix of the success category is TARGET_STATE_, which no failure category carries, so that the status SUCCESS can only come from it (a test checks this). E05's S_ and INTERRUPTED_ categories and its catch-all mapping are not part of E04. A reset interruption is recorded as RESET_FAILED with TOOLING attribution, as in E05.

### 2.3 Attribution (issue (xix), decision D-16 option B, adapted) (pending)

- An attempt is labeled **TOOLING** when a block is interrupted by the harness or the client: a runner or client exception, a browser or client crash or disconnect, or the per-execution watchdog. This is the E05 labeling of the reused blocks: E05's stimulus-request boundary was never crossed inside them, so their interruptions were TOOLING. E04 keeps that labeling.
- A runner cancelled or lost by the workflow is a TOOLING case of D-16, but the executor does not record it (open item 7 of the implementation notes).
- Every other attempt is labeled **SUT**: a recorded failure of a block (a non-2xx answer, a missing confirmation, a starting state that did not hold) and every attempt whose cause cannot be assigned mechanically.
- Attribution is fixed by these mechanical rules and never by the pattern of results. No attempt leaves any denominator. Attributed counts are reported beside the raw TSRR, which is never recomputed on them.
- **Not implemented; open for the START package.** The response clause of the design default (an exception after a response of the SUT is SUT) is not implemented. Every realization receives a response before its first block that can raise (the login or the page load), so that clause would make TOOLING almost unreachable and would change the labeling of E05's reused blocks. The decision is open (section 4, item 1; IMPLEMENTATION-NOTES.md, point 3).

### 2.4 Attempts, starting-state aborts and the further-attempt gate (pending)

- Attempt 1 only under the dispatch authorization. An attempt whose starting-state check fails is ABORTED with its cause, recorded with its own execution index, and counted in TSRR's denominator, as in E05 (decisions D-02 and D-09 of E05).
- A further attempt (attempt 2 or more, from a first execution named by the approval) is admitted only under a recorded further-attempt approval of the human research lead that names the condition, the first execution and the attempt: gate G-E04-A2 of the measured workflow, the E05 gate G-E05-A2 renamed. Nothing is re-run; a GitHub-native re-run is refused.

### 2.5 No comparison, no analysis script (pending)

No between-ecosystem comparison is computed or prepared. TSRR is reported per condition and per ecosystem with its own N, as TSRR is defined per condition in protocol/repeatability-determinism-v1.md. Any between-ecosystem comparison of TSRR needs canonical scenarios with FROZEN mapping records (protocol/equivalent-scenario-mapping-v1.md) and is EXPLORATORY unless pre-registered otherwise (protocol/statistical-analysis-plan-v1.md, section 4). No analysis script is part of this draft; the TSRR analysis is a later, separate operation with its own instruction.

## 3. Overlaps with other campaigns (noted, not decided)

- **E02-state-establishment (FROZEN 2026-11-12).** E02 measures the establishment of state for ten web and api conditions, N = 50 each (its configuration is in experiments/E02-state-establishment/README.md). E04 would repeat the establishment of the CS-001 target state for the thirteen E05 conditions. The two campaigns share the operation (reset, establishment) on the same SUTs; the establishment data of E02 and of E04 are not combined, and whether E04 adds information beyond E02 is not decided here.
- **The establishment phase of E05 (FROZEN 2026-11-16 local date, 2026-11-17 UTC).** Each E05 execution already contains the same reset, starting-state check, establishment and verification of its condition, 50 times per condition, on the same instance model. E04 therefore repeats, without stimulus, a phase that E05 measures inside its executions. This is the reason the D-20 disposition chose E04 as a minimal, later campaign, and it is recorded here as an overlap. Whether E04 is run at all, after E05's TSRR and CEOR are known, is the human research lead's decision; this draft does not make it.
- **The statistical plan.** protocol/statistical-analysis-plan-v1.md, section 4.3 lists E04 and E05 for H3 although H3's criteria are E05 quantities; this wording gap (D-20) stays flagged and is not amended here.

## 4. Open items for the START package

1. Confirm or change each working default of section 2 (conditions, categories, attribution, the attempt gate, no comparison). The response clause of the attribution default is not implemented (section 2.3).
2. The identical-block groups of section 2.1 ({E04-SUT01-API-01, -06}; {E04-SUT01-API-02, -03, -04, -05}; {E04-SUT05-API-01, -02}): keep the conditions as separate conditions, or merge them within a group. A merge would change the number of conditions and the executions, so it is a configuration decision.
3. The SUT-04 message-count baseline (E04-SUT04-API-02): the baseline read is kept as part of the verification block because E05's verification block contains it. Confirm it, or remove it as a stimulus-only support. Removal would change the target-state verification of that condition.
4. The guest names of the SUT-04 conditions are derived from the E04 condition identifiers (the salt of the derivation is E04, not E05); the reset also still matches the stimulus names of the E05 counterparts (kept so that the reset is unchanged). Both are identity details to confirm.
5. The measured-job timeout of 60 minutes is inherited from E05 (decision v9 of E05, from the E05 DRY_RUN rounds). It must be re-derived from E04 DRY_RUN durations before the START; it is TBD, and it is not raised.
6. The controlled-instance status of each E04 condition does not exist yet. The measured workflow reads manifests of the form experiments/E04-repeatability/controlled-instance-status.yaml; the file is created only by the verification rounds and the human research lead's decision, and a missing file fails the gate closed.
7. The primary metric names in the locked configuration (TSRR, as the measured gate now requires) and the E05-only metrics that E04 does not compute (CEOR, E2E-ROR, Outcome Entropy, H3).
8. Whether a workflow-recorded infrastructure interruption is recorded as a TOOLING input of the measured workflow, and how (section 2.3).
9. The working prompt ORCHESTRATOR-E04-repeatability-v1 becomes a frozen copy only at the START (prompts/README.md).
10. The E04 implementation hash: the executor is a draft; the hash locked at START is the hash of the final executor (run-condition.sh), which is computed after the last edit.

## 5. Approvals still needed (none given)

Each of the following needs its own explicit approval from the human research lead; none is given by this draft:

- the E04 campaign START and its authorization id (protocol/change-control-v1.md, section 7, moment 1), with the locked "Campaign configuration" in experiments/E04-repeatability/README.md (that README is not edited by this draft);
- the verification rounds (DRY_RUN) on GitHub Actions, each dispatch of the verification workflow (dry_run must be true; DRY_RUN bundles are never imported);
- the controlled-instance verification record of each condition, from those rounds;
- the export of this draft to the public repository (a human decision; the ORCHESTRATOR pushes only after the human research lead's yes to the exact line);
- one dispatch authorization per SUT (protocol/agent-governance-v6.md, section 3.7; manifests/e04-dispatch-authorization-sut0N-v1.yaml, none exists);
- the campaign freeze (protocol/change-control-v1.md, section 7, moment 2);
- the TSRR analysis of the measured data, under a separate instruction (protocol/statistical-analysis-plan-v1.md, section 4).

## 6. What this draft does not do

It does not start E04, does not run or dispatch any workflow, does not write any manifest or authorization, does not export, does not change E05, and does not edit any file of the existing E04 README, the protocol, the manifests, or the schemas. The E04 README already in the repository states NOT STARTED, and that status is unchanged.

## 7. Decisions of 2026-11-17 (answers of the human research lead to a question dialog)

- The verification workflow `.github/workflows/e04-environment-verification.yml` stays as in E05: it has no START gate, so a DRY_RUN can run before the START; it is dispatched only with the human research lead's yes to each exact line, and its bundles are never imported (chosen option: leave it as E05).
- The attribution of an interruption of a block as TOOLING (section 2.3 and IMPLEMENTATION-NOTES.md, point 3) is confirmed as a working value; it stays an open item of the START package, where the rule is locked (chosen option: confirm TOOLING).
- The update of the agent-instructions file with the state of export v65, the refresh D23 of the status page and this DRAFT was approved. The other working defaults of section 2 stay pending until the START package.
- Nothing else is decided: no START, no dispatch authorization, no export of this draft and no DRY_RUN has been approved.
