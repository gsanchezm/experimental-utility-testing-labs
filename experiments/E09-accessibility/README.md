# E09 — Accessibility

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) provides a known accessibility violation that can be activated as a ground-truth condition, and whether an accessibility scanner run against the affected page or state detects it. Per the frozen modality list, the Accessibility modality is Web only; this campaign does not scan native mobile surfaces. Detection is judged against the known violation, not against the scanner's total finding count. The outcome "no ground-truth condition available" is recorded as a categorical finding about Experimental Breadth / Experimental Controllability and is reported as "no data" with that reason in the RQ5 detection-rate comparison; it is never a detection failure and never a detection rate of zero (protocol/statistical-analysis-plan-v1.md, section 5). Activating a known violation is a fault activation and is performed only on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance; a documented always-on violation may be scanned on any environment type, with the environment recorded (protocol/study-design-v1.md, section 10.3).

## Related research question(s)

- RQ5 Controlled Non-functional Experimentation (primary).
- Informs dimensions 1 Experimental Breadth and 2 Experimental Controllability.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Known violation condition (from a catalogue built during E01 with provenance; TBD before freeze) — candidate.
- Page / state under scan — candidate.

## Future dependent variables (candidate — not frozen)

- Detection outcome (categorical: detected / not detected / no ground-truth condition available) — candidate.
- Ground-truth availability (categorical: whether a documented, activatable known violation exists) — candidate.

## Required evidence

- Condition activation record showing how the known violation was enabled, with provenance of the mechanism.
- One run manifest per condition × page execution conforming to schemas/run-manifest.schema.json, carrying `environment_type`.
- Scanner output (raw, machine-readable where the tool provides it).
- DOM snapshot of the scanned page or state at scan time.
- Accessibility scanner candidate per manifests/toolchain-manifest.yaml; tool and version used must be recorded in the run manifest.
- Raw observations in `raw-data/E09-accessibility/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
