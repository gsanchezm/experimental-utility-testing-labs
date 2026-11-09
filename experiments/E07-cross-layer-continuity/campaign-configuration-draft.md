# E07-cross-layer-continuity: Campaign configuration (SKELETON)

| Field | Value |
|---|---|
| Status | DRAFT. Not a locked configuration. Not an input to any run, workflow, or dispatch. |
| Campaign | E07-cross-layer-continuity (experiments/E07-cross-layer-continuity/README.md) |
| Campaign status | NOT_STARTED (experiments/E07-cross-layer-continuity/README.md, "Current status") |
| Scope | Web and API layers only (human research lead decision of 2026-11-05). Mobile layers are not configured. |
| Prepared | 2026-11-05, as a design draft for the orchestrator, accompanying design-brief-draft.md |
| Order | Follows the "Campaign configuration" bullet of experiments/README.md ("Common rules for all campaigns"): mapping records, pinned SUT versions, toolchain versions, prompt version(s), conditions and environment types, sample size, exclusion and attribution rules, CONFIRMATORY comparisons. Sections 9 to 13 are added because E03 and the campaign rules require them. |
| Convention | Every unknown is marked HUMAN DECISION. Candidate identifiers are "candidate, not frozen". |

## 1. Frozen scenario mapping records

| canonical_scenario_id | File (proposed) | Mapping status | Directions | Used by |
|---|---|---|---|---|
| CS-005 | experiments/scenario-mappings/CS-005.yaml (DRAFT drafted as CS-006.yaml) | DRAFT. Must be FROZEN before START (experiments/README.md; protocol/equivalent-scenario-mapping-v1.md, section 6). | API -> WEB | E07 |
| CS-006 | not drafted | Proposed (design-brief-draft.md, section 5). HUMAN DECISION whether to draft it. | WEB -> API | E07 |

Gate: every canonical scenario the campaign uses is FROZEN and approved by an explicit human decision, one change-log row per record (protocol/change-control-v1.md, section 5). Human decision on DP-1 to DP-9 (CS-006.yaml, notes) is a precondition of the freeze.

## 2. Pinned SUT versions

Values are copied from manifests/sut-manifest.yaml (ORCHESTRATOR pins). Presence values are E01 facts; they are not pins. Provenance of "evaluated_version_frozen" is set at the E03 START; E07 needs its own START record.

| sut_id | Surfaces in scope | Repository and pin | Release | Notes |
|---|---|---|---|---|
| SUT-01 | web, api | gsanchezm/OmniPizza, commit 9ca37674d374e9303912e259641ee86baf3aabe1 (default branch main) | none | web and api from one commit |
| SUT-02 | (web only; api ABSENT) | web: saucelabs/sample-app-web, commit 60fdd634bb111c092282fa07977513a0a7765593 | none | Not in any E07 pair (NOT_COMPARABLE). |
| SUT-03 | web, api | browserstack/browserstack-demo-app, commit 7ab934d733f2f74d4b912e94e86f59ae0f6b7609 (branch master) | none | web and api served by one Next.js process |
| SUT-04 | web, api | mwinteringham/restful-booker-platform, commit d36bd3f8647a091d406e53bad463c5e3e5d2ece1 | release tag 2.2 (no assets) | web and api from one monorepo |
| SUT-05 | web, api | juice-shop/juice-shop, commit 1618a611b173b4bf114028e6e02549950606e29d | release v20.2.0 | GitHub Actions route: packaged distribution of v20.2.0 (release commit 5658473c..., manifest note); E03 precedent |
| SUT-06 | (web and api ABSENT) | webdriverio/native-demo-app (mobile only) | v2.2.0 | Not in scope |

Ecosystem versions must match the mapping record's version (protocol/equivalent-scenario-mapping-v1.md, section 6). If a pin changes, the mapping is re-validated and re-frozen.

## 3. Toolchain versions

Source: manifests/toolchain-manifest.yaml. Every entry is a pin for this campaign, not an install record; install_date and platform are recorded per run.

| Role | Tool | Pin | Status |
|---|---|---|---|
| Web runner | Playwright for Python | 1.63.0 (also pinned by experiments/E03-resetability/executor/requirements.txt, with hashes) | The toolchain notes say DRAFT until START. Chromium build is not hash-pinned; its version is recorded per run. |
| API client | Python 3 standard library (urllib.request) | runner python3 (3.12 series at preparation) | exact version recorded per run |
| Schema validation | Ajv, major 8 | version: null (not installed) | HUMAN DECISION: exact version and the date-time format plugin, before the first validation. The E03 measured workflow is the reference for the validation step. |
| Analysis runtime | Node.js | v23.6.1 (toolchain-manifest.yaml, scripting_runtime) | used only for analysis |
| Mobile runner | none | not applicable (web/API scope) | |

## 4. Prompt version(s)

| Item | Value |
|---|---|
| Executor role | None. Under protocol/agent-governance-v5.md (Section 3.6) and CAMPAIGN-CI-WRITE-AUTH-01, the ORCHESTRATOR performs E07 coordination. No executor role exists for E07. |
| Dispatch procedure prompt | HUMAN DECISION: to be written and frozen before START. E03 precedent: prompts/frozen/ORCHESTRATOR-E03-resetability-v1.md. |
| Prompt version | HUMAN DECISION (value not assigned). |
| Implementation | Not written. Recommended: a new implementation under experiments/E07-cross-layer-continuity/ (its own hash, not the E03 hash). Reuse by copy, not by import at run time (design-brief-draft.md, section 12). |

## 5. Conditions and their environment types

A condition is (sut_id, canonical_scenario_id, direction). Condition IDs are candidate, not frozen. Every condition in this table is NOT_STARTED. "Environment type" follows protocol/study-design-v1.md, section 10.1; establishment writes state, so every condition needs a controlled instance and is never PUBLIC_HOSTED (section 10.3).

| condition_id (candidate) | canonical_scenario_id | sut_id | source_layer -> verification_layer | Mapping comparability | environment_type (proposed) | N | Status |
|---|---|---|---|---|---|---|---|
| E07-CS004-SUT01-API-WEB | CS-005 | SUT-01 | api -> web | COMPARABLE (recommended; HUMAN DECISION at freeze) | SELF_HOSTED per component (E03 precedent for GitHub Actions instances; HUMAN DECISION to confirm) | 50 | NOT_STARTED |
| E07-CS004-SUT04-API-WEB | CS-005 | SUT-04 | api -> web | HUMAN DECISION (DP-7) | SELF_HOSTED per component (proposed) | 50 | NOT_STARTED; blocked on DP-7 |
| E07-CS004-SUT05-API-WEB | CS-005 | SUT-05 | api -> web | HUMAN DECISION (DP-7); recommended NOT_COMPARABLE | SELF_HOSTED per component (proposed) | 50 | NOT_STARTED; blocked on DP-7 |
| E07-CS004-SUT03-API-WEB | CS-005 | SUT-03 | api -> web | NOT_COMPARABLE (proposed; DP-4) | not applicable | 0 | NO DATA: NOT_COMPARABLE (section 9) |
| E07-CS004-SUT02-API-WEB | CS-005 | SUT-02 | api -> web | NOT_COMPARABLE (NO_APPLICABLE_SURFACE) | not applicable | 0 | NO DATA: NOT_COMPARABLE (section 9) |
| E07-CS004-SUT06-API-WEB | CS-005 | SUT-06 | api -> web | NOT_COMPARABLE (NO_APPLICABLE_SURFACE) | not applicable | 0 | NO DATA: NOT_COMPARABLE (section 9) |
| E07-CS005-SUT04-WEB-API | CS-006 (not drafted) | SUT-04 | web -> api | Candidate; needs CS-006 record | SELF_HOSTED per component (proposed) | 50 | Candidate, only if CS-006 is drafted and frozen |
| E07-CS005-SUT01-WEB-API | CS-006 (not drafted) | SUT-01 | web -> api | Evidence gap: no E01 row for web-established state read through the API | SELF_HOSTED per component (proposed) | 50 | Blocked on evidence (HUMAN DECISION) |
| E07-CS005-SUT05-WEB-API | CS-006 (not drafted) | SUT-05 | web -> api | Evidence gap: no E01 row for web add-to-basket | SELF_HOSTED per component (proposed) | 50 | Blocked on evidence (HUMAN DECISION) |
| E07-CS005-SUT03-WEB-API | CS-006 (not drafted) | SUT-03 | web -> api | NOT_COMPARABLE (cart client-side; SUT03-EV-0032) | not applicable | 0 | NO DATA: NOT_COMPARABLE |

Note on SUT-03 and CONFIRMATORY evaluability: under DP-4 option (a) (strict), no SUT-03 condition exists in CS-005 or CS-006; see section 13.

## 6. Sample size

| Item | Value | Source |
|---|---|---|
| N per condition | 50 | protocol/repeatability-determinism-v1.md, section 3 (standard target); protocol/statistical-analysis-plan-v1.md, section 4.1 |
| Reduced N = 30 | not applicable | Reserved for expensive mobile conditions (repeatability section 3). E07 has no mobile condition in scope. |
| Justification of N | Standard target; no reduction. | |
| Power or minimum detectable difference | not stated in the SAP. HUMAN DECISION: pre-register a minimum detectable difference, or accept descriptive interpretation only. Arithmetic for orientation only, not a protocol value: at N = 50 per arm, a 95% Wald half-width for one proportion near 0.5 is about 0.14, and for a risk difference between two arms of 50 it is about 0.20. | arithmetic on section 6 values |
| Restart rule | No attempt is re-run to replace another. A further attempt needs an explicit dispatch instruction (CAMPAIGN-CI-WRITE-AUTH-01; repeatability section 5, rule 5). | |

## 7. Exclusion and attribution rules (proposal for freeze)

Common base: protocol/repeatability-determinism-v1.md, section 5, rules 4 to 6 (failures are outcomes; no attempt is discarded; interruptions are recorded). The E04/E05 attribution rule is DEFERRED to those campaigns (protocol/study-design-v1.md, section 13, issue (xix)); E07 needs its own rule, frozen in this configuration (protocol/statistical-analysis-plan-v1.md, section 4.2, rule 3; protocol/repeatability-determinism-v1.md, section 6).

| Rule | Text (proposed) | Status |
|---|---|---|
| X-1 | No valid measured attempt is excluded for any reason. | Proposed |
| X-2 | Each attempt has exactly one outcome category, fixed before START: VERIFIED, NOT_VERIFIED, ESTABLISHMENT_FAILED, INTERRUPTED, RUNNER_ERROR. | Proposed. HUMAN DECISION on the category set. |
| X-3 | VERIFIED: every declared identity key and attribute is observed on the verification layer and matches the establishment record. NOT_VERIFIED: the verification completed and at least one key or attribute is absent or different. ESTABLISHMENT_FAILED: the establishment check on the source layer did not confirm the unit. | Proposed |
| X-4 | A failed declared-starting-state check is recorded as INTERRUPTED with its cause. The reset is repeated before the next attempt. The attempt is kept. | Proposed (follows the E03 ABORTED convention, not its exclusion) |
| X-5 | RUNNER_ERROR (tool, browser, or infrastructure fault inside a run) is counted in every primary rate. A sensitivity table without RUNNER_ERROR is reported as EXPLORATORY. | HUMAN DECISION (alternative: exclude with an attribution record, which needs a frozen attribution criterion) |
| X-6 | Cell-level no-data states are not attempts: NOT_COMPARABLE (mapping decision), NOT_APPLICABLE_STRUCTURAL (a surface absent in the evaluated version), NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE (environment). Each is reported as "no data" with its reason, never as a zero or as a failure (protocol/study-design-v1.md, section 11, rule 9; protocol/statistical-analysis-plan-v1.md, section 5). | Proposed |
| X-7 | Continuity proportion denominator. Option A: VERIFIED / all valid measured attempts (recommended for H4). Option B: VERIFIED / attempts whose establishment succeeded (reported descriptively). Both are fixed here before START. | HUMAN DECISION (DP-8) |

## 8. Run manifest and identifiers

| Item | Value |
|---|---|
| Schema | schemas/run-manifest.schema.v2.json. source_layer and verification_layer use the lowercase enumeration web, api, android, ios (schema lines 479 to 506). |
| Campaign convention | source_layer and verification_layer are mandatory on every E07 run record (the schema keeps them optional). actions[].outcome is mandatory on every action (campaign convention; the schema description). establishment_mechanisms is recommended (optional at schema level). |
| Traceable identity keys | Set per condition, before START. Candidates: SUT-01: session sid (JWT claim) and the cart line (pizza_id, size, quantity). SUT-04: run-unique guest names and check-in date, and bookingid. SUT-05: basket id and ProductId, quantity. Each key must be observable on the verification layer; a key that is not observable there cannot be used. HUMAN DECISION (DP-5). |
| Run-unique values | Derived from the run identifier and written to a precondition record before the first action (E03 precedent: experiments/E03-resetability/executor/README.md, section 4.5 and section 4.6). |

## 9. Pair-level absence records

Required by experiments/E07-cross-layer-continuity/README.md ("Explicit record for every layer pair that is absent, not applicable, or not testable, with reason"). They are not run manifests and are not counted as attempts.

| Record | canonical_scenario_id | sut_id | Direction | Status | Reason | Evidence |
|---|---|---|---|---|---|---|
| A-1 | CS-005 | SUT-02 | api -> web | NOT_COMPARABLE | NO_APPLICABLE_SURFACE (API absent) | SUT02-EV-0004 to SUT02-EV-0006 |
| A-2 | CS-005 | SUT-06 | api -> web | NOT_COMPARABLE | NO_APPLICABLE_SURFACE (WEB and API absent) | manifests/sut-manifest.yaml, SUT-06 notes |
| A-3 | CS-005 | SUT-03 | api -> web | NOT_COMPARABLE (proposed; DP-4) | OTHER: no API-established persistent state | SUT03-EV-0006 to -0008, -0031 |
| A-4 | CS-006 | SUT-02 | web -> api | NOT_COMPARABLE | NO_APPLICABLE_SURFACE (API absent) | SUT02-EV-0004 to SUT02-EV-0006 |
| A-5 | CS-006 | SUT-06 | web -> api | NOT_COMPARABLE | NO_APPLICABLE_SURFACE | manifests/sut-manifest.yaml |
| A-6 | CS-006 | SUT-03 | web -> api | NOT_COMPARABLE (proposed) | ORACLE_CLASS_UNOBSERVABLE (client-side cart never reaches the API) | SUT03-EV-0032 |
| A-7 | CS-005 | SUT-05 | api -> web | Pending DP-7 | evidence gap (web basket) | not applicable yet |

Each absence record keeps the E01 structural_scope_note of its cell (protocol/capability-rubric-v1.md; protocol/study-design-v1.md, section 11, rule 2). No absence record changes a capability score.

## 10. Environment verification status (controlled instances)

Source: experiments/E03-resetability/controlled-instance-status.yaml (latest-run rule), and experiments/E03-resetability/README.md. E03 verified the instances, not the E07 realizations. E07 needs its own environment verification (non-measured, labeled ENVIRONMENT_VERIFICATION) for each new realization step (experiments/README.md, "Common rules", execution substrate bullet).

| Surface | E03 status (as recorded) | E07 requirement |
|---|---|---|
| SUT-01 web and api | VERIFIED on GitHub Actions (E03-CS001-SUT01-WEB, -SUT01-API) | Realization check of the CS-005 steps (token injection, Checkout read-through) |
| SUT-04 web and api | VERIFIED on GitHub Actions (E03-CS001-SUT04-WEB, -SUT04-API) | Realization check, including the admin listing (not verified by E03) and the cookie decision (DP-7) |
| SUT-05 api | VERIFIED on GitHub Actions (run 37354458611, manifest note) | Realization check of the basket steps |
| SUT-05 web | NO RECORD (E03 mapped SUT-05 on the API surface only) | Required only if SUT-05 is COMPARABLE on CS-005 or CS-006 |
| SUT-03 web | VERIFIED (E03-CS001-SUT03-WEB) | Not required while SUT-03 is NOT_COMPARABLE |
| SUT-03 api | NO RECORD (E03 mapped SUT-03 on the WEB surface only: CS-001.yaml, SUT-03 surfaces_used [WEB]) | Required only if SUT-03 is reopened under DP-4 option (b) |

## 11. Execution substrate and workflow gates (names only)

Execution: GitHub Actions under ORCHESTRATOR coordination (CAMPAIGN-CI-WRITE-AUTH-01; experiments/README.md, execution substrate bullet). Local runs are DEVELOPMENT, SYNTAX_VALIDATION, TOOL_QUALIFICATION, SMOKE, ENVIRONMENT_VERIFICATION, or DRY_RUN only, and never enter raw-data/. No workflow exists yet; authoring one authorizes no execution.

| Gate (proposed name) | Checks (names only) | Model in E03 |
|---|---|---|
| E07-G-01 | campaign START record present with its human authorization id | E03 G-1 |
| E07-G-02 | configuration locked (this file, once approved) | E03 G-2 |
| E07-G-03 | every canonical scenario used is FROZEN and active (CS-005; CS-006 if used) | E03 G-3 (and G-4 for excluded scenarios) |
| E07-G-04 | pair-level absence records (section 9) present for every NOT_COMPARABLE cell | new |
| E07-G-05 | run-manifest schema validation with source_layer and verification_layer | E03 G-5 |
| E07-G-06 | frozen agent governance in force | E03 G-6 |
| E07-G-07 | mobile gate: fails closed if any mobile cell is configured (none is in scope) | E03 G-7 |
| E07-G-08 | controlled instance verified on GitHub Actions for each surface of each condition | E03 G-8 |
| E07-G-09 | frozen dispatch prompt | E03 G-9 |
| E07-G-10 | frozen implementation hash | E03 G-10 |
| E07-G-11 | pinned repository commit, workflow revision, and toolchain | E03 G-11 |
| E07-G-12 | per-SUT dispatch authorization (HUMAN DECISION; the governance successor that gives this per-SUT authorization is not yet written) | new |
| E07-G-13 | isolation: the job checks out only its own SUT's raw-data subtree | CAMPAIGN-CI-WRITE-AUTH-01 |
| E07-G-14 | first attempt only; default branch only | CAMPAIGN-CI-WRITE-AUTH-01 |

Raw data: raw-data/E07-cross-layer-continuity/<SUT>/** for MEASURED_EXPERIMENT artifacts only (raw-data/README.md). Import by the ORCHESTRATOR after verification against the GitHub digest.

## 12. Authorizations and dates

| Item | Value |
|---|---|
| Campaign START | Not issued. HUMAN DECISION (protocol/change-control-v1.md, section 7). |
| Configuration freeze | Not proposed yet. |
| Dispatch | Each dispatch needs its own explicit human approval, recorded before the run (CAMPAIGN-CI-WRITE-AUTH-01). |
| Schedule | DATA FREEZE 2027-01-05 (task brief of 2026-11-05; not re-verified against manifests/planning-deadlines-v2.yaml). The E07 evidence decisions (DP-4, DP-7) are on the critical path. |

## 13. CONFIRMATORY comparisons

Source: protocol/statistical-analysis-plan-v1.md, section 4.2 and section 4.3 (H4 row: variable "continuity success proportion per layer pair (E07)"; pairs SUT-01 vs SUT-02 and SUT-01 vs SUT-03; method "risk difference with interval; Fisher's exact test where applicable"). Each comparison must be pre-registered in this configuration before START, with its exact specification (SAP, section 4.2, classification rule 3).

| Comparison id (candidate — not frozen) | Hypothesis | Ecosystem pair | Scenario and direction | Evaluability today |
|---|---|---|---|---|
| CONFIRMATORY (H4), E07-A | H4 | SUT-01 vs SUT-02 | CS-005, API -> WEB | NOT EVALUABLE: SUT-02 is NOT_COMPARABLE (A-1). Report side by side with reason. |
| CONFIRMATORY (H4), E07-B | H4 | SUT-01 vs SUT-03 | CS-005, API -> WEB | NOT EVALUABLE under DP-4 option (a): SUT-03 is NOT_COMPARABLE (A-3). |
| CONFIRMATORY (H4), E07-C | H4 | SUT-01 vs SUT-02 | CS-006, WEB -> API | NOT EVALUABLE: SUT-02 has no API (A-4). |
| CONFIRMATORY (H4), E07-D | H4 | SUT-01 vs SUT-03 | CS-006, WEB -> API | NOT EVALUABLE under DP-4 option (a) (A-6). |

Open items for this section (HUMAN DECISIONS):
- Whether E07-A to E07-D are registered as four comparisons, or as H4 with two directions (the SAP does not number them).
- Holm family: SAP section 4.2 applies Holm across the CONFIRMATORY comparisons of one research question. RQ4 also contains the E06 H4 parity comparisons, so the family must be defined across E06 and E07. Recommendation: list only evaluable comparisons in the family, and state the non-evaluable ones explicitly.
- Interval method for the risk difference: SAP section 3 specifies a risk difference "with its 95% confidence interval" but does not name the method (Wilson is named only for single proportions). Recommendation: a Newcombe-type hybrid score interval built from the Wilson intervals, fixed here. HUMAN DECISION.
- Specialists: any SUT-04 or SUT-05 comparison is EXPLORATORY unless pre-registered (SAP section 4.2, rules 1 and 3; the E03 README's CONFIRMATORY section takes the same position for E03).

## 14. Summary of HUMAN DECISIONS in this file

1. Section 1: approval of CS-005 (after DP-1 to DP-9), and whether to draft CS-006.
2. Section 3: Ajv version and format handling before the first validation.
3. Section 4: dispatch procedure prompt, its version, and the implementation hash.
4. Section 5: comparability of SUT-01, SUT-04 and SUT-05 on CS-005 (DP-7); environment type of the conditions.
5. Section 6: whether to pre-register a minimum detectable difference.
6. Section 7: X-2 category set, X-5 treatment of RUNNER_ERROR, X-7 continuity denominator (DP-8).
7. Section 8: identity keys per ecosystem (DP-5).
8. Section 11: the per-SUT dispatch authorization mechanism (governance successor, not yet written).
9. Section 12: campaign START.
10. Section 13: comparison identifiers, Holm family across E06 and E07, risk-difference interval method.
