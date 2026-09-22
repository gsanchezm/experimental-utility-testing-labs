# E08 — Performance

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) offers a known, reproducible ground-truth degraded-performance condition, and whether performance measurement under that condition detects the expected degradation relative to a baseline condition. The campaign assesses the controllability of the degraded condition as much as the measurement itself; an ecosystem without a controllable ground-truth condition is recorded as such rather than measured on an uncontrolled basis. The outcome "no ground-truth condition available" is recorded as a categorical finding about Experimental Breadth / Experimental Controllability and is reported as "no data" with that reason in the RQ5 detection-rate comparison; it is never a detection failure and never a detection rate of zero (protocol/statistical-analysis-plan-v1.md, section 5). Significant load and intentional degradation are applied only to a controlled instance (SELF_HOSTED or LOCAL for the service components under load; protocol/study-design-v1.md, section 10.1) when an open-source deployment of the evaluated version is available and never to a PUBLIC_HOSTED instance; otherwise the condition is NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE (protocol/study-design-v1.md, section 10.3).

## Related research question(s)

- RQ5 Controlled Non-functional Experimentation (primary).
- Informs dimensions 1 Experimental Breadth and 2 Experimental Controllability.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Condition (baseline vs known degraded) — candidate.
- Load profile (profiles TBD before freeze) — candidate.

## Future dependent variables (candidate — not frozen)

- Expected degradation detected (categorical: detected / not detected / no ground-truth condition available) — candidate.
- Measured deltas between baseline and degraded conditions (descriptive only) — candidate.
- Controllability of the degraded condition (categorical, criteria TBD before freeze) — candidate.

## Required evidence

- Condition activation record showing how the degraded condition was enabled and disabled, with provenance of the mechanism.
- One run manifest per condition × load profile execution conforming to schemas/run-manifest.schema.json, carrying `environment_type`.
- Measurement artifacts from the performance tool (raw output, not summaries only).
- Baseline measurement artifacts captured under the same load profile.
- Performance tool is TBD; see manifests/toolchain-manifest.yaml (performance candidate: TBD between appropriate open-source tools). The tool and version used must be recorded in the run manifest.
- Raw observations in `raw-data/E08-performance/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
