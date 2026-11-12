# E02 — State Establishment

## Objective

Measure the Required Actions, and secondarily the duration, needed to establish an equivalent target state in each evaluated ecosystem (each a system under test, SUT) starting from a declared starting state. The campaign characterizes the mechanisms each ecosystem offers for reaching a controlled state and the effort those mechanisms demand. "Equivalent target state" across ecosystems means semantic equivalence under protocol/equivalent-scenario-mapping-v1.md: every target state used for inferential comparison is a canonical scenario with a FROZEN mapping record before this campaign executes; an ecosystem without a defensible semantic equivalent is NOT_COMPARABLE for that scenario (not a score, not a zero). One-time provisioning of each instance is recorded descriptively in a provisioning record and is not counted; only per-run / per-condition setup enters Required Actions (protocol/setup-effort-v2.md; v1 is AMENDED).

## Related research question(s)

- RQ2 Controllability, Observability, Automation Affordances, and Setup Effort (primary).
- Informs dimensions 2 Experimental Controllability and 6 Setup Effort.

## Independent variables (locked in the campaign configuration below)

- Ecosystem (SUT-01 through SUT-06; SUT-06 is NOT_COMPARABLE on both scenarios and has no condition).
- Target state (canonical_scenario_id from the frozen scenario mapping records, protocol/equivalent-scenario-mapping-v1.md); the FROZEN records CS-003 and CS-004 are required and are the only target states of this campaign.
- Surface (web / api; the mapped surfaces of CS-003 and CS-004, listed per condition in the campaign configuration; android and ios are not used).
- Establishment mechanism(s) used (`establishment_mechanisms`; frozen vocabulary: UI_FLOW, API_SEED, DIRECT_ROUTE, DEEP_LINK, FIXTURE, PREDEFINED_ACCOUNT, CONFIGURATION, APP_STATE_CONTROL, NONE, OTHER — protocol/setup-effort-v2.md, section 10; one or more per run).

## Dependent variables (locked in the campaign configuration below)

- Required action count, broken down by the six action classes defined in protocol/setup-effort-v2.md sections 4 and 5 (FROZEN-PRE-DATA; the counting rules of the executor README, section 3).
- Establishment success / failure (categorical).
- Duration from declared starting state to verified target state (secondary).
- Manual intervention required (categorical, with description).

## Required evidence

- Run manifest per run conforming to schemas/run-manifest.schema.v2.json (v1 is preserved; v2 adds only the optional per-action outcome), including ecosystem id, canonical scenario (`scenario` = canonical_scenario_id, as in every campaign that uses canonical scenarios), target state id (`target_state_id`: the target state defined by that scenario's frozen mapping record; the exact per-run convention is fixed in this campaign's configuration, protocol/change-control-v1.md section 7), surface (`platform`), `environment_type`, establishment mechanism(s) (`establishment_mechanisms`, mandatory and non-empty for E02 runs; protocol/setup-effort-v2.md, section 10), declared starting state (`starting_state_id`), and outcome.
- Frozen mapping record for every canonical scenario used, listed in the campaign configuration (protocol/change-control-v1.md, section 7), with the comparability marker per ecosystem.
- Provisioning record per instance used (protocol/setup-effort-v2.md, section 8), descriptive only.
- Ordered action list for the run, recorded in the run manifest `actions` field (schemas/run-manifest.schema.v2.json): every action taken, its class per protocol/setup-effort-v2.md section 4 (Action classes), its position, whether it was a retry, and the reason for any manual action.
- Verification artifact confirming the target state was reached (for example a response record, screenshot, or state dump): the run manifest with `actions.json` and `precondition.json` of the run (decision HD-22 of the executor notes).
- Provenance of the ecosystem artifacts exercised (repository, commit_sha_or_release), recorded as null when unknown.
- Record of any manual intervention, including what was done and why.
- Raw observations in `raw-data/E02-state-establishment/<SUT>/<run_id>/`.

## Execution path

Every MEASURED_EXPERIMENT of this campaign runs only through `.github/workflows/e02-measured-execution.yml` on GitHub Actions, under ORCHESTRATOR coordination and the narrow authorization CAMPAIGN-CI-WRITE-AUTH-01 (no executor role is launched; protocol/agent-governance-v6.md, Sections 3.6 and 3.7). A dispatch is made only within a dispatch authorization that the human research lead issues for the assigned SUT (Section 3.7), is recorded before it runs, and is never re-run. The environment verification of each condition (`.github/workflows/e02-environment-verification.yml`, DRY_RUN only, never measured data) precedes the START; its record is `manifests/e02-environment-verification-import-v1.yaml`.

## H2, establish side

The establish side of H2 has two pairs per comparison, CS-003 and CS-004, on the web surface: SUT-01 against SUT-02 and SUT-01 against SUT-03 (descriptive, because two pairs cannot reach significance; protocol/statistical-analysis-plan-v1.md, section 4). The analysis starts only on a separate human instruction; the reset side is E03-resetability.

## Campaign configuration

LOCKED at the E02 campaign START of 2026-11-10 under the human authorization `E02-START-AUTH-01` (protocol/change-control-v1.md, section 7, moment 1: `campaign NOT_STARTED -> IN_PROGRESS`, change-log row of the same date). From that moment every item below is locked for the campaign: a change to any of them while IN_PROGRESS requires its own change-log row with the reason, and results collected before the change are analyzed under the earlier configuration. The section is justified item by item in `manifests/e02-campaign-start-package-v3.yaml` (or its successor version); the realization rows, counting conventions, and the decisions listed under "Decisions carried into the configuration" are those of `experiments/E02-state-establishment/executor/README.md` and `executor/IMPLEMENTATION-NOTES.md` at the locked implementation hash.

### Canonical scenarios and mapping records

- **CS-003** (`experiments/scenario-mappings/CS-003.yaml`, sha256 `83815775737c258c9e44c9946e9d2264015cf398ef796f7e08d61f5e38dae3f3`), mapping_status FROZEN (`E02-CS003-FREEZE-AUTH-01`, 2026-11-02): precondition CLEAN_SESSION; COMPARABLE for SUT-01 (WEB, API), SUT-02 (WEB), SUT-03 (WEB), SUT-04 (WEB, API), SUT-05 (API); SUT-06 NOT_COMPARABLE.
- **CS-004** (`experiments/scenario-mappings/CS-004.yaml`, sha256 `590af7258aeeb17b5ed73376ae3d8a2e71f86771b5c086ee5af4c266accc4cfe`), mapping_status FROZEN (`E02-CS004-FREEZE-AUTH-01`, 2026-11-06): precondition SEEDED_BUSINESS_STATE (uncounted); WEB only; COMPARABLE for SUT-01, SUT-02, SUT-03; NOT_COMPARABLE for SUT-04, SUT-05, SUT-06.
- `experiments/scenario-mappings/CS-001.yaml` is scoped to E03-resetability and is not an input to this configuration.
- Population: six systems under test (SUT); SUT-06 stays a member and has no condition (NOT_COMPARABLE on both scenarios, NO_EQUIVALENT_INTENT).

### Pinned SUT versions

`manifests/sut-manifest.yaml` (pinned 2026-09-16; `evaluated_version_frozen` true since the E03 START of 2026-10-28), copied here for the components that the conditions run; no pinned value is changed by this START.

| SUT | Surface | Repository | Commit | Release |
|---|---|---|---|---|
| SUT-01 | web | https://github.com/gsanchezm/OmniPizza | 9ca37674d374e9303912e259641ee86baf3aabe1 | none |
| SUT-01 | api | https://github.com/gsanchezm/OmniPizza | 9ca37674d374e9303912e259641ee86baf3aabe1 | none |
| SUT-02 | web | https://github.com/saucelabs/sample-app-web | 60fdd634bb111c092282fa07977513a0a7765593 | none |
| SUT-03 | web | https://github.com/browserstack/browserstack-demo-app | 7ab934d733f2f74d4b912e94e86f59ae0f6b7609 | none |
| SUT-04 | web | https://github.com/mwinteringham/restful-booker-platform | d36bd3f8647a091d406e53bad463c5e3e5d2ece1 | 2.2 |
| SUT-04 | api | https://github.com/mwinteringham/restful-booker-platform | d36bd3f8647a091d406e53bad463c5e3e5d2ece1 | 2.2 |
| SUT-05 | api | https://github.com/juice-shop/juice-shop | 1618a611b173b4bf114028e6e02549950606e29d | v20.2.0 |

The SUT-05 instance runs the packaged distribution of its pinned release v20.2.0 and the SUT-04 instance follows the route of the SUT's README, as provisioned by the pinned workflow (the provisioning steps are those of the E03 measured job, copied into `.github/workflows/e02-measured-execution.yml`).

### Toolchain versions

- Web runner: Playwright for Python 1.63.0, with its runtime dependencies pinned by exact version and sha256 hashes in `experiments/E02-state-establishment/executor/requirements.txt` (sha256 `7d8dafab6bda619c24cd690013386dc5c1a03ff7f97733aa644d774382dd435f`; its 13 non-comment lines equal those of the E03 requirements file), installed with `--require-hashes --only-binary :all:`; Chromium is the build that this Playwright version names, downloaded by `playwright install chromium`, not hash-pinned by the study, and its observed version is recorded per run.
- API client: the Python 3 standard library (`urllib.request`) of the runner's python3; the observed version is recorded per run.
- Execution substrate: GitHub Actions, ubuntu-24.04 GitHub-hosted runners, through `.github/workflows/e02-measured-execution.yml` only (CAMPAIGN-CI-WRITE-AUTH-01); the workflow file sha256, the repository SHA, and the runner image are captured per run as gate and provenance outputs.
- Mobile runner: not used; no mobile condition exists in this campaign.

### Dispatch procedure prompt, implementation, schema

- Dispatch procedure prompt version id (the `executor_prompt_version` input of the measured-execution workflow and the `prompt_version` of every run manifest): `ORCHESTRATOR-E02-state-establishment-v1` (frozen copy `prompts/frozen/ORCHESTRATOR-E02-state-establishment-v1.md`, sha256 `9306ac72a6bd49ec47d7efcef3e158d18f76c28c4e2247c29e0c6280604a2f91`); the working copy is byte-identical to the frozen copy, which is written once, at the START (prompts/README.md, rule 2).
- Executor implementation: `experiments/E02-state-establishment/executor/run-condition.sh`, sha256 `d0b1bbb9d3014fedb0edaa58186b1cfb2d52759dfd67c2bc1c218c7f45db5200` (3032 bytes); the digests embedded in that file cover every other implementation file (`executor/executor/*.py`, `requirements.txt`), so this single hash locks the whole implementation; the run manifests record `agent_role` ORCHESTRATOR.
- Run-manifest schema: `schemas/run-manifest.schema.v2.json` (sha256 `9a86cf37c4ccd2abe3368866309e18a9f9554a2330f5dceeacda6d02a2932757`); `actions[].outcome` is mandatory on every emitted action record by campaign convention; `establishment_mechanisms`, `starting_state_id`, and `target_state_id` are recorded on every run (protocol/setup-effort-v2.md, section 10).
- Agent governance: `protocol/agent-governance-v6.md` (sha256 `c890a9d004b2989aa9ae33a54bc68b000c47fc9e3f79d60ad0051de78b3f2a4a` of the canonical file; the public repository holds the provider-neutral export of that file, bridged to it by `PUBLIC-EXPORT-MANIFEST.yaml`), FROZEN-PRE-DATA since 2026-11-06, whose Sections 3.6 and 3.7 govern the execution of this campaign under ORCHESTRATOR coordination with one dispatch authorization per assigned SUT.

### Conditions

Ten conditions, one per COMPARABLE SUT x surface x scenario, establish direction only (resetting a state belongs to E03-resetability). `environment_type` is SELF_HOSTED on a GitHub-hosted runner for every condition (protocol/study-design-v1.md, section 10.3: a controlled instance, never PUBLIC_HOSTED). A condition is dispatched only while its record in `experiments/E02-state-establishment/controlled-instance-status.yaml` is CONTROLLED and VERIFIED on GitHub Actions (gate G-8). Mechanisms are recorded per run, not per condition.

| Condition id | SUT | Surface | Scenario | Starting state | Establishment mechanisms declared by the realization | N per condition | Status at START |
|---|---|---|---|---|---|---|---|
| E02-CS003-SUT01-WEB | SUT-01 | WEB | CS-003 | CLEAN_SESSION | PREDEFINED_ACCOUNT, API_SEED, APP_STATE_CONTROL, DIRECT_ROUTE | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS003-SUT01-API | SUT-01 | API | CS-003 | CLEAN_SESSION | PREDEFINED_ACCOUNT, API_SEED | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS004-SUT01-WEB | SUT-01 | WEB | CS-004 | SEEDED_BUSINESS_STATE | PREDEFINED_ACCOUNT, API_SEED, APP_STATE_CONTROL, DIRECT_ROUTE | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS003-SUT02-WEB | SUT-02 | WEB | CS-003 | CLEAN_SESSION | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS004-SUT02-WEB | SUT-02 | WEB | CS-004 | SEEDED_BUSINESS_STATE | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS003-SUT03-WEB | SUT-03 | WEB | CS-003 | CLEAN_SESSION | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS004-SUT03-WEB | SUT-03 | WEB | CS-004 | SEEDED_BUSINESS_STATE | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS003-SUT04-WEB | SUT-04 | WEB | CS-003 | CLEAN_SESSION | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS003-SUT04-API | SUT-04 | API | CS-003 | CLEAN_SESSION | PREDEFINED_ACCOUNT, API_SEED | 50 (EX0001 to EX0050) | EXECUTABLE |
| E02-CS003-SUT05-API | SUT-05 | API | CS-003 | CLEAN_SESSION | PREDEFINED_ACCOUNT, API_SEED | 50 (EX0001 to EX0050) | EXECUTABLE |

All ten conditions are executable. The checkout-entry and checkout-view selectors of the CS-004 realizations of SUT-02 and SUT-03 were read from the pinned sources on 2026-11-06 (SUT-02 commit 60fdd634bb111c092282fa07977513a0a7765593, SUT-03 commit 7ab934d733f2f74d4b912e94e86f59ae0f6b7609; decision of the human research lead recorded in `manifests/campaign-execution-decisions-v3.yaml`, OPEN-1) and were exercised by the environment-verification DRY_RUNs that precede this START. All ten conditions are VERIFIED on GitHub Actions: the DRY_RUNs of 2026-11-09 with execution id DR0002, run on the implementation hash locked above, ran each condition to SUCCESS with its declared counted operations (`experiments/E02-state-establishment/controlled-instance-status.yaml`; record `manifests/e02-environment-verification-import-v1.yaml`). The first round of ten (DR0001, implementation hash 602dfaf6ccc4...) found three defects of starting-state checks, corrected before the lock (HD-N below); the DRY_RUN bundles are reviewed and never imported as measured data. The run-level `establishment_mechanisms` of a run is the list that its realization declares (the column above); it names every mechanism that the counted operations and the uncounted precondition steps of the realization use (a contract test of the executor enforces it), and the precondition steps are recorded one by one in `precondition.json`.

### Sample size per condition

N = 50 per condition (protocol/repeatability-determinism-v1.md, section 3, Standard): execution ids EX0001 to EX0050, attempt 1 each, one dispatch per execution; 500 planned executions in all. Required Actions (establish) statistics are computed over the attempts that reached the verification; ABORTED, INCONCLUSIVE, and ERROR attempts are reported beside them, never dropped.

### Counting, starting state, and between-run reset

- Counting follows `experiments/E02-state-establishment/executor/README.md`, section 3, at the locked implementation hash (protocol/setup-effort-v2.md, sections 4 and 5): one counted action is one experimenter-initiated operation with an observable effect, authentication and the verification read count, and no count is predeclared in this configuration.
- The declared starting state is checked by an uncounted read; when it does not hold the run stops as ABORTED and keeps the counted operations performed before the check. A failed counted operation stops the establishment; no retry exists.
- Between runs each measured job provisions a fresh controlled instance (provisioning, not counted); the named reset realizations of the mapping records are not executed.

### Decisions carried into the configuration

These are the decisions of 2026-11-05 and 2026-11-06 recorded in `manifests/campaign-execution-decisions-v2.yaml` and `manifests/campaign-execution-decisions-v3.yaml`, used as the working defaults: HD-R (a fresh instance per run instead of the named reset; disclosed), HD-8 of the CS-003 record (the SUT-02 oracle is UI-only and the SUT-04 account is an administrator under the standard actor state; used as the frozen text words them and disclosed in the paper), HD-15 (every page load started by the experimenter is counted, the first included), HD-A (the starting-state check follows the first identity action where the state needs it), HD-C (the SUT-03 float-cart close is counted), HD-V (a verification read that completes is SUCCESS and the predicate decides the run outcome), HD-F (no retry after a failed counted operation), HD-22 (the verification artifact is the run manifest with `actions.json` and `precondition.json`), HD-E (resolved: governance v6 was frozen on 2026-11-06 and the CI correction OP-CI-17 made the verification gate check the working prompt), HD-S (the CS-004 checkout selectors of SUT-02 and SUT-03 were read from the pinned sources), HD-M (the declared run-level mechanisms of a condition name every mechanism that its realization uses), and HD-N (the starting-state checks corrected after the first DRY_RUNs: an absent client cart key is an empty client cart for SUT-01, the cart half of the SUT-02 CS-003 state is read after the authentication because the cart link does not exist on the login page, and the Checkout label of SUT-03 is compared without regard to case).

### Exclusion and attribution rules

None beyond the frozen discipline: no run is excluded after the fact; an attempt keeps its recorded outcome; a further attempt (attempt + 1) is dispatched only on an explicit human instruction that names the condition and the execution; the first attempt of an execution is immutable; no attribution rule is introduced (the deferred issue (xix) belongs to other campaigns).

### CONFIRMATORY comparisons

H2 (`protocol/statistical-analysis-plan-v1.md`, section 4.3): SUT-01 versus SUT-02 and SUT-01 versus SUT-03, on Required Actions (establish) per COMPARABLE canonical scenario, paired on the WEB surface; this campaign contributes the establish side only (the reset side is E03-resetability). The pairs are CS-003 and CS-004 (two pairs per comparison). The method is descriptive: paired per-scenario differences are reported without a significance test, because the statistical analysis plan applies a Wilcoxon test only where the number of non-tied pairs is adequate, a term it does not define, and with n non-tied pairs the smallest two-sided exact p-value is 2 x 2^-n (derived here: 0.5 at n = 2). No comparison involving SUT-04 or SUT-05, and no API comparison, is pre-registered CONFIRMATORY; they stay EXPLORATORY.

### Execution

Every MEASURED_EXPERIMENT runs only through `.github/workflows/e02-measured-execution.yml` on the default branch of the PUBLIC repository (GitHub Actions reads the public tree, so the dispatches follow the publication of the START state), one condition, one execution, one attempt per dispatch, first attempt only, no GitHub re-run. The runs are dispatched by the ORCHESTRATOR under `protocol/agent-governance-v6.md`, Sections 3.6 and 3.7, and the frozen dispatch procedure `ORCHESTRATOR-E02-state-establishment-v1`, with the frozen inputs of this record; no agent session is instantiated per SUT. The ORCHESTRATOR dispatches only within a dispatch authorization that the human research lead issued, one per assigned SUT, naming that SUT's executable conditions and N; a dispatch authorization is not issued by this section, by a prepared record, or by the START, and the human may revoke it at any time. Within it each execution is dispatched in the order below without a further approval of each exact dispatch: exactly one dispatch per execution, never cancelled, re-run, or repeated, and never a second run of a condition while one is in progress.

### Order of dispatches and dispatch record

Order (fixed here, before the first dispatch; protocol/agent-governance-v6.md, Section 3.7, "Order and record"): within a dispatch authorization, the conditions of the assigned SUT are dispatched in the order of the Conditions table above, a condition being completed (EX0001 to EX0050, in ascending order, each only after the run before it concluded) before the next condition of the same SUT starts; no order across SUTs is fixed by this record, the chains of different SUTs are independent, and no decision whether, when, or how to dispatch an execution depends on a measured output of any SUT. Dispatch record: the append-only record is one file per condition, `manifests/e02-measured-dispatch/<condition id>.jsonl`, one line per event; the line of a dispatch (condition id, execution id, attempt, inputs, the UTC clock reading, and the revisions of the public repository and of the workflow file that are dispatched) is committed before the dispatch is made, and the line of its run identity (run id, run number, run attempt, head sha, creation time) is committed no later than the dispatch line of the next execution of that condition, or at the close of the condition. The stop conditions are those of the frozen dispatch procedure.

## Current status

**FROZEN** since 2026-11-12 (human authorization `E02-FREEZE-AUTH-01`; protocol/change-control-v1.md, section 7, moment 2; record `manifests/e02-campaign-freeze-v1.yaml`), after being **IN PROGRESS** from the campaign START of 2026-11-10 (human authorization `E02-START-AUTH-01`; protocol/change-control-v1.md, section 7, moment 1; record `manifests/e02-campaign-start-v1.yaml`). The START authorized no dispatch. The five dispatch authorizations, one per assigned SUT, were issued by the human research lead on 2026-11-11 under protocol/agent-governance-v6.md, Section 3.7 (E02-DISPATCH-SUT01-AUTH-01 to E02-DISPATCH-SUT05-AUTH-01; `manifests/e02-dispatch-authorization-sut01-v1.yaml` to `manifests/e02-dispatch-authorization-sut05-v1.yaml`; 500 executions in all, attempt 1). All 500 executions were dispatched and imported unchanged under `raw-data/E02-state-establishment/<SUT>/` between 2026-11-11T18:31Z and 2026-11-12T04:44Z UTC, with their dispatch records under `manifests/e02-measured-dispatch/` (503 dispatches: 497 executions as attempt 1 and three as attempt 2, SUT-01 EX0008, SUT-02 EX0007 and SUT-03 EX0005, each under its own further-attempt approval record, `manifests/e02-further-attempt-approval-sut01-v1.yaml` to `-sut03-v1.yaml`, operation OP-ATTEMPT2-E02-01, with the workflow revision of operation OP-CI-18, `manifests/e02-op-ci-18-v1.yaml`). The three attempt-1 runs that left no bundle stay recorded in the dispatch records and are reported beside attempt 2, never replaced or deleted. The campaign configuration above is immutable, `raw-data/E02-state-establishment/` is append-only, and no E02 analysis has been made (H2 establish side NOT_ANALYZED). All ten conditions are VERIFIED on GitHub Actions (`manifests/e02-environment-verification-import-v1.yaml`; `experiments/E02-state-establishment/controlled-instance-status.yaml`).

Resumed by the human research lead's decision of 2026-11-02 (manifests/campaign-resumption-v1.yaml); the deferral of scope A (manifests/campaign-disposition-v1.yaml) no longer governs the schedule.

Preparation (2026-11-02): the target-state records are the canonical scenarios CS-003 (experiments/scenario-mappings/CS-003.yaml), FROZEN on 2026-11-02 under the authorization id E02-CS003-FREEZE-AUTH-01 (manifests/cs-003-freeze-v1.yaml; the five design points DP-1 to DP-5 were decided by the human research lead as recommended), and CS-004 (experiments/scenario-mappings/CS-004.yaml), FROZEN on 2026-11-06 under the authorization id E02-CS004-FREEZE-AUTH-01 (manifests/cs-004-freeze-v1.yaml): WEB only, SUT-01, SUT-02 and SUT-03 COMPARABLE, the other three SUTs NOT_COMPARABLE; the checkout selectors of SUT-02 and SUT-03 were read from the pinned sources on 2026-11-06 and exercised by the environment-verification DRY_RUNs of 2026-11-09. experiments/scenario-mappings/CS-001.yaml is scoped to E03-resetability and is not reused. The campaign configuration above is locked.

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
