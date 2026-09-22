# E10 — Visual

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) supports a known visual perturbation that can be activated as a ground-truth condition, and whether screenshot comparison between the unperturbed baseline and the perturbed state detects the expected difference. The campaign also records false positives, that is, differences reported when comparing an unperturbed baseline against itself under repeated capture. The outcome "no ground-truth condition available" is recorded as a categorical finding about Experimental Breadth / Experimental Controllability and is reported as "no data" with that reason in the RQ5 detection-rate comparison; it is never a detection failure and never a detection rate of zero (protocol/statistical-analysis-plan-v1.md, section 5). Activating a perturbation is a fault activation and is performed only on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance (protocol/study-design-v1.md, section 10.3).

## Related research question(s)

- RQ5 Controlled Non-functional Experimentation (primary).
- Informs dimensions 1 Experimental Breadth and 2 Experimental Controllability.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Perturbation condition (from a catalogue built during E01 with provenance; TBD before freeze) — candidate.
- Viewport / platform (viewport set and platform list TBD before freeze) — candidate.

## Future dependent variables (candidate — not frozen)

- Expected difference detected (categorical: detected / not detected / no ground-truth condition available) — candidate.
- False positive on unperturbed baseline (categorical, from repeated capture of the same unperturbed state) — candidate.

## Required evidence

- Baseline screenshots (unperturbed state) and perturbed screenshots, each with capture metadata (viewport, platform, timestamp).
- Comparison output (raw difference metrics and difference images where the tool produces them).
- Condition activation record showing how the perturbation was enabled and disabled, with provenance of the mechanism.
- One run manifest per condition × viewport execution conforming to schemas/run-manifest.schema.json, carrying `environment_type`.
- Visual comparison tooling candidate per manifests/toolchain-manifest.yaml; tool and version used must be recorded in the run manifest.
- Raw observations in `raw-data/E10-visual/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
