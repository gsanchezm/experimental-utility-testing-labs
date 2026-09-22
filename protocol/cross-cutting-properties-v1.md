# Cross-cutting Properties

| Field | Value |
|---|---|
| Document | protocol/cross-cutting-properties-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## Purpose

This document defines eight cross-cutting properties of a testing laboratory ecosystem, the system under test (SUT) of this study. The properties are described per ecosystem during the capability audit (experiments/E01-capability-audit) and inform the six dimensions of the Experimental Utility profile defined in protocol/study-design-v1.md. They are neither dimensions nor testing modalities; they cut across both. Observability and Automation Affordances are the descriptive basis of Dimension 5 and of the observability and automation-affordance components of RQ2 (protocol/study-design-v1.md, section 5).

At protocol v1 the properties are descriptive only. No property carries a score, weight, threshold, or metric value. Any later quantification of a property requires a new protocol version under protocol/change-control-v1.md; it cannot be introduced by an audit, a campaign, or an analysis step.

The definitions below apply identically to every evaluated ecosystem (SUT-01 through SUT-06). No ecosystem receives a privileged interpretation of any property.

## State Controllability

The ability to directly establish a target state in the SUT, rather than reaching it only by replaying the end-user path. Mechanisms that may provide this ability include:

- API
- fixtures
- predefined users
- deep links
- direct routes
- setup endpoints
- deterministic configuration

The audit describes which mechanisms exist, which states they can establish, and which target states can only be reached through the user interface or not at all.

## Resetability

The ability to restore the SUT to a known initial state after it has been modified. The audit describes the reset mechanisms that exist, the scope of state each mechanism covers (for example application data, session, device state, external services), and any state that no mechanism resets.

Later metrics may include:

- reset success rate
- number of reset actions
- reset duration
- manual intervention requirement

These are candidate metrics — not frozen. They are listed for orientation only; their definitions and any use in analysis require a protocol version and are exercised through experiments/E03-resetability and protocol/setup-effort-v1.md.

## Determinism

The same controlled initial state and the same stimulus should produce the same expected observable outcome. The audit documents the following separately, with the mechanism responsible for each:

- deterministic behavior — outcome fully determined by initial state and stimulus
- stochastic behavior — outcome depends on randomness inside the SUT (for example random data generation, random failures, shuffled content)
- time-dependent behavior — outcome depends on clock, date, timers, or elapsed time
- external dependency behavior — outcome depends on services, networks, or data outside the SUT's control

Statistically reproducible randomness (for example an outcome distribution that is stable across many runs, or randomness controlled by an undocumented seed) is not treated as deterministic. Behavior is classified as deterministic only when the expected observable outcome is the same on every run under the controlled conditions.

## Observability

The extent to which the state and behavior of the SUT can be inspected from outside without modifying it. Examples of observability affordances:

- APIs
- OpenAPI / Swagger descriptions
- logs
- health endpoints
- IDs (stable identifiers for entities, sessions, requests)
- responses (structured, inspectable response bodies and status codes)
- state inspection
- diagnostic endpoints

The audit describes which affordances exist, which layers (Web, API, Android, iOS) they cover, and whether they are documented.

## Automation Affordances

The extent to which the SUT is built to be driven by automated tooling. Examples:

- data-testid attributes
- stable semantic selectors
- accessibility identifiers
- deep links
- test users
- setup/reset APIs
- machine-readable schemas
- explicit automation hooks

The audit describes which affordances exist per layer, whether they are consistent across screens and platforms, and whether they are documented or only discoverable from source.

## Cross-platform Scenario Parity

Whether logically equivalent scenarios exist across:

- Web
- Android
- iOS

Having three applications does not automatically imply parity. Parity exists for a given scenario only when the same business intent, the same preconditions, and the same expected observable outcome can be expressed on each platform; this is the same semantic-equivalence criterion defined for cross-ecosystem scenarios in protocol/equivalent-scenario-mapping-v1.md, applied to the surfaces of one ecosystem. Identical UI, selectors, or step counts are not required. The audit describes scenario parity per scenario, not per application, and records partial parity (for example a scenario available on two of three platforms) as partial.

## Cross-layer State Continuity

Whether a state or entity established through one layer of the SUT can be verified through another layer. Examples:

- API -> Web
- API -> Android
- API -> iOS
- Web -> API

The audit describes which layer pairs share state, through which mechanism (for example a shared backend, a shared database, a synchronized account), and which layer pairs are isolated from each other.

## Functional Complexity

The business rules available in the SUT, described objectively: which entities exist, which operations act on them, which rules constrain those operations (validation, authorization, workflow states, calculations), and how these rules can be exercised.

More features do not automatically imply greater experimental utility. The audit describes functional complexity as an inventory and does not rank ecosystems by it.

## Recording

- Each audit describes the eight properties in audits/<SUT-directory>/audit.md under a fixed heading per property, using the property names exactly as written in this document. The audit directories are audits/SUT-01-omnipizza, audits/SUT-02-saucelabs, audits/SUT-03-browserstack, audits/SUT-04-restful-booker, audits/SUT-05-juice-shop, and audits/SUT-06-webdriverio.
- Every property description must cite evidence records that follow protocol/evidence-rules-v1.md, by evidence_id. A statement without a cited evidence record is not admissible.
- Absence is recorded as absence. If no mechanism for a property is found, the audit states this explicitly with the evidence status of the search; it does not leave the heading empty.
- No property is scored at v1.

Mapping from property to the campaign(s) that exercise it:

| Property | Related campaign(s) |
|---|---|
| State Controllability | E02-state-establishment |
| Resetability | E03-resetability |
| Determinism | E05-determinism (and E04-repeatability) |
| Observability | E01-capability-audit (primary; descriptive component of RQ2 and Dimension 5); informed cross-cuttingly by all campaigns (protocol/study-design-v1.md, sections 4 and 5) |
| Automation Affordances | E01-capability-audit (primary; descriptive component of RQ2 and Dimension 5); informed cross-cuttingly by all campaigns (protocol/study-design-v1.md, sections 4 and 5) |
| Cross-platform Scenario Parity | E06-cross-platform-parity |
| Cross-layer State Continuity | E07-cross-layer-continuity |
| Functional Complexity | E01-capability-audit — descriptive only |

Campaign directories live under experiments/. All campaigns are NOT STARTED.

## Versioning

This is v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6). Adding, removing, or renaming a property, or attaching any score, weight, or metric to a property, now creates a new version file (for example protocol/cross-cutting-properties-v2.md) under protocol/change-control-v1.md. This frozen version of the document is never overwritten in place.
