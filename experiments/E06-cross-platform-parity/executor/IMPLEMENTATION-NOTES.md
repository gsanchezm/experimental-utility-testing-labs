# E06-cross-platform-parity executor: implementation notes (DRAFT, operation OP-PREP-E06-EXECUTOR)

Status: DRAFT. Not frozen, not locked, not dispatched. This file records what was built, the choices the repository did not fix, where
every selector comes from, what differs from the E07 and E09 precedent, and what only a non-measured DRY_RUN can establish.

## 1. Base of the work

The worktree was created from a public snapshot line (`95efcff4`, the origin of the public repository) and was moved with
`git reset --keep` to the canonical main `87f9e7ec`, which the task names as the base. The move discarded no change (the worktree was clean),
and the 46 public-snapshot commits it left out remain in the reflog and on origin.

## 2. Choices the repository did not fix (decided here, to be confirmed)

1. Execution model: one invocation runs the executions of one condition in sequence, one bundle each (the E07 model), not one execution per
   dispatch (the E09 model). The clean state of each execution comes from the reset of CS-007 (SESSION_RESET): a new browser context on the
   web, and an uninstall plus a new Appium session with a clean install on Android.
2. The web sign-in goes through the sign-in form of the application, with no token injected (the E03 and E09 web realizations inject a token,
   which CS-007 forbids: its precondition is the sign-in inside the scenario).
3. Market of SUT-01 on both surfaces: US with language en. The web defaults to US (frontend/src/pages/Login.jsx line 44; language from
   frontend/src/store.js line 84), and the Android build defaults to US and en (qualification/compatibility-smoke-sut01/README.md, realization
   table). The web executor clicks the market control market-US explicitly, so the market is part of the record of the scenario.
4. Identity of SUT-01: the pizza id. The web test identifiers carry the viewport suffix -desktop (width at least 768 px) or -responsive
   (frontend/src/hooks/useResponsive.js). The executor fixes the viewport at 1280 x 800, strips the suffix, and records the raw identifier beside
   the normalized id (`identity.py`, `facts.raw_identifiers`, `identity_raw`).
5. Android identity: the card label card-pizza-<id> (content description; PizzaCard.tsx line 23 at tag v1.1.8). The harness reads the labels
   through the driver, and the Python side parses the kept page source again; a disagreement is noted in the record.
6. Identity of SUT-02: the text of the first titleTV in document order (default sort NAME_ASC, MainActivity.java line 101). On the web: the text
   of the first inventory-item-name in document order (default sort az, sample-app-web src/pages/Inventory.jsx line 22).
7. Arrival on SUT-02 Android: the login screen gives way to the landing screen (productRV) with nameET absent. The catalogue is also visible
   before any sign-in (the smoke realization starts there), so the catalogue alone is not an arrival signal. The Logout Menu Item is not read
   (open item 9).
8. Non-arrival reasons and their precedence are declared in `classify.not_arrived_reason` (the first matching rule wins). The Android app cannot
   report backend answers, so a sign-in with no refusal shown within the budget is INFRA_CATALOGUE_TIMEOUT there, and disclosed as such.
9. Attribution has four values (SUT, INFRASTRUCTURE, TOOLING, UNDETERMINED) and NONE for an arrival. E07 used two (SUT, TOOLING). The added values
   keep a backend refusal distinct from a fault of the tool, which the task asks to record with its message.
10. Modality: the schema enum has no E06 value, so each execution takes the enum value of its platform (Web UI Functional, Android Native), and
    the scenario is recorded in the `scenario` field (CS-007).
11. Reset and establishment mechanisms in the manifest: SESSION_RESET and UI_FLOW (the vocabulary of the E03 executors).
12. `actions` is empty on every manifest: the Required Actions vocabulary of protocol/setup-effort-v2.md does not name the sign-in steps of this
    scenario, so no action is classified (as the E09 executor does).
13. The identity oracle switch is checked twice: the value in the conditions file must equal the value named by EXPECTED_IDENTITY_ORACLE (the
    configuration passed by the workflow), and the executor refuses otherwise. With arrival_only, no identity is read or recorded.
14. The Android harness refuses any account other than standard_user on SUT-01, because the quick-login control realizes that account only.
15. Timeouts: screen 90 s, sign-in 60 s, identity 60 s, navigation 90 s on the web (hosted cold starts), per-execution Android job budget 180 s;
    job limit 360 minutes (the GitHub maximum). A duration of 50 clean installs per Android condition is not established (open item 11).

## 3. Selectors and their sources

Every selector is taken from a pinned source; none has been verified against a hosted deployment or a device. The conditions file holds the
same list with file and line, and each one is to be verified by a non-measured DRY_RUN.

| Surface | Step | Selector | Source (file, line at the pin) |
|---|---|---|---|
| SUT-01 web | market | [data-testid="market-US"] | frontend/src/pages/Login.jsx line 208 (data-testid market-${code}); default US line 44 |
| SUT-01 web | username | [data-testid="username-desktop"] | Login.jsx line 155 (tid("username")); prefilled standard_user line 30 |
| SUT-01 web | password | [data-testid="password-desktop"] | Login.jsx line 169; prefilled pizza123 line 31 |
| SUT-01 web | sign-in | [data-testid="login-button-desktop"] | Login.jsx line 230 |
| SUT-01 web | error | [data-testid="login-error"] | Login.jsx line 225 |
| SUT-01 web | arrival | [data-testid="screen-catalog"] | frontend/src/pages/Catalog.jsx line 95; navigate to /catalog, Login.jsx line 83 |
| SUT-01 web | identity | [data-testid^="pizza-name-"] | frontend/src/components/ProductCard.jsx line 36 (pizza-name-${id}); suffix rule frontend/src/hooks/useResponsive.js |
| SUT-02 web | username | #user-name | sample-app-web src/pages/Login.jsx line 99 (id user-name) |
| SUT-02 web | password | [data-test="password"] | sample-app-web src/pages/Login.jsx line 109 (testId password); E03 precedent executor/sut02_web.py line 26 |
| SUT-02 web | sign-in | #login-button | sample-app-web src/pages/Login.jsx line 124 (testId login-button); E03 precedent sut02_web.py line 27 |
| SUT-02 web | error | [data-test="error"] | sample-app-web src/components/ErrorMessage.jsx line 16 |
| SUT-02 web | arrival | URL **/inventory.html and [data-test="inventory-list"] | sample-app-web src/pages/Inventory.jsx line 109 |
| SUT-02 web | identity | [data-test="inventory-item-name"] | sample-app-web src/components/InventoryListItem.jsx line 150; sort az, Inventory.jsx lines 20 to 22 |
| SUT-01 Android | quick login | accessibility id Standard | qualification/compatibility-smoke-sut01/README.md realization (LoginScreen.tsx lines 29, 219 to 225; qa.ts lines 58 to 72) |
| SUT-01 Android | sign-in | accessibility id Sign In | the same realization (PrimaryButton of btn-login, LoginScreen.tsx line 206) |
| SUT-01 Android | arrival | accessibility id screen-catalog | CatalogScreen.tsx line 52 (smoke realization) |
| SUT-01 Android | error | UiAutomator resourceIdMatches text-login-error | LoginScreen.tsx line 198 (testID); the resource-id mapping of React Native is open (open item 5) |
| SUT-01 Android | identity | UiAutomator descriptionStartsWith card-pizza- | frontend-mobile/src/components/PizzaCard.tsx line 23 at tag v1.1.8 (commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a) |
| SUT-02 Android | landing | id productRV | the SUT-02 smoke realization, qualification/compatibility-smoke/harness/smoke.mjs line 48 |
| SUT-02 Android | menu | id menuIV | app/src/main/res/layout/menu_header_layout.xml line 15 (commit 36b012eecdf6a2b488b9504e16b3d0c3ca9a0e7b) |
| SUT-02 Android | drawer row | accessibility id Login Menu Item | MainActivity.java line 259 (MenuItem with the label); MenuAdapter.java lines 55 to 59 |
| SUT-02 Android | fields | id nameET, passwordET | fragment_login.xml lines 68 and 129 |
| SUT-02 Android | sign-in | id loginBtn | fragment_login.xml line 190; LoginFragment.java lines 87 (listener) and 170 (loginWithEmail) |
| SUT-02 Android | arrival | id nameET absent, id productRV displayed | LoginFragment.java line 204 (MainActivity with back stack cleared) |
| SUT-02 Android | errors | id nameErrorTV, passwordErrorTV | fragment_login.xml lines 92 and 153 |
| SUT-02 Android | identity | id titleTV | app/src/main/res/layout/item_products.xml (the titleTV resource; the static reading of static-reading-oracle-draft.md) |

SUT-02 Android credential: the candidate bod@example.com with the password 10203040 is the first quick-pick pair of the pinned layout
(fragment_login.xml lines 238 to 258; strings.xml line 92). The application accepts any non-empty pair except alice@example.com
(SUT02-EV-0007), so the web account standard_user with secret_sauce would also be accepted. The choice is open item 1.

## 4. Deviations from the precedent and why

1. E09 injects a token and uses MX and es; E06 signs in through the form and uses US and en (CS-007 forbids the injection; the market is the
   one of the Android default, and the frozen mapping says one market per ecosystem).
2. E07 keeps one shared instance across the executions of a condition; E06 uses a clean state for each execution (CS-007 reset SESSION_RESET).
3. E07 and E09 emit one run per dispatch; E06 emits one run per execution, all under one condition summary.
4. The WebDriver client copies the smoke client and adds findElements and sendKeys. The copy passes its request headers to the transport; the
   smoke copy built the request options without them (its PASS observations were made that way). This is a difference of the transport.
5. The mobile-runner admissibility of the measured workflow is not a reimplementation: it is the G-7 block of
   .github/workflows/e03-measured-execution.yml (operation OP-CI-14, which implements policy v3, sections 9.5 and 9.7.9 to 9.7.11, clause by
   clause, including the remediation lineage) generated by tests/lift_g7.py between two markers of e06-measured-execution.yml. The first
   version of this draft carried a 35-line approximation (a substring match on the lineage, no read of the mirror, no selection-basis,
   gate-authorization or runner-version checks); it was replaced. The lift applies five changes, each a string replacement that must apply
   exactly once (a change of the E03 block fails tests/test_gates.py LiftTests instead of drifting silently): T1 the multiplication sign
   of one clause is written as a unicode escape; T2 and T3 the Smoke records reader and the per-condition read accept the exact QUALIFIER
   records of both SUTs (the E03 prefix test would keep SUT-01 closed, because qualification/compatibility-smoke-sut01/README.md does not
   start with qualification/compatibility-smoke/); T4 two added gates that relax nothing: no FAIL_RUNNER of the selected runner in the SUT-01
   QUALIFIER record (the lineage retains only the one SUT-02 x ios row), and the smoke entry must point to the QUALIFIER record of its own
   SUT; T5 the block runs inside try/except, so a missing record is a failed gate with ready=false. Baseline before the change: the
   unmodified E03 block on the real records of this repository gave 0 failures for SUT-02 x android and exactly the two prefix failures for
   SUT-01 x android. The checkout of the measured workflow is in cone mode, so that PUBLIC-EXPORT-MANIFEST.yaml at the root is present on the
   public tree and the hash comparisons of the lineage bridge the publication-only transformations, as the E03 and E07 gates do. The
   manifests/g7-effective-admissibility-v1.yaml record and the policy text were not re-read for this lift: the code is copied, and its
   clauses are exercised on the real records by tests/test_gates.py (opens for both Android conditions; closes on a missing lineage, an altered
   lineage hash, a second remediation authorization, a mirror FAIL_RUNNER entry, and a SUT-01 FAIL_RUNNER row).
   The rest of the gate is adapted from the E07 gate (55 checks), with these E07 gates left out because they do not apply, and why: the
   further-attempt approval (G-E07-A2): this workflow admits attempt 1 only, so a further attempt needs a corrected workflow under its own
   approval, as OP-CI-18 did for E02 (open item 16); the controlled-instance status (G-6): CS-007 is read-only, SUT-01 is hosted on both
   surfaces and SUT-02 Android runs from the local database of the pinned build, and the environment_type of each condition is the one of the
   conditions file and is recorded in the provenance; the assigned-SUT and first-execution inputs: the condition names its SUT and a dispatch
   always runs executions 1 to 50. Added for E06: the CS-007 freeze record and the COMPARABLE entry of the SUT, the pinned commit and release of
   the surface component of the condition, the conditions-file hash and the workflow-file hash in the locked configuration, and a provenance
   job that records every frozen-input hash, the pin, the environment type, and the timeout, retry and concurrency policies (the contract of
   E07: `E06-MEASURED_EXPERIMENT-<condition>-provenance`).
6. The Appium stack of both workflows is the one that passed the SUT-01 smoke: `npm ci` in qualification/compatibility-smoke-sut01/harness from
   its lockfile (exact versions and recorded integrity), APPIUM_HOME set to that directory, and the server started from it, as the smoke does
   (smoke-common.sh lines 100 to 102 and 152). The first version installed the two packages by name with --no-package-lock, which leaves the
   transitive tree floating; it was replaced. The lockfile and its package.json are in the DIGESTS block, so a change of either is refused at run
   time, and the Android jobs record the pre-runner backend probe that the smoke records (smoke_probe_backend, /health; android-job.sh does it
   for SUT-01). The driver discovery under APPIUM_HOME is the smoke's own (exercised by the run of APPIUM3-COMPAT-SMOKE-AUTH-04).
7. The workflow writes its bundles under the workspace (the runner context is not allowed in job-level env by the pinned actionlint); the
   bundles are uploaded as artifacts and never written under raw-data/.
8. The DIGESTS block covers the Python modules, requirements.txt, the Android job script, the Node harness (e06-android.mjs and wd.mjs), the
   conditions file, and the package.json and package-lock.json of the locked Appium stack (tests/embed_digests.py, EXTRA_FILES). The gate's locked hash is the hash of run-condition.sh, which embeds those
   digests, so a change of any covered file changes the entry script's verification and is refused at run time. The digests bind the
   implementation of this draft; they do not bind the workflow file itself: the locked configuration names the SHA-256 of the measured
   workflow file and the gate checks it, and the provenance records it with the commit SHA of the run.

## 5. Open items for the human research lead (none decided here)

1. The SUT-02 Android account: the candidate bod@example.com / 10203040 (the layout pair) or standard_user / secret_sauce (the web account,
   which gives the same account on both surfaces, the pairing rule's wording).
2. The web application's API origin on SUT-01 (not recorded in an E01 row); a DRY_RUN must show it. D-E06-8 assumes the same hosted backend.
3. Every web selector and the root route of both web applications: verified by a DRY_RUN only.
4. environment_type of SUT-02 web (PUBLIC_HOSTED proposed by analogy with D-E06-8) and of SUT-02 Android (EMULATED proposed).
5. The SUT-01 Android testID mapping (accessibility label or resource id) for the error element; the card labels are read as accessibility labels.
6. SUT-02 has no market or language parameter in the sources read; both SUT-02 conditions carry null for them.
7. identity_oracle is item_identity for all four conditions. arrival_only is the DP-3 fallback, recorded before the START only after a DRY_RUN.
8. The Android drawer row Log In is at position 10 of the drawer; whether a scroll is needed is a DRY_RUN question (the harness scrolls when the
   row is not found within 10 s).
9. Whether SUT-02 Android also reads the Logout Menu Item as a second signal of the authenticated state.
10. Analysis rule for ARRIVED_IDENTITY_UNREADABLE (counted as a non-parity in the parity rule as written, or a separate category).
11. Duration: the Android jobs may not fit 50 executions each within 360 minutes; a DRY_RUN observation decides.
12. Resolved in this draft: the locked hash covers the harness, the Android job script, and the conditions file (section 4.8). A new lock of
    the digests is still needed when the campaign configuration is locked.
13. Resolved in this draft: the Android jobs run npm ci from the lockfile of the SUT-01 smoke (section 4.6).
14. Resolved in this draft: the mobile-runner admissibility is the lift of the G-7 block of the E03 workflow (section 4.5). It still has to be
    rehearsed on the exported bytes of the public tree, with PUBLIC-EXPORT-MANIFEST.yaml present, before the START.
15. Dispatch authorization identifiers, the executor prompt version, the implementation hash, and the campaign configuration are null until
    the human research lead issues or locks them (governance v6, Section 3.7; the START).
16. A further-attempt path is not implemented: the workflow admits attempt 1 of executions 1 to 50 in one job per condition. An interrupted
    job (as the three HTTP 502 cases of E02) leaves no bundle and cannot be completed under this workflow. Whether to add the E07 mechanism
    (a first-execution input and a further-attempt approval record) before the START, or to correct the workflow if the case arises (the
    OP-CI-18 precedent), is a decision for the START package. The executor digest is locked at the START, so adding it later changes the lock.
17. Pairing and time. The design brief (risk 2) says both surfaces are read within the same cycle. The workflow runs one dispatch per condition
    (50 sequential executions), so execution k of the WEB condition and execution k of the ANDROID condition of an ecosystem are paired by index,
    not read at the same time; the decisions of 2026-11-21 and the frozen CS-007 say paired per index and do not say simultaneous. To limit
    drift on the hosted SUT-01, the dispatches of the two conditions of an ecosystem can be made back to back; the disclosure belongs to the
    START package.
18. The START package contract: the locked "Campaign configuration" section of the E06 README must name, for the gate to pass, each condition id,
    run-manifest.schema.v2.json, the prompt version, the implementation hash, `N = 50`, CS-007, the SHA-256 of the conditions file, the pinned
    commit and release of each surface component, and the SHA-256 of the measured workflow file; manifests/e06-campaign-start-v1.yaml
    (record_class CAMPAIGN_START, campaign_id, authorization_id) and one protocol/CHANGELOG.md START row; and each dispatch authorization
    (manifests/e06-dispatch-authorization-sut0N-v1.yaml) the fields of the E07 records (issued_by `human research lead`, assigned_sut,
    conditions, n_executions 50, attempt 1, authorization_date, campaign_start_authorization_id, frozen_inputs with the implementation and prompt
    SHA-256). Those names are proposals taken from the E07 gate; the START package may rename them before the workflow hash is locked.

## 6. What only a non-measured DRY_RUN can establish

- Whether each web selector matches on the hosted deployments, and at which viewport the testids carry the suffix.
- Whether the Android accessibility tree exposes the card labels with the expected count, and whether the testID of the error element maps to a
  resource id.
- Whether the drawer row is on screen without a scroll, and whether the release APK installs and starts on API 35 within the budgets.
- Whether the hosted backend answers in time, and whether the first catalogue item is the same across two executions in one cycle (drift).
- How long 50 executions take on each surface, and whether each job fits its budget.

## 7. Not done and why

- No DRY_RUN, no environment verification, no dispatch, no START, no freeze, and no push: each needs its own explicit approval.
- No browser was installed and no Playwright run was made; the web flows are tested through a fake page only.
- No emulator, no Appium server, and no device was used; the Android flow is tested against a fake W3C server only.
- No hosted system under test was called.
- The Playwright pins are the pins of the repository and their installation was not exercised; the Appium stack is the smoke's (section 4.6).

## 8. Review corrections and the precedent files read

Defects found by the independent review of the first version, and fixed:

1. The Python-to-Node call passed `--input <path> --out <path>`, which the harness does not parse (it reads `--key=value`), so every Android
   execution would have become a runner fault. Fixed: the Python side passes `--input=` and `--out=`. Covered by tests/test_android_path.py
   (five tests through the real harness and a fake WebDriver server, with a stub adb and a temporary APK; the manifests are validated against
   schema v2). Before this fix no Python test covered the Android path.
2. A harness fault that did not let the execution arrive was ignored by the classification (it surfaced as INFRA_BACKEND_NO_RESPONSE through
   page_loaded false). Fixed: such an execution is NOT_ARRIVED_RUNNER (RUNNER_FAULT); covered by a harness-record fixture in test_run_loop.py.
3. The digests did not cover the harness, the Android job script, or the conditions file. Fixed (section 4.8).
4. The gate fixtures did not match the real records. Fixed: (a) the dispatch authorization's implementation hash is read from
   `frozen_inputs.executor_implementation_sha256`, as the E07 dispatch record nests it; (b) the START is read from one protocol/CHANGELOG.md row
   (campaign NOT_STARTED -> IN_PROGRESS that names the START authorization id), as the E07 and E09 gates read it; (c) the Android admissibility is
   tested on the real toolchain manifest, the real smoke mirror, both real QUALIFIER records, and the real remediation lineage record
   (test_gates.py: it opens for SUT-01 and SUT-02, and closes without the lineage); (d) the observed runner version of the PASS row must equal the
   pin.
5. A measured execution with an empty prompt version is refused (repository rule 9; prompts/README.md rule 5).

Corrections made after the independent verification of this draft by the ORCHESTRATOR (the suite was re-run with PyYAML, actionlint 1.7.7 and
shellcheck 0.10.0: 128 tests passed, none skipped, before these corrections):

6. The Android gate was an approximation of G-7 and its tests used minimal fictitious mobile records that hid the difference: replaced by the lift
   (section 4.5) and by tests on the real mobile records, with nine one-change mutations and a drift test.
7. The measured workflow checked out in non-cone mode, which omits the root file PUBLIC-EXPORT-MANIFEST.yaml: on the public tree the lineage hash
   comparisons would have been made on exported bytes without the export manifest and would have failed there only. Both workflows now use cone
   mode, as the E03 and E07 workflows do.
8. The gate lacked checks that the E07 gate has (START record, locked configuration items, dispatch authorization fields, mapping, workflow
   revision) and the measured provenance was five fields: both completed (section 4.5).
9. The Appium install floated its transitive tree: replaced by npm ci from the smoke lockfile (section 4.6).
10. The Python suite ran its unclosed-file warnings as ignored exceptions: the tests that opened files without closing them were corrected.

Precedent files read for this review:

- E07 and E09 measured workflows: their bundles are named `E07-MEASURED_EXPERIMENT-<condition>-provenance` and
  `E09-MEASURED_EXPERIMENT-<condition>-<execution>-A<attempt>-provenance` (upload-artifact at e07-measured-execution.yml lines 431 to 433 and
  e09-measured-execution.yml lines 329 to 331). The bundles of this draft follow the same pattern: `E06-MEASURED_EXPERIMENT-<condition>-run<id>-a<attempt>`
  for measured runs and `E06-NON_MEASURED-<condition>-run<id>-a<attempt>` for the verification workflow. The Python version of the draft is 3.12
  (E07 also uses 3.11 and 3.12); the Node version is the smoke pin 22.23.2 (E07 uses node 24 in its own jobs).
- E07 and E09 gates: the START is one protocol/CHANGELOG.md row (e07-measured-execution.yml line 230; e09 line 158); the dispatch
  authorization carries the implementation hash under frozen_inputs (manifests/e07-dispatch-authorization-sut01-v1.yaml).
- The SUT-01 smoke: APPIUM_HOME is the harness directory (smoke-common.sh line 102); the server is started from that directory with npx
  (line 152); the pre-runner backend probe (smoke_probe_backend, lines 131 to 148) is reproduced in android-job.sh for SUT-01.

Precedent files NOT re-read in full: manifests/g7-effective-admissibility-v1.yaml and policy v3 sections 9.5 and 9.7.9 to 9.7.11 (the gate code
that implements them is copied, section 4.5); governance v6 section 3.7 (only the field names of the E07 dispatch record were compared with the
fixtures).
