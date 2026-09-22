# Mobilewright Qualification

## Status

NOT STARTED.

Template only. No qualification run has been executed and no result, attribution, or decision field below has been filled. Nothing recorded here is evidence about any system under test (SUT). Governing policy: protocol/mobile-runner-policy-v1.md (DRAFT). Owner: QUALIFIER-MOBILE-01 (protocol/agent-governance-v1.md).

## Gate definition

Mobilewright must pass this gate before use in any experimental campaign for the Android Native or iOS Native modalities. The gate consists of the scenarios defined in protocol/mobile-runner-policy-v1.md, Section 4, each exercised on both platforms of Section 6:

| ID | Scenario | Purpose |
|---|---|---|
| MQ1 | Login → Catalog | Navigation and selector compatibility |
| MQ2 | Catalog → Product Interaction | Native control interaction |
| MQ3 | API State Seed → Deep Link → Target UI State | Direct controlled mobile state establishment |

Platforms: Android emulator (environment_type EMULATED) and iOS Simulator (environment_type SIMULATED). Six scenario × platform combinations. The purpose of the gate is to determine whether Mobilewright supports the mobile capabilities this study requires (mandatory capabilities MC-01 … MC-10, protocol/mobile-runner-policy-v1.md, Section 5). It is not a benchmark against Appium 3.

## Qualification SUT

The qualification SUT is OmniPizza (SUT-01), designated in protocol/mobile-runner-policy-v1.md, Section 3. Results obtained on it qualify the runner only; they are not evidence about OmniPizza or any other evaluated ecosystem, confer no familiarity advantage and no privileged interpretation, and are disclosed as a study limitation. The build is pinned by the ORCHESTRATOR under `qualification_build` in manifests/toolchain-manifest.yaml before the first run and copied verbatim into the table below by QUALIFIER-MOBILE-01, which never selects or changes it; a discrepancy between the pinned record and the build obtained is recorded in qualification/unresolved.md (created on first use), never corrected here or in the manifest.

| Field | Value |
|---|---|
| Qualification SUT | OmniPizza (SUT-01) |
| Repository | null / TBD (copied from manifests/toolchain-manifest.yaml qualification_build) |
| Commit SHA or release (or strongest reproducible identifier) | null / TBD (copied from manifests/toolchain-manifest.yaml qualification_build) |
| Android build identity | null / TBD (copied from manifests/toolchain-manifest.yaml qualification_build) |
| iOS build identity | null / TBD (copied from manifests/toolchain-manifest.yaml qualification_build) |
| Pinned by / date (from the manifest) | null / TBD |
| Copied by / date | null / TBD |

## Scenario realization (recorded before the first run)

The concrete realization of each scenario on the qualification SUT is recorded here before any run and is identical for every execution.

| Scenario | Start state | Concrete steps (screens, identifiers, controls) | API seed (MQ3 only) | Deep link (MQ3 only) | Pre-declared terminal UI state |
|---|---|---|---|---|---|
| MQ1 | null / TBD | null / TBD | — | — | null / TBD |
| MQ2 | null / TBD | null / TBD (includes at least one scroll or swipe) | — | — | null / TBD |
| MQ3 | null / TBD | null / TBD | null / TBD | null / TBD | null / TBD |

## Pass criteria (protocol/mobile-runner-policy-v1.md, Section 7)

- N = 10 clean measured executions per scenario × platform combination (60 in total).
- Pass requires all four: (1) 100% support of MC-01 … MC-10 on both platforms; (2) 10/10 successful measured executions for every combination; (3) no repeated runner-caused blocker for any mandatory capability; (4) no manual intervention inside any measured scenario.
- Warm-up executions may precede the measured executions of a combination and never count toward N; a runner-caused warm-up failure is still recorded and counts under the repeated-blocker criterion (3).
- Infrastructure failures unrelated to Mobilewright are recorded as EXCLUDED with an attribution record and replaced by an additional measured execution; a failure whose attribution is uncertain is runner-caused.
- Execution duration is secondary evidence only. Mobilewright must NOT be selected solely because it is faster.

## Execution log

One row per execution (warm-up, measured, or excluded). Fields per protocol/mobile-runner-policy-v1.md, Section 7.1. No row exists.

| execution_id | combination (MQn × platform) | kind (WARMUP / MEASURED / EXCLUDED) | attempt | timestamp | environment_type | Mobilewright version | outcome (SUCCESS / FAILURE / EXCLUDED) | duration | artifacts | notes |
|---|---|---|---|---|---|---|---|---|---|---|

## Results per combination

| Combination | Warm-ups (count) | Measured successes / 10 | Excluded (count) | Runner-caused failures (count) | Manual intervention (count) | Result |
|---|---|---|---|---|---|---|
| MQ1 × Android emulator | | | | | | |
| MQ1 × iOS Simulator | | | | | | |
| MQ2 × Android emulator | | | | | | |
| MQ2 × iOS Simulator | | | | | | |
| MQ3 × Android emulator | | | | | | |
| MQ3 × iOS Simulator | | | | | | |

## Capability support

| Capability | Android emulator (SUPPORTED / UNSUPPORTED) | iOS Simulator (SUPPORTED / UNSUPPORTED) | Runner-caused failures (count, execution ids) | Notes |
|---|---|---|---|---|
| MC-01 Install and launch | | | | |
| MC-02 Locate by stable identifier | | | | |
| MC-03 Text entry | | | | |
| MC-04 Tap / press native control | | | | |
| MC-05 Scroll / swipe | | | | |
| MC-06 Screen navigation and verification | | | | |
| MC-07 Deep link with parameters | | | | |
| MC-08 Read UI state | | | | |
| MC-09 App state reset between executions | | | | |
| MC-10 Artifact capture | | | | |

## Attribution records (excluded executions)

One row per excluded execution. An exclusion without a complete row is invalid and the execution counts as a failed measured execution. Attributed cause is never RUNNER.

| execution_id | combination | timestamp | failure description | attributed cause (INFRASTRUCTURE / SUT_INSTANCE / API_SEED / OPERATOR / OTHER) | demonstrating artifacts | recorded_by |
|---|---|---|---|---|---|---|

## Secondary evidence — duration

| Combination | Median duration | IQR | Notes |
|---|---|---|---|
| MQ1 × Android emulator | | | |
| MQ1 × iOS Simulator | | | |
| MQ2 × Android emulator | | | |
| MQ2 × iOS Simulator | | | |
| MQ3 × Android emulator | | | |
| MQ3 × iOS Simulator | | | |

## Prerequisites

All items must be satisfied before the first run.

- [ ] protocol/mobile-runner-policy-v1.md is in state FROZEN-PRE-DATA with human approval recorded per protocol/change-control-v1.md
- [ ] Mobilewright and Appium 3 versions are recorded in manifests/toolchain-manifest.yaml (currently null)
- [ ] Qualification SUT build is pinned by the ORCHESTRATOR in manifests/toolchain-manifest.yaml and copied verbatim above by QUALIFIER-MOBILE-01
- [ ] Scenario realization is recorded above
- [ ] Environment is recorded in manifests/toolchain-manifest.yaml by the ORCHESTRATOR and copied below
- [ ] Explicit instruction to execute the gate, issued by a human and relayed by the ORCHESTRATOR, has been received and is recorded below

### Environment record

| Field | Value |
|---|---|
| Mobilewright version | null / TBD |
| Android emulator identity (device profile, OS image) | null / TBD |
| iOS Simulator identity (device, OS version) | null / TBD |
| Host platform | null / TBD |
| Date of first run | null / TBD |
| Instruction to execute (date, human source, relaying role) | null / TBD |

## Decision record

| Field | Value |
|---|---|
| Date | |
| Gate result (PASS / FAIL) | |
| Failed criteria and capabilities (if FAIL) | |
| Decision (one of: Mobilewright, Appium 3) | |
| Rationale | |
| Recorded by | |

The decision is also recorded in manifests/toolchain-manifest.yaml and in the change log per protocol/change-control-v1.md (protocol/mobile-runner-policy-v1.md, Section 8). If the runner is Appium 3, the compatibility smoke (qualification/compatibility-smoke/) is executed with Appium 3. Appium 2 is never introduced.

## Warning

Do not execute qualification until explicitly instructed and until protocol/mobile-runner-policy-v1.md is frozen. Do not fill any result, attribution, or decision field before a run has actually occurred. Do not use anything recorded here as evidence about any SUT.
