# E03-resetability — Controlled-Instance Determination

| Field | Value |
|---|---|
| Prepared by | ORCHESTRATOR |
| Date | 2026-09-21 (source inspection only); revised 2026-09-22 (human-authorized NON-MEASURED PRE-START provisioning and environment verification) |
| Method (2026-09-22) | PROVISIONING + ENVIRONMENT_VERIFICATION by execution on the operator workstation, under the explicit human authorization of 2026-09-22 (cloning, downloading pinned releases, installing dependencies, building, starting controlled instances, installing applications, starting an emulator and a simulator, verifying environment readiness, recording evidence). No E03 measured execution, no Required Actions measurement, no mobile-runner qualification, no executor launch. |
| Machine-readable status | `experiments/E03-resetability/controlled-instance-status.yaml` (read by the measured-execution gate) |

## Vocabulary

Per `protocol/study-design-v1.md`, section 10.1, a controlled instance is the set of components a condition acts on, each running in a controlled environment: SELF_HOSTED or LOCAL for web and api service components; EMULATED or SIMULATED for android and ios builds. A condition whose controlled instance has been established and verified is **CONTROLLED**; otherwise it is **NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE** (section 10.3). CONTROLLED is an experimental-control fact, never a capability score, and never by itself an execution authorization: measured execution on GitHub-hosted runners additionally requires a VERIFIED GitHub Actions environment-verification record per condition and every other campaign gate (`experiments/E03-resetability/ci-cd-execution-model.md`, section 3).

## Per-condition determination (2026-09-22)

| condition_id | SUT | surface | environment_type | pinned_version | provisioning_status | environment_verification_status | controlled_instance_status | evidence_path | notes |
|---|---|---|---|---|---|---|---|---|---|
| E03-CS001-SUT01-WEB | SUT-01 | WEB | LOCAL | `9ca37674…aabe1` (monorepo) | PROVISIONED (`SUT01-PROV-0001`) | VERIFIED | CONTROLLED | `environment-verification/SUT-01-web-api.json` | web served by vite preview of the production build; backend under a standalone CPython 3.12 (SUT requires 3.11/3.12); docker-compose path not used (host Docker daemon unavailable) |
| E03-CS001-SUT01-API | SUT-01 | API | LOCAL | `9ca37674…aabe1` | PROVISIONED (`SUT01-PROV-0001`) | VERIFIED | CONTROLLED | `environment-verification/SUT-01-web-api.json` | `/health` 200; served OpenAPI declares `/api/session/reset` and `/api/session`; `POST /api/session/reset` answers 403 unauthenticated (reachable, SUT01-EV-0006); nothing established or reset |
| E03-CS001-SUT02-WEB | SUT-02 | WEB | LOCAL | `60fdd634…c583` | PROVISIONED (`SUT02-PROV-0001`) | VERIFIED | CONTROLLED | `environment-verification/SUT-02-web.json` | Node 24.21.0 (engines ≥24.9); production build served; 'Reset App State' present in source (SUT02-EV-0002) |
| E03-CS001-SUT02-ANDROID | SUT-02 | ANDROID | EMULATED | release 2.2.0 (`36b012ee…0e7b`), `mda-2.2.0-25.apk` | PROVISIONED (`SUT02-PROV-0002`) | VERIFIED | CONTROLLED | `environment-verification/SUT-02-android.json` | AVD Pixel_API35_Test (android-35 google_apis x86_64, Android 15); installed; MainActivity resumed; 'Reset App State' in resources (SUT02-EV-0008); no mobile runner used; mobile qualification still REQUIRED and NOT_STARTED |
| E03-CS001-SUT02-IOS | SUT-02 | IOS | SIMULATED | release 2.2.2 (`031358f5…31a7`), `SauceLabs-Demo-App.Simulator.zip` | ATTEMPTED (`SUT02-PROV-0003`) | NOT_VERIFIED | NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE | `environment-verification/SUT-02-ios.json` | iPhone 16 / iOS 18.2 booted and the artifact unpacked, but every later `simctl` call hung on this host (HOST_SIMULATOR_SERVICE_UNRESPONSIVE); install/launch not confirmed; designated route: GitHub Actions macos-15 job; mobile qualification REQUIRED |
| E03-CS001-SUT03-WEB | SUT-03 | WEB | LOCAL | `7ab934d7…7609` | PROVISIONED (`SUT03-PROV-0001`) | VERIFIED | CONTROLLED | `environment-verification/SUT-03-web.json` | Node 14.21.3 / npm 6 with `--legacy-peer-deps`; `formdata-node@4` added `--no-save` (undeclared import in a dependency; no SUT source changed); `/` and `/signin` 200; `/api/products` 200 (E01-confirmed api surface, same process); Sign-Out → `store2.session.clearAll()` present (SUT03-EV-0030/0031) |
| E03-CS001-SUT04-WEB | SUT-04 | WEB | LOCAL | `d36bd3f8…2ece1` | PROVISIONED (`SUT04-PROV-0001`) | VERIFIED | CONTROLLED | `environment-verification/SUT-04-web-api.json` | built with a scratch Temurin JDK 26 (pom compiles with `--release 26`) and `mvn clean install -DskipTests`; six services + assets started as `run_locally.sh` does; docker-compose path not used |
| E03-CS001-SUT04-API | SUT-04 | API | LOCAL | `d36bd3f8…2ece1` | PROVISIONED (`SUT04-PROV-0001`) | VERIFIED | CONTROLLED | `environment-verification/SUT-04-web-api.json` | auth, booking, room answer with defined statuses unauthenticated; `DELETE /booking/999999` 403 (reachable, SUT04-EV-0006); no booking created |
| E03-CS001-SUT05-API | SUT-05 | API | LOCAL | `1618a611…e29d` (reports 20.2.0) | PROVISIONED (`SUT05-PROV-0001`) | VERIFIED | CONTROLLED | `environment-verification/SUT-05-api.json` | source build (no darwin x86_64 release archive); login and basket routes answer unauthenticated; stop → unreachable → start → 200 confirms the process-restart mechanism (SUT05-EV-0003); web `/` 200 from the same process |

SUT-06 has no condition in the current configuration (NOT_COMPARABLE on CS-001) and was not provisioned; it remains one of the six SUTs.

Every path in the evidence column is relative to `experiments/E03-resetability/`. Provisioning records: `manifests/provisioning/<sut-id>/`.

## Result

- **8 of 9 conditions are CONTROLLED** on the operator workstation (LOCAL / EMULATED). **1 condition (E03-CS001-SUT02-IOS) remains NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE** on this host.
- **No condition is ready for measured execution**: the GitHub Actions environment verification (the substrate measured runs use) has not run for any condition (it is dispatched only on explicit instruction; the public repository's export log is in `PUBLIC-EXPORT-MANIFEST.yaml`), mobile qualification is NOT_STARTED (governance v2 was frozen 2026-09-22, so that gate is satisfiable), no campaign configuration is locked, and E03 START is not authorized. `controlled-instance-status.yaml` records `measured_execution_readiness: NOT_READY` for all nine.
- `manifests/sut-manifest.yaml` `controlled_instance_available`: **true for SUT-03, SUT-04, SUT-05** (every E01-confirmed-present surface — web and api, in each case served by the single pinned process or service set — verified running from the pinned commit in a controlled environment); **null for SUT-01** (E01-confirmed android and ios surfaces not provisioned: no E03 condition uses them), **null for SUT-02** (ios not verified), **null for SUT-06** (not provisioned). Never inferred; per-condition decisions live in `controlled-instance-status.yaml`, not in the boolean (section 10.5: "the boolean summarizes, it does not decide").

## What this determination is not

- Not a measurement: no canonical state was established, no reset under evaluation was performed, no Required Action was counted, no run manifest was written, nothing entered `raw-data/`.
- Not a qualification: no mobile test runner was used; the Android and iOS checks used `adb` and `simctl` only.
- Not an authorization: E03 START, mobile qualification execution, and executor launch remain human decisions.

## Historical: 2026-09-21 source-inspection-only determination

Superseded by the table above; retained for the record (full text at commit `b67ac64`). All nine CS-001 conditions and the two later-excluded CS-002 conditions were then `NOT_EXECUTION_VERIFIED` with candidate `environment_type` values (SELF_HOSTED for web/api, EMULATED, SIMULATED) from `manifests/sut-manifest.yaml` and E01 evidence, and every condition defaulted to `NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE` pending the provisioning authorization that was then `HUMAN_DECISION_REQUIRED` and was granted on 2026-09-22. The candidate SELF_HOSTED label for workstation instances is now recorded precisely as LOCAL (section 10.1); SELF_HOSTED is the label for GitHub-hosted-runner instances (`ci-cd-execution-model.md`, section 6).
