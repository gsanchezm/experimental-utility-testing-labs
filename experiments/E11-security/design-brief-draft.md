# E11 Security: design brief

**DRAFT.** Nothing in this file freezes, starts, authorizes, or dispatches anything. Every unknown is a HUMAN DECISION (section 8) or an open verification item (section 9).

| Field | Value |
|---|---|
| Campaign | E11-security (experiments/E11-security/README.md; status NOT_STARTED) |
| Modality | Security Testing (protocol/study-design-v1.md, section 7) |
| Hypothesis | H5, descriptive count comparison of controlled non-functional ground-truth conditions per ecosystem, SUT-01 against SUT-02 and SUT-01 against SUT-03, CONFIRMATORY (H5) (protocol/statistical-analysis-plan-v1.md, sections 4.2 and 4.3; the variable spans E08, E09, E10 and E11; detection rates per condition are reported per section 5). The specialist baselines SUT-04 and SUT-05 are contextual references: EXPLORATORY unless pre-registered as confirmatory in the campaign configuration (decision E11-D-2) |
| Date | 2026-11-23 (local) |
| Basis | E01 adjudicated matrix (derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json) and the evidence of its Security Testing cells. The ground truth rule (protocol/study-design-v1.md, section 8) applies: the known condition and its expected outcome are fixed before the instrument runs |

## 1. Summary

- Security Testing is CONFIRMED Score 3 for SUT-01 and SUT-05. SUT-02 and SUT-03 are Score 2 because their E01 evidence found no documented intentional vulnerability (SUT02-EV-0019 and SUT03-EV-0025 are negative searches; SUT02-EV-0018 and SUT03-EV-0024 are stable scenarios, not known vulnerable conditions). SUT-04 is Score 2 by the human ruling E01-HR-02 (its SQL queries use bound parameters, SUT04-EV-0023; the plaintext password column of SUT04-EV-0024 was weighed in that ruling). SUT-06 is Score 1. For H5 this matches the E09 precedent: SUT-02 and SUT-03 have no ground-truth condition in E01 evidence, so the E11 count is 0 with "no data, no ground-truth condition available" (never a detection rate of zero; protocol/statistical-analysis-plan-v1.md, section 5; protocol/study-design-v1.md, issue (xiii)). The scope below is therefore SUT-01, with SUT-05 as the specialist reference.
- SUT-05 offers a catalogue of named intentional vulnerabilities with a server-side, deterministic oracle (SUT05-EV-0010, SUT05-EV-0011). The record SUT05-EV-0010 states 113 challenges; a parse of the same pinned file (1593 lines, 16 categories, as the record states) made for this brief finds 116 entries with distinct keys and names. The difference of 3 is not reconciled; the E01 record is frozen and stays unchanged, and no E11 condition depends on the total. Only a subset suits an automated method. Recommended: three conditions whose vulnerable code was read at the pinned commit.
- SUT-01 offers the account `security_glitch_user` with three mechanisms (SUT01-EV-0022 to SUT01-EV-0025). Only the IDOR (SUT01-EV-0023) is fully deterministic; the profile payload (SUT01-EV-0024) is not shown to execute as client-side XSS, and the leak messages (SUT01-EV-0025) appear in about half of the checkouts.
- Detection is judged against the known condition, never against the total number of findings a tool reports (experiments/E11-security/README.md).

## 2. What the evidence establishes

| Evidence | SUT | Mechanism | Status | Use in E11 |
|---|---|---|---|---|
| SUT05-EV-0010 | SUT-05 | catalogue of keyed challenges in data/static/challenges.yml, 16 categories (the record states 113 challenges; see section 1) | SOURCE_VERIFIED | ground-truth inventory |
| SUT05-EV-0011 | SUT-05 | `solveIf` / `solve` flip the persisted `solved` field when the exact exploitation criteria hold | SOURCE_VERIFIED | oracle that a condition was actually triggered, read from GET /api/Challenges |
| SUT05-EV-0012 | SUT-05 | some challenges carry `disabledEnv` (for example Docker and Heroku on the NoSQL ones) | SOURCE_VERIFIED | the inventory is not uniform across deployment environments; select only challenges with no `disabledEnv` |
| SUT01-EV-0023 | SUT-01 | GET and PATCH /api/orders/{id} skip the ownership check for `security_glitch_user` | SOURCE_VERIFIED | deterministic IDOR |
| SUT01-EV-0024 | SUT-01 | unsanitized script payload stored in one of three profile fields, returned verbatim by GET /api/users/me/profile | SOURCE_VERIFIED | stored-input persistence at API level only; not verified as working XSS in the web client (the audit found no dangerouslySetInnerHTML) |
| SUT01-EV-0025 | SUT-01 | about 0.5 probability of HTTP 500 with a leak-style message on checkout | SOURCE_VERIFIED | probabilistic: excluded from the recommended set |

Pins: SUT-05 commit 1618a611b173b4bf114028e6e02549950606e29d (release v20.2.0 for the packaged route); SUT-01 commit 9ca37674d374e9303912e259641ee86baf3aabe1. The web and api surfaces of both were verified as controlled instances on GitHub Actions for conditions of E03 (SUT-05 by the Packaged Distributions route); the study-level flag `controlled_instance_available` is null for SUT-01 (its mobile surfaces were not provisioned) and is true for SUT-05, so the per-condition decision goes in the campaign configuration and is confirmed by this campaign's DRY_RUN rounds.

## 3. Proposed conditions (candidate, not frozen)

Read in the SUT-05 source at the pinned commit: `routes/login.ts` builds the login query by string concatenation (line 34) and `loginAdminChallenge` is solved when the authenticated user is the administrator (line 69); `routes/search.ts` builds the product search query by string concatenation (line 23) and `unionSqlInjectionChallenge` is solved there; `server.ts` serves `/ftp` with a directory index (lines 287 to 289) and `directoryListingChallenge` is solved when the file `acquisitions.md` is requested (`routes/fileServer.ts`, line 29). `redirectChallenge` (Unvalidated Redirects) is an allowlist bypass that needs a crafted target; it is left out of the minimal set. The class each ZAP rule observes is a proposal that section 9 asks to verify.

| Condition | SUT | Known condition | Where | Class an automated method could observe | H5 count |
|---|---|---|---|---|---|
| E11-SUT01-IDOR-ORDER | SUT-01 | IDOR of SUT01-EV-0023 (the ownership check skipped for `security_glitch_user`) | GET and PATCH /api/orders/{id} | broken access control; no scan rule is expected to observe it without an authorization matrix | yes |
| E11-SUT05-SQLI-LOGIN | SUT-05 | SQL injection in the login (vulnerable code at `routes/login.ts`, line 34) | POST /rest/user/login | SQL injection | specialist reference |
| E11-SUT05-SQLI-SEARCH | SUT-05 | SQL injection in the product search (`routes/search.ts`, line 23) | GET /rest/products/search | SQL injection | specialist reference |
| E11-SUT05-DIRLIST-FTP | SUT-05 | exposed directory index of `/ftp` (`server.ts`, lines 287 to 289) | GET /ftp | directory browsing | specialist reference |

Each condition is paired with a control: the same endpoint under a user, request or order for which the condition is not active (for SUT-01 the account `standard_user`, which receives 403; for SUT-05 a request that carries no injection), so that a false positive can be recorded per condition. The README of E11 does not ask for it: it is an addition of this design.

## 4. Verification methods (candidate)

- **M1 targeted check.** A short scripted request sequence written by the study, with its expected response fixed before execution (for SUT-05 the oracle is the `solved` field of the challenge read after the request; for SUT-01 the 200 versus 403 pair). It exercises the documented condition directly.
- **M2 automated scan.** OWASP ZAP (candidate in manifests/toolchain-manifest.yaml, `tools.security`, version null; pin proposal in experiments/E11-security/zap-pin-proposal-draft.md, not approved) run against the controlled instance, restricted to the single target URL and to the one scan rule of the class in section 3, so one execution lasts seconds to minutes and N = 50 stays operationally feasible. An alert counts as detection only when its rule and its target URL equal the pre-registered expectation of the condition; other alerts are recorded and never counted.
- M1 states whether the condition is present and reachable; M2 states whether an automated method observes it. They are reported separately and never merged into one rate.

## 5. Outcome and measures

- Per condition and method: detected / not detected, counted over N executions; N = 50 (protocol/repeatability-determinism-v1.md, section 3, standard target; no mobile condition, so no reduced target).
- Per condition and method: false positive on the control (count out of N).
- Per ecosystem and condition: "no ground-truth condition available" where applicable.
- Reporting: Wilson 95% interval per proportion, descriptive, as in E05, E06 and E07; no ranking, no composite, no hypothesis label.

## 6. Environment and safety

- Active scanning is allowed only on a controlled instance (protocol/study-design-v1.md, section 10.3): SUT-05 and SUT-01 run LOCAL or SELF_HOSTED on a GitHub Actions runner, torn down after each job. No PUBLIC_HOSTED instance is ever a target. The instance record (deployment identifier, host, time window) goes in every run manifest.
- Each execution starts from a fresh instance or an equivalent reset, so that a prior solved flag or a stored payload cannot leak into the next attempt (E03 and E05 precedent).

## 7. Execution model

- GitHub Actions under CAMPAIGN-CI-WRITE-AUTH-01, one dispatch-only workflow for environment verification and one for measured execution, a frozen executor with an implementation hash, a frozen dispatch prompt, one dispatch authorization per assigned SUT (agent-governance-v6, Section 3.7), first attempt only. Non-measured DRY_RUN rounds precede the START and never enter raw-data/.

## 8. HUMAN DECISIONS (recommended defaults; each can be vetoed by its id)

| Id | Decision | Recommended default |
|---|---|---|
| E11-D-1 | Which ecosystems carry measured conditions | SUT-01 (H5 pair) and SUT-05 (specialist reference); SUT-02, SUT-03, SUT-04 and SUT-06 reported as "no data, no ground-truth condition available" (SUT-04: E01-HR-02) |
| E11-D-2 | Classification of the SUT-05 conditions | EXPLORATORY specialist reference; the alternative is a comparison pre-registered as confirmatory in the campaign configuration (statistical-analysis-plan-v1.md, section 4, rule 3), which needs its own id and a specification before the START |
| E11-D-2b | Count unit for H5 (shared with E08, E09, E10, as E09's HD-2) | each configured ground-truth condition counts once; control conditions do not count |
| E11-D-2c | The conditions of section 3 | the four rows as listed |
| E11-D-3 | Verification methods | M1 and M2, reported separately |
| E11-D-4 | Detection rule of M2 | rule and target URL equal to the pre-registered expectation; other alerts recorded, not counted |
| E11-D-5 | N | 50 per condition and method |
| E11-D-6 | Scope of the ZAP scan | one URL and one scan rule per condition, no spider, no whole-site scan |
| E11-D-7 | The probabilistic leak (SUT01-EV-0025) and the stored payload (SUT01-EV-0024) | excluded from E11 and kept as E01 evidence only |
| E11-D-8 (DECIDED 2026-11-24: Route A, answer of the human research lead; no entry made yet in manifests/toolchain-manifest.yaml, which stays null until the DRY_RUN records the installed add-ons, install date and platform) | Pin route for ZAP (experiments/E11-security/zap-pin-proposal-draft.md, section 7) | Route A: release v2.17.0 as the container image pulled by digest (amd64 manifest `sha256:c2d63bbb…`, index `sha256:9624669d…`), update checks off; Route B (archive plus hash-pinned add-ons) is the alternative |
| E11-D-9 (DECIDED 2026-11-24: the four expectations as listed, DIRLIST-FTP kept, answer of the human research lead) | Expected rule and target URL per condition (proposal, section 6), fixed from class and source before any DRY_RUN | SQLI-LOGIN and SQLI-SEARCH: rule 40018; DIRLIST-FTP: rule 0 on `/ftp/`; IDOR-ORDER: M2 not applicable (no rule of the pinned add-on set targets the class), carried by M1; DIRLIST-FTP kept even though source reading predicts no match |

## 9. Open verification items

- V-1 The exact ZAP release to pin and its rule identifiers for SQL injection, directory browsing and external redirect. READ 2026-11-24 (zap-pin-proposal-draft.md, sections 3, 5 and 6): the latest stable release is v2.17.0 (source commit `8a1bff31…`, published 2025-12-15); rule ids 40018 (SQL Injection), 0 (Directory Browsing, active), 10033 (Directory Browsing, passive) and 20019 (External Redirect) read in the sources of ascanrules 84 and pscanrules 77. STILL OPEN: the human decision on the pin (E11-D-8) and on the expectations (E11-D-9).
- V-2 Whether ZAP runs on a GitHub-hosted runner from its published container image or distribution, and the digest to pin. READ 2026-11-24: the image `ghcr.io/zaproxy/zaproxy:2.17.0` has index digest `sha256:9624669d…` and amd64 manifest `sha256:c2d63bbb…`; the version tag is mutable (the release-day image has a different digest), so only the digest is a pin; the add-ons inside an image are the marketplace state at its build (2026-11-03), derived as ascanrules 84, pscanrules 77, not observed. STILL OPEN: that a runner pulls the image by digest and that the installed add-on list read from the running instance equals the derived set and does not change across a run (DRY_RUN).
- V-3 Whether the packaged route of SUT-05 on GitHub Actions leaves the vulnerable code of the three conditions active. READ 2026-11-24 (static, pinned commit 1618a611b173b4bf114028e6e02549950606e29d): the entries `loginAdminChallenge`, `directoryListingChallenge` and `unionSqlInjectionChallenge` of data/static/challenges.yml carry no `disabledEnv`; the 19 entries that do carry it name only Docker, Heroku or Windows, so no environment detection can disable the three. STILL OPEN: that the packaged route on the runner reaches the three code paths unchanged (confirmed by the DRY_RUN, not by reading). The challenge total (113 in the record, 116 entries in the parse of the pinned file) stays unreconciled and is not used by any condition (section 1).
- V-4 That each M1 sequence flips the matching `solved` flag and that no sequence of another condition does. READ 2026-11-24 (static): the three solve predicates are distinct and tied to distinct request paths: `loginAdminChallenge` is solved after a successful login when the user id equals the administrator id (`routes/login.ts`, line 69), `unionSqlInjectionChallenge` when the product search response contains the email and the password hash of every user (`routes/search.ts`, lines 26 to 39) and `directoryListingChallenge` when the file `acquisitions.md` is requested under `/ftp` (`routes/fileServer.ts`, line 29); none of the three request paths reaches the predicate of either of the other two conditions (each path also reaches other Juice Shop predicates, which E11 does not read). STILL OPEN: the executed confirmation in the DRY_RUN, and the reset between executions (a `solved` flag persists in the instance, so each execution needs a fresh instance or an equivalent reset).
- V-5 That ZAP's restricted run against the unmodified login endpoint terminates within the job time and does not change the instance state in a way that leaks into the next execution.
- V-6 The scenario record: E11 has no cross-ecosystem canonical scenario; the comparison is per ecosystem, so no mapping record is needed unless a decision says otherwise.
- V-7 Whether rule 0 (and the passive rule 10033) match the listing that SUT-05 serves at `/ftp`. Source reading predicts no match (the `serve-index` package files hold neither `Parent directory` nor `<img =`, and the title is not `Index of /`); NOT ESTABLISHED until the DRY_RUN. A "not detected" outcome is valid and does not change the expectation.
- V-8 How a restricted ZAP run is seeded without a spider and whether the JSON login body is injected: the core defaults list query string, POST data and plain body as injectable targets and JSON among the enabled RPC variants (read in ScannerParam at v2.17.0); the API parameters for a single-request scan are not verified; the DRY_RUN decides.
- V-9 M1 and M2 never share an instance (the SQL injection scan on the login can flip `loginAdminChallenge`), and every execution starts from a fresh instance; for IDOR-ORDER the M2 column records "not applicable: no rule of the pinned set targets the class" (E11-D-9).
