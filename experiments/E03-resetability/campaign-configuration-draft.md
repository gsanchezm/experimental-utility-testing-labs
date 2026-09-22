# E03-resetability — DRAFT Campaign Configuration (PRE-START)

| Field | Value |
|---|---|
| Prepared by | ORCHESTRATOR |
| Date | 2026-09-21 (updated after Issue (xviii) human ruling and canonical-scenario catalogue completion); corrected 2026-09-22 (CS-002 excluded from the campaign by human ruling `E03-CS002-EXCLUSION-RULING-01`, `manifests/e03-cs002-exclusion-v1.yaml`; active catalogue = CS-001 only) |
| Authorization | Human-selected E03-resetability as next campaign for PRE-START preparation only (2026-09-21); Issue (xviii) human ruling (`ISSUE-XVIII-RULING-01`) and E03 configuration-completion instruction (2026-09-21). Neither authorizes campaign start, execution, mobile qualification execution, or executor launch. |
| Status of this document | **DRAFT. This is NOT the "Campaign configuration" record of experiments/README.md / protocol/change-control-v1.md, section 7.** That record is written, under that exact heading, in this campaign's own README.md, only at campaign start (NOT_STARTED -> IN_PROGRESS), on its own separate explicit human instruction. This document is a preparatory draft, positioned so a future, separately authorized campaign-start operation can promote it (with the blockers below resolved) with minimal rework. |

## 0. Blockers to promoting this draft into a real campaign-start "Campaign configuration" record

1. ~~protocol/study-design-v1.md, section 13, issue (xviii)~~ — **RESOLVED 2026-09-21** (`ISSUE-XVIII-RULING-01`; `protocol/setup-effort-v2.md`). No longer a blocker; Required Actions can now be counted and are reflected in both mapping records.
2. ~~protocol/unresolved.md, PROTO-U08~~ — **RESOLVED 2026-09-21** as DUPLICATE_OR_ALREADY_RESOLVED_CONCERN, non-blocking. The underlying fact (no SUT's `controlled_instance_available` was verified in E01) remains true and still means every condition below is, today, `NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE` pending provisioning (`experiments/E03-resetability/controlled-instance-determination.md`) — but this is a campaign-configuration-lock-time gate (§10.3), not a mapping-freeze or draft-preparation blocker.
3. ~~`experiments/scenario-mappings/CS-001.yaml`~~ — **FROZEN 2026-09-21** (`E03-CS001-FREEZE-AUTH-01`); the sole accepted canonical scenario for the current E03 campaign version. `experiments/scenario-mappings/CS-002.yaml` (FROZEN 2026-09-21, `E03-CS002-FREEZE-AUTH-01`) was **EXCLUDED_FROM_CAMPAIGN on 2026-09-22** by explicit human ruling (`E03-CS002-EXCLUSION-RULING-01`; `protocol/CHANGELOG.md`; `protocol/unresolved.md`, PROTO-U09): its intent was generalized from SUT-06-specific E01 evidence, contrary to `protocol/equivalent-scenario-mapping-v1.md`, section 6. The file is preserved unchanged and is not an input to this configuration (`experiments/E03-resetability/canonical-scenario-catalogue.md`).
4. ~~No condition is verified `CONTROLLED`~~ — **provisioning authorized and performed 2026-09-22** (NON-MEASURED PRE-START): 8 of 9 conditions are `CONTROLLED` on the operator workstation (LOCAL / EMULATED); `E03-CS001-SUT02-IOS` remains `NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE` on this host (`experiments/E03-resetability/controlled-instance-determination.md`, `controlled-instance-status.yaml`). No condition is measured-execution-ready: the GitHub Actions environment verification has not run for any condition, and the gates below remain.
5. Toolchain versions are all `null` in `manifests/toolchain-manifest.yaml` (nothing installed) — ordinary pre-execution state.
6. No agent prompt exists for an E03 executor role — prompt authoring and freeze remain explicitly out of scope (Gate G8).
7. ~~CI/CD measured-execution model is BLOCKED~~ — **resolved 2026-09-22** by human decision: GitHub Actions selected; `.github/workflows/**` granted to ORCHESTRATOR (`E03-CI-WRITE-AUTH-01`, AGENT-INSTRUCTIONS.md); the four workflows exist and the measured one fails closed (`experiments/E03-resetability/ci-cd-execution-model.md`); schema gap resolved by `schemas/run-manifest.schema.v2.json` (`actions[].outcome`, mandatory by campaign convention). Remaining before START: governance v2 freeze, GitHub Actions environment verification per condition, mobile qualification, executor prompt and implementation freeze, and the public-repository push mode (`PUBLIC-EXPORT-MANIFEST.yaml`).

None of the above blocks this draft's own completeness; items 5–6 and the remaining gates named in items 4 and 7 block only promotion to a locked, executable campaign-start record.

## 1. Canonical scenario ids and mapping records

One FROZEN, accepted scenario, covering every SUT with an explicit COMPARABLE/NOT_COMPARABLE entry (`experiments/E03-resetability/canonical-scenario-catalogue.md`):

| SUT | CS-001 (business-object establish-then-reset) |
|---|---|
| SUT-01 OmniPizza | COMPARABLE — WEB, API — cart |
| SUT-02 Sauce Labs Demo Ecosystem | COMPARABLE — WEB, ANDROID, IOS — cart |
| SUT-03 BrowserStack Demo Ecosystem | COMPARABLE — WEB — cart (client-side only) |
| SUT-04 Restful Booker Platform | COMPARABLE — WEB, API — booking |
| SUT-05 OWASP Juice Shop | COMPARABLE — API — basket |
| SUT-06 WebdriverIO Native Demo App | NOT_COMPARABLE (NO_EQUIVALENT_INTENT) — remains in the six-SUT population; no measured condition in this configuration |

CS-002 (`experiments/scenario-mappings/CS-002.yaml`) is **not** a mapping record of this configuration: EXCLUDED_FROM_CAMPAIGN 2026-09-22 (Section 0, item 3). This population and these surface subsets come from already-adjudicated, FROZEN E01 evidence — this is mapping support (comparability rule condition 1), not tailoring E03's population to E01 scores (verified in the E03 PRE-START integrity audit, Part B: `SCOPE_COMPLIANT`).

## 2. Pinned SUT versions

Per `manifests/sut-manifest.yaml` (pinned 2026-09-16 by ORCHESTRATOR, unchanged). `evaluated_version_frozen: false` for all six — unchanged; flipping it is a campaign-start-adjacent action outside this operation's scope.

## 3. Toolchain versions

`manifests/toolchain-manifest.yaml`: unchanged. All versions remain `null`; nothing is installed. Mobile runner: Mobilewright remains candidate, qualification NOT_STARTED (Section 7).

## 4. Prompt version id(s)

None. No E03 executor prompt exists in `prompts/working/` or `prompts/frozen/`. Prompt authoring and freeze remain explicitly excluded from this operation.

## 5. Conditions, environment_type, NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE

One condition per (COMPARABLE SUT × surface-used) combination in the sole accepted scenario CS-001, reset direction only (establish is E02's concern); recomputed from the frozen record on 2026-09-22. Reset mechanisms and Required Actions counts are concrete (`experiments/scenario-mappings/CS-001.yaml`); `environment_type` / executability remain the one genuinely open axis, per `experiments/E03-resetability/controlled-instance-determination.md`.

| Condition id | SUT | Scenario | Surface | Reset mechanism | Required Actions (reset) | environment_type | Executable today? |
|---|---|---|---|---|---|---|---|
| E03-CS001-SUT01-WEB | SUT-01 | CS-001 | WEB | API_RESET / SESSION_RESET | 2 | LOCAL verified 2026-09-22 (SELF_HOSTED on GitHub-hosted runners) | CONTROLLED (workstation); measured execution NOT_READY (GitHub Actions verification pending, other gates) |
| E03-CS001-SUT01-API | SUT-01 | CS-001 | API | API_RESET / SESSION_RESET | 2 | LOCAL verified 2026-09-22 (SELF_HOSTED on GitHub-hosted runners) | CONTROLLED (workstation); measured execution NOT_READY |
| E03-CS001-SUT02-WEB | SUT-02 | CS-001 | WEB | APP_DATA_CLEAR | 2 | LOCAL verified 2026-09-22 (SELF_HOSTED on GitHub-hosted runners) | CONTROLLED (workstation); measured execution NOT_READY |
| E03-CS001-SUT02-ANDROID | SUT-02 | CS-001 | ANDROID | APP_DATA_CLEAR | 3 | EMULATED verified 2026-09-22 | CONTROLLED (workstation emulator); measured execution NOT_READY; mobile-qualification-gated (NOT_STARTED) |
| E03-CS001-SUT02-IOS | SUT-02 | CS-001 | IOS | APP_DATA_CLEAR | 3 | SIMULATED attempted 2026-09-22, NOT verified (host simulator service unresponsive) | NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE; mobile-qualification-gated (NOT_STARTED); designated route: GitHub Actions macos-15 job |
| E03-CS001-SUT03-WEB | SUT-03 | CS-001 | WEB | SESSION_RESET | 2 | LOCAL verified 2026-09-22 (SELF_HOSTED on GitHub-hosted runners) | CONTROLLED (workstation); measured execution NOT_READY |
| E03-CS001-SUT04-WEB | SUT-04 | CS-001 | WEB | API_RESET | 2 | LOCAL verified 2026-09-22 (SELF_HOSTED via docker-compose on GitHub-hosted runners) | CONTROLLED (workstation); measured execution NOT_READY |
| E03-CS001-SUT04-API | SUT-04 | CS-001 | API | API_RESET | 2 | LOCAL verified 2026-09-22 (SELF_HOSTED on GitHub-hosted runners) | CONTROLLED (workstation); measured execution NOT_READY |
| E03-CS001-SUT05-API | SUT-05 | CS-001 | API | ENVIRONMENT_RESTART | 2 | LOCAL verified 2026-09-22 incl. stop/start (SELF_HOSTED on GitHub-hosted runners) | CONTROLLED (workstation); measured execution NOT_READY |

**Nine candidate conditions**, all on CS-001. The two CS-002-derived rows of the 2026-09-21 draft (`E03-CS002-SUT06-ANDROID`, `E03-CS002-SUT06-IOS`) are removed by the 2026-09-22 ruling and are not candidate conditions; SUT-06 remains in the population without a measured condition. Every condition requires deterministic reset (`protocol/study-design-v1.md` §10.3) and is therefore never executed against PUBLIC_HOSTED. As of 2026-09-22, 8 of 9 conditions have a verified controlled instance on the operator workstation and 1 does not (`experiments/E03-resetability/controlled-instance-status.yaml`); none is measured-execution-ready. No condition was added to maximize coverage and none removed to avoid mobile qualification — every row traces to a COMPARABLE mapping entry on real evidence.

## 6. Sample size per condition

Candidate default only, not locked: N = 50 per condition where operationally feasible (`protocol/repeatability-determinism-v1.md` §3), N = 30 for the two mobile conditions (`E03-CS001-SUT02-ANDROID`, `-IOS`) only with a written justification recorded before execution — none is recorded yet, so N = 50 is the default absent that justification. No sample size is locked because campaign start has not occurred.

## 7. Mobile qualification applicability

**REQUIRED** — covering **two** condition rows: `E03-CS001-SUT02-ANDROID`, `E03-CS001-SUT02-IOS` (the two CS-002-derived SUT-06 rows of the 2026-09-21 draft are no longer part of the configuration). Mobilewright must pass the qualification gate (`protocol/mobile-runner-policy-v1.md` §§2–7) — or the study switches to Appium 3 under §8 — before either row can execute; SUT-02 must additionally pass its own per-SUT compatibility smoke (§9). Neither the gate nor any smoke is executed by this operation.

## 8. Exclusion and attribution rules

None defined beyond the frozen E03/setup-effort discipline. No E03-specific exclusion or attribution rule is introduced.

## 9. CONFIRMATORY comparisons

Per `protocol/statistical-analysis-plan-v1.md` §4.3, row H2, and `manifests/study-manifest.yaml`'s `comparison_classification.confirmatory_pairs`: SUT-01 vs SUT-02 and SUT-01 vs SUT-03, on Required Actions (reset) per COMPARABLE canonical scenario. Both pairs are COMPARABLE on CS-001, the sole accepted scenario; the CS-002 exclusion does not touch either pair (SUT-01 was NOT_COMPARABLE on CS-002). Required Actions can now actually be counted (Issue (xviii) resolved) once a condition becomes executable. No comparison involving SUT-04, SUT-05, or SUT-06 is pre-registered CONFIRMATORY; all remain EXPLORATORY / contextual (`protocol/statistical-analysis-plan-v1.md` §4.2).

## 10. Unit of evaluation

The testing laboratory ecosystem (`manifests/sut-manifest.yaml`, `unit_of_comparison`). All six SUTs evaluated under identical rules on CS-001; SUT-06's NOT_COMPARABLE marking is a scenario-level finding, not an exclusion from E03 (`protocol/study-design-v1.md` §11, rule 9).

## 11. Modalities / dimensions informed

Experimental Controllability; Setup Effort (`protocol/study-design-v1.md` §4). RQ2 (primary). No other dimension or RQ is claimed.

## 12. CI/CD measured-execution substrate

**GitHub Actions** (human decision 2026-09-22; AGENT-INSTRUCTIONS.md, `E03-CI-WRITE-AUTH-01`). Every MEASURED_EXPERIMENT runs through `.github/workflows/e03-measured-execution.yml`, which fails closed on every campaign gate; local executions are non-measured only. Run manifests conform to `schemas/run-manifest.schema.v2.json` with `actions[].outcome` mandatory on every action record. Model, guards, reproducibility contract, attempt immutability, artifact retention and import: `experiments/E03-resetability/ci-cd-execution-model.md`. Publication mode of the repository the workflows run in: `PUBLIC-EXPORT-MANIFEST.yaml`.

## Current status

DRAFT / PRE-START. Not the campaign's locked "Campaign configuration" record. Campaign status in `manifests/study-manifest.yaml` remains `NOT_STARTED`.
