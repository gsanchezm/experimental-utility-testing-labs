# E09-accessibility — Campaign configuration (skeleton)

## 0. DRAFT-1 (2026-11-12): the decisions incorporated, and what is still open

Every decision HD-1 to HD-20 of design-brief-draft.md, section 12, is answered (manifests/campaign-execution-decisions-v4.yaml, -v6.yaml and -v8.yaml; the source reads that closed two verification items are in manifests/source-reads-v1.yaml). The text below keeps the skeleton's wording; where it says HUMAN DECISION, read the value in this table. Still a DRAFT: nothing is locked, started or authorized.

| HD | Decided value |
|---|---|
| HD-1 | one SUT-01 condition, the missing_name stratum, N = 50 attempts, stratified by the realized draw (not adaptive, not three conditions) |
| HD-2 | the H5 count for SUT-01 is 1 |
| HD-3 | predeclared expected rule: empty-heading only; confirmed by the probe of the second DRY_RUN (empty-heading fires on the 12 affected h2; image-alt reports 0 nodes on an empty alt) |
| HD-4 | explicit inclusion of empty-heading in the rule set (`runOnly` rule), recorded as a best-practice, minor-impact rule, so the ground truth is weaker than a WCAG failure; the default rule set also reports it (probe) |
| HD-5 | detected = at least one node of empty-heading matching the predeclared selector |
| HD-6 | include the control condition E09-CTRL-SUT01-STANDARD (not counted in H5) |
| HD-7 | market MX, language es (the E03 values) |
| HD-8 | the catalog page only |
| HD-9 | N = 50 attempts per condition |
| HD-10 | an environment verification of E09's own on GitHub Actions; the controlled-instance decision is per condition only; controlled_instance_available in the SUT manifest stays null |
| HD-11 | incidental violations (such as the missing alt attributes of SUT-03) are excluded |
| HD-12 | scanner loaded from the pinned tarball by URL, sha512 verified, axe.min.js injected from Python; no Node in the executor |
| HD-13 | no mapping record now; decided before any cross-SUT rate comparison |
| HD-14 | run-manifest schema v2 |
| HD-15 | no Required Actions in E09 |
| HD-16 | axe-core 4.14.0 (manifests/campaign-execution-decisions-v4.yaml) |
| HD-17 | REVISED 2026-11-12 (manifests/campaign-execution-decisions-v8.yaml): a frozen dispatch-procedure prompt, ORCHESTRATOR-E09-accessibility-v1 (working copy prompts/working/ORCHESTRATOR-E09-accessibility-v1.md), frozen at START; the earlier outcome (no prompt) was a recommendation made in error |
| HD-18 | an E09 implementation lock of its own (the digests in run-condition.sh), same pins, leaving the E03 lock untouched |
| HD-19 | an entry in protocol/unresolved.md (PROTO-U22); no E01 record edited |
| HD-20 | a non-detection is recorded as a non-detection of the predeclared rule set on the DOM condition confirmed at scan time, no cause inferred |

Open before the START package (nothing here is a decision of this draft):
1. A third environment-verification DRY_RUN on the bytes that the START will lock (decided 2026-11-12, manifests/campaign-execution-decisions-v8.yaml): export v56 publishes the corrected classifier first. The controlled-instance status record experiments/E09-accessibility/controlled-instance-status.yaml (read by gate G-5 of the measured workflow) is written from that run.
2. The START itself: the lock of this record, the implementation hash (sha256 of experiments/E09-accessibility/executor/run-condition.sh), the freeze of the dispatch prompt, the order of conditions and executions and the location of the dispatch record, and the dispatch authorization of SUT-01 (one authorization, 100 executions: 50 of each condition, attempt 1). Each needs the human research lead's explicit approval.
3. The toolchain entry for axe-core 4.14.0 in manifests/toolchain-manifest.yaml (written 2026-11-12 on the decision HD-16) must equal the pins of the executor at START; the measured workflow checks it.

**DRAFT skeleton. Not locked.** The "Campaign configuration" is locked only at campaign START under explicit human authorization (protocol/change-control-v1.md, section 7). Every unknown is marked HUMAN DECISION; the options are in design-brief-draft.md, section 12 (HD-1 to HD-20). Candidate condition ids are not frozen. Nothing here starts, authorizes, or dispatches anything.

Order follows experiments/README.md, "Common rules for all campaigns".

## 1. Run manifest and environment_type

- Run manifest per condition × page execution (experiments/E09-accessibility/README.md, Required evidence).
- Schema: schemas/run-manifest.schema.v2.json (HUMAN DECISION HD-14; recommended). Schema sha256 recorded at START.
- environment_type: SELF_HOSTED for every E09 condition, on a GitHub-hosted runner the study provisions (experiments/E03-resetability/ci-cd-execution-model.md, section 6). LOCAL is permitted only for DEVELOPMENT, SYNTAX_VALIDATION, TOOL_QUALIFICATION, SMOKE, ENVIRONMENT_VERIFICATION, or DRY_RUN classes.

## 2. Environment control

- Fault activation (the SUT-01 condition): controlled instance only; never a PUBLIC_HOSTED instance (protocol/study-design-v1.md, section 10.3).
- Controlled-instance verification on GitHub Actions for the SUT-01 condition: **NOT YET** (environment verification required). HUMAN DECISION HD-10.
- sut-manifest `controlled_instance_available` for SUT-01: stays null (section 10.5). The per-condition decision is recorded below.

| Condition | Controlled instance | Verification status |
|---|---|---|
| E09-A11Y-SUT01-MISSING-NAME | required (fault activation) | not yet verified for E09 (HD-10) |
| E09-CTRL-SUT01-STANDARD | required (same instance, same page) | not yet verified for E09 |

## 3. Campaign configuration items

### 3a. Scenario mapping records

None required by the recommended design. HUMAN DECISION HD-13 applies if any pairwise detection comparison is configured.

### 3b. Pinned SUT versions (web surfaces)

Copied from manifests/sut-manifest.yaml. Re-check against it at START.

| SUT | Surface | Repository | Commit | Release | Configured condition |
|---|---|---|---|---|---|
| SUT-01 | web | https://github.com/gsanchezm/OmniPizza | 9ca37674d374e9303912e259641ee86baf3aabe1 | none | yes (two conditions) |
| SUT-02 | web | https://github.com/saucelabs/sample-app-web | 60fdd634bb111c092282fa07977513a0a7765593 | none | no |
| SUT-03 | web | https://github.com/browserstack/browserstack-demo-app | 7ab934d733f2f74d4b912e94e86f59ae0f6b7609 | none | no |
| SUT-04 | web | https://github.com/mwinteringham/restful-booker-platform | d36bd3f8647a091d406e53bad463c5e3e5d2ece1 | 2.2 | no |
| SUT-05 | web | https://github.com/juice-shop/juice-shop | 1618a611b173b4bf114028e6e02549950606e29d | v20.2.0 | no |
| SUT-06 | none (no web surface) | — | — | — | structural, no condition |

SUT-02 to SUT-05 are listed for completeness only. No scan is configured for them unless a condition is later found (HUMAN DECISION HD-8 and section 5 of the brief).

### 3c. Toolchain versions

- Web runner: Playwright for Python **1.63.0** (manifests/toolchain-manifest.yaml, `tools.web_runner`). Hashed requirements: reuse of experiments/E03-resetability/executor/requirements.txt under its own lock, or a new E09 lock (HUMAN DECISION HD-18).
- Browser: the Chromium build named by Playwright 1.63.0, not hash-pinned by the study; observed version recorded per run.
- Accessibility scanner: **axe-core 4.14.0, PROPOSED** (axe-core-pin-proposal-draft.md). npm integrity `sha512-9WTZxEjsZ7b13TH8JPmbV2z8CHbl80/2hm3XPEG4JgNdQLK81IBRXmSxHfMAOkSqQeRxT/0dwNDz2GOm3zzpcQ==`; browser build `axe.min.js`, sha256 `20c09fe157a8a34a30e241aaa1fcdade657734f08ab379ecfbeb7d45cc46e878`. Version and route: HUMAN DECISION HD-12 and HD-16.
- Python runtime: the runner's python3 series, exact version recorded per run; pin not stated for E09 (HUMAN DECISION HD-18).
- Node.js: not required under the recommended loading route; required under the alternative (HD-12).
- Runner image: ubuntu-24.04 GitHub-hosted runner; image version recorded per run.

### 3d. Prompt versions

No agent prompt is recommended. HUMAN DECISION HD-17: whether the dispatch procedure needs a frozen prompt (E03 has one: `ORCHESTRATOR-E03-resetability-v1`).

### 3e. Conditions and environment types

| Condition id (candidate, not frozen) | SUT | Page | Activation | Declared behavior class | environment_type | Expected rule | Ground-truth instance | Sample size |
|---|---|---|---|---|---|---|---|---|
| E09-A11Y-SUT01-MISSING-NAME | SUT-01 | Catalog, route `/catalog` (SUT01-EV-0001) | Documented account `a11y_glitch_user` (SUT01-EV-0017); server draws the mode per call (SUT01-EV-0018) | stochastic | SELF_HOSTED | `empty-heading` (HD-3, HD-4) | DOM at scan time: every affected `h2` empty (catalog response body corroborates) | 50 attempts (HD-9) |
| E09-CTRL-SUT01-STANDARD | SUT-01 | Same as above | Default account `standard_user` (experiments/E03-resetability/executor/README.md, section 4.1) | deterministic (to confirm, brief section 13 item 3) | SELF_HOSTED | none (rule absent) | not applicable (control) | 50 attempts |

- Not conditions: the `wrong_lang` and `extreme_text` draws of the first condition are recorded as "no ground-truth instance" (HD-1 option (a)).
- Viewport 1280 x 800 and market `MX` with language `es`, the values of the E03 SUT-01 realization (HD-7).
- SUT-02 to SUT-05: no condition; H5 count 0; detection rate "no data — no ground-truth condition available".
- SUT-06: structural; no condition; "no data — modality rated Score 0 in E01 (NO_WEB_SURFACE)".

### 3f. Sample size

- N = 50 attempts per condition (protocol/repeatability-determinism-v1.md, section 3). The reduced N = 30 does not apply (Web only).
- Attempt numbering, first attempt only, one dispatch per execution, no retry (E03 convention). HUMAN DECISION HD-9 if N differs.
- Ground-truth draw counts are derived after the run, not configured.

### 3g. Exclusion and attribution rules

- Ground-truth instance: at scan time, every affected `h2[data-testid^="pizza-name-"]` has empty text (HD-1 (a)); the catalog response body is recorded as corroboration. The classifier is validated by probe before lock (brief section 13 item 1).
- Denominator (fixed before any data): the detection rate is detections divided by the count of ground-truth instances among the N = 50 executions of the condition. Other draws are reported beside it and are never added to the denominator.
- Non-detection attribution (predeclared, HD-20): a non-detection is recorded as a non-detection of the predeclared rule set on the predeclared DOM condition; no cause is inferred from the data.
- Detection: at least one node of rule `empty-heading` whose target matches the predeclared selector (HD-5).
- Scanner failure or page failure: classified INCONCLUSIVE or ERROR; excluded from the detection denominator by this rule; reported beside the results.
- ABORTED: a run that stops before the scan; reported.
- No run excluded after the fact. Total violation count is descriptive only.
- Attribution rule: none introduced. A missed detection is not attributed to the scanner without a recorded probe.

### 3h. CONFIRMATORY comparisons

- **H5** (protocol/statistical-analysis-plan-v1.md, section 4.3): SUT-01 vs SUT-02 and SUT-01 vs SUT-03. Variable: number of controlled non-functional ground-truth conditions per ecosystem (descriptive count). Detection rates per condition reported per SAP section 5. Classification: CONFIRMATORY (H5) (SAP section 4.2).
- No pre-registered additional confirmatory comparison (a specialist positive-control entry would need its own decision).
- With SUT-02 and SUT-03 at zero conditions, no pairwise detection comparison exists, so no Fisher table and no risk difference is formed.

## 4. Scenario equivalence

Not required by the recommended design. SAP section 4.1 requires equivalent conditions for any between-ecosystem comparison; HD-13 applies before any cross-SUT rate comparison.

## 5. Comparison classification

Per protocol/statistical-analysis-plan-v1.md, section 4.2: H5 is CONFIRMATORY (H5); every other comparison is EXPLORATORY. Point estimate, interval, and N are reported per arm where applicable.

## 6. Setup effort

- Required Actions in the run manifest: not recorded by default (optional for E09 under the schema; HUMAN DECISION HD-15).
- One provisioning record per SUT-01 controlled instance, descriptive (protocol/setup-effort-v2.md; experiments/README.md, "Common rules", setup effort).

## 7. Raw and derived data

- Raw (MEASURED only, after ORCHESTRATOR import with digest verification): `raw-data/E09-accessibility/SUT-01/<run-id>/`.
- Per-run artifacts: scanner JSON (`passes`, `violations`, `incomplete`, `inapplicable`); DOM snapshot at scan time; catalog response body; activation record (account and realized draw); environment record (runner image, Chromium version, viewport, locale). Screenshot optional (HUMAN DECISION, minor).
- Derived: a table of detections per condition with the realized draw counts, produced by a named script with a version (derived-data/README.md; analysis/README.md). Name and location: to be set at START.
- SUT-02 to SUT-06: no raw data (no measured run). Their "no data" cells appear in the derived table with the reason.

## 8. Identical rules for all ecosystems

The same rules apply to every SUT. A scan is configured for a SUT only if a condition exists for it. For SUT-02 to SUT-05 the cell is "no data" with the evidence reason; for SUT-06 the cell is structural. No cell is dropped (experiments/README.md, "Common rules").

## 9. Repetition targets

N = 50 per repeatable condition (protocol/repeatability-determinism-v1.md, section 3). The reduced target applies only to Android and iOS modalities.

## 10. Analysis

- protocol/statistical-analysis-plan-v1.md: section 3 (Wilson interval for each detection rate), section 4.3 (H5 mapping), section 5 (reporting: "no data" with reason; no detection rate of zero).
- No test on the count comparison beyond description. No bootstrap (SAP section 3 applies the bootstrap to durations only).
- Software versions used for analysis recorded at analysis time (SAP section 3).

## 11. Tooling

Tool entries are written into manifests/toolchain-manifest.yaml by the ORCHESTRATOR only after explicit human approval (section 3c; `tools.accessibility` is null until then).

## 12. Execution substrate

- GitHub Actions only, under ORCHESTRATOR coordination (CAMPAIGN-CI-WRITE-AUTH-01, recorded in the agent-instructions file).
- Proposed workflow names, not created: `e09-environment-verification.yml` (non-measured) and `e09-measured-execution.yml` (measured). Gate names are in brief section 9.
- Each measured dispatch needs its own explicit human approval, is recorded before it runs, is never re-run, and is first attempt only, on the default branch only.
- Repository must be public for GitHub Actions to read the workflow (agent-instructions file, E03-CI-WRITE-AUTH-01).

## 13. Evidence classification

- E01 evidence used for the mechanism: SUT01-EV-0017 (DOCUMENTED), SUT01-EV-0018 and SUT01-EV-0019 (SOURCE_VERIFIED); negative records SUT02-EV-0014, SUT03-EV-0020, SUT04-EV-0019, SUT05-EV-0018 and SUT05-EV-0019; structural SUT06-EV-0023.
- E09 measured outcomes are campaign observations under raw-data/. Any evidence record they produce follows protocol/evidence-rules-v1.md.
- The expected rule is a pre-registered expectation, not evidence of detection, until the measured run.

## Human decisions referenced in this skeleton

HD-1 to HD-20 are defined in design-brief-draft.md, section 12. In brief terms:
- **HD-17.** Dispatch-procedure prompt: none, or a frozen prompt (3d).
- **HD-18.** Lock for the Python executor: reuse the E03 hashed requirements under their lock, or a new E09 lock; and the Python 3 series pin (3c).
- **HD-19.** Where the discrepancy with SUT01-EV-0019 (the `image-alt` half cannot occur; frozen E01 evidence) is recorded: an unresolved entry (recommended), a change-control correction record (recommended alternative), or the configuration only. No E01 record is edited.
- **HD-20.** Attribution of a non-detection: predeclared as a rule-set outcome on the DOM condition (recommended), or with a predeclared DOM assertion beside the scanner.
