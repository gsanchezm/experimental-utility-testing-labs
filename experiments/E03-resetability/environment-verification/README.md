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

The same checks run on GitHub-hosted runners through `.github/workflows/e03-environment-verification.yml` (artifact names `E03-ENVIRONMENT_VERIFICATION-<SUT>-<surface>-run<id>-a<attempt>`). Because measured executions run on GitHub-hosted runners, the measured-execution gate requires a VERIFIED GitHub Actions record per condition, transcribed into `controlled-instance-status.yaml` by the ORCHESTRATOR; a workstation record alone does not satisfy that gate. No GitHub Actions record exists yet: the environment-verification workflow is dispatched only on explicit instruction, and none has been given.
