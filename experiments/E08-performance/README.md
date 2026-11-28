# E08 — Performance

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) offers a known, reproducible ground-truth degraded-performance condition, and whether performance measurement under that condition detects the expected degradation relative to a baseline condition. The campaign assesses the controllability of the degraded condition as much as the measurement itself; an ecosystem without a controllable ground-truth condition is recorded as such rather than measured on an uncontrolled basis. The outcome "no ground-truth condition available" is recorded as a categorical finding about Experimental Breadth / Experimental Controllability and is reported as "no data" with that reason in the RQ5 detection-rate comparison; it is never a detection failure and never a detection rate of zero (protocol/statistical-analysis-plan-v1.md, section 5). Significant load and intentional degradation are applied only to a controlled instance (SELF_HOSTED or LOCAL for the service components under load; protocol/study-design-v1.md, section 10.1) when an open-source deployment of the evaluated version is available and never to a PUBLIC_HOSTED instance; otherwise the condition is NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE (protocol/study-design-v1.md, section 10.3).

## Related research question(s)

- RQ5 Controlled Non-functional Experimentation (primary).
- Informs dimensions 1 Experimental Breadth and 2 Experimental Controllability.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Condition (baseline vs known degraded) — candidate.
- Load profile (profiles TBD before freeze) — candidate.

## Future dependent variables (candidate — not frozen)

- Expected degradation detected (categorical: detected / not detected / no ground-truth condition available) — candidate.
- Measured deltas between baseline and degraded conditions (descriptive only) — candidate.
- Controllability of the degraded condition (categorical, criteria TBD before freeze) — candidate.

## Required evidence

- Condition activation record showing how the degraded condition was enabled and disabled, with provenance of the mechanism.
- One run manifest per condition × load profile execution conforming to schemas/run-manifest.schema.json, carrying `environment_type`.
- Measurement artifacts from the performance tool (raw output, not summaries only).
- Baseline measurement artifacts captured under the same load profile.
- Performance tool is TBD; see manifests/toolchain-manifest.yaml (performance candidate: TBD between appropriate open-source tools). The tool and version used must be recorded in the run manifest.
- Raw observations in `raw-data/E08-performance/`.

## Current status

FROZEN since the campaign freeze of 2026-11-27 (human authorization E08-FREEZE-AUTH-01; protocol/change-control-v1.md, section 7, moment 2; record manifests/e08-campaign-freeze-v1.yaml), after IN PROGRESS from the campaign START of 2026-11-26 (E08-START-AUTH-01; record manifests/e08-campaign-start-v1.yaml). The "Campaign configuration" section below is locked and immutable. The 200 executions (four web conditions on SUT-01 (1), SUT-02 (1) and SUT-03 (2), N = 50 each, all attempt 1) were imported unchanged under raw-data/E08-performance/ on 2026-11-27 UTC within the three dispatch authorizations E08-DISPATCH-SUT01-AUTH-01, E08-DISPATCH-SUT02-AUTH-01 and E08-DISPATCH-SUT03-AUTH-01 (manifests/e08-dispatch-authorization-sut0N-v1.yaml; dispatch records manifests/e08-measured-dispatch/e08-sut0N.jsonl); raw-data/E08-performance/ is append-only. The raw data were published by export v93 (public main 5cd808a4, pushed 2026-11-28T03:28:02Z UTC). The E08 contribution to H5 was analyzed descriptively on 2026-11-27 on the instruction of the human research lead (analysis/h5-analysis/compute-h5-e08.js; derived-data/h5-analysis/H5-e08-result.json and derived-data/E08-performance/outcomes-per-attempt.csv, each with a provenance sidecar): the H5 count of the E08 contribution is 1 for SUT-01, 1 for SUT-02 and 2 for SUT-03 (SUT-04, SUT-05 and SUT-06: no data, no ground-truth condition available); the recorded category was DETECTED in 50 of 50 executions in each of E08-SUT01-WEB-DELAY, E08-SUT02-WEB-BLOCK and E08-SUT03-WEB-LCP and NOT_DETECTED in 50 of 50 in E08-SUT03-WEB-CLS (a valid outcome: its expectation is not changed and no cause is inferred), and the baseline-against-baseline false-positive record was true in 0 of 50 executions of each of the four conditions; descriptive, with no test, no pooled rate and no verdict (no support criterion is frozen for H5). The performance tool is pinned in manifests/toolchain-manifest.yaml, `tools.performance` (Playwright for Python 1.63.0, probe version e08-probe-v1); the candidate wording of the sections above ("candidate — not frozen", "Performance tool is TBD") is superseded by the locked configuration below.

Resumed by the human research lead's decision of 2026-11-02 (manifests/campaign-resumption-v1.yaml); the deferral of scope A (manifests/campaign-disposition-v1.yaml) no longer governs the schedule. Preparation record: manifests/campaign-execution-decisions-v19.yaml, -v23.yaml and -v24.yaml; environment verification: manifests/e08-environment-verification-rounds-v1.yaml (round 1).

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.

## Campaign configuration

This record is the "Campaign configuration" of E08-performance. It is locked at the campaign START (protocol/change-control-v1.md, section 7, moment 1) under the human authorization named below, and is immutable from then on; a change after the START is a change-control row recorded before the affected execution. It authorizes no dispatch: each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) is issued separately by the human research lead. The decisions E08-D-1 to E08-D-19 of experiments/E08-performance/design-brief-draft.md and campaign-configuration-draft.md are recorded in manifests/campaign-execution-decisions-v19.yaml (the earlier acceptance of E08-D-1 to E08-D-7, whose exact text is not reproduced), manifests/campaign-execution-decisions-v23.yaml (E08-D-1 to E08-D-19, with the exact text of the answer) and manifests/campaign-execution-decisions-v24.yaml (E08-D-13, the time budgets, answered in the dialog of the START). A system under test (SUT) is one of the evaluated ecosystems of README.md.

### Identity and START

- Campaign: E08-performance. Hypothesis label: H5 (protocol/statistical-analysis-plan-v1.md, sections 4.2, 4.3 and 5), a descriptive count comparison of controlled non-functional ground-truth conditions per ecosystem, SUT-01 against SUT-02 and SUT-01 against SUT-03; the count of E08 is SUT-01 1, SUT-02 1, SUT-03 2, each configured ground-truth condition counting once whatever its detection result (E08-D-2); SUT-04, SUT-05 and SUT-06 are reported as "no data, no ground-truth condition available"; no support or non-support criterion is frozen for H5 and none is invented. The E08 contribution is one dataset beside those of E09 and E11; the datasets are never summed.
- START authorization id: E08-START-AUTH-01 (the human research lead's explicit approval of the START; the change-log row of protocol/CHANGELOG.md names it).
- Protocol: v1 FROZEN-PRE-DATA. Agent governance: protocol/agent-governance-v6.md, FROZEN-PRE-DATA since 2026-11-06 (Sections 3.6 and 3.7).
- Execution: GitHub Actions only (CAMPAIGN-CI-WRITE-AUTH-01), through .github/workflows/e08-measured-execution.yml, by the ORCHESTRATOR under dispatch authorizations; first attempt only, default branch only, no re-run; one dispatch per condition (the 50 executions of a condition run in one job, one after the other, on one shared instance); the dispatch record of each SUT is manifests/e08-measured-dispatch/e08-sut0N.jsonl, written before each dispatch.
- Scenario mapping: none. E08 compares per ecosystem (design brief, section 7; E08-D-10); there is no canonical scenario and no mapping record.

### Pinned versions

- SUT-01 web and api: https://github.com/gsanchezm/OmniPizza at commit 9ca37674d374e9303912e259641ee86baf3aabe1 (manifests/sut-manifest.yaml; no release).
- SUT-02 web: https://github.com/saucelabs/sample-app-web at commit 60fdd634bb111c092282fa07977513a0a7765593 (manifests/sut-manifest.yaml; no release), built and served by vite preview.
- SUT-03 web: https://github.com/browserstack/browserstack-demo-app at commit 7ab934d733f2f74d4b912e94e86f59ae0f6b7609 (manifests/sut-manifest.yaml; no release), Node.js 14, next start.
- SUT-04, SUT-05 and SUT-06: no condition (E08-D-1; SUT-04 has no controlled-degradation condition, SUT04-EV-0017).
- Run-manifest schema: schemas/run-manifest.schema.v2.json, sha256 9a86cf37c4ccd2abe3368866309e18a9f9554a2330f5dceeacda6d02a2932757 (E08-D-11).
- Instrument: Playwright for Python 1.63.0 (hashed requirements of the executor; the pin of tools.web_runner) with the Chromium build that this version installs (not hash-pinned by the study; the version is recorded in every run, and 153.0.8010.12 was observed in the first environment-verification round), and the PerformanceObserver script of the executor, probe version e08-probe-v1; the entry is tools.performance of manifests/toolchain-manifest.yaml (E08-D-11), and gate G-10 of the measured workflow requires it to agree with the executor.
- Python runtime of the executor: the runner's python3 (3.12 series on ubuntu-24.04), recorded per run. Runner image: ubuntu-24.04, version recorded per run.
- External dependency: the delayed image of the E08-SUT03-WEB-LCP condition comes from the host picsum.photos, outside the evaluated version (SUT03-EV-0013); each execution records whether and when the image answered.

### Prompt version and implementation

- Dispatch procedure prompt: ORCHESTRATOR-E08-performance-v1, frozen at the START as prompts/frozen/ORCHESTRATOR-E08-performance-v1.md, a byte-identical copy of prompts/working/ORCHESTRATOR-E08-performance-v1.md, sha256 eaa751fc75a160f7fec89d4dbf5775f894ce99bc4f057b19c6190c792213a044 (E08-D-16).
- Implementation hash (sha256 of experiments/E08-performance/executor/run-condition.sh, which embeds the digests of the executor files and refuses an unlisted one): da24b1326d8ef55711fe077ac7363efccbf4c9d0277e6943e19649b9b1d7e4b2. This is the implementation that ran complete on GitHub Actions in the first environment-verification round (run 45878792738; manifests/e08-environment-verification-rounds-v1.yaml).
- Measured workflow: .github/workflows/e08-measured-execution.yml, sha256 32696fafa7e9a9b85bd907aa6b8379721671bc3b9ead082a8eabddef687a546a. Verification workflow: .github/workflows/e08-environment-verification.yml, sha256 7ee76a1bac36f9a4c2656a83158e7ce821a723f325382bdda36f2684759ddf9a.
- Conditions file: experiments/E08-performance/conditions-draft.json, sha256 e4aaf35651d3b8e0d1abd6c29b9716b733756f2af0332ef90713ccc75b499a98.
- agent_role in run manifests: ORCHESTRATOR.
- Time budgets (E08-D-13): executor watchdog 420 s per execution; measured-execution job 120 minutes; gate and provenance jobs 10 minutes; no step retry; no automatic re-run. The first environment-verification round observed about 7 s (SUT-01), 14 s (SUT-02) and 25 s (SUT-03) per execution, far below these budgets; they are ceilings, not measured parameters. The comments "to be set from the timing of a DRY_RUN before the START" at executor/executor/common.py (line 36) are superseded by this paragraph.

### Conditions (four; N = 50 each; 200 executions; attempt 1)

| Condition | SUT | Degraded load D | Paired baseline load | Metric | Expected effect | Threshold | Behavior class | N |
|---|---|---|---|---|---|---|---|---|
| E08-SUT01-WEB-DELAY | SUT-01 | `performance_glitch_user`, `/catalog` | `standard_user`, `/catalog` | first_item_ms | 3000 ms (SUT01-EV-0015) | D minus Ba of at least 2500 ms | deterministic | N = 50 |
| E08-SUT02-WEB-BLOCK | SUT-02 | `performance_glitch_user`, `/inventory.html` | `standard_user`, `/inventory.html` | longest_longtask_ms | 5000 ms (SUT02-EV-0011) | D minus Ba of at least 4500 ms | deterministic | N = 50 |
| E08-SUT03-WEB-LCP | SUT-03 | `/sut/ui/high-lcp` | `/sut/ui/zero-cls` | lcp_ms | 3000 ms (SUT03-EV-0013) | D minus Ba of at least 2500 ms | external dependency | N = 50 |
| E08-SUT03-WEB-CLS | SUT-03 | `/sut/ui/high-cls` | `/sut/ui/zero-cls` | cls (largest session window) | a shift at 4000 ms (SUT03-EV-0012) | CLS(D) above CLS(Ba) and a shift entry of D at or after 3500 ms whose sources include `#target-text` | deterministic | N = 50 |

- Tolerances (500 ms) are fixed from the evidence records and the brief, never from data. The host-dependent CPU endpoint of SUT-01, its random latency spike (SUT01-EV-0016) and the 2G view of SUT-03 (SUT03-EV-0015) are not conditions of E08 (E08-D-2, E08-D-17 option A); the limit is stated in every report of E08: the instrument is a web-page measurement, the spike is an API endpoint, the 2G view needs a network emulation the instrument does not use, and none is excluded for being unfavorable to any SUT.
- environment_type SELF_HOSTED for every condition, on a GitHub-hosted runner provisioned in the job; the controlled-instance record is experiments/E08-performance/controlled-instance-status.yaml (all four conditions VERIFIED by environment-verification round 1, run 45878792738). No PUBLIC_HOSTED instance is ever a target.
- The baseline page of the LCP condition is `/sut/ui/zero-cls` (E08-D-19; the evidence names no separate LCP baseline).
- Expectation of E08-SUT03-WEB-CLS: the expectation of the E01 record SUT03-EV-0012 (a late layout shift of `#target-text`) is kept although the static reading of pages/sut/ui/high-cls.jsx predicted none and round 1 observed none (no shift entry after the banner at about 4.09 s); a NOT_DETECTED is a valid outcome and the expectation is not changed after any DRY_RUN or measured execution (E08-D-8).

### One execution

- One execution is three page loads of the same condition, each in a fresh browser context (no cache, storage or cookies carried over): the degraded load D, an earlier baseline load Ba and a later baseline load Bb. The order rotates over the absolute execution index i: (D, Ba, Bb) for i mod 3 = 1, (Ba, D, Bb) for 2, (Ba, Bb, D) for 0, so that D takes each position (16, 17 and 17 times in 50 executions) and a drift of the runner acts on both kinds of load (E08-D-9). Detection compares D with Ba; the false-positive record compares Bb with Ba under the same rule. Nothing is restarted between executions (a page load changes no state of the SUT); the instance is provisioned once per job.
- Blocks, in order: starting-state check (the surface answers; SUT-01 also logs in both accounts with the behavior the condition declares), method (the three loads), classification, record (the run manifest last). An exception before the first measured navigation is attributed to TOOLING, after it to the SUT.
- Per load: SUT-01 logs in through `POST /api/auth/login`, seeds the client state on a first load of the web root, navigates to `/catalog`, waits for the first catalogue item (up to 20 s) and 1 s more. SUT-02 logs in through the login form (the session is a cookie), waits for the inventory list (the 5 s block of the glitch account after login is not measured), navigates to `/inventory.html` as a full document load, waits for the inventory list (up to 30 s) and 1 s more. SUT-03 logs in through `/sut/login` with the dummy credentials its labels show, navigates to the page and observes it for a fixed window of 8000 ms from the start of the document (E08-D-12). The measurement script is present from the start of every document and reads only the browser's own Performance APIs.

### Metrics, rules, categories

- first_item_ms: `performance.now()` of the document at the first attachment of an element matching `h2[data-testid^="pizza-name-"]`. longest_longtask_ms: the largest duration among the Long Tasks entries of the document (an observed API with no entry is 0 ms; an unsupported API is INCONCLUSIVE_METRIC_ABSENT). lcp_ms: `startTime` of the last Largest Contentful Paint entry within the window. cls: the web.dev definition, the largest sum of the shifts without recent input over session windows.
- Rule: DELAY, BLOCK and LCP are DETECTED when metric(D) minus metric(Ba) is at least the threshold of the table; CLS is DETECTED when cls(D) is above cls(Ba) and D has a shift entry at or after 3500 ms whose sources include the element with id `target-text`. The false-positive record applies the same difference rule to (Bb, Ba) (for CLS: cls(Bb) above cls(Ba)).
- A load counts only if the page showed its own content (the first catalogue item, the inventory list, or the page heading); a login page or an error page is INCONCLUSIVE_READY_SIGNAL_MISSING, never a non-detection; a missing signal of Bb only removes the false-positive record of that execution.
- Categories: DETECTED (SUCCESS), NOT_DETECTED (FAILURE; a recorded non-detection, not an error), INCONCLUSIVE_READY_SIGNAL_MISSING, INCONCLUSIVE_METRIC_ABSENT, INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED (LCP only; attribution EXTERNAL; never a non-detection, E08-D-14), START_SURFACE_NOT_READY and START_ACTIVATION_NOT_CONFIRMED (ABORTED), INTERRUPTED_ (ERROR), STUB_NO_BUNDLE (ERROR). There is no catch-all: an undeclared label is kept with a note so that the analysis fails closed on it. A recorded outcome of an execution, whatever its category, is data and never a stop.
- Denominators (E08-D-18, fixed before any data): the detection proportion of a condition is the number of DETECTED executions over the number of executions that are valid measurements (DETECTED or NOT_DETECTED); every INCONCLUSIVE_, START_, INTERRUPTED_ and STUB_NO_BUNDLE execution is reported with its count and its attribution and sits outside that denominator. The false-positive proportion is the number of executions whose baseline-against-baseline record is true over the number of executions that have such a record (both baseline loads valid), whatever the category of D. All N = 50 executions of a condition appear in the table of counts. No minimum number of valid executions is invented.

### Order, records, reporting

- Order of dispatch within an authorization: the order of the conditions file for the assigned SUT, one condition at a time (SUT-01: E08-SUT01-WEB-DELAY; SUT-02: E08-SUT02-WEB-BLOCK; SUT-03: E08-SUT03-WEB-LCP, then E08-SUT03-WEB-CLS); chains of the three SUTs are independent. Each condition is one workflow run holding EX0001 to EX0050; the run is imported under raw-data/E08-performance/<SUT>/ before the next condition of the same SUT is dispatched.
- Reporting (the analysis, later and only on the human research lead's instruction): per condition the proportion of executions that detect the degradation and the baseline-against-baseline false-positive proportion, each with a Wilson 95% interval, the medians descriptive; per ecosystem the H5 count; no composite, ranking or hypothesis label beyond H5; a near-certain result is stated as controllability evidence of the ground-truth condition and of the measurement, never as discriminating power (E08-D-7).
- Stop conditions: those of the frozen dispatch procedure (protocol/agent-governance-v6.md, Sections 3.5 and 3.7).
- Not decided by this record: any dispatch authorization, any further attempt, the campaign freeze, the analysis.
