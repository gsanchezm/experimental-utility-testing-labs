# E09-accessibility executor -- implementation notes (DRAFT, operation OP-PREP-E09)

**DRAFT. Nothing here starts, locks, authorizes, freezes, or dispatches anything.** Campaign status: NOT_STARTED (unchanged). Protocol
state when this file was written: protocol/agent-governance-v6.md was a DRAFT and not in force; protocol/agent-governance-v5.md was the
document in force. Update 2026-11-12 (representation only; nothing below was re-run): protocol/agent-governance-v6.md has been
FROZEN-PRE-DATA since 2026-11-06 and v5 is AMENDED, so gate G-4 now passes on the real file (its `| Protocol state |` field and its
"### 3.7 Dispatch authorization" heading were checked directly); statements below that say v6 is a DRAFT describe the state at writing.

## 0. Base, sources, and the hard rules of this task

- The worktree was created from the public snapshot commit 95efcff4, which predates the E09 drafts and governance v6. The drafts were read
  from the main repository's commit c19fadfd through the read-only git object database, and the three design briefs and governance v6 were
  compared byte for byte with the main working tree (identical). Nothing was written to the main repository.
- Nothing was committed, staged, pushed, or dispatched; no `gh` command ran; no SUT was started; no `raw-data/` file or derived result was read.
- Files are new and untracked in the worktree. Every executor file that is embedded in the lock was re-hashed after its last edit
  (tests/embed_digests.py; tests/test_digests.py checks it independently).
- The public-snapshot agent-instructions file is referred to only as "the agent-instructions file"; no file name of it is written anywhere.

## 1. What is done

| Deliverable | Path (repository-relative) | State |
|---|---|---|
| Executor package (pure classifier, scanner loader, config, common, instance, browser driver, scenario, entry, verification) | experiments/E09-accessibility/executor/executor/ | DRAFT; imports and compiles; browser code not executed (no Playwright here) |
| Entry point with the embedded-digest lock | experiments/E09-accessibility/executor/run-condition.sh | DRAFT; digests embedded by script; refusal tested |
| Hash-pinned requirements (Playwright 1.63.0 and its dependencies, copied unchanged from E03) | experiments/E09-accessibility/executor/requirements.txt | DRAFT; pin lines byte-identical to the E03 file (checked) |
| Executor README (realization, outcome categories, stochastic handling, pins, manifest mapping, record vocabulary) | experiments/E09-accessibility/executor/README.md | DRAFT |
| Measured workflow (dispatch-only, fail-closed gate, first attempt, default branch, expressions only in environment) | .github/workflows/e09-measured-execution.yml | DRAFT; refuses every dispatch today |
| Environment verification workflow (dispatch-only; DRY_RUN option as E03) | .github/workflows/e09-environment-verification.yml | DRAFT; fails today by design (glitch password) |
| Tests and recorded output | experiments/E09-accessibility/executor/tests/ (RECORDED-OUTPUT.txt is the record of the last run) | DRAFT; counts in the final report, not repeated here |

## 2. What is NOT done

- No "Campaign configuration" section exists in experiments/E09-accessibility/README.md. This is deliberate: the section is locked only at the
  START (protocol/change-control-v1.md, section 7). The E09 README was not edited.
- No campaign START row, no dispatch authorization record, no controlled-instance status record for E09, no probe record, no toolchain entry for
  axe-core (manifests/toolchain-manifest.yaml, `tools.accessibility`, is still null), no protocol or manifest change of any kind.
- The browser path (Playwright launch, page load, add_script_tag, axe.run, page DOM extraction) has not been executed: Playwright is not
  installed in the sandbox and no Chromium is available. axe-core has not been run against any page, including synthetic fixtures: no DOM
  engine is available without fetching packages beyond the allowed pin re-check. The axe-core rule behaviour is taken from the pin proposal's static
  reading, not from execution. The synthetic axe-shaped JSON fixtures are unit-test inputs, not axe output.
- The real pinned tarball was fetched once (into an empty scratch directory outside the repository) for the pin re-check; its sha512 and the
  `axe.min.js` sha256 were verified by test_scanner.py through the environment variable E09_AXE_TARBALL_FOR_TEST (outside the repository).
- The SUT-01 DOM checks named in the brief's section 13 are not done: the probe of the classifier, the `h2` ARIA attributes in the pinned frontend
  source, the `/catalog` route in the pinned source, the control account's behavior value, the single catalog fetch per load, the `-desktop`
  selector suffix. They are the content of the ENVIRONMENT_VERIFICATION run and of the probe record the lock requires.
- The gate has no way to check the probe record's content: it checks that the configuration names an existing probe record file.

## 3. What is BLOCKED (and by whom)

| Blocker | Who decides or does it | Notes |
|---|---|---|
| Activation password of `a11y_glitch_user` (executor/executor/config.py, `ACCOUNTS`) | human research lead (HD-E09-A) | **RESOLVED 2026-11-12** (representation of the decision; see manifests/campaign-execution-decisions-v5.yaml). Not in the E01 evidence rows (SUT01-EV-0017 to -0019), not guessed: read read-only, without a clone, from the account table of the SUT-01 README at the pinned commit 9ca37674 (README blob sha256 9c49c616...), on the explicit human authorization of 2026-11-12; `config.py` now locks it and the implementation digests were re-embedded. The refusal and NOT_VERIFIED paths stay as the fail-closed behavior for an unlocked password. |
| E09 campaign START (NOT_STARTED to IN_PROGRESS row with the authorization id) | human research lead | protocol/change-control-v1.md, section 7 |
| "Campaign configuration" lock of experiments/E09-accessibility/README.md | ORCHESTRATOR after the human approval of the exact text | The gate reads the section and names the items listed in section 5 below |
| Governance v6 freeze (DRAFT to FROZEN-PRE-DATA at its content SHA-256) | human research lead, explicit approval | Done 2026-11-06 (manifests/agent-governance-v6-amendment-v1.yaml). Until then the gate refused every dispatch, by design |
| Dispatch authorization per SUT (governance v6, Section 3.7) | human research lead, issued in writing | Field names defined in executor/README.md, section 11 (not in governance v6; a choice of this draft) |
| Controlled-instance verification of both conditions on GitHub Actions | ORCHESTRATOR (after HD-E09-A) | Environment verification run; import of its artifacts; status record |
| Probe record of the classifier and the rule behaviour (brief section 13, item 1) | ORCHESTRATOR, from the verified run's imported artifacts | The lock names the probe record path; the gate checks the file exists |
| `tools.accessibility` pin in manifests/toolchain-manifest.yaml | ORCHESTRATOR, after the human approval | The gate requires version, npm integrity, pinned_by, and pinned_at |
| Unresolved-register entry or correction record for the discrepancy of SUT01-EV-0019 (HD-19) | ORCHESTRATOR with the human approval (the execution plan lists it as not given) | No E01 record is edited. The `image-alt` half of SUT01-EV-0019 cannot occur under the pinned source (pin proposal, section 4). |
| Public export of this work | human research lead, pushed in person | Not requested; not done |

## 4. How a DEVELOPMENT or DRY_RUN would be made after approval

- **DEVELOPMENT (operator workstation, never measured):** install requirements.txt with `--require-hashes --only-binary :all:` into a Python
  3.12 environment, then `playwright install chromium`. Download the pinned tarball into an empty directory outside the repository and export
  `AXE_TARBALL` to it. Start the SUT-01 web and api locally at the instance URLs (127.0.0.1:3000 and 127.0.0.1:8000) from the pinned commit,
  write a hand-made `instance.json` with `record_class` DEVELOPMENT, export the environment names of run-condition.sh (CONDITION_ID,
  ASSIGNED_SUT, EXECUTION_ID as DV plus four digits, ATTEMPT, EXECUTOR_PROMPT_VERSION, OUTPUT_DIR named after the run id, PROVENANCE_JSON,
  RUNTIME_ENVIRONMENT_JSON, RECORD_CLASS DEVELOPMENT, INSTANCE_JSON), and run `bash experiments/E09-accessibility/executor/run-condition.sh`
  from the repository root. The OUTPUT_DIR must be outside `raw-data/`. The run refuses without a manifest while the password is None.
- **DRY_RUN (hosted):** the environment verification workflow with `dry_run` true, after its verification step passed. Its DRY_RUN bundles are
  uploaded as artifacts and never imported.
- **ENVIRONMENT_VERIFICATION (hosted):** the same workflow without `dry_run`; its record is `verification.json`, never a run manifest.

## 5. What a locked configuration must name (what the gate checks; brief section 9 and configuration draft)

The condition id (one of the two candidate ids), `run-manifest.schema.v2.json`, the executor prompt version and its frozen file, the
implementation SHA-256 of run-condition.sh, the axe-core 4.14.0 pin with its npm integrity string and the browser build sha256, `N = 50`, the
SUT-01 web commit of manifests/sut-manifest.yaml, a line `Probe record: <repository path>` whose file exists, the declared behavior class,
`H5` as CONFIRMATORY, and the scenario mapping decision (`HD-13`).

## 6. HUMAN DECISIONs (each with the default used; the human research lead may veto any default by its id)

The execution plan of 2026-11-05 (manifests/campaign-execution-plan-v1.yaml) adopts the recommended defaults of the design briefs as the working
proposal, so the brief defaults below are used.

| Id | Decision | Default used | Status |
|---|---|---|---|
| HD-1 | Stochastic activation design | (a): one glitch condition, N = 50 attempts, realized-draw stratification from the DOM | as recommended |
| HD-2 | H5 count unit for SUT-01 | 1 (the mode with a named rule) | stated in the configuration requirements |
| HD-3 | Expected rule set | `empty-heading` only; `image-alt` not run | as recommended |
| HD-4 | Scanner rule scope | (iii): explicit `runOnly` rule `empty-heading`, recorded in every bundle | as recommended |
| HD-5 | Detection threshold | at least one matching node | as recommended |
| HD-6 | Control condition | included; not counted in H5 | as recommended |
| HD-7 | Market and locale | MX, es (as E03); browser locale en-US and UTC, as the E03 web runner | as recommended |
| HD-8 | Pages | Catalog only | as recommended |
| HD-9 | Sample size | N = 50 attempts per condition | as recommended |
| HD-10 | Controlled-instance evidence | E09 environment verification (no reuse of E03's record) | as recommended |
| HD-11 | Incidental violations | excluded (no condition for SUT-02 to SUT-05) | as recommended |
| HD-12 | Scanner loading route | (i): tarball fetched in provisioning, sha512 checked, browser build injected from Python | as recommended |
| HD-13 | Mapping record | none; the configuration must state it | as recommended |
| HD-14 | Run-manifest schema | v2 | as recommended |
| HD-15 | Required Actions | none (`actions` empty) | as recommended |
| HD-16 | Axe-core version | 4.14.0 (latest at retrieval; published 2026-10-05; the age is a human choice) | as recommended |
| HD-17 | Dispatch-procedure prompt | **DEVIATION**: the brief recommends none, but a measured run must carry a non-null `prompt_version` (rule 9 of the agent-instructions file admits null only for a human-executed run). The default used is a frozen prompt id required as input and checked by the gate, as E03 does. The human research lead must decide the prompt file (a frozen dispatch prompt) before START. | **open conflict** |
| HD-18 | Python executor lock | a new E09 lock with the same pins (copied); Python 3.12 series for the executor, the exact version recorded per run | as recommended |
| HD-19 | Recording the SUT01-EV-0019 discrepancy | (i) or (ii) recommended; not performed (blocked, section 3) | **open** |
| HD-20 | Attribution of a non-detection | (i): recorded as a non-detection of the predeclared rule set on the DOM condition; no cause inferred | as recommended |
| HD-E09-A | Password of `a11y_glitch_user` | locked in config.py from the SUT-01 README at the pinned commit (read-only read authorized 2026-11-12); digests re-embedded | **resolved 2026-11-12**; the DRY_RUN environment verification is no longer blocked by it |
| HD-E09-B | Run status for each outcome category | the mapping of executor/README.md section 4 (DETECTED = SUCCESS; NOT_DETECTED = FAILURE; a draw without ground truth = INCONCLUSIVE with its category) | default; the schema has no value for a non-ground-truth draw |
| HD-E09-C | Declared behavior class of the control | null (TBD); the configuration draft proposes "deterministic (to confirm)"; the activation record confirms the account's behavior at run time | open |
| HD-E09-D | Candidate condition ids | the candidate ids of the configuration draft, unchanged | candidate, not frozen |
| HD-E09-E | ARIA-named empty headings | outcome INCONCLUSIVE_ARIA_NAME_PRESENT (the rule cannot fire by its definition; brief section 4.3 asks for a re-decision before lock) | open |
| HD-E09-F | Matching of a node to the predeclared selector | on the node HTML (an h2 whose data-testid starts with pizza-name-), because axe-core targets are generated selectors (brief section 4.5 says "target matches") | deviation in wording, recorded |
| HD-E09-G | `experiment_id` | E09-A11Y-SUT01 (no E03 analog) | default |
| HD-E09-H | `scenario` in the manifest | omitted (the schema types it as a string; no canonical scenario exists) | default |
| HD-E09-I | Attempts | attempt 1 only (governance v6, Section 3.7 admits no further attempt); a further attempt needs its own approval and a mechanism not yet defined | open |
| HD-E09-J | Dispatch authorization record fields | defined in executor/README.md section 11; governance v6 names the content, not the field names | default of this draft |
| HD-E09-K | environment_type | SELF_HOSTED on GitHub-hosted runners (E03 convention) | as recommended |
| HD-E09-L | Probe record | the verified run's imported artifacts, written into the repository as a probe record file before the lock | open |

## 7. Deviations and remaining differences from the briefs and the execution plan

1. **Prompt (HD-17):** see the table; the brief's default conflicts with rule 9 of the agent-instructions file for ORCHESTRATOR-dispatched measured runs.
2. **Governance v6 gate vocabulary:** the gate reads Section 3.7 (heading present, the record's attempt 1, authorization date, issuer, SUT,
   conditions, N, START id, and the two frozen-input SHA-256 values) and refuses while the document is a DRAFT. Governance v6 does not define field
   names; executor/README.md section 11 does (HD-E09-J). The brief's gate 4 cites the v5 document; this draft reads v6, as the human research lead's
   2026-11-05 decision requires.
3. **Gate 5 of the brief (pinned web commit):** the gate reads the SUT-01 web commit from manifests/sut-manifest.yaml and requires the locked
   configuration to name it. The commit is not re-read from the repository of the SUT.
4. **Gate 10 of the brief (classifier validated by probe):** the gate checks the configuration names an existing probe record file; the probe itself
   is not performed (section 2).
5. **Gate 19 of the brief (publication hygiene of the study):** not in the measured gate; the repository's validation workflow and the
   publication procedure carry it. This draft's own files are checked by test_workflows.py (HygieneTests).
6. **Pins:** the tarball integrity string, the browser build sha256, and the version match the pin proposal. The executor checks them twice (in
   provisioning and in the run); the workflow's env pins duplicate the values of executor/executor/scanner.py, and a test requires equality.
7. **Environment record (brief 4.9):** the environment record is written (Chromium build, viewport, locale, time zone, market, runner image).
8. **Control outcome categories:** the brief names detected, not detected, and not applicable for the glitch condition only. The control is given
   CONTROL_RULE_ABSENT and CONTROL_RULE_PRESENT (not counted in H5), and an INCONCLUSIVE category when its DOM is not a non-empty state.
9. **Timing:** the page wait for product headings is bounded by ACTION_TIMEOUT_MS (15 s); the settle is bounded by SETTLE_TIMEOUT_MS (15 s) with a
   500 ms quiet window (E03 values). A DOM without headings is INCONCLUSIVE, not "no ground truth".
10. **Catalog responses:** captured from the page's own requests and read after the settle; the executor never requests `/api/pizzas` itself.
11. **Mobile and other SUTs:** none in this draft (brief section 9 gate 18: no scan for SUT-02 to SUT-06; the workflow's assigned-SUT input admits
    SUT-01 only).
12. **Not in the study's own records yet:** the E09 README status line, the configuration section, the controlled-instance status file, the toolchain
    pin, the dispatch records, and the probe record. All are blocked (section 3).
13. **Campaign execution plan:** the plan includes E09 in the minimum set and adopts the briefs' defaults as the working proposal (used here). It
    does not start or authorize E09, and it leaves the freeze of governance v6 and each START to the human research lead.

## 8. Tests and their limits

`tests/RECORDED-OUTPUT.txt` is the recorded run of the static suite (unittest discovery in tests/, with PyYAML from a pure-Python copy on the path,
actionlint 1.7.7 with shellcheck 0.10.0 when their paths are supplied). What the recorded run proves: the classifier and the outcome mapping on
synthetic fixtures; the tarball checks on synthetic and the real pinned archive; the manifest against the schema subset; the gate on a must-pass
fake tree, on one mutation per gate, and on the as-is repository (fail closed); the entry point's refusals; the embedded digests; the workflow
static rules (no expression in any run script, the OP-CI-15 length estimate, the sparse checkout of one SUT's raw-data, pins equal to the
implementation, publication hygiene). What it does not prove: anything about the browser, axe-core's rule behaviour in a DOM, or the SUT.

## 9. First environment-verification DRY_RUN (2026-11-12, run 43292830947) and the corrections that followed

Dispatched once, by the exact line the human research lead approved (manifests/e09-environment-verification-dispatch-v1.yaml). The verification record passed its seven checks (instance interface, pinned axe-core tarball, health, both logins with the glitch password locked, one Catalog load and one explicit-rule axe run per account). It found two defects of the rehearsal and one limit of the check, none a finding about the SUT:

1. **Record class of the DRY_RUN instance file.** The DRY_RUN step reused instance.json, whose record class is ENVIRONMENT_VERIFICATION, while the executor refuses an instance file whose record class differs from the run's (DRY_RUN). Both DRY_RUN bundles recorded status ERROR and category RUNNER_FAULT. Corrected in the workflow: the step writes instance-dry-run.json with the record class DRY_RUN.
2. **A green step over ERROR bundles.** run-condition.sh exits 0 whenever a manifest was written, an ERROR included (by design, section 1), so the run concluded success. Corrected in the workflow: the step reads every DRY_RUN manifest and fails on status ERROR or ABORTED or category RUNNER_FAULT.
3. **One load cannot show the scanner.** The activation mode is drawn at random per catalog call; the single glitch load of that run drew a mode other than missing_name (DOM state NOT_EMPTY, 0 matching nodes), so the verification could not show empty-heading firing, image-alt not firing on an empty alt, or the default rule set. Corrected in the executor: executor/probe.py loads the Catalog page of the glitch account up to 30 times, one new browser context and one explicit-rule scan per load, until a load renders an ALL_EMPTY draw, and on that load runs the explicit pair (empty-heading, image-alt) and the default rule set; its decisions are pure functions (probe.summarize) tested without a browser (tests/test_probe.py). The probe is part of the environment verification only; it never enters a measured run.

What that run did show: the catalog was requested once per page load in the load that was recorded (31 network entries, one GET of the catalog API); the h2 of the pinned frontend carries no ARIA name (source finding F06 of manifests/source-reads-v1.yaml). The corrected workflow and executor are the canonical files; they run on GitHub Actions only after an export, and a second DRY_RUN needs its own exact-line approval.
