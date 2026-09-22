# E06 — Cross-platform Parity

## Objective

Determine whether logically equivalent scenarios exist across the Web, Android, and iOS surfaces of each evaluated ecosystem (each a system under test, SUT), and whether those scenarios produce equivalent observable outcomes when executed. Parity is assessed per scenario per platform; the presence of three applications does not imply parity, and each claimed equivalence must be demonstrated by execution or explicitly recorded as absent or untested. Equivalence across platforms within an ecosystem, and across ecosystems, is semantic equivalence under protocol/equivalent-scenario-mapping-v1.md; every scenario used for inferential comparison has a FROZEN mapping record before this campaign executes, and an ecosystem without a defensible semantic equivalent is NOT_COMPARABLE for that scenario (not a score, not a zero). Mobile executions use the runner selected under protocol/mobile-runner-policy-v1.md, and only for ecosystems that passed the per-SUT compatibility smoke (section 9); the smoke is a tooling prerequisite and produces no evidence about any ecosystem.

## Related research question(s)

- RQ4 Cross-platform and Cross-layer Integration (primary).
- Informs dimension 4 Cross-platform and Cross-layer Integration; relates to the cross-cutting property Cross-platform Scenario Parity in protocol/cross-cutting-properties-v1.md.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Scenario (canonical_scenario_id with a FROZEN mapping record, protocol/equivalent-scenario-mapping-v1.md) — candidate.
- Platform (Web / Android / iOS) — candidate.

## Future dependent variables (candidate — not frozen)

- Parity presence per scenario × platform (categorical: present / absent / not applicable / not testable) — candidate.
- Equivalence of observable outcome across platforms for scenarios present on more than one platform (categorical) — candidate.
- Recorded deviations between platforms, classified (taxonomy TBD before freeze) — candidate.

## Required evidence

- Scenario definitions recorded before execution, stating the intended logically equivalent behavior and the observable outcome that constitutes equivalence.
- One run manifest per scenario × platform execution conforming to schemas/run-manifest.schema.json, including ecosystem id, scenario id (canonical_scenario_id), platform, `environment_type`, and outcome.
- Screenshots and logs per execution supporting the parity and equivalence judgments.
- Explicit record for every scenario × platform cell that is absent, not applicable, or not testable, with reason.
- Mobile executions comply with protocol/mobile-runner-policy-v1.md, including the qualification gate status of the mobile runner in use and the compatibility-smoke record of each ecosystem × platform executed (qualification/compatibility-smoke/).
- Raw observations in `raw-data/E06-cross-platform-parity/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
