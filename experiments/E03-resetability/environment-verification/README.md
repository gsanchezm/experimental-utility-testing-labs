# E03-resetability — Environment Verification Records (NON-MEASURED)

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). This directory holds the ENVIRONMENT_VERIFICATION evidence produced when a controlled instance of a system under test (SUT) is provisioned for an E03-resetability condition and its surface and reset mechanism are checked for reachability. Every record here carries `record_class: ENVIRONMENT_VERIFICATION` and `measured_experiment: false`.

## What a record is, and is not

- It verifies that the pinned SUT component runs in a controlled environment (protocol/study-design-v1.md, section 10.1: LOCAL, SELF_HOSTED, EMULATED, SIMULATED), that the surface answers, and that the reset mechanism named in the frozen mapping record (`experiments/scenario-mappings/CS-001.yaml`) is reachable (an endpoint responds with a defined status, a control is present in the served source or installed artifact). It records tool versions, the pinned provenance, the host, timestamps, and an explicit `verification_result` (VERIFIED or NOT_VERIFIED).
- It never establishes the canonical state, never performs the reset under evaluation, never counts Required Actions, and never produces a run manifest. It is one-time provisioning evidence (protocol/setup-effort-v2.md, section 2) and is never written under `raw-data/` or used in any analysis.
- One-time provisioning steps are recorded separately in `manifests/provisioning/<sut-id>/<provisioning_id>.yaml`; the per-condition controlled-instance determination that consumes these records is `experiments/E03-resetability/controlled-instance-status.yaml` (machine-readable, read by the measured-execution gate) and `controlled-instance-determination.md` (narrative).

## Records (2026-09-22, operator workstation, human-authorized NON-MEASURED PRE-START provisioning)

| File | SUT | Surface(s) | Conditions | environment_type | Result |
|---|---|---|---|---|---|
| `SUT-01-web-api.json` | SUT-01 | WEB, API | E03-CS001-SUT01-WEB, -API | LOCAL | VERIFIED |
| `SUT-02-web.json` | SUT-02 | WEB | E03-CS001-SUT02-WEB | LOCAL | VERIFIED |
| `SUT-02-android.json` | SUT-02 | ANDROID | E03-CS001-SUT02-ANDROID | EMULATED | VERIFIED |
| `SUT-02-ios.json` | SUT-02 | IOS | E03-CS001-SUT02-IOS | SIMULATED | NOT_VERIFIED (host simulator service unresponsive) |
| `SUT-03-web.json` | SUT-03 | WEB | E03-CS001-SUT03-WEB | LOCAL | VERIFIED (the E01-confirmed api surface, served by the same process, was probed too) |
| `SUT-04-web-api.json` | SUT-04 | WEB, API | E03-CS001-SUT04-WEB, -API | LOCAL | VERIFIED |
| `SUT-05-api.json` | SUT-05 | API | E03-CS001-SUT05-API | LOCAL | VERIFIED |

SUT-06 has no E03 condition in the current configuration (NOT_COMPARABLE on CS-001) and was not provisioned; it remains in the E03 population.

## GitHub Actions records

The same checks run on GitHub-hosted runners through `.github/workflows/e03-environment-verification.yml` (artifact names `E03-ENVIRONMENT_VERIFICATION-<SUT>-<surface>-run<id>-a<attempt>`). Because measured executions run on GitHub-hosted runners, the measured-execution gate requires a VERIFIED GitHub Actions record per condition, transcribed into `controlled-instance-status.yaml` by the ORCHESTRATOR; a workstation record alone does not satisfy that gate. The workflow ran four times. Run 37074152972 (2026-10-02, attempt 1, operation OP-ENV-01) ran at public main 34c0453 with the workflow revision whose canonical SHA-256 is 1aa32454...; its artifacts are imported byte-exact under `github-actions/run37074152972-a1/` and were transcribed on 2026-10-03 (operation OP-ENV-02). The workflow was then corrected (operation OP-ENV-03, commit 3852edc; lint correction OP-CI-01, commit b1124a8), and run 37206291883 (2026-10-04, attempt 1, operation OP-ENV-04 second issue) ran at public main 08ef8c8 (export v31) with the corrected revision, canonical SHA-256 f4a80288...; its artifacts are imported byte-exact under `github-actions/run37206291883-a1/` and transcribed on 2026-10-04 (operation OP-ENV-05). The workflow was corrected again (operation OP-ENV-06, commit 516cd17: the iOS presence check reads the raw bytes of the installed app bundle, SUT-05 is provisioned by the SUT README's Packaged Distributions route of its pinned release, and every job replaces runner host paths in its kept text artifacts by `<host-path>` before upload), and run 37265782721 (2026-10-05, attempt 1, operation OP-ENV-07) ran at public main f0071bf (export v32) with that revision, canonical SHA-256 5ec3f22b...; its artifacts are imported byte-exact under `github-actions/run37265782721-a1/` and transcribed on 2026-10-05 (operation OP-ENV-08). The workflow was corrected again (operation OP-CI-02, commit 3490db2: the SUT-05 job starts its instance in its own session and process group, stops the whole group with SIGTERM, waits until port 3000 refuses connections before it evaluates the stop, records the process tree before the stop, after it, and after the restart, and fails closed), and run 37354458611 (2026-10-05, attempt 1, operation OP-ENV-09, input target SUT-05: only the job sut-05-api ran, the six other jobs were skipped) ran at public main 4261d15 (export v33) with that revision, canonical SHA-256 fcd26a91...; its artifact is imported byte-exact under `github-actions/run37354458611-a1/` and transcribed on 2026-10-05 (operation OP-ENV-10). Each `IMPORT-RECORD.yaml` lists each archive's GitHub digest and every member's SHA-256. The latest run that ran a job for a condition governs: `controlled-instance-status.yaml` carries the values of run 37265782721 for eight conditions and of run 37354458611 for E03-CS001-SUT05-API, and the rows of runs 37074152972 and 37206291883 and the `sut-05-api` row of run 37265782721 below are history.

| Run | Job | GitHub job conclusion | Record (`verification_result`) | Conditions | Status from that run |
|---|---|---|---|---|---|
| 37074152972 | `sut-01-web-api` | success | `github-actions/run37074152972-a1/sut-01-web-api/environment-verification.json` (VERIFIED) | E03-CS001-SUT01-WEB, -API | VERIFIED |
| 37074152972 | `sut-02-web` | success | `github-actions/run37074152972-a1/sut-02-web/environment-verification.json` (VERIFIED) | E03-CS001-SUT02-WEB | VERIFIED |
| 37074152972 | `sut-03-web` | success | `github-actions/run37074152972-a1/sut-03-web/environment-verification.json` (VERIFIED) | E03-CS001-SUT03-WEB | VERIFIED |
| 37074152972 | `sut-02-android` | failure | `github-actions/run37074152972-a1/sut-02-android/environment-verification.json` (NOT_VERIFIED) | E03-CS001-SUT02-ANDROID | NOT_VERIFIED (workflow defect) |
| 37074152972 | `sut-02-ios` | failure | `github-actions/run37074152972-a1/sut-02-ios/environment-verification.json` (NOT_VERIFIED; empty provenance) | E03-CS001-SUT02-IOS | NOT_VERIFIED (workflow defect) |
| 37074152972 | `sut-04-web-api` | failure | no record (the artifact holds the Compose version and an empty service log) | E03-CS001-SUT04-WEB, -API | NOT_VERIFIED (provisioning defect) |
| 37074152972 | `sut-05-api` | failure | no record, no artifact | E03-CS001-SUT05-API | NOT_VERIFIED (provisioning failure; root cause not established) |
| 37206291883 | `sut-01-web-api` | success | `github-actions/run37206291883-a1/sut-01-web-api/environment-verification.json` (VERIFIED) | E03-CS001-SUT01-WEB, -API | VERIFIED |
| 37206291883 | `sut-02-web` | success | `github-actions/run37206291883-a1/sut-02-web/environment-verification.json` (VERIFIED) | E03-CS001-SUT02-WEB | VERIFIED |
| 37206291883 | `sut-02-android` | success | `github-actions/run37206291883-a1/sut-02-android/environment-verification.json` (VERIFIED) | E03-CS001-SUT02-ANDROID | VERIFIED |
| 37206291883 | `sut-03-web` | success | `github-actions/run37206291883-a1/sut-03-web/environment-verification.json` (VERIFIED) | E03-CS001-SUT03-WEB | VERIFIED |
| 37206291883 | `sut-04-web-api` | success | `github-actions/run37206291883-a1/sut-04-web-api/environment-verification.json` (VERIFIED) | E03-CS001-SUT04-WEB, -API | VERIFIED |
| 37206291883 | `sut-02-ios` | failure | `github-actions/run37206291883-a1/sut-02-ios/environment-verification.json` (NOT_VERIFIED) | E03-CS001-SUT02-IOS | NOT_VERIFIED (0 occurrences of the reset label in the app's executable; cause not established; check-design item) |
| 37206291883 | `sut-05-api` | failure | `github-actions/run37206291883-a1/sut-05-api/environment-verification.json` (NOT_VERIFIED; provisioning failed, verification skipped) | E03-CS001-SUT05-API | NOT_VERIFIED (the SUT's own sbom step failed at the pinned commit; attribution not established) |
| 37265782721 | `sut-01-web-api` | success | `github-actions/run37265782721-a1/sut-01-web-api/environment-verification.json` (VERIFIED) | E03-CS001-SUT01-WEB, -API | VERIFIED |
| 37265782721 | `sut-02-web` | success | `github-actions/run37265782721-a1/sut-02-web/environment-verification.json` (VERIFIED) | E03-CS001-SUT02-WEB | VERIFIED |
| 37265782721 | `sut-02-android` | success | `github-actions/run37265782721-a1/sut-02-android/environment-verification.json` (VERIFIED) | E03-CS001-SUT02-ANDROID | VERIFIED |
| 37265782721 | `sut-02-ios` | success | `github-actions/run37265782721-a1/sut-02-ios/environment-verification.json` (VERIFIED) | E03-CS001-SUT02-IOS | VERIFIED (the reset label counted once in the installed app bundle, the compiled Menu storyboard scene) |
| 37265782721 | `sut-03-web` | success | `github-actions/run37265782721-a1/sut-03-web/environment-verification.json` (VERIFIED) | E03-CS001-SUT03-WEB | VERIFIED |
| 37265782721 | `sut-04-web-api` | success | `github-actions/run37265782721-a1/sut-04-web-api/environment-verification.json` (VERIFIED) | E03-CS001-SUT04-WEB, -API | VERIFIED |
| 37265782721 | `sut-05-api` | failure | `github-actions/run37265782721-a1/sut-05-api/environment-verification.json` (NOT_VERIFIED; provisioning by the Packaged Distributions route succeeded, the process-restart check failed) | E03-CS001-SUT05-API | NOT_VERIFIED (the API still answered after the stop signals; cause not established; verification-step item, OP-CI-02) |
| 37354458611 | `sut-05-api` | success | `github-actions/run37354458611-a1/sut-05-api/environment-verification.json` (VERIFIED) | E03-CS001-SUT05-API | VERIFIED (target SUT-05; the six other jobs skipped; the process-group stop closed port 3000 in 1.0 s and the restart answered 200; the process tree npm start, sh -c node build/app, node build/app recorded) |

Every GitHub Actions record verifies reachability and presence only: no state is established and no reset is exercised.
