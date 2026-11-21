# E06-cross-platform-parity executor (DRAFT, operation OP-PREP-E06-EXECUTOR)

**DRAFT. Not frozen, not locked, not dispatched.** Nothing here starts, configures, authorizes, dispatches, or freezes the E06 campaign.
The conditions file (`../conditions-draft.json`) is a draft; its candidate values are open items for the human research lead
(IMPLEMENTATION-NOTES.md, section 5). The measured workflow `.github/workflows/e06-measured-execution.yml` refuses every dispatch until the
campaign START (a protocol/CHANGELOG.md row, as in the E07 and E09 gates), a locked "Campaign configuration" section, a dispatch authorization
of the assigned SUT (protocol/agent-governance-v6.md, Section 3.7), a frozen dispatch prompt, and, for the Android conditions, the study
mobile-runner admissibility and the smoke PASS of the exact SUT x platform x runner are all present.

| Field | Value |
|---|---|
| Campaign | E06-cross-platform-parity (experiments/E06-cross-platform-parity/README.md; status NOT_STARTED) |
| Scenario | CS-007 (experiments/scenario-mappings/CS-007.yaml, FROZEN; freeze record manifests/cs-007-freeze-v1.yaml) |
| Conditions | E06-CS007-SUT01-WEB, E06-CS007-SUT01-ANDROID, E06-CS007-SUT02-WEB, E06-CS007-SUT02-ANDROID; N = 50 each; attempt 1, or a further attempt only under a recorded approval of the human research lead |
| Surfaces | web: Playwright for Python 1.63.0 (hash-pinned in requirements.txt); Android: Appium 3.7.0 with appium-uiautomator2-driver 8.7.0, Node.js 22.23.2, GitHub-hosted emulator (API 35, pixel_7) |
| Entry point | `run-condition.sh` (one condition per invocation; ATTEMPT and FIRST_EXECUTION; a non-measured record is attempt 1 only; verifies the digests of every implementation file first) |
| Output | one bundle per execution (`<condition>__EX<NNNN>__A1/`, `run-manifest.json` written last), plus `condition-summary.json` (counts only) |

## 1. What one invocation does

For one condition, the executor runs executions 1 to N in sequence (N = 50 when measured, 3 for a DRY_RUN, 1 for an environment
verification). Each execution starts from a clean state (a fresh browser context on the web; an uninstall, a new Appium session, and a
clean install on Android), performs the sign-in of CS-007 through the application's own sign-in control (no token is injected), and reads
the identity of the first catalogue position (the pizza id on SUT-01; the product title on SUT-02, unless the identity oracle switch names
`arrival_only` for the condition). It classifies the execution, writes its bundle, and goes on with the next one. No execution is retried. A further
attempt (attempt 2 or more, executions FIRST_EXECUTION to N) exists only for the measured workflow under a recorded approval of the human research lead
(gate G-E06-A2, decision D-E06-14); the bundles of attempt n carry the suffix `__A<n>`.

## 2. Classification vocabulary (declared in the conditions file before any run)

| Category | Outcome status (schema v2) | Attribution | Meaning |
|---|---|---|---|
| ARRIVED_IDENTITY_READ | SUCCESS | NONE | arrived at the authenticated catalogue; identity read |
| ARRIVED_ARRIVAL_ONLY | SUCCESS | NONE | arrived; the switch is `arrival_only` (DP-3 fallback), no identity by design |
| ARRIVED_IDENTITY_UNREADABLE | INCONCLUSIVE | UNDETERMINED | arrived; the identity could not be read |
| NOT_ARRIVED_INFRASTRUCTURE | ABORTED | INFRASTRUCTURE | backend refusal or unavailability, or a timeout, with its reason (INFRA_USER_LIMIT_429, INFRA_BACKEND_5XX, INFRA_BACKEND_NO_RESPONSE, INFRA_CATALOGUE_TIMEOUT) |
| NOT_ARRIVED_SUT | FAILURE | SUT | the system answered and did not admit the actor (SUT_SIGN_IN_REFUSED, which on SUT-02 Android also covers a catalogue shown after the sign-in without the Logout Menu Item row, decision D-E06-13; SUT_CATALOGUE_NOT_REACHED_AFTER_SIGN_IN) |
| NOT_ARRIVED_RUNNER | ERROR | TOOLING | a fault of the executor, browser, client, or Appium session, including a harness fault that did not let the execution arrive (RUNNER_FAULT) |

Parity is not decided here. It is a pairwise property of execution k of the WEB condition and execution k of the ANDROID condition of the
same ecosystem (conditions-draft.json, `pairing_rule` and `parity_rule`), computed by the analysis after import.

## 3. Files

| Path | Role |
|---|---|
| `run-condition.sh` | entry point: environment checks, attempt and record-class refusals, digest verification, then `python3 -m executor.run` |
| `android-job.sh` | job body of the Android jobs: defaults APPIUM_HOME to the installed packages, records the backend probe (SUT-01), starts the Appium 3.7.0 server, waits for it, runs `run-condition.sh`, stops the server |
| `executor/config.py` | conditions file loading and validation against the vocabulary of this code |
| `executor/identity.py` | pure parsers of the identity (web test identifiers; Android page sources, replayable from the kept evidence) |
| `executor/classify.py` | pure classification and the non-arrival precedence |
| `executor/common.py` | environment, scrubbing, per-execution bundles, and the run manifest (schema v2) for both surfaces |
| `executor/web.py` | the SUT-01 and SUT-02 web flows, over a small page interface; the Playwright adapter and the E09-style settle logic |
| `executor/android.py` | APK digest check, `adb uninstall` before each execution, the call of the Node harness, and the harness record |
| `executor/run.py` | the condition loop, the drivers, the refusals (attempt, record class, oracle, prompt version for measured runs), the summary, and `main` |
| `../harness/e06-android.mjs` | one Node process per Android execution: session, sign-in, identity read, the second signal of the authenticated state on SUT-02 (the Logout Menu Item row), and the record |
| `../harness/wd.mjs` | the study-authored WebDriver client over node:http (a copy of the smoke client with findElements and sendKeys added) |
| `tests/` | the Python tests (171), including the Android path through the real harness and a fake WebDriver server, the measured-execution gate on fictitious common records and on the real mobile records (one-change mutations), and the workflow checks; `lift_g7.py` (generates the mobile-runner admissibility block of the measured workflow from the G-7 block of the E03 workflow, and checks it for drift); `embed_digests.py`; `RECORDED-OUTPUT.txt`; `record_output.py` |
| `../harness/tests/` | the Node tests (16): the client, the harness flows against a fake W3C server, and the entry point |
| `requirements.txt` | the hash-pinned Playwright set (copied from the E09 executor, unchanged) |
| Appium stack | not in this directory: `npm ci` from the lockfile of the SUT-01 smoke (`qualification/compatibility-smoke-sut01/harness`), digested in `run-condition.sh` |

## 4. Verification run (not a measured run)

`tests/record_output.py` runs both suites and writes `tests/RECORDED-OUTPUT.txt`. On the recorded run: 171 Python tests OK, none skipped (with
ResourceWarning as an error; 2 of them run actionlint and shellcheck with the pinned binaries, 5 run the Android path through the real
Node harness, and the measured-execution gate runs on fictitious common records for the four conditions, on the real mobile records for the
Android conditions, and on one-change must-fail cases, each failing on the gate it names, those of the further-attempt gate G-E06-A2 included), and 16 Node tests pass. actionlint 1.7.7 and
shellcheck 0.10.0 pass on both workflows and on both shell scripts. The Python tests need PyYAML; without it the gate tests are skipped, so a
run that reports skipped tests is not the recorded run. They run on Python 3.14.2 and the Node tests on Node 23.6.1 (the local versions), not on
the pinned runtimes of the workflows (Python 3.12, Node.js 22.23.2). No browser, emulator, Appium server, or hosted system under test was used.
The gate has not yet run on the exported bytes of the public tree (with PUBLIC-EXPORT-MANIFEST.yaml at its root); that rehearsal precedes the START.

## 5. Re-embedding the digests

Run `python3 tests/embed_digests.py` after every edit of `executor/*.py`, `requirements.txt`, `android-job.sh`, `../harness/*.mjs`, or
`../conditions-draft.json`; `tests/test_digests.py` fails until the DIGESTS block of `run-condition.sh` matches the files. The entry script
verifies the same digests before anything runs.
