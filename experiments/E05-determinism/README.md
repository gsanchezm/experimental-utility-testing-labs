# E05 — Determinism

## Objective

Execute a controlled condition together with a fixed stimulus repeatedly in each evaluated ecosystem (each a system under test, SUT) and classify the observed outcome of each execution into categories defined before execution. The campaign measures whether identical inputs yield identical observable outcomes and characterizes the sources of variation where they do not. Outcome categories must be fixed and recorded before any execution to prevent post hoc classification. Executions run on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance (protocol/study-design-v1.md, section 10.3). Determinism is measured with two rates plus entropy (protocol/repeatability-determinism-v1.md, section 4): CEOR (Conditional Exact Outcome Rate, denominator restricted to executions whose target-state establishment succeeded; NOT_ESTIMABLE, never 0, when none did) and E2E-ROR (End-to-End Reproducible Outcome Rate, denominator = all valid measured attempts); this resolves the former Exact Outcome Rate denominator question (issue (xi), RESOLVED). H3's criterion is fixed as CEOR = 1.00 and Outcome Entropy H(Y) = 0 for conditions classified a priori as deterministic (issue (xx), RESOLVED). The tooling-versus-SUT attribution rule remains DEFERRED-BEFORE-CAMPAIGN (issue (xix)).

## Related research question(s)

- RQ3 Repeatability and Determinism (primary).
- Informs dimension 3 Repeatability and Determinism.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Condition (controlled state plus stimulus, from the catalogue defined before freeze) — candidate.
- Behavior class of the condition, as declared before execution: deterministic / stochastic / time-dependent / external dependency — candidate.

## Future dependent variables (candidate — not frozen)

- CEOR — Conditional Exact Outcome Rate (executions whose outcome category equals the pre-declared expected outcome category / executions in which the required target state was successfully established; NOT_ESTIMABLE, never 0, when no attempt establishes the target state; never derived from the observed modal outcome), per protocol/repeatability-determinism-v1.md, section 4 — candidate.
- E2E-ROR — End-to-End Reproducible Outcome Rate (executions whose outcome category equals the pre-declared expected outcome category / all valid measured attempts), per protocol/repeatability-determinism-v1.md, section 4 (secondary) — candidate.
- Outcome Entropy over the observed outcome categories, computed over the same execution set as CEOR (secondary) — candidate.
- Count of distinct outcome categories observed — candidate.

## Required evidence

- Outcome category definitions recorded before execution, with the criteria for assigning each category.
- One record per execution (attempt), each with a run manifest conforming to schemas/run-manifest.schema.json, including ecosystem id, condition id (`condition`), declared behavior class (`behavior_class`), attempt index (`attempt`), `environment_type`, and assigned outcome category (`outcome.outcome_category`).
- Raw observation artifact per execution supporting the assigned category (for example response body, screenshot, or log excerpt; form TBD before freeze).
- Repetition count per condition per protocol/repeatability-determinism-v1.md, recorded before execution.
- Raw observations in `raw-data/E05-determinism/`.

## Current status

FROZEN since 2026-11-16 (human authorization E05-FREEZE-AUTH-01; protocol/change-control-v1.md, section 7, moment 2; record manifests/e05-campaign-freeze-v1.yaml), after being IN PROGRESS from the campaign START of 2026-11-16 (human authorization E05-START-AUTH-01; protocol/change-control-v1.md, section 7, moment 1; record manifests/e05-campaign-start-v1.yaml). The "Campaign configuration" section below is locked and immutable. The START authorized no dispatch and no dispatch authorization; each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) was issued separately by the human research lead (E05-DISPATCH-SUT01-AUTH-01, -SUT02-, -SUT04- and -SUT05-AUTH-01; records manifests/e05-dispatch-authorization-sut0N-v1.yaml).

Dispatch concluded on 2026-11-17 UTC (operation OP-DISPATCH-E05-02, within those four dispatch authorizations; records manifests/e05-measured-dispatch/e05-sut0N.jsonl): the ORCHESTRATOR dispatched and imported the 650 planned executions, thirteen conditions of 50 executions each (SUT-01 seven, SUT-02 one, SUT-04 three, SUT-05 two), all attempt 1, as 13 dispatches, one per condition, from the first run at 2026-11-17T03:10:42Z to the last import, which its dispatch-record event dates 2026-11-17T03:43:21Z. Each bundle was verified against its GitHub digest and imported byte-exact under raw-data/E05-determinism/<SUT>/; in every one of the 13 runs the workflow concluded success. No stop condition of the dispatch prompt occurred and no attempt was repeated. The campaign is frozen (the freeze had its own explicit human authorization, protocol/change-control-v1.md, section 7, moment 2), published by export v64 on 2026-11-17, and analyzed descriptively for H3 on 2026-11-17 (derived-data/h3-analysis/H3-e05-result.json and derived-data/E05-determinism/outcomes-per-attempt.csv; the Campaign configuration below is unchanged).

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.

## Campaign configuration

This record is the "Campaign configuration" of E05-determinism. It is locked at the campaign START (protocol/change-control-v1.md, section 7, moment 1) under the human authorization named below, and is immutable from then on; a change after the START is a change-control row recorded before the affected execution. It authorizes no dispatch: each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) is issued separately by the human research lead. The decisions D-01 to D-20 and the decisions of 2026-11-14 are recorded in manifests/campaign-execution-decisions-v4.yaml to -v9.yaml; the design is in experiments/E05-determinism/design-brief-draft.md and its configuration draft. A system under test (SUT) is one of the evaluated ecosystems of README.md.

### Identity and START

- Campaign: E05-determinism. Hypothesis label: H3 (protocol/statistical-analysis-plan-v1.md, section 4.3; protocol/study-design-v1.md, section 6, note (d)): a single-ecosystem prediction for the SUT-01 conditions classified a priori as deterministic (CEOR = 1.00 and Outcome Entropy H(Y) = 0). The same metrics are computed for the deterministic conditions of every ecosystem and are descriptive for them.
- START authorization id: E05-START-AUTH-01 (the human research lead's explicit approval of the START; the change-log row of protocol/CHANGELOG.md names it).
- Protocol: v1 FROZEN-PRE-DATA (protocol/study-design-v1.md; protocol/repeatability-determinism-v1.md; protocol/statistical-analysis-plan-v1.md; protocol/cross-cutting-properties-v1.md). Agent governance: protocol/agent-governance-v6.md, FROZEN-PRE-DATA since 2026-11-06 (Sections 3.6 and 3.7).
- Execution: GitHub Actions only (CAMPAIGN-CI-WRITE-AUTH-01), through .github/workflows/e05-measured-execution.yml, by the ORCHESTRATOR under dispatch authorizations; attempt 1 under the authorization, a further attempt only under a recorded further-attempt approval (gate G-E05-A2), default branch only, no GitHub re-run. Workflow file sha256 df04c65f777754ce3dd85358c0751b8bb80205838ada99041cb6bef4f5687afd (gate G-9 reads it from this record).

### Scenario mapping (D-17)

- The target states are those of the canonical scenario CS-001 (experiments/scenario-mappings/CS-001.yaml, sha256 e251e3825ebbbe3aa1a0f3fee8a30131fa1e0910161ae583a09cb34d9f1cc583, mapping_status FROZEN, E03-CS001-FREEZE-AUTH-01, 2026-09-21); no new canonical scenario and no new mapping record. E05 makes no cross-ecosystem comparison of rates that needs a further mapping.

### Pinned versions

- SUT-01 web and api: https://github.com/gsanchezm/OmniPizza at commit 9ca37674d374e9303912e259641ee86baf3aabe1 (no release). SUT-02 web: https://github.com/saucelabs/sample-app-web at commit 60fdd634bb111c092282fa07977513a0a7765593. SUT-04 web and api: https://github.com/mwinteringham/restful-booker-platform at commit d36bd3f8647a091d406e53bad463c5e3e5d2ece1, release 2.2. SUT-05 api: https://github.com/juice-shop/juice-shop at commit 1618a611b173b4bf114028e6e02549950606e29d, release v20.2.0 (the packaged distribution). Source: manifests/sut-manifest.yaml. SUT-03 and SUT-06 have no condition (SUT-03: no E05 condition proposed; SUT-06: NOT_COMPARABLE on CS-001).
- Run-manifest schema: schemas/run-manifest.schema.v2.json, sha256 9a86cf37c4ccd2abe3368866309e18a9f9554a2330f5dceeacda6d02a2932757.
- Web runner: Playwright for Python 1.63.0 with the hashed requirements of experiments/E05-determinism/executor/requirements.txt (an E05 lock of its own). Browser: the Chromium build named by Playwright 1.63.0, not hash-pinned by the study; reference value 153.0.8010.12, recorded in every execution (tool-versions file).
- Reference values read from the DRY_RUN rounds (decision of 2026-11-14, manifests/campaign-execution-decisions-v9.yaml); drift is recorded per job and is not a gate: runner ubuntu-24.04 (ImageOS ubuntu24, image version 20261111.370.1 in round 2); system Python 3.12.3 and executor Python 3.12.16; Node.js v22.23.4; SUT-04 provisioning with Temurin-26.0.2.1+1 and Apache Maven 3.9.14; manifest validation with ajv-cli 5.0.0 and ajv-formats 3.0.1 (resolved from the majors the workflow names, npm registry, 2026-11-14).
- Analysis runtime: recorded in the derived-data record when the H3 loader is written after the data freeze (the pure core is analysis/h3-analysis/h3-metrics.js); its name, version and hash are set then.

### Prompt version and implementation

- Dispatch procedure prompt: ORCHESTRATOR-E05-determinism-v1, frozen at the START as prompts/frozen/ORCHESTRATOR-E05-determinism-v1.md, a byte-identical copy of prompts/working/ORCHESTRATOR-E05-determinism-v1.md, sha256 c094e62471fe3142bb5210ee18f598615a026b898632091f0194f1b72737879e.
- Implementation hash (sha256 of experiments/E05-determinism/executor/run-condition.sh, which embeds the digests of the executor files and refuses an unlisted one): bade00d2a45e69da3b25707e6c00cd84d892c15ccdf0bf69485ae8f3570f9ac0. This is the implementation that ran complete on GitHub Actions in the second and third environment-verification rounds.
- Conditions file: experiments/E05-determinism/conditions-draft.json, sha256 40b226610904f339a7e40d90ffeaf6e4d0ddb8862f6adba4cc2cf5efc2923eb8 (categories, expected categories, classes, k, reset kind, minimum S for H3; read by the executor and by the analysis).
- agent_role in run manifests: ORCHESTRATOR.

### Conditions (13; E05-SUT02-WEB-02 retired before the START, decision of 2026-11-14)

All conditions: N = 50, environment_type SELF_HOSTED (a controlled instance provisioned in the job from the pinned commit on a GitHub-hosted runner, never PUBLIC_HOSTED), target state CS-001, seed null.

| Condition | SUT, surface | Account | Declared behavior class | H3 label | Expected category | Categories | Reset between attempts |
|---|---|---|---|---|---|---|---|
| E05-SUT01-API-01 | SUT-01 api | standard_user | deterministic | yes | S_ORDER_TOTAL_MATCH | S_ORDER_TOTAL_MATCH, S_ORDER_TOTAL_MISMATCH, S_HTTP_NON_200, INTERRUPTED_ (k = 4) | restart of the backend process |
| E05-SUT01-API-02 | SUT-01 api | standard_user | deterministic | yes | S_CATALOG_MATCH | S_CATALOG_MATCH, S_CATALOG_MISMATCH, S_HTTP_NON_200, INTERRUPTED_ (k = 4) | session clear through the API |
| E05-SUT01-API-03 | SUT-01 api | standard_user | deterministic | yes | S_LOCKOUT_403_EXACT_MESSAGE | S_LOCKOUT_403_EXACT_MESSAGE, S_OTHER_STATUS_OR_BODY, INTERRUPTED_ (k = 3) | session clear through the API |
| E05-SUT01-API-04 | SUT-01 api | performance_glitch_user | deterministic | yes | S_CONTENT_MATCH_200 | S_CONTENT_MATCH_200, S_CONTENT_MISMATCH, S_HTTP_NON_200, S_CLIENT_TIMEOUT, INTERRUPTED_ (k = 5) | session clear through the API |
| E05-SUT01-API-05 | SUT-01 api | a11y_glitch_user | stochastic | no | S_MODE_MISSING_NAME | S_MODE_MISSING_NAME, S_MODE_WRONG_LANG, S_MODE_EXTREME_TEXT, S_OTHER, INTERRUPTED_ (k = 5) | session clear through the API |
| E05-SUT01-API-06 | SUT-01 api | error_user | stochastic | no | S_ORDER_CREATED | S_ORDER_CREATED, S_HTTP_500, S_OTHER, INTERRUPTED_ (k = 4) | restart of the backend process |
| E05-SUT01-WEB-01 | SUT-01 web | standard_user | deterministic | yes | S_ORDER_CONFIRMED | S_ORDER_CONFIRMED, S_VALIDATION_MESSAGE, S_HTTP_ERROR_VISIBLE, S_OTHER_VIEW, INTERRUPTED_ (k = 5) | restart of the backend process |
| E05-SUT02-WEB-01 | SUT-02 web | standard_user | deterministic | no | S_BADGE_2 | S_BADGE_2, S_BADGE_OTHER, S_NO_CHANGE, INTERRUPTED_ (k = 4) | 'Reset App State' of the application |
| E05-SUT04-WEB-01 | SUT-04 web | admin | deterministic | no | S_NO_CONFIRMATION_SHOWN | S_NO_CONFIRMATION_SHOWN, S_BOOKING_CONFIRMED, S_OTHER, INTERRUPTED_ (k = 4) | deletion of the booking through the delete control |
| E05-SUT04-API-01 | SUT-04 api | admin | deterministic | no | S_CONFLICT_REJECTED | S_CONFLICT_REJECTED, S_CREATED_UNEXPECTED, S_OTHER_STATUS, INTERRUPTED_ (k = 4) | deletion of the condition bookings through the API |
| E05-SUT04-API-02 | SUT-04 api | admin | external dependency | no | S_MESSAGE_RECORD_PRESENT | S_MESSAGE_RECORD_PRESENT, S_MESSAGE_RECORD_ABSENT, S_BOOKING_NON_2XX, S_OTHER, INTERRUPTED_ (k = 5) | deletion of the condition bookings and of the stimulus booking by the id of the 201 response |
| E05-SUT05-API-01 | SUT-05 api | documented_account | deterministic | no | S_REJECTED_AS_EXPECTED | S_REJECTED_AS_EXPECTED, S_ACCEPTED_UNEXPECTED, S_OTHER, INTERRUPTED_ (k = 4) | restart of the process |
| E05-SUT05-API-02 | SUT-05 api | documented_account | stochastic | no | S_CAPTCHA_ISSUED | S_CAPTCHA_ISSUED, S_CAPTCHA_NOT_ISSUED, S_OTHER, INTERRUPTED_ (k = 4) | restart of the process |

- Phase prefixes of every category: S_ (stimulus outcome), INTERRUPTED_, ESTABLISHMENT_ and RESET_; ESTABLISHMENT_ and RESET_ labels are outside the CEOR denominator. A label outside a condition's set is mapped to the catch-all that the condition declares (the first of its categories, in this order of preference, that starts with S_OTHER, ends in _OTHER, or ends in MISMATCH) with the original label in the note of the attempt, and is never dropped.
- E05-SUT01-API-04: client timeout 30 s (ten times the fixed 3.0 s delay). E05-SUT04-API-02: the stimulus is an accepted booking that persists; its reset deletes it by the id of the 201 response; the message record kept by the message service is declared residual state; the instance runs the real message service. The other two SUT-04 conditions are rejected-only stimuli.
- Expected categories were written before the START from documentation or source and never from an observed run (protocol/repeatability-determinism-v1.md, section 4). For the stochastic and external conditions, one pre-declared category with CEOR descriptive and H(Y) primary (D-07, option (a)).
- Controlled-instance verification: the three non-measured DRY_RUN rounds of 2026-11-14 on GitHub Actions (runs 43547714203, 43579847658 and 43913235559; the latest governs), recorded in experiments/E05-determinism/controlled-instance-status.yaml and manifests/e05-environment-verification-rounds-v1.yaml; every condition is CONTROLLED and VERIFIED.

### Sample size, order and dispatch record

- N = 50 executions per condition (protocol/repeatability-determinism-v1.md, section 3); 650 executions in all: SUT-01 350 (7 conditions), SUT-02 50 (1), SUT-04 150 (3), SUT-05 100 (2); 13 dispatches under 4 per-SUT dispatch authorizations. One dispatch runs the 50 executions EX0001 to EX0050 of one condition sequentially on one shared instance (D-02, model B), in one job with a 60-minute limit. Identifiers: execution_id EX0001 to EX0050; attempt = the attempt index, 1 under the authorization; run_id = <condition_id>__<execution_id>__A<attempt> (D-19).
- Order of dispatch (fixed here, before the first dispatch): under each SUT's authorization the conditions run one at a time in this order, a condition's dispatch only after the previous run has concluded and been imported: SUT-01: E05-SUT01-API-01, API-02, API-03, API-04, API-05, API-06, WEB-01; SUT-02: E05-SUT02-WEB-01; SUT-04: E05-SUT04-API-01, API-02, WEB-01; SUT-05: E05-SUT05-API-01, API-02. The chains of different SUTs are independent and may run concurrently.
- Dispatch record (append-only, committed before each dispatch; the run identity is appended after it starts): manifests/e05-measured-dispatch/e05-sut01.jsonl, e05-sut02.jsonl, e05-sut04.jsonl and e05-sut05.jsonl.
- Import: byte-exact under raw-data/E05-determinism/<SUT>/ after the verification of every archive against its GitHub digest: each executions/<run_id>/ directory becomes raw-data/E05-determinism/<SUT>/<run_id>/ and the job files (condition-summary.json, sut-logs/, stdout.log, stderr.log, exit-status.txt, finished-at.txt, duration-seconds.txt, started-at.txt, ci-provenance.json, runtime-environment.json) are kept in raw-data/E05-determinism/<SUT>/<condition_id>__job__A<attempt>/. The H3 loader reads the run directories and ignores *__job__A*.
- A runner lost before all 50 executions are written leaves the completed executions importable and the missing ones without a record; replacing them is a further attempt (executions first_execution to 50, attempt incremented) dispatched only under a further-attempt approval record of the human research lead (manifests/e05-further-attempt-approval-sut0N-v<version>.yaml) that enumerates the executions it covers; nothing is re-run and attempt 1 keeps its recorded outcome.

### Exclusion and attribution rules

- No attempt is excluded from any denominator (protocol/repeatability-determinism-v1.md, section 5, rules 4 and 5). An attempt whose starting-state check fails is recorded as ABORTED with its cause; the job goes on with the next execution.
- Attribution (issue (xix), D-16 option B and D-16b): mechanical TOOLING and SUT labels, raw rates unchanged, attributed counts reported beside them; TOOLING only for an exception or client crash before the stimulus request is sent or an infrastructure interruption recorded by the workflow; uncertain attributions are labeled SUT. An interrupted attempt after establishment counts as an INTERRUPTED_ category (D-09, D-16b). The criteria are fixed here and never applied after seeing a result pattern.
- Global exclusion list for projections: order identifiers (ORDER-<hex>), cart and item identifiers (ITEM-<hex>), tokens and session claims, cookie values, timestamps and dates generated at runtime, randomly generated values (CAPTCHA operands, randomized prices, random modes where the category set does not name them); the SUT's own response values are compared. The executor's scrubber applies to every evidence file.

### CONFIRMATORY comparisons and analysis

- None. H3 is a single-ecosystem prediction (protocol/statistical-analysis-plan-v1.md, section 4.3), so it defines no between-ecosystem comparison; every cross-ecosystem comparison of CEOR or H(Y) is EXPLORATORY and reported with its point estimate, interval and N.
- H3 evaluation rule (pre-registered here): for a condition classified deterministic, H3 is satisfied when the stimulus-phase attempts M equal S with S at or above 45 of the 50 (D-06), and falsified by any unexpected stimulus-phase category among S attempts; below S = 45 the condition is not evaluable for H3, with the reason.
- Metrics: TSRR, CEOR, E2E-ROR and Outcome Entropy H(Y) with k stated, Wilson intervals without continuity correction (D-05), NOT_ESTIMABLE and never 0 when no attempt establishes the target state; the pure core is analysis/h3-analysis/h3-metrics.js with its tests; the loader and the command-line driver are written after the data freeze, and the derived dataset names its raw inputs, script and script version (derived-data/README.md; analysis/README.md).
- Raw data: raw-data/E05-determinism/<SUT>/ only, after import; per run the run manifest (schema v2), the attempt record, the executor log, the tool versions, the provenance, the runtime environment and the evidence files.

### Gates the measured workflow enforces

START recorded with its authorization id; this record present, naming the condition, the schema, the prompt and implementation hashes, the conditions-file hash, the workflow-file hash (G-9), N = 50, CS-001, H3 and the pinned commits and releases of the assigned SUT; the dispatch authorization of the assigned SUT (ISSUED, VALID, issued by the human research lead, naming the condition, N = 50, attempt 1 and the two SHA-256 values); for a further attempt, the further-attempt approval (G-E05-A2); governance v6 frozen; CS-001 FROZEN; the controlled-instance status VERIFIED for the condition (SELF_HOSTED); the implementation equal to the locked hash; the frozen prompt file; default branch only; no GitHub re-run.

### Change log

- None. Any change after the START is recorded as a change-control row (protocol/change-control-v1.md) before the affected execution, and results collected before the change are analyzed under the earlier configuration.
