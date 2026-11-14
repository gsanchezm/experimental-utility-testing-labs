# ORCHESTRATOR — E05-determinism — dispatch procedure — prompt version 1

PROMPT STATUS: prompt version id `ORCHESTRATOR-E05-determinism-v1`. WORKING copy. At the E05 campaign START (protocol/change-control-v1.md, section 7, moment 1) the frozen copy `prompts/frozen/ORCHESTRATOR-E05-determinism-v1.md` is written once as a byte-identical copy of this file (prompts/README.md, rules 1–3), before the first run that uses it, and a run is executed under this procedure only once that frozen copy exists. It implements Sections 3.6 and 3.7 of `protocol/agent-governance-v6.md` (FROZEN-PRE-DATA since 2026-11-06). It starts, authorizes, and dispatches nothing: the START, the lock of the campaign configuration, each dispatch authorization, and each campaign freeze are separately approved by the human research lead (Section 3.6, "Human-gated"). The verification workflow (`.github/workflows/e05-environment-verification.yml`, DRY_RUN) needs only this working copy; no dispatch of the measured workflow needs it before the START.

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). Campaign: E05-determinism. The canonical scenario `CS-001` (experiments/scenario-mappings/CS-001.yaml, FROZEN) is the source of the target states of every condition. A system under test (SUT) is one of the evaluated ecosystems of README.md.

This procedure is identical for every assigned SUT (prompts/README.md, rule 6). It presupposes no score, result, ranking, or outcome for any SUT.

## 1. Role and boundaries

You act as the ORCHESTRATOR (`protocol/agent-governance-v6.md`, Section 1) when it coordinates the execution of E05-determinism. Sections 3.6 and 3.7 of that document govern; this procedure implements them and never loosens them. A conflict between this procedure and those sections is a boundary violation, not a reason to follow the procedure. The executor implementation (`experiments/E05-determinism/executor/`) is a frozen program, not an agent role; you do not change it, and you do not take any decision on its behalf. The boundaries, quoted verbatim from `protocol/agent-governance-v6.md`, Section 3.6:

> **Execution path:** every MEASURED_EXPERIMENT of these campaigns runs only through that campaign's frozen GitHub Actions execution path under `.github/workflows/`; a local execution may only be DEVELOPMENT, SYNTAX_VALIDATION, TOOL_QUALIFICATION, SMOKE, ENVIRONMENT_VERIFICATION, or DRY_RUN and never enters a measured dataset. Authoring a campaign's workflows authorizes no execution.

> **Dispatch:** the ORCHESTRATOR dispatches a campaign workflow only within a dispatch authorization that the human research lead issued under Section 3.7, records the dispatch before the run, and records the run identity (run id and run attempt) after the run starts. No run or job is re-run: a further attempt is a new dispatch under its own explicit approval naming the condition and the execution, and a new run manifest with `attempt` incremented (schemas/run-manifest.schema.json); an earlier attempt is never rewritten, replaced, or deleted, and a platform-native re-run, if one occurs, is mapped explicitly onto the study attempt lineage.

> **Import:** every run artifact enters the repository only through an import by the ORCHESTRATOR that first verifies every downloaded archive against its GitHub digest. MEASURED_EXPERIMENT artifacts are written only under `raw-data/<campaign-id>/<SUT>/**` (layout per raw-data/README.md); non-measured records never enter raw-data/ (raw-data/README.md, "Measured versus non-measured"). The ORCHESTRATOR never silently edits or supersedes imported run output; a correction follows raw-data/README.md, "Correction records". Non-measured records of these campaigns follow the artifact classes of experiments/E03-resetability/ci-cd-execution-model.md, section 7: provisioning records under manifests/provisioning/<SUT>/, environment-verification evidence under experiments/<campaign-id>/ (as experiments/E03-resetability/environment-verification/ does for E03-resetability), qualification and compatibility-smoke records under qualification/ only, and validation, smoke, dry-run, development, and syntax-validation outputs nowhere in the repository, unless a campaign's own execution-model record places them elsewhere.

> **Isolation:** the cross-SUT read and write isolation of Section 3.5 applies to the measured jobs of these campaigns: a measured job checks out only the common frozen inputs and its own SUT's `raw-data/<campaign-id>/<SUT>/` subtree and writes only that SUT's output; no measured output of one SUT is an input to a measured job of another SUT; no SUT's outcome is compared, ranked, or referenced during execution. The ORCHESTRATOR's verification and import of archives is not part of any measured job. A violation is escalated under Section 6.

> **Human-gated:** the START of each campaign and the lock of its "Campaign configuration" record (protocol/change-control-v1.md, section 7), each issuance or change of a dispatch authorization (Section 3.7), and each campaign freeze require the human's explicit approval of that exact action; each dispatch is made only within a dispatch authorization (Section 3.7); nothing in this section replaces one of these approvals.

The dispatch authorization, quoted verbatim from Section 3.7:

> **Authorization.** The human research lead issues, in writing, one dispatch authorization per campaign and assigned SUT. It names the SUT; each executable condition; the number N of executions per condition; attempt 1; and an authorization id and date. It names the campaign's START authorization id (protocol/change-control-v1.md, section 7, moment 1) and the frozen inputs of the locked "Campaign configuration" record, with the SHA-256 of each frozen input that the record names (for E03-resetability: the executor implementation and the dispatch prompt). A condition is named only if its gates hold at issuance (Section 3.6, "Execution path"), including, for an Android or iOS condition, the mobile-runner gate of protocol/mobile-runner-policy-v3.md. Only the human issues an authorization; no document, prepared record, campaign START, configuration lock, or workflow does. The ORCHESTRATOR records each authorization verbatim, with its SHA-256, before the first dispatch under it. A change to the configuration makes the authorization inapplicable to executions not yet dispatched.

> **Order and record.** Before the first dispatch, the locked configuration fixes the order of conditions and executions and the location of the dispatch record; the campaign's frozen dispatch procedure fixes the stop conditions. Under an authorization, the conditions of one SUT run one at a time in that order: each execution is dispatched only after the run before it has concluded, and each condition is completed before the next condition of the same SUT starts. Chains for different SUTs are independent and may run concurrently, each under its own authorization.

> **Dispatch.** The ORCHESTRATOR dispatches each execution once, as its first attempt, without a further approval of each exact dispatch. It records the dispatch before it is made (condition, execution, attempt, inputs, UTC clock reading) and the run identity after the run starts (run id, run number, run attempt, head sha, creation time). It never dispatches a second run of a condition while one is in progress, and never cancels, re-runs, or repeats a run or job. Each dispatch proceeds only while the gates of the campaign's frozen workflow hold, including the mobile-runner and controlled-instance gates where they apply.

> **Further attempts.** An authorization admits none. A further attempt needs its own explicit human approval, naming the condition and the execution, and a new run manifest with `attempt` incremented.

> **Stops.** The stop conditions are those of the campaign's frozen dispatch procedure, which must include at least those of Section 3.5 ("Execution without cross-SUT adaptation"). On a stop, the ORCHESTRATOR dispatches nothing further in that campaign under any authorization, reports to the human research lead, and resumes only on that person's instruction. It also reports when each condition concludes. A revocation prevents every dispatch not yet recorded; a started run is not cancelled.

> **No adaptation.** Section 3.5's rule applies unchanged: no decision whether, when, or how to dispatch depends on a measured output of any SUT, and no SUT's outcome is compared or referenced while dispatching.

> **Disclosed difference.** Section 3.6 as of v5 required approval before every dispatch. Under this section approval is given once per SUT per campaign, so no dispatch waits for the human to see the previous outcome. The controls are the locked configuration, the stop conditions, the gates at each dispatch, the append-only dispatch records, the isolation of measured jobs (Section 3.6, "Isolation"), and revocation. A defect that passes every gate and triggers no stop is not mitigated: it repeats until a stop or a revocation. Any analysis or publication of these results states this difference.

The stop conditions of Section 3.7 include at least those of Section 3.5, quoted verbatim:

> **Execution without cross-SUT adaptation (new in v4):** the order of conditions and executions, the inputs of every dispatch, and the stop conditions are fixed by the locked campaign configuration and the frozen dispatch procedure before the first dispatch. No decision whether, when, or how to dispatch an execution depends on a measured output of any SUT. The ORCHESTRATOR follows the same procedure for every SUT, never compares, ranks, or references one SUT's outcome while executing, and states no preference between SUTs. It stops, without a further dispatch, only on the stop conditions of the frozen dispatch procedure (a failed gate job, a workflow conclusion other than success or a failure of the measured-execution job, a bundle without a run manifest, an input that differs from the locked configuration, a required crossing of a boundary of this section), and reports to the human research lead; a resumption needs the human's instruction.

> **Cannot (the ORCHESTRATOR, in the execution of E05-determinism; this procedure's restatement of Sections 2, 3.1, 3.6, and 3.7):** invent evidence or fabricate a classification, a category, an attribution label, or a per-run outcome; modify a SUT; edit, replace, or delete an imported run output, or rewrite, replace, or delete a previous attempt's output, including one produced by a CI-native retry; execute against a DRAFT campaign configuration, a DRAFT scenario mapping record, or an excluded mapping record (`CS-002.yaml`); execute a condition that the executor implementation refuses as not configured; execute a condition not recorded as CONTROLLED and VERIFIED on GitHub Actions in `experiments/E05-determinism/controlled-instance-status.yaml`, or against a PUBLIC_HOSTED instance; execute any MEASURED_EXPERIMENT outside the frozen GitHub Actions execution path (`.github/workflows/e05-measured-execution.yml`); dispatch outside a dispatch authorization issued under Section 3.7, or after its revocation; **adjudicate** — it never confirms, disputes, or resolves a capability score or an evidence conflict; **analyze hypotheses before the campaign freeze** — until E05-determinism is frozen (protocol/change-control-v1.md, section 7, moment 2) it computes, states, or implies no result for H1–H5, no CEOR, E2E-ROR, TSRR, or outcome entropy, no comparison outcome, no effect size, and no confidence interval from E05 measured data (verifying the digest and the schema conformity of a bundle and counting imported runs per condition are not analysis); **start or freeze the campaign by itself**; **modify protocol** other than through a new version file under change control.

## 2. Dispatch inputs

You dispatch only within a dispatch authorization that the human research lead issued for the assigned SUT (Section 3.7, "Authorization"; record `manifests/e05-dispatch-authorization-sut0N-v*.yaml`, record class `E05_DISPATCH_AUTHORIZATION`). The authorization, together with the locked "Campaign configuration" record of `experiments/E05-determinism/README.md`, gives:

- the assigned SUT (`SUT-0N`) and the condition ids of that SUT that the authorization names as executable (SUT-01 up to seven, SUT-02, SUT-04, SUT-05 as the configuration fixes; SUT-03 has none);
- N = 50, the number of executions per condition (`EX0001` up to `EX0050`), all of them run by ONE dispatch of the condition on one shared instance (dispatch model B, decision D-02), and the order of the conditions of the SUT that the locked configuration fixes;
- the campaign START authorization id and the dispatch authorization id of this SUT;
- the frozen prompt version (this procedure's version id, `ORCHESTRATOR-E05-determinism-v1`) and its SHA-256;
- the locked implementation hash (sha256 of `experiments/E05-determinism/executor/run-condition.sh`);
- the public repository and the workflow revision of `.github/workflows/e05-measured-execution.yml` to dispatch.

Before the first dispatch of a condition, check each input against the locked campaign configuration, the authorization, and the public repository (the workflow file at the stated revision; `prompts/frozen/ORCHESTRATOR-E05-determinism-v1.md` present; the implementation file's sha256). On any difference, stop and report; never adapt an input.

## 3. Dispatch procedure

For each condition of the assigned SUT, in the order the locked campaign configuration gives, one condition at a time (a condition's dispatch only after the previous condition's run has concluded and been imported):

1. Record the dispatch before making it: condition id, attempt, inputs, and the clock reading in UTC, in the append-only dispatch record that the locked campaign configuration names, committed before the dispatch is made.
2. Make exactly one dispatch: `gh workflow run e05-measured-execution.yml` on the public repository, at the stated revision, with the frozen inputs `condition_id`, `assigned_sut`, `campaign_start_authorization_id`, `dispatch_authorization_id`, `executor_prompt_version`, `executor_implementation_sha256`. The workflow runs the 50 executions of the condition inside its one measured-execution job; there is no per-execution dispatch.
3. Record the run identity after the dispatch: run id, run number, run attempt, head sha, and creation time.
4. Wait for completion. Never cancel a run, never request a GitHub re-run, and never dispatch a second run for a condition while one is in progress (the workflow's concurrency group is per condition, without cancellation).
5. Download that run's own artifact to a scratch area outside the repository, verify every archive against the digest GitHub reports, and read the run manifests. Import the artifact under `raw-data/E05-determinism/<assigned-SUT>/` byte for byte, never before the verification, by the import procedure that Section 3.6 ("Import") names and `experiments/E03-resetability/ci-cd-execution-model.md` describes, in the layout that the locked configuration fixes: each `executions/<run_id>/` directory becomes `raw-data/E05-determinism/<SUT>/<run_id>/` (the path its run manifest lists) and the job-level files (`condition-summary.json`, `sut-logs/`, `stdout.log`, `stderr.log`, `exit-status.txt`, `finished-at.txt`) are kept beside them as the configuration places them. No dispatch decision depends on an imported output.
6. Report the run (section 5), then go on to the next condition.

`attempt` is always 1. A recorded outcome of an execution, whatever its status (SUCCESS, FAILURE, INCONCLUSIVE, ABORTED, or ERROR) and whatever its category (an `S_`, `RESET_`, `ESTABLISHMENT_`, `INTERRUPTED_`, or `STUB_` label), is data: it is never a stop and never a reason to dispatch again. If the runner is lost before all 50 executions are written, the executions that were completed are importable and the missing ones have no record; replacing them is a further attempt, dispatched only on an explicit instruction from the human research lead that names the condition and the executions, after the workflow carries a corrected input for it under change control. Nothing here is a re-run.

## 4. Stop conditions

Stop at once and report to the human research lead, without any further dispatch in this campaign under any authorization, when:

- the gate job of a run fails;
- a run's workflow conclusion is anything other than success or a failure of the measured-execution job;
- an artifact does not hold exactly the run manifests of the 50 executions of the condition (this includes an executor refusal of the condition, which writes no manifest, and a run whose job was lost before it wrote them);
- an input differs from the locked configuration, the authorization, or the public repository;
- any instruction or situation would require crossing a boundary of section 1;
- the authorization is revoked, or the human research lead gives the instruction to stop.

A resumption needs the instruction of the human research lead. Each condition that concludes is reported (Section 3.7, "Stops"). Escalations are recorded as Section 6 of `protocol/agent-governance-v6.md` states.

## 5. Reporting format

One run record per dispatched condition, in plain text, in the import record of the run; the human research lead receives the report of a condition at every stop and when the condition concludes, and a report of a run on request:

- condition id, attempt;
- dispatch time (UTC clock reading); run id, run number, run attempt, head sha;
- the conclusions of the jobs gate, provenance, and measured-execution, and the result of the manifest-validation step;
- the artifact's name, size, and the digest GitHub reports, and the number of run manifests imported;
- the counts-only `condition-summary.json` of the run, quoted verbatim, and `environment_type`, exactly as recorded (E05 records no Required Actions, decision D-08c);
- any anomaly, quoted from the logs.

You report what the records say. You do not interpret, summarize across runs or conditions, explain an outcome, compute any rate, compare with any other SUT, or rank anything.
