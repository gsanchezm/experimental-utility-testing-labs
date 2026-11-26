# E08-performance executor -- DRAFT (operation OP-PREP-E08)

**DRAFT. Not frozen, not locked, not dispatched.** Nothing in this directory starts, configures, authorizes, or dispatches a campaign. Its measured workflow fails closed until the E08 campaign START, the locked "Campaign configuration" record, a dispatch authorization of the human research lead (protocol/agent-governance-v6.md, Section 3.7, FROZEN-PRE-DATA since 2026-11-06), a controlled-instance verification on GitHub Actions, the frozen dispatch prompt and the toolchain entry of the instrument are all present. Working basis: experiments/E08-performance/design-brief-draft.md and campaign-configuration-draft.md; the conditions are in conditions-draft.json. Deviations and open items: IMPLEMENTATION-NOTES.md (same folder).

| Field | Value |
|---|---|
| Campaign | E08-performance (experiments/E08-performance/README.md; status NOT_STARTED) |
| Modality | Performance (protocol/study-design-v1.md, section 7), web only |
| Hypothesis | H5 (protocol/statistical-analysis-plan-v1.md, section 4.3), descriptive count comparison, CONFIRMATORY for SUT-01 against SUT-02 and SUT-03 |
| Assigned SUTs | SUT-01 (one condition), SUT-02 (one condition), SUT-03 (two conditions); SUT-04 to SUT-06 have no condition |
| Instrument | Playwright for Python 1.63.0 (manifests/toolchain-manifest.yaml, `tools.web_runner`), hash-pinned in requirements.txt, driving Chromium (the build that version installs, recorded per run); the in-page measurement script `executor/probe.py` (probe version `e08-probe-v1`) reads only the browser's own Performance APIs and adds no dependency |
| Entry point | run-condition.sh (bash), which verifies the embedded digests before anything else |

## 1. What one execution does, and what it never does

For one condition the job runs N = 50 executions one after the other on one shared instance (nothing is restarted). One execution is: the **starting-state check** (SUT-01: the web surface and the API health answer 200 and both accounts log in through `POST /api/auth/login` with the behavior the condition declares; SUT-02 and SUT-03: the surface answers 200); the **method**, three page loads (the degraded load D and two baseline loads Ba and Bb) in the rotating order of conditions-draft.json (`load_orders`, by the absolute execution index), each in a **fresh browser context** (headless Chromium, viewport 1280 x 800, time zone UTC, locale en-US) with the measurement script injected before any page script; the **classification** from the three raw snapshots by the rule of the condition; the **record** (bundle, run manifest last).

Per load the executor logs in (SUT-01: API login, then a first load of the web root and one injection of the client state of the E03 SUT-01 web realization; SUT-02: the login form of the application; SUT-03: the login page of the performance test area), calls `run.mark_stimulus_sent()` immediately before the first **measured navigation** (the boundary of attribution), navigates to the page with `wait_until='commit'`, waits for the page's own ready signal (SUT-01 and SUT-02; bounded) or for the fixed observation window (SUT-03: 8000 ms from the start of the document), and reads the raw snapshot of the probe. It never performs a Required Action (`actions` is absent), never retries, never writes under `raw-data/` outside a measured workflow run, and never reads another campaign's or another SUT's output.

## 2. Conditions (candidate ids, not frozen until the configuration is locked)

| Condition id | SUT | Degraded load D | Paired baseline | Metric (unit) | Rule |
|---|---|---|---|---|---|
| E08-SUT01-WEB-DELAY | SUT-01 | `performance_glitch_user`, `/catalog` | `standard_user`, `/catalog` | first_item_ms (ms) | D - Ba >= 2500 |
| E08-SUT02-WEB-BLOCK | SUT-02 | `performance_glitch_user`, `/inventory.html` | `standard_user`, `/inventory.html` | longest_longtask_ms (ms) | D - Ba >= 4500 |
| E08-SUT03-WEB-LCP | SUT-03 | `/sut/ui/high-lcp` | `/sut/ui/zero-cls` | lcp_ms (ms) | D - Ba >= 2500 |
| E08-SUT03-WEB-CLS | SUT-03 | `/sut/ui/high-cls` | `/sut/ui/zero-cls` | cls (score) | cls(D) > cls(Ba) and a shift of `#target-text` at or after 3500 ms |

The false-positive record of an execution applies the same difference rule to the later baseline against the earlier one (Bb against Ba). Details, evidence ids and the predeclared reading of the CLS page: campaign-configuration-draft.md, sections 2 to 4c.

## 3. Outcome categories and the run status

| outcome_category | status | matches_expected | Meaning |
|---|---|---|---|
| DETECTED | SUCCESS | true | the rule holds for D against Ba, every required ready signal present |
| NOT_DETECTED | FAILURE | false | valid measurements, the rule does not hold (a recorded non-detection, not an error) |
| INCONCLUSIVE_READY_SIGNAL_MISSING | INCONCLUSIVE | null | D or Ba never showed the page's own content (a login page, an error page, a timeout) |
| INCONCLUSIVE_METRIC_ABSENT | INCONCLUSIVE | null | the browser did not offer the entry type, or the page painted nothing measurable |
| INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED | INCONCLUSIVE | null | LCP only: the delayed image of the external host was not painted as a largest-paint candidate of D; attribution EXTERNAL |
| START_SURFACE_NOT_READY, START_ACTIVATION_NOT_CONFIRMED | ABORTED | null | a surface did not answer, or an account's activation (behavior, cookie) was not confirmed |
| INTERRUPTED_ | ERROR | null | an exception of the harness or of the client, or the watchdog (420 s per execution) |
| STUB_NO_BUNDLE | ERROR | null | the bundle of an execution could not be completed; a stub is written |

Attribution is mechanical (E05 D-16): TOOLING for an exception before the first measured navigation, SUT otherwise and when uncertain, EXTERNAL for the one external-image category. The per-execution detail (the three metric values, the difference, the rule results, the false-positive record, the order) is `evidence/NNN-detection.json`; the raw snapshots are `evidence/NNN-loadK-<role>-probe.json`, so every metric can be recomputed from the evidence.

## 4. Instance, environment, and bundle

- `instance.json` (interface version 1; the layout of experiments/E03-resetability/executor/README.md, section 6): surfaces `web` at `http://127.0.0.1:3000` (SUT-01 also `api` at `http://127.0.0.1:8000`), the provisioning record (repository, commit, route), `process` (SUT-01 only, recorded and never used for a restart).
- Bundle (`executions/<run_id>/` of the job's artifact; a measured run is imported as `raw-data/E08-performance/<SUT>/<run_id>/`, the path its run manifest lists; the artifact root holds the job-level files): `run-manifest.json` (written last), `executor.log`, `attempt-record.json`, `tool-versions.json`, `ci-provenance.json`, `runtime-environment.json`, and `evidence/` with one numbered file per record: `instance`, the login transcripts (passwords redacted), `activation`, per load `loadK-<role>-probe`, `-network-log`, `-console-log` (and a screenshot of each degraded load), and `detection`.
- The scrubber replaces the password of each account, every access token, host paths, and private network addresses before any file is kept. The documented dummy password of SUT-03 (`password`, shown in its own page labels) is not registered as a secret: the word is part of the page and of every form field name.

## 5. Run manifest (schemas/run-manifest.schema.v2.json)

`campaign_id` E08-performance; `experiment_id` and `condition` the condition id; `sut_id`; `platform` web; `modality` "Performance"; `attempt`; `outcome` {status, expected, observed, matches_expected, outcome_category}; `behavior_class` the condition's (deterministic, or external dependency for the LCP condition); `reset_mechanisms`, `establishment_mechanisms`, `target_state_id` and `starting_state_id` null; `seed` null; no `actions`, no `scenario`; `agent_role` ORCHESTRATOR; `prompt_version` the frozen executor prompt id; `protocol_version` v1; `toolchain` (web_runner, browser, performance, executor_runtime, scripting_runtime, and api_client for SUT-01, each with a version observed in the run); `sut_provenance` (the components with repository and commit). tests/test_attempt.py checks the manifests against the schema subset.

## 6. Implementation integrity (the E03 lock mechanism, with its own digests)

`run-condition.sh` embeds the sha256 of every `executor/executor/*.py` file and of `requirements.txt`, verifies them, and refuses any unlisted Python file under `executor/executor/`, before anything else. The digests are computed by `tests/embed_digests.py` (run it last, after every edit of an executor file); they are not typed. `tests/test_digests.py` re-checks them independently. The gate of the measured workflow locks the single hash of `run-condition.sh`, which covers the whole implementation, and checks that `tools.performance` of the toolchain manifest equals the Playwright pin of requirements.txt and the probe version of probe.py.

## 7. Tests (static; run on any Python 3, with PyYAML for the gate test and Node.js for the probe test)

Run from `tests/`: `python3 -m unittest discover -s . -p 'test_*.py' -v` (set `PYTHONPATH` to a PyYAML copy when the interpreter has none).

| File | What it checks |
|---|---|
| test_classify.py | the four metrics on synthetic snapshots (session windows of CLS included), the rule of each condition at its threshold, the false-positive record, the inconclusive categories, the external-image rule, attribution and the manifest outcome |
| test_config.py | the conditions file and its validation (one mutation per refusal), the load-order rotation |
| test_probe.py | the in-page script, run in Node.js against a mock of the browser APIs: observers registered with buffering, entries from the callback and from the queue, shift sources, the watch stamps |
| test_attempt.py | the attempt loop with a fake realization (no browser): categories, orders, attribution, bundles, manifests against the schema, no secret in any file, the stub path |
| test_run.py | the entry checks of `executor.run` and the registry of realizations |
| test_gates.py | the measured gate extracted from the workflow and run on fake trees: a must-pass tree, one mutation per must-fail gate, the further-attempt approval, and the as-is repository state (must fail closed) |
| test_workflows.py | both workflows: dispatch-only, read-only, the same provisioning steps in both, no expression inside a run script of the measured workflow, bash and Python of every block, actionlint and shellcheck when available |
| test_digests.py, test_run_condition.py | the embedded digests; a tampered or unlisted file is refused by the entry point |

Not tested here: the behaviour of the browser (no Chromium in the test environment), the Performance APIs in Chromium, and the live SUTs. The first real evidence of these is an ENVIRONMENT_VERIFICATION DRY_RUN (section 9).

## 8. Dispatch authorization record (governance v6, Section 3.7) -- the fields the gate reads

The human research lead issues the record; no agent writes it as an authorization. The gate reads `manifests/e08-dispatch-authorization-sut0N-v*.yaml` and matches `authorization_id` to the dispatch input. Required fields: `authorization_id`, `authorization_date`, `issued_by` (`human research lead`), `status` (ISSUED), `record_validity` (VALID), `dispatch_eligibility` (ELIGIBLE), `revoked` (false), `assigned_sut`, `conditions` (the executable conditions of that SUT), `n_executions` (50), `attempt` (1), `campaign_start_authorization_id`, and `frozen_inputs` with `executor_implementation_sha256` and `executor_prompt_sha256` (the SHA-256 of the frozen prompt file). A further attempt needs a record `manifests/e08-further-attempt-approval-sut0N-v*.yaml` of class `E08_FURTHER_ATTEMPT_APPROVAL` (gate G-E08-A2).

## 9. Environment verification and DRY_RUN

`.github/workflows/e08-environment-verification.yml` (dispatch-only, manual) provisions the condition's SUT from the pinned commit on a GitHub-hosted runner, writes `instance.json` with record class DRY_RUN, and runs this executor for two or three executions per condition (never fifty). Its bundles are labeled DRY_RUN and are never imported, never measured and never a source for an expectation. The plan of the rounds is experiments/E08-performance/dry-run-plan-draft.md.
