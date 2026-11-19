# E04 — Repeatability

## Objective

Reproduce a target state repeatedly under a fixed condition in each evaluated ecosystem (each a system under test, SUT) and measure how often the reproduction succeeds. The repetition target is N = 50 attempts per repeatable condition; N = 30 may be used for expensive mobile conditions only when a justification is recorded before that campaign executes (see protocol/repeatability-determinism-v1.md). Every attempt is recorded; no attempt may be discarded. Attempts run on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance (protocol/study-design-v1.md, section 10.3). Between-ecosystem comparison of TSRR (Target-State Reproduction Rate) is made only on canonical scenarios with FROZEN mapping records (protocol/equivalent-scenario-mapping-v1.md) and is classified CONFIRMATORY or EXPLORATORY per protocol/statistical-analysis-plan-v1.md, section 4. The tooling-versus-SUT attribution rule for deviations is DEFERRED-BEFORE-CAMPAIGN and is locked in the campaign configuration (protocol/study-design-v1.md, section 13, issue (xix)).

## Related research question(s)

- RQ3 Repeatability and Determinism (primary).
- Informs dimension 3 Repeatability and Determinism.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Condition (a target state plus its establishment procedure, from the catalogue defined before freeze) — candidate.
- Surface (web / api / android / ios) — candidate.

## Future dependent variables (candidate — not frozen)

- TSRR — Target-State Reproduction Rate (successful target-state establishments / all valid measured attempts) with a Wilson confidence interval, per protocol/repeatability-determinism-v1.md, section 4 — candidate.
- Failure classification per unsuccessful attempt (taxonomy TBD before freeze) — candidate.

## Required evidence

- One run manifest per attempt conforming to schemas/run-manifest.schema.json, including attempt index, ecosystem id, condition id, surface, `environment_type`, and outcome.
- Verification artifact per attempt showing whether the target state was reached.
- Pre-execution record of N for each condition, including the justification if N = 30 is used for a mobile condition.
- Complete attempt sequence with no discarded attempts; aborted or interrupted attempts are recorded as such with a reason.
- Raw observations in `raw-data/E04-repeatability/`.

## Current status

FROZEN since the campaign freeze of 2026-11-18 (human authorization E04-FREEZE-AUTH-01; protocol/change-control-v1.md, section 7, moment 2; record manifests/e04-campaign-freeze-v1.yaml), after IN PROGRESS from the campaign START of 2026-11-18 (E04-START-AUTH-01; record manifests/e04-campaign-start-v1.yaml). The 650 executions (thirteen web/api conditions, N = 50 each, all attempt 1) were imported unchanged under raw-data/E04-repeatability/ on 2026-11-18 within the four dispatch authorizations E04-DISPATCH-SUT01-AUTH-01, -SUT02-, -SUT04- and -SUT05-AUTH-01 (dispatch records manifests/e04-measured-dispatch/e04-sut0N.jsonl); raw-data/E04-repeatability/ is append-only and the "Campaign configuration" section below is immutable. The raw data are not yet published and the TSRR is not analyzed.

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.

## Campaign configuration

This record is the "Campaign configuration" of E04-repeatability. It is locked at the campaign START (protocol/change-control-v1.md, section 7, moment 1) under the human authorization named below, and it is immutable from then on; a change after the START is a change-control row recorded before the affected execution. It authorizes no dispatch: each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) is issued separately by the human research lead. The design record is experiments/E04-repeatability/design-notes-draft.md; the executor is experiments/E04-repeatability/executor/. The working defaults of that design record are the values of this text; each is marked where it is a proposal that the human research lead confirms or changes at the START, and this text is then re-prepared (with new hashes) if any value changes. A system under test (SUT) is one of the evaluated ecosystems of README.md.

### Identity and START

- Campaign: E04-repeatability. Design: minimal, establishment-only (decision D-20, option (b), manifests/campaign-execution-decisions-v4.yaml). Each execution establishes the target state of the condition and verifies it; no stimulus is sent and no outcome is classified. The primary metric is TSRR (see "Blocks, outcome categories and TSRR"). No hypothesis label applies: H3 is an E05 hypothesis and is not tested by this campaign.
- START authorization id: E04-START-AUTH-01 (proposed; the human research lead confirms the id at the START). The START row of protocol/CHANGELOG.md names it.
- Protocol: v1 FROZEN-PRE-DATA (protocol/repeatability-determinism-v1.md, sections 4 and 5, applied unchanged). Agent governance: protocol/agent-governance-v6.md, sha256 c890a9d004b2989aa9ae33a54bc68b000c47fc9e3f79d60ad0051de78b3f2a4a, FROZEN-PRE-DATA since 2026-11-06, Sections 3.6 and 3.7.
- Execution: GitHub Actions only (CAMPAIGN-CI-WRITE-AUTH-01), through .github/workflows/e04-measured-execution.yml, dispatched by the ORCHESTRATOR under dispatch authorizations. Attempt 1 only under the authorization; a further attempt only under a recorded further-attempt approval (gate G-E04-A2); default branch only; no GitHub re-run.
- Measured workflow file sha256 17a526f14c21d7c1b0491373763962f749748fbc37aa26fc6cf1be3c8e215ad2 (gate G-9 reads this hash from this record). Verification workflow file sha256 4bf2d2ad84bda6084f9282b53fabfc0d5f51160d3b467a362ecda3e3f5c4f396 (provenance only; the verification workflow has no START gate, as in E05).

### Scenario mapping

- The target states are those of the canonical scenario CS-001 (experiments/scenario-mappings/CS-001.yaml, sha256 e251e3825ebbbe3aa1a0f3fee8a30131fa1e0910161ae583a09cb34d9f1cc583, mapping_status FROZEN, E03-CS001-FREEZE-AUTH-01). No new canonical scenario and no new mapping record are used. No cross-ecosystem comparison is made.

### Pinned versions

- SUT-01 web: OmniPizza at commit 9ca37674d374e9303912e259641ee86baf3aabe1; SUT-01 api: OmniPizza at commit 9ca37674d374e9303912e259641ee86baf3aabe1 (no release). SUT-02 web: saucelabs/sample-app-web at commit 60fdd634bb111c092282fa07977513a0a7765593 (no release). SUT-04 api: restful-booker-platform at commit d36bd3f8647a091d406e53bad463c5e3e5d2ece1 (release 2.2); SUT-04 web: the same commit and release. SUT-05 api: juice-shop at commit 1618a611b173b4bf114028e6e02549950606e29d (release v20.2.0, the packaged distribution). Source: manifests/sut-manifest.yaml, sha256 7f954c958f5558729ff9be23b9bea1471d205e43baf0f461ccb08f7984cf2d58.
- Web runner: Playwright for Python 1.63.0 with the hashed requirements of experiments/E04-repeatability/executor/requirements.txt, sha256 35b65ea4c57a3bc1ddccaab846bab0b986ff76de8b09ac69d2455fedf04dfb4b. Browser: the Chromium build named by Playwright 1.63.0, not hash-pinned by the study.
- Run-manifest schema: schemas/run-manifest.schema.v2.json, sha256 9a86cf37c4ccd2abe3368866309e18a9f9554a2330f5dceeacda6d02a2932757.
- Reference values of the runner, Python, Node.js and browser versions: not recorded in the round 1 record; TBD before the first dispatch. They are recorded per job in tool-versions.json and are never a gate.

### Prompt version and implementation

- Dispatch procedure prompt: ORCHESTRATOR-E04-repeatability-v1. Working copy: prompts/working/ORCHESTRATOR-E04-repeatability-v1.md, sha256 65a1a818e87b0ad95587b5c2d2f5a2af6e958cff0692d941c09f0b895b7928e9. The frozen copy prompts/frozen/ORCHESTRATOR-E04-repeatability-v1.md is written once at the START as a byte-identical copy of the working copy (prompts/README.md, rules 1 to 3); it is not written by this text.
- Implementation hash (sha256 of experiments/E04-repeatability/executor/run-condition.sh, which embeds the digests of the executor Python files and of requirements.txt and refuses an unlisted file): e7a8986fe2e5f8b5f3a55131b13eaf0411085aca224b45e12e4772e14e39dc4d. This is the implementation that ran in the first non-measured environment-verification round (run 44331428884).
- Conditions file: experiments/E04-repeatability/conditions-draft.json, sha256 5964b23592174ce4fe3dea76c446db7eb3239afa1fef04875cb8dcfb3939d562 (thirteen conditions; read by the executor). The conditions file is hashed here at the START.

### Conditions (13)

All conditions: N = 50 executions, EX0001 to EX0050, attempt 1, environment_type SELF_HOSTED (a controlled instance provisioned in the job from the pinned commit on a GitHub-hosted runner, never PUBLIC_HOSTED), target state CS-001, expected category TARGET_STATE_VERIFIED. Each condition mirrors the E05 condition of the same SUT, surface, account and reset (experiments/E05-determinism/conditions-draft.json; the mirror is the condition identifier with E04 in place of E05).

| Condition | Account | Reset between attempts | Starting-state check | Establishment (target state) | Target-state verification | Note |
|---|---|---|---|---|---|---|
| E04-SUT01-API-01 | standard_user | restart of the backend process (ENVIRONMENT_RESTART; SIGTERM to the process group, port refused, start in a new session, readiness) | GET /api/session: the server cart is empty | POST /api/cart with one line (pizza_id p02, quantity 1) | GET /api/session shows exactly that line | blocks identical to E04-SUT01-API-06 (restart and cart line); the accounts differ |
| E04-SUT01-API-02 | standard_user | session clear through the API (API_RESET, SESSION_RESET) | GET /api/session: the server cart is empty | POST /api/cart with one line (pizza_id p02, quantity 1) | GET /api/session shows exactly that line | blocks identical to E04-SUT01-API-03, -04 and -05 (session clear and cart line); the accounts differ |
| E04-SUT01-API-03 | standard_user | session clear through the API (API_RESET, SESSION_RESET) | GET /api/session: the server cart is empty | POST /api/cart with one line (pizza_id p02, quantity 1) | GET /api/session shows exactly that line | blocks identical to E04-SUT01-API-02, -04 and -05; the accounts differ |
| E04-SUT01-API-04 | performance_glitch_user | session clear through the API (API_RESET, SESSION_RESET) | GET /api/session: the server cart is empty | POST /api/cart with one line (pizza_id p02, quantity 1) | GET /api/session shows exactly that line | blocks identical to E04-SUT01-API-02, -03 and -05; the accounts differ |
| E04-SUT01-API-05 | a11y_glitch_user | session clear through the API (API_RESET, SESSION_RESET) | GET /api/session: the server cart is empty | POST /api/cart with one line (pizza_id p02, quantity 1) | GET /api/session shows exactly that line | blocks identical to E04-SUT01-API-02, -03 and -04; the accounts differ |
| E04-SUT01-API-06 | error_user | restart of the backend process (ENVIRONMENT_RESTART; SIGTERM to the process group, port refused, start in a new session, readiness) | GET /api/session: the server cart is empty | POST /api/cart with one line (pizza_id p02, quantity 1) | GET /api/session shows exactly that line | blocks identical to E04-SUT01-API-01 (restart and cart line); the accounts differ |
| E04-SUT01-WEB-01 | standard_user | restart of the backend process (ENVIRONMENT_RESTART; SIGTERM to the process group, port refused, start in a new session, readiness) | GET /api/session: the server cart is empty, and the client cart holds no item | navigation to the Checkout route (DIRECT_ROUTE) after the client state of the E03 realization W-A is injected | the Checkout view shows the order item p02 (data-testid order-item-p02) | no identical block in this configuration |
| E04-SUT02-WEB-01 | standard_user | 'Reset App State' in the side drawer of the application (APP_DATA_CLEAR) | the cart link reads 'Cart, empty' with no badge | load the inventory page and click the first item add-to-cart control | the cart badge reads 1 | no identical block in this configuration |
| E04-SUT04-WEB-01 | admin | deletion of the room 1 bookings that carry the condition's guest names, through the admin web control (API_RESET) | room 1 holds no booking with the condition's guest names | booking through the web form of the reservation route with the condition guest names and dates; confirmation shown | the admin room page lists exactly one row with the condition's guest names | no identical block in this configuration |
| E04-SUT04-API-01 | admin | deletion of the room 1 bookings that carry the condition's guest names, through the booking API (API_RESET) | room 1 holds no booking with the condition's guest names | POST /booking/ for room 1 with the condition guest names, without email or phone | GET /booking/{id} answers 200 | no identical block in this configuration |
| E04-SUT04-API-02 | admin | deletion of the room 1 bookings that carry the condition's guest names, through the booking API (API_RESET); the names of the E05 stimulus booking are kept in the reset so that it is unchanged | room 1 holds no booking with the condition's guest names | POST /booking/ for room 1 with the condition guest names, without email or phone | GET /booking/{id} answers 200; the message count GET {message}/message/count answers with a count (the baseline of the E05 stimulus; open item) | the message-count read of the verification block is the baseline of the E05 stimulus; kept as part of the E05 verification block (open item) |
| E04-SUT05-API-01 | documented_account | restart of the SUT process (ENVIRONMENT_RESTART; SIGTERM to the process group, port refused, start in a new session, readiness) | the documented account's basket holds no item | POST /api/BasketItems with ProductId 1 for the basket of the documented account | GET /rest/basket/{bid} shows ProductId 1 | blocks identical to E04-SUT05-API-02 (restart and basket line); both accounts are the documented account |
| E04-SUT05-API-02 | documented_account | restart of the SUT process (ENVIRONMENT_RESTART; SIGTERM to the process group, port refused, start in a new session, readiness) | the documented account's basket holds no item | POST /api/BasketItems with ProductId 1 for the basket of the documented account | GET /rest/basket/{bid} shows ProductId 1 | blocks identical to E04-SUT05-API-01 (restart and basket line); both accounts are the documented account |

Notes. The identical-block groups were derived from the executor code by comparing, for each condition, the four block methods as resolved through inheritance, the mechanisms and components of the realization, and the reset kind (fields block_group and identical_blocks_with of experiments/E04-repeatability/conditions-draft.json): E04-SUT01-API-01 with E04-SUT01-API-06 (restart of the backend process; the accounts differ); E04-SUT01-API-02, E04-SUT01-API-03, E04-SUT01-API-04 and E04-SUT01-API-05 (session clear through the API; the accounts differ); E04-SUT05-API-01 with E04-SUT05-API-02 (restart of the SUT process; the same documented account). The SUT-01 API conditions share one inherited code path, and the reset kind selects the restart or the session-clear branch. No other pair of conditions runs identical blocks. All thirteen conditions are kept as separate conditions, as the one-to-one mirror of E05 requires; the notes are part of the proposal and are confirmed at the START. E05-SUT02-WEB-02 is not mirrored: it was retired before the E05 START.

### Blocks, outcome categories and TSRR

- Block order of every execution: reset; starting-state check; establishment; target-state verification; record. There is no stimulus block and no classification block.
- A block that does not hold stops that execution with its category; the job goes on with the next execution. Only a failure of the job itself stops the job.
- Outcome categories (declared before any execution, in experiments/E04-repeatability/conditions-draft.json): TARGET_STATE_VERIFIED (status SUCCESS; every block held); RESET_FAILED (status ABORTED); RESET_STARTING_STATE_NOT_REACHED (status ABORTED, with its cause); ESTABLISHMENT_FAILED (status ABORTED); ESTABLISHMENT_VERIFICATION_FAILED (status ABORTED); ESTABLISHMENT_INTERRUPTED (status ABORTED; an interruption of the establishment or verification block, attributed TOOLING); STUB_NO_BUNDLE (status ERROR; an execution that began and left no bundle, counted in T, attributed SUT). The expected category of every condition is TARGET_STATE_VERIFIED.
- TSRR (primary, protocol/repeatability-determinism-v1.md, section 4): TSRR = successful target-state establishments / all valid measured attempts. The numerator is the executions with TARGET_STATE_VERIFIED; the denominator is every valid measured attempt of the condition, including the ABORTED, ERROR and interrupted ones. TSRR is computed per condition. If no valid measured attempt exists, TSRR is not estimable and is reported as such, never as 0.

### Attribution and exclusion rules

- No attempt is excluded from any denominator (protocol/repeatability-determinism-v1.md, section 5, rules 4 and 5). An attempt whose starting-state check fails is recorded as ABORTED with its cause, is counted in T, and the job goes on.
- Attribution (issue (xix), decision D-16, option B, adapted; the working attribution confirmed by the human research lead on 2026-11-17): TOOLING for every interruption of a block, that is a runner or client exception, a browser or client crash or disconnect, or the per-execution watchdog, in any block and whatever responses the system under test returned earlier in the execution. SUT for every recorded failure of a block (a non-2xx answer, a state that did not hold) and for every attempt whose cause cannot be assigned mechanically.
- The response-boundary clause of the design default (an exception after a response of the system under test is SUT) is NOT adopted in this text (proposal; confirmed or changed at the START). The executor implements the rule above only.
- A runner cancelled or lost by the workflow leaves an incomplete bundle; the proposal is that the ORCHESTRATOR records such an execution at import as TOOLING of that execution (proposal; not implemented by the executor; confirmed at the START).
- Attribution is mechanical and fixed here; it is never applied after seeing a result pattern. Attributed counts (TOOLING and SUT per category) are reported beside the raw TSRR; the raw TSRR is never recomputed on the attributed counts.
- The executor scrubs host paths and private network addresses from every kept text file (the executor's scrubber); no secret is recorded.

### Sample size, order and dispatch model

- N = 50 executions per condition: 650 executions in all, SUT-01 350 (seven conditions), SUT-02 50 (one), SUT-04 150 (three), SUT-05 100 (two); thirteen dispatches, one per condition, one job per dispatch, attempt 1.
- Model: one job runs the 50 executions of one condition sequentially on one shared instance (the model B of E05, decision D-02, carried over as a proposal); the reset of the condition runs at the start of every execution, and the starting-state check follows it in every execution.
- Dispatch order (proposal, fixed here before the first dispatch): SUT-01: E04-SUT01-API-01, API-02, API-03, API-04, API-05, API-06, WEB-01; SUT-02: E04-SUT02-WEB-01; SUT-04: E04-SUT04-API-01, API-02, WEB-01; SUT-05: E04-SUT05-API-01, API-02. The conditions of one SUT run one at a time, a dispatch only after the previous run of its authorization has concluded and been imported; the chains of different SUTs are independent and may run concurrently.
- Dispatch records (append-only, committed before each dispatch; the run identity is appended after it starts): manifests/e04-measured-dispatch/e04-sut01.jsonl, e04-sut02.jsonl, e04-sut04.jsonl and e04-sut05.jsonl, created at the first dispatch of each SUT, not at the START.
- Identifiers: execution_id EX0001 to EX0050; attempt A1; run_id <condition_id>__<execution_id>__A<attempt>.
- Import: byte-exact under raw-data/E04-repeatability/<SUT>/ after the verification of every archive against its GitHub digest: each executions/<run_id>/ directory becomes raw-data/E04-repeatability/<SUT>/<run_id>/; the job files are kept in raw-data/E04-repeatability/<SUT>/<condition_id>__job__A<attempt>/.
- Stop conditions: the frozen dispatch procedure (prompts/frozen/ORCHESTRATOR-E04-repeatability-v1.md, section 4) applies: the gate job of a run fails; a run's conclusion is other than success or a failure of the measured job; an artifact does not hold exactly the 50 run manifests of its condition; an input differs from this text, the authorization or the public repository; a boundary of the procedure would be crossed; the authorization is revoked or the human research lead stops the campaign. On a stop nothing further is dispatched in this campaign under any authorization until the human research lead instructs otherwise.

### Dispatch authorization and further attempts

- One dispatch authorization per SUT, issued separately by the human research lead under protocol/agent-governance-v6.md, Section 3.7: E04-DISPATCH-SUT01-AUTH-01 (SUT-01, seven conditions), E04-DISPATCH-SUT02-AUTH-01 (SUT-02, one condition), E04-DISPATCH-SUT04-AUTH-01 (SUT-04, three conditions), E04-DISPATCH-SUT05-AUTH-01 (SUT-05, two conditions). Each names the conditions of its SUT, N = 50, attempt 1, the implementation hash and the prompt hash above, and the authorization id of this START. The START authorizes no dispatch authorization.
- Further attempt (attempt 2 or more, from a first execution named by the approval): only under a further-attempt approval of the human research lead that names the condition, the first execution and the attempt (gate G-E04-A2; the approval record is manifests/e04-further-attempt-approval-sut0N-v1.yaml, created only when approved). Nothing is re-run; the failed or interrupted executions of the first attempt keep their recorded outcomes.

### Controlled instances

- Controlled-instance record: experiments/E04-repeatability/controlled-instance-status.yaml, written at the START from the prepared content. Every condition is CONTROLLED: its status is VERIFIED on GitHub Actions by the non-measured DRY_RUN round 1 of .github/workflows/e04-environment-verification.yml (run 44331428884; 2 executions per condition; all 26 executions TARGET_STATE_VERIFIED; record manifests/e04-environment-verification-rounds-v1.yaml, sha256 7c25a6db09a64c47cbcb11e60438655d70e5cf29a0947562dddda1c8b0b1ff93). The round is the only one recorded at the time of this text. DRY_RUN bundles are never measured and never imported.

### Analysis (TSRR) and what is not computed

- Per condition: T (valid measured attempts), S (TARGET_STATE_VERIFIED executions), TSRR = S / T with the Wilson 95 percent interval without continuity correction (the repository convention stated in experiments/E05-determinism/README.md, "Metrics"); the attributed counts (TOOLING and SUT per category) beside it. Descriptive only.
- The analysis is run only on a separate instruction of the human research lead, after the campaign is frozen, with its own derived dataset (derived-data/README.md; analysis/README.md).
- Not computed, not compared, not pooled: no between-ecosystem comparison; no pooled rate across conditions or ecosystems; no composite score; no CEOR; no E2E-ROR; no Outcome Entropy; no H3 evaluation.

### Gates the measured workflow enforces

The measured job starts only if the gate step of .github/workflows/e04-measured-execution.yml passes: the campaign status is IN_PROGRESS in manifests/study-manifest.yaml; exactly one START row of protocol/CHANGELOG.md names this campaign README and the START authorization id; the START record manifests/e04-campaign-start-v1.yaml names the campaign and the authorization id; this section names the condition, the schema, the prompt version, the implementation hash, the conditions-file hash, the measured workflow hash (G-9), N = 50, CS-001, TSRR, the pinned commits of the assigned SUT and, for a release, the release; the dispatch authorization of the assigned SUT is ISSUED, VALID, ELIGIBLE, not revoked, issued by the human research lead, and names the condition, N = 50, attempt 1, the START id and the two hashes; the frozen prompt file exists and matches its hash; the further-attempt approval (G-E04-A2) when the attempt is above 1; agent-governance-v6 is in force with Section 3.7; the run-manifest schema v2 is present; the controlled-instance status of the condition is CONTROLLED, its GitHub Actions verification is VERIFIED, no reverification is required, and the environment type is SELF_HOSTED; the CS-001 mapping is FROZEN with an entry for the assigned SUT; the executor implementation equals the locked hash. The job also refuses a GitHub re-run (github.run_attempt must be 1) and any branch other than the default branch.

### Change log

- None at the time of this text. Any change after the START is a change-control row (protocol/change-control-v1.md) recorded before the affected execution; results collected before a change are analyzed under the configuration in force when they were collected.
