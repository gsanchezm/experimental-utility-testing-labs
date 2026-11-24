# E11-security: campaign configuration (DRAFT-1, 2026-11-24 UTC, 2026-11-23 local)

**DRAFT. Nothing here locks, starts, authorizes, or dispatches anything.** The "Campaign configuration" is locked only at the campaign START under explicit human authorization (protocol/change-control-v1.md, section 7). Working basis: design-brief-draft.md (decisions E11-D-1 to E11-D-9; the recommended defaults of its section 8 are awaiting the human research lead's re-confirmation (the earlier acceptance has no exact text on record), while E11-D-8 and E11-D-9 were decided on 2026-11-24 UTC, manifests/campaign-execution-decisions-v19.yaml, and E11-D-10 to E11-D-15 on the same day, v20) and zap-pin-proposal-draft.md. The machine-readable mirror of section 4 is conditions-draft.json. Every item marked HUMAN DECISION has a recommended default and is open until answered.

## 1. Scope in one table

| Item | Value |
|---|---|
| Hypothesis | H5, descriptive count comparison, CONFIRMATORY for SUT-01 against SUT-02 and SUT-03 (the count of SUT-02 and SUT-03 is 0 with "no data, no ground-truth condition available"); SUT-05 conditions are an EXPLORATORY specialist reference (E11-D-2). No support criterion is frozen for H5 and none is invented |
| Ecosystems with measured conditions | SUT-01 (one condition) and SUT-05 (three conditions) (E11-D-1) |
| Reported as "no data" | SUT-02, SUT-03, SUT-04 (E01-HR-02), SUT-06 |
| Methods | M1 targeted check; M2 OWASP ZAP restricted run; reported separately, never merged (E11-D-3) |
| N | 50 per cell (protocol/repeatability-determinism-v1.md, section 3; E11-D-5); attempt 1 only |
| environment_type | SELF_HOSTED on a GitHub-hosted runner for every measured cell; LOCAL only for DEVELOPMENT, SYNTAX_VALIDATION, TOOL_QUALIFICATION, SMOKE, ENVIRONMENT_VERIFICATION or DRY_RUN, never entering a measured dataset |
| Run manifest | schemas/run-manifest.schema.v2.json (HUMAN DECISION E11-D-10, default: as E05 and E09) |
| Execution | GitHub Actions under CAMPAIGN-CI-WRITE-AUTH-01; one dispatch-only environment-verification workflow and one dispatch-only measured workflow; a frozen executor with an implementation hash; a frozen dispatch prompt; one dispatch authorization per assigned SUT (protocol/agent-governance-v6.md, Section 3.7) |

## 2. Cells (condition × method × kind)

Each condition has a control (brief, section 3), so a false positive is recorded per condition and method. A cell is the unit of one job and of N = 50.

| Cell id | SUT | Condition | Method | Kind | Counts in H5 |
|---|---|---|---|---|---|
| E11-SUT01-IDOR-ORDER-M1 | SUT-01 | IDOR on GET /api/orders/{id} (SUT01-EV-0023) | M1 | CONDITION | yes (count 1 for SUT-01) |
| E11-SUT01-IDOR-ORDER-M1-CTRL | SUT-01 | same request as `standard_user` | M1 | CONTROL | no |
| E11-SUT05-SQLI-LOGIN-M1, -M2 | SUT-05 | SQL injection in the login | M1, M2 | CONDITION | specialist reference |
| E11-SUT05-SQLI-SEARCH-M1, -M2 | SUT-05 | SQL injection in the product search | M1, M2 | CONDITION | specialist reference |
| E11-SUT05-DIRLIST-FTP-M1, -M2 | SUT-05 | exposed directory index of `/ftp` | M1, M2 | CONDITION | specialist reference |
| the six SUT-05 cells above with suffix `-CTRL` | SUT-05 | control (section 3) | M1, M2 | CONTROL | no |

Totals: 14 cells, 700 executions (SUT-01: 2 cells, 100 executions; SUT-05: 12 cells, 600 executions). M2 is not configured for IDOR-ORDER (E11-D-9: no rule of the pinned add-on set targets the class); the cell is recorded as "M2 not applicable", never as a detection failure. HUMAN DECISION E11-D-10b (default: all 14 cells; the alternative is controls for M2 only, 10 cells and 500 executions, which leaves the M1 oracle without a negative check).

## 3. Per-condition realization (candidate; the exact strings are fixed at the lock)

| Condition | M1 sequence (expected response fixed before execution) | M1 oracle | M2 expectation (E11-D-9) | Control |
|---|---|---|---|---|
| SQLI-LOGIN | POST /rest/user/login with an injection payload in the email field | GET /api/Challenges: `loginAdminChallenge` solved becomes true (user.id equals the administrator id, `routes/login.ts`, line 69) | rule 40018 on `POST /rest/user/login` | M1: a valid non-administrator login, flag stays false. M2: a login-like endpoint without a concatenated SQL query (TBD, V-10) |
| SQLI-SEARCH | GET /rest/products/search?q= with a UNION payload | `unionSqlInjectionChallenge` solved (`routes/search.ts`, lines 26 to 39: every user's email and password hash in the response) | rule 40018 on `GET /rest/products/search` | M1: a benign search term, flag stays false. M2: a search-like endpoint without a concatenated SQL query (TBD, V-10) |
| DIRLIST-FTP | GET /ftp and GET /ftp/acquisitions.md | `directoryListingChallenge` solved (`routes/fileServer.ts`, line 29: the file `acquisitions.md` is requested) | rule 0 on `/ftp/` (source reading predicts no detection; V-7) | M1: GET of another file under /ftp, flag stays false. M2: a path with no directory index (TBD, V-10) |
| IDOR-ORDER | as `security_glitch_user`, GET /api/orders/{id} of an order created by another user (SUT01-EV-0023; the PATCH of the same evidence is not executed in the default, E11-D-15) | HTTP 200 with the other user's order | none: M2 not applicable | `standard_user`, same order: HTTP 403 |

Payload strings, the account names, the order creation of the establishment block and the control endpoints are not written here: payloads are fixed at the lock from the documented challenge class and recorded before any measured execution; the control endpoints of M2 need a source reading (V-10, new) and a decision (E11-D-12). Nothing in this table is derived from a DRY_RUN outcome.

## 4. Blocks of one execution and outcome categories (candidate)

Blocks, in order: **reset** (SUT-05: restart of the instance process in its own session and process group; SUT-01: restart of the backend process, the D-03 b reset of E05 API-01; both as in E05), **starting-state check** (SUT-05: the condition's challenge `solved` is false and the instance answers; SUT-01: the prerequisite order exists), **method** (M1 sequence; or M2: a fresh ZAP container from the pinned image digest, update checks off, one seeded request, one restricted active scan, alerts read, container removed), **classification**, **record** (run manifest last). M1 and M2 never share an instance, and one execution never reuses a ZAP session of another (V-9).

| Phase | Categories (proposal; attribution TOOLING or SUT as in E05) |
|---|---|
| reset, starting state | RESET_FAILED, RESET_STARTING_STATE_NOT_REACHED |
| M1 | M1_ORACLE_FLIPPED, M1_ORACLE_NOT_FLIPPED, M1_RESPONSE_OTHER; for IDOR: M1_IDOR_BYPASS_OBSERVED (200), M1_IDOR_BLOCKED (403), M1_RESPONSE_OTHER |
| M2 | M2_EXPECTED_ALERT (an alert whose rule id and target URL equal the expectation), M2_NO_EXPECTED_ALERT (other alerts are recorded and never counted, E11-D-4), ZAP_START_FAILED, ZAP_API_ERROR, ZAP_SCAN_TIMEOUT |
| any | INTERRUPTED_ (TOOLING before the request is sent, SUT after) |

For a CONTROL cell the expected category is the "not" category; the "flipped" or "expected alert" category on a control is a false positive. Per cell the record is the count of each category out of N (descriptive; Wilson 95% interval per proportion, as E05 to E07); there is no composite, ranking or hypothesis label.

## 4b. Matching rules (defined here, before any DRY_RUN; a DRY_RUN may expose a defect but does not choose them)

- **M2 match.** An alert counts as the expected detection only when all three hold: its `pluginId` equals the condition's expected rule id (string comparison); its request `method` equals the expected method (POST for SQLI-LOGIN, GET for SQLI-SEARCH and DIRLIST-FTP); and its `url`, after normalization, equals the condition's expected path. Normalization: scheme, host and port are replaced by the instance base URL, the query string and the fragment are removed (the alert carries the attack request's URL, so a GET injection has the payload in the query), and the path is compared exactly, a trailing slash included (rule 0 requests `/ftp/`, so the expected path is `/ftp/`). Every other alert is recorded in the evidence with its rule id, method and normalized path and is never counted (E11-D-4).
- **M1 match (SUT-05).** The category is decided by the `solved` field of the condition's challenge key read from GET /api/Challenges after the sequence, not by the response of the sequence itself (SUT05-EV-0011).
- **M1 match (IDOR-ORDER).** The response of the **GET** /api/orders/{id} decides the category: 200 is M1_IDOR_BYPASS_OBSERVED, 403 is M1_IDOR_BLOCKED, any other status is M1_RESPONSE_OTHER. The PATCH of SUT01-EV-0023 is not executed in the default (same predicate, and it would change the other user's order); HUMAN DECISION E11-D-15 (default: GET only).

- **ZAP settings (E11-D-6 and E11-D-8).** The scan policy is created with no attack strength and no alert threshold argument, so the release defaults of ZAP v2.17.0 apply to the one enabled rule; the injectable targets, the enabled RPC variants and the duration limits are the defaults of the pinned core (`TARGET_INJECTABLE_DEFAULT`, `TARGET_ENABLED_RPC_DEFAULT`). None is tuned to an outcome. Every M2 execution records what it ran with (the enabled scanner row with its `attackStrength` and `alertThreshold`, the two option views and the two duration limits) in the observation of the `method` step, so that a later change of a default is visible.

## 4c. Source reading V-10 (2026-11-24 UTC; static, pinned commits; fixes the payloads and the control endpoints, E11-D-12)

SUT-05 at `1618a611b173b4bf114028e6e02549950606e29d` (`server.ts` route list, `routes/login.ts`, `routes/search.ts`, `routes/fileServer.ts`, `routes/securityQuestion.ts`, `routes/resetPassword.ts`, `models/product.ts`); SUT-01 at `9ca37674d374e9303912e259641ee86baf3aabe1` (`backend/constants.py`, `backend/routers/checkout.py`). Strings below are candidates fixed at the lock; none comes from a DRY_RUN.

| Condition | M1 sequence (candidate strings) | M1 control | M2 control endpoint (selected by this reading) |
|---|---|---|---|
| SQLI-LOGIN | `POST /rest/user/login` `{"email": "' or 1=1--", "password": "x"}`; the query is built by concatenation (`login.ts`, line 34) and the predicate is `user.id === users.admin.id` (line 69); the first user of `data/static/users.yml` is the administrator | `POST /rest/user/login` with the documented account `mc.safesearch@juice-sh.op` / `Mr. N00dles` (the account of E05-SUT05-API-01): `loginAdminChallenge` stays unsolved | `POST /api/Users` (JSON body with email, password and passwordRepeat; read at `server.ts`: handlers that trim and validate the body at lines 427 to 441, then the generic REST resource that line 503 declares for the user model, whose own code was not read; no rate limit applies to the route among the ones read: reset-password at line 362 and the 2FA routes at lines 478 to 491); NOT `POST /rest/user/reset-password`, which `server.ts` (line 362) rate-limits to 100 requests per 5 minutes, so a ZAP run would be answered with 429 and the control would measure the limiter, not the absence of the class. Caveat: ZAP creates users on the instance; every execution starts from a fresh instance |
| SQLI-SEARCH | `GET /rest/products/search?q=qwert')) UNION SELECT id, email, password, '4', '5', '6', '7', '8', '9' FROM Users--`; the query is built by concatenation (`search.ts`, line 23); the predicate needs every user's email and password hash in the response (lines 26 to 39); 9 columns assumed (6 declared columns in `models/product.ts` plus createdAt, updatedAt and deletedAt; the query itself filters on `deletedAt`) | `GET /rest/products/search?q=apple`: `unionSqlInjectionChallenge` stays unsolved | `GET /rest/user/security-question?email=` (Sequelize `where: { email: email?.toString() }`, `routes/securityQuestion.ts`; not rate-limited) |
| DIRLIST-FTP | `GET /ftp/` then `GET /ftp/acquisitions.md`; the flag is flipped by the file request (`fileServer.ts`, line 29), not by the listing, so the oracle shows that the exposed file is served; the status and file names of the listing are recorded descriptively | `GET /ftp/legal.md`: `directoryListingChallenge` stays unsolved | `/assets/` (served by `express.static`, `server.ts`, line 307, which has no directory index; what the application answers for a directory path without an index is not read here and is recorded in the DRY_RUN) |
| IDOR-ORDER | owner `performance_glitch_user` logs in (password `pizza123`), `POST /api/cart` then `POST /api/checkout`, keeping the order id; then `security_glitch_user` logs in and `GET /api/orders/{id}` (the GET decides, E11-D-15). The owner is `performance_glitch_user`, whose only documented effect is a 3 s delay per call (`constants.py`), so that the control requester can be `standard_user` as the brief states | the same GET as `standard_user`: expected 403 (`checkout.py`, line 157: the requester's username differs from the owner's and its behavior is not `security_glitch`) | not applicable |

Reading result that touches the expectations: for DIRLIST-FTP the flag is the oracle of the file request, so M1 shows that the file is served and M2 (rule 0, predicted no alert, V-7) asks a different question (does an automated rule observe a listing); the two are reported separately (E11-D-3).

## 5. Pins and instances

- SUT-01: commit 9ca37674d374e9303912e259641ee86baf3aabe1 (web and api verified as controlled instances for E03 and E05 conditions; the E11 verification is its own, E11-D-11).
- SUT-05: commit 1618a611b173b4bf114028e6e02549950606e29d, release v20.2.0 by the Packaged Distributions route (verified for E03 and E05 conditions; the E11 verification is its own and must show the three vulnerable paths reachable, V-3 and V-4).
- ZAP: v2.17.0 as the image by digest, Route A (E11-D-8): amd64 manifest `sha256:c2d63bbb2d907a5c5257914fb20e26e969c92b25f265def7f89f08203f912882` (index `sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af`); the installed add-on list, the install date and the platform are read in the DRY_RUN and recorded before any entry is made in manifests/toolchain-manifest.yaml. Update checks off (`start.checkForUpdates=false`, no `-addonupdate`); the list before and after a run must be equal.
- Python and Playwright: not needed (no browser is configured; M1 and M2 are HTTP).

## 6. HUMAN DECISIONS opened by this draft (recommended defaults)

| Id | Decision | Default |
|---|---|---|
| E11-D-10 | Run-manifest schema; the cell list of section 2 (E11-D-10b) | schema v2; all 14 cells, 700 executions |
| E11-D-11 | Environment verification of E11's own on GitHub Actions for SUT-01 and SUT-05; `controlled_instance_available` in the SUT manifest unchanged | an E11 verification (a DRY_RUN round per cell family) before the START; the per-condition decision goes in the configuration |
| E11-D-12 | The M2 control. CHANGE from the brief: the brief defines a control as the same endpoint with no injection, which has no meaning for ZAP because ZAP generates its own attacks; this draft proposes instead a different endpoint of the same instance whose parameter is not concatenated into a SQL query (or, for DIRLIST-FTP, a path with no directory index). That control differs from the condition in the endpoint as well as in the vulnerability, so it measures a false positive on a non-vulnerable endpoint, not on the same endpoint. The M1 controls (a benign request on the same endpoint) keep the brief's definition | endpoints selected by a source reading of the pinned SUT-05 before the lock (V-10), recorded with sources, none chosen from a DRY_RUN outcome; alternative: no M2 control, the false-positive information then being only the other alerts recorded and not counted |
| E11-D-13 | A frozen dispatch prompt ORCHESTRATOR-E11-security-v1 and an E11 implementation lock of its own (E09 HD-17 and HD-18 precedent) | yes |
| E11-D-14 | Job layout: one job per cell, N sequential executions each, fresh instance and fresh ZAP per execution | CONDITIONAL: yes if a DRY_RUN times one M2 execution (instance restart, JVM start, one restricted scan) so that 50 sequential executions fit the job time limit with margin; otherwise a smaller chunk per job is decided then |
| E11-D-15 | IDOR-ORDER M1: the GET decides, the PATCH is not executed | GET only |

## 7. Open before the START package

1. DONE 2026-11-24 UTC: the source reading for the control endpoints and the payloads (section 4c); the strings are fixed at the lock.
2. The executor and the two workflows (not written; drafts only) and the DRY_RUN rounds that verify: that the pinned image runs and pulls on the runner (V-2), the installed add-on list (V-2), the three vulnerable paths (V-3, V-4), the seeding and the JSON login body (V-8), the `/ftp` outcome (V-7), the reset between executions (V-9).
3. The START itself, the dispatch authorizations, the freeze: each needs the human research lead's explicit approval.
4. The pin record in manifests/toolchain-manifest.yaml (after the DRY_RUN has the add-on list, the install date and the platform).
