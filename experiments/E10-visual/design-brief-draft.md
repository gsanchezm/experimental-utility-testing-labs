# E10 Visual: design brief

**DRAFT.** Nothing in this file freezes, starts, authorizes, or dispatches anything. Every unknown is a HUMAN DECISION (section 8) or an open verification item (section 9).

| Field | Value |
|---|---|
| Campaign | E10-visual (experiments/E10-visual/README.md; status NOT_STARTED) |
| Modality | Visual Testing (protocol/study-design-v1.md, section 7) |
| Hypothesis | H5, descriptive count comparison of controlled non-functional ground-truth conditions per ecosystem, SUT-01 against SUT-02 and SUT-01 against SUT-03, CONFIRMATORY (H5) (protocol/statistical-analysis-plan-v1.md, sections 4.2 and 4.3; the variable spans E08, E09, E10 and E11; detection rates per condition are reported per section 5). Specialist baselines are EXPLORATORY unless pre-registered |
| Date | 2026-11-23 (local) |
| Basis | E01 adjudicated matrix and the evidence of its Visual Testing cells |

## 1. Summary

- Visual Testing is effective Score 3 for SUT-01 (by the human ruling E01-HR-01 after the adjudicator returned DISPUTED; the auditor's own confirmed score was 2), SUT-02 and SUT-03 (CONFIRMED). SUT-04 and SUT-05 are Score 1 and SUT-06 is Score 2. H5 compares SUT-01 with SUT-02 and with SUT-03, and all three have a documented, source-verified visual perturbation tied to an account or a page, so the recommended scope is SUT-01, SUT-02 and SUT-03 on the web surface. SUT-04, SUT-05 and SUT-06 are reported as "no data, no ground-truth condition available" (never a detection rate of zero; protocol/statistical-analysis-plan-v1.md, section 5).
- The SUT-01 perturbation is a data condition (price 0.0 and a broken image address for every item; SUT01-EV-0020). The auditor's tie-break note names the missing piece for a firmer Score 3: an executed screenshot comparison showing the condition as a stable, tool-detectable difference against a baseline. E10 produces that observation. It is reported in its own E10 table and never edits or restates the E01 score (different evidence layers).
- E10 also records the false positive of the method: the same unperturbed state captured repeatedly and compared with itself (this is a requirement of the E10 README).

## 2. What the evidence establishes

| Evidence | SUT | Mechanism | Status | Use in E10 |
|---|---|---|---|---|
| SUT01-EV-0020 | SUT-01 | `problem` behaviour forces price 0.0 and the broken image address on catalogue and cart items | SOURCE_VERIFIED | perturbation |
| SUT01-EV-0021 | SUT-01 | profile seeding endpoint documented as pinning a value before a visual-regression snapshot | SOURCE_VERIFIED | state pinning |
| SUT02-EV-0001, -0015 | SUT-02 | account `visual_user` adds the classes `visual_failure` and `btn_visual_failure` to the cart icon container, the checkout button and the drawer menu icons; the inventory prices become random | SOURCE_VERIFIED | perturbation (the class part is deterministic, the prices are not) |
| SUT03-EV-0001, -0021 | SUT-03 | account `image_not_loading_user` forces every product thumbnail source to an empty string | SOURCE_VERIFIED | perturbation (the primary basis of the SUT-03 score) |
| SUT03-EV-0012, -0014, -0023 | SUT-03 | the high-CLS page shifts its content at 4000 ms and the zero-CLS page does not | SOURCE_VERIFIED | second SUT-03 condition, with its paired baseline |

Pins and instances: the pinned commits are in manifests/sut-manifest.yaml (SUT-01 9ca37674d374e9303912e259641ee86baf3aabe1). The web surfaces of the three ecosystems each have a controlled instance verified on GitHub Actions for E03 conditions; the study-level flag `controlled_instance_available` is null for SUT-01 (its mobile surfaces were not provisioned), so the per-condition decision goes in the campaign configuration and is confirmed by this campaign's DRY_RUN rounds.

## 3. Proposed conditions (candidate, not frozen)

| Condition | SUT | State A (baseline) | State B (perturbed) | Expected difference |
|---|---|---|---|---|
| E10-SUT01-WEB-PROBLEM | SUT-01 | `standard_user`, catalogue page | `problem_user`, same page, market and viewport | every item price and every item image |
| E10-SUT02-WEB-VISUAL | SUT-02 | `standard_user`, inventory page | `visual_user`, same page | cart icon container, checkout button, drawer menu icons (the random prices are excluded from the expectation) |
| E10-SUT03-WEB-IMAGE | SUT-03 | `demouser`, shelf | `image_not_loading_user`, same shelf | every product thumbnail |
| E10-SUT03-WEB-SHIFT | SUT-03 | the zero-CLS page | the high-CLS page after the 4 s mark | the shifted element |

Each condition has a baseline-against-baseline control: State A captured again and compared with the first capture, in the same job. It is the false-positive condition and is not a ground-truth condition.

## 4. Measurement (candidate)

- Capture: Playwright screenshots (manifests/toolchain-manifest.yaml, `tools.visual`) at one desktop viewport, animations disabled, the same browser build for A and B, element-scoped captures where the expectation is an element, after the page reports every image settled (complete, with the recorded natural width of the broken ones).
- Comparison: Pixelmatch with a fixed per-pixel threshold; the differing-pixel count and ratio are recorded unchanged with the diff image.
- Detection rule per condition, fixed before the first run: the difference is detected when the differing-pixel ratio is at least the ratio of decision E10-D-5 and the diff mask overlaps the bounding box of every element named in the expectation (boxes read from the DOM at capture). A ratio alone would not show that the expected difference, and not noise, was found.
- N = 50 executions per condition (protocol/repeatability-determinism-v1.md, section 3, standard target; no mobile condition); 200 executions in all. One execution = capture A, capture B, capture A again, each from a fresh page load.
- Reporting: per condition the proportion of executions detecting the expected difference and the proportion flagging a difference on baseline against baseline, each with a Wilson 95% interval, ratios descriptive; per ecosystem the H5 count; no ranking, no composite.

## 5. Environment and safety

- A perturbation is a fault activation, so it runs only on a controlled instance (protocol/study-design-v1.md, section 10.3): each web surface LOCAL or SELF_HOSTED on a GitHub Actions runner, never PUBLIC_HOSTED. The instance record goes in every run manifest.
- The SUT-01 broken image address points at an external host. The expected state is a failed image load; the run records whether the host name resolved, and the check never depends on that host answering.

## 6. Execution model

- GitHub Actions under CAMPAIGN-CI-WRITE-AUTH-01: dispatch-only environment-verification and measured-execution workflows, a frozen executor with its implementation hash, a frozen dispatch prompt, one dispatch authorization per assigned SUT (agent-governance-v6, Section 3.7), first attempt only. Non-measured DRY_RUN rounds precede the START, never enter raw-data/, and are the only place where the ratio of E10-D-5 may be calibrated.

## 7. Scenario mapping

- H5 counts conditions per ecosystem and reports detection per condition; it does not require one canonical scenario across ecosystems. No mapping record is proposed unless a decision says otherwise.

## 8. HUMAN DECISIONS (recommended defaults; each can be vetoed by its id)

| Id | Decision | Recommended default |
|---|---|---|
| E10-D-1 | Which ecosystems carry measured conditions | SUT-01, SUT-02, SUT-03 (web); the others "no data, no ground-truth condition available" |
| E10-D-2 | Count unit for H5 (shared with E08, E09, E11, as E09's HD-2) | each configured ground-truth condition counts once; baseline and control conditions do not count |
| E10-D-3 | Conditions | the four rows of section 3 |
| E10-D-4 | Viewport | one desktop viewport |
| E10-D-5 | Detection rule | ratio threshold calibrated on DRY_RUN baseline captures and fixed before the START, plus overlap with the expected element boxes |
| E10-D-6 | Tooling | Playwright screenshots and Pixelmatch at pinned versions |
| E10-D-7 | N | 50 per condition |
| E10-D-8 | Relation to E01 | the E10 result is reported separately; the E01 score stays untouched |

## 9. Open verification items

- V-1 That the broken image state of SUT-01 is reached identically on a GitHub-hosted runner (name resolution, time to failure) and that the settle check makes the capture stable.
- V-2 The baseline false-positive ratio over repeated DRY_RUN captures (fonts, anti-aliasing, any clock or date on the page), to calibrate E10-D-5 without looking at the perturbed ratio.
- V-3 That the SUT-02 class perturbation is visible at the chosen viewport and that the random prices can be masked or excluded without touching the expected elements.
- V-4 That the SUT-03 catalogue shows the same item set for both accounts, and that the 4 s shift can be captured at a fixed time after the mark.
- V-5 The pinned Playwright and Pixelmatch releases, with registry data retrieved on a recorded date (the Playwright environment of earlier campaigns may be reused).
