# E05-determinism: "Campaign configuration" record (skeleton)

| Field | Value |
|---|---|
| Document | campaign-configuration-draft.md (DRAFT-2, 2026-11-14: the decisions of manifests/campaign-execution-decisions-v4.yaml to -v9.yaml, the source findings of manifests/source-reads-v1.yaml to -v4.yaml and the two DRY_RUN rounds are incorporated; still a draft) |
| State | DRAFT skeleton. Not a campaign configuration, not locked, not an authorization. Nothing here starts E05, selects a condition, or dispatches anything. |
| Heading it is meant for | "Campaign configuration" in experiments/E05-determinism/README.md (the record is locked at campaign START, protocol/change-control-v1.md, section 7) |
| Order | Follows the items of experiments/README.md, "Common rules for all campaigns" (campaign configuration bullet), then E05-specific items (sections 10 to 13). |
| Companion | design-brief-draft.md. Its section numbers are cited as "brief s.N". |

Conventions: null = unknown and must stay null until a source records it. TBD = a decision or a value that has to be recorded before START. HUMAN DECISION = an a-priori declaration that only the human research lead can make; this draft proposes an option but decides nothing. SUT = system under test.

## 1. Campaign identity and START

- campaign_id: E05-determinism
- status: NOT_STARTED (unchanged by this draft)
- START authorization id: null. To be issued by the human research lead (protocol/change-control-v1.md, section 7, moment 1).
- configuration version: DRAFT-2 (not a locked version). What is decided and what is still TBD is marked per item; the items that still need the human research lead are listed in section 15.
- protocol: v1, FROZEN-PRE-DATA: protocol/repeatability-determinism-v1.md; protocol/study-design-v1.md; protocol/statistical-analysis-plan-v1.md; protocol/cross-cutting-properties-v1.md.
- Hypothesis label: H3 applies to SUT-01 conditions classified a priori as deterministic (protocol/statistical-analysis-plan-v1.md, section 4.3). The same metrics are computed for the deterministic conditions of every ecosystem and are descriptive for them (protocol/study-design-v1.md, section 6, note (d)).
- Dispatch authorization: TBD. A per-SUT dispatch authorization is announced for the campaigns in the minimum set (the governance successor is not yet written). Dispatch needs its own explicit approval, and the agent-instructions file (CAMPAIGN-CI-WRITE-AUTH-01) applies.

## 2. Scenario mapping records

- Canonical scenario used as the source of target states: CS-001 (experiments/scenario-mappings/CS-001.yaml, mapping FROZEN 2026-09-21; sha256 as recorded in experiments/E03-resetability/README.md, Campaign configuration).
- A mapping record is a hard prerequisite for cross-ecosystem comparison (experiments/README.md, Common rules). E05 proposes no cross-ecosystem comparison (section 11), so no further mapping is required for the proposed conditions.
- DECIDED 2026-11-12 (D-17, manifests/campaign-execution-decisions-v6.yaml): E05 uses CS-001 target states only; no new canonical scenario record.

## 3. Pinned SUT versions

Copy at START from manifests/sut-manifest.yaml. The values in use are those of experiments/E03-resetability/README.md, Campaign configuration, "Pinned SUT versions": SUT-01 web and api (one commit); SUT-02 web; SUT-03 web and api (one commit; no E05 condition on SUT-03 is proposed); SUT-04 web and api (one commit, release tag 2.2); SUT-05 api (packaged distribution of release v20.2.0).

- Presence of each surface in the pinned version: from the E01 transcription (manifests/sut-manifest.yaml, presence fields). Surfaces without a reset realization are excluded (brief s.3).
- controlled_instance_available: copy from manifests/sut-manifest.yaml per SUT at START, never inferred.

## 4. Toolchain versions

| Tool | Value to record | Status | Gap (brief s.8) |
|---|---|---|---|
| Web runner | Playwright for Python 1.63.0 with pinned runtime dependencies and hashes (experiments/E03-resetability/executor/requirements.txt) | pinned | none for the runner itself |
| Browser | Chromium build named by Playwright 1.63.0 (E03 README: chromium-1243, Chrome for Testing 153.0.8010.12) | reference value 153.0.8010.12, recorded in the tool-versions file of every DRY_RUN execution of round 2 (decisions-v9) | P1: no study pin; the per-run record is the control |
| API client | Python 3 standard library (urllib.request) on the runner's python3 | reference values: executor runtime 3.12.16, system python3 3.12.3 (round 2; decisions-v9) | P2: recorded per run |
| Runner image | ubuntu-24.04 GitHub-hosted runner | reference value ImageOS ubuntu24, image version 20261111.370.1 (round 2); drift is recorded in the runtime-environment file of every job and is not a gate (decisions-v9) | P3: recorded per job |
| SUT-04 provisioning | Temurin JDK 26 (reference build Temurin-26.0.2.1+1, read from the log of run 43579847658); Apache Maven 3.9.14; Node.js 24.21.0 | JDK build recorded as a reference value | P4: recorded per job in the job log |
| Manifest validation | ajv-cli@5 and ajv-formats@3 as used by the validation step of the measured workflow | reference values ajv-cli 5.0.0 and ajv-formats 3.0.1 (npm registry, 2026-11-14); the step resolves them by major version; manifests/toolchain-manifest.yaml schema_validator.version is null | P5 |
| Analysis runtime | Node.js v23.6.1 (manifests/toolchain-manifest.yaml, scripting_runtime; platform recorded as Darwin x86_64) | pin to be confirmed for the host that runs the H3 script at the START package; script hash recorded before its first run | P6 |
| Schema | schemas/run-manifest.schema.v2.json (sha256 as recorded in experiments/E03-resetability/README.md) | pinned | none |

Drift control (brief s.8): the per-attempt toolchain values are recorded in every run manifest. The analysis script reports any change of a value inside a condition.

## 5. Prompt version(s) and frozen implementation

- Dispatch procedure prompt id: ORCHESTRATOR-E05-determinism-v1 (working copy prompts/working/ORCHESTRATOR-E05-determinism-v1.md). DECIDED 2026-11-14 (decisions-v9): its frozen copy, byte-identical, is written to prompts/frozen/ at the START, on the human research lead's approval of the START (experiments/README.md, Common rules; prompts/README.md).
- Implementation: the candidate hash is the sha256 of experiments/E05-determinism/executor/run-condition.sh, bade00d2a45e69da3b25707e6c00cd84d892c15ccdf0bf69485ae8f3570f9ac0, the implementation that ran complete on GitHub Actions in the second DRY_RUN round (run 43579847658); it embeds the digests of the realizations, the projection file and the requirements. The conditions file is hashed with this record at START. The hash is locked here at START.
- Run-manifest schema: schemas/run-manifest.schema.v2.json.
- agent_role in run manifests: ORCHESTRATOR (agent-instructions file, CAMPAIGN-CI-WRITE-AUTH-01; protocol/agent-governance-v5.md, Section 3.6).

## 6. Dispatch model, attempt accounting and sample size

- Dispatch model: DECIDED 2026-11-12 (D-02, manifests/campaign-execution-decisions-v4.yaml): B, one shared instance per condition with N sequential attempts and a reset between attempts (brief s.2.2).
- Attempt order: each attempt is reset, starting-state check, establishment, target-state verification, stimulus, classification, record (brief s.2.1). Sequential (protocol section 5, rule 2).
- Sample size: N = 50 per condition (protocol section 3). N = 30 is not used (no mobile condition).
- Identifiers: DECIDED 2026-11-12 (D-19): the E03 convention (E03 convention, executor README, section 8): execution_id EX0001 to EX0050 for the N = 50 executions of a condition; attempt = the attempt index within that execution, starting at 1; run_id = <condition_id>__<execution_id>__A<attempt>. A re-execution is an additional attempt with its own index and a recorded reason (protocol section 5, rule 5). The schema's description of attempt (index within the repeated executions of a condition) differs from this convention; the difference is recorded, not resolved here.
- No-bundle attempts: DECIDED 2026-11-12 (D-09, manifests/campaign-execution-decisions-v5.yaml): an interrupted attempt in T with a stub record and its own attempt index; it counts against TSRR and E2E-ROR and never against CEOR.
- Abort rule: an attempt whose starting-state check fails is recorded as ABORTED with its cause (executor README, section 3, item 11). Whether the job continues after an abort is part of D-02.
- Environment type: DECIDED 2026-11-12 (D-18): SELF_HOSTED per condition for web and api instances on GitHub-hosted runners, as the E03 route records (experiments/E03-resetability/ci-cd-execution-model.md, section 6), and a controlled-instance verification of each condition before START.
- Controlled-instance verification: two non-measured DRY_RUN rounds ran on GitHub Actions, each on the exact-line approval of the human research lead: round 1, run 43547714203 (2026-11-14, 2 executions per condition; 11 of 14 conditions green, three defects found and corrected); round 2, run 43579847658 (2026-11-14, 3 executions per condition; an outcome recorded in all 13 configured conditions). Every condition needs a controlled instance verified on GitHub Actions before the campaign measures it (agent-instructions file, CAMPAIGN-CI-WRITE-AUTH-01); the status record experiments/E05-determinism/controlled-instance-status.yaml that gate G-6 reads is written with the START package.

## 7. Conditions

The machine-readable mirror of this section is experiments/E05-determinism/conditions-draft.json (categories, expected categories, classes, k, reset kind, minimum S); the executor and the analysis read it, and it is hashed with the configuration at START.

Each condition is one record. Common fields for all: seed null (protocol section 5, rule 7); N = 50; environment_type as in section 6; controlled-instance verification run: null (none exists); categories are phase-tagged (S_ stimulus, INTERRUPTED_, ESTABLISHMENT_, RESET_; brief s.4.1).

### E05-SUT01-API-01
- SUT: SUT-01, surface api. Account: standard_user (documented).
- target_state_id: CS-001. starting_state_id: CS-001-STARTING. Establishment and reset: executor README, section 4.1 (reused unchanged).
- Stimulus: POST /api/checkout, market MX. Required fields (SOURCE_VERIFIED, manifests/source-reads-v1.yaml F02): country_code MX, items, name (2-100 characters), address (at least 5), phone (at least 8) and colonia; tip field propina (0, 5, 10 or 15); optional zip_code of five digits.
- Projection: total, subtotal, tax, delivery fee, tip, currency, decimal places, line items. Excluded: order identifiers, timestamps, tokens.
- Categories (k = 4): S_ORDER_TOTAL_MATCH (expected), S_ORDER_TOTAL_MISMATCH, S_HTTP_NON_200, INTERRUPTED_.
- Expected: S_ORDER_TOTAL_MATCH; expected values computed from the source formula and constants before START (TBD).
- behavior_class: deterministic, SOURCE_VERIFIED (F01: no random and no clock in the outcome path for standard_user; D-11 resolved by the source check).
- Residual state: orders persist (brief s.4.4). DECIDED (D-03): a process-restart reset of the SUT-01 instance between attempts, a new realization to be implemented and verified before START (see section 15).

### E05-SUT01-API-02
- SUT: SUT-01, surface api. Account: standard_user. target_state_id: CS-001 (not read by the stimulus).
- Stimulus: GET /api/pizzas, X-Country-Code MX, no X-Language.
- Projection: name, description, price, currency per item.
- Categories (k = 4): S_CATALOG_MATCH (expected), S_CATALOG_MISMATCH, S_HTTP_NON_200, INTERRUPTED_.
- behavior_class: deterministic (row SUT01-EV-0027). DECIDED (D-10): counts toward H3 with the flag nominal stimulus (static-content read).

### E05-SUT01-API-03
- SUT: SUT-01, surface api. Target state: CS-001 (established under standard_user); stimulus uses a separate session.
- Stimulus: POST /api/auth/login as locked_out_user.
- Categories (k = 3): S_LOCKOUT_403_EXACT_MESSAGE (expected), S_OTHER_STATUS_OR_BODY, INTERRUPTED_.
- behavior_class: deterministic (row SUT01-EV-0007). DECIDED (D-10): counts toward H3 with the flag nominal stimulus (the stimulus does not act on the target state).

### E05-SUT01-API-04
- SUT: SUT-01, surface api. Account: performance_glitch_user (establishment block 4.1 with this account; reset block 4.1; account changed).
- Stimulus: GET /api/pizzas as performance_glitch_user.
- Projection: content only; latency excluded from the comparison (protocol section 6: speed is not a determinism criterion).
- Categories (k = 5): S_CONTENT_MATCH_200 (expected), S_CONTENT_MISMATCH, S_HTTP_NON_200, S_CLIENT_TIMEOUT, INTERRUPTED_. Client timeout value: 30 s, DECIDED 2026-11-14 (decisions-v9; ten times the fixed 3.0 s delay, which the second DRY_RUN measured as 3.01 s per execution).
- behavior_class: deterministic by mechanism, DECIDED (D-04): a fixed 3.0 s delay applied by apply_user_behavior to the catalog and checkout routes (row SUT01-EV-0015; F04), the timeout category kept.

### E05-SUT01-API-05
- SUT: SUT-01, surface api. Account: a11y_glitch_user (account changed).
- Stimulus: GET /api/pizzas as a11y_glitch_user.
- Categories (k = 5): S_MODE_MISSING_NAME, S_MODE_WRONG_LANG, S_MODE_EXTREME_TEXT, S_OTHER, INTERRUPTED_.
- Expected: D-07 decided as option (a) (one pre-declared category, CEOR descriptive, H(Y) primary); the category is S_MODE_MISSING_NAME, DECIDED 2026-11-14 (decisions-v9; the choice among three equiprobable modes is arbitrary and changes no H(Y) value).
- behavior_class: stochastic (row SUT01-EV-0018).

### E05-SUT01-API-06 (discriminant control)
- SUT: SUT-01, surface api. Account: error_user (account changed).
- Stimulus: POST /api/checkout as error_user.
- Categories (k = 4): S_ORDER_CREATED, S_HTTP_500, S_OTHER, INTERRUPTED_. The 500 for behavior error carries the detail 'Random checkout error triggered for testing purposes' (F03, SOURCE_VERIFIED; probability 0.5 per call).
- Expected: D-07 decided as option (a); the category is S_ORDER_CREATED (what the documented standard checkout does), DECIDED 2026-11-14 (decisions-v9).
- behavior_class: stochastic (row SUT01-EV-0025). Its role is to show that the classifier can report non-determinism; it is excluded from H3 by class.

### E05-SUT01-WEB-01
- SUT: SUT-01, surface web. Account: standard_user (token injection, executor README section 4.2, reused unchanged with the W-A reset).
- Stimulus: activate the place-order control on Checkout with market MX fields: the element with data-testid built by tid('place-order-btn'), then the confirmation control confirm-order-yes of the modal that it opens (F05, SOURCE_VERIFIED); the order-success route is /order-success.
- Categories (k = 5): S_ORDER_CONFIRMED (expected; order-success route per row SUT01-EV-0001), S_VALIDATION_MESSAGE, S_HTTP_ERROR_VISIBLE, S_OTHER_VIEW, INTERRUPTED_.
- behavior_class: deterministic, SOURCE_VERIFIED (F05; D-11 resolved by the source check). Residual: orders (brief s.4.4); process-restart reset (D-03).

### E05-SUT02-WEB-01
- SUT: SUT-02, surface web. Account: standard_user. target_state_id: CS-001 (executor README, section 4.3, reused unchanged with APP_DATA_CLEAR).
- Stimulus: add a second inventory item to the cart: the control whose data-test is the label 'add to cart', a hyphen and the item name, lowercased with spaces turned into hyphens; the badge to read has data-test shopping-cart-badge (F07, SOURCE_VERIFIED).
- Categories (k = 4): S_BADGE_2 (expected), S_BADGE_OTHER, S_NO_CHANGE, INTERRUPTED_.
- behavior_class: deterministic, SOURCE_VERIFIED (F07: the cart path of a user that is neither problem_user nor error_user has no random and no clock; D-11 resolved by the source check).

### E05-SUT02-WEB-02 (RETIRED before the START)
- RETIRED on 2026-11-14, before any measured datum (decisions-v9, E05-SUT02-WEB-02-RETIRED): its category set rested on a visual marker (row SUT02-EV-0015) that no recorded source defines. The SUT-02 audit holds no such row, and the only branch specific to visual_user in the files read at the pin is the random price (manifests/source-reads-v3.yaml, F23), which the projection excludes. The condition is not in the conditions file, not in the choices of the workflows and not in any dispatch authorization. The study keeps 13 conditions (650 executions); H3 is unchanged because stochastic conditions are excluded from H3 by class. The original record is kept in design-brief-draft.md, section 4.

### E05-SUT04-WEB-01
- SUT: SUT-04, surface web. Account: admin (block 4.6 establishment with the guest form).
- target_state_id: CS-001 (block 4.6, reused unchanged with the delete-control reset).
- Stimulus: second reservation through the web form for room 1 with the run's dates (overlapping).
- Categories (k = 4): S_NO_CONFIRMATION_SHOWN (expected), S_BOOKING_CONFIRMED, S_OTHER, INTERRUPTED_. A conflict answers 409 with no body (F09) and the web form then shows no confirmation. The earlier provisional name S_NO_CONFIRMATION_FORM_REMAINS rested on the inference that the page stays on the form (F10); the first DRY_RUN (run 43547714203, 2026-11-14) showed the framework error page 'This page couldn't load' instead, so the category is defined by the source facts (HTTP 409 and no confirmation) and the page state is recorded as evidence only (IMPLEMENTATION-NOTES.md, point 21); the name was confirmed on 2026-11-14 (decisions-v9). S_CONFLICT_MESSAGE of the earlier draft is dropped.
- behavior_class: deterministic, resolved by the source check (D-13; F08: the date validator and the conflict check read request dates only). Residual: the stimulus is rejected-only (D-03), so no booking persists.

### E05-SUT04-API-01
- SUT: SUT-04, surface api. Account: admin for the token (block 4.5, reused unchanged with the DELETE reset).
- Stimulus: POST /booking/ for room 1 with overlapping dates, no email or phone.
- Categories (k = 4): S_CONFLICT_REJECTED (expected; HTTP 409 with no body, F09), S_CREATED_UNEXPECTED, S_OTHER_STATUS, INTERRUPTED_.
- behavior_class: deterministic, resolved by the source check (D-13; F08, F09).

### E05-SUT04-API-02
- SUT: SUT-04, surface api. target_state_id: CS-001 (block 4.5).
- Stimulus: POST /booking/ with email and phone.
- Projection: presence of the message record (the count of GET /message/count on the message service, manifests/source-reads-v3.yaml, F24; the instance runs the real message service, not a double).
- Categories (k = 5): S_MESSAGE_RECORD_PRESENT (expected), S_MESSAGE_RECORD_ABSENT, S_BOOKING_NON_2XX, S_OTHER, INTERRUPTED_. DECIDED 2026-11-14 (decisions-v9): S_OTHER is the catch-all; the executor's labels S_MESSAGE_COUNT_UNREADABLE and S_MESSAGE_COUNT_UNEXPECTED map to it and the original label stays in the note of the attempt.
- Expected: D-07 decided as option (a); the category is S_MESSAGE_RECORD_PRESENT (the documented flow posts a message when email and phone are present, F09), DECIDED 2026-11-14 (decisions-v9).
- behavior_class: external dependency (audit section 4 Determinism; rows SUT04-EV-0028 and SUT04-EV-0029 for the in-repo doubles). The measured instance runs the real message service (executor README, section 3).
- DECIDED 2026-11-12 (D-03 follow-up, manifests/campaign-execution-decisions-v7.yaml): the stimulus is an ACCEPTED booking (the message is posted only after a successful create, F09), which persists; the reset of this condition deletes the stimulus booking by the id of the 201 response in addition to the CS-001 booking (a new, small realization, for this condition only). The message record kept by the message service is not deleted and is declared residual state. The other two SUT-04 conditions stay rejected-only.

### E05-SUT05-API-01
- SUT: SUT-05, surface api. Account: documented account (block 4.7, reused unchanged with the ENVIRONMENT_RESTART reset).
- Stimulus: POST /rest/user/login for the documented account with a wrong password.
- Categories (k = 4): S_REJECTED_AS_EXPECTED (expected; HTTP 401 with the body 'Invalid email or password.', F11), S_ACCEPTED_UNEXPECTED, S_OTHER, INTERRUPTED_.
- behavior_class: deterministic (audit section 4 Determinism names the API login handler, row SUT05-EV-0006; F11: no random and no clock in the query).

### E05-SUT05-API-02
- SUT: SUT-05, surface api. target_state_id: CS-001 (block 4.7).
- Stimulus: GET /rest/captcha (F12; row SUT05-EV-0023 names routes/captcha.ts). The projection excludes captchaId (a counter that grows on every call until the process restarts) as well as the operands, operators and answer.
- Categories (k = 4): S_CAPTCHA_ISSUED (expected), S_CAPTCHA_NOT_ISSUED, S_OTHER, INTERRUPTED_.
- behavior_class: stochastic (row SUT05-EV-0023). Granularity note: brief s.4.2.
- Expected: S_CAPTCHA_ISSUED, declared before START (the category excludes the random operands; row SUT05-EV-0023).

## 8. Sample size and seeds

- N = 50 for each of the thirteen conditions in section 7 (protocol section 3), 650 executions in all: SUT-01 350 (7 conditions), SUT-02 50 (1), SUT-04 150 (3), SUT-05 100 (2); 13 dispatches under 4 per-SUT authorizations.
- seed: null for every attempt (protocol section 5, rule 7). No SUT exposes a seed in the rows read for these mechanisms.
- Timestamps are recorded per attempt for traceability only (protocol section 5, rule 8).

## 9. Exclusion and attribution rules

- No attempt is excluded from any denominator (protocol section 5, rules 4 and 5).
- Attribution rule for issue (xix) (protocol/study-design-v1.md, section 13): DECIDED 2026-11-12 (D-16, manifests/campaign-execution-decisions-v4.yaml): option B, mechanical TOOLING and SUT labels, raw rates unchanged, attributed counts reported beside them, uncertain attributions labeled SUT (brief s.6, rules 1 to 5). D-16b DECIDED (manifests/campaign-execution-decisions-v5.yaml): a TOOLING interruption after establishment counts as an INTERRUPTED_ category and is reported with its label.
- TOOLING criteria (if D-16 accepts option B): exception or client crash before the stimulus request is sent; infrastructure interruption recorded by the workflow. The criteria are fixed here before START and never applied after seeing a result pattern.
- Global exclusion list for projections (applies to every condition): order identifiers (ORDER-<hex>), cart and item identifiers (ITEM-<hex>), tokens and session claims, cookie values, timestamps and dates generated at runtime, randomly generated values (CAPTCHA operands, randomized prices, random modes where the category set does not name them). The SUT's own response values are compared.
- Publication scrubbing: the executor's scrubber applies to every evidence file (executor README, section 9).

## 10. Outcome categories and comparison rules

- Category sets are closed and listed per condition in section 7. Labels outside the set are classified OTHER_ (stimulus phase) and are reported, never dropped.
- Phase prefixes: ESTABLISHMENT_ (outside the CEOR denominator), RESET_ (starting state not reached), S_ (stimulus outcome, compared with the expected category), INTERRUPTED_ (protocol section 5, rule 6).
- k is stated with every H(Y) value (protocol section 4).
- Expected categories are written before START from documentation or source (protocol section 4). Never taken from an observed run.
- Labels are carried in outcome.outcome_category (schema v2 string; brief s.5.8).

## 11. CONFIRMATORY comparisons

- None. H3 is a single-ecosystem prediction (protocol section 6, note (d); SAP section 4.3), so it defines no between-ecosystem comparison.
- H3 evaluation rule (pre-registered here as the analysis specification, brief s.5.5): for a condition classified deterministic, H3 is satisfied when M = S with S at or above 45 (D-06), and falsified by any unexpected stimulus-phase category among S attempts.
- All cross-ecosystem comparisons of CEOR or H(Y) are EXPLORATORY (SAP section 4.2). Their point estimate, interval and N are reported like any other result.

## 12. Analysis specification

- Script: the pure core exists, analysis/h3-analysis/h3-metrics.js (TSRR, CEOR, E2E-ROR, H(Y), Wilson, NOT_ESTIMABLE, the H3 rule with the minimum S, the consistency checks of brief s.5.7, the attribution table), with its tests (analysis/h3-analysis/test, node --test, 15 tests on synthetic records). The loader that turns the bundles of raw-data/E05-determinism/ into attempt records and the CLI with the pinned raw-data tree are written after the configuration is locked. Input: the run manifests of raw-data/E05-determinism/ (after import). Output: a derived-data table naming the input file hashes, the script hash, and the runtime (SAP section 5; analysis/README.md).
- Metrics: TSRR, CEOR, E2E-ROR and H(Y) as in brief s.5, with Wilson intervals without continuity correction (DECIDED, D-05) and NOT_ESTIMABLE handling (brief s.5.3).
- Minimum denominator for H3: DECIDED (D-06): S at least 45 of the N = 50 attempts of the condition; below that the condition is not evaluable for H3, with the reason (the value 45 was proposed by the ORCHESTRATOR).
- Expected-category policy for stochastic and external conditions: DECIDED (D-07): option (a), one pre-declared category, CEOR descriptive, H(Y) with counts primary.
- Runtime: P6 (section 4). The script's own hash is recorded before its first run.
- Consistency checks: brief s.5.7 (fail-closed).

## 13. Gates the measured workflow must enforce (mirror of the agent-instructions file, CAMPAIGN-CI-WRITE-AUTH-01)

The workflow (.github/workflows/e05-measured-execution.yml) implements these gates and, as gate G-9, requires that this record names the sha256 of the workflow file; it stays a DRAFT until it is exported (export v61) and the START locks its hash. These are the gates it checks before any MEASURED_EXPERIMENT:

1. START recorded with its authorization id (section 1).
2. This locked configuration present, with its hash recorded.
3. A FROZEN mapping record for every canonical scenario used (CS-001, section 2).
4. The run-manifest schema the configuration names (schema v2, section 5).
5. Frozen agent governance in force (protocol/agent-governance-v5.md or its successor).
6. Controlled instance verified on GitHub Actions for every condition that requires one (section 6); the status record is written with the START package.
7. Pinned repository commit and workflow revision (sections 3 and 5).
8. The frozen prompt and frozen implementation hashes (section 5).
9. Attempt 1 under the dispatch authorization; default branch only; no GitHub re-run; a further attempt only under gate G-E05-A2 (item 12).
10. No mobile condition present in the configuration (brief s.3; a separate design is needed).
11. Per-SUT dispatch authorization, issued under protocol/agent-governance-v6.md, Section 3.7 (section 1).
12. A further attempt (attempt 2 or more, executions first_execution to 50) only under a further-attempt approval record of the human research lead that names the condition, the first execution and the attempt (gate G-E05-A2; decisions-v9).

## 15. What is still open before a START package (nothing here is a decision of this draft)

Decided and incorporated above: D-01 to D-10, D-14 to D-20 and D-11 to D-13 (resolved by the source reads), and, on 2026-11-14 (manifests/campaign-execution-decisions-v9.yaml): the retirement of E05-SUT02-WEB-02, the catch-all S_OTHER of E05-SUT04-API-02 (k = 5), the four confirmed values (30 s timeout of E05-SUT01-API-04; the expected categories of E05-SUT01-API-05, E05-SUT01-API-06 and E05-SUT04-API-02; the name S_NO_CONFIRMATION_SHOWN), the job timeout of 60 minutes, the reference pins, the freezing of the dispatch prompt at the START and the further-attempt mechanism (gate G-E05-A2). Realized and verified: the executor (two DRY_RUN rounds on GitHub Actions) and the two workflows. Still to do or to confirm:

1. **Export v61 (preparation, then the human research lead's yes to its exact push line):** publishes the corrected conditions file, the two workflows (timeout 60, gate G-E05-A2, thirteen conditions), the working prompt and decisions-v9, so that the workflow hash that gate G-9 reads is that of the corrected file. The executor implementation is unchanged (bade00d2...), so no further DRY_RUN is required by that change; a DRY_RUN is run only if the human research lead asks for one.
2. **Records written with the START package:** the controlled-instance status record of the 13 conditions (from the two DRY_RUN rounds); the lock of this record with the sha256 of the conditions file, of the workflow file, of the executor implementation and of the frozen prompt; the import layout of the dispatch procedure (each executions/<run_id>/ directory under raw-data/E05-determinism/<SUT>/<run_id>/, the job files under <condition_id>__job__A<attempt>/ because a further attempt also has job files and a bare __job directory would collide); the template of the further-attempt approval, which enumerates the executions it covers (first_execution to 50, one by one) so that it names "the condition and the execution" as Section 3.7 requires; the dispatch record location; the order of conditions per SUT.
3. **Pins still to record at the START package:** the analysis runtime on the host that runs the H3 script and the script hash (the other pins are reference values in section 4).
4. **Approvals that only the human research lead can give:** the push of export v61, the START and the configuration lock (with the copy of the frozen prompt), the four per-SUT dispatch authorizations under Section 3.7 of protocol/agent-governance-v6.md (SUT-01, SUT-02, SUT-04, SUT-05), any further DRY_RUN line, any further-attempt approval, the freeze.

## 14. Change log

- None. Any change after START is recorded as a change-control row (protocol/change-control-v1.md) before the affected attempt, and results collected before the change are analyzed under the earlier configuration.
