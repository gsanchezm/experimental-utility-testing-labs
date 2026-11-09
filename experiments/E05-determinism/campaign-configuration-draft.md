# E05-determinism: "Campaign configuration" record (skeleton)

| Field | Value |
|---|---|
| Document | campaign-configuration-draft.md |
| State | DRAFT skeleton. Not a campaign configuration, not locked, not an authorization. Nothing here starts E05, selects a condition, or dispatches anything. |
| Heading it is meant for | "Campaign configuration" in experiments/E05-determinism/README.md (the record is locked at campaign START, protocol/change-control-v1.md, section 7) |
| Order | Follows the items of experiments/README.md, "Common rules for all campaigns" (campaign configuration bullet), then E05-specific items (sections 10 to 13). |
| Companion | design-brief-draft.md. Its section numbers are cited as "brief s.N". |

Conventions: null = unknown and must stay null until a source records it. TBD = a decision or a value that has to be recorded before START. HUMAN DECISION = an a-priori declaration that only the human research lead can make; this draft proposes an option but decides nothing. SUT = system under test.

## 1. Campaign identity and START

- campaign_id: E05-determinism
- status: NOT_STARTED (unchanged by this draft)
- START authorization id: null. To be issued by the human research lead (protocol/change-control-v1.md, section 7, moment 1).
- configuration version: DRAFT-0 (not a locked version).
- protocol: v1, FROZEN-PRE-DATA: protocol/repeatability-determinism-v1.md; protocol/study-design-v1.md; protocol/statistical-analysis-plan-v1.md; protocol/cross-cutting-properties-v1.md.
- Hypothesis label: H3 applies to SUT-01 conditions classified a priori as deterministic (protocol/statistical-analysis-plan-v1.md, section 4.3). The same metrics are computed for the deterministic conditions of every ecosystem and are descriptive for them (protocol/study-design-v1.md, section 6, note (d)).
- Dispatch authorization: TBD. A per-SUT dispatch authorization is announced for the campaigns in the minimum set (the governance successor is not yet written). Dispatch needs its own explicit approval, and the agent-instructions file (CAMPAIGN-CI-WRITE-AUTH-01) applies.

## 2. Scenario mapping records

- Canonical scenario used as the source of target states: CS-001 (experiments/scenario-mappings/CS-001.yaml, mapping FROZEN 2026-09-21; sha256 as recorded in experiments/E03-resetability/README.md, Campaign configuration).
- A mapping record is a hard prerequisite for cross-ecosystem comparison (experiments/README.md, Common rules). E05 proposes no cross-ecosystem comparison (section 11), so no further mapping is required for the proposed conditions.
- HUMAN DECISION D-17: whether E05 uses CS-001 target states only (recommended in brief s.4.2) or needs a new canonical scenario record (none proposed).

## 3. Pinned SUT versions

Copy at START from manifests/sut-manifest.yaml. The values in use are those of experiments/E03-resetability/README.md, Campaign configuration, "Pinned SUT versions": SUT-01 web and api (one commit); SUT-02 web; SUT-03 web and api (one commit; no E05 condition on SUT-03 is proposed); SUT-04 web and api (one commit, release tag 2.2); SUT-05 api (packaged distribution of release v20.2.0).

- Presence of each surface in the pinned version: from the E01 transcription (manifests/sut-manifest.yaml, presence fields). Surfaces without a reset realization are excluded (brief s.3).
- controlled_instance_available: copy from manifests/sut-manifest.yaml per SUT at START, never inferred.

## 4. Toolchain versions

| Tool | Value to record | Status | Gap (brief s.8) |
|---|---|---|---|
| Web runner | Playwright for Python 1.63.0 with pinned runtime dependencies and hashes (experiments/E03-resetability/executor/requirements.txt) | pinned | none for the runner itself |
| Browser | Chromium build named by Playwright 1.63.0 (E03 README: chromium-1243, Chrome for Testing 153.0.8010.12) | build identifier TBD | P1: no study pin; per-run equality check needed |
| API client | Python 3 standard library (urllib.request) on the runner's python3 | exact CPython version TBD | P2 |
| Runner image | ubuntu-24.04 GitHub-hosted runner | image identifier TBD (recorded per run only) | P3 |
| SUT-04 provisioning | Temurin JDK 26 (build TBD); Apache Maven 3.9.14; Node.js 24.21.0 | JDK build TBD | P4 |
| Manifest validation | ajv-cli and ajv-formats as used by the measured workflow | versions TBD; manifests/toolchain-manifest.yaml schema_validator.version is null | P5 |
| Analysis runtime | Node.js v23.6.1 (manifests/toolchain-manifest.yaml, scripting_runtime; platform recorded as Darwin x86_64) | pin to be confirmed for the host that runs the H3 script; script hash TBD | P6 |
| Schema | schemas/run-manifest.schema.v2.json (sha256 as recorded in experiments/E03-resetability/README.md) | pinned | none |

Drift control (brief s.8): the per-attempt toolchain values are recorded in every run manifest. The analysis script reports any change of a value inside a condition.

## 5. Prompt version(s) and frozen implementation

- Dispatch procedure prompt id: TBD (no E05 prompt exists). It must be frozen before START and named here (experiments/README.md, Common rules; prompts/README.md).
- Implementation: TBD. The E05 realizations, projection file and category file are hashed and locked; the hash is recorded here at START.
- Run-manifest schema: schemas/run-manifest.schema.v2.json.
- agent_role in run manifests: ORCHESTRATOR (agent-instructions file, CAMPAIGN-CI-WRITE-AUTH-01; protocol/agent-governance-v5.md, Section 3.6).

## 6. Dispatch model, attempt accounting and sample size

- Dispatch model: HUMAN DECISION D-02. Recommended: B, one shared instance per condition with N sequential attempts and a reset between attempts (brief s.2.2). Alternative A: fresh instance per attempt.
- Attempt order: each attempt is reset, starting-state check, establishment, target-state verification, stimulus, classification, record (brief s.2.1). Sequential (protocol section 5, rule 2).
- Sample size: N = 50 per condition (protocol section 3). N = 30 is not used (no mobile condition).
- Identifiers: HUMAN DECISION D-19. Proposed (E03 convention, executor README, section 8): execution_id EX0001 to EX0050 for the N = 50 executions of a condition; attempt = the attempt index within that execution, starting at 1; run_id = <condition_id>__<execution_id>__A<attempt>. A re-execution is an additional attempt with its own index and a recorded reason (protocol section 5, rule 5). The schema's description of attempt (index within the repeated executions of a condition) differs from this convention; the difference is recorded, not resolved here.
- No-bundle attempts: HUMAN DECISION D-09. Recommended: an interrupted attempt in T with a stub record (brief s.5.9).
- Abort rule: an attempt whose starting-state check fails is recorded as ABORTED with its cause (executor README, section 3, item 11). Whether the job continues after an abort is part of D-02.
- Environment type: SELF_HOSTED for web and api instances on GitHub-hosted runners, as the E03 route records (experiments/E03-resetability/ci-cd-execution-model.md, section 6). HUMAN DECISION D-18: confirm for E05 (protocol section 10.3 fixes the choice per condition).
- Controlled-instance verification: TBD. Every condition needs a controlled instance verified on GitHub Actions before the campaign measures it (agent-instructions file, CAMPAIGN-CI-WRITE-AUTH-01). No E05 verification run exists.

## 7. Conditions

Each condition is one record. Common fields for all: seed null (protocol section 5, rule 7); N = 50; environment_type as in section 6; controlled-instance verification run: null (none exists); categories are phase-tagged (S_ stimulus, INTERRUPTED_, ESTABLISHMENT_, RESET_; brief s.4.1).

### E05-SUT01-API-01
- SUT: SUT-01, surface api. Account: standard_user (documented).
- target_state_id: CS-001. starting_state_id: CS-001-STARTING. Establishment and reset: executor README, section 4.1 (reused unchanged).
- Stimulus: POST /api/checkout, market MX, required MX fields TBD (read from the pinned source; not in the rows read).
- Projection: total, subtotal, tax, delivery fee, tip, currency, decimal places, line items. Excluded: order identifiers, timestamps, tokens.
- Categories (k = 4): S_ORDER_TOTAL_MATCH (expected), S_ORDER_TOTAL_MISMATCH, S_HTTP_NON_200, INTERRUPTED_.
- Expected: S_ORDER_TOTAL_MATCH; expected values computed from the source formula and constants before START (TBD).
- behavior_class: deterministic (proposed). HUMAN DECISION D-11 (basis: audit section 4 Determinism, no evidence row; row SUT01-EV-0027).
- Residual state: orders persist (brief s.4.4). HUMAN DECISION D-03.

### E05-SUT01-API-02
- SUT: SUT-01, surface api. Account: standard_user. target_state_id: CS-001 (not read by the stimulus).
- Stimulus: GET /api/pizzas, X-Country-Code MX, no X-Language.
- Projection: name, description, price, currency per item.
- Categories (k = 4): S_CATALOG_MATCH (expected), S_CATALOG_MISMATCH, S_HTTP_NON_200, INTERRUPTED_.
- behavior_class: deterministic (proposed; row SUT01-EV-0027). HUMAN DECISION D-10 (static-content read).

### E05-SUT01-API-03
- SUT: SUT-01, surface api. Target state: CS-001 (established under standard_user); stimulus uses a separate session.
- Stimulus: POST /api/auth/login as locked_out_user.
- Categories (k = 3): S_LOCKOUT_403_EXACT_MESSAGE (expected), S_OTHER_STATUS_OR_BODY, INTERRUPTED_.
- behavior_class: deterministic (proposed; row SUT01-EV-0007). HUMAN DECISION D-10 (the stimulus does not act on the target state).

### E05-SUT01-API-04
- SUT: SUT-01, surface api. Account: performance_glitch_user (establishment block 4.1 with this account; reset block 4.1; account changed).
- Stimulus: GET /api/pizzas as performance_glitch_user.
- Projection: content only; latency excluded from the comparison (protocol section 6: speed is not a determinism criterion).
- Categories (k = 5): S_CONTENT_MATCH_200 (expected), S_CONTENT_MISMATCH, S_HTTP_NON_200, S_CLIENT_TIMEOUT, INTERRUPTED_. Client timeout value: TBD (must be declared before START).
- behavior_class: deterministic (proposed, by mechanism: a fixed 3.0 s delay, row SUT01-EV-0015; audit section 4 agrees). The client timeout is TBD and must be declared well above 3.0 s before START. HUMAN DECISION D-04 (time-dependent is the conservative alternative).

### E05-SUT01-API-05
- SUT: SUT-01, surface api. Account: a11y_glitch_user (account changed).
- Stimulus: GET /api/pizzas as a11y_glitch_user.
- Categories (k = 5): S_MODE_MISSING_NAME, S_MODE_WRONG_LANG, S_MODE_EXTREME_TEXT, S_OTHER, INTERRUPTED_.
- Expected: HUMAN DECISION D-07.
- behavior_class: stochastic (row SUT01-EV-0018).

### E05-SUT01-API-06 (discriminant control)
- SUT: SUT-01, surface api. Account: error_user (account changed).
- Stimulus: POST /api/checkout as error_user.
- Categories (k = 4): S_ORDER_CREATED, S_HTTP_500, S_OTHER, INTERRUPTED_. The body of the 500 for behavior error is not described in row SUT01-EV-0025 (the leak messages are for security_glitch); this must be read from the pinned source before START (TBD).
- Expected: HUMAN DECISION D-07.
- behavior_class: stochastic (row SUT01-EV-0025). Its role is to show that the classifier can report non-determinism; it is excluded from H3 by class.

### E05-SUT01-WEB-01
- SUT: SUT-01, surface web. Account: standard_user (token injection, executor README section 4.2, reused unchanged with the W-A reset).
- Stimulus: activate the place-order control on Checkout with market MX fields (control selector TBD; read from the pinned source).
- Categories (k = 5): S_ORDER_CONFIRMED (expected; order-success route per row SUT01-EV-0001), S_VALIDATION_MESSAGE, S_HTTP_ERROR_VISIBLE, S_OTHER_VIEW, INTERRUPTED_.
- behavior_class: deterministic (proposed, absence-based for standard_user). HUMAN DECISION D-11. Residual: orders (brief s.4.4).

### E05-SUT02-WEB-01
- SUT: SUT-02, surface web. Account: standard_user. target_state_id: CS-001 (executor README, section 4.3, reused unchanged with APP_DATA_CLEAR).
- Stimulus: add a second inventory item to the cart (selector TBD; pattern as in block 4.3).
- Categories (k = 4): S_BADGE_2 (expected), S_BADGE_OTHER, S_NO_CHANGE, INTERRUPTED_.
- behavior_class: deterministic (proposed, absence-based; audit section 4 Determinism for the account and reset branches). HUMAN DECISION D-11.

### E05-SUT02-WEB-02
- SUT: SUT-02, surface web. Account: visual_user (account changed; reset block 4.3).
- Stimulus: load the inventory page.
- Projection: presence of the visual marker (row SUT02-EV-0015); price excluded because it is random.
- Categories (k = 4): S_VISUAL_MARKER_PRESENT (expected), S_VISUAL_MARKER_ABSENT, S_OTHER, INTERRUPTED_.
- behavior_class: stochastic (audit section 4 Determinism: Math.random() price on each render). Granularity note: brief s.4.2 and integrity-notes-draft.md, R4.
- Expected: S_VISUAL_MARKER_PRESENT, declared before START from the deterministic marker branch (audit section 4; row SUT02-EV-0015). Not a D-07 item.

### E05-SUT04-WEB-01
- SUT: SUT-04, surface web. Account: admin (block 4.6 establishment with the guest form).
- target_state_id: CS-001 (block 4.6, reused unchanged with the delete-control reset).
- Stimulus: second reservation through the web form for room 1 with the run's dates (overlapping).
- Categories (k = 4): S_CONFLICT_MESSAGE (expected; message text TBD), S_BOOKING_CONFIRMED, S_OTHER, INTERRUPTED_.
- behavior_class: time-dependent (proposed, pending source check). HUMAN DECISION D-13. Residual: accepted bookings persist (brief s.4.4).

### E05-SUT04-API-01
- SUT: SUT-04, surface api. Account: admin for the token (block 4.5, reused unchanged with the DELETE reset).
- Stimulus: POST /booking/ for room 1 with overlapping dates, no email or phone.
- Categories (k = 4): S_CONFLICT_REJECTED (expected; status TBD from source), S_CREATED_UNEXPECTED, S_OTHER_STATUS, INTERRUPTED_.
- behavior_class: time-dependent (proposed, pending source check; same as E05-SUT04-WEB-01). HUMAN DECISION D-13.

### E05-SUT04-API-02
- SUT: SUT-04, surface api. target_state_id: CS-001 (block 4.5).
- Stimulus: POST /booking/ with email and phone.
- Projection: presence of the message record (message service endpoint TBD from the pinned source).
- Categories (k = 4): S_MESSAGE_RECORD_PRESENT, S_MESSAGE_RECORD_ABSENT, S_BOOKING_NON_2XX, INTERRUPTED_.
- Expected: HUMAN DECISION D-07 (depends on whether the instance runs the message service or a double).
- behavior_class: external dependency (audit section 4 Determinism; rows SUT04-EV-0028 and SUT04-EV-0029 for the in-repo doubles). Whether the measured instance uses a double is TBD.

### E05-SUT05-API-01
- SUT: SUT-05, surface api. Account: documented account (block 4.7, reused unchanged with the ENVIRONMENT_RESTART reset).
- Stimulus: POST /rest/user/login for the documented account with a wrong password.
- Categories (k = 4): S_REJECTED_AS_EXPECTED (expected; status TBD from source), S_ACCEPTED_UNEXPECTED, S_OTHER, INTERRUPTED_.
- behavior_class: deterministic (proposed; audit section 4 Determinism names the API login handler, row SUT05-EV-0006).

### E05-SUT05-API-02
- SUT: SUT-05, surface api. target_state_id: CS-001 (block 4.7).
- Stimulus: GET of the CAPTCHA route (path TBD; row SUT05-EV-0023 names routes/captcha.ts).
- Categories (k = 4): S_CAPTCHA_ISSUED (expected), S_CAPTCHA_NOT_ISSUED, S_OTHER, INTERRUPTED_.
- behavior_class: stochastic (row SUT05-EV-0023). Granularity note: brief s.4.2.
- Expected: S_CAPTCHA_ISSUED, declared before START (the category excludes the random operands; row SUT05-EV-0023).

## 8. Sample size and seeds

- N = 50 for each of the fourteen conditions in section 7 (protocol section 3).
- seed: null for every attempt (protocol section 5, rule 7). No SUT exposes a seed in the rows read for these mechanisms.
- Timestamps are recorded per attempt for traceability only (protocol section 5, rule 8).

## 9. Exclusion and attribution rules

- No attempt is excluded from any denominator (protocol section 5, rules 4 and 5).
- Attribution rule for issue (xix) (protocol/study-design-v1.md, section 13): HUMAN DECISION D-16. Recommended option B: mechanical TOOLING and SUT labels, raw rates unchanged, attributed counts reported beside them, uncertain attributions labeled SUT (brief s.6).
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
- H3 evaluation rule (pre-registered here as the analysis specification, brief s.5.5): for a condition classified deterministic, H3 is satisfied when M = S with S at or above the minimum denominator of D-06, and falsified by any unexpected stimulus-phase category among S attempts.
- All cross-ecosystem comparisons of CEOR or H(Y) are EXPLORATORY (SAP section 4.2). Their point estimate, interval and N are reported like any other result.

## 12. Analysis specification

- Script: TBD (not written). Input: the run manifests of raw-data/E05-determinism/ (after import). Output: a derived-data table naming the input file hashes, the script hash, and the runtime (SAP section 5; analysis/README.md).
- Metrics: TSRR, CEOR, E2E-ROR and H(Y) as in brief s.5, with Wilson intervals (uncorrected: HUMAN DECISION D-05) and NOT_ESTIMABLE handling (brief s.5.3).
- Minimum denominator for H3: HUMAN DECISION D-06 (recommended: S = T).
- Expected-category policy for stochastic and external conditions: HUMAN DECISION D-07.
- Runtime: P6 (section 4). The script's own hash is recorded before its first run.
- Consistency checks: brief s.5.7 (fail-closed).

## 13. Gates the measured workflow must enforce (mirror of the agent-instructions file, CAMPAIGN-CI-WRITE-AUTH-01)

The workflow does not exist. These are the gates it must check before any MEASURED_EXPERIMENT:

1. START recorded with its authorization id (section 1).
2. This locked configuration present, with its hash recorded.
3. A FROZEN mapping record for every canonical scenario used (CS-001, section 2).
4. The run-manifest schema the configuration names (schema v2, section 5).
5. Frozen agent governance in force (protocol/agent-governance-v5.md or its successor).
6. Controlled instance verified on GitHub Actions for every condition that requires one (section 6). Not yet present.
7. Pinned repository commit and workflow revision (sections 3 and 5).
8. The frozen prompt and frozen implementation hashes (section 5).
9. First attempt only; default branch only; no re-run.
10. No mobile condition present in the configuration (brief s.3; a separate design is needed).
11. Per-SUT dispatch authorization, once the governance successor is written (section 1).

## 14. Change log

- None. Any change after START is recorded as a change-control row (protocol/change-control-v1.md) before the affected attempt, and results collected before the change are analyzed under the earlier configuration.
