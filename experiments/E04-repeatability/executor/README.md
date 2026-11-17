# E04-repeatability executor (DRAFT)

| Field | Value |
|---|---|
| State | DRAFT. Preparation under CAMPAIGN-CI-WRITE-AUTH-01 (operation OP-PREP-E04). Not locked, not hashed into a configuration, not an authorization. Nothing here starts E04, selects a condition, or dispatches anything. |
| Design record | IMPLEMENTATION-NOTES.md (points 1 to 14, open items in section 3) and ../design-notes-draft.md (the five working defaults, pending the START package). |
| Model | The E05 executor, from which this one is derived by copying and by removing the stimulus and classification blocks (experiments/E05-determinism/executor/). |

## 1. Shape

One job runs the N = 50 executions of ONE condition, sequentially, on one shared instance: 13 conditions, 13 jobs. Entry point: `run-condition.sh` (verifies the embedded digests, then `python3 -m executor.run`).

Environment (all set by the workflow, or by hand for a DEVELOPMENT run):

| Variable | Meaning |
|---|---|
| CONDITION_ID, ASSIGNED_SUT | for example E04-SUT05-API-01 and SUT-05; the condition must belong to the SUT and exist in conditions-draft.json |
| EXECUTOR_PROMPT_VERSION | the frozen dispatch procedure prompt id (null before START) |
| OUTPUT_DIR | job output root; executions are written under OUTPUT_DIR/executions/ |
| PROVENANCE_JSON, RUNTIME_ENVIRONMENT_JSON | the files the workflow writes; copied byte for byte into every bundle as ci-provenance.json and runtime-environment.json |
| INSTANCE_JSON | instance.json (default ./instance.json), with the format of experiments/E05-determinism/executor/README.md, section 3 (unchanged) |
| RECORD_CLASS | MEASURED_EXPERIMENT (accepted only when GITHUB_WORKFLOW_REF names .github/workflows/e04-measured-execution.yml; EXECUTIONS unset or 50), DRY_RUN (EXECUTIONS 1 to 3) or DEVELOPMENT (EXECUTIONS 1 to 50) |
| EXECUTIONS | the number of executions (see RECORD_CLASS); FIRST_EXECUTION (default 1) and ATTEMPT (default 1) exist for a further attempt under a recorded approval |

Identifiers: execution_id EX0001 to EX0050 (DR0001.. for DRY_RUN, DV0001.. for DEVELOPMENT), attempt A1, run_id `<condition_id>__<execution_id>__A<attempt>`.

Output (one workflow artifact per dispatch):

```
OUTPUT_DIR/
  executions/<run_id>/            one directory per execution, complete before the next execution starts
    run-manifest.json             schema v2, written last; outcome.outcome_category carries the category
    attempt-record.json           steps, cause, mechanical attribution (TOOLING or SUT), duration
    executor.log  tool-versions.json  ci-provenance.json  runtime-environment.json  evidence/
  condition-summary.json          counts only: categories, phases, category by attribution, the list of run ids
  sut-logs/                       tails of the SUT logs named in instance.json and of the kept restarts
```

stdout.log, stderr.log, exit-status.txt and finished-at.txt of the job are written by the workflow at the artifact root. The upload step runs with `if: always()`, so if the runner dies at execution k the executions 1 to k-1 are complete and importable; replacing k to 50 is a further attempt under a recorded approval (gate G-E04-A2), never a re-run.

Exit status of run-condition.sh: 0 when every execution that began has a run manifest (TARGET_STATE_VERIFIED, RESET_, and ESTABLISHMENT_ categories are recorded outcomes); 1 when an execution has none (a stub record, STUB_NO_BUNDLE, is written first when the ordinary bundle fails); 2 when the executor refused the run before it began (no record). A digest mismatch, an unlisted Python file or a missing variable exits 1 before anything runs.

## 2. Blocks of one execution

reset, starting-state check, establishment, target-state verification, record. There is no stimulus and no classification block. The reset is a step, not an action (E05 decision D-08c): the run manifest carries no actions[]. A block that does not hold stops that execution with its pre-declared category, and the job goes on with the next execution:

| Block | Does not hold | Exception of the harness or client |
|---|---|---|
| reset | RESET_FAILED | RESET_FAILED (TOOLING) |
| starting-state | RESET_STARTING_STATE_NOT_REACHED (status ABORTED, with its cause) | same |
| establishment | ESTABLISHMENT_FAILED | ESTABLISHMENT_INTERRUPTED (TOOLING) |
| verification | ESTABLISHMENT_VERIFICATION_FAILED | ESTABLISHMENT_INTERRUPTED (TOOLING) |
| success | (not a block; reached when every block above holds) | TARGET_STATE_VERIFIED, status SUCCESS |

Per condition, the reset (as in E05): SUT-01 API-02 to API-05 clear the session (API_RESET, SESSION_RESET); SUT-01 API-01, API-06 and WEB-01 restart the backend process (ENVIRONMENT_RESTART; E05 decision D-03 b); SUT-02 uses 'Reset App State' (APP_DATA_CLEAR); SUT-04 deletes the bookings that carry the condition's guest names (API_RESET); SUT-05 restarts the process (ENVIRONMENT_RESTART). Web conditions keep one Chromium context for the whole job. The attribution rule is IMPLEMENTATION-NOTES.md, point 3.

## 3. Integrity

`run-condition.sh` embeds the sha256 of every `executor/*.py` and of `requirements.txt`, and refuses an unlisted Python file under `executor/`. After any edit run `python3 tests/embed_digests.py` (it writes the block; nothing is typed by hand). No file of the executor, of a workflow or of a comment may carry the literal name of the agent-instructions file (the public export aliases it and breaks the digests): write "agent-instructions file". The conditions file (../conditions-draft.json) is hashed with the campaign configuration at START, if the human research lead decides it.

## 4. Tests (static; nothing contacts a SUT)

Run from this directory with the documented command: `PYTHONDONTWRITEBYTECODE=1 python3 -I -m unittest discover -s tests`. The command uses the Python standard library; the gate tests write a stand-in when PyYAML is not importable. The lint test runs only when `ACTIONLINT` and `SHELLCHECK` are set (otherwise it is skipped). Result of the final draft run: 97 tests, 0 failures, 0 errors, 0 skipped, with actionlint and shellcheck (exit 0). Counts per module: test_attempt 10, test_config_classify 23, test_digests 3, test_gates 14, test_run_condition 5, test_workflows 42. The attempt tests run the executor against fake systems in separate processes (tests/fake_sut.py), so the restarts are real; the manifests are checked against schemas/run-manifest.schema.v2.json by a small validator (tests/mini_jsonschema.py).

## 5. Decisions of the START package that touch the executor (none decided)

Open items are listed in IMPLEMENTATION-NOTES.md, section 3. In short: the identical-block conditions, the SUT-04 message-count baseline, the guest-name salt, the response clause of the attribution default, the 60-minute timeout (inherited from E05, to be re-derived), the metric name in the configuration, and the controlled-instance file, which does not exist yet.

## 6. Not here

The TSRR analysis, any START record or dispatch authorization, any frozen prompt, any controlled-instance verification, any E04 measured data, and any mobile condition (E04 has none, as E05).
