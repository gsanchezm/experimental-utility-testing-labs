# E07-cross-layer-continuity executor (DRAFT)

| Field | Value |
|---|---|
| State | DRAFT. Preparation under CAMPAIGN-CI-WRITE-AUTH-01 (operation OP-PREP-E07-04). Not locked, not hashed into a configuration, not an authorization. Nothing here starts E07, selects a condition, or dispatches anything. |
| Design record | IMPLEMENTATION-NOTES.md (points 1 to 14, open items in section 3), ../design-brief-draft.md (sections 17 and 18), ../campaign-configuration-draft.md, and the decisions of manifests/campaign-execution-decisions-v10.yaml, -v11.yaml and -v12.yaml (D-E07-0 to D-E07-10). |
| Model | The E04 executor, from which this one is derived by copying (experiments/E04-repeatability/executor/) and changing the blocks to a cross-layer establishment and verification. |
| Scenario records | experiments/scenario-mappings/CS-005.yaml (API to WEB) and CS-006.yaml (WEB to API), both DRAFT. |

## 1. Shape

One job runs the N = 50 executions of ONE condition, sequentially, on one shared instance (decision D-E07-8): four conditions, four jobs, 200 executions. Entry point: `run-condition.sh` (verifies the embedded digests, then `python3 -m executor.run`).

| Condition | Scenario | SUT | Source layer | Verification layer | Unit |
|---|---|---|---|---|---|
| E07-CS005-SUT01-API-WEB | CS-005 | SUT-01 | api | web | one cart line, pizza_id p02, quantity 1 |
| E07-CS005-SUT04-API-WEB | CS-005 | SUT-04 | api | web | one booking of room 1 |
| E07-CS006-SUT01-WEB-API | CS-006 | SUT-01 | web | api | one cart line, pizza_id p02, quantity 1 |
| E07-CS006-SUT04-WEB-API | CS-006 | SUT-04 | web | api | one booking of room 1 |

SUT-02, SUT-03, SUT-05 and SUT-06 have no condition (NOT_COMPARABLE; conditions-draft.json, `no_condition`).

Environment (all set by the workflow, or by hand for a DEVELOPMENT run):

| Variable | Meaning |
|---|---|
| CONDITION_ID, ASSIGNED_SUT | for example E07-CS005-SUT04-API-WEB and SUT-04; the condition must belong to the SUT and exist in conditions-draft.json |
| EXECUTOR_PROMPT_VERSION | the frozen dispatch procedure prompt id (ORCHESTRATOR-E07-cross-layer-continuity-v1 once frozen; null before START) |
| OUTPUT_DIR | job output root; executions are written under OUTPUT_DIR/executions/ |
| PROVENANCE_JSON, RUNTIME_ENVIRONMENT_JSON | the files the workflow writes; copied byte for byte into every bundle as ci-provenance.json and runtime-environment.json |
| INSTANCE_JSON | instance.json (default ./instance.json), with the format of experiments/E05-determinism/executor/README.md, section 3. Read: interface_version 1, sut_id, record_class, surfaces.<name>.base_url, provisioning, logs. SUT-01 needs surfaces.api and surfaces.web. SUT-04 needs surfaces.api (the booking service), surfaces.auth (the auth service) and surfaces.web. The `process` block is not read: no E07 reset restarts a process. |
| RECORD_CLASS | MEASURED_EXPERIMENT (accepted only when GITHUB_WORKFLOW_REF names .github/workflows/e07-measured-execution.yml; EXECUTIONS unset or 50), DRY_RUN (EXECUTIONS 1 to 3) or DEVELOPMENT (EXECUTIONS 1 to 50) |
| EXECUTIONS | the number of executions (see RECORD_CLASS); FIRST_EXECUTION (default 1) and ATTEMPT (default 1) exist for a further attempt under a recorded approval |

Identifiers: execution_id EX0001 to EX0050 (DR0001.. for DRY_RUN, DV0001.. for DEVELOPMENT), attempt A1, run_id `<condition_id>__<execution_id>__A<attempt>`.

Output (one workflow artifact per dispatch):

```
OUTPUT_DIR/
  executions/<run_id>/            one directory per execution, complete before the next execution starts
    run-manifest.json             schema v2, written last; outcome.outcome_category carries the category; source_layer and verification_layer are set
    attempt-record.json           steps, cause, interrupted_cause, mechanical attribution (TOOLING or SUT), the identity record, duration
    executor.log  tool-versions.json  ci-provenance.json  runtime-environment.json  evidence/
  condition-summary.json          counts only: categories, interrupted causes, category by attribution, the list of run ids
  sut-logs/                       tails of the SUT logs named in instance.json
```

stdout.log, stderr.log, exit-status.txt and finished-at.txt of the job are written by the workflow at the artifact root. The upload step runs with `if: always()`, so if the runner dies at execution k the executions 1 to k-1 are complete and importable; replacing k to 50 is a further attempt under a recorded approval.

Exit status of run-condition.sh: 0 when every execution that began has a run manifest (every category of D-E07-10 is a recorded outcome); 1 when an execution has none (a record of the category RUNNER_ERROR, cause BUNDLE_NOT_WRITTEN, is written first when the ordinary bundle fails); 2 when the executor refused the run before it began (no record), including a conditions file whose identity keys differ from the keys the realization compares. A digest mismatch, an unlisted Python file or a missing variable exits 1 before anything runs.

## 2. Blocks of one execution

reset, starting-state check, establishment (source layer), establishment check (source layer, read-only), verification (the other layer, read-only), record. The reset is a step, not an action (E05 decision D-08c): the run manifest carries no actions[]. The reset runs outside the scenario and is not counted (DATA_RESET): SUT-01 logs in, clears the session through the API and injects the client state into a NEW browser context; SUT-04 deletes through the booking API every booking of room 1 whose first name is the condition's first name, then logs in to the admin web app in the new context. A block that does not hold stops that execution with its pre-declared category, and the job goes on with the next execution:

| Block | Does not hold | Exception of the harness, browser or client | Watchdog |
|---|---|---|---|
| reset | INTERRUPTED, cause RESET_FAILED (SUT) | RUNNER_ERROR (TOOLING) | INTERRUPTED, cause WATCHDOG (TOOLING) |
| starting-state | INTERRUPTED, cause STARTING_STATE_NOT_REACHED (SUT) | RUNNER_ERROR (TOOLING) | INTERRUPTED, cause WATCHDOG (TOOLING) |
| establishment | ESTABLISHMENT_FAILED (SUT) | RUNNER_ERROR (TOOLING) | INTERRUPTED, cause WATCHDOG (TOOLING) |
| establishment check | ESTABLISHMENT_FAILED (SUT) | RUNNER_ERROR (TOOLING) | INTERRUPTED, cause WATCHDOG (TOOLING) |
| verification | NOT_VERIFIED (SUT): the observation completed, or did not complete, and a declared key is absent or different | RUNNER_ERROR (TOOLING) | INTERRUPTED, cause WATCHDOG (TOOLING) |
| success | (reached when every block holds) | | VERIFIED, status SUCCESS |

Outcome status in run-manifest.json: VERIFIED SUCCESS; NOT_VERIFIED FAILURE; ESTABLISHMENT_FAILED ABORTED; INTERRUPTED ABORTED; RUNNER_ERROR ERROR. outcome.expected is VERIFIED for every condition.

Identity (decision D-E07-9): the attempt record carries `identity` with the declared keys, the keys compared, the keys not compared with the reason, what was established, what the verification layer showed and one comparison entry per key (match true only when the key was observed and equals the established value). The sid claim of the login token is recorded as a digest, never in clear. SUT-01 compares sid, the number of cart lines, the pizza_id and the quantity of the line; SUT-04 compares the number of bookings with the names, the first and last name and the check-in date, and on the API layer also the check-out date (the admin web row is not documented to show it, so it is not compared there; IMPLEMENTATION-NOTES.md, point 8).

## 3. Integrity

`run-condition.sh` embeds the sha256 of every `executor/*.py` and of `requirements.txt`, and refuses an unlisted Python file under `executor/`. After any edit run `python3 tests/embed_digests.py` (it writes the block; nothing is typed by hand). No file of the executor, of a workflow or of a comment may carry the literal name of the agent-instructions file (the public export aliases it and breaks the digests): write "agent-instructions file". The conditions file (../conditions-draft.json) is hashed with the campaign configuration at START, if the human research lead decides it.

## 4. Tests (static; nothing contacts a SUT)

Run from this directory with the documented command: `PYTHONDONTWRITEBYTECODE=1 python3 -I -m unittest discover -s tests`. The command uses the Python standard library. Result of the draft run: 77 tests, 0 failures, 0 errors, 0 skipped. Counts per module: test_attempt 30, test_config_classify 27, test_digests 3, test_run_condition 5, test_ui_calls 12. The workflow and gate tests (test_gates, test_workflows) belong to the workflows of E07 and are not part of this directory yet.

The attempt tests run the executor against fake systems in separate processes (tests/fake_sut.py); the web leg of each condition is replaced by a fake UI that talks to the same fake SUT over HTTP and records every call with the phase it was made in, because no browser is installed in the static tests. They cover every category and its attribution, both directions for both SUTs, a NOT_VERIFIED case where the verification layer lacks the unit and a case where one attribute differs, that the verification block makes only GET requests, and the manifests against schemas/run-manifest.schema.v2.json by a small validator (tests/mini_jsonschema.py). test_ui_calls runs the Playwright code of the web legs against a recording stand-in for the browser: it checks the order of the interactions, the selectors, the values the methods return and that the reads click nothing; it does not prove that the selectors exist on the pages. The real behavior of the SUTs and of the pages is verified only by the non-measured DRY_RUN rounds on GitHub Actions.

## 5. Decisions that touch the executor

Decided on 2026-11-18 (manifests/campaign-execution-decisions-v12.yaml): the shape of four conditions with N = 50 and the reset (D-E07-8), the identity keys (D-E07-9), the categories, the denominator and the attribution (D-E07-10). Open items are listed in IMPLEMENTATION-NOTES.md, section 3. In short: the selectors read from the pinned source of SUT-01 and not from a recorded study text, the check-out date on the admin web row, the quantity locator of the Checkout view, the circularity of the sid key, the stub record of a bundle that cannot be written, the modality and platform values of a cross-layer record, the 60-minute timeout, and the controlled-instance status of the conditions.

## 6. Not here

The analysis of the continuity proportions, any START record or dispatch authorization, any frozen prompt, any controlled-instance verification, any workflow, any E07 measured data, and any mobile condition (E07 is web and API only, D-E07-7).
