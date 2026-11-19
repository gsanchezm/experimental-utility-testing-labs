# E07 — Cross-layer Continuity

## Objective

Determine whether a state established through one layer of an evaluated ecosystem (each a system under test, SUT) is verifiable through another layer. The candidate layer pairs are API->Web, API->Android, API->iOS, and Web->API. The campaign records whether the same entity or state is observable across layers, how many actions the verification requires, and, secondarily, the latency between establishment and verifiability. Entities and states used for inferential comparison are canonical scenarios with FROZEN mapping records (protocol/equivalent-scenario-mapping-v1.md; observable_oracle_class OTHER, with free text naming the cross-layer consistency check, per the frozen controlled vocabulary of protocol/equivalent-scenario-mapping-v1.md, section 3); an ecosystem without a defensible semantic equivalent is NOT_COMPARABLE for that scenario. State-changing establishment steps run on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance when the state would be visible to other users of a shared instance or would persist beyond the experimenter's own session (protocol/study-design-v1.md, section 10.3). Mobile layers are exercised only for ecosystems that passed the per-SUT compatibility smoke (protocol/mobile-runner-policy-v3.md, section 9).

## Related research question(s)

- RQ4 Cross-platform and Cross-layer Integration (primary).
- Informs dimension 4 Cross-platform and Cross-layer Integration; relates to the cross-cutting property Cross-layer State Continuity in protocol/cross-cutting-properties-v1.md.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Source layer (the layer through which the state is established) — candidate.
- Verification layer (the layer through which the state is observed) — candidate.
- Entity / state type (canonical_scenario_id with a FROZEN mapping record, protocol/equivalent-scenario-mapping-v1.md) — candidate.

## Future dependent variables (candidate — not frozen)

- Continuity success (categorical: verified / not verified / not applicable / not testable) — candidate.
- Required actions to perform the cross-layer verification — candidate.
- Latency from establishment to verifiability (secondary) — candidate.

## Required evidence

- One run manifest per source layer × verification layer × entity execution conforming to schemas/run-manifest.schema.json, including ecosystem id, both layers (`source_layer` and `verification_layer`), entity/state type (`scenario` = canonical_scenario_id), `environment_type`, and outcome.
- Entity identifiers created or referenced during establishment, recorded so that the verification can be traced to the same entity.
- Request and response records for API-side steps.
- Verification artifacts from the verification layer (for example screenshot, response record, or state dump; form TBD before freeze).
- Explicit record for every layer pair that is absent, not applicable, or not testable, with reason.
- Mobile executions comply with protocol/mobile-runner-policy-v3.md.
- Raw observations in `raw-data/E07-cross-layer-continuity/`.

## Current status

IN PROGRESS since the campaign START of 2026-11-19 (human authorization E07-START-AUTH-01; protocol/change-control-v1.md, section 7, moment 1; record manifests/e07-campaign-start-v1.yaml). The "Campaign configuration" section below is locked and immutable. The START authorized no dispatch and no dispatch authorization; each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) is issued separately by the human research lead.

Resumed by the human research lead's decision of 2026-11-02 (manifests/campaign-resumption-v1.yaml); the deferral of scope A (manifests/campaign-disposition-v1.yaml) no longer governs the schedule. The canonical scenario records CS-005 (API to WEB) and CS-006 (WEB to API) were FROZEN on 2026-11-19 (manifests/cs-005-freeze-v1.yaml, manifests/cs-006-freeze-v1.yaml). All four conditions are VERIFIED on GitHub Actions by the non-measured DRY_RUN rounds 2 and 3 (manifests/e07-environment-verification-rounds-v1.yaml; experiments/E07-cross-layer-continuity/controlled-instance-status.yaml).

## Scope note (2026-11-18)

Preparation covers the web and API layers only (the human research lead's decision of 2026-11-05, restated by decision D-E07-7 of 2026-11-18, manifests/campaign-execution-decisions-v11.yaml): the pairs API->Web and Web->API are drafted as the canonical scenario records experiments/scenario-mappings/CS-005.yaml and CS-006.yaml (FROZEN on 2026-11-19). The mobile pairs listed in the Objective (API->Android and API->iOS) are outside this preparation; a mobile record would need the compatibility smoke of its exact SUT x platform x runner and an admissible runner under protocol/mobile-runner-policy-v3.md. The design brief (design-brief-draft.md, sections 17 and 18) and the configuration draft (campaign-configuration-draft.md) hold the decisions taken and those still open. This note changes no definition above and authorizes nothing: the status stays NOT STARTED.

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.

## Campaign configuration

This record is the "Campaign configuration" of E07-cross-layer-continuity. It is locked at the campaign START (protocol/change-control-v1.md, section 7, moment 1) under the human authorization named below, and it is immutable from then on; a change after the START is a change-control row recorded before the affected execution. It authorizes no dispatch: each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) is issued separately by the human research lead. The design records are experiments/E07-cross-layer-continuity/design-brief-draft.md (sections 17 and 18) and campaign-configuration-draft.md; the executor is experiments/E07-cross-layer-continuity/executor/. The values of this text are those decided on 2026-11-18 and 2026-11-19 (manifests/campaign-execution-decisions-v10.yaml to -v14.yaml); every hash below was computed from the recorded file at the START and not typed. A system under test (SUT) is one of the evaluated ecosystems of README.md.

### Identity and START

- Campaign: E07-cross-layer-continuity. Scope: web and API layers only (decisions of 2026-11-05 and D-E07-7). Design: cross-layer continuity in two directions, API to WEB (canonical scenario CS-005) and WEB to API (canonical scenario CS-006): an actor establishes one unit of business state through the source layer and a read-only observation on the other layer is compared with the establishment record. The primary variable is the continuity success proportion (see "Blocks, outcome categories and the continuity proportion"). Hypothesis label: H4, continuity part, but no CONFIRMATORY comparison is evaluable under DP-4 strict (D-E07-1; see "Analysis and what is not computed"); every result is descriptive. The continuity success proportion is the variable that protocol/statistical-analysis-plan-v1.md, section 4.3 (H4 row), names for E07.
- START authorization id: E07-START-AUTH-01 (the id of the human research lead's approval of this START). The START row of protocol/CHANGELOG.md names it.
- Protocol: v1 FROZEN-PRE-DATA (protocol/study-design-v1.md, section 6; protocol/statistical-analysis-plan-v1.md, sections 4 and 5; protocol/equivalent-scenario-mapping-v1.md; protocol/repeatability-determinism-v1.md, section 5, applied for the rules of valid measured attempts). Agent governance: protocol/agent-governance-v6.md, sha256 c890a9d004b2989aa9ae33a54bc68b000c47fc9e3f79d60ad0051de78b3f2a4a, FROZEN-PRE-DATA since 2026-11-06, Sections 3.6 and 3.7.
- Execution: GitHub Actions only (CAMPAIGN-CI-WRITE-AUTH-01), through .github/workflows/e07-measured-execution.yml, dispatched by the ORCHESTRATOR under dispatch authorizations. Attempt 1 only under the authorization; a further attempt only under a recorded further-attempt approval (gate G-E07-A2); default branch only; no GitHub re-run.
- Measured workflow file sha256 b4888425c06dd735eab87250a3dbbf9ba7bb4ef709c1fbdc7384a6ba932ded89 (gate G-9 reads this hash from this record). Verification workflow file sha256 3bfba625eaef22083543cb2cd09cd45cf5bd84763c64d29266b35e10b33a6206 (provenance only; the verification workflow has no START gate, as in E04 and E05).

### Scenario mapping

- Canonical scenario CS-005 (API to WEB): experiments/scenario-mappings/CS-005.yaml, sha256 3721efba476137a3b3893fae2a123c4bd72cb7c09d7ab0966d4aea869bda5069, mapping_status FROZEN on 2026-11-19, authorization id E07-CS005-FREEZE-AUTH-01 (record manifests/cs-005-freeze-v1.yaml; the two open cells of D-E07-6 were decided COMPARABLE, D-E07-11 and D-E07-12, after round 1 of the DRY_RUN). Canonical scenario CS-006 (WEB to API): experiments/scenario-mappings/CS-006.yaml, sha256 b5764b776b447c5055f1288a54a7739e0651a30353bf999dde4d34a88b791986, mapping_status FROZEN on 2026-11-19, authorization id E07-CS006-FREEZE-AUTH-01 (record manifests/cs-006-freeze-v1.yaml).
- The comparability recorded in the frozen mapping records is the one used: SUT-01 and SUT-04 are COMPARABLE in both records, so each of the four conditions below has a COMPARABLE entry; SUT-02, SUT-03, SUT-05 and SUT-06 are NOT_COMPARABLE in both records and have no condition (they are reported as no data with their reasons, never as a zero or a failure; protocol/statistical-analysis-plan-v1.md, section 5). No cross-ecosystem comparison is made by this campaign.

### Pinned versions

- SUT-01 web and api: OmniPizza at commit 9ca37674d374e9303912e259641ee86baf3aabe1 (no release). SUT-04 web and api: restful-booker-platform at commit d36bd3f8647a091d406e53bad463c5e3e5d2ece1 (release 2.2). Source: manifests/sut-manifest.yaml, sha256 7f954c958f5558729ff9be23b9bea1471d205e43baf0f461ccb08f7984cf2d58.
- Web runner: Playwright for Python 1.63.0 with the hashed requirements of experiments/E07-cross-layer-continuity/executor/requirements.txt, sha256 35b65ea4c57a3bc1ddccaab846bab0b986ff76de8b09ac69d2455fedf04dfb4b (a copy of the requirements of E04). API client: the Python 3 standard library (urllib.request). Browser: the Chromium build named by Playwright 1.63.0, not hash-pinned by the study.
- Run-manifest schema: schemas/run-manifest.schema.v2.json, sha256 9a86cf37c4ccd2abe3368866309e18a9f9554a2330f5dceeacda6d02a2932757. source_layer and verification_layer are mandatory on every E07 record by campaign convention.
- Reference values of the runner, Python, Node.js and browser versions, as recorded by the DRY_RUN rounds 2 and 3 (recorded per job in tool-versions.json and runtime-environment.json, and never a gate): executor Python 3.12.16, bash 5.2.21(1)-release, Playwright for Python 1.63.0, Chromium 153.0.8010.12; runner image ubuntu24 20261111.127.1 and ubuntu24 20261111.370.1 and ubuntu24 20261116.133.1; system Python 3.12.3, Node.js v22.23.4 and v22.23.5, npm 10.9.9, git version 2.56.1. The runner image version differs between jobs of the same dispatch; the drift is recorded per job and is not a gate.

### Prompt version and implementation

- Dispatch procedure prompt: ORCHESTRATOR-E07-cross-layer-continuity-v1. Working copy: prompts/working/ORCHESTRATOR-E07-cross-layer-continuity-v1.md, sha256 60c0cc08e3b8fc2b7aa2b8d8d6e45f5d6eafaabebd55d69e5336de1dd6201895. The frozen copy prompts/frozen/ORCHESTRATOR-E07-cross-layer-continuity-v1.md is written once at the START as a byte-identical copy of the working copy (prompts/README.md, rules 1 to 3); it is not written by this text.
- Implementation hash (sha256 of experiments/E07-cross-layer-continuity/executor/run-condition.sh, which embeds the digests of the executor Python files and of requirements.txt and refuses an unlisted file): 55a352aaabb37c64ead88b235dbe9fe7e10e167d45d39162dd6ea63c17f0ef59. This is the implementation that ran in the non-measured environment-verification rounds 2 and 3 (runs 44564694778 and 44567888786); round 1 (run 44529314764) ran the previous implementation d1c48df5ced86bf0b972c555e3d060d3065f2e8ccebb8a4f49cd0cce01a89f00, which did not compare the check-out date on the SUT-04 admin web row (decision D-E07-15).
- Conditions file: experiments/E07-cross-layer-continuity/conditions-draft.json, sha256 0baf2497948562f35c5236df460cf497497b571ec4024ef7a27ecc13ff5f2151 (four conditions; read by the executor; hashed here at the START).

### Conditions

All conditions: N = 50 executions, EX0001 to EX0050, attempt 1, environment_type SELF_HOSTED (a controlled instance provisioned in the job from the pinned commit on a GitHub-hosted runner, never PUBLIC_HOSTED), expected category VERIFIED. The condition list below is the one of the decision D-E07-8; the four cells are COMPARABLE in the frozen mapping records (CS-005: SUT-01 and SUT-04; CS-006: SUT-01 and SUT-04), and the cells of SUT-02, SUT-03, SUT-05 and SUT-06 are recorded as no data with their reasons.

| Condition | Scenario and direction | Account | Reset between attempts (outside the scenario, not counted) | Identity keys and attributes compared |
|---|---|---|---|---|
| E07-CS005-SUT01-API-WEB | CS-005, API to WEB | standard_user | session clear through the API (API_RESET, SESSION_RESET) and a new browser context per execution | JWT claim sid; cart line pizza_id p02, quantity 1 |
| E07-CS005-SUT04-API-WEB | CS-005, API to WEB | admin | deletion through the booking API of the room 1 bookings that carry the run's guest names (API_RESET) and a new browser context per execution | run-unique guest names; check-in and check-out dates of room 1 |
| E07-CS006-SUT01-WEB-API | CS-006, WEB to API | standard_user | as E07-CS005-SUT01-API-WEB | as E07-CS005-SUT01-API-WEB |
| E07-CS006-SUT04-WEB-API | CS-006, WEB to API | admin | as E07-CS005-SUT04-API-WEB | as E07-CS005-SUT04-API-WEB |

The per-step realizations (login, establishment, read-back, verification) are those of the entries of CS-005 and CS-006 for the SUT and of the executor README (experiments/E07-cross-layer-continuity/executor/README.md); the keys are declared here before the first attempt and a key that is not observable on the verification layer is not used (D-E07-9).

### Blocks, outcome categories and the continuity proportion

- Block order of every execution: reset; starting-state check; establishment (source layer); establishment check (source layer, read-only); verification (the other layer, read-only); record. Verification changes no state; timing is not part of the criterion.
- A block that does not hold stops that execution with its category; the job goes on with the next execution. Only a failure of the job itself stops the job.
- Outcome categories (declared before any execution, in experiments/E07-cross-layer-continuity/conditions-draft.json; D-E07-10): VERIFIED (status SUCCESS; every declared key and attribute is observed on the verification layer and matches the establishment record); NOT_VERIFIED (the observation completed and at least one key or attribute is absent or different, including an HTTP error answer of the verification read); ESTABLISHMENT_FAILED (the establishment or its source-side check did not confirm the unit); INTERRUPTED (a failed reset, RESET_FAILED, a starting state not reached, STARTING_STATE_NOT_REACHED, or the per-execution watchdog, WATCHDOG; each with its cause); RUNNER_ERROR (an exception of the executor, browser, client or infrastructure inside a block, with the last phase recorded). The mapping of each category to the run-manifest outcome status is the one of the executor README. The expected category of every condition is VERIFIED.
- Primary variable: the continuity success proportion per condition = VERIFIED / all valid measured attempts (option A; the denominator includes every attempt, also the ones that ended in ESTABLISHMENT_FAILED, INTERRUPTED or RUNNER_ERROR), with the Wilson 95 percent interval without continuity correction. Secondary, reported apart: the conditional proportion = VERIFIED / attempts whose establishment succeeded (option B), with its Wilson interval, and NOT_ESTIMABLE (never 0) when no attempt established the unit. If no valid measured attempt exists the proportion is not estimable and is reported as such.

### Attribution and exclusion rules

- No attempt is excluded from any denominator (protocol/repeatability-determinism-v1.md, section 5, rules 4 and 5). A failed starting-state check is recorded as INTERRUPTED with its cause, is counted, and the job goes on.
- Attribution (decision D-E07-10, as in E04): TOOLING for an interruption of a block (the per-execution watchdog) and for every exception of the executor, browser, client or infrastructure (RUNNER_ERROR); SUT for every recorded failure of a block (a failed reset or establishment, an HTTP error answer, a state that did not hold, NOT_VERIFIED) and for every attempt whose cause cannot be assigned mechanically. Attribution is mechanical and fixed here; it is never applied after seeing a result pattern. Attributed counts (TOOLING and SUT per category) are reported beside the raw proportion; the raw proportion is never recomputed on the attributed counts.
- As implemented by the executor (experiments/E07-cross-layer-continuity/executor/IMPLEMENTATION-NOTES.md, section 3, items 5 to 7; confirmed by the human research lead's approval of this text at the START): a transport failure of an HTTP call (no answer) is recorded as an observation of that call and counts as a recorded failure of the block (SUT), as in E04; an exception of the browser or of the executor is RUNNER_ERROR (TOOLING); a bundle that cannot be written is recorded as RUNNER_ERROR (TOOLING) with the cause BUNDLE_NOT_WRITTEN (the category STUB_NO_BUNDLE of E04 is not carried: the five categories of D-E07-10 are the whole set). The check-out date is compared on both layers (D-E07-15: DRY_RUN round 1 showed that the SUT-04 admin web row lists it); the sid claim of the SUT-01 key confirms the session binding, since both layers hold the same login token.
- A runner cancelled or lost by the workflow leaves an incomplete bundle; the ORCHESTRATOR records such an execution at import as TOOLING of that execution (not implemented by the executor; confirmed by the human research lead's approval of this text at the START).
- The executor scrubs host paths and private network addresses from every kept text file (the executor's scrubber); no secret is recorded.

### Sample size, order and dispatch model

- N = 50 executions per condition (protocol/repeatability-determinism-v1.md, section 3, standard target; no reduction): 50 times the number of conditions (200 for the four conditions above); one dispatch per condition, one job per dispatch, attempt 1.
- Model: one job runs the 50 executions of one condition sequentially on one shared instance (the model B of E04 and E05, decision D-E07-8); the reset of the condition runs at the start of every execution and the starting-state check follows it in every execution.
- Dispatch order (fixed here before the first dispatch): SUT-01: E07-CS005-SUT01-API-WEB, E07-CS006-SUT01-WEB-API; SUT-04: E07-CS005-SUT04-API-WEB, E07-CS006-SUT04-WEB-API. The conditions of one SUT run one at a time, a dispatch only after the previous run of its authorization has concluded and been imported; the chains of the two SUTs are independent and may run concurrently.
- Dispatch records (append-only, committed before each dispatch; the run identity is appended after it starts): manifests/e07-measured-dispatch/e07-sut01.jsonl and e07-sut04.jsonl, created at the first dispatch of each SUT, not at the START.
- Identifiers: execution_id EX0001 to EX0050; attempt A1; run_id <condition_id>__<execution_id>__A<attempt>.
- Import: byte-exact under raw-data/E07-cross-layer-continuity/<SUT>/ after the verification of every archive against its GitHub digest: each executions/<run_id>/ directory becomes raw-data/E07-cross-layer-continuity/<SUT>/<run_id>/; the job files are kept in raw-data/E07-cross-layer-continuity/<SUT>/<condition_id>__job__A<attempt>/.
- Stop conditions: the frozen dispatch procedure (prompts/frozen/ORCHESTRATOR-E07-cross-layer-continuity-v1.md, section 4) applies: the gate job of a run fails; a run's conclusion is other than success or a failure of the measured job; an artifact does not hold exactly the 50 run manifests of its condition; an input differs from this text, the authorization or the public repository; a boundary of the procedure would be crossed; the authorization is revoked or the human research lead stops the campaign. On a stop nothing further is dispatched in this campaign under any authorization until the human research lead instructs otherwise.

### Dispatch authorization and further attempts

- One dispatch authorization per SUT, issued separately by the human research lead under protocol/agent-governance-v6.md, Section 3.7: E07-DISPATCH-SUT01-AUTH-01 (SUT-01) and E07-DISPATCH-SUT04-AUTH-01 (SUT-04). Each names the conditions of its SUT, N = 50, attempt 1, the implementation hash and the prompt hash above, and the authorization id of this START. The START authorizes no dispatch authorization.
- Further attempt (attempt 2 or more, from a first execution named by the approval): only under a further-attempt approval of the human research lead that names the condition, the first execution and the attempt (gate G-E07-A2; the approval record is manifests/e07-further-attempt-approval-sut0N-v1.yaml, created only when approved). Nothing is re-run; the failed or interrupted executions of the first attempt keep their recorded outcomes.

### Controlled instances

- Controlled-instance record: experiments/E07-cross-layer-continuity/controlled-instance-status.yaml, written at the START from the prepared content. Every condition is CONTROLLED only when its status is VERIFIED on GitHub Actions by a non-measured DRY_RUN round of .github/workflows/e07-environment-verification.yml. All four conditions are VERIFIED by rounds 2 and 3, both run under the executor implementation locked here, 3 executions per condition DR0001 to DR0003 (12 executions read; record manifests/e07-environment-verification-rounds-v1.yaml, sha256 1dbb8b9f0cc989d346a15b3a25f0b2f4087e7dadff31f138a147f77a73ff6c03): round 2 (run 44564694778, dispatched 2026-11-19T16:18:59Z on public main 4992205ba9988d3b4553054b96514c9ae1430236) holds the three conditions E07-CS005-SUT01-API-WEB, E07-CS006-SUT01-WEB-API and E07-CS006-SUT04-WEB-API; its fourth job, E07-CS005-SUT04-API-WEB, failed in its Maven build step before the executor ran (no execution; it stays recorded), and round 3 (run 44567888786, dispatched 2026-11-19T16:35:53Z on public main 4992205ba9988d3b4553054b96514c9ae1430236, limited to that condition) repeated it. Round 1 (run 44529314764) ran the previous implementation d1c48df5ced86bf0b972c555e3d060d3065f2e8ccebb8a4f49cd0cce01a89f00 and is a historical reference, not a basis. In the three conditions SUT-01 API to WEB, SUT-04 API to WEB and SUT-04 WEB to API every execution recorded VERIFIED, and in SUT-01 WEB to API every execution recorded NOT_VERIFIED; the verified controlled instance is the environment status of the condition, and the continuity category of a DRY_RUN execution is neither an environment status nor a measurement. DRY_RUN bundles are never measured and never imported.

### Analysis and what is not computed

- Per condition: T (valid measured attempts), V (VERIFIED executions), the continuity success proportion V / T with its Wilson 95 percent interval, the conditional proportion with its interval, the category counts and the attributed counts beside the raw proportion. Descriptive only.
- Under DP-4 strict (D-E07-1) SUT-03 is NOT_COMPARABLE in both records, so no CONFIRMATORY H4 continuity comparison is evaluable: the four candidate comparisons of campaign-configuration-draft.md, section 13, are reported with their reasons (SUT-02 and SUT-03 no data), never as a zero or a failure. The SUT-04 conditions are a specialist reference and EXPLORATORY (protocol/statistical-analysis-plan-v1.md, section 4.2).
- Not computed, not compared, not pooled: no between-ecosystem comparison; no pooled rate across conditions, directions or ecosystems; no composite score; no latency (D-E07-5); no test, p-value, risk difference or effect size; no Holm family.
- The analysis is run only on a separate instruction of the human research lead, after the campaign is frozen, with its own derived dataset (derived-data/README.md; analysis/README.md).

### Gates the measured workflow enforces

The measured job starts only if the gate step of .github/workflows/e07-measured-execution.yml passes: the campaign status is IN_PROGRESS in manifests/study-manifest.yaml; exactly one START row of protocol/CHANGELOG.md names this campaign README and the START authorization id; the START record manifests/e07-campaign-start-v1.yaml names the campaign and the authorization id; this section names the condition, the schema, the prompt version, the implementation hash, the conditions-file hash, the measured workflow hash (G-9), N = 50, CS-005 and CS-006, the continuity success proportion, and the pinned commits of the assigned SUT and, for a release, the release; the dispatch authorization of the assigned SUT is ISSUED, VALID, ELIGIBLE, not revoked, issued by the human research lead, and names the condition, N = 50, attempt 1, the START id and the two hashes; the frozen prompt file exists and matches its hash; the further-attempt approval (G-E07-A2) when the attempt is above 1; agent-governance-v6 is in force with Section 3.7; the run-manifest schema v2 is present; the controlled-instance status of the condition is CONTROLLED, its GitHub Actions verification is VERIFIED, no reverification is required, and the environment type is SELF_HOSTED; the mapping records of the condition's canonical scenario are FROZEN with a COMPARABLE entry for the assigned SUT; the executor implementation equals the locked hash. The job also refuses a GitHub re-run (github.run_attempt must be 1) and any branch other than the default branch.

### Change log

- None at the time of this text. Any change after the START is a change-control row (protocol/change-control-v1.md) recorded before the affected execution; results collected before a change are analyzed under the configuration in force when they were collected.
