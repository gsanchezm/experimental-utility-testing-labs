# E03 — Resetability

## Objective

Measure the ability of each evaluated ecosystem (each a system under test, SUT) to restore a known initial state after that state has been altered. The campaign records which reset mechanisms exist, whether they succeed, how many actions they require, and whether manual intervention is needed. Reset success is judged by verification of state before and after the reset, not by the mechanism's own reporting. Deterministic reset requires a controlled instance when an open-source deployment of the evaluated version is available; reset operations are never executed against a PUBLIC_HOSTED instance, and an ecosystem for which no controlled instance can be established records NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE for the affected conditions (protocol/study-design-v1.md, section 10.3). The known initial state is the starting state of a canonical scenario with a FROZEN mapping record (protocol/equivalent-scenario-mapping-v1.md). Restarting or rebuilding an instance as one-time provisioning is not a reset action and is recorded in the provisioning record, not in Required Actions (protocol/setup-effort-v2.md).

## Current status

**NOT STARTED.** Human-selected for PRE-START preparation on 2026-09-21 and for NON-MEASURED PRE-START provisioning, environment verification, and CI/CD infrastructure on 2026-09-22. Preparation is not a campaign-status value and does not change this line. **E03 START is NOT authorized. No measured execution has occurred. No E03 result exists; H2 is NOT_ANALYZED.** The locked "Campaign configuration" record referenced throughout this repository's other campaign READMEs is a separate, later, campaign-start artifact (protocol/change-control-v1.md, section 7) and is not written here.

## PRE-START state (as of 2026-09-22)

| Item | State | Authoritative record |
|---|---|---|
| Canonical scenario | **CS-001 is the sole accepted canonical scenario** for the current E03 campaign version (FROZEN 2026-09-21, `E03-CS001-FREEZE-AUTH-01`). Canonical scenarios are defined independently of SUT-specific implementation evidence; E01 evidence establishes mapping/comparability only. | `experiments/scenario-mappings/CS-001.yaml`; `experiments/E03-resetability/canonical-scenario-catalogue.md` |
| CS-002 | Historical, preserved unchanged, **EXCLUDED_FROM_CAMPAIGN** (2026-09-22, human ruling `E03-CS002-EXCLUSION-RULING-01`): its intent was generalized from SUT-06-specific E01 evidence, contrary to protocol/equivalent-scenario-mapping-v1.md, section 6. Not an input to any E03 configuration, workflow, or executor. No successor or replacement scenario. | `manifests/e03-cs002-exclusion-v1.yaml`; `protocol/CHANGELOG.md`; `protocol/unresolved.md`, PROTO-U09 |
| Population | Six SUTs. SUT-06 remains a member, NOT_COMPARABLE on CS-001 (NO_EQUIVALENT_INTENT); it has no measured condition in this configuration and none is invented for it. | `CS-001.yaml`, SUT-06 entry |
| Candidate conditions | **9**, all on CS-001, recomputed from the frozen record (one per COMPARABLE SUT × `surfaces_used` entry): SUT-01 WEB, API; SUT-02 WEB, ANDROID, IOS; SUT-03 WEB; SUT-04 WEB, API; SUT-05 API. | `experiments/E03-resetability/campaign-configuration-draft.md`, section 5 |
| Issue (xviii) | RESOLVED, **A2 + B1** (`ISSUE-XVIII-RULING-01`, 2026-09-21): a verification counts as a Required Action classified by its mechanism; a partially successful action counts as one action with its outcome recorded separately. | `protocol/setup-effort-v2.md` (FROZEN-PRE-DATA; v1 AMENDED); `manifests/issue-xviii-ruling-v1.yaml` |
| PROTO-U08 | RESOLVED, non-blocking (DUPLICATE_OR_ALREADY_RESOLVED_CONCERN): the frozen protocol already fixes the controlled-instance determination per condition at campaign-configuration lock. | `protocol/unresolved.md` |
| Required Action semantics | Count of discrete experimenter-initiated operations with an observable effect, per action class (protocol/setup-effort-v2.md, sections 3–5); establish and reset counted separately; scripted sequences count each constituent action; retries counted and tagged. | `protocol/setup-effort-v2.md` |
| Action outcome semantics | Every emitted action record carries `outcome` ∈ {SUCCESS, PARTIAL_SUCCESS, FAILURE}, recorded separately from the count; a retry is a further action record with `is_retry` true and is never represented by changing an earlier action's outcome; run-level `outcome.status` is a distinct, run-scoped concept. | `protocol/setup-effort-v2.md`, section 5, rules 4, 8, 9 |
| Run-manifest schema | **v2** — `schemas/run-manifest.schema.v2.json` (adds only the optional `actions[].outcome`; v1 preserved). Future E03 run manifests conform to v2; `actions[].outcome` is REQUIRED BY CAMPAIGN CONVENTION on every emitted action record. | `manifests/run-manifest-schema-v2-provenance.yaml`; `schemas/README.md` |
| Controlled-instance verification | Non-measured provisioning and environment verification performed 2026-09-22 on the operator workstation (LOCAL / EMULATED / SIMULATED) under explicit human authorization; per-condition status and the GitHub Actions verification requirement for measured execution are in the status record. | `experiments/E03-resetability/controlled-instance-determination.md`; `experiments/E03-resetability/controlled-instance-status.yaml`; `experiments/E03-resetability/environment-verification/`; `manifests/provisioning/` |
| Provisioning vs measured execution | Provisioning (clone, download, install, build, start, emulator/simulator boot, install app) and environment verification (surface and reset-mechanism reachability) are ONE-TIME PROVISIONING, recorded descriptively, never counted, never `raw-data/`. A measured execution establishes the canonical state, resets it, verifies before and after, and records every Required Action with its outcome in a run manifest under `raw-data/E03-resetability/<sut-id>/<run-id>/`. | `protocol/setup-effort-v2.md`, sections 2 and 8; `raw-data/README.md` |
| CI/CD | **GitHub Actions is the E03 orchestrator** (human decision 2026-09-22; AGENT-INSTRUCTIONS.md, `E03-CI-WRITE-AUTH-01`). Every MEASURED_EXPERIMENT must run through `.github/workflows/e03-measured-execution.yml`, which fails closed on every gate (campaign START, locked configuration, CS-001 frozen and CS-002 excluded, schema v2, frozen governance, mobile qualification for mobile cells, GitHub-verified controlled instance, frozen executor prompt and implementation, default branch, first attempt only). Local executions are DEVELOPMENT / SYNTAX_VALIDATION / TOOL_QUALIFICATION / SMOKE / ENVIRONMENT_VERIFICATION / DRY_RUN only and never enter the measured dataset. | `experiments/E03-resetability/ci-cd-execution-model.md`; `.github/workflows/` |
| Retry / attempt semantics | campaign → SUT → scenario → condition → execution → attempt. Attempt 1 is immutable; a retry is a new dispatch with attempt+1 and a new run id; GitHub-native re-runs are refused; no automatic retry. Candidate run-id convention `<condition_id>__<execution_id>__A<attempt>` (locked only at campaign start). | `ci-cd-execution-model.md`, section 5 |
| Artifact retention | One immutable bundle per attempt (run manifest, stdout/stderr, structured logs, action records with outcomes, pre/reset/post evidence, API evidence, screenshots, browser/mobile logs, environment and GitHub metadata, ids, exit status, timestamps, hashes); 90-day GitHub retention; imported into canonical `raw-data/` by the ORCHESTRATOR with hash verification. PROVISIONING, ENVIRONMENT_VERIFICATION, QUALIFICATION, SMOKE, and DRY_RUN artifacts are labeled as such and never enter `raw-data/`. | `ci-cd-execution-model.md`, section 7 |
| Mobile qualification | **INVALID / REQUIRES RE-EXECUTION** (PROTO-U10, 2026-09-22). A Mobilewright gate ran on 2026-09-22 (`e03-mobile-qualification.yml` runs 35763051534 Android, 35767911878 iOS; 60 measured executions) on a relayed authorization that no human had issued; its executions are preserved and quarantined as HISTORICAL_UNAUTHORIZED_EXECUTION (`qualification/mobilewright/output/QUARANTINE-RECORD.yaml`), and the FAIL decision and Appium 3 selection derived from it are superseded (historical, non-authoritative observation: MQ1/MQ2 10/10 on both platforms, MQ3 10/10 on iOS, MQ3 0/10 on the Android emulator, MC-07). **Current state:** primary candidate Mobilewright 0.0.60, fallback Appium 3.7.0, selected runner none; Appium 2 never. **Still REQUIRED** before `E03-CS001-SUT02-ANDROID` and `E03-CS001-SUT02-IOS`: a protocol-valid gate under a NEW human authorization, then the per-SUT compatibility smoke of SUT-02 with the selected runner (policy sections 2, 7–9); PREQUALIFICATION_OUTCOME_EXPOSURE true (frozen inputs immutable). Qualification records are tool-qualification records, never SUT evidence. | `protocol/mobile-runner-policy-v1.md`; `qualification/`; `manifests/mobile-qualification-authorization-correction-v1.yaml` |
| Agent governance | `protocol/agent-governance-v2.md` is **FROZEN-PRE-DATA** (2026-09-22, at its exact pre-freeze content hash, authorization id AGENT-GOVERNANCE-V2-FREEZE-AUTH-01; `manifests/agent-governance-v2-freeze-v1.yaml`; v1 AMENDED): explicit executor READ and WRITE boundaries, cross-SUT isolation, GitHub Actions permissions and prohibitions, granted CI-config boundary. G6 now satisfiable. It grants no execution authority: EXECUTOR-E03-RESETABILITY is defined, not launched, and launch still requires E03 START, a frozen executor prompt, and every other gate. | `protocol/agent-governance-v2.md`; AGENT-INSTRUCTIONS.md |
| Executor prompt | None exists (expected at this stage; prompt authoring and freeze follow campaign START in the current lifecycle, prompts/README.md). | `prompts/` |
| E03 START | **NOT AUTHORIZED.** A LOCAL_DEVELOPMENT_PREFLIGHT ran 2026-09-22 (implementation baseline locked; Android complete, iOS blocked on host infrastructure; `qualification/mobilewright/local-preflight/`) — non-qualification, non-measured, and does not change any gate below. Remaining human approvals: a NEW mobile-qualification EXECUTION authorization (protocol-valid gate); the compatibility smoke of the selected runner for SUT-02 (Android, iOS); E03 campaign START; executor prompt freeze and launch. Governance v2 freeze and the public-repository publication mode were decided 2026-09-22. | `manifests/study-manifest.yaml` |

## PRE-START artifacts

- `experiments/E03-resetability/issue-xviii-analysis.md` — ambiguity analysis leading to the human ruling on issue (xviii).
- `experiments/E03-resetability/canonical-scenario-catalogue.md` — active catalogue (CS-001 only), methodological rule, excluded record, correction record.
- `experiments/E03-resetability/campaign-configuration-draft.md` — draft configuration (nine candidate conditions), explicitly distinct from the locked campaign-start record.
- `experiments/E03-resetability/controlled-instance-determination.md` and `controlled-instance-status.yaml` — per-condition controlled-instance determination (source inspection 2026-09-21; workstation provisioning and environment verification 2026-09-22; GitHub Actions verification pending).
- `experiments/E03-resetability/environment-verification/` — ENVIRONMENT_VERIFICATION evidence records (non-measured).
- `experiments/E03-resetability/ci-cd-execution-model.md` — implemented GitHub Actions model, guards, reproducibility contract, artifact classes, import step.
- `protocol/agent-governance-v2.md` — FROZEN-PRE-DATA (2026-09-22); defines EXECUTOR-E03-RESETABILITY.
- `manifests/mobile-qualification-package-v1.yaml` — frozen-input package for the mobile qualification gate (preparation only).

## Related research question(s)

- RQ2 Controllability, Observability, Automation Affordances, and Setup Effort (primary).
- Informs dimensions 2 Experimental Controllability and 6 Setup Effort.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Reset mechanism(s) used (`reset_mechanisms`; frozen vocabulary: API_RESET, SESSION_RESET, APP_RELAUNCH, APP_DATA_CLEAR, FIXTURE_RESTORE, ENVIRONMENT_RESTART, REDEPLOY, MANUAL, NONE, OTHER — protocol/setup-effort-v2.md, section 10; one or more per run; MANUAL is valid evidence and is never hidden) — candidate.
- Surface (web / api / android / ios) — candidate.

## Future dependent variables (candidate — not frozen)

- Reset success rate (proportion of attempts in which the verified post-reset state matches the known initial state) — candidate.
- Reset action count (Required Actions of the reset procedure, by action class per protocol/setup-effort-v2.md section 4 (Action classes)) — candidate.
- Reset duration (secondary) — candidate.
- Manual intervention requirement (categorical, with description) — candidate.

## Required evidence

- Run manifest per run conforming to schemas/run-manifest.schema.v2.json, including ecosystem id, reset mechanism(s) (`reset_mechanisms`, mandatory and non-empty for E03 runs; protocol/setup-effort-v2.md, section 10), surface, `environment_type`, outcome, and, for every action record, `outcome` (campaign convention).
- Pre-reset state verification record (the altered state, captured before reset).
- Post-reset state verification record (the state captured after reset) and the comparison against the known initial state.
- Definition of the known initial state used, with provenance.
- Ordered action list for the reset procedure, recorded in the run manifest `actions` field (schemas/run-manifest.schema.v2.json), with action classes per protocol/setup-effort-v2.md section 4 (Action classes) and per-action outcomes per section 5, rule 9.
- Record of any manual intervention.
- CI provenance (`ci-provenance.json`, `runtime-environment.json`) from the frozen GitHub Actions execution path.
- Raw observations in `raw-data/E03-resetability/`, imported from the immutable attempt bundle.

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution — satisfied for every protocol document in force, including protocol/agent-governance-v2.md (frozen 2026-09-22). A frozen protocol is not an execution authorization. Do not execute without explicit instruction. Do not report any E03 result: none exists.
