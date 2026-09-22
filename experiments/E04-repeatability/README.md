# E04 — Repeatability

## Objective

Reproduce a target state repeatedly under a fixed condition in each evaluated ecosystem (each a system under test, SUT) and measure how often the reproduction succeeds. The repetition target is N = 50 attempts per repeatable condition; N = 30 may be used for expensive mobile conditions only when a justification is recorded before that campaign executes (see protocol/repeatability-determinism-v1.md). Every attempt is recorded; no attempt may be discarded. Attempts run on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance (protocol/study-design-v1.md, section 10.3). Between-ecosystem comparison of TSRR (Target-State Reproduction Rate) is made only on canonical scenarios with FROZEN mapping records (protocol/equivalent-scenario-mapping-v1.md) and is classified CONFIRMATORY or EXPLORATORY per protocol/statistical-analysis-plan-v1.md, section 4. The tooling-versus-SUT attribution rule for deviations is DEFERRED-BEFORE-CAMPAIGN and is locked in the campaign configuration (protocol/study-design-v1.md, section 13, issue (xix)).

## Related research question(s)

- RQ3 Repeatability and Determinism (primary).
- Informs dimension 3 Repeatability and Determinism.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Condition (a target state plus its establishment procedure, from the catalogue defined before freeze) — candidate.
- Surface (web / api / android / ios) — candidate.

## Future dependent variables (candidate — not frozen)

- TSRR — Target-State Reproduction Rate (successful target-state establishments / all valid measured attempts) with a Wilson confidence interval, per protocol/repeatability-determinism-v1.md, section 4 — candidate.
- Failure classification per unsuccessful attempt (taxonomy TBD before freeze) — candidate.

## Required evidence

- One run manifest per attempt conforming to schemas/run-manifest.schema.json, including attempt index, ecosystem id, condition id, surface, `environment_type`, and outcome.
- Verification artifact per attempt showing whether the target state was reached.
- Pre-execution record of N for each condition, including the justification if N = 30 is used for a mobile condition.
- Complete attempt sequence with no discarded attempts; aborted or interrupted attempts are recorded as such with a reason.
- Raw observations in `raw-data/E04-repeatability/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
