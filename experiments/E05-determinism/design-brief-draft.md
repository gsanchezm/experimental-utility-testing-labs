# E05 (determinism) and E04 (repeatability): design brief

| Field | Value |
|---|---|
| Document | design-brief-draft.md |
| State | DRAFT. Not a protocol, not a campaign configuration, not frozen, not an authorization. It starts, selects, authorizes, and dispatches nothing. |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Prepared | 2026-11-05, for the human research lead. E04 and E05 are NOT_STARTED (experiments/E04-repeatability/README.md; experiments/E05-determinism/README.md). |
| Companions | campaign-configuration-draft.md (skeleton of the campaign configuration record); integrity-notes-draft.md (validity risks and controls) |
| Protocol basis | protocol/repeatability-determinism-v1.md; protocol/study-design-v1.md (sections 6, 9, 10, 13); protocol/statistical-analysis-plan-v1.md (sections 3 to 6); protocol/cross-cutting-properties-v1.md (Determinism) |

Terms: SUT = system under test. CEOR, E2E-ROR, TSRR and H(Y) are defined in section 5. Every condition identifier in this brief is a proposal.

## 0. Provenance and disclosure

- **Read:** both campaign READMEs; protocol/repeatability-determinism-v1.md in full; study-design sections 6, 9, 10 and issues (xi), (xix), (xx) of section 13; SAP sections 3 to 6; cross-cutting properties (Determinism); experiments/README.md (Common rules); the E03 README (Current status, Campaign configuration); the executor README sections 1 to 12; the E03 CI/CD model, section 6; schemas/run-manifest.schema.v2.json; manifests/toolchain-manifest.yaml; manifests/sut-manifest.yaml (presence and pins); the scenario-mapping directory listing.
- **E01 evidence:** the populated audits are on the branches audit/e01-sut0N-* (for example audit/e01-sut01-omnipizza, commit fa807da). The audits/ directories on main are NOT_STARTED templates (executor README, section 2, citing PROTO-U07). The audit.md and evidence.csv files of the six branches were read with read-only git commands; no branch was checked out or changed. Evidence is cited by evidence_id. The E01 limitations files were extracted but not read.
- **E01 adjudicated matrix** (derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json): read because the request named it, for web and API cell scores only. It holds capability levels from documentation and source, not run outcomes.
- **Not read:** raw-data/ (any campaign); any derived-data result of any campaign other than the E01 matrix, in particular derived-data/h2-analysis/; any E03 run bundle or dispatch record; the E03 PRE-START state rows.
- **Observed-outcome exposure (disclosed):** executor README sections 11 and 12 contain DEVELOPMENT and DRY_RUN observations (for example run DV0008, which read the SUT-03 closed-cart badge after a Logout, and runs DV0011 to DV0016). PROTO-U21 in protocol/unresolved.md records one of them. These were read for realization conventions and open issues only. No class, category, expected value, or threshold in this brief is derived from them. The SUT-03 reset question is recorded as an open reset-sufficiency issue, not as evidence for any class.
- **Human exposure (disclosed):** the human research lead has seen the descriptive E03 H2 reset-side result (derived-data/h2-analysis/, not read by this author). The a-priori classes below are not derived from it or from any E03 outcome.
- **No source access:** no SUT source is in the repository and none was cloned. "Source" rationales are the E01 evidence rows and the executor README's cited lines. Where the E01 audit asserts a property without an evidence row, this brief writes "audit section 4, no evidence row" and does not invent a citation.

## 1. Summary

1. H3 needs only CEOR and H(Y) (protocol/study-design-v1.md, section 6; SAP section 4.3). Both are computed from E05 attempts alone. E04 is not needed for H3 (section 9).
2. The attempt skeleton reorders the E03 blocks: every attempt starts with the declared reset, then establishment, target-state verification, stimulus, and classification (section 2). Establishment and reset blocks of E03 are reusable; stimulus, classifier and orchestration are new.
3. Fourteen conditions are proposed (section 4): SUT-01 API 6, SUT-01 web 1, SUT-02 web 2, SUT-04 web 1, SUT-04 API 2, SUT-05 API 2. Proposed classes: deterministic 7, time-dependent 2, stochastic 4, external dependency 1. Of the seven deterministic conditions, five are SUT-01 conditions under the H3 label; one each is SUT-02 and SUT-05, which get the same metrics, described as descriptive.
4. Several classes rest on absence of a documented mechanism or on documentation that disagrees with itself. These are flagged HUMAN DECISION, not decided here.
5. Four open design forks need a human decision before any configuration can be locked: the dispatch model (section 2.2), residual state from order-creating or booking-creating stimuli (section 4.4), the attribution rule of issue (xix) (section 6), and the no-bundle attempt accounting (section 5.9).
6. Pins are missing for the browser build, the exact CPython version, the runner image, the JDK build of SUT-04 and the schema validator (section 8).

## 2. Attempt skeleton and dispatch model

### 2.1 Order of blocks in one attempt

Protocol rule 1 (protocol/repeatability-determinism-v1.md, section 5) requires that each attempt start from the declared reset procedure. E03 orders its blocks establish, verify, reset (experiments/E03-resetability/executor/README.md, section 1). E05 reorders them.

| Step | Block | Source | Status |
|---|---|---|---|
| 1 | Reset to the declared starting state | E03 reset-side realization (executor README, section 4, reset items) | Reused unchanged where the condition's target state is a CS-001 state; otherwise the same mechanism with a new account parameter |
| 2 | Starting-state check (read before establishment; ABORTED with cause if it fails) | executor README, section 3, item 11 | Reused |
| 3 | Establishment (not counted as Required Action) | executor README, section 4, establishment items | Reused unchanged for CS-001 states; account parameter changed for other conditions |
| 4 | Target-state verification (the TSRR numerator and the CEOR denominator gate); failure stops the attempt before step 5 | executor README, section 4, pre-reset verification items | Reused |
| 5 | Stimulus (one predeclared action or read) | none in E03 | New |
| 6 | Outcome projection and classification into the closed category set | none in E03 | New |
| 7 | Record: run manifest (schema v2), evidence, attempt index | executor README, sections 6 to 9 | Reused, with new manifest fields and a new classifier |

E05 does not count Required Actions: protocol section 4 defines no action metric for E05. Setup-effort counting is set by protocol/setup-effort-v2.md, which this brief did not read; protocol/repeatability-determinism-v1.md, section 6, says durations are analyzed under Setup Effort. Whether the reset is also emitted as actions[] is open (HUMAN DECISION D-08, item c).

### 2.2 Dispatch model (HUMAN DECISION D-02)

E03 dispatched one execution per dispatch, each on an ephemeral GitHub-hosted runner (experiments/E03-resetability/README.md, section "Execution"; experiments/E03-resetability/ci-cd-execution-model.md, section 6). E05 has to choose whether its N attempts of a condition share one instance.

| Model | Consequences for E05 |
|---|---|
| A. Fresh instance per attempt (E03 style) | Each attempt starts from the provisioning state, not from the reset. The reset then runs on a clean instance and cannot reveal reset inadequacy. The partial reset of SUT-01 (orders persist, SUT01-EV-0006) never accumulates. Cost: provisioning per attempt; N = 50 per condition multiplies the E03 provisioning time. Protocol rule 1 is met in form only. |
| B. Shared instance, N sequential attempts, reset between attempts | Rule 1 is met in substance. Residual state accumulates (section 4.4), so each attempt's starting-state check is a real measurement of the reset. Rule 2 (sequential) and isolation matter. Confounds from accumulation are part of the result and must be reported. |

Recommendation: B, with the starting-state check of step 2 as a recorded observation and with the residual-state list of section 4.4 fixed in the configuration. Under B, an attempt whose starting-state check fails is recorded as ABORTED with its cause (E03 convention), and the campaign's rules decide whether the job continues.

## 3. Eligibility: SUT and surface pairs

A condition needs an E03 reset realization (protocol section 5, rule 1: "if no reset procedure exists for the condition, the condition is not a repeatable condition and is not executed"). Scores are the E01 adjudicated matrix values (effective_confirmed_score; web and API cells only).

| SUT / surface | E01 score | E03 reset realization | E05 status |
|---|---|---|---|
| SUT-01 API | 3 | executor README 4.1 (API_RESET, SESSION_RESET) | Eligible |
| SUT-01 web | 3 | executor README 4.2 (realization W-A) | Eligible |
| SUT-02 web | 3 | executor README 4.3 (APP_DATA_CLEAR) | Eligible |
| SUT-02 API | 0 (NO_API_SURFACE; SUT-02 presence ABSENT in sut-manifest) | none | Structural absence, recorded as such |
| SUT-03 web | 3 | executor README 4.4 (SESSION_RESET; open item PROTO-U21) | Eligible; no condition proposed (section 4.5) |
| SUT-03 API | 3 | none (E03 has no SUT-03 API condition) | Not a repeatable condition; recorded |
| SUT-04 web | 3 | executor README 4.6 (API_RESET through the row's delete control) | Eligible |
| SUT-04 API | 3 | executor README 4.5 (API_RESET) | Eligible |
| SUT-05 API | 3 | executor README 4.7 (ENVIRONMENT_RESTART) | Eligible |
| SUT-05 web | 3 | none (the restart realization is recorded for the API surface) | HUMAN DECISION D-01 |
| SUT-06 web and API | 0 (NO_WEB_SURFACE, NO_API_SURFACE) | none | Structural absence, recorded as such |

Mobile conditions are outside this brief. A mobile cell needs an admissible runner and the compatibility smoke of the exact SUT x platform x runner (protocol/mobile-runner-policy-v3.md; experiments/README.md, Common rules). No SUT-01 mobile smoke entry exists in manifests/compatibility-smoke-status.yaml. Mobile E05 conditions need their own design.

## 4. Condition catalogue

### 4.1 Rules that apply to every row

- **Seed:** null for every condition. Protocol section 5, rule 7, records seeds only where the SUT or the tooling exposes them. No E01 evidence row names an exposed seed for these mechanisms.
- **N:** 50 per condition (protocol section 3, standard target). No mobile condition, so no N = 30 justification is needed.
- **Projection:** each condition names the fields compared. Run-varying fields are excluded explicitly: order and cart identifiers (audit section 4, Observability, cites SUT01-EV-0029 for the ORDER-<8 hex> and ITEM-<8 hex> identifiers), tokens and session claims, timestamps, and random values. Without the exclusions every CEOR would be 0 by construction (protocol section 2, "exact outcome match").
- **Categories:** closed, pre-declared, phase-tagged. Phase tags: ESTABLISHMENT_ (outside the CEOR denominator), RESET_ (starting state not reached), S_ (stimulus-phase outcome), INTERRUPTED_ (protocol section 5, rule 6). Stimulus-phase categories include OTHER, so that no response is unclassifiable. k = number of stimulus-phase categories including INTERRUPTED_ when it can occur after establishment.
- **Expected:** a single category per condition, written from documentation or source before START, never from observed runs (protocol section 4).
- **Class:** proposed from the mechanism named in the evidence, declared before execution (protocol section 2). It is not revised from observed variance.
- **Evidence grades:** "row" means a named E01 evidence_id; "audit s4" means the audit's section 4 Determinism bullet without an evidence row.

### 4.2 Proposed conditions

Reuse is stated inside the target-state cell: "E03 block" means the executor README realization of the same target state is reused unchanged; "account changed" means that E03 block is reused with another documented account; "new" means no E03 block exists for the step.

| ID | SUT / surface | Target state and establishment | Stimulus | Categories (k) and expected | Proposed class and basis | Notes |
|---|---|---|---|---|---|---|
| E05-SUT01-API-01 | SUT-01 API | CS-001 API state: E03 block 4.1 (cart seeded, standard_user) | POST /api/checkout, standard_user, market MX (required MX fields: not stated in the rows read; read from the pinned source before START) | S_ORDER_TOTAL_MATCH (expected), S_ORDER_TOTAL_MISMATCH, S_HTTP_NON_200, INTERRUPTED_ (k=4) | deterministic. audit s4 (calculate_order_total, no evidence row); row SUT01-EV-0027 (COUNTRY_CONFIG per-market fixed values); audit s4 finds no time mechanism. | Creates an order; see 4.4. Expected total derived before START from the source formula and the constants, not from a run. |
| E05-SUT01-API-02 | SUT-01 API | CS-001 API state (reused unchanged; the stimulus does not read the cart) | GET /api/pizzas, X-Country-Code MX, no X-Language | S_CATALOG_MATCH (expected), S_CATALOG_MISMATCH, S_HTTP_NON_200, INTERRUPTED_ | deterministic. Row SUT01-EV-0027 (per-request translation and market fixed values). | Static-content read. Its agreement is close to a constant of the source, so it tests little runtime behavior. HUMAN DECISION D-10. |
| E05-SUT01-API-03 | SUT-01 API | CS-001 API state (reused unchanged) | POST /api/auth/login as locked_out_user (separate session) | S_LOCKOUT_403_EXACT_MESSAGE (expected), S_OTHER_STATUS_OR_BODY, INTERRUPTED_ | deterministic. Row SUT01-EV-0007 (SOURCE_VERIFIED: unconditional 403, checked before the password). | The target state is established but the stimulus does not use it. Establishment success is near-certain; TSRR is uninformative here. HUMAN DECISION D-10 (the stimulus is nominal with respect to the target state). |
| E05-SUT01-API-04 | SUT-01 API | Login as performance_glitch_user, then E03 block 4.1 with that account (account changed) | GET /api/pizzas as performance_glitch_user (sleep of 3.0 s on each call; row SUT01-EV-0015) | S_CONTENT_MATCH_200 (expected), S_CONTENT_MISMATCH, S_HTTP_NON_200, S_CLIENT_TIMEOUT (time-limited), INTERRUPTED_ (k=5) | deterministic by mechanism (proposed): audit s4 lists this fixed 3.0 s delay under deterministic (row SUT01-EV-0015), and the categorical outcome does not depend on elapsed time when the client timeout is declared well above 3.0 s. Time-dependent is the conservative alternative. | Latency is not a determinism criterion (protocol section 6). A timeout that occurs is an unexpected category and counts. HUMAN DECISION D-04. |
| E05-SUT01-API-05 | SUT-01 API | Login as a11y_glitch_user, then the 4.1 reset (account changed) | GET /api/pizzas as a11y_glitch_user | S_MODE_MISSING_NAME, S_MODE_WRONG_LANG, S_MODE_EXTREME_TEXT, S_OTHER, INTERRUPTED_ (k=5). Expected: HUMAN DECISION D-07. | stochastic. Row SUT01-EV-0018 (random.choice among three documented modes per call). | Expected category has no single correct value (section 5.9). |
| E05-SUT01-API-06 | SUT-01 API | Login as error_user, then E03 block 4.1 with that account (account changed) | POST /api/checkout as error_user | S_ORDER_CREATED, S_HTTP_500 (body not described for behavior error; the leak messages in row SUT01-EV-0025 are for security_glitch), S_OTHER, INTERRUPTED_ (k=4). Expected: HUMAN DECISION D-07. | stochastic. Row SUT01-EV-0025 (probability 0.5 for behaviors error and security_glitch). | Discriminant control: a classifier that reports CEOR = 1 or H(Y) = 0 here has a defect. Excluded from H3 by class. Creates orders (4.4). |
| E05-SUT01-WEB-01 | SUT-01 web | CS-001 web state: E03 block 4.2 (token injection, cart seeded, Checkout view) with the W-A reset | Activate the place-order control on Checkout with market MX fields (control selector not stated in the rows read; read from the pinned source) | S_ORDER_CONFIRMED (expected; order-success route per row SUT01-EV-0001), S_VALIDATION_MESSAGE, S_HTTP_ERROR_VISIBLE, S_OTHER_VIEW, INTERRUPTED_ (k=5) | deterministic for standard_user (proposed). Absence-based: the only stochastic checkout mechanism named in the rows (SUT01-EV-0025) covers behaviors error and security_glitch. audit s4 finds no time mechanism. | Creates an order (4.4). HUMAN DECISION D-11 (accept an absence-based class). |
| E05-SUT02-WEB-01 | SUT-02 web | CS-001 SUT-02 state: E03 block 4.3 (login, backpack in cart) with the APP_DATA_CLEAR reset | Add a second inventory item to the cart (selector pattern as in block 4.3; exact selector not stated in the rows read) | S_BADGE_2 (expected), S_BADGE_OTHER, S_NO_CHANGE, INTERRUPTED_ (k=4) | deterministic (proposed). Absence-based: audit s4 lists account-branch and reset behaviors as deterministic (audit section 4 Determinism cites SUT02-EV-0001, -0002 and -0003 for the account and reset branches) and names no random mechanism on the standard account's cart path; no evidence row for this path. | HUMAN DECISION D-11. |
| E05-SUT02-WEB-02 | SUT-02 web | Login as visual_user (account changed); reset block 4.3 | Load the inventory page; projection keeps the visual marker and excludes the price | S_VISUAL_MARKER_PRESENT (expected; declared from the deterministic marker branch), S_VISUAL_MARKER_ABSENT, S_OTHER, INTERRUPTED_ (k=4) | stochastic. audit s4: randomPrice() uses Math.random() on each render for visual_user (Inventory.jsx line 122; row SUT02-EV-0015 is named there). | Granularity trap (section 5.9 and integrity-notes-draft.md, risk R4): with the price excluded, every attempt may fall in one category. The class stays stochastic because the mechanism is random. |
| E05-SUT04-WEB-01 | SUT-04 web | CS-001 SUT-04 web state: E03 block 4.6 (booking exists, admin room page) with its delete-control reset | Second reservation through the web form for room 1 with the run's dates (overlapping) | S_CONFLICT_MESSAGE (expected; message text not stated in the rows read), S_BOOKING_CONFIRMED, S_OTHER, INTERRUPTED_ (k=4) | time-dependent (proposed, pending source check). Conflict: audit s4 says validation uses the request's dates, but places DateCheckValidator under its time-dependent bullet. | HUMAN DECISION D-13. Accepted reservations persist (4.4). |
| E05-SUT04-API-01 | SUT-04 API | CS-001 SUT-04 API state: E03 block 4.5 (booking created, token) with the DELETE reset | POST /booking/ for room 1 with overlapping dates, no email or phone | S_CONFLICT_REJECTED (expected; status not stated in the rows read), S_CREATED_UNEXPECTED, S_OTHER_STATUS, INTERRUPTED_ (k=4) | time-dependent (proposed, pending source check): as E05-SUT04-WEB-01. | Accepted bookings are not deleted by the CS-001 reset (4.4). |
| E05-SUT04-API-02 | SUT-04 API | CS-001 SUT-04 API state: E03 block 4.5 | POST /booking/ with email and phone (the message side effect that block 4.6 also notes) | S_MESSAGE_RECORD_PRESENT, S_MESSAGE_RECORD_ABSENT, S_BOOKING_NON_2XX, INTERRUPTED_ (k=4). Expected: HUMAN DECISION D-07. | external dependency. audit s4: booking creation calls the message service; in-repo WireMock doubles exist (SUT04-EV-0029). Whether the measured instance uses them is not stated. | Class spelling follows the schema: "external dependency". |
| E05-SUT05-API-01 | SUT-05 API | CS-001 SUT-05 state: E03 block 4.7 (basket item, token) with the restart reset | POST /rest/user/login for the documented account with a wrong password (the basket is not read) | S_REJECTED_AS_EXPECTED (status not stated in the rows read), S_ACCEPTED_UNEXPECTED, S_OTHER, INTERRUPTED_ (k=4) | deterministic (proposed). audit s4 lists the API login handler as deterministic (SUT05-EV-0006). | Tests account gating under the target session. |
| E05-SUT05-API-02 | SUT-05 API | CS-001 SUT-05 state: E03 block 4.7 | GET of the CAPTCHA route (path not stated in the rows read; row SUT05-EV-0023 names routes/captcha.ts) | S_CAPTCHA_ISSUED (expected; declared: the category excludes the random operands), S_CAPTCHA_NOT_ISSUED, S_OTHER, INTERRUPTED_ (k=4) | stochastic. Row SUT05-EV-0023 (Math.random for operands and operators on every request). | Granularity trap: the issued category is identical across attempts. The class stays stochastic. |

### 4.3 Notes on the table

- **Class counts:** deterministic 7 (SUT01-API-01, -02, -03, -04; SUT01-WEB-01; SUT02-WEB-01; SUT05-API-01); time-dependent 2 (SUT04-WEB-01; SUT04-API-01); stochastic 4 (SUT01-API-05, -06; SUT02-WEB-02; SUT05-API-02); external dependency 1 (SUT04-API-02).
- **H3 label:** H3 is labeled for SUT-01 only (protocol section 6, note (d)). The metrics are computed identically for the deterministic conditions of every ecosystem, and those comparisons stay descriptive.
- **Mechanism versus outcome:** E05-SUT01-API-05 and E05-SUT02-WEB-02 and E05-SUT05-API-02 are stochastic even where the chosen projection yields a single category. The class follows the mechanism (protocol section 2, "statistically reproducible randomness is not determinism").

### 4.4 Residual state the reset does not clear

| SUT / surface | Documented residual state | Affected conditions | Control |
|---|---|---|---|
| SUT-01 API and web | Orders persist. The reset clears the caller's cart, market and profile only, and whole-backend reset needs a process restart (SUT01-EV-0006; audit s4 Resetability). | SUT01-API-01, -06; SUT01-WEB-01 | HUMAN DECISION D-03: non-persistent stimuli only, or a process-restart reset for SUT-01 (a new realization, not in E03). Exclude order identifiers. Do not make the starting-state check depend on order count. |
| SUT-04 API and web | A booking created by an accepted stimulus survives the CS-001 reset, which deletes only the CS-001 booking (executor README 4.5 and 4.6). A residual booking can change the next attempt's conflict outcome. | SUT04-API-01; SUT04-WEB-01 | HUMAN DECISION D-03: extended reset that deletes stimulus bookings (a new realization), or rejected-only stimuli. |
| SUT-03 web | Open item PROTO-U21 (protocol/unresolved.md): whether the Sign-Out reset clears the running client's cart is contested. Non-blocking for E03. | None proposed | Resolve before any SUT-03 condition. |
| SUT-05 API | The restart re-creates the data (executor README 4.7; SUT05-EV-0003). The restart readiness budget (180 s) can fail, which is an ERROR outcome, not a determinism result. | SUT05-API-01, -02 | Budgets stay as in the executor; a readiness failure is a reset-phase category. |
| SUT-04 scheduled reset | The scheduler is disabled by default when dbRefresh is unset (audit section 4, Resetability, and SUT04-EV-0027). The E03 provisioning workflows refuse a dbRefresh or dbServer environment variable (the guard in .github/workflows/e03-measured-execution.yml and e03-environment-verification.yml). So the scheduled reset is not configured on the E03 route. | SUT-04 conditions | Not a time mechanism on this route. Recorded so that a route change reopens the question. |

### 4.5 Not proposed

- **SUT-03 web:** no condition is proposed. No deterministic stimulus has a named E01 evidence row that applies to the Chromium runner. SUT03-EV-0004 is conditioned on a Firefox version, so it does not apply to a Chromium runner by its own text. The audit's checkout date stamp (audit s4, time-dependent) has no evidence row. The stochastic candidate (p99-outlier) is recorded as present in source but not reachable (audit s4, pointing to section 5 of the audit). It is not a condition. HUMAN DECISION D-14 (wait for an evidence row).
- **SUT-03 API and SUT-05 web:** no reset realization (section 3).
- **SUT-02 API, SUT-06:** structural absence.

## 5. Metric specification (for a future analysis script)

### 5.1 Sets per condition

- **T** = valid measured attempts for the condition (protocol section 4 definition). Includes attempts whose reset or establishment failed, and attempts that were interrupted and recorded.
- **S** = attempts whose target-state verification passed. This is the TSRR numerator and the CEOR denominator.
- **M** = attempts whose stimulus-phase category equals the expected category. M is a subset of S, because the stimulus runs only after verification passes.
- **n_y** = number of S attempts in stimulus-phase category y. Sum of n_y over the category set equals S.

### 5.2 Formulas

- TSRR = S / T (defined when T is at least 1).
- CEOR = M / S (defined when S is at least 1).
- E2E-ROR = M / T (defined when T is at least 1).
- H(Y) = - sum over y with n_y > 0 of (n_y / S) x log2(n_y / S), with 0 x log 0 taken as 0. The sum runs over the pre-declared category set of size k, not over observed categories (protocol section 4). Maximum = log2(k), where k is stated with every value.
- Identity (consistency check, not a definition): E2E-ROR = TSRR x CEOR whenever S is at least 1.

### 5.3 NOT_ESTIMABLE

- If S = 0: CEOR = NOT_ESTIMABLE and H(Y) = NOT_ESTIMABLE. Neither is encoded as 0, and neither gets an interval (protocol section 4).
- TSRR = 0 and E2E-ROR = 0 are legitimate values when T is at least 1 and S or M is 0. They are not NOT_ESTIMABLE.
- If T = 0: every metric is NOT_ESTIMABLE and the cell reads "no data" with the reason (SAP section 5).
- The identity of section 5.2 does not apply when CEOR is NOT_ESTIMABLE.

### 5.4 Wilson interval

For x successes out of n (n at least 1), with z the 97.5th percentile of the standard normal distribution:

- centre = (p + z^2 / (2n)) / (1 + z^2 / n), where p = x / n
- half-width = z x sqrt(p(1 - p) / n + z^2 / (4 n^2)) / (1 + z^2 / n)
- interval = centre plus or minus half-width.

Applied to TSRR (x = S, n = T), CEOR (x = M, n = S) and E2E-ROR (x = M, n = T). No interval is computed for a NOT_ESTIMABLE value (SAP section 3). Continuity correction is not specified by the SAP; this brief recommends none (HUMAN DECISION D-05).

H(Y) has no interval in the SAP ("no test is applied to entropy values", SAP section 3). Report the point value with k and n.

### 5.5 H3 evaluation rule (for deterministic conditions only)

For a condition whose class is declared deterministic in the configuration:

- **Not evaluable** if S = 0 (CEOR NOT_ESTIMABLE) or S is below the minimum denominator of HUMAN DECISION D-06.
- **Satisfied** if M = S. Then H(Y) = 0 necessarily (all S attempts share the expected category). The script checks H(Y) = 0 as a consistency test and fails if the two disagree.
- **Falsified** if any S attempt has a stimulus-phase category other than the expected one (protocol study-design section 6, note (e): "One valid unexpected categorical outcome ... means that condition does not satisfy the preregistered H3 criterion"). The attribution rule of section 6 decides how that interacts with tooling deviations.
- A satisfied H3 means no unexpected outcome in S executions. It is not a proof of determinism. The report states the Wilson interval beside the point value (section 5.6).

### 5.6 Power note

Under independence and a per-attempt match probability q, the probability that all S attempts match is q^S. A condition with a small unexpected-outcome rate can therefore satisfy the point criterion with substantial probability at N = 50. The report must state this with each H3 result. The formula, not a value, is the content.

### 5.7 Script consistency checks

Input is one run manifest per attempt (schema v2). The script fails closed on any of the following:

- S is at most T, and M is at most S.
- Sum of n_y equals S.
- Every category label belongs to the pre-declared set of the condition, and k matches the configuration.
- The class is one of the four schema values: "deterministic", "stochastic", "time-dependent", "external dependency".
- Identifiers (HUMAN DECISION D-19; proposed E03 convention): execution_id runs exactly EX0001 to EX00N (N = 50), each with attempt 1 unless re-executed. Within an execution, attempt indices run 1, 2, ... without gaps. A re-execution is an additional attempt with its own attempt index and a recorded reason (protocol section 5, rule 5). T counts attempt records, not executions. A repeated (execution_id, attempt) pair fails the check.
- The E2E-ROR identity holds when CEOR is estimable.
- For each condition, the toolchain values of every attempt are listed. More than one value is reported as a drift confound (section 8), not excluded.

### 5.8 Fields the script reads

From schemas/run-manifest.schema.v2.json: campaign_id, condition, attempt, behavior_class, environment_type, outcome.status, outcome.outcome_category, outcome.matches_expected, target_state_id, starting_state_id, toolchain, and run_id. Identifier convention: HUMAN DECISION D-19 (section 5.7). The schema has no field for the establishment-verification result. Proposed: the phase is carried in the outcome_category label (for example S_..., ESTABLISHMENT_..., RESET_..., INTERRUPTED_...). outcome_category is a free string in schema v2, so this needs no schema change. The alternative is a schema field, which is a change to a frozen schema (HUMAN DECISION D-08).

### 5.9 Decision points in the metric spec

- **Minimum denominator (D-06):** the protocol sets no minimum. A condition whose establishment succeeds once has CEOR = 1 on n = 1. Options: (a) S must equal T (no failed establishment); (b) a pre-declared minimum k; (c) none (the literal protocol). Recommendation: (a), because it removes the case where a single success decides an H3 result.
- **Expected category for per-call random or dependent conditions (D-07):** protocol section 4 requires one predefined expected category. For a per-call random choice among documented modes, no single category is correct. Options: (a) pre-declare one category per stochastic condition, label CEOR as descriptive, and rely on H(Y) and category counts; (b) report H(Y) and category counts only, which needs a protocol decision. Recommendation: (a), labeled descriptive, with H(Y) as the primary descriptive measure.
- **No-bundle attempts (D-09):** described below.
- **Interruption after establishment:** counts in S and in H(Y) as an INTERRUPTED_ category (protocol section 5, rule 6). Section 6 covers tooling attribution.

#### No-bundle attempts (D-09)

E03 recorded two attempts that left no bundle because they failed before the executor ran (experiments/E03-resetability/README.md, Current status). Their replacements were dispatched as attempt 2 under explicit approval. Protocol rule 5 requires that both the original and the re-execution be recorded with their own attempt numbers, and rule 6 requires an interruption to be recorded as an attempt with an interruption category. Protocol section 4 defines a valid measured attempt as one "recorded with a run manifest". These rules conflict for a failure before the manifest exists. Options: (a) such an attempt is an interrupted attempt in T, recorded by a stub record with its reason, and counts against TSRR and E2E-ROR but never against CEOR; (b) it is recorded in the dispatch log only, outside T, and its attempt index is not reused. Recommendation: (a), which is the literal reading of rules 5 and 6 and keeps the failure visible in the rates.

## 6. Attribution rule for issue (xix) (options and recommendation)

HUMAN DECISION D-16 (options below; recommendation B).

Issue (xix) (protocol/study-design-v1.md, section 13) is DEFERRED-BEFORE-CAMPAIGN. The rule must be locked in each campaign configuration. Protocol section 6 already says that attributed deviations are "reported alongside the raw rates", and that attempts are not discarded (section 5, rules 4 and 5).

| Option | Description | Assessment |
|---|---|---|
| A. No rule | Every deviation counts; suspected cause is a note only. This is the protocol's current default until (xix) is fixed. | Simplest. Tooling faults count as SUT non-determinism or as interruptions, with no transparency. |
| B. Mechanical attribution beside raw rates | Pre-declared, mechanical criteria assign each attempt a label. The raw rates are unchanged and count everything. Attributed counts are reported beside them. | Consistent with protocol section 6 and rules 4 and 5. Requires criteria that do not depend on the SUT's response content. |
| C. Exclusion of tooling-attributed attempts | Attempts assigned to tooling leave the denominators. | Conflicts with protocol rules 4 and 5 (failures are outcomes; no discard) and with the definition of a valid measured attempt. Rejected. |

Recommendation: **B**, with these rules, all fixed before START:

1. **TOOLING labels** (mechanical, from harness-level records only): a runner or client exception raised before the stimulus request is sent; a browser or client crash or disconnect before the stimulus request is sent; an infrastructure interruption recorded by the workflow (runner cancelled or lost).
2. **SUT label:** any response received from the SUT after the stimulus request is sent, whatever its status or content.
3. **Uncertain goes to SUT.** An attempt whose cause cannot be assigned mechanically is labeled SUT. This mirrors the conservative tie-break that the mobile runner policy applies to uncertain runner failures (protocol/mobile-runner-policy-v2.md, section 9.4), and it works against an H3 confirmation.
4. **No response-pattern judgment.** Attribution is never made after seeing the pattern of results.
5. **Reporting:** raw primary rates count all attempts. A secondary table gives the TOOLING-labeled counts per category. No attempt leaves any denominator.
6. **H3 interaction (HUMAN DECISION D-16b):** a TOOLING interruption after establishment is an INTERRUPTED_ category, so it stops H3 from being satisfied (H(Y) above zero and M below S). Protocol section 5, rules 5 and 6, leave no alternative. Recommendation: count it, and report it with its attribution label. A tooling-labeled unexpected response is still an unexpected outcome in this reading; a human decision could change that, but that is a protocol matter, not a configuration choice.

## 7. Reuse and new work (question d)

| Area | Reusable from E03 (unchanged or with the account parameter changed) | New for E05 |
|---|---|---|
| Establishment and reset blocks | executor README 4.1 to 4.7 (reset side and establishment side); counting conventions (section 3); starting-state check (item 11); surface-control rule (item 10) | Re-ordering to reset-first; target-state verification as a gate for the stimulus |
| Instance and bundle | instance interface (section 6); output bundle layout (section 7); scrubber (section 9); HTTP client and network log (section 9); Playwright pin (section 9) | Bundle files for stimulus evidence and the classifier output |
| Implementation integrity | embedded digests and absence of unlisted Python files (section 9); export invariance rules (section 9) | Digests of the E05 realization and category file |
| Outcome classification | outcome.status values (section 3, item 9) | Stimulus realizations; projection; closed category sets; phase tags; the attribution labels of section 6 |
| Orchestration | run-condition.sh pattern (one entry point; refuses an existing manifest) | Attempt loop over N attempts on one instance (dispatch model B); per-attempt starting-state abort rule |
| Workflow gates | the fail-closed structure of e03-measured-execution.yml | Gates for E05: campaign START and authorization id; locked configuration; CS-001 mapping FROZEN where used; the category and projection file hash; schema v2; frozen prompt; N per condition; attempt indices |
| Analysis | Wilson and rate conventions of SAP section 3 | The script of section 5 (new; no bootstrap, so no random seed) |
| Manifests | run manifest schema v2 (no change) | Campaign-specific values in outcome_category labels (section 5.8) |

## 8. Pins still missing (question e)

Sources: manifests/toolchain-manifest.yaml (`tools.web_runner`, `tools.api`, `tools.schema_validator`, `tools.scripting_runtime`); experiments/E03-resetability/README.md (section "Toolchain versions" and "Execution substrate"); executor README sections 9 and 12.

1. **Chromium build.** Playwright 1.63.0 is pinned by exact version and hashes (executor README, section 9). The browser is not: the toolchain manifest says Chromium is "not hash-pinned by the study" and that its version is "recorded per run". The E03 README names the build that this Playwright version names (chromium-1243, Chrome for Testing 153.0.8010.12), but that is a named build, not a study pin. Missing: a study pin of the build identifier, and a per-run equality check against it. Over 50 attempts, browser drift is a confound.
2. **API client runtime.** `tools.api.version` reads "the runner's python3 (3.12 series on ubuntu-24.04 at preparation; exact version recorded per run)". The exact CPython version is not pinned. Missing: an exact version, and the same per-run equality check.
3. **Runner image.** The E03 README records the runner image per run and does not pin it. Missing: an image identifier pin, or the explicit decision that the per-run record is sufficient.
4. **SUT-04 JDK.** The E03 README lists "Temurin JDK 26" with no build number. Maven 3.9.14 and Node.js 24.21.0 are pinned in the same place. Missing: the JDK build.
5. **Schema validator.** `tools.schema_validator.version` is null, while the measured workflow validates manifests with ajv-cli and ajv-formats (executor README, section 12, which names ajv-cli 5 and the ajv-formats requirement). The manifest lags the workflow. Missing: exact versions of both packages in the manifest, before the first E05 validation.
6. **Analysis runtime.** `tools.scripting_runtime` pins Node.js v23.6.1 with platform "Darwin x86_64" and install date 2026-09-18. analysis/README.md rule 3 requires the runtime to be recorded before the first script run (quoted in the manifest's notes; PROTO-U06 records a past breach). Missing: confirmation that the pin holds on the host that runs the H3 script, and the script's own source hash.
7. **Dispatch procedure prompt.** No E05 prompt exists. It has to be frozen before START (experiments/README.md, Common rules: "the frozen prompt and the frozen implementation that the configuration names").

Drift check (recommended, part of the script): compare the per-attempt toolchain record of each condition; report any change inside a condition as a confound.

## 9. E04 (question f)

- **Is E04 needed for H3?** No. H3 is defined on CEOR and H(Y) (protocol section 6, note (e); SAP section 4.3 names those variables). Both are computed from E05 attempts, and E05 already records the establishment result that TSRR needs.
- **Why E04 is still listed for H3:** SAP section 4.3 lists "E04, E05" as the campaigns of H3. That is a wording gap: the criteria named there are E05 quantities. Flagged for the human research lead (see section 11, D-20).
- **What E04 would add:** the TSRR table of protocol section 4, with its own raw-data directory. TSRR is primary in E04 (protocol section 4), and E04 has its own raw-data path (experiments/README.md, Common rules: raw observations go to raw-data/<campaign-id>/).
- **Minimum E04 content if the TSRR table is wanted:** establishment-only attempts (no stimulus) for the same target states, N = 50 each, same reset, same classes of establishment outcome. Cheaper than E05, not an input to H3.
- **Options (D-20):** (a) do not run E04 now and report the establishment-phase rate of E05 as a descriptive secondary, recorded by a change-control note, because protocol section 4 assigns TSRR to E04; (b) run the minimum E04 later, after E05; (c) run a full E04. The agent-instructions file lists E04 among the resumed campaigns, so option (a) changes the resumption decision and needs the human research lead's explicit choice. Recommendation: (a) or (b), and never on the H3 critical path. The minimum campaign set decided today (E02, E05, E07 web/API, E09 and a small mobile suite) does not include E04.
- E02 establishment attempts would also yield establishment rates. That overlap is noted, not decided.

## 10. Items outside this brief

- Mobile E05 conditions (section 3).
- The E06 and E07 designs.
- Any SUT-03 condition (section 4.5).
- Any cross-ecosystem comparison of CEOR or H(Y). Such comparisons are EXPLORATORY unless pre-registered as CONFIRMATORY (SAP section 4.2). The H3 label is SUT-01 only.

## 11. HUMAN DECISIONS

Each item lists options and a recommendation. Nothing here is decided. Numbering in this draft is final.

- **D-01 (SUT-05 web):** Does the surface-agnostic ENVIRONMENT_RESTART (executor README 4.7) count as the reset for SUT-05's web surface? Protocol section 5 says "recorded for that ecosystem", not "for that surface". Options: (a) yes, with a recorded note; (b) no. Recommendation: (b) for this cycle.
- **D-02 (dispatch model):** A (fresh instance per attempt) or B (shared instance, reset between attempts). Recommendation: B, with the starting-state check and the residual list of section 4.4. Consequences of A are in section 2.2.
- **D-03 (residual state):** For SUT-01 and SUT-04 order- and booking-creating stimuli: (a) non-persistent stimuli only; (b) a process-restart reset for SUT-01 and an extended reset for SUT-04, both new realizations; (c) accept the residual with a documented confound. Recommendation: (b) for SUT-01 orders, because a whole-backend restart is the only documented way to clear orders; otherwise (a). Decide before START.
- **D-04 (performance read class):** SUT01-API-04 is deterministic by mechanism (proposed) or time-dependent (conservative alternative). Recommendation: deterministic by mechanism, with the client timeout declared well above the 3.0 s delay before START and a timeout category kept. The class follows the mechanism, not the effect on H3 (brief s.4.1).
- **D-05 (Wilson):** Continuity correction, or none. Recommendation: none, because the SAP specifies none. Fix before any analysis.
- **D-06 (minimum denominator):** (a) S = T; (b) a pre-declared minimum k; (c) none. Recommendation: (a).
- **D-07 (expected category for per-call random or dependent conditions):** SUT01-API-05, SUT01-API-06 and SUT04-API-02 only. (a) Pre-declare one category, report CEOR as descriptive, rely on H(Y) and counts; (b) H(Y) and counts only, which needs a protocol decision. Recommendation: (a). The collapsed-projection conditions (SUT02-WEB-02, SUT05-API-02) carry a declared expected category instead (config s.7).
- **D-08 (schema, phase labels, actions[]):** (a) phase carried in outcome_category labels (no schema change; recommended); (b) a schema field (change to a frozen schema). Item (c): whether the reset is also emitted as actions[] (low priority; section 2.1).
- **D-09 (no-bundle attempts):** (a) an interrupted attempt in T, with a stub record and its own attempt index (recommended); (b) outside T, dispatch log only.
- **D-10 (nominal stimuli):** SUT01-API-02 (static content) and SUT01-API-03 (the stimulus does not act on the target state). Count toward H3 with a flag (recommended), or exclude before START with a documented reason.
- **D-11 (absence-based classes):** SUT01-WEB-01, SUT02-WEB-01, and the no-evidence-row part of SUT01-API-01. Options: accept, or require a source check first. Recommendation: source check first; the SUT source is not in the repository, so the check needs the human research lead to provide or authorize the read.
- **D-12 (expected totals and selectors):** The values marked "TBD" in the configuration (required MX fields, the place-order control, the 500 body for behavior error, status codes, message text) must come from the pinned source and be recorded before START. Options: a source read under an explicit authorization, or decision by the human research lead.
- **D-13 (DateCheckValidator class):** After a source check at the pin: deterministic (request dates only) or time-dependent (any clock comparison). Recommendation: check first; time-dependent until then.
- **D-14 (SUT-03 conditions):** Wait for an E01 evidence row that names a deterministic stimulus (recommended), or add a documented-only class.
- **D-15 (mobile E05 conditions):** A separate design, gated by the mobile runner policy (brief s.3).
- **D-16 (attribution rule, issue (xix)):** A (none), B (mechanical labels beside raw rates, uncertain goes to SUT; recommended), or C (exclusion; rejected by protocol rules 4 and 5). Recommended B with the six rules of brief s.6.
- **D-16b (H3 interaction of tooling interruptions):** Count a TOOLING interruption after establishment as an INTERRUPTED_ category and report it with its label (recommended), or another rule that needs protocol treatment.
- **D-17 (canonical scenario use):** CS-001 target states only (recommended) or a new canonical scenario record (none proposed).
- **D-18 (environment type and controlled instance):** Confirm SELF_HOSTED per condition on GitHub-hosted runners (recommended), and require the controlled-instance verification run before START for each condition.
- **D-19 (identifiers):** execution_id and attempt convention. Recommended: the E03 convention (execution_id = repetition index; attempt = re-execution index within it; run_id = condition__execution__A attempt). The alternative is the schema's reading (attempt = index across the condition). Either way, record the difference from the schema description.
- **D-20 (E04):** (a) do not run E04 now; report the establishment-phase rate of E05 as a descriptive secondary with a change-control note (recommended); (b) minimum E04 later; (c) full E04. Also decide whether to correct the SAP section 4.3 wording that lists E04 for H3.
