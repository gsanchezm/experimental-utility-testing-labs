# E02-state-establishment executor -- DRAFT (not locked, not started)

| Field | Value |
|---|---|
| Status | **DRAFT.** Nothing here starts, configures, authorizes, or dispatches a campaign. The implementation hash is written by `tools/refresh_embedded_digests.py` and is locked only at the campaign START, which needs a human approval. |
| Campaign | E02-state-establishment (`experiments/E02-state-establishment/README.md`, status NOT_STARTED) |
| Scenarios | CS-003 (FROZEN 2026-11-02, `experiments/scenario-mappings/CS-003.yaml`); CS-004 (FROZEN 2026-11-06, `experiments/scenario-mappings/CS-004.yaml`; WEB only; SUT-01, SUT-02, and SUT-03 COMPARABLE) |
| Derived from | The E03 executor (`experiments/E03-resetability/executor/`) by copying. Nothing is imported from the E03 path at run time. The E03 files are the reset-side source; this executor does not share their hash. |
| Design sources | `experiments/E02-state-establishment/design-brief-draft.md` (recommendations HD-1 to HD-23), `h2-reset-side-options-draft.md` (reset-side options; they change nothing of the establish side), `protocol/setup-effort-v2.md`, sections 4 to 6 and 10; `protocol/agent-governance-v6.md`, Section 3.7 (FROZEN-PRE-DATA 2026-11-06) |
| Gates | `.github/workflows/e02-measured-execution.yml` (measured, dispatch-only) and `.github/workflows/e02-environment-verification.yml` (DRY_RUN, dispatch-only) |
| Companion | `IMPLEMENTATION-NOTES.md` (deviations, human decisions, what is not done) |

## 1. Layout

| Path | Content |
|---|---|
| `run-condition.sh` | Entry point. Checks the embedded digests of every implementation file and that no unlisted Python file exists under `executor/executor/`, refuses an existing manifest, then runs `python3 -m executor.run`. |
| `executor/common.py` | Run context, evidence, scrubber, HTTP client, counted actions (`Run.action`), uncounted steps (`Run.step`), run manifest. Rewritten from the E03 `common.py` for the establish-side counting. |
| `executor/run.py` | Entry point: input checks, the realization lookup, `execute()` (maps stops to outcomes). |
| `executor/instance.py`, `executor/web.py` | Copied from the E03 executor (labels changed). |
| `executor/sut01.py` ... `sut05.py` | The realizations (establish side): `cs003_api`, `cs003_web`, `cs004_web` per SUT, and `SPEC` per condition. |
| `requirements.txt` | Copied from the E03 executor: Playwright for Python 1.63.0 and its declared dependencies, by exact version and wheel hashes. |
| `tools/refresh_embedded_digests.py` | Computes the sha256 of every implementation file and rewrites the `DIGESTS` block of `run-condition.sh`. Run after every edit of `executor/*.py`. |
| `tests/` | Unit, contract, gate-matrix, digest, hygiene, and workflow tests (section 9). |

## 2. Conditions and realizations

The ten conditions are the design brief's set (HD-10): seven CS-003 conditions and three CS-004 conditions. CS-004 maps WEB only, for SUT-01, SUT-02, and SUT-03 (CS-004 DP-4; brief HD-4); no API, mobile, SUT-04, or SUT-05 condition exists for CS-004.

| Condition | Surface | Scenario | Counted operations (planned) | Establishment mechanisms | Configured |
|---|---|---|---|---|---|
| `E02-CS003-SUT01-API` | api | CS-003 | 3: login; `POST /api/cart`; `GET /api/session` (verification) | PREDEFINED_ACCOUNT, API_SEED | yes |
| `E02-CS003-SUT01-WEB` | web | CS-003 | 6: open `{web}/`; API login; storage injection; `POST /api/cart`; open `/checkout`; read Checkout (verification) | PREDEFINED_ACCOUNT, API_SEED, APP_STATE_CONTROL, DIRECT_ROUTE | yes |
| `E02-CS003-SUT02-WEB` | web | CS-003 | 6: open `{web}/`; fill user; fill password; submit; add to cart; read badge (verification) | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | yes |
| `E02-CS003-SUT03-WEB` | web | CS-003 | 7: open `/signin`; select user; enter password; sign in; buy product 1; close float cart; read closed-cart bag (verification) | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | yes |
| `E02-CS003-SUT04-API` | api | CS-003 | 3: login (token cookie); `POST /booking/`; `GET /booking/{id}` (verification) | PREDEFINED_ACCOUNT, API_SEED | yes |
| `E02-CS003-SUT04-WEB` | web | CS-003 | 13: open `/admin`; fill user; fill password; submit; open reservation page; open form; four fields; Reserve Now; open `/admin/room/1`; read rows (verification) | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | yes |
| `E02-CS003-SUT05-API` | api | CS-003 | 3: login (token and basket id); `POST /api/BasketItems`; `GET /rest/basket/{bid}` (verification) | PREDEFINED_ACCOUNT, API_SEED | yes (its BasketItems route is SOURCE_VERIFIED only) |
| `E02-CS004-SUT01-WEB` | web | CS-004 | 2: open `/checkout` directly; read Checkout (verification). The seeding (login, cart line, storage injection) is the uncounted precondition. | PREDEFINED_ACCOUNT, API_SEED, APP_STATE_CONTROL, DIRECT_ROUTE | yes |
| `E02-CS004-SUT02-WEB` | web | CS-004 | 4: read badge (verification); click the cart link; click Checkout; read the step-one view (verification). The seeding (first load, sign-in, add-to-cart of the backpack) is the uncounted precondition. | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | yes (selectors read from the pinned source on 2026-11-06; verified only by a DRY_RUN) |
| `E02-CS004-SUT03-WEB` | web | CS-004 | 2: click Checkout in the open float cart; read the order summary of the checkout view (verification). The seeding (sign-in, buy of product 1) is the uncounted precondition. | PREDEFINED_ACCOUNT, DIRECT_ROUTE, UI_FLOW | yes (selectors read from the pinned source on 2026-11-06; verified only by a DRY_RUN) |

Counts against the mapping's indicative counts are listed in `IMPLEMENTATION-NOTES.md`, section 3.

## 3. Counting conventions (setup-effort-v2, sections 4 and 5)

1. **Unit.** One counted action is one experimenter-initiated operation with an observable effect: one fill, one selection, one click, one page load or route change, one API request, one read used as verification. A multi-step control inside one user operation (the two clicks of an option selection) is one action. Each operation counted here is a `with run.action(...)` statement in the realization; the test `test_realization_contract.py` counts them from the source.
2. **Authentication counts** (rule 3): every login, token acquisition, credential entry, and submit of a login form.
3. **Verification counts** (rule 8) and is classified by its class (API action, UI action, navigation action); its `actions.json` mechanism is null. A verification read that completes is `SUCCESS` whatever it shows; the run outcome carries the predicate (SUCCESS when it holds, FAILURE when it does not). A verification that cannot be obtained stops the run as INCONCLUSIVE.
4. **Not counted:** the precondition (CS-004 seeding; the first page load of a CLEAN realization is counted, see IMPLEMENTATION-NOTES HD-15), the declared starting-state check (a read; a failure gives ABORTED), provisioning of the instance, the between-run reset (a fresh instance is provisioned for each run in the measured job), and evidence capture.
5. **Outcome per action:** SUCCESS, PARTIAL_SUCCESS (counted once; the establishment continues), or FAILURE. A FAILURE, or an exception inside a counted operation, stops the establishment: no further operation is performed (no retry is predeclared; `is_retry` is false for every action). The run outcome is then FAILURE.
6. **Run outcome:** SUCCESS when the predicate of the final verification holds; FAILURE when it does not hold, or when the establishment stopped on a failed operation; INCONCLUSIVE when the verification could not be obtained; ABORTED when the declared starting state does not hold (the counted operations performed before the check are kept); ERROR for a runner fault or the watchdog.
7. **Mechanisms.** `establishment_mechanisms` (run level, mandatory, non-empty; schema vocabulary) is the realization's declared list. Per-action mechanisms are in `actions.json`; the run-manifest action records carry no mechanism field (the schema forbids it).
8. **Duration** (secondary, setup-effort-v2 section 6.1): from the start of the first counted action to the end of the last one; recorded in `actions.json` as `establishment_duration_s`, never in the manifest.

## 4. Starting state and between-run reset

- The starting state is declared per realization: CS-003 CLEAN_SESSION (no authenticated session, no cart, no basket item, no booking with this run's guest names). The check is an uncounted read; where the identity is needed to read the state (the basket id, the cookie token, the bag that appears for a signed-in actor), the check follows the identity action (login). For SUT-02 CS-003 the cart link exists only after the login, so the login form is read on the first load (an uncounted precondition) and the cart half of the state after the authentication, before the add-to-cart (IMPLEMENTATION-NOTES HD-N).
- Between runs, each measured job provisions a fresh instance (the E03 provisioning steps), so the reset is provisioning and is not counted. The CS-003 and CS-004 reset realizations (session reset, Reset App State, Sign-Out, booking delete, process restart) are not executed. This is a DRAFT decision (IMPLEMENTATION-NOTES HD-R).

## 5. Refused, not configured

`run.py` refuses (exit 2, no manifest) a condition whose realization is not configured (`SPEC.configured` False). Today none is: the two CS-004 conditions for SUT-02 and SUT-03 were refused until 2026-11-06, because their checkout-entry and checkout-view selectors (and, for SUT-03, the route from the float cart) were not in the E03 records or the E01 rows. On the human research lead's decision of 2026-11-06 (`manifests/campaign-execution-decisions-v3.yaml`, OPEN-1) they were read from the pinned sources (SUT-02 commit `60fdd634`; SUT-03 commit `7ab934d7`; the source citations are in the module docstrings and in `CITATIONS_CS004`) and the two realizations were configured. Nothing was run: the selectors are verified only by a DRY_RUN, which must precede the lock.

## 6. Embedded digests (the E03 mechanism)

`run-condition.sh` embeds the sha256 of every implementation file (`executor/executor/*.py` and `requirements.txt`) in its `DIGESTS` block and verifies them, and refuses any unlisted Python file under `executor/executor/`, before anything else. The block is written by `tools/refresh_embedded_digests.py` from the file bytes; no digest is typed. The implementation hash that the measured workflow compares with the locked configuration is the sha256 of `run-condition.sh` itself. Procedure after any edit: (1) run `python3 tools/refresh_embedded_digests.py <executor dir>`; (2) run the tests; (3) record the new `run-condition.sh` hash in the configuration at the START. Export invariance: each implementation file must survive the publication transformations unchanged. Checked on the canonical tree on 2026-11-06 (read-only scan): none of the 28 files of the executor, the dispatch procedure prompt, CS-003, CS-004, the two E02 workflows, and the E02 README contains a token that the publication builder aliases or any vendor name, so the builder has nothing to rewrite in them; the export build itself must record each of them as UNCHANGED.

## 7. Gates (the workflows)

The measured workflow fails closed unless all of the following hold (gate names of `IMPLEMENTATION-NOTES.md`, section 5, map each to the brief's identifiers):

- ref `main`, first attempt, input attempt 1, condition of the ten, condition and SUT agree, EXnnnn;
- E02 status IN_PROGRESS in `manifests/study-manifest.yaml`; exactly one START row in `protocol/CHANGELOG.md` carrying the START authorization id;
- the locked "Campaign configuration" section of the E02 README (it does not exist today) names the condition, schema v2, the prompt version, the implementation hash, the requirements hash, and the H2 comparison specification; it does not cite CS-002;
- CS-003 and CS-004 are FROZEN (the campaign requires both); the SUT is COMPARABLE on the condition's scenario for its surface;
- `protocol/agent-governance-v6.md` is FROZEN-PRE-DATA or AMENDED **and** contains Section 3.7 (the per-SUT dispatch authorization);
- one ISSUED, unrevoked E02 dispatch authorization for the SUT (`manifests/e02-dispatch-authorization-sut0N-v*.yaml`, record class `E02_DISPATCH_AUTHORIZATION`) names this dispatch id, the START id, the implementation hash, the prompt version and its SHA-256, attempt 1, the condition with N executions, and the execution within N;
- a CONTROLLED, GitHub-Actions-VERIFIED controlled instance of the condition id with environment type SELF_HOSTED or LOCAL (`experiments/E02-state-establishment/controlled-instance-status.yaml`, which does not exist today);
- the frozen prompt file exists; the implementation hash equals the input and the configuration.

Today, on the repository as it stands (2026-11-06, canonical `main`), the measured gate refuses with 17 failing gates and 16 passing ones, all of which belong to the state before the START (`IMPLEMENTATION-NOTES.md`, section 6). The verification workflow checks the working prompt `prompts/working/<version>.md` (a frozen copy, if one exists, must be byte-identical; CI correction OP-CI-17) and not the frozen one; its gate passes on the repository as it stands, so a DRY_RUN needs only the human research lead's approval of the dispatch.

## 8. Entry point refusals (no manifest)

`run.py` refuses: an unknown condition; a condition of another SUT; a record class outside MEASURED_EXPERIMENT, DRY_RUN, DEVELOPMENT; MEASURED_EXPERIMENT outside `e02-measured-execution.yml`; an execution id not in the record class's form; an output directory not named after the run id; an existing manifest; a Playwright version other than the pin; a realization not configured.

## 9. Tests (run from this directory; no SUT, no browser, no dispatch)

| Module | What it checks |
|---|---|
| `tests/test_counting.py` | The API realizations against threaded loopback fakes: counts, classes, outcomes, ABORTED, FAILURE, INCONCLUSIVE, PARTIAL_SUCCESS, exceptions, scrubbing, and conformance of the manifest with a subset validator of `schemas/run-manifest.schema.v2.json`. |
| `tests/test_realization_contract.py` | The declared counts of every realization against the source (`with run.action` statements), the action classes and mechanisms against the vocabulary, that the declared run-level mechanisms of each condition cover every mechanism its operations and precondition steps use, the configuration flags, and the regression guards of the three starting-state defects that the first DRY_RUNs found (HD-N). |
| `tests/test_gate_matrix.py` | The gate code extracted from both workflows and executed on fake repository trees: one fixture that passes, one mutation per gate that fails it, the verification gate, the guard steps, and the real worktree, which must fail closed. |
| `tests/test_run_condition.py` | The embedded digests against the copied files; a changed file, an unlisted Python file, and a missing variable each stop the script; the refresh tool is idempotent. |
| `tests/test_workflows_static.py` | YAML parses; dispatch-only triggers; every `inputs.` reference is declared; the OP-CI-15 length estimate for each string that carries an expression; no gate script carries an expression. |
| `tests/test_hygiene.py` | No forbidden name, attribution, person name, local path, or conversation identifier in any file this draft creates. |

Commands: `python3 tests/test_counting.py -v` and the same for each module. `test_gate_matrix.py` and `test_workflows_static.py` need PyYAML: set `EUS_PYLIB` to a directory that contains it. Recorded output: `tests/RESULTS.txt`.

## 10. Not verified (each needs a DRY_RUN or a source check before the START)

- SUT-01: `GET /api/session` without a token answers 401 or 403 in the fresh instance (assumed from the E03 middleware); the Checkout order line after the storage injection.
- SUT-04: the booking list `GET /booking/?roomid=1` response shape (`bookings`; the first and last names) and the displayed date format of the admin room page (the predicate uses the names and the ISO check-in date, as the E03 executor did).
- SUT-05: the `POST /api/BasketItems` request shape and the basket response (`Products` with `ProductId`); its first execution is a DRY_RUN check.
- SUT-02 and SUT-03 CS-003: the selectors are the E03-verified ones; the landing check on `/inventory.html` and the float-cart close are new.
- SUT-02 and SUT-03 CS-004: every selector, route, and the declared starting-state reads come from the pinned source and no run; the SUT-03 id attribute of product 1 (`li[id="1"]` in the order summary) and the second `li.product-option` as the quantity are read from the source of the checkout page; the first DRY_RUN of each is the verification.
- First DRY_RUNs (2026-11-09, execution_id DR0001, the ten conditions, implementation hash 602dfaf6...): seven conditions ran to SUCCESS with the declared counted operations; three aborted in the declared starting-state check before any establishment (SUT-01 WEB CS-003, SUT-02 WEB CS-003, SUT-03 WEB CS-004) because of defects of the checks, which are corrected in this version (IMPLEMENTATION-NOTES HD-N). The corrected realizations have not run yet, and the seven that passed have not run on the new bytes.
