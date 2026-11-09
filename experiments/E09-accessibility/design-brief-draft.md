# E09 Accessibility — design brief

**DRAFT.** Nothing in this file freezes, starts, authorizes, or dispatches anything. Every unknown is a HUMAN DECISION (section 12) or an open verification item (section 13).

| Field | Value |
|---|---|
| Campaign | E09-accessibility (experiments/E09-accessibility/README.md; status NOT_STARTED) |
| Modality | Accessibility — Web only (protocol/study-design-v1.md, section 7, item 6) |
| Hypothesis | H5, descriptive count comparison; SUT-01 vs SUT-02 and SUT-01 vs SUT-03 (protocol/statistical-analysis-plan-v1.md, sections 4.2 and 4.3; CONFIRMATORY by section 4.2) |
| Date | 2026-11-05 (local). Registry data retrieved 2026-11-06T01:25:42Z (UTC), see the pin proposal |
| Companion files | axe-core-pin-proposal-draft.md; campaign-configuration-draft.md (same folder) |

## 1. Summary

- Only SUT-01 has a documented, source-verified activation of a known accessibility violation (test account `a11y_glitch_user`). The violation mode is drawn at random per API call, so the experimenter cannot choose it. Only one of the three modes yields a known violation.
- The pinned scanner source does not support the E01 expectation that `image-alt` fires on an empty `alt`. The only expected rule under that mode is `empty-heading`, which is tagged best-practice, not WCAG. A WCAG-only scan configuration would never run it.
- SUT-02, SUT-03, SUT-04, and SUT-05 have no ground-truth condition in their E01 evidence. Recommended: no measured scan; each is reported as "no data — no ground-truth condition available".
- SUT-06 is a structural Score 0 (NO_WEB_SURFACE). It is reported as "no data — modality rated Score 0 in E01".
- H5 as specified compares a count of one (or three) with zero. No pairwise detection comparison is possible on current evidence, so no Fisher test and no risk difference can be computed.
- Recommended minimum design: one SUT-01 condition (ground-truth draws only), one control condition, N = 50 attempts each, and an environment verification on GitHub Actions before any START.

## 2. Verification basis

**Where the values come from.** `audits/` on the main branch is an unmerged template (experiments/E03-resetability/executor/README.md, section 2; PROTO-U07). The E01 audit content is on the six branches `audit/e01-sut0N-*`. Values below are the auditor rows of each branch (`audits/SUT-0N-*/audit.md`, section 3, row "Accessibility — Web only"; evidence records in `audits/SUT-0N-*/evidence.csv`, cited by evidence_id).

| SUT | Web surface | Provisional | Confirmed | Confirmation state | Evidence ids (branch) |
|---|---|---|---|---|---|
| SUT-01 | Yes (SUT01-EV-0003) | 3 | 3 | CONFIRMED (DOCUMENTED 1, SOURCE_VERIFIED 2) | SUT01-EV-0017, -0018, -0019 |
| SUT-02 | Yes | 2 | blank (no cap) | — | SUT02-EV-0013; negative SUT02-EV-0014 |
| SUT-03 | Yes | 2 | 2 | — | SUT03-EV-0019; negative SUT03-EV-0020 |
| SUT-04 | Yes | 2 | 2 | — | SUT04-EV-0018; negative SUT04-EV-0019 |
| SUT-05 | Yes | 1 | 1 | — | SUT05-EV-0019; negative SUT05-EV-0018 |
| SUT-06 | No | 0 | blank | structural | SUT06-EV-0023 (NO_WEB_SURFACE) |

The counts in the brief (3, 2, 2, 2, 1, 0) match these auditor rows. **Disputed-cell check:** the two human rulings on E01 cells concern SUT-01 Visual Testing (E01-HR-01) and SUT-04 Security Testing (E01-HR-02) (manifests/e01-proto-u04-correction.yaml). No accessibility cell was disputed.

**Not done.** The adjudicated matrix is derived data and was not read (common rule 2). Confirm before freeze that the adjudicated accessibility cells equal the values above.

## 3. Candidate known-violation catalogue

| Candidate id (not frozen) | SUT | Activation | Known outcome | Ground-truth status |
|---|---|---|---|---|
| E09-A11Y-SUT01-MISSING-NAME | SUT-01 | Documented account `a11y_glitch_user` (SUT01-EV-0017, DOCUMENTED); server mode `missing_name` (SUT01-EV-0018, SOURCE_VERIFIED) | `h2` heading with empty text (SUT01-EV-0019) | Known outcome only under this mode; drawn at random per call |
| (SUT-01 other modes) | SUT-01 | Same account; modes `wrong_lang` and `extreme_text` | No rule is named by any record | Not a known violation (see 4.4) |
| none | SUT-02 to SUT-05 | No activation found | No documented or source-verified violation with a defined expected outcome | No ground truth (count 0) |
| none | SUT-06 | No web surface | Structural absence | Not applicable to the modality (NO_WEB_SURFACE) |

## 4. SUT-01 (the only ground-truth candidate)

### 4.1 What the evidence establishes

- **Activation.** The README test-user table documents `a11y_glitch_user` as "Random a11y defect per call" (SUT01-EV-0017, DOCUMENTED). Activation is therefore by choosing an account, which is a documented mechanism (a Score 3 example: "deterministic test account").
- **Mechanism.** Under behavior `a11y_glitch`, `GET /api/pizzas` and `GET /api/cart` choose one of three modes at random per call (`random.choice`) and apply it to every item in that response: `missing_name` (name and description become ''), `wrong_lang` (text in another language), `extreme_text` (text repeated 15 times) (SUT01-EV-0018, SOURCE_VERIFIED, `backend/database.py`, `backend/constants.py`).
- **Rendered effect.** `ProductCard.jsx` renders `pizza.name` as the text of an `h2` (`data-testid pizza-name-<id>`) and as the `alt` of the product image. Under `missing_name` the heading is empty and `alt` is empty (SUT01-EV-0019, SOURCE_VERIFIED).
- **Page.** The catalog page is `frontend/src/pages/Catalog.jsx` (SUT01-EV-0003).
- **Auditor's own classification.** Stochastic, recorded in the cross-cutting Determinism section of the audit. The Score 3 rationale states that a fully enumerated three-outcome set satisfies the ground-truth rule (branch `audit/e01-sut01-omnipizza`, `audits/SUT-01-omnipizza/audit.md`, section 3 rationale; protocol/capability-rubric-v1.md, "Ground truth linkage").
- **Not executed.** The auditor ran no scanner. Expected rules were stated as examples ("e.g. axe-core's 'empty-heading' and 'image-alt' rules", SUT01-EV-0019).

### 4.2 Rubric consequence

The rubric's ground-truth rule requires a known expected outcome (protocol/capability-rubric-v1.md, "Ground truth linkage"). The `missing_name` draw has one. The other two draws have no named scanner rule, so they are not known violations for E09. The partial control of the draw is itself a categorical finding about Experimental Controllability. It is not a detection failure.

### 4.3 Expected outcome, corrected from the pinned scanner source

The pinned package is axe-core 4.14.0 (pin proposal). Its source (`package/axe.js` in that tarball) shows:

- `image-alt` passes when the `alt` attribute exists. Its `any` list includes `has-alt` (line 37401 block; `hasAltEvaluate` at line 28501 returns `hasAttr('alt')`). The `none` check `alt-space-value` flags only whitespace-only text (line 31013). So `alt=""` produces **no** `image-alt` violation. The E01 expectation (SUT01-EV-0019) does not hold for this mode.
- `empty-heading` (line 37234) applies to `h1` to `h6` and `[role=heading]`, and passes when the heading has visible text, `aria-label`, `aria-labelledby`, or a non-empty `title`. Its tags are `cat.name-role-value` and `best-practice`; impact `minor`. Its block has no `enabled: false` flag.
- Consequence: the predeclared expected rule under `missing_name` should be `empty-heading` only. Whether the `h2` carries `aria-label`, `aria-labelledby`, or `title` in the pinned frontend source is **not verified** here and must be checked. If it does, no predeclared rule fires on that DOM state: the condition then has no scanner-detectable expected outcome and must be re-decided before lock (HD-3), never after data.
- The E01 expectation that `image-alt` fires is recorded in SUT01-EV-0019, a frozen E01 record. The discrepancy is handled under HD-19, and no E01 record is edited.
- Consequence for the scan configuration: a WCAG-tag-only run would not execute `empty-heading`. The rule-set record must include best-practice tags or name the rule explicitly (HUMAN DECISION HD-4).

Verification of the rule behavior in a browser (visibility, computed roles) is not done here. It is an open verification item (section 13).

### 4.4 Stochastic handling: options

The executor cannot select the mode. The records name no parameter, seed, or documented override. Options:

- **(a) Recommended.** One condition, the `missing_name` stratum. Every attempt (N = 50) is a page load. A ground-truth instance is decided from the rendered DOM at scan time: every affected `h2[data-testid^="pizza-name-"]` has empty text. The catalog response body is recorded as corroboration. Detection is judged only on ground-truth instances. The count of ground-truth instances and of other draws is reported. Declared behavior class: stochastic (protocol/repeatability-determinism-v1.md, section 2: a stable distribution across repetitions is stochastic).
- **(b) Adaptive.** Repeat until 50 ground-truth draws. Not recommended: it changes what N counts and invites optional stopping. No protocol text allows it.
- **(c) Three conditions, one per mode.** Not recommended as ground truth: two modes have no named rule, so two of three conditions would be negative controls with no defined detection outcome.

The DOM rule is the operative classifier, because the scanner judges the DOM. The probe must confirm that the page fetches `GET /api/pizzas` once per load, or that every fetch in one load shares one draw. A second fetch could show a different draw from the one rendered (SUT01-EV-0018 does not say whether the mode is reported back).

### 4.5 Detection judgment and run-manifest mapping

- **Detected:** `violations[]` contains rule `empty-heading` with at least one node whose target matches the predeclared selector for the affected `h2` (`h2[data-testid^="pizza-name-"]`, with empty text). Rule presence elsewhere on the page does not count. Recommended threshold: at least one node (HUMAN DECISION HD-5).
- **Not detected:** a ground-truth instance (DOM condition confirmed at scan time) with no matching violation of the predeclared rule. Attribution is predeclared (HD-20): recorded as a non-detection of the predeclared rule set on the predeclared DOM condition; no cause is inferred from the data.
- **No ground-truth instance:** the draw is not `missing_name`. Recorded, not counted as a failure, not counted as a rate of zero.
- **Inconclusive or error:** scanner or page failure. Recorded, excluded from the denominator by the predeclared rule, and reported.
- **Total violation count:** recorded descriptively only, never the judgment.
- **Run manifest** (schemas/run-manifest.schema.v2.json): `outcome.expected` = rule id plus selector; `outcome.observed` = matched rule ids and node targets; `outcome.matches_expected` = detection; `outcome.outcome_category` carries the category above. `toolchain.web_runner` = Playwright 1.63.0; `toolchain.accessibility` = axe-core 4.14.0 (after the pin is recorded). `seed` = null (no seed control recorded). `environment_type` = SELF_HOSTED (section 4.9).

### 4.6 Page, state, and viewport

- Route `/catalog`, reached by direct navigation as documented in the SUT-01 README (SUT01-EV-0001). Login by the documented API route, then the client-state injection used in the E03 SUT-01 realization (experiments/E03-resetability/executor/README.md, sections 4.1 and 4.2).
- Viewport 1280 x 800. The E03 realization states that test ids built by `tid()` take a `-desktop` suffix at widths of 768 px and above (section 4.2). The target selector therefore needs a prefix or pattern match, validated in the probe.
- Market and language: the E03 realization uses `MX` and `es`. Predeclare the same values for comparability (HUMAN DECISION HD-7 if they change).
- Cart page: not recommended for the primary condition. The cart mutation exists (SUT01-EV-0018), but the records do not say that cart names render through an `h2` with an `alt`. Include only on a decision (HD-8).

### 4.7 Control condition

Same page, same viewport, and the default account `standard_user` used by the E03 SUT-01 realization (experiments/E03-resetability/executor/README.md, section 4.1). Expected rule absent. This separates the scan's baseline behavior from the activation effect. Its declared behavior class must be confirmed (its documented `behavior` value is not restated in the records read). Recommended: include (HD-6). It is not counted in H5.

### 4.8 Sample size

- **What is stated.** The E09 README says one run manifest per condition × page execution (Required evidence). It states no N. Repetition targets are in protocol/repeatability-determinism-v1.md, section 3: N = 50 per repeatable condition; the reduced N = 30 applies only to Android and iOS conditions, so it does not apply to a Web-only campaign. protocol/statistical-analysis-plan-v1.md, sections 3 and 4.1: N is the number of executions of one condition, and proportions use Wilson intervals.
- **Proposal.** N = 50 attempts for the SUT-01 condition and N = 50 for the control, each on one page (the catalog).
- **Arithmetic (planning only, assumption not stated in the records).** If the three modes were equally likely, about 17 of 50 attempts would be `missing_name` draws. The distribution is not stated. With 17 of 17 detected, the Wilson 95% lower bound is about 0.82. A larger N is not stated by the protocol and would need its own pre-registration in the configuration (HUMAN DECISION HD-9).

### 4.9 Activation and environment record

- Fault activation is an intentional fault, so the condition runs only on a controlled instance (protocol/study-design-v1.md, section 10.3; experiments/README.md, "Common rules", environment control). Never against the PUBLIC_HOSTED Render endpoint in `manifests/sut-manifest.yaml`.
- A GitHub-hosted runner that the study provisions is SELF_HOSTED (experiments/E03-resetability/ci-cd-execution-model.md, section 6). A workstation instance is LOCAL and is usable only for DEVELOPMENT or DRY_RUN classes.
- E03 verified the SUT-01 web and api surfaces as controlled instances (experiments/E03-resetability/README.md, section "Conditions": E03-CS001-SUT01-WEB verified by run 40628631086). Under section 10.5 that is evidence of the controlled instance, but E09 requires its own environment verification of the glitch path under CAMPAIGN-CI-WRITE-AUTH-01, which requires a controlled instance verified for each condition that needs one (HUMAN DECISION HD-10).
- `controlled_instance_available` for SUT-01 is null in `manifests/sut-manifest.yaml` because Android and iOS surfaces were not provisioned. Section 10.5 says the boolean summarizes and does not decide; the per-condition decision lives in the configuration. The boolean is not changed by E09.
- Record per run: scanner output (raw JSON, `violations`, `passes`, `incomplete`, `inapplicable`; axe.js line 34920), DOM snapshot at scan time, catalog response body, activation record (the account and the observed mode), environment record (runner image, Chromium build observed, locale, viewport).

### 4.10 What is missing for SUT-01

Realized-draw classifier validated in a probe; target selector and `-desktop` suffix validated; `h2` ARIA attributes checked in the pinned frontend source; empty-heading in the default rule set confirmed by execution; control account's behavior value confirmed; the single catalog fetch per load (section 4.4); environment verification on GitHub Actions; the discrepancy with SUT01-EV-0019 recorded under HD-19 before lock.

## 5. SUT-02 to SUT-05: no ground-truth condition

| SUT | Positive E01 finding (evidence) | Negative search (evidence) | What is not stated | Recommendation |
|---|---|---|---|---|
| SUT-02 | Stable DOM and aria/alt usage (SUT02-EV-0013) | No intentional fault or a11y dependency in `src/` (SUT02-EV-0014) | The search recorded covers `src/` only; documentation is not recorded as searched | No measured scan. A documentation-only check is an open item (section 13) |
| SUT-03 | Aria and alt usage (SUT03-EV-0019): alt "present on most (not all)" images | No documented or code-level intentional fault in README or all `src/` and `pages/` (SUT03-EV-0020) | Incidental alt gaps are not documented as known | No measured scan. The incidental gaps are not ground truth (HD-11) |
| SUT-04 | Labels and live regions (SUT04-EV-0018) | No axe dependency, documented or known violation in package, docs, or source (SUT04-EV-0019) | None material | No measured scan |
| SUT-05 | Score 1: UI reachable by a generic scanner (SUT05-EV-0019) | No accessibility dependency (SUT05-EV-0018); no accessibility challenge in the 16 categories or the Angular app directory (SUT05-EV-0019) | README and docs search not recorded | No measured scan. Documentation check open (section 13) |

For SUT-02 to SUT-05 the H5 count is 0, recorded as a finding. The detection-rate cell is "no data — no ground-truth condition available" (SAP, section 5; experiments/E09-accessibility/README.md, Objective). It is never a detection failure and never a rate of zero.

## 6. SUT-06: structural recording

SUT-06 has no web surface (SUT06-EV-0001, SUT06-EV-0002). Its E01 cell is Score 0 with `structural_scope_note` NO_WEB_SURFACE (SUT06-EV-0023). Its native mobile identifiers are Automation Affordances, not evidence for this Web-scoped modality (SUT06-EV-0023, notes). In E09 it has no run and no condition. The cell is shown in every E09 table as "no data — modality rated Score 0 in E01 (NO_WEB_SURFACE)". It is not dropped, not a separate exemption, and not a detection rate of zero (protocol/capability-rubric-v1.md, "Structural scope note"; SAP section 5).

## 7. H5 implications

| SUT | Ground-truth conditions (recommended count) | Detection rate | Note |
|---|---|---|---|
| SUT-01 | 1 (HD-2) | Measured (N = 50 attempts; ground-truth instances reported) | Wilson interval per SAP section 3 |
| SUT-02 | 0 | no data | No condition |
| SUT-03 | 0 | no data | No condition |
| SUT-04 | 0 | no data | No condition |
| SUT-05 | 0 | no data | No condition |
| SUT-06 | 0 (structural) | no data | NO_WEB_SURFACE |

With SUT-02 and SUT-03 at zero, the two H5 pairs have no shared condition. No Fisher 2x2 table and no risk difference is formed (SAP sections 3 and 4.1). The H5 comparison on the count is descriptive.

## 8. Mapping record

No FROZEN mapping record is required for the recommended design. The common rule that requires one names E02 to E07 only (experiments/README.md, "Common rules", scenario equivalence). SAP section 4.1, however, requires equivalent conditions for any between-ecosystem comparison, and the mapping vocabulary includes `ACCESSIBILITY_FINDING` (protocol/equivalent-scenario-mapping-v1.md, field table, `observable_oracle_class`). HUMAN DECISION HD-13 decides whether a mapping record is needed once any SUT-02 or SUT-03 condition exists.

## 9. Workflow gate list (names only; proposed, not created)

Proposed workflow names, following E03: `e09-environment-verification.yml` and `e09-measured-execution.yml`. Gates, by name:

1. Campaign START and its authorization id (protocol/change-control-v1.md, section 7).
2. Locked "Campaign configuration" record in experiments/E09-accessibility/README.md.
3. Run-manifest schema named and digest-checked.
4. Frozen agent governance (protocol/agent-governance-v5.md).
5. Pinned web commit for SUT-01 captured (9ca37674 per manifests/sut-manifest.yaml).
6. Toolchain pins present and equal to the executed versions (`web_runner`, `accessibility`).
7. Scanner tarball integrity check (sha512) before use.
8. Controlled instance verified on GitHub Actions for each fault-activation condition (section 10.3).
9. Controlled-instance decision recorded per condition with environment_type SELF_HOSTED.
10. Realized-draw classifier and expected-rule selector validated in a recorded probe before lock.
11. Declared behavior class (stochastic) locked per condition.
12. Comparison classification (H5 CONFIRMATORY) recorded.
13. Mapping record check (only if a pairwise detection comparison is configured).
14. Prompt check (only if an agent prompt is configured).
15. Pinned repository commit and workflow revision captured as outputs.
16. First attempt only; default branch only; one dispatch per approval.
17. Guard: refuses any PUBLIC_HOSTED target for a fault-activation condition.
18. Guard: no scan for SUT-02 to SUT-06 unless a condition is configured.
19. Publication-hygiene check.

## 10. Reuse of the E03 Playwright executor, and what is new

**Reuse (pattern, not code).** The dispatch-only workflow with a fail-closed gate job (E03 ci-cd model, section 3); an entry script that verifies implementation digests before running and writes the manifest last, with no retry (executor README, section 1; `run-condition.sh`); provenance capture (ci-cd model, section 4); environment_type determination (section 6); Playwright for Python 1.63.0 with hashed requirements (executor `requirements.txt`); login and client-state injection (executor README, sections 4.1 and 4.2).

**Reuse (code).** Only by copying generic helpers into a separate E09 package under its own digest lock. Importing the locked E03 package would couple two campaigns and touch a frozen implementation.

**New.** The scanner loader and tarball hash check; the `add_script_tag` injection and `axe.run` call; the result capture (passes, violations, incomplete, inapplicable); the realized-draw classifier; the target selector and detection judgment; the control condition; the DOM snapshot and scanner artifact classes (align with ci-cd model, section 7, which this brief did not read in full).

## 11. Activation and environment-record needs, summarized

- Activation of the SUT-01 condition: controlled instance only (section 10.3).
- Records: activation record with the account and the observed draw; environment record; the scanner tool and version in the run manifest; the target selector and rule set as predeclared.
- Non-measured environment verification (ENVIRONMENT_VERIFICATION) before any START: the glitch path, the draw classifier, the selector, the rule set, and the `h2` ARIA check. Local runs are DEVELOPMENT or DRY_RUN only and never enter raw-data/.

## 12. HUMAN DECISIONs

- **HD-1. Stochastic activation design.** Options: (a) one `missing_name` condition with N = 50 attempts and realized-draw stratification; (b) adaptive stopping until 50 ground-truth draws; (c) three conditions, one per mode. **Recommend (a).** Reason: (b) changes what N counts; (c) gives two conditions no named rule.
- **HD-2. H5 count unit for SUT-01.** Options: 1 (only the mode with a named rule) or 3 (all modes). **Recommend 1.** Reason: the count should count conditions with a defined expected outcome (protocol/capability-rubric-v1.md, "Ground truth linkage").
- **HD-3. Expected rule set.** Options: `empty-heading` only, or `empty-heading` plus `image-alt`. **Recommend `empty-heading` only.** Reason: `image-alt` cannot fire for `alt=""` in the pinned source (section 4.3); a predeclared rule that cannot fire would make the count an artifact. Confirm by probe before lock.
- **HD-4. Scanner rule scope.** Options: (i) default rule set (includes best-practice); (ii) WCAG tags only, which excludes `empty-heading`; (iii) explicit inclusion of `empty-heading`. **Recommend (iii) with the rule set recorded.** Reason: (ii) makes the known violation undetectable by design. The record must state that `empty-heading` is a best-practice, minor rule, so the ground truth is weaker than a WCAG failure.
- **HD-5. Detection threshold.** Options: at least one matching node, or all affected nodes. **Recommend at least one node.** Reason: the question is whether the scanner detects the known violation, not coverage.
- **HD-6. Control condition.** Options: include (recommended), or omit. Not counted in H5 either way.
- **HD-7. Market and locale.** Options: reuse the E03 values (`MX`, `es`), or other values. **Recommend reuse.**
- **HD-8. Pages.** Options: Catalog only (recommended), or Catalog and cart. Cart requires its own probe.
- **HD-9. Sample size.** Options: N = 50 attempts (recommended, the protocol standard); or a pre-registered larger N to reach a target number of ground-truth draws. Any larger N needs its own justification in the configuration.
- **HD-10. Controlled-instance evidence.** Options: reuse the E03 SUT-01 web verification, or run an E09 environment verification (recommended, under CAMPAIGN-CI-WRITE-AUTH-01). Also decide whether the E09 controlled-instance decision is recorded per condition only (recommended) and the sut-manifest boolean stays null.
- **HD-11. Incidental violations.** Options: (i) exclude source-observed incidental gaps such as SUT-03 missing alt (recommended, because Score 3 requires a controllable mechanism and an incidental defect cannot be activated or reset); (ii) include them as ground truth. Recommend (i).
- **HD-12. Scanner loading route.** Options: (i) fetch the pinned tarball by URL, verify sha512, inject `axe.min.js` from Python (recommended; no Node in the executor; parity with pip `--require-hashes`); (ii) `npm ci` from a lock file (requires Node in the job; the study already uses this pattern for its mobile harness). See the pin proposal.
- **HD-13. Mapping record.** Options: none now (recommended, no SUT-02 or SUT-03 condition exists); or require a FROZEN mapping record for any pairwise detection comparison, as SAP section 4.1 implies. Decide the second option before any cross-SUT rate comparison.
- **HD-14. Run-manifest schema.** Options: v2 (recommended; a superset that adds the optional `actions[].outcome`) or v1 (the E09 README and experiments/README name `schemas/run-manifest.schema.json`). Recommend v2, as E03 uses.
- **HD-15. Required Actions.** The schema makes actions mandatory for E02 and E03 only. Options: record no actions for E09 (recommended, scope discipline), or record login and navigation as actions for comparability.
- **HD-16. Axe-core version.** Options: 4.14.0 (recommended; latest at retrieval, not deprecated) or 4.13.0. See the pin proposal.
- **HD-17. Dispatch-procedure prompt.** Options: none, or a frozen prompt as E03 has. **Recommend none**, unless the configuration names one; the measured dispatch is by the ORCHESTRATOR under CAMPAIGN-CI-WRITE-AUTH-01.
- **HD-18. Python executor lock.** Options: reuse the E03 hashed requirements under the E03 lock, or a new E09 lock with the same pins (Playwright 1.63.0 with its runtime dependencies, by hash), plus the Python series pin. **Recommend a new E09 lock**, so that the E03 locked implementation is not touched.
- **HD-19. Recording the SUT01-EV-0019 discrepancy.** E01 is frozen, and its records are closed to ordinary modification (protocol/change-control-v1.md, section 7). The `image-alt` half of SUT01-EV-0019's expected outcome cannot occur under the pinned source (section 4.3). Options: (i) an entry in protocol/unresolved.md (or the unresolved list of the SUT-01 audit branch), with no change to the E01 record; (ii) a correction record under protocol/change-control-v1.md, section 5, in the same form as the existing E01 correction records under manifests/; (iii) a note in the E09 configuration only. **Recommend (i) or (ii).** Neither option edits the frozen E01 record.
- **HD-20. Attribution of a non-detection.** Options: (i) a non-detection is recorded as a non-detection of the predeclared rule set on the DOM condition confirmed at scan time, with no cause inferred (recommended); (ii) in addition, a predeclared DOM assertion runs beside the scanner, so that a non-detection can be separated from the absence of the DOM condition. **Recommend (i)**, with (ii) decided only if the probe shows the DOM condition is unstable.

## 13. Open verification items (before lock; not decisions)

1. Probe (ENVIRONMENT_VERIFICATION, not measured): the DOM-based ground-truth classifier, with the catalog response body as corroboration; whether the page fetches `GET /api/pizzas` once per load; the selector including the `-desktop` form; `empty-heading` firing on the affected `h2`; `image-alt` not firing on `alt=""`; the default rule set includes `empty-heading`.
2. Pinned frontend source: whether the affected `h2` carries `aria-label`, `aria-labelledby`, or `title` (any of which would prevent `empty-heading`).
3. Control account `standard_user`: confirm its documented behavior value is the non-glitch default.
4. SUT-02 and SUT-05: documentation search (README and docs) for documented known accessibility issues, recorded as evidence before "no ground truth" is recorded as a final finding.
5. The adjudicated accessibility cells equal the auditor values in section 2 (ORCHESTRATOR check against the adjudicated matrix; not read here).
6. The `/catalog` route (documented in SUT01-EV-0001) confirmed against the pinned frontend source.
7. The SUT-05 web surface's controlled-instance status: E03 verified the SUT-05 API surface on GitHub Actions; the web surface is served by the same process (manifests/sut-manifest.yaml, SUT-05 notes) but is not separately recorded for E09.

## 14. Sources

- experiments/E09-accessibility/README.md (Objective; Required evidence; Future variables).
- protocol/study-design-v1.md, sections 7, 8, 9 (campaign mapping table, E09 row), 10.1 to 10.5.
- protocol/statistical-analysis-plan-v1.md, sections 3, 4.1 to 4.3, 5.
- protocol/capability-rubric-v1.md, Score 2 and 3, "Score 3 confirmation", "Structural scope note", "Ground truth linkage".
- protocol/repeatability-determinism-v1.md, sections 2 and 3.
- experiments/README.md, "Common rules" and "Current state".
- manifests/sut-manifest.yaml; manifests/toolchain-manifest.yaml (`tools.web_runner`, `tools.accessibility`).
- manifests/e01-proto-u04-correction.yaml (disputed cells).
- Branches audit/e01-sut01-omnipizza to audit/e01-sut06-webdriverio: `audits/SUT-0N-*/audit.md` section 3, `audits/SUT-0N-*/evidence.csv`, cited by evidence_id.
- experiments/E03-resetability/README.md (Conditions; Campaign configuration); executor/README.md (sections 1 to 4); ci-cd-execution-model.md (sections 3, 6).
- schemas/run-manifest.schema.v2.json.
- Registry data: https://registry.npmjs.org/axe-core/latest (retrieved 2026-11-06T01:25:42Z) and https://registry.npmjs.org/axe-core/-/axe-core-4.14.0.tgz (retrieved 2026-11-06T01:31:09Z; integrity verified).
