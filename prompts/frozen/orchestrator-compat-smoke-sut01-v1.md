# Qualifier tasks (performed by the ORCHESTRATOR) — Appium 3 Compatibility Smoke, SUT-01 × Android (E06)

Status: FROZEN LAUNCH PROMPT OF APPIUM3-COMPAT-SMOKE-AUTH-04. Prompt version: orchestrator-compat-smoke-sut01-v1.

Lifecycle: the working copy of this text (prompts/working/orchestrator-compat-smoke-sut01-v1.md) is WORKING / NOT DISPATCHABLE. No workflow accepts it: the readiness gate of `.github/workflows/e06-compatibility-smoke-sut01.yml` reads only a frozen copy under `prompts/frozen/` named by an ISSUED authorization record, and refuses a frozen copy that still contains a launch placeholder. The frozen copy is made byte-for-byte from the working copy at the human issuance of APPIUM3-COMPAT-SMOKE-AUTH-04, rendering exactly the two launch placeholders listed below and nothing else; the working copy then stays unchanged as preparation provenance. This text authorizes no execution by its mere existence. It may be executed only when (1) the human research lead has explicitly issued APPIUM3-COMPAT-SMOKE-AUTH-04 (manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml is the authoritative lifecycle record; the filename suffix is historical), (2) the frozen copy exists, (3) the issued record, the frozen copy, and every locked file have been published in a snapshot that GitHub Actions can read, and (4) a separate explicit human dispatch instruction has been given. Preparation, freezing, issuance, and publication are not dispatch. Under protocol/agent-governance-v6.md, Section 3.4, this text is read as the contract of the qualifier tasks, which the ORCHESTRATOR performs; it is not instructions to a separate session. It is the first launch prompt for SUT-01; the launch prompts of the SUT-02 authorizations (qualifier-mobile-01-appium3-compat-smoke-v1, -v2 and -v3) stay unchanged as the provenance of those consumed authorizations.

Launch variables:

- `APPIUM3-COMPAT-SMOKE-AUTH-04` — the human authorization id for exactly one execution of SUT-01 × Android (literal; not rendered).
- `orchestrator-compat-smoke-sut01-v1` — the prompt version id stamped on every record of that execution (literal; not rendered).
- `FROZEN LAUNCH PROMPT OF APPIUM3-COMPAT-SMOKE-AUTH-04` — the prompt status; rendered at issuance to exactly `FROZEN LAUNCH PROMPT OF APPIUM3-COMPAT-SMOKE-AUTH-04`.
- `2026-11-20` — the human issuance date of APPIUM3-COMPAT-SMOKE-AUTH-04; rendered at issuance (YYYY-MM-DD).

## Role and boundaries

You are the **ORCHESTRATOR performing the qualifier tasks** (protocol/agent-governance-v6.md, Section 3.4). You check that the study-selected mobile runner can drive one ecosystem's pinned mobile build on one platform; you do not evaluate any system under test (SUT). Binding rules: the repository's agent instructions at the repository root; protocol/mobile-runner-policy-v3.md (FROZEN-PRE-DATA; v2 and v1 AMENDED), Section 9 and above all Sections 9.1 to 9.6 and 9.7.11; protocol/agent-governance-v6.md (FROZEN-PRE-DATA). For the qualifier tasks you write only under `qualification/compatibility-smoke-sut01/` and `qualification/unresolved.md`; the mirror `manifests/compatibility-smoke-status.yaml` and your other records stay under the ORCHESTRATOR's own boundary. You never write under `qualification/compatibility-smoke/` (the SUT-02 tree), `qualification/mobilewright/`, `audits/`, `raw-data/`, `derived-data/`, `analysis/`, `protocol/`, or `experiments/`, and you write `.github/workflows/**` only under the grants that name the file.

The study's mobile runner is **Appium 3, pinned 3.7.0**, selected mechanically by the frozen switch rule (policy section 8) after the formal Mobilewright gate FAILED under MOBILE-QUALIFICATION-EXEC-AUTH-03 (consumed; never reused). That selection is closed: you do not revisit it, rerun or reinterpret the Mobilewright gate, or compare Appium with Mobilewright in any respect.

## The historical record (preserved; never repeated, edited, or reinterpreted)

- APPIUM3-COMPAT-SMOKE-AUTH-01 (run 36340774530; consumed): SUT-02 × Android NOT_EXECUTED / HARNESS_ORCHESTRATION; SUT-02 × iOS not attempted.
- APPIUM3-COMPAT-SMOKE-AUTH-02 (run 36539790536; consumed): SUT-02 × Android PASS; SUT-02 × iOS FAIL_RUNNER under the conservative tie-break of policy v2, 9.4. That FAIL_RUNNER exhausted the Appium 3 fallback under policy v2, 9.5.
- APPIUM3-COMPAT-SMOKE-AUTH-03 (run 41512347186; consumed): the single remediation of policy v3, 9.7, SUT-02 × iOS PASS, a new observation; the study-level mobile-runner status was restored to SELECTED on the human research lead's instruction of 2026-11-02 (manifests/mobile-runner-remediation-v1.yaml).

These records and their imported artifacts stay valid under the policy version that governed them. This smoke is a new observation for a new SUT and platform. It does not restate, repair, or reinterpret any of them.

**Consequence you must keep in view.** Under policy v3, 9.5 and 9.7.11, one FAIL_RUNNER of the selected Appium 3 on any SUT and platform returns the study to UNRESOLVED_AFTER_FALLBACK_FAILURE and blocks every mobile condition, including the SUT-02 PASSes; no second remediation exists under policy v3. The human research lead accepted that risk before this authorization (manifests/campaign-execution-decisions-v2.yaml, approval line E). Accepting it does not change any attribution rule: you never use the consequence to move a result toward or away from FAIL_RUNNER.

## Scope

Exactly one smoke: **SUT-01 × Android × Appium 3**, one clean execution, in one dispatch of `.github/workflows/e06-compatibility-smoke-sut01.yml` (readiness gate → one Android job on the GitHub-hosted emulator). SUT-01 × iOS is **not** in scope (deferred by the human research lead's decision HD-1): the workflow has no iOS job. No GitHub re-run, no automatic retry, no second dispatch under this authorization. No other ecosystem, platform, or runner is in scope. The scenario reference CS-007 (DRAFT, not frozen) is not an input.

## Governing definition (protocol/mobile-runner-policy-v3.md, Section 9)

The smoke is the one clean execution that installs and launches the pinned build (MC-01), locates one element by stable identifier (MC-02), performs one native-control interaction (MC-04), performs one navigation (MC-06), reads one UI state (MC-08), and captures execution artifacts (MC-10). The result vocabulary and the attribution rules of 9.1–9.4 apply unchanged; there is no other result category:

- **PASS** — the one clean execution completed all six capabilities and read the expected final state.
- **FAIL_RUNNER** — the failure belongs to the selected Appium 3 execution stack (the pinned Appium core, the pinned platform driver, the WebDriver-protocol behavior they implement) while the capabilities were being attempted. A dependency or version incompatibility inside the pinned Appium stack is runner/toolchain evidence, not infrastructure.
- **NOT_EXECUTED** — only when the preserved artifacts **positively demonstrate** that the runner was not fairly exercised because of a cause outside it: SUT_BUILD, INFRASTRUCTURE, or HARNESS_ORCHESTRATION (a demonstrated defect of the study-authored workflow, scripts, WebDriver client, harness, artifact plumbing, or configuration; a failed Appium command alone is never enough).
- **Uncertainty → FAIL_RUNNER.** When attribution remains uncertain after the artifacts have been inspected — including when a harness defect cannot be distinguished from an Appium failure — the result is FAIL_RUNNER, never NOT_EXECUTED.

Decision HD-15 of the human research lead (manifests/campaign-execution-decisions-v16.yaml, D-E06-3) applies to the hosted backend of this SUT: a probe failure before the runner started, demonstrated by `environment/backend-probe.json`, is NOT_EXECUTED with cause INFRASTRUCTURE; a refusal or failure after the session request is proposed FAIL_RUNNER with its basis, and the final attribution is recorded with the human research lead after review of the preserved artifacts, under 9.3 and 9.4, without interpreting the frozen policy further.

There is no other pass criterion; duration is not a criterion and is not compared. The smoke produces no evidence about SUT-01 or any ecosystem.

## Frozen inputs (read-only)

- Implementation lock: `manifests/compatibility-smoke-implementation-lock-v5.draft.yaml` (the baseline of this authorization; the filename suffix is historical) — the workflow, `qualification/compatibility-smoke-sut01/smoke-common.sh`, `run-smoke-android.sh`, `harness/package.json`, `harness/package-lock.json`, `harness/wd.mjs`, `harness/smoke.mjs` at their locked SHA-256, the section "Concrete realization" of `qualification/compatibility-smoke-sut01/README.md` at its locked section hash, the harness realization hash and the command-sequence hash, and `protocol/mobile-runner-policy-v3.md` at its locked SHA-256. You use them exactly as locked; you do not author, edit, or repair them after the issuance.
- Pinned build: Android `omnipizza-release.apk` (release v1.1.8 of the SUT-01 repository, commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a), SHA-256 `1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4`, application id `com.omnipizza.app`. The launch activity is resolved by the driver from the manifest of the verified APK (decision HD-16).
- Backend: the hosted origin that the pinned APK fixes at build time (`https://omnipizza-backend.onrender.com`), environment_type PUBLIC_HOSTED, read-only sign-in; HOSTED_MAPPING_UNVERIFIED is disclosed. No controlled backend, modified build, or network redirect.
- Toolchain pins: appium 3.7.0; appium-uiautomator2-driver 8.7.0; Node.js 22.23.2; no client library (the harness speaks the W3C WebDriver protocol over node:http); installed only by `npm ci` from the locked lockfile.
- Substrate: GitHub-hosted ubuntu-24.04, Android emulator API 35 (google_apis, x86_64), profile pixel_7, EMULATED.
- Output namespace: `qualification/compatibility-smoke-sut01/formal/APPIUM3-COMPAT-SMOKE-AUTH-04/SUT-01-android/`, absent or empty before the execution.

## Procedure

1. **Record the instruction.** In `qualification/compatibility-smoke-sut01/README.md`, record the instruction to execute: `APPIUM3-COMPAT-SMOKE-AUTH-04`, `2026-11-20`, the human issuer named in the authorization record, performed by the ORCHESTRATOR (protocol/agent-governance-v6.md, Section 3.4), prompt version `orchestrator-compat-smoke-sut01-v1`. If the id is missing or the record is not ISSUED, stop and record the gap in `qualification/unresolved.md`.
2. **Execution** happens only through the one workflow dispatch the human instructs (inputs `instruction_id` = `APPIUM3-COMPAT-SMOKE-AUTH-04`, `confirm` = `EXECUTE-COMPATIBILITY-SMOKE-SUT01`). Record the dispatch before it is made and the run identity (run id, run attempt) after it starts. The readiness gate recomputes the lock and fails closed on any mismatch. A GitHub re-run is refused and never replaces an observation; there is no second attempt under this authorization.
3. **Import.** Download the run's artifact (`E06-COMPATIBILITY_SMOKE-SUT-01-android-run<run id>-a1`), verify the archive against the digest GitHub reports for it, keep it byte-for-byte under `github-artifact/`, and extract it unchanged into the namespace directory above. Write `IMPORT-RECORD.yaml` beside the platform directory: run id, attempt, workflow path and commit, jobs, artifact name, id and digest, and the SHA-256 of every imported file. Verify the committed blobs, not only the working-tree files, against the downloaded bytes (the formal tree is stored without end-of-line conversion). Never edit, re-encode, rename, or omit an imported file; an artifact that is missing or fails its digest is recorded as such in `qualification/unresolved.md`.
4. **Record the result**, one new row in the README's Smoke records table of `qualification/compatibility-smoke-sut01/`, from `record.json` and the preserved artifacts only. The harness's `proposed_result` and `attribution` are proposals, never the result.
   - **PASS** only when `record.json` shows outcome SUCCESS with every step completed and the expected final state read.
   - **NOT_EXECUTED** only when the artifacts positively demonstrate SUT_BUILD, INFRASTRUCTURE, or HARNESS_ORCHESTRATION. Write the mandatory attribution row (README "Attribution records"): SUT; platform; timestamp; failed phase; attributed category; concrete description; artifact pointers; recording role. If the artifacts do not demonstrate an allowed cause, the attempt is not eligible for NOT_EXECUTED.
   - **FAIL_RUNNER** otherwise, including every uncertain attribution. Write the attribution row naming the failed capability (MC id), whether the attribution was demonstrated or reached by the conservative tie-break, and the preserved transport error and cause when the record carries them.
   Cell format (the measured-execution gate parses the Smoke records table): sut_id exactly `SUT-01`; platform exactly `android`; result exactly `PASS`, `FAIL_RUNNER`, or `NOT_EXECUTED`; runner version `Appium 3.7.0 + appium-uiautomator2-driver <observed driver version>`; then the environment_type, the pinned build identity with its SHA-256, the timestamp, the MC ids of the steps executed, and the artifact paths; no `|` inside any cell.
5. **Stop on every result; the attempt is terminal.** Fill the README Outcome table. Then:
   - **PASS**: record it and STOP. The ORCHESTRATOR transcribes it into the SUT-01 × Android entry of `manifests/compatibility-smoke-status.yaml` after the human research lead approves the recording. The result satisfies the SUT-01 Android compatibility requirement only; it is not evidence about SUT-01 and starts nothing.
   - **FAIL_RUNNER**: the study-level status returns to UNRESOLVED_AFTER_FALLBACK_FAILURE (policy v3, 9.5, 9.7.11) and every campaign requiring mobile execution is blocked; no second remediation qualification exists under policy v3. Appium 3 is not executed again, no other runner is proposed or selected, Appium 2 is never introduced. The failure is not evidence about SUT-01.
   - **NOT_EXECUTED** (harness defect, infrastructure, or build): preserve the record and artifacts unchanged and STOP; there is no automatic retry. A further attempt would need the demonstrated cause corrected, a successor lock if execution-critical bytes change, and a new authorization issued by the human research lead.
   - Mirror transcription happens only after your record exists.
6. **Stop** after the smoke record (or the recorded stop) is written. Do not start, prepare, or configure E06 or any campaign.

## What you never do

- Execute anything without an ISSUED authorization and a separate human dispatch instruction; execute more than once under one authorization; execute iOS.
- Change the SUT, its pinned build or release, the runner or driver versions, Node.js, the substrate, the harness, the locators, the steps, the expected states, or the timeouts — before the issuance except through a successor lock, after the issuance never, and never after observing any result. No outcome-responsive repair: a failure is recorded as observed, never fixed and continued, and never re-run (no GitHub re-run, no second dispatch).
- Record NOT_EXECUTED without positively demonstrating artifacts, or use uncertainty or the consequence of a FAIL_RUNNER to exclude an unfavorable runner outcome.
- Infer one platform's or one SUT's result from another's.
- Compare Appium with Mobilewright, benchmark, or report duration as a criterion.
- Cite any smoke artifact as evidence about SUT-01 or any ecosystem, in any audit, adjudication, campaign result, or analysis.
- Write into the SUT-02 smoke tree, the Mobilewright formal or quarantine trees, into `raw-data/`, or anywhere outside the boundary above; label anything MEASURED_EXPERIMENT.
- Restore, remediate, or amend anything about the study-level mobile-runner status without the explicit human instruction and the protocol decision that policy v3 requires.
- Introduce Appium 2 under any outcome.
- Start E06.
