# E11-security executor: implementation notes (DRAFT, operation OP-PREP-E11)

## 1. What is copied and what is new

Copied from the E05 executor and adapted (each campaign locks its own hash): `common.py` (job, run, scrubber, HTTP client, run manifest; the phases are now reset, starting-state, method, classification; no scenario, no state ids, no behavior class), `instance.py` (instance.json and the process restart; the temporary prefix is `e11-restart-`), `attempt.py` (the loop with the E11 blocks), `run.py` (entry point; no browser check; the measured workflow is e11-measured-execution.yml). New: `config.py` (cells), `classify.py` (E11 categories), `zap.py` (M2), `sut05.py` (twelve cells), `sut01.py` (the two IDOR cells).

## 2. Decisions applied

| Id | Applied as |
|---|---|
| E11-D-3 | M1 and M2 are separate cells and are never merged into one rate |
| E11-D-4 | M2 counts an alert only when rule id, method and normalized path equal the expectation; other alerts recorded, not counted (zap.match_alerts) |
| E11-D-8 | ZAP v2.17.0 as the image `ghcr.io/zaproxy/zaproxy@sha256:c2d63bbb…` (amd64 manifest); a tag is refused by DockerLauncher; `-config start.checkForUpdates=false`; the add-on list is read before and after every scan and compared (`addons_unchanged`), a difference is noted in the run manifest |
| E11-D-9 | the four expectations; no M2 on SUT-01 (config.validate refuses it) |
| E11-D-12 | M2 controls are other endpoints of the same instance (POST /api/Users, GET /rest/user/security-question?email=, /assets/); the difference from the condition is the endpoint as well as the vulnerability |
| E11-D-14 | one job per cell, a fresh instance and a fresh ZAP container per execution; the budgets `SCAN_TIMEOUT_S` (300 s), `READY_TIMEOUT_S` (180 s) and the per-execution `WATCHDOG_S` (1200 s, above the sum of the M2 budgets) are placeholders to be set from the DRY_RUN timing; the watchdog is re-raised by the ZAP client, never turned into ZAP_API_ERROR |
| E11-D-15 | the IDOR cell executes the GET only |

## 3. Open items that only a DRY_RUN can close

1. ZAP API names and parameters were read in the core source at tag v2.17.0 (ActiveScanAPI, CoreAPI, AutoUpdateAPI): `ascan` actions `scan` (url, recurse, inScopeOnly, scanPolicyName, method, postData, contextId), `addScanPolicy`, `disableAllScanners`, `enableScanners` (ids, scanPolicyName), views `status` (scanId) and `scanners`; `core` action `sendRequest` (request, followRedirects) and views `alerts` (baseurl, start, count) and `version`; `autoupdate` view `installedAddons`. Not read from the API class: the answer shapes (the `scan` key of the scan action, the row keys of `scanners` and `installedAddons`) and the names of the four option views, which are derived from the option getters; the settings views are non-fatal. A mismatch of an answer shape shows in the DRY_RUN.
2. That the pinned image pulls and starts by digest on a GitHub-hosted runner with `--network host`, and how long that takes (about 1.2 GB compressed).
3. The installed add-ons of the image (derived, not observed: ascanrules 84, pscanrules 77, commonlib 1.44.0) and that they do not change across a run.
4. That the packaged SUT-05 leaves the three vulnerable paths active and that each M1 sequence flips only its own flag (V-3, V-4); that the nine-column UNION payload matches the Products table.
5. That rule 0 does not match the `/ftp` listing (V-7, predicted) and what rule 40018 does on the login (JSON body) and the search (V-8).
6. What the application answers for `/assets/` (the M2 control of DIRLIST-FTP).
7. The timing of one M2 execution, which decides E11-D-14.
8. Whether the host process list kept as evidence (`process-tree-*`) can carry a secret on a runner: the workflow starts the instance and ZAP without secrets on the command line; the tests exclude those files from the secret scan because a development host's `ps` is host-dependent.

## 3b. DRY_RUN round 1 (run 45376285190, 2026-11-24; manifests/e11-environment-verification-rounds-v1.yaml): what it settled and what it changed

Settled (observed): the pinned image pulls and starts by digest on a GitHub-hosted runner; the ZAP API names, parameters and answer shapes worked as written (items 1 and 2 above); the installed add-ons are `ascanrules@84.0.0`, `pscanrules@77.0.0` and `commonlib@1.44.0` among 49, equal before and after a run, matching the derived set; the policy rows carry attackStrength and alertThreshold DEFAULT; injectable targets 35 and enabled RPC variants 191; no duration limit (0). An M2 execution took 10 to 27 s, a job of two executions 25 to 49 s (item 7: E11-D-14 holds with a wide margin). IDOR: 200 as `security_glitch_user`, 403 as `standard_user`. SQLI-LOGIN and DIRLIST-FTP M1 flip their flags and their controls do not; rule 40018 raised an alert on the JSON login and on the search query; rule 0 raised no alert on `/ftp/` (V-7: predicted, now observed; ZAP's passive rules did report three other alerts on the page, which are never counted); the three M2 controls raised none in 5 of 6 executions.

Defects found and corrected in the harness (the expectations are untouched): (a) the SQLI-SEARCH M1 payload worked (the response held every user's email and hash) but the immediate oracle read still showed the flag unsolved: the oracle is now read with a bounded wait (sut05.M1.ORACLE_WAIT_S = 5 s, 0.25 s polls); (b) one `ascan/action/scan` answered HTTP 400 in the first execution of E11-SUT05-SQLI-SEARCH-M2-CTRL (ZAP_API_ERROR, TOOLING) and not in the other 11 M2 executions: the error body was not recorded, so the cause is not established; the ZAP client now waits, bounded, until `core/view/urls` lists the seeded URL and records the wait, and an HTTP error message carries the body of the answer. Whether (a) is a timing effect and whether (b) is a seed race is decided by round 2, not by this note.

## 4. Deviations from E05 worth knowing

- No establishment or verification block: the starting-state check of SUT-01 also creates the owner's order (it is a precondition of the method, not an action of the study).
- The attribution is E05's: a recorded observation that a block did not hold (for example an oracle already solved at the start) is attributed to SUT, because only an exception before the first request that can change the SUT is TOOLING; ZAP_ categories are TOOLING by prefix.
- `mark_stimulus_sent` keeps its E05 name and marks the first request of the method that can change the SUT (M2: the seed request to the SUT through ZAP).
- The documented Juice Shop account password used by the SQLI-LOGIN M1 control is public and is kept in evidence as E05 keeps it; the SUT-01 test-account password and every session token are scrubbed.

## 5. Not done here

The measured workflow `e11-measured-execution.yml` (written after the DRY_RUN rounds, by the same method as the verification workflow: the provisioning steps of the two stay identical), the frozen dispatch prompt (a working copy exists: prompts/working/ORCHESTRATOR-E11-security-v1.md), the START package, the entry in manifests/toolchain-manifest.yaml. DONE as drafts: `.github/workflows/e11-environment-verification.yml` (dispatch-only; built from the E05 verification workflow with the SUT-01 api and SUT-05 packaged provisioning steps, a ZAP pull by digest for the M2 cells, no browser) and ../dry-run-plan-draft.md. Each is a separate step and each START, authorization, dispatch and freeze needs the human research lead's explicit approval.
