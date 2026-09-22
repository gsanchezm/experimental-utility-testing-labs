# E05 — Determinism

## Objective

Execute a controlled condition together with a fixed stimulus repeatedly in each evaluated ecosystem (each a system under test, SUT) and classify the observed outcome of each execution into categories defined before execution. The campaign measures whether identical inputs yield identical observable outcomes and characterizes the sources of variation where they do not. Outcome categories must be fixed and recorded before any execution to prevent post hoc classification. Executions run on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance (protocol/study-design-v1.md, section 10.3). Determinism is measured with two rates plus entropy (protocol/repeatability-determinism-v1.md, section 4): CEOR (Conditional Exact Outcome Rate, denominator restricted to executions whose target-state establishment succeeded; NOT_ESTIMABLE, never 0, when none did) and E2E-ROR (End-to-End Reproducible Outcome Rate, denominator = all valid measured attempts); this resolves the former Exact Outcome Rate denominator question (issue (xi), RESOLVED). H3's criterion is fixed as CEOR = 1.00 and Outcome Entropy H(Y) = 0 for conditions classified a priori as deterministic (issue (xx), RESOLVED). The tooling-versus-SUT attribution rule remains DEFERRED-BEFORE-CAMPAIGN (issue (xix)).

## Related research question(s)

- RQ3 Repeatability and Determinism (primary).
- Informs dimension 3 Repeatability and Determinism.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Condition (controlled state plus stimulus, from the catalogue defined before freeze) — candidate.
- Behavior class of the condition, as declared before execution: deterministic / stochastic / time-dependent / external dependency — candidate.

## Future dependent variables (candidate — not frozen)

- CEOR — Conditional Exact Outcome Rate (executions whose outcome category equals the pre-declared expected outcome category / executions in which the required target state was successfully established; NOT_ESTIMABLE, never 0, when no attempt establishes the target state; never derived from the observed modal outcome), per protocol/repeatability-determinism-v1.md, section 4 — candidate.
- E2E-ROR — End-to-End Reproducible Outcome Rate (executions whose outcome category equals the pre-declared expected outcome category / all valid measured attempts), per protocol/repeatability-determinism-v1.md, section 4 (secondary) — candidate.
- Outcome Entropy over the observed outcome categories, computed over the same execution set as CEOR (secondary) — candidate.
- Count of distinct outcome categories observed — candidate.

## Required evidence

- Outcome category definitions recorded before execution, with the criteria for assigning each category.
- One record per execution (attempt), each with a run manifest conforming to schemas/run-manifest.schema.json, including ecosystem id, condition id (`condition`), declared behavior class (`behavior_class`), attempt index (`attempt`), `environment_type`, and assigned outcome category (`outcome.outcome_category`).
- Raw observation artifact per execution supporting the assigned category (for example response body, screenshot, or log excerpt; form TBD before freeze).
- Repetition count per condition per protocol/repeatability-determinism-v1.md, recorded before execution.
- Raw observations in `raw-data/E05-determinism/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
