# E09-accessibility executor -- DRAFT (operation OP-PREP-E09)

**DRAFT. Not frozen, not locked, not dispatched.** Nothing in this directory starts, configures, authorizes, or dispatches a campaign. Its
measured workflow fails closed until the E09 campaign START, the locked "Campaign configuration" record, a dispatch authorization of the
human research lead (protocol/agent-governance-v6.md, Section 3.7, which is itself a DRAFT), a controlled-instance verification on GitHub
Actions, and a locked activation password are all present. Working basis: experiments/E09-accessibility/design-brief-draft.md,
campaign-configuration-draft.md, and axe-core-pin-proposal-draft.md. Deviations and open items: IMPLEMENTATION-NOTES.md (same folder).

| Field | Value |
|---|---|
| Campaign | E09-accessibility (experiments/E09-accessibility/README.md; status NOT_STARTED) |
| Modality | Accessibility -- Web only (protocol/study-design-v1.md, section 7) |
| Hypothesis | H5 (protocol/statistical-analysis-plan-v1.md, section 4.3), descriptive count comparison, CONFIRMATORY |
| Assigned SUT | SUT-01 only (the one SUT with a candidate ground-truth condition; SUT-02 to SUT-06 have no condition) |
| Scanner | axe-core 4.14.0 (npm tarball, integrity `sha512-9WTZ...` as in executor/executor/scanner.py), browser build `package/axe.min.js` with sha256 `20c09fe1...` |
| Web runner | Playwright for Python 1.63.0 (manifests/toolchain-manifest.yaml, `tools.web_runner`), hash-pinned in requirements.txt |
| Entry point | run-condition.sh (bash), which verifies the embedded digests before anything else |

## 1. What one attempt does, and what it never does

For one condition and one attempt the executor: refuses on any inconsistent input (no manifest); reads the instance interface
(instance.json, written by the provisioning steps); verifies the pinned axe-core tarball (sha512) and its browser build (sha256) before
any browser starts; logs in through the documented API route as the condition's account and records the login response's `behavior`
(the activation record); starts one headless Chromium context (viewport 1280 x 800, time zone UTC, locale en-US, as the E03 web realization);
loads the web root once, injects the client state of the E03 SUT-01 realization (market MX, language es, the token and account keys,
an empty client cart); loads the Catalog page (`/catalog`); waits for the product headings (bounded), then settles the network (bounded);
records the DOM snapshot, a screenshot, the catalog responses it captured, and the network and console logs; runs axe-core once with the
explicit rule set; decides the ground truth from the DOM records; classifies the outcome; writes the bundle; writes `run-manifest.json` last.

It never performs a Required Action (`actions` is empty; HUMAN DECISION HD-15 default), never retries, never calls the SUT from Python
to read the catalog (a call from Python would draw a new activation mode; the corroboration uses the page's own captured responses), never
writes under `raw-data/` outside a measured workflow run, and never reads another campaign's or another SUT's output.

## 2. Conditions (candidate ids, not frozen until the configuration is locked)

| Condition id | Kind | Account | Behavior class (manifest) | Expected outcome (outcome.expected) |
|---|---|---|---|---|
| E09-A11Y-SUT01-MISSING-NAME | GLITCH | `a11y_glitch_user` (documented in the SUT-01 README; SUT01-EV-0017) | stochastic (the server draws the mode per call; SUT01-EV-0018) | empty-heading reports a node of a product heading, when every product heading is empty (missing_name draw) |
| E09-CTRL-SUT01-STANDARD | CONTROL | `standard_user` (the account of the E03 SUT-01 realization) | null, TBD until confirmed by the lock (brief, section 13 item 3) | empty-heading reports no node of a product heading (rule absent) |

The control is not counted in H5. The `wrong_lang` and `extreme_text` draws of the glitch account are not ground-truth instances: they are
recorded as NO_GROUND_TRUTH_INSTANCE and are never added to the denominator.

## 3. Ground truth (decided from the DOM) and detection (decided from the scanner result)

Ground truth is decided in Python from the DOM records read at scan time, for every `h2[data-testid^="pizza-name-"]` element
(`classify.dom_state`; the same selector and fields as `sut01_catalog.DOM_RECORDS_JS`):

| DOM state | Meaning | Outcome for the glitch condition |
|---|---|---|
| NO_CARDS | no product heading rendered | INCONCLUSIVE, INCONCLUSIVE_NO_PRODUCT_HEADINGS |
| NOT_EMPTY | no product heading empty | INCONCLUSIVE, NO_GROUND_TRUTH_INSTANCE (draw is not missing_name) |
| MIXED | some empty, some not | INCONCLUSIVE, INCONCLUSIVE_MIXED_DOM_STATE |
| EMPTY_ARIA_NAMED | every heading empty, at least one with an ARIA name or title | INCONCLUSIVE, INCONCLUSIVE_ARIA_NAME_PRESENT (the predeclared rule cannot fire by its definition; the brief, section 4.3, asks for a re-decision before lock: HUMAN DECISION, see IMPLEMENTATION-NOTES) |
| ALL_EMPTY | ground truth: every product heading empty, none ARIA-named | DETECTED or NOT_DETECTED (below) |

A "heading empty" means its text content is whitespace-only. The DOM snapshot (`dom-snapshot.html`) is saved so that the decision can be
replayed (tests/dom_records.py reads a saved snapshot in the same way).

Detection (`classify.matching_nodes`): the predeclared rule `empty-heading` in `violations`, with at least one node whose HTML opens an
`h2` whose `data-testid` starts with `pizza-name-`. The match is made on `node.html`, because axe-core generates its own `target`
selectors (which need not contain the test id); the target strings of every matching node are recorded in the outcome. Rule presence
elsewhere on the page does not count. The total count of `empty-heading` nodes is recorded descriptively (`rule_nodes_total_descriptive`),
never as the judgment.

The axe-core run uses the explicit rule scope (HUMAN DECISION HD-4, option iii): `{"runOnly": {"type": "rule", "values": ["empty-heading"]}}`.
`image-alt` is not run (HD-3): under the pinned source it cannot fire for `alt=""` (pin proposal, section 4).

Corroboration (never the judgment): each `GET /api/pizzas` response the page itself caused (captured with its body after the page
settled) is classed MISSING_NAME_BODY, NON_EMPTY_NAMES, MIXED_NAMES, or UNPARSEABLE; the record states AGREES, DISAGREES, or
NOT_INTERPRETABLE against the DOM state, and whether all captured responses carry one draw (SINGLE_DRAW) or not (MULTIPLE_DRAWS).

## 4. Outcome categories and the run status (HUMAN DECISION HD-E09-B, default used)

| outcome_category | status | matches_expected | Meaning |
|---|---|---|---|
| DETECTED | SUCCESS | true | glitch, ground truth, at least one matching node |
| NOT_DETECTED | FAILURE | false | glitch, ground truth, no matching node |
| NO_GROUND_TRUTH_INSTANCE | INCONCLUSIVE | null | glitch, the draw is not missing_name; recorded, not counted as a failure nor a rate of zero |
| INCONCLUSIVE_* (above) | INCONCLUSIVE | null | the DOM state cannot be decided by the rule |
| CONTROL_RULE_ABSENT | SUCCESS | true | control, no matching node |
| CONTROL_RULE_PRESENT | FAILURE | false | control, a matching node (an unexpected finding; recorded) |
| INCONCLUSIVE_CONTROL_DOM_STATE | INCONCLUSIVE | null | control DOM not NOT_EMPTY |
| ABORTED_BEFORE_SCAN | ABORTED | null | stopped before the scan (for example activation not confirmed by the login response) |
| SCANNER_INTEGRITY, RUNNER_FAULT, WATCHDOG | ERROR | null | scanner pin mismatch, runner or infrastructure fault, or the whole-run budget (900 s) |

A non-ground-truth draw is a recorded attempt and is excluded from the detection denominator by the predeclared rule (design brief,
section 3g); the denominator is fixed before any data (detections over ground-truth instances among the N = 50 attempts).

## 5. Stochastic activation handling

- One attempt is one page load and one scan. The mode is drawn by the server per call; the executor cannot choose or seed it, and
  no seed is recorded (`seed` null). Draws are classified after the run, never configured.
- N = 50 attempts per condition (HD-9 default), each a separate execution (EX0001 to EX0050) dispatched once under the dispatch
  authorization. No adaptive stopping (HD-1 option b is not used): the number of ground-truth instances is a derived count.
- Each attempt records the realized draw (MISSING_NAME, NOT_MISSING_NAME, or UNDECIDED) from the DOM, the body corroboration, and the
  draw consistency of the page load.
- The control has no draw of its own: the behavior of its account is recorded from the login response (activation record).

## 6. Pins and the scanner loading route (HD-12 option i, HD-16 default)

- The workflow downloads `https://registry.npmjs.org/axe-core/-/axe-core-4.14.0.tgz` during provisioning (before the executor) and checks its
  sha512 against the pinned integrity string. The executor checks the same tarball again before use (`scanner.read_browser_build`) and reads
  `package/axe.min.js` from inside it (no extraction to disk), checks its sha256 against the pin, and injects the text with
  `add_script_tag(content=...)`. The page's `axe.version` must equal `4.14.0`, or the run is refused as a scanner-integrity ERROR.
- The Python executor needs no Node.js. The run itself performs no network access beyond the SUT instance (the provisioning step is not part of
  the run).
- The pin values in `executor/executor/scanner.py` are the registry values recorded in the pin proposal and re-checked on 2026-11-06
  (version metadata and tarball fetched into an empty scratch directory; both digests reproduced).

## 7. Instance, environment, and bundle

- `instance.json` (interface version 1; the layout of experiments/E03-resetability/executor/README.md, section 6): surfaces `web` at
  `http://127.0.0.1:3000` and `api` at `http://127.0.0.1:8000`, the provisioning record (repository, commit, route), `process` null.
- Environment record (`evidence/.../environment.json`): Chromium build, viewport, browser locale, time zone, market, runner image.
- Bundle (`raw-data/E09-accessibility/SUT-01/<run_id>/` for a measured run): `run-manifest.json` (written last), `executor.log`, the
  workflow files (`stdout.log`, `stderr.log`, `exit-status.txt`, `finished-at.txt`), `ci-provenance.json`, `runtime-environment.json`, and
  `evidence/` holding one numbered file per record (`Run.jsonfile` and `Run.text` name them `NNN-<name>.<ext>`): `instance`, `login-*`
  (the login transcript; the password is redacted), `activation` (login status, username, behavior, confirmed), `precondition` (first-load
  status, the `omnipizza-release` value read and not written, the keys injected), `environment` (Chromium build, viewport, browser locale,
  time zone, market, runner image), `dom-snapshot` (`page.content()` at scan time), `dom-heading-records`, `catalog-responses` (status and
  body of each captured catalog response), `detection` (matching nodes, descriptive total, options object, axe version, DOM state,
  corroboration, draw consistency, settle record), `axe-result` (the full axe.run result), `screenshot` (PNG), `network-log`,
  `console-log`, and `storage-after-load`.
- The scrubber replaces the password of each account, every access token, host paths, and private network addresses before any file is kept.

## 8. Run manifest (schemas/run-manifest.schema.v2.json; HD-14 default)

Values: `campaign_id` E09-accessibility; `experiment_id` E09-A11Y-SUT01 (HUMAN DECISION, no E03 analog); `sut_id` SUT-01; `platform` web;
`modality` "Accessibility — Web only" (the exact enum literal); `condition`; `attempt`; `outcome` {status, expected, observed,
matches_expected, outcome_category} (`outcome` allows no other key); `actions` []; `reset_mechanisms` null; `establishment_mechanisms` null;
`target_state_id` and `starting_state_id` null; `seed` null; `behavior_class` as above; `related_evidence_ids` (SUT01-EV-0001, -0017, -0018, -0019);
`agent_role` ORCHESTRATOR; `prompt_version` the frozen executor prompt id (a run needs a non-null value; see IMPLEMENTATION-NOTES, HD-17);
`protocol_version` v1; `toolchain` (web_runner, browser, accessibility, api_client, executor_runtime, scripting_runtime, each with a version
observed in the run, or null with the reason in `notes`); `sut_provenance` (web and api components with repository and commit).
`scenario` is omitted: E09 has no canonical scenario (HD-13 default). Tests/test_manifest.py checks the build against the schema subset.

## 9. Implementation integrity (the E03 lock mechanism, with its own digests)

`run-condition.sh` embeds the sha256 of every `executor/executor/*.py` file and of `requirements.txt`, verifies them, and refuses any unlisted
Python file under `executor/executor/`, before anything else. The digests are computed by `tests/embed_digests.py` (run it last, after every
edit of an executor file); they are not typed. `tests/test_digests.py` re-checks them independently. The gate of the measured workflow locks
the single hash of `run-condition.sh`, which covers the whole implementation. The implementation requirements of this directory are a
separate lock with the same pins as E03 (HD-18); the E03 implementation is not imported.

## 10. Tests (static; run on the sandbox or any Python 3 with PyYAML for the gate and workflow checks)

Run from `tests/`: `python3 -m unittest discover -s . -p 'test_*.py' -v`. `tests/RECORDED-OUTPUT.txt` is the recorded output of the last run.

| File | What it checks |
|---|---|
| test_classify.py | ground truth states from synthetic DOM fixtures; detection on synthetic axe-shaped fixtures; corroboration; activation; the outcome mapping |
| test_scanner.py | tarball sha512 and browser-build sha256 verification on synthetic archives; refusal paths; the real pinned tarball when `E09_AXE_TARBALL_FOR_TEST` names a local copy |
| test_manifest.py | the manifest of each outcome class validates against schemas/run-manifest.schema.v2.json (subset validator; the schema's keywords are all supported) |
| test_gates.py | the measured gate extracted from the workflow and run on fake trees: a must-pass tree, one mutation per must-fail gate, and the as-is repository state (must fail closed) |
| test_workflows.py | both workflows: dispatch-only, no expression inside any run script, dispatch inputs read from the step environment, the OP-CI-15 length estimate, pins agree with the implementation, the measured job's sparse checkout, actionlint and shellcheck when available, module imports, and publication hygiene of every new file |
| test_digests.py, test_run_condition.py | the embedded digests; a tampered or unlisted file is refused by the entry point; an unmodified copy writes no manifest when refused |

Not tested here: the browser behaviour (Playwright is not installed in the sandbox; no Chromium), the rule behaviour of axe-core in a DOM
(no DOM engine is available), and the live SUT. The first real evidence of these is an ENVIRONMENT_VERIFICATION run (see below).

## 11. Dispatch authorization record (governance v6, Section 3.7) -- the fields the gate reads

The human research lead issues the record; no agent writes it as an authorization. The gate reads `manifests/e09-dispatch-authorization-*.yaml`
and matches `authorization_id` to the dispatch input. Required fields: `authorization_id`, `authorization_date`, `issued_by`
(`human research lead`), `status` (ISSUED), `record_validity` (VALID), `dispatch_eligibility` (ELIGIBLE), `assigned_sut` (SUT-01),
`conditions` (the executable conditions), `n_executions` (50), `attempt` (1), `campaign_start_authorization_id`, and `frozen_inputs` with
`executor_implementation_sha256` and `executor_prompt_sha256` (the SHA-256 of the frozen prompt file). The gate also requires the Section 3.7
heading and a non-DRAFT state of protocol/agent-governance-v6.md.

## 12. Environment verification and DRY_RUN

`.github/workflows/e09-environment-verification.yml` (dispatch-only, manual) provisions SUT-01 web and api from the pinned commit, verifies
the tarball, writes `instance.json` with record class ENVIRONMENT_VERIFICATION, and runs `executor.verify` (non-measured): interface, tarball, the login behaviour
of both accounts, and, for each account whose activation is confirmed, one Catalog load and one explicit-rule axe run in a browser. It writes
`verification.json` and no run manifest; its artifact is labeled ENVIRONMENT_VERIFICATION and is never imported. The input `dry_run` additionally
runs the executor once per condition after the verification passed (DRY_RUN, never imported, never measured). While the glitch account's
password is not locked, the verification reports NOT_VERIFIED and the job fails by design.
