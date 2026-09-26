# E03-resetability — CI/CD Measured-Execution Model

| Field | Value |
|---|---|
| Prepared by | ORCHESTRATOR |
| Date | 2026-09-21 (design only, BLOCKED); revised 2026-09-22 (human decisions applied; infrastructure created) |
| Status | **IMPLEMENTED AS PRE-START INFRASTRUCTURE; MEASURED EXECUTION NOT_STARTED.** GitHub Actions is the selected orchestrator (human decision, 2026-09-22). The four workflows under `.github/workflows/` exist and are lint-clean; the measured-execution workflow fails closed on every campaign gate and cannot execute a condition until a human starts E03. Nothing in this document authorizes E03 START. |

## 1. Decisions that resolved the 2026-09-21 blockers

The 2026-09-21 version of this document (commit `41d5226`, retained in git history) surfaced four blockers and resolved none. All four were resolved by explicit human decision on 2026-09-22 (the E03 PRE-START corrective operation instruction):

| 2026-09-21 blocker | 2026-09-22 resolution | Where recorded |
|---|---|---|
| AGENT-INSTRUCTIONS.md "no CI" Style rule conflict | Narrowest amendment: GitHub Actions workflow files under `.github/workflows/**` for E03-resetability measured execution and its validation are the sole exception; no general CI permission for E02, E04–E12, other platforms, or unrelated automation | AGENT-INSTRUCTIONS.md, "Style" and "E03 CI/CD infrastructure" |
| No CI-config write boundary | `.github/workflows/**` granted to ORCHESTRATOR only (`E03-CI-WRITE-AUTH-01`); EXECUTOR-E03-RESETABILITY may only trigger/read a frozen workflow | AGENT-INSTRUCTIONS.md; protocol/agent-governance-v2.md (FROZEN-PRE-DATA 2026-09-22), sections 3.5 and 4 |
| No CI orchestrator selected | **GitHub Actions.** Every E03 MEASURED_EXPERIMENT must run through the frozen GitHub Actions path; local runs are limited to DEVELOPMENT, SYNTAX_VALIDATION, TOOL_QUALIFICATION, SMOKE, ENVIRONMENT_VERIFICATION, DRY_RUN and never enter the measured dataset | AGENT-INSTRUCTIONS.md; this document |
| SCHEMA_GAP_FOUND (per-action outcome) | `schemas/run-manifest.schema.v2.json` adds the optional `actions[].outcome` (SUCCESS / PARTIAL_SUCCESS / FAILURE); mandatory on every emitted action record by E03 campaign convention | manifests/run-manifest-schema-v2-provenance.yaml; protocol/CHANGELOG.md; schemas/README.md |

Additionally decided on 2026-09-22: the study repository intended for GitHub Actions must be **PUBLIC** (section 8 below), and CS-001 is the sole accepted canonical scenario (nine conditions; `experiments/E03-resetability/canonical-scenario-catalogue.md`).

## 2. Workflow architecture (`.github/workflows/`)

| Workflow file | Name | Trigger | Class of every job | What it may never do |
|---|---|---|---|---|
| `e03-validate.yml` | E03 Validate Configuration | push, pull_request, workflow_dispatch | VALIDATION (schema compile; YAML parse; frozen E01 hashes; active catalogue = CS-001 only, nine conditions recomputed from the frozen record; campaign-status invariants; change-log completeness; evidence-header identity; publication hygiene over tracked files and pushed commits; actionlint; domain-oriented names) | execute a SUT; write raw-data/ |
| `e03-environment-verification.yml` | E03 Environment Verification | workflow_dispatch (target: all or one SUT surface) | ENVIRONMENT_VERIFICATION, one job per surface: provision from the pinned commit/release, start, verify surface and reset-mechanism reachability, upload an artifact named `E03-ENVIRONMENT_VERIFICATION-<SUT>-<surface>-run<id>-a<attempt>` | establish and reset business state as an experiment; count Required Actions; write raw-data/ |
| `e03-mobile-qualification.yml` | E03 Mobile Qualification | workflow_dispatch (instruction id, runner candidate Mobilewright or Appium 3, platform, confirmation) | **RETIRED 2026-09-26** (MOBILEWRIGHT_QUALIFICATION_PATH_RETIRED_AFTER_VALID_FORMAL_GATE_AND_RUNNER_SELECTION): the first gate step refuses every dispatch after the valid formal gate (MOBILE-QUALIFICATION-EXEC-AUTH-03, run 35938250936, FAIL) and the section 8 selection of Appium 3; re-opening needs a new explicit protocol decision. Historically: QUALIFICATION (gate: policy frozen, qualification build pinned, runner version and emulator/simulator identities recorded, scenario realization recorded, instruction recorded; execution jobs fail closed until QUALIFIER-MOBILE-01 authors the gate procedure; since PROTO-U12, 2026-09-23: an issued, dispatch-ELIGIBLE authorization whose frozen prompt declares its prompt version, implementation-lock v2 hashes, and an absent-or-empty formal namespace `qualification/mobilewright/formal/<instruction id>/`; one dispatch with platform both runs gate → Android → iOS, never concurrently; only the formal namespace is uploaded) | introduce Appium 2; produce SUT evidence; write raw-data/ |
| `e03-compatibility-smoke.yml` | E03 Compatibility Smoke | workflow_dispatch only (authorization id APPIUM3-COMPAT-SMOKE-AUTH-<nn>, confirmation) | COMPATIBILITY_SMOKE (added 2026-09-24, re-locked 2026-09-26 under protocol/mobile-runner-policy-v2.md section 9; prepared and never dispatched; for the selected runner Appium 3 3.7.0 on SUT-02 Android and iOS: the gate admits only an issued, dispatch-ELIGIBLE, never-dispatched smoke authorization with a frozen prompt, recomputes `manifests/compatibility-smoke-implementation-lock-v2.yaml`, the realization section hash, and the policy v2 hash, requires the study-level mobile-runner status SELECTED, no FAIL_RUNNER in the mirror, an absent-or-empty namespace `qualification/compatibility-smoke/formal/<authorization id>/`, unpopulated smoke and attribution records and mirror (first attempt only), and E03 NOT_STARTED; gate → Android → iOS, the iOS job only after an Android proposed PASS, never concurrent; run attempt 1 only; one artifact per platform) | introduce Appium 2; produce SUT evidence; write raw-data/ or manifests/; re-run an observation |
| `e03-measured-execution.yml` | E03 Measured Execution | workflow_dispatch (condition, assigned SUT, execution id, attempt, campaign-start authorization id, executor prompt version, executor implementation hash) | MEASURED_EXPERIMENT, gated (section 3) | run on a non-default branch; re-run natively; commit; overwrite an attempt; read another SUT's measured outputs |

Job, step, and artifact names are domain-oriented; the validation workflow refuses any name carrying assistant or vendor terms.

## 3. Measured-execution guards (fail closed)

`e03-measured-execution.yml`, job "E03 Measured Execution Gate", checks out only frozen inputs (no `raw-data/` at all) and refuses to let the measured job start unless **every** gate holds:

1. `github.ref` is `refs/heads/main` and `github.run_attempt` is 1 (a GitHub-native re-run is refused; a further attempt is a new dispatch with attempt+1).
2. `manifests/study-manifest.yaml` records E03-resetability as IN_PROGRESS (campaign START exists) and `protocol/CHANGELOG.md` carries exactly one `campaign NOT_STARTED -> IN_PROGRESS` row for `experiments/E03-resetability/README.md` containing the dispatched authorization id.
3. `experiments/E03-resetability/README.md` has the locked "Campaign configuration" record, and that record names the dispatched condition, `run-manifest.schema.v2.json`, the executor prompt version, and the executor implementation hash.
4. `experiments/scenario-mappings/CS-001.yaml` is FROZEN; the assigned SUT is COMPARABLE on it for the condition's surface; the configuration cites CS-001 and no `E03-CS002` condition; the change log carries the CS-002 `EXCLUDED_FROM_CAMPAIGN` row; the catalogue declares one active scenario.
5. `schemas/run-manifest.schema.v2.json` exists with the v2 `$id`.
6. `protocol/agent-governance-v2.md` is FROZEN-PRE-DATA or AMENDED (never DRAFT).
7. For an ANDROID or IOS condition (corrected 2026-09-24, PROTO-U14, before E03 START): `manifests/toolchain-manifest.yaml` `mobile_runner_selection.selected_runner` is Mobilewright or Appium 3, and the lineage of that selected runner holds — **Mobilewright path** (the runner passed the gate): `mobile_primary_candidate.qualification_status: PASSED` and the selection names the Mobilewright pin; **Appium 3 path** (protocol/mobile-runner-policy-v1.md section 8 switch after Mobilewright failed the gate): `mobile_primary_candidate.qualification_status: FAILED`, fallback candidate Appium 3 with `selected_version_pin` 3.7.0 equal to its pin, and `basis` naming protocol/mobile-runner-policy-v1.md section 8. On both paths: the selection's `human_authorization` is exactly one VALID, ISSUED, dispatched gate-authorization record; the selected runner's own `version` is recorded and equals its pin; the compatibility smoke is PASS for the condition's exact SUT × platform × selected runner (corrected 2026-09-24, PROTO-U15; since 2026-09-26, PROTO-U18, it is preceded for every mobile condition by the study-wide rule of protocol/mobile-runner-policy-v2.md section 9.5 — the study-level `mobile_runner_status` must be SELECTED and no FAIL_RUNNER of the selected runner may be recorded for any SUT × platform in the mirror or the QUALIFIER records; the state is ADMISSIBLE, FALLBACK_EXHAUSTED_VERIFIED, or PROVENANCE_INCONSISTENT_FAIL_CLOSED, and any non-admissible state blocks every mobile condition, including one whose own smoke passed): exactly one matching entry in `manifests/compatibility-smoke-status.yaml` (the ORCHESTRATOR mirror of the QUALIFIER-MOBILE-01 records under `qualification/compatibility-smoke/`) with result PASS and `runner_version` equal to the pin, whose `qualifier_record` holds a PASS row for the same SUT and platform with that version — an Android result never satisfies an iOS condition, nor the reverse, and another SUT's or runner's result never counts; the study-level `compatibility_smoke_status` summaries are not read; Appium 2 is never selected. Selected runner `none`, a smoke that is not PASSED, or an absent version fails closed. (Until 2026-09-24 this gate required `qualification_status: PASSED` for every mobile condition and accepted any runner's version, so it represented only the Mobilewright-pass path.)
8. `experiments/E03-resetability/controlled-instance-status.yaml` records the condition as `CONTROLLED` **and** its `github_actions_verification.status` as `VERIFIED` (a workstation verification alone does not satisfy this gate, because the measured run executes on a GitHub-hosted runner).
9. `prompts/frozen/<executor_prompt_version>.md` exists.
10. `experiments/E03-resetability/executor/run-condition.sh` exists and its SHA-256 equals the dispatched hash recorded in the locked configuration.
11. Pinned revisions are captured as gate outputs: repository SHA, workflow file SHA-256, E03 configuration SHA-256, CS-001 SHA-256, schema v2 SHA-256, executor prompt SHA-256, governance SHA-256, and the `Canonical-Source-Commit` trailer when the run executes in a reproducibility export (section 8).

As of 2026-09-22 gates 2, 3, 7, 8 (GitHub Actions verification), 9, and 10 cannot hold, so the measured job cannot run; gate 6 became satisfiable when protocol/agent-governance-v2.md was frozen on 2026-09-22. That is the intended state.

## 4. Reproducibility contract (captured per measured run)

The job "E03 Provenance Capture" writes `ci-provenance.json` and the measured job writes `runtime-environment.json`; both travel inside the attempt bundle:

repository SHA and ref; canonical source commit (export mode); workflow ref and file SHA-256; E03 configuration hash; CS-001 mapping hash; run-manifest schema v2 hash; executor prompt version and hash; executor implementation hash; agent-governance v2 hash; SUT version (repository, commit, release from `manifests/sut-manifest.yaml`); `environment_type` (section 6); runner OS, image, image version, CPU architecture; runtime versions (Python, Node.js, npm, Java, Docker, git) and browser version as observed on the runner; lockfile hashes and tool versions as recorded by the executor implementation for the condition; Android emulator and iOS Simulator configuration and, for an ANDROID or IOS condition, the study-selected mobile runner as the execution runner (`mobile_runner.selected_runner` / `execution_runner`, its pin and recorded version, the selection basis and authorization, and the condition's SUT × platform compatibility-smoke entry), with the primary candidate and the fallback kept separately under `historical_candidates` (PROTO-U15, 2026-09-24; `mobile_runner` is null for WEB and API conditions); timezone (UTC enforced); timeout policy; retry policy (none); concurrency policy (one run per condition, never cancelled); artifact retention (90 days); GitHub run id, run attempt, run number, job; condition id, execution id, attempt number, run id. No secret value is ever recorded (none is used).

## 5. Execution/attempt model and immutability

`campaign -> SUT -> scenario -> condition -> execution -> attempt`, realized as:

- **Run id (candidate convention, to be locked at campaign start, not frozen here):** `<condition_id>__<execution_id>__A<attempt>` — for example `E03-CS001-SUT01-API__EX0001__A1`. It is flat because `schemas/run-manifest.schema.v2.json` requires `run_id` to equal the directory name directly under `raw-data/<campaign-id>/<sut-id>/` (raw-data/README.md); the hierarchy is encoded in the id rather than nested. raw-data/README.md's `<run-id> format: TBD before freeze` is resolved by this convention only when the locked campaign configuration adopts it.
- **Attempt 1 is immutable.** The workflow refuses to run if the run directory already exists; the artifact is uploaded with overwrite disabled, so an attempt's bundle can never be replaced; a re-run is a new dispatch with attempt+1 and a new run id. A GitHub-native re-run (`run_attempt` > 1) is refused at the gate, so the platform's attempt counter never silently aliases a study attempt; if a platform re-run were ever observed, its run id and attempt are recorded in the new attempt's provenance rather than mapped implicitly.
- **Per attempt, preserved:** result (run manifest `outcome`), stdout, stderr, structured logs, Required Action records with per-action outcomes (`actions[].outcome`), pre-reset, reset, and post-reset evidence, API evidence, screenshots, browser and mobile logs, environment metadata, GitHub Actions metadata, execution id, attempt lineage, exit status, start/finish timestamps, commit hashes, configuration and mapping hashes.
- **No automatic retry** exists for the measured step; no `continue-on-error`; job timeouts are declared and recorded.

## 6. `environment_type` determination for GitHub-hosted runners

protocol/study-design-v1.md, section 10.1: SELF_HOSTED is "an instance of the pinned evaluated version deployed by the study on infrastructure under the study's control (server, container host, or cloud account)". A GitHub-hosted runner is an ephemeral cloud host that the study controls for the duration of the job (the study chooses image, versions, and what runs there; no other user shares the instance), so a web or api instance provisioned there is recorded **SELF_HOSTED**; an Android emulator on the runner is **EMULATED**; an iOS Simulator on a macOS runner is **SIMULATED**. A workstation instance is **LOCAL**. All four are controlled environments. This determination is written into every ENVIRONMENT_VERIFICATION record and into the measured provenance record rather than implied.

## 7. Artifact classes and retention

| Class | Produced by | Artifact name prefix | Where it may end up |
|---|---|---|---|
| VALIDATION | `e03-validate.yml` | (logs only) | nowhere in the repository |
| PROVISIONING / ENVIRONMENT_VERIFICATION | `e03-environment-verification.yml`; workstation provisioning under human authorization | `E03-ENVIRONMENT_VERIFICATION-…` | `manifests/provisioning/<sut-id>/` (provisioning records, ORCHESTRATOR-authored) and `experiments/E03-resetability/environment-verification/` (verification evidence); **never** `raw-data/` |
| QUALIFICATION | `e03-mobile-qualification.yml` | `E03-QUALIFICATION-…` | `qualification/` only |
| COMPATIBILITY_SMOKE | `e03-compatibility-smoke.yml` | `E03-COMPATIBILITY_SMOKE-SUT-02-<platform>-run<id>-a1` | `qualification/compatibility-smoke/formal/<authorization id>/SUT-02-<platform>/` only, by QUALIFIER-MOBILE-01 import |
| SMOKE / DRY_RUN / DEVELOPMENT / SYNTAX_VALIDATION | local or CI, labeled as such | (none) | nowhere; never `raw-data/` |
| MEASURED_EXPERIMENT | `e03-measured-execution.yml` only | `E03-MEASURED_EXPERIMENT-<condition>-<execution>-A<attempt>` (+ `-provenance`) | `raw-data/E03-resetability/<SUT>/<run-id>/`, by import (below) |

Retention: 90 days on GitHub (the public-repository maximum). A measured bundle must therefore be imported within that window. **Import:** the measured workflow never commits (`permissions: contents: read`). After a run, the ORCHESTRATOR downloads the bundle, verifies every file's SHA-256 against the bundle's own manifest and the GitHub run/attempt identifiers against `ci-provenance.json`, and commits it unchanged under `raw-data/E03-resetability/<SUT>/<run-id>/` in the canonical repository as "campaign execution under ORCHESTRATOR coordination" (protocol/agent-governance-v2.md, section 4), with the GitHub run id, run attempt, and artifact id recorded in the commit message and in a per-run `import-record.yaml` beside the bundle. No non-measured artifact enters `raw-data/` merely because GitHub Actions produced it; the artifact-name prefix and the `record_class` field inside every record make the class explicit.

## 8. Public repository and publication mode

The repository intended for GitHub Actions must be PUBLIC. The canonical repository's history is preserved internally exactly as recorded and is never rewritten (frozen artifacts cite its commits by SHA, for example the six auditor-result commits in the adjudicated matrix and H1 result). The public repository is a separate, provider-neutral clean reproducibility snapshot (publication mode CLEAN_PROVIDER_NEUTRAL_REPRODUCIBILITY_EXPORT, human decision 2026-09-22): fresh snapshot commits built from the canonical trees under explicit inclusion/exclusion rules and a transformation manifest, with every exported file traced to its canonical blob in `PUBLIC-EXPORT-MANIFEST.yaml` at the root of each exported branch; the rules and the export log are recorded in `PUBLIC-EXPORT-MANIFEST.yaml`. Each snapshot commit carries the trailers `Canonical-Source-Commit`, `Canonical-Source-Branch`, and `Export-Manifest-SHA256`, and nothing else. The measured workflow reads the `Canonical-Source-Commit` trailer, if present, into its provenance so that a run executed in the export is traceable to the canonical commit whose tree it ran on.

## 9. Local execution classes

A local execution on the operator's workstation or any other non-GitHub host may be only DEVELOPMENT, SYNTAX_VALIDATION, TOOL_QUALIFICATION, SMOKE, ENVIRONMENT_VERIFICATION, or DRY_RUN. It never produces a run manifest under `raw-data/`, never carries `record_class: MEASURED_EXPERIMENT`, and never enters any E03 dataset or analysis. The 2026-09-22 workstation provisioning of the CS-001 conditions is of class PROVISIONING / ENVIRONMENT_VERIFICATION (`experiments/E03-resetability/controlled-instance-determination.md`).

## 10. Summary

```
CI_ORCHESTRATOR = GITHUB_ACTIONS (human decision 2026-09-22)
EXISTING_INFRASTRUCTURE = .github/workflows/ (4 workflows; E03-CI-WRITE-AUTH-01)
SCHEMA_GAP = RESOLVED (schemas/run-manifest.schema.v2.json)
AGENT_INSTRUCTIONS_NO_CI_RULE = AMENDED (narrow exception)
CI_WRITE_BOUNDARY = GRANTED to ORCHESTRATOR (.github/workflows/** only)
MEASURED_EXECUTION = NOT_STARTED (gated; cannot run until E03 START and every gate holds)
PUBLICATION_MODE = PUBLIC-EXPORT-MANIFEST.yaml
```
