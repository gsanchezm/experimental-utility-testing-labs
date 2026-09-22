# E02 — State Establishment

## Objective

Measure the Required Actions, and secondarily the duration, needed to establish an equivalent target state in each evaluated ecosystem (each a system under test, SUT) starting from a declared starting state. The campaign characterizes the mechanisms each ecosystem offers for reaching a controlled state and the effort those mechanisms demand. "Equivalent target state" across ecosystems means semantic equivalence under protocol/equivalent-scenario-mapping-v1.md: every target state used for inferential comparison is a canonical scenario with a FROZEN mapping record before this campaign executes; an ecosystem without a defensible semantic equivalent is NOT_COMPARABLE for that scenario (not a score, not a zero). One-time provisioning of each instance is recorded descriptively in a provisioning record and is not counted; only per-run / per-condition setup enters Required Actions (protocol/setup-effort-v1.md).

## Related research question(s)

- RQ2 Controllability, Observability, Automation Affordances, and Setup Effort (primary).
- Informs dimensions 2 Experimental Controllability and 6 Setup Effort.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Target state (canonical_scenario_id from the frozen scenario mapping records, protocol/equivalent-scenario-mapping-v1.md) — candidate.
- Surface (web / api / android / ios) — candidate.
- Establishment mechanism(s) used (`establishment_mechanisms`; frozen vocabulary: UI_FLOW, API_SEED, DIRECT_ROUTE, DEEP_LINK, FIXTURE, PREDEFINED_ACCOUNT, CONFIGURATION, APP_STATE_CONTROL, NONE, OTHER — protocol/setup-effort-v1.md, section 10; one or more per run) — candidate.

## Future dependent variables (candidate — not frozen)

- Required action count, broken down by the six action classes defined in protocol/setup-effort-v1.md section 4 (Action classes) (counting rules are candidate — not frozen) — candidate.
- Establishment success / failure (categorical) — candidate.
- Duration from declared starting state to verified target state (secondary) — candidate.
- Manual intervention required (categorical, with description) — candidate.

## Required evidence

- Run manifest per run conforming to schemas/run-manifest.schema.json, including ecosystem id, canonical scenario (`scenario` = canonical_scenario_id, as in every campaign that uses canonical scenarios), target state id (`target_state_id`: the target state defined by that scenario's frozen mapping record; the exact per-run convention is fixed in this campaign's configuration, protocol/change-control-v1.md section 7), surface (`platform`), `environment_type`, establishment mechanism(s) (`establishment_mechanisms`, mandatory and non-empty for E02 runs; protocol/setup-effort-v1.md, section 10), declared starting state (`starting_state_id`), and outcome.
- Frozen mapping record for every canonical scenario used, listed in the campaign configuration (protocol/change-control-v1.md, section 7), with the comparability marker per ecosystem.
- Provisioning record per instance used (protocol/setup-effort-v1.md, section 8), descriptive only.
- Ordered action list for the run, recorded in the run manifest `actions` field (schemas/run-manifest.schema.json): every action taken, its class per protocol/setup-effort-v1.md section 4 (Action classes), its position, whether it was a retry, and the reason for any manual action.
- Verification artifact confirming the target state was reached (for example a response record, screenshot, or state dump; form TBD before freeze).
- Provenance of the ecosystem artifacts exercised (repository, commit_sha_or_release), recorded as null when unknown.
- Record of any manual intervention, including what was done and why.
- Raw observations in `raw-data/E02-state-establishment/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
