# E05-determinism executor (DRAFT)

| Field | Value |
|---|---|
| State | DRAFT. Preparation under CAMPAIGN-CI-WRITE-AUTH-01 (operation OP-PREP-E05). Not locked, not hashed into a configuration, not an authorization. Nothing here starts E05, selects a condition, or dispatches anything. |
| Design record | IMPLEMENTATION-NOTES.md (points 1 to 18). Inputs: ../design-brief-draft.md ("brief"), ../campaign-configuration-draft.md ("config"), ../conditions-draft.json, ../../../manifests/source-reads-v1.yaml to -v3.yaml. |
| Models | The E03 and E02 executors (primitives copied, each campaign locks its own hash), the E02 and E09 entry point and gate tests. |

## 1. Shape

One job runs the N executions of ONE condition, sequentially, on one shared instance (D-02, model B): 14 conditions, 14 jobs. Entry point: `run-condition.sh` (verifies the embedded digests, then `python3 -m executor.run`).

Environment (all set by the workflow, or by hand for a DEVELOPMENT run):

| Variable | Meaning |
|---|---|
| CONDITION_ID, ASSIGNED_SUT | for example E05-SUT05-API-01 and SUT-05; the condition must belong to the SUT and exist in conditions-draft.json |
| EXECUTOR_PROMPT_VERSION | the frozen dispatch procedure prompt id (null before START) |
| OUTPUT_DIR | job output root; executions are written under OUTPUT_DIR/executions/ |
| PROVENANCE_JSON, RUNTIME_ENVIRONMENT_JSON | the files the workflow writes; copied byte for byte into every bundle as ci-provenance.json and runtime-environment.json |
| INSTANCE_JSON | instance.json (default ./instance.json), section 3 |
| RECORD_CLASS | MEASURED_EXPERIMENT (accepted only when GITHUB_WORKFLOW_REF names .github/workflows/e05-measured-execution.yml; EXECUTIONS unset or 50), DRY_RUN (EXECUTIONS 1 to 3) or DEVELOPMENT (EXECUTIONS 1 to 50) |
| EXECUTIONS | the number of executions (see RECORD_CLASS); FIRST_EXECUTION (default 1) and ATTEMPT (default 1) exist for a further attempt under a recorded approval |

Identifiers: execution_id EX0001 to EX0050 (DR0001.. for DRY_RUN, DV0001.. for DEVELOPMENT), attempt A1, run_id `<condition_id>__<execution_id>__A<attempt>` (D-19).

Output (one workflow artifact per dispatch):

```
OUTPUT_DIR/
  executions/<run_id>/            one directory per execution, complete before the next execution starts
    run-manifest.json             schema v2, written last; outcome.outcome_category carries the phase and the category (D-08)
    attempt-record.json           steps, cause, mechanical attribution (TOOLING or SUT), stimulus-sent flag, duration
    executor.log  tool-versions.json  ci-provenance.json  runtime-environment.json  evidence/
  condition-summary.json          counts only: categories, phases, category by attribution, the list of run ids
  sut-logs/                       tails of the SUT logs named in instance.json and of the kept restarts
```

stdout.log, stderr.log, exit-status.txt and finished-at.txt of the job are written by the workflow at the artifact root. The upload step runs with `if: always()`, so if the runner dies at execution k the executions 1 to k-1 are complete and importable; replacing k to 50 is a further attempt under a recorded approval, never a re-run.

Exit status of run-condition.sh: 0 when every execution that began has a run manifest (every RESET_, ESTABLISHMENT_, S_ and INTERRUPTED_ category is a recorded outcome); 1 when an execution has none (a stub record, STUB_NO_BUNDLE, is written first when the ordinary bundle fails); 2 when the executor refused the run before it began (no record). A digest mismatch, an unlisted Python file or a missing variable exits 1 before anything runs.

## 2. Blocks of one execution

reset, starting-state check, establishment, target-state verification, stimulus, classification, record (brief s.2.1). The reset is a step, not an action (D-08c): the run manifest carries no actions[]. A block that does not hold stops that execution with its pre-declared category and the job goes on with the next execution:

| Block | Does not hold | Exception of the harness or client |
|---|---|---|
| reset | RESET_FAILED | RESET_FAILED (TOOLING) |
| starting-state | RESET_STARTING_STATE_NOT_REACHED (status ABORTED, with its cause) | same, TOOLING |
| establishment | ESTABLISHMENT_FAILED | ESTABLISHMENT_INTERRUPTED (TOOLING) |
| verification | ESTABLISHMENT_VERIFICATION_FAILED | ESTABLISHMENT_INTERRUPTED (TOOLING) |
| stimulus, classification | (a SUT answer is classified, never judged) | INTERRUPTED_ (TOOLING before the request is sent, SUT after) |

Per condition, the reset: SUT-01 API-02 to API-05 clear the session (API_RESET, SESSION_RESET); SUT-01 API-01, API-06 and WEB-01 restart the backend process (ENVIRONMENT_RESTART, D-03 b); SUT-02 uses 'Reset App State' (APP_DATA_CLEAR); SUT-04 deletes the bookings that carry the condition's guest names (API_RESET); SUT-05 restarts the process (ENVIRONMENT_RESTART). Web conditions keep one Chromium context for the whole job.

## 3. instance.json (interface version 1; written by the provisioning step before run-condition.sh)

```
{ "interface_version": 1, "sut_id": "SUT-01", "record_class": "DRY_RUN",
  "surfaces": { "api": {"base_url": "http://127.0.0.1:8000"}, "web": {"base_url": "http://127.0.0.1:5173"} },
  "process": { "pid": 1234, "pgid": 1234, "port": 8000, "start_command": ["python3", "-m", "uvicorn", "..."], "cwd": "<backend dir>",
               "env": {}, "readiness_url": "/health", "readiness_timeout_s": 180, "stop_timeout_s": 30 },
  "provisioning": { "repository": "...", "commit_sha": "...", "release": null, "route": "...", "asset": {"name": "...", "sha256": "..."} },
  "logs": ["<path of a SUT log>"] }
```

* surfaces: SUT-01 api and web; SUT-02 web; SUT-04 web, api (booking service), auth (auth service) and message (the real message service on port 3006, not a double; manifests/source-reads-v2.yaml F13 to F15); SUT-05 api. Only the surfaces the condition uses are read.
* process: required for SUT-01 (the conditions E05-SUT01-API-01, E05-SUT01-API-06 and E05-SUT01-WEB-01) and for SUT-05. The instance process must be started in its own session and process group (start_new_session), `pgid` being that group, so that the executor can send SIGTERM to the whole group, wait until `port` refuses connections, start `start_command` again in a new session and group, and wait until `GET <api base_url><readiness_url>` answers 200 (the readiness budget of SUT-05 is 180 s). The executor replaces `pid` and `pgid` in memory after every restart. `start_command` and `env` reproduce the provisioning start line (for SUT-01 the backend only; the web app is a separate process that the restart does not touch).
* The instance.json file is never modified by the executor; its sha256 is recorded in every manifest note.

## 4. Integrity

`run-condition.sh` embeds the sha256 of every `executor/*.py`, of `expected-sut01.json` (derived statically from the pinned SUT-01 source by `tools/derive_sut01_expected.py`) and of `requirements.txt`, and refuses an unlisted Python file under `executor/`. After any edit run `python3 tests/embed_digests.py`. No file of the executor, of a workflow or of a comment may carry the literal name of the agent-instructions file (the public export aliases it and breaks the digests): write "agent-instructions file". The conditions file (../conditions-draft.json) is hashed with the campaign configuration at START.

## 5. Tests (static; nothing contacts a SUT)

`PYTHONDONTWRITEBYTECODE=1 python3 -I -m unittest discover -s tests` from this directory: configuration and classifier tests, the attempt loop against fake systems (tests/fake_sut.py, separate processes, so the restarts are real), the manifest check against schemas/run-manifest.schema.v2.json, the digest lock and the entry point. The web realizations (SUT-01 WEB-01, SUT-02, SUT-04 WEB-01) need a browser and are exercised by the first DRY_RUN only.

## 6. Conditions that cannot run yet (decisions of the START package)

E05-SUT02-WEB-02 is not configured: no recorded source defines its visual marker (source-reads-v3.yaml, F23), and run.py refuses it. E05-SUT04-API-02 declares no catch-all category (k = 4). The SUT-01 web controls built by tid(...) are located by contains selectors until the DRY_RUN confirms them (F22). The pins that are still missing are listed in ../campaign-configuration-draft.md, section 15.

## 7. Not here

The H3 loader and CLI (after the configuration is locked), any mobile condition, E04 content (decision D-20 b).
