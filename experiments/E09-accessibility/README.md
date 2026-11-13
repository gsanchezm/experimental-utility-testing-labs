# E09 — Accessibility

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) provides a known accessibility violation that can be activated as a ground-truth condition, and whether an accessibility scanner run against the affected page or state detects it. Per the frozen modality list, the Accessibility modality is Web only; this campaign does not scan native mobile surfaces. Detection is judged against the known violation, not against the scanner's total finding count. The outcome "no ground-truth condition available" is recorded as a categorical finding about Experimental Breadth / Experimental Controllability and is reported as "no data" with that reason in the RQ5 detection-rate comparison; it is never a detection failure and never a detection rate of zero (protocol/statistical-analysis-plan-v1.md, section 5). Activating a known violation is a fault activation and is performed only on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance; a documented always-on violation may be scanned on any environment type, with the environment recorded (protocol/study-design-v1.md, section 10.3).

## Related research question(s)

- RQ5 Controlled Non-functional Experimentation (primary).
- Informs dimensions 1 Experimental Breadth and 2 Experimental Controllability.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Known violation condition (from a catalogue built during E01 with provenance; TBD before freeze) — candidate.
- Page / state under scan — candidate.

## Future dependent variables (candidate — not frozen)

- Detection outcome (categorical: detected / not detected / no ground-truth condition available) — candidate.
- Ground-truth availability (categorical: whether a documented, activatable known violation exists) — candidate.

## Required evidence

- Condition activation record showing how the known violation was enabled, with provenance of the mechanism.
- One run manifest per condition × page execution conforming to schemas/run-manifest.schema.json, carrying `environment_type`.
- Scanner output (raw, machine-readable where the tool provides it).
- DOM snapshot of the scanned page or state at scan time.
- Accessibility scanner candidate per manifests/toolchain-manifest.yaml; tool and version used must be recorded in the run manifest.
- Raw observations in `raw-data/E09-accessibility/`.

## Current status

IN PROGRESS since the campaign START of 2026-11-12 (human authorization E09-START-AUTH-01; record manifests/e09-campaign-start-v1.yaml). The "Campaign configuration" section below is locked. The START authorized no dispatch and no dispatch authorization.

Resumed by the human research lead's decision of 2026-11-02 (manifests/campaign-resumption-v1.yaml); the deferral of scope A (manifests/campaign-disposition-v1.yaml) no longer governs the schedule: the status above is unchanged, preparation may begin, and the campaign START needs its own explicit human authorization (protocol/change-control-v1.md, section 7).

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.

## Campaign configuration

This record is the "Campaign configuration" of E09-accessibility. It is locked at the campaign START (protocol/change-control-v1.md, section 7, moment 1) under the human authorization named below, and is immutable from then on; a change after the START is a change-control row recorded before the affected execution. It authorizes no dispatch: each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) is issued separately by the human research lead. The decisions HD-1 to HD-20 of experiments/E09-accessibility/design-brief-draft.md, section 12, are recorded in manifests/campaign-execution-decisions-v4.yaml, -v6.yaml and -v8.yaml. A system under test (SUT) is one of the evaluated ecosystems of README.md.

### Identity and START

- Campaign: E09-accessibility. Hypothesis label: H5 (protocol/statistical-analysis-plan-v1.md, section 4.3), a descriptive count comparison; no support or non-support criterion is frozen for H5 and none is invented.
- START authorization id: E09-START-AUTH-01 (the human research lead's explicit approval of the START; the change-log row of protocol/CHANGELOG.md names it).
- Protocol: v1 FROZEN-PRE-DATA (protocol/study-design-v1.md; protocol/repeatability-determinism-v1.md; protocol/statistical-analysis-plan-v1.md; protocol/capability-rubric-v1.md). Agent governance: protocol/agent-governance-v6.md, FROZEN-PRE-DATA since 2026-11-06 (Sections 3.6 and 3.7).
- Execution: GitHub Actions only (CAMPAIGN-CI-WRITE-AUTH-01), through .github/workflows/e09-measured-execution.yml, by the ORCHESTRATOR under dispatch authorizations; first attempt only, default branch only, no re-run.

### Scenario mapping (HD-13)

No canonical scenario and no mapping record is used: there is no between-ecosystem comparison of detection rates (SUT-02 to SUT-06 have no condition). HD-13: the decision whether a FROZEN mapping record is needed is taken before any cross-SUT rate comparison, which this configuration does not make.

### Pinned versions

- SUT-01 web and api: https://github.com/gsanchezm/OmniPizza at commit 9ca37674d374e9303912e259641ee86baf3aabe1 (manifests/sut-manifest.yaml; no release). SUT-02 to SUT-05 web: listed in that manifest, no condition configured. SUT-06: no web surface.
- Run-manifest schema: schemas/run-manifest.schema.v2.json, sha256 9a86cf37c4ccd2abe3368866309e18a9f9554a2330f5dceeacda6d02a2932757 (HD-14).
- Web runner: Playwright for Python 1.63.0 with the hashed requirements of experiments/E09-accessibility/executor/requirements.txt (an E09 lock of its own, HD-18). Browser: the Chromium build named by Playwright 1.63.0, not hash-pinned by the study; the observed version is recorded per run (153.0.8010.12 in the verification runs).
- Accessibility scanner: axe-core 4.14.0 (HD-16), npm integrity sha512-9WTZxEjsZ7b13TH8JPmbV2z8CHbl80/2hm3XPEG4JgNdQLK81IBRXmSxHfMAOkSqQeRxT/0dwNDz2GOm3zzpcQ==; browser build package/axe.min.js, sha256 20c09fe157a8a34a30e241aaa1fcdade657734f08ab379ecfbeb7d45cc46e878; loaded from the tarball by URL with the sha512 verified before use (HD-12); the toolchain entry is manifests/toolchain-manifest.yaml, tools.accessibility.
- Python runtime of the executor: the 3.12 series on the runner (3.12.16 in the verification runs), recorded per run. Runner image: ubuntu-24.04, version recorded per run. Viewport 1280 x 800, market MX, language es (HD-7).

### Prompt version and implementation

- Dispatch procedure prompt (HD-17, revised): ORCHESTRATOR-E09-accessibility-v1, frozen at the START as prompts/frozen/ORCHESTRATOR-E09-accessibility-v1.md, a byte-identical copy of prompts/working/ORCHESTRATOR-E09-accessibility-v1.md, sha256 1734cf977102e0f22c721a1ad1ffdfdebfa62fef76e0e9964eca686e8070a2f0.
- Implementation hash (sha256 of experiments/E09-accessibility/executor/run-condition.sh, which embeds the digests of the executor files and refuses an unlisted one): 9eeb2a1c1a7b35ac8fceb016897d317d5534f09777a03f315e4e132dd3b11156. This is the implementation that ran complete on GitHub Actions in the third environment-verification run.
- agent_role in run manifests: ORCHESTRATOR.

### Conditions

| Condition | SUT | Page | Activation | Declared behavior class | environment_type | Expected | Ground-truth instance | N |
|---|---|---|---|---|---|---|---|---|
| E09-A11Y-SUT01-MISSING-NAME | SUT-01 | Catalog, /catalog | documented account a11y_glitch_user; the server draws the mode per call | stochastic | SELF_HOSTED | rule empty-heading reports at least one node of an h2 whose data-testid starts with pizza-name- | DOM at scan time: every such h2 empty (the catalog response body corroborates) | N = 50 |
| E09-CTRL-SUT01-STANDARD | SUT-01 | same | default account standard_user | not declared (null in the manifest; the control is not a determinism condition; its login behavior is standard in every verification run) | SELF_HOSTED | rule empty-heading reports no node of a product heading | not applicable (control) | N = 50 |

- The behavior class of each condition is the one in the table; the glitch condition is stochastic by the mechanism (the mode is drawn at random per call, SUT01-EV-0018).
- The wrong_lang and extreme_text draws of the first condition are recorded as no ground-truth instance (HD-1, option (a)); they are not conditions. SUT-02 to SUT-05: no condition, H5 count 0, detection rate "no data: no ground-truth condition available"; SUT-06: structural, "no data: modality rated Score 0 in E01 (NO_WEB_SURFACE)".
- Rule set (HD-3, HD-4): the explicit rule empty-heading only, a best-practice, minor-impact rule, so the ground truth is weaker than a WCAG failure; image-alt is not predeclared (it cannot fire on an empty alt attribute in the pinned axe-core; PROTO-U22). Scope: runOnly rule empty-heading, recorded verbatim in every bundle.
- Detection (HD-5): at least one node of empty-heading whose HTML opens an h2 whose data-testid starts with pizza-name- (the -desktop suffix matches). Non-detection (HD-20): recorded as a non-detection of the predeclared rule set on the DOM condition confirmed at scan time; no cause is inferred.
- Environment control (HD-10): fault activation runs only on a controlled instance that the job provisions from the pinned commit on a GitHub-hosted runner (SELF_HOSTED), never against a PUBLIC_HOSTED instance. The per-condition decision is recorded in experiments/E09-accessibility/controlled-instance-status.yaml (both conditions CONTROLLED and VERIFIED); controlled_instance_available in the SUT manifest stays null.
- Probe record: manifests/e09-environment-verification-run-v3.yaml (the verification of the realized-draw classifier, the selector with the -desktop suffix, the behavior of empty-heading and image-alt and of the default rule set, and the single catalog request per load; brief section 13, item 1).

### Sample size, order and dispatch record

- N = 50 attempts per condition (protocol/repeatability-determinism-v1.md, section 3; HD-9); 100 executions in all; execution ids EX0001 to EX0050 within each condition; attempt 1 only. Seed: null (no seed control recorded).
- Order of dispatch (fixed here, before the first dispatch): for n = 1 to 50, execution EXnnnn of E09-A11Y-SUT01-MISSING-NAME and then EXnnnn of E09-CTRL-SUT01-STANDARD; each run is completed, its bundle verified against its GitHub digest and read, before the next dispatch (the concurrency group is per condition, without cancellation).
- Dispatch record (append-only, committed before each dispatch): manifests/e09-measured-dispatch/e09-sut01.jsonl; the run identity is appended after each dispatch. Import: byte-exact under raw-data/E09-accessibility/SUT-01/ after the verification of every archive against its GitHub digest.

### Exclusion and attribution rules

- Denominator (fixed before any data): the detection rate is the detections divided by the count of ground-truth instances (draws classified ALL_EMPTY) among the N = 50 executions of the glitch condition; the other draws are reported beside it and never enter the denominator. The count of ground-truth instances is a result, not a configuration.
- Scanner failure or page failure: INCONCLUSIVE or ERROR, excluded from the detection denominator by this rule and reported; ABORTED: a run that stops before the scan, reported. No execution is excluded after the fact. The total violation count is descriptive only.
- Attribution: none introduced. A non-detection is not attributed to the scanner or to the SUT without a recorded probe.

### CONFIRMATORY comparisons

- H5 (protocol/statistical-analysis-plan-v1.md, section 4.3): SUT-01 versus SUT-02 and SUT-01 versus SUT-03, on the number of controlled non-functional ground-truth conditions per ecosystem; the HD-2 count unit for SUT-01 is 1. Classification: CONFIRMATORY (H5), descriptive. With SUT-02 and SUT-03 at zero conditions, no pairwise detection comparison exists and no Fisher table or risk difference is formed. Every other comparison is EXPLORATORY.
- Detection rates per condition are reported with a Wilson interval (statistical-analysis-plan-v1.md, section 3) and "no data" with its reason where no condition exists.

### Setup effort, data and analysis

- No Required Actions are recorded (HD-15). One provisioning record per controlled instance, descriptive (protocol/setup-effort-v2.md).
- Raw data: raw-data/E09-accessibility/SUT-01/<run-id>/ only, after import. Per run: scanner JSON (passes, violations, incomplete, inapplicable), DOM snapshot at scan time, catalog response body, activation record (account and realized draw), environment record (runner image, Chromium build, viewport, locale), screenshot. Derived: a table of detections per condition with the realized draw counts, from a named script with a version (derived-data/README.md; analysis/README.md), written after the data freeze; its name is set when it is written.

### Gates the measured workflow enforces

START recorded with its authorization id; this record present; the schema and the prompt and implementation hashes as above; the dispatch authorization of SUT-01 (ISSUED, VALID, issued by the human research lead, naming both conditions, N = 50, attempt 1 and the two SHA-256 values); governance v6 frozen; the controlled-instance status VERIFIED for the condition; the toolchain entries equal to the pins; the activation password of the condition's account locked in the implementation; first attempt only; default branch only.

### Change log

- None. Any change after the START is recorded as a change-control row (protocol/change-control-v1.md) before the affected execution, and results collected before the change are analyzed under the earlier configuration.
