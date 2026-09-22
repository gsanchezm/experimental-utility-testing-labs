# E11 — Security

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) provides a known vulnerable condition, such as a documented intentional vulnerability class, that can serve as ground truth, and whether a security verification method applied to the running instance detects it. Detection is judged against the known condition, not against the total number of findings a tool reports. All security testing is confined to the evaluated SUT instances that the study itself deploys and controls (environment_type SELF_HOSTED or LOCAL for the service components under test, EMULATED or SIMULATED for mobile application builds; protocol/study-design-v1.md, section 10.1); no verification may be directed at any third-party production system or PUBLIC_HOSTED instance. An ecosystem for which no controlled instance can be established records NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE for every active-testing condition (protocol/study-design-v1.md, section 10.3); this is an experimental-control fact, not a capability score. The outcome "no ground-truth condition available" is recorded as a categorical finding about Experimental Breadth / Experimental Controllability and is reported as "no data" with that reason in the RQ5 detection-rate comparison; it is never a detection failure and never a detection rate of zero (protocol/statistical-analysis-plan-v1.md, section 5).

## Related research question(s)

- RQ5 Controlled Non-functional Experimentation (primary).
- Informs dimensions 1 Experimental Breadth and 2 Experimental Controllability.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Known vulnerable condition (for example a documented intentional vulnerability class; catalogue built during E01 with provenance, TBD before freeze) — candidate.
- Verification method (for example automated scan vs targeted check; method list TBD before freeze) — candidate.

## Future dependent variables (candidate — not frozen)

- Detection outcome (categorical: detected / not detected / no ground-truth condition available) — candidate.
- Ground-truth availability (categorical: whether a documented, reproducible known vulnerable condition exists) — candidate.

## Required evidence

- Reference to the documentation of the known vulnerable condition, with provenance (repository, commit_sha_or_release, file_path_or_endpoint), recorded as null when unknown.
- Verification artifacts (raw tool output or targeted check records).
- Instance record confirming the target was a study-controlled deployment (deployment identifier, host, and time window), satisfying the authorized-testing scope.
- One run manifest per condition × verification method execution conforming to schemas/run-manifest.schema.json, carrying `environment_type` (controlled environments only: SELF_HOSTED or LOCAL for services, EMULATED or SIMULATED for mobile builds).
- Security tooling candidate per manifests/toolchain-manifest.yaml; tool and version used must be recorded in the run manifest.
- Raw observations in `raw-data/E11-security/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
