# Per-SUT Compatibility Smoke

## Status

NOT STARTED.

Template only. No smoke has been executed and no field below has been filled. Nothing recorded here is evidence about any system under test (SUT). Governing policy: protocol/mobile-runner-policy-v1.md, Section 9 (DRAFT). Owner: QUALIFIER-MOBILE-01 (protocol/agent-governance-v1.md).

## Purpose

After the study mobile runner is selected (Mobilewright by passing the qualification gate, or Appium 3 by the switch rule) and after E01 has verified which ecosystems have an Android or iOS surface, each mobile-capable ecosystem receives one lightweight compatibility smoke per platform before it participates in E06, E07, or any other campaign exercising its Android Native or iOS Native modality. The smoke establishes only that the selected runner can drive that ecosystem's pinned mobile build. It is not Mobilewright-versus-Appium benchmarking, records no duration comparison, and produces no evidence about any ecosystem.

## Scope per ecosystem × platform

One execution from a clean state that: installs and launches the pinned build (MC-01); locates one element by stable identifier (MC-02); performs one navigation (MC-06); performs one native control interaction (MC-04); reads one UI state (MC-08); captures artifacts (MC-10). One successful execution passes the smoke for that ecosystem × platform.

## Prerequisites

- [ ] The study mobile runner has been selected and recorded in manifests/toolchain-manifest.yaml and in the change log
- [ ] E01 has verified the mobile surfaces of every ecosystem (manifests/sut-manifest.yaml presence values)
- [ ] The mobile builds of every mobile-capable ecosystem are pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml
- [ ] Explicit instruction to execute the smoke, issued by a human and relayed by the ORCHESTRATOR, has been received and is recorded below

| Field | Value |
|---|---|
| Selected runner and version | null / TBD |
| Android emulator identity | null / TBD |
| iOS Simulator identity | null / TBD |
| Host platform | null / TBD |
| Instruction to execute (date, human source, relaying role) | null / TBD |

## Smoke records

One row per ecosystem × platform for which E01 confirmed a surface. Result values: PASS; FAIL_RUNNER (runner-caused failure on a mandatory capability, triggers the switch rule for the whole study); NOT_EXECUTED (pinned build could not be obtained or installed; reason required; not a runner failure). A platform whose surface E01 recorded as ABSENT has no row. Every ecosystem, SUT-01 included, is recorded under the same definition.

| sut_id | platform (android / ios) | environment_type (EMULATED / SIMULATED) | pinned build identity | timestamp | runner version | steps executed (MC ids) | result | artifacts | notes / reason |
|---|---|---|---|---|---|---|---|---|---|

## Outcome

| Field | Value |
|---|---|
| Date | |
| All mobile-capable ecosystems passed (YES / NO) | |
| Runner-caused failures (sut_id, platform, capability) | |
| Switch rule triggered (YES / NO) | |
| Recorded by | |

A FAIL_RUNNER result for any ecosystem means the runner cannot reliably support that capability for the experimental SUT set; the switch rule of protocol/mobile-runner-policy-v1.md, Section 8, applies to the whole study and the smoke is repeated with the fallback runner, Appium 3. Appium 2 is never introduced.

## Warning

Do not execute until explicitly instructed and until protocol/mobile-runner-policy-v1.md is frozen. Do not fill any field before an execution has actually occurred. Do not use anything recorded here as evidence about any SUT.
