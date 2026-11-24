# E08 Performance: design brief

**DRAFT.** Nothing in this file freezes, starts, authorizes, or dispatches anything. Every unknown is a HUMAN DECISION (section 8) or an open verification item (section 9).

| Field | Value |
|---|---|
| Campaign | E08-performance (experiments/E08-performance/README.md; status NOT_STARTED) |
| Modality | Performance (protocol/study-design-v1.md, section 7) |
| Hypothesis | H5, descriptive count comparison of controlled non-functional ground-truth conditions per ecosystem, SUT-01 against SUT-02 and SUT-01 against SUT-03, CONFIRMATORY (H5) (protocol/statistical-analysis-plan-v1.md, sections 4.2 and 4.3; the variable spans E08, E09, E10 and E11; detection rates per condition are reported per section 5). Specialist baselines are EXPLORATORY unless pre-registered |
| Date | 2026-11-23 (local) |
| Basis | E01 adjudicated matrix and the evidence of its Performance cells |

## 1. Summary

- Performance is CONFIRMED Score 3 for SUT-01, SUT-02 and SUT-03; SUT-04 is Score 2 (no controlled-degradation condition, SUT04-EV-0017), SUT-05 and SUT-06 are Score 1. H5 compares SUT-01 with SUT-02 and with SUT-03, and the E01 evidence shows that all three have a documented, source-verified, deterministic degraded condition. Measuring only SUT-01 would count the other two as zero although their evidence shows otherwise, so the recommended scope is SUT-01, SUT-02 and SUT-03, on the web surface.
- SUT-04, SUT-05 and SUT-06 have no ground-truth condition in their E01 evidence for this modality and are reported as "no data, no ground-truth condition available" (never a detection rate of zero; protocol/statistical-analysis-plan-v1.md, section 5).
- The three degraded conditions are different mechanisms. A fixed server delay (SUT-01), a blocked main thread (SUT-02) and a late layout shift or late largest paint (SUT-03) are observed with one common instrument that reads the browser's own metrics (section 4), so that no ecosystem is measured with an instrument built for another.
- The expected effects are large against runner noise, so detection is near certain by construction. The result is a statement about controllability of the ground-truth condition and about the measurement, not about instrument sensitivity; the report says so.

## 2. What the evidence establishes

| Evidence | SUT | Mechanism | Status | Use in E08 |
|---|---|---|---|---|
| SUT01-EV-0014, -0015 | SUT-01 | `performance_glitch_user`: `apply_user_behavior()` sleeps 3.0 s on every endpoint that applies the user behaviour (GET /api/pizzas, POST /api/checkout) | DOCUMENTED, SOURCE_VERIFIED | degraded condition |
| SUT01-EV-0016 | SUT-01 | random latency spike (0.5 to 5.0 s, applied delay reported in the body) and a host-dependent CPU endpoint | SOURCE_VERIFIED | not deterministic; see E08-D-2 |
| SUT02-EV-0001, -0011 | SUT-02 | six fixed accounts with one shared password; for `performance_glitch_user` the inventory page runs a synchronous 5000 ms busy-wait | SOURCE_VERIFIED | degraded condition (web) |
| SUT03-EV-0012, -0013, -0014 | SUT-03 | after a client-side cookie check, a layout shift at exactly 4000 ms (high CLS page) and a largest paint delayed 3000 ms with the image from an external host (high LCP page); paired zero-shift and low-INP pages | SOURCE_VERIFIED | degraded conditions with paired baselines |
| SUT03-EV-0015 | SUT-03 | a 2G-only view when the Network Information API reports 2g | SOURCE_VERIFIED | not selected (engine-dependent) |

Pins and instances: the pinned commits are in manifests/sut-manifest.yaml (SUT-01 9ca37674d374e9303912e259641ee86baf3aabe1). The web surfaces of SUT-01, SUT-02 and SUT-03 each have a controlled instance verified on GitHub Actions for the conditions of E03; the study-level flag `controlled_instance_available` is null for SUT-01 (its mobile surfaces were not provisioned) and the per-condition decision goes in the campaign configuration, to be confirmed by this campaign's DRY_RUN rounds.

## 3. Proposed conditions (candidate, not frozen)

| Condition | SUT | Degraded | Paired baseline | Expected |
|---|---|---|---|---|
| E08-SUT01-WEB-DELAY | SUT-01 | `performance_glitch_user` opens the catalogue | a standard test user, same page | the first catalogue item appears about 3.0 s later |
| E08-SUT02-WEB-BLOCK | SUT-02 | `performance_glitch_user` opens the inventory page | `standard_user`, same page | a main-thread task of about 5000 ms |
| E08-SUT03-WEB-LCP | SUT-03 | the high-LCP page | the zero-shift page (largest paint without the delay; to be verified, V-4) | largest paint delayed by about 3.0 s |
| E08-SUT03-WEB-CLS | SUT-03 | the high-CLS page | the zero-CLS page | a layout shift at about 4.0 s, CLS above zero |

Each degraded condition is measured in the same job as its paired baseline, in interleaved order, so that runner speed changes act on both. A baseline measured against itself across executions gives a false-positive record per condition; it is an addition of this design, not a requirement of the campaign README.

## 4. Measurement (candidate)

- Instrument: Playwright driving Chromium, with the browser's own Performance APIs read through a pinned PerformanceObserver script (navigation and paint timing, largest contentful paint, layout shift, long tasks), one instrument and one script for every condition (manifests/toolchain-manifest.yaml, `tools.performance`, still TBD). The tool and its version go in every run manifest, and the raw metric stream is kept unchanged. The load is one sequential client and no significant load.
- Detection rule per condition, fixed before the first run and written from the evidence, never from data: the degraded run exceeds its paired baseline of the same execution on the named metric by at least the expected effect minus a fixed tolerance (SUT-01: first catalogue item, 3.0 s minus 0.5 s; SUT-02: longest long task at least 4.5 s; SUT-03 LCP: largest-paint time, 3.0 s minus 0.5 s; SUT-03 CLS: a shift of the target element after 3.5 s with CLS above the baseline).
- N = 50 executions per condition (protocol/repeatability-determinism-v1.md, section 3, standard target; no mobile condition); 200 executions in all.
- Reporting: per condition the proportion of executions that detect the degradation and the baseline-against-baseline false-positive proportion, each with a Wilson 95% interval, median differences descriptive; per ecosystem the H5 count; no ranking, no composite; a near-certain result stated as controllability evidence.

## 5. Environment and safety

- A degraded condition is an intentional fault activation, so it runs only on a controlled instance (protocol/study-design-v1.md, section 10.3): each web surface LOCAL or SELF_HOSTED on a GitHub Actions runner, never PUBLIC_HOSTED. The instance record goes in every run manifest.
- E08-SUT03-WEB-LCP loads the delayed image from an external host (SUT03-EV-0013); that host sits outside the evaluated version's control and its answer time can add to the delay. The run records whether and when it answered, and the condition is flagged as having an external dependency (a determinism class of E05).

## 6. Execution model

- GitHub Actions under CAMPAIGN-CI-WRITE-AUTH-01: dispatch-only environment-verification and measured-execution workflows, a frozen executor with its implementation hash, a frozen dispatch prompt, one dispatch authorization per assigned SUT (agent-governance-v6, Section 3.7), first attempt only; non-measured DRY_RUN rounds before the START, which never enter raw-data/.

## 7. Scenario mapping

- H5 counts conditions per ecosystem and reports detection per condition; it does not require one canonical scenario across ecosystems. No mapping record is proposed unless a decision says otherwise (V-5).

## 8. HUMAN DECISIONS (recommended defaults; each can be vetoed by its id)

| Id | Decision | Recommended default |
|---|---|---|
| E08-D-1 | Which ecosystems carry measured conditions | SUT-01, SUT-02, SUT-03 (web); the others "no data, no ground-truth condition available" |
| E08-D-2 | Count unit for H5 (shared with E09, E10, E11, as E09's HD-2) | every configured ground-truth condition with a known expected outcome counts once, deterministic or stochastic with its draw recorded; control and baseline conditions do not count; the host-dependent CPU endpoint of SUT-01 has no expected value and is not a condition |
| E08-D-3 | Conditions | the four rows of section 3; SUT-01's random latency spike is added only if D-2 is read to admit it |
| E08-D-4 | Instrument | Playwright with browser Performance APIs, one script for all conditions |
| E08-D-5 | Detection rule and tolerances | as in section 4 |
| E08-D-6 | N | 50 per condition |
| E08-D-7 | Reading of near-certain results | controllability evidence, not discriminating power |

## 9. Open verification items

- V-1 That the SUT-01 catalogue request of `performance_glitch_user` goes through the 3.0 s dependency and that the catalogue's first item is a stable "ready" signal; whether login itself is delayed (it would change what is timed).
- V-2 That the 5000 ms task of SUT-02 shows in the Long Tasks API in the pinned Chromium, and how the page reports "ready".
- V-3 That the SUT-03 pages are reachable through the documented flow (client-side sign-in, then the page) in a fresh browser state, and the same cookie gate applies on every load.
- V-4 What serves as the baseline of the high-LCP page (the zero-CLS page loads its content synchronously; the evidence does not name an LCP baseline).
- V-5 That no scenario mapping record is needed.
- V-6 Runner noise: the spread of baseline timings in the DRY_RUN rounds, to check that the tolerances are well above it.
- V-7 The Playwright and Chromium pins (the environment of E09 may be reused) and a verified release for any added script dependency, with registry data retrieved on a recorded date.
