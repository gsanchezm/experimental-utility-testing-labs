# E03-resetability — DRAFT Campaign Configuration (PRE-START)

| Field | Value |
|---|---|
| Prepared by | ORCHESTRATOR |
| Date | 2026-09-21 (updated after Issue (xviii) human ruling and canonical-scenario catalogue completion); corrected 2026-09-22 (CS-002 excluded from the campaign by human ruling `E03-CS002-EXCLUSION-RULING-01`, `manifests/e03-cs002-exclusion-v1.yaml`; active catalogue = CS-001 only); sections 3 and 4 updated 2026-10-06 (operation OP-PREP-E03); sections 0, 2, 5, 6, 7 and the current status refreshed 2026-10-26 (operation OP-LOCK-01: the stale statements of the pre-verification state replaced by the state recorded at that date; no value of the campaign is chosen by this refresh) |
| Authorization | Human-selected E03-resetability as next campaign for PRE-START preparation only (2026-09-21); Issue (xviii) human ruling (`ISSUE-XVIII-RULING-01`) and E03 configuration-completion instruction (2026-09-21). Neither authorizes campaign start, execution, mobile qualification execution, or executor launch. |
| Status of this document | **DRAFT. This is NOT the "Campaign configuration" record of experiments/README.md / protocol/change-control-v1.md, section 7.** That record is written, under that exact heading, in this campaign's own README.md, only at campaign start (NOT_STARTED -> IN_PROGRESS), on its own separate explicit human instruction. This document is a preparatory draft, positioned so a future, separately authorized campaign-start operation can promote it (with the blockers below resolved) with minimal rework. |

## 0. Blockers to promoting this draft into a real campaign-start "Campaign configuration" record

1. ~~protocol/study-design-v1.md, section 13, issue (xviii)~~ — **RESOLVED 2026-09-21** (`ISSUE-XVIII-RULING-01`; `protocol/setup-effort-v2.md`). No longer a blocker; Required Actions can now be counted and are reflected in both mapping records.
2. ~~protocol/unresolved.md, PROTO-U08~~ — **RESOLVED 2026-09-21** as DUPLICATE_OR_ALREADY_RESOLVED_CONCERN, non-blocking. The underlying fact (no SUT's `controlled_instance_available` was verified in E01) was addressed per condition by the provisioning and the GitHub Actions verification of item 4 (the determination is recorded in `experiments/E03-resetability/controlled-instance-determination.md`); it was a campaign-configuration-lock-time gate (§10.3), not a mapping-freeze or draft-preparation blocker.
3. ~~`experiments/scenario-mappings/CS-001.yaml`~~ — **FROZEN 2026-09-21** (`E03-CS001-FREEZE-AUTH-01`); the sole accepted canonical scenario for the current E03 campaign version. `experiments/scenario-mappings/CS-002.yaml` (FROZEN 2026-09-21, `E03-CS002-FREEZE-AUTH-01`) was **EXCLUDED_FROM_CAMPAIGN on 2026-09-22** by explicit human ruling (`E03-CS002-EXCLUSION-RULING-01`; `protocol/CHANGELOG.md`; `protocol/unresolved.md`, PROTO-U09): its intent was generalized from SUT-06-specific E01 evidence, contrary to `protocol/equivalent-scenario-mapping-v1.md`, section 6. The file is preserved unchanged and is not an input to this configuration (`experiments/E03-resetability/canonical-scenario-catalogue.md`).
4. ~~No condition is verified `CONTROLLED`~~ — **provisioning performed 2026-09-22** (NON-MEASURED PRE-START) and **verified on GitHub Actions** eight times since 2026-10-02. Under the latest run that ran a job for each condition (run 40361964609, 2026-10-26, target all, dry_run true) eight conditions are `CONTROLLED` and VERIFIED (the seven web/api conditions and `E03-CS001-SUT02-ANDROID`) and `E03-CS001-SUT02-IOS` is NOT_VERIFIED (its job was cancelled by GitHub without a runner; it was VERIFIED under three earlier runs; it is outside the scope of the planned manuscript and gate G-7 blocks it regardless); no condition carries `reverification_required` (`experiments/E03-resetability/controlled-instance-determination.md`, `controlled-instance-status.yaml`). No condition is measured-execution-ready before the campaign START and the gates below.
5. ~~Toolchain versions are all `null`~~ — the web runner (Playwright for Python 1.63.0) and the API client are pinned for the executable conditions (`manifests/toolchain-manifest.yaml`, `tools.web_runner` and `tools.api`; `experiments/E03-resetability/executor/requirements.txt`; operation OP-PREP-E03, 2026-10-06); the mobile-runner entries are unchanged and concern only the two blocked mobile conditions.
6. ~~No agent prompt exists for an E03 executor role~~ — a WORKING prompt exists since 2026-10-05 (`prompts/working/EXECUTOR-E03-RESETABILITY-E03-resetability-v1.md`, decision D3); its freeze to `prompts/frozen/` is a step of the campaign START, after a pre-freeze revision recorded in `manifests/e03-campaign-start-package-v1.yaml`.
7. ~~CI/CD measured-execution model is BLOCKED~~ — **resolved 2026-09-22** by human decision: GitHub Actions selected; `.github/workflows/**` granted to ORCHESTRATOR (`E03-CI-WRITE-AUTH-01`, AGENT-INSTRUCTIONS.md); the four workflows exist and the measured one fails closed (`experiments/E03-resetability/ci-cd-execution-model.md`); schema gap resolved by `schemas/run-manifest.schema.v2.json` (`actions[].outcome`, mandatory by campaign convention). Remaining before START: the confirmations of the lock package, the prompt freeze, and the lock of the implementation hash (`manifests/e03-campaign-start-package-v1.yaml`), then the START itself; governance v3 is in force (v2 was frozen 2026-09-22, v3 on 2026-10-03), the GitHub Actions verification is done (item 4), and the public repository must carry the START state (an export, `PUBLIC-EXPORT-MANIFEST.yaml`) before the first dispatch, because the gates of the measured workflow read the public tree.

None of the above blocks this draft's own completeness; the remaining gates named in items 4, 6, and 7 block only promotion to a locked, executable campaign-start record.

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

Per `manifests/sut-manifest.yaml` (pinned 2026-09-16 by ORCHESTRATOR; no pinned value changed; on 2026-10-02 the E01 presence values were transcribed and the never-pinned SUT-03 api provenance was filled from its web artifact, `manifests/sut-presence-transcription-v1.yaml`). `evaluated_version_frozen: false` for all six — unchanged; no definition of the flag exists (`manifests/sut-presence-transcription-v1.yaml`, C-5), it is set at a campaign's START, and the scope of that setting is an open item of `manifests/e03-campaign-start-package-v1.yaml`.

## 3. Toolchain versions

DRAFT, not frozen (operation OP-PREP-E03; `manifests/toolchain-manifest.yaml`, `tools.web_runner` and `tools.api`): web runner Playwright for Python 1.63.0, pinned with sha256 hashes by `experiments/E03-resetability/executor/requirements.txt` together with the runtime dependencies its metadata declares (pyee 13.0.1, greenlet 3.5.6, typing-extensions 4.16.0); Chromium downloaded by `playwright install chromium`, the build named by that version, its version recorded per run; API client the Python 3 standard library (`urllib.request`) of the runner's python3 (3.12 series on ubuntu-24.04), its exact version recorded per run; no third-party HTTP client. The pins are copied into the locked configuration at campaign START. Mobile runner: `tools.mobile_runner_selection` of `manifests/toolchain-manifest.yaml`, unchanged by that operation.

## 4. Prompt version id(s)

Candidate, DRAFT, not frozen: `EXECUTOR-E03-RESETABILITY-E03-resetability-v1`, the working prompt `prompts/working/EXECUTOR-E03-RESETABILITY-E03-resetability-v1.md` (operation OP-PREP-E03; human decisions of 2026-10-05, decision D3). Its freeze, a byte-identical copy under `prompts/frozen/`, is a step of the campaign START; no frozen E03 executor prompt exists.

## 5. Conditions, environment_type, NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE

One condition per (COMPARABLE SUT × surface-used) combination in the sole accepted scenario CS-001, reset direction only (establish is E02's concern); recomputed from the frozen record on 2026-09-22. Reset mechanisms and Required Actions counts are concrete (`experiments/scenario-mappings/CS-001.yaml`); `environment_type` and executability are recorded per condition in `experiments/E03-resetability/controlled-instance-status.yaml` (verified on GitHub Actions; section 0, item 4).

| Condition id | SUT | Scenario | Surface | Reset mechanism | Required Actions (reset) | environment_type | Executable today? |
|---|---|---|---|---|---|---|---|
| E03-CS001-SUT01-WEB | SUT-01 | CS-001 | WEB | API_RESET / SESSION_RESET | 2 | SELF_HOSTED (GitHub-hosted runner; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED on GitHub Actions; executable after the campaign START and the gates of the measured workflow |
| E03-CS001-SUT01-API | SUT-01 | CS-001 | API | API_RESET / SESSION_RESET | 2 | SELF_HOSTED (GitHub-hosted runner; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED on GitHub Actions; executable after the campaign START and the gates of the measured workflow |
| E03-CS001-SUT02-WEB | SUT-02 | CS-001 | WEB | APP_DATA_CLEAR | 2 | SELF_HOSTED (GitHub-hosted runner; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED on GitHub Actions; executable after the campaign START and the gates of the measured workflow |
| E03-CS001-SUT02-ANDROID | SUT-02 | CS-001 | ANDROID | APP_DATA_CLEAR | 3 | EMULATED (workstation emulator verified 2026-09-22; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED; BLOCKED from START and measurement by the study mobile-runner state (UNRESOLVED_AFTER_FALLBACK_FAILURE; gate G-7) |
| E03-CS001-SUT02-IOS | SUT-02 | CS-001 | IOS | APP_DATA_CLEAR | 3 | SIMULATED (GitHub Actions macos-15 job; VERIFIED under runs 37265782721, 38018788066, and 39316211051; NOT_VERIFIED under run 40361964609, whose job was cancelled without a runner) | CONTROLLED (GitHub Actions simulated instance; the workstation simulator stays unresponsive); BLOCKED by the mobile-runner state (gate G-7); a further verification dispatch needs its own explicit approval |
| E03-CS001-SUT03-WEB | SUT-03 | CS-001 | WEB | SESSION_RESET | 2 | SELF_HOSTED (GitHub-hosted runner; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED on GitHub Actions; executable after the campaign START and the gates of the measured workflow |
| E03-CS001-SUT04-WEB | SUT-04 | CS-001 | WEB | API_RESET | 2 | SELF_HOSTED (GitHub-hosted runner, the route of the SUT's README since operation OP-CI-06; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED on GitHub Actions; executable after the campaign START and the gates of the measured workflow |
| E03-CS001-SUT04-API | SUT-04 | CS-001 | API | API_RESET | 2 | SELF_HOSTED (GitHub-hosted runner; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED on GitHub Actions; executable after the campaign START and the gates of the measured workflow |
| E03-CS001-SUT05-API | SUT-05 | CS-001 | API | ENVIRONMENT_RESTART | 2 | SELF_HOSTED (GitHub-hosted runner; the packaged distribution of the pinned release, stop and start included; verified on GitHub Actions, run 40361964609) | CONTROLLED and VERIFIED on GitHub Actions; executable after the campaign START and the gates of the measured workflow |

**Nine candidate conditions**, all on CS-001. The two CS-002-derived rows of the 2026-09-21 draft (`E03-CS002-SUT06-ANDROID`, `E03-CS002-SUT06-IOS`) are removed by the 2026-09-22 ruling and are not candidate conditions; SUT-06 remains in the population without a measured condition. Every condition requires deterministic reset (`protocol/study-design-v1.md` §10.3) and is therefore never executed against PUBLIC_HOSTED. Per the status record and its latest-run rule (`experiments/E03-resetability/controlled-instance-status.yaml`), all nine conditions are CONTROLLED, eight are VERIFIED on GitHub Actions (run 40361964609), and E03-CS001-SUT02-IOS is NOT_VERIFIED; none is measured-execution-ready before the campaign START. No condition was added to maximize coverage and none removed to avoid mobile qualification — every row traces to a COMPARABLE mapping entry on real evidence.

## 6. Sample size per condition

N = 50 per executable condition (human decision D2 of 2026-10-05; executor README, section 11, item Q7): execution ids EX0001 to EX0050, attempt 1 each, with the Required Actions (reset) statistics over the attempts that reached the reset action and the ABORTED and ERROR attempts reported beside them (`protocol/repeatability-determinism-v1.md` §3). The two mobile conditions have no sample size: they are blocked (section 7). Not locked until the campaign START.

## 7. Mobile qualification applicability

**REQUIRED and not satisfied** — covering **two** condition rows: `E03-CS001-SUT02-ANDROID`, `E03-CS001-SUT02-IOS` (the two CS-002-derived SUT-06 rows of the 2026-09-21 draft are no longer part of the configuration). Mobilewright FAILED the qualification gate (2026-09-24), the frozen switch rule selected Appium 3 (pinned 3.7.0), and its compatibility smoke on SUT-02 passed for Android and failed for iOS (FAIL_RUNNER by the conservative tie-break of `protocol/mobile-runner-policy-v2.md` §9.4), which exhausted the fallback (`mobile_runner_status` UNRESOLVED_AFTER_FALLBACK_FAILURE, 2026-09-29). Both rows are therefore blocked from START and measurement (gate G-7); the remediation path of `protocol/mobile-runner-policy-v3.md` §9.7 is not pursued before the planned manuscript's DATA FREEZE (human decision of 2026-10-20, `manifests/mobile-path-disposition-v1.yaml`). The rows are recorded, not omitted.

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

DRAFT / PRE-START. Not the campaign's locked "Campaign configuration" record. Campaign status in `manifests/study-manifest.yaml` remains `NOT_STARTED`. The candidate text of the locked record and the confirmations it needs are prepared in `manifests/e03-campaign-start-package-v1.yaml` (operation OP-LOCK-01, 2026-10-26); this draft is promoted only at the START.
