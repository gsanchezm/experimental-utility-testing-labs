# E11-security executor (DRAFT, operation OP-PREP-E11)

**DRAFT. Not frozen, not locked, not dispatched.** Nothing in this directory starts, configures, authorizes, or dispatches a campaign, and nothing in it has run against a real SUT or a real ZAP: the tests use fake systems (`tests/fake_sut.py`) and a fake ZAP API (`tests/fake_zap.py`). Working basis: `../design-brief-draft.md`, `../campaign-configuration-draft.md`, `../conditions-draft.json`, `../zap-pin-proposal-draft.md`, and the decisions of manifests/campaign-execution-decisions-v19.yaml and -v20.yaml.

| Field | Value |
|---|---|
| Campaign | E11-security (experiments/E11-security/README.md; status NOT_STARTED) |
| Modality | Security Testing (protocol/study-design-v1.md, section 7); platform `api` (every method is HTTP) |
| Cells | 14 (condition or control, M1 or M2), 700 executions at N = 50, attempt 1 |
| Method M1 | a fixed request sequence, then the `solved` flag of the challenge read from GET /api/Challenges (SUT-05), or the status of the requester's GET /api/orders/{id} (SUT-01) |
| Method M2 | OWASP ZAP v2.17.0, Route A: container image by digest (executor/zap.py), one rule, one seeded target, update checks off |
| Entry point | `run-condition.sh` (bash), which verifies the embedded digests before anything else |
| Dependencies | Python 3 standard library and `docker` on the runner; no package |

## 1. Shape

One job runs the N executions of ONE cell, sequentially (decision E11-D-14, conditional on a DRY_RUN that times one M2 execution). Each execution restarts the instance process (SUT-05: SIGTERM to the process group, port refused, start in a new session, readiness; SUT-01: the same for the backend), so no `solved` flag, order or ZAP state carries over. An M2 execution starts its own ZAP container and removes it.

Environment (set by the workflow, or by hand for a DEVELOPMENT run):

| Variable | Meaning |
|---|---|
| CELL_ID, ASSIGNED_SUT | for example E11-SUT05-SQLI-LOGIN-M2 and SUT-05; the cell must belong to the SUT and exist in conditions-draft.json |
| EXECUTOR_PROMPT_VERSION | the frozen dispatch procedure prompt id (null before START) |
| OUTPUT_DIR, PROVENANCE_JSON, RUNTIME_ENVIRONMENT_JSON, INSTANCE_JSON | as in the E05 executor |
| RECORD_CLASS | MEASURED_EXPERIMENT (accepted only when GITHUB_WORKFLOW_REF names .github/workflows/e11-measured-execution.yml; EXECUTIONS unset or 50), DRY_RUN (EXECUTIONS 1 to 3) or DEVELOPMENT (EXECUTIONS 1 to 50) |
| EXECUTIONS, FIRST_EXECUTION, ATTEMPT | as in the E05 executor; a further attempt needs a recorded approval |

Identifiers: execution_id EX0001 to EX0050 (DR0001.. for DRY_RUN, DV0001.. for DEVELOPMENT); run_id `<cell_id>__<execution_id>__A<attempt>`. The cell id is the `condition` and `experiment_id` of the run manifest.

Output (one workflow artifact per dispatch), as in E05: `executions/<run_id>/` with `run-manifest.json` (schema v2, written last), `attempt-record.json`, `executor.log`, `tool-versions.json`, `ci-provenance.json`, `runtime-environment.json`, `evidence/`; `condition-summary.json` (counts only); `sut-logs/`. An M2 execution adds `zap-alerts.json` (every alert ZAP returned) and `zap-container-log`.

Exit status of run-condition.sh: 0 when every execution that began has a run manifest; 1 when one has none (a stub is written first); 2 when the executor refused the run before it began.

## 2. Blocks and categories

reset, starting-state, method, classification, record (campaign-configuration-draft.md, section 4). Categories are the closed sets of conditions-draft.json (`category_sets`): RESET_FAILED and RESET_STARTING_STATE_NOT_REACHED (the oracle challenge is already solved, or SUT-01 could not create the owner's order), M1_ORACLE_FLIPPED, M1_ORACLE_NOT_FLIPPED, M1_IDOR_BYPASS_OBSERVED, M1_IDOR_BLOCKED, M1_RESPONSE_OTHER, M2_EXPECTED_ALERT, M2_NO_EXPECTED_ALERT, ZAP_START_FAILED, ZAP_API_ERROR, ZAP_SCAN_TIMEOUT, INTERRUPTED_. A non-detection is an observation (status SUCCESS, matches_expected false), never an error; a ZAP failure is status ERROR and attribution TOOLING.

Matching rules (section 4b): an M2 alert counts only when its rule id, request method and normalized path all equal the cell's expectation; every other alert is recorded and never counted. An M1 SUT-05 cell is decided by the `solved` flag, not by the response of the sequence. The IDOR cell is decided by the GET.

## 3. instance.json (interface version 1)

As in E05: `surfaces.api.base_url` (SUT-05: the Packaged Distributions instance, port 3000; SUT-01: the backend), and a `process` block (pgid, port, start_command, cwd, env, readiness_url, readiness_timeout_s, stop_timeout_s) because every execution restarts the process. The file is never modified by the executor.

## 4. Integrity

`run-condition.sh` embeds the sha256 of every `executor/*.py` and of `requirements.txt`, and refuses an unlisted Python file under `executor/`. After any edit run `python3 tests/embed_digests.py`. No file of the executor, of a workflow or of a comment may carry the literal name of the agent-instructions file (the public export aliases it and breaks the digests). The ZAP image is addressed by digest in `executor/zap.py` and is part of the hashed code; the conditions file is hashed with the campaign configuration at START.

## 5. Tests (static; nothing contacts a SUT or a ZAP)

`PYTHONDONTWRITEBYTECODE=1 python3 -I -m unittest discover -s tests` from this directory (about 2.5 minutes: the restarts are real processes). 79 tests: the cells file and the classifier, zap.py against a fake ZAP API, the attempt loop for every M1 and M2 cell family against fake systems, the manifest check against schemas/run-manifest.schema.v2.json, the digest lock and the entry point, and the static checks of .github/workflows/e11-environment-verification.yml (dispatch-only, read-only permissions, the cells listed, the ZAP image pulled by the executor's digest, every bash and Python block parses).

## 6. Not verified here (decided by the first DRY_RUN, never by this draft)

See IMPLEMENTATION-NOTES.md, section 3. In short: the ZAP API method names and parameters; that a runner pulls and starts the image by digest; the installed add-on list; the three vulnerable paths of the packaged SUT-05; the `/ftp` outcome of rule 0; the JSON login body as an injectable target; the timing of one M2 execution.
