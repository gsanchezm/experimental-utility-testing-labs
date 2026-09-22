# E07 — Cross-layer Continuity

## Objective

Determine whether a state established through one layer of an evaluated ecosystem (each a system under test, SUT) is verifiable through another layer. The candidate layer pairs are API->Web, API->Android, API->iOS, and Web->API. The campaign records whether the same entity or state is observable across layers, how many actions the verification requires, and, secondarily, the latency between establishment and verifiability. Entities and states used for inferential comparison are canonical scenarios with FROZEN mapping records (protocol/equivalent-scenario-mapping-v1.md; observable_oracle_class OTHER, with free text naming the cross-layer consistency check, per the frozen controlled vocabulary of protocol/equivalent-scenario-mapping-v1.md, section 3); an ecosystem without a defensible semantic equivalent is NOT_COMPARABLE for that scenario. State-changing establishment steps run on a controlled instance when an open-source deployment of the evaluated version is available and never against a PUBLIC_HOSTED instance when the state would be visible to other users of a shared instance or would persist beyond the experimenter's own session (protocol/study-design-v1.md, section 10.3). Mobile layers are exercised only for ecosystems that passed the per-SUT compatibility smoke (protocol/mobile-runner-policy-v1.md, section 9).

## Related research question(s)

- RQ4 Cross-platform and Cross-layer Integration (primary).
- Informs dimension 4 Cross-platform and Cross-layer Integration; relates to the cross-cutting property Cross-layer State Continuity in protocol/cross-cutting-properties-v1.md.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Source layer (the layer through which the state is established) — candidate.
- Verification layer (the layer through which the state is observed) — candidate.
- Entity / state type (canonical_scenario_id with a FROZEN mapping record, protocol/equivalent-scenario-mapping-v1.md) — candidate.

## Future dependent variables (candidate — not frozen)

- Continuity success (categorical: verified / not verified / not applicable / not testable) — candidate.
- Required actions to perform the cross-layer verification — candidate.
- Latency from establishment to verifiability (secondary) — candidate.

## Required evidence

- One run manifest per source layer × verification layer × entity execution conforming to schemas/run-manifest.schema.json, including ecosystem id, both layers (`source_layer` and `verification_layer`), entity/state type (`scenario` = canonical_scenario_id), `environment_type`, and outcome.
- Entity identifiers created or referenced during establishment, recorded so that the verification can be traced to the same entity.
- Request and response records for API-side steps.
- Verification artifacts from the verification layer (for example screenshot, response record, or state dump; form TBD before freeze).
- Explicit record for every layer pair that is absent, not applicable, or not testable, with reason.
- Mobile executions comply with protocol/mobile-runner-policy-v1.md.
- Raw observations in `raw-data/E07-cross-layer-continuity/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
