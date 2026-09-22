# manifests/provisioning/ — One-Time Provisioning Records

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). Protocol v1/v2 FROZEN-PRE-DATA (the provisioning-record envelope is protocol/setup-effort-v2.md, section 8, carried forward unchanged from v1). This storage location was frozen by explicit human decision, 2026-09-16, resolving the "Storage: ... (candidate — not frozen)" location left open in protocol/setup-effort-v1.md, section 8.

## Purpose

This directory holds provisioning records: descriptive reproducibility metadata for ONE-TIME PROVISIONING (protocol/setup-effort-v2.md, section 2) — the work performed once to make an instance of an evaluated ecosystem available in a given environment, before any run (installing dependencies, building, first emulator or simulator setup, downloading binaries, starting services, obtaining or configuring a hosted account).

Provisioning records are descriptive reproducibility metadata only. They are never part of the primary Setup Effort comparison (protocol/setup-effort-v2.md, sections 3 and 7; protocol/study-design-v1.md, section 11, rule 11), never counted in Required Actions, and never converted into a score. They must not be mixed into E02-state-establishment or E03-resetability Required Actions observations, which cover per-run / per-condition setup only.

## Who writes here

Only the ORCHESTRATOR role writes under `manifests/` (protocol/agent-governance-v1.md; manifests/README.md), the same rule that governs `sut-manifest.yaml` and `toolchain-manifest.yaml`. A provisioning record is authored by the ORCHESTRATOR from the provisioning facts relayed by whichever role actually performed the provisioning (an auditor setting up its own SUT's instance, or QUALIFIER-MOBILE-01 setting up the qualification build) — the same pin-from-relayed-observation pattern already used for `sut-manifest.yaml` provenance (manifests/README.md, "Provenance sequence"). No other role edits a file in this directory.

## Current status

- First records written 2026-09-22 under the explicit human authorization for NON-MEASURED PRE-START provisioning of the E03-resetability CS-001 conditions (operator workstation): `SUT-01/SUT01-PROV-0001.yaml` (LOCAL web+api), `SUT-02/SUT02-PROV-0001.yaml` (LOCAL web), `SUT-02/SUT02-PROV-0002.yaml` (EMULATED android), `SUT-02/SUT02-PROV-0003.yaml` (SIMULATED ios — attempted, not verified), `SUT-03/SUT03-PROV-0001.yaml` (LOCAL web+api), `SUT-04/SUT04-PROV-0001.yaml` (LOCAL web+api), `SUT-05/SUT05-PROV-0001.yaml` (LOCAL api+web). Each is descriptive reproducibility metadata; `campaigns_served` is empty because no campaign has used any instance (E03 is NOT_STARTED). The matching environment-verification evidence is under `experiments/E03-resetability/environment-verification/`.
- A record is filed at `manifests/provisioning/<sut-id>/<provisioning_id>.yaml` (protocol/setup-effort-v2.md, section 8), one file per environment instance used by a campaign, referenced by every campaign that reuses that instance.

## Envelope record

Each provisioning record uses the envelope defined in protocol/setup-effort-v2.md, section 8 (`provisioning_id`, `sut_id`, `environment_type`, `instance_identifier`, `sut_provenance`, `steps`, `duration`, `performed_by`, `date`, `campaigns_served`, `notes`); this document does not restate that envelope. Its `steps` field is an ordered list, one entry per provisioning operation, each following the per-step template below.

## Per-step template

A future provisioning record's `steps` entries should be able to capture the following fields. No field is required when it does not apply to a given step (for example `required_external_dependency` is empty for a step with no external dependency); an empty or inapplicable field is left out or recorded as `null`, never guessed.

| Field | Content |
|---|---|
| `sut_id` | SUT-01 … SUT-06 |
| `component` | The ecosystem component this step provisions (for example web, api, android, ios — as named in manifests/sut-manifest.yaml), or a shared/tooling component |
| `operating_system` | Operating system and version the step ran on, when applicable |
| `prerequisite` | What had to already be present before this step could run |
| `installation_or_build_step` | What was installed, built, downloaded, configured, or started |
| `required_external_dependency` | Any external service, package registry, or network resource the step depended on |
| `estimated_or_observed_duration` | Optional; descriptive only; never added to the Duration secondary metric of protocol/setup-effort-v2.md, section 6 |
| `automation_classification` | AUTOMATED or MANUAL, with a reason for MANUAL |
| `provenance` | Tool name and exact version, source URL, or package identifier used for this step |
| `notes` | Deviations, retries, or anything else needed to reproduce this step |

### Example (illustrative only — no study content; not a populated record)

```yaml
steps:
  - sut_id: SUT-0n
    component: <example: web>
    operating_system: <example: Ubuntu 22.04>
    prerequisite: <example: Node.js runtime present>
    installation_or_build_step: <example: npm ci && npm run build>
    required_external_dependency: <example: npm registry>
    estimated_or_observed_duration: <example: 4m12s, or null>
    automation_classification: AUTOMATED
    provenance: <example: npm 10.x, package.json at pinned commit>
    notes: null
```

## Relation to raw-data/

Provisioning records live here, under `manifests/`, not under `raw-data/`: they are configuration and provenance metadata authored by the ORCHESTRATOR, not raw experimental observations produced by a campaign run (raw-data/README.md). `raw-data/` never holds a provisioning record.
