# Equivalent Scenario Mapping

| Field | Value |
|---|---|
| Document | protocol/equivalent-scenario-mapping-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 (pre-freeze hardening iteration) |
| Last pre-freeze hardening iteration | final pre-freeze checklist closure (controlled vocabulary freeze, explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## 1. Purpose

RQ2, RQ3, and RQ4 compare ecosystems on "equivalent" target states, conditions, and scenarios. This document gives the operational definition of equivalence across ecosystems, the record that fixes a scenario's canonical experimental intent, the per-ecosystem mapping that realizes it, the NOT_COMPARABLE marker, and the lifecycle under which mapping records are frozen. It applies to every evaluated testing laboratory ecosystem (each a system under test, SUT, SUT-01 to SUT-06) identically and to every campaign that compares ecosystems on a scenario or condition (E02–E07 directly; E08–E12 wherever a between-ecosystem comparison on a scenario is made).

No mapping record exists. No scenario has been defined. This document defines the method only.

## 2. Definition: semantic equivalence

Two realizations of a scenario in two ecosystems are **equivalent** when they express the same **canonical experimental intent** (Section 3). Equivalence is semantic, not implementation equivalence.

Equivalent scenarios do NOT require:

- identical UI;
- identical selectors;
- identical products or business objects;
- identical endpoint names;
- identical number of workflow steps;
- identical domain vocabulary.

Equivalent scenarios DO require the same: precondition class, actor state, business intent, target state or transition, observable oracle class, and reset requirement, on a surface that both realizations have and within the allowed domain mapping. One ecosystem may realize the intent with a book, another with a concert ticket, another with a parking permit; the business object does not need to be identical, the semantic testing intent must be.

Conceptual example (illustrative domain objects; no statement about any evaluated ecosystem): *An authenticated user places one purchasable item into a cart and reaches a checkout-ready state.* The intent is the same whether the item is a book, a concert ticket, or a parking permit, whether the cart is called a cart, a basket, or an order, whether it takes three screens or one, and whether the oracle is a cart total in the UI, a cart entity returned by an API, or both.

## 3. Canonical experimental intent

Every cross-ecosystem scenario has exactly one canonical experimental intent record, written in ecosystem-neutral terms **before** any per-ecosystem mapping is written and before any campaign that uses it starts. It contains at least the following fields.

| Field | Definition | Vocabulary (frozen by explicit human decision, 2026-09-16) |
|---|---|---|
| canonical_scenario_id | Stable identifier of the scenario, unique across the study and independent of campaign. Format `CS-nnn`. | — |
| precondition_class | The class of state the ecosystem must be in before the actor acts. | `CLEAN_SESSION`; `AUTHENTICATED_SESSION`; `SEEDED_BUSINESS_STATE`; `EXISTING_RESOURCE`; `CONFIGURED_CONTEXT`; `OTHER` (requires a free-text explanation) |
| actor_state | The identity and session state of the actor. | `ANONYMOUS`; `AUTHENTICATED_STANDARD`; `AUTHENTICATED_SPECIAL`; `NOT_APPLICABLE`; `OTHER` (requires a free-text explanation). Equivalence between two "special" actors is never inferred unless their experimental role is semantically equivalent. |
| business_intent | One sentence, in domain-neutral terms, stating what the actor sets out to accomplish. | free text |
| target_state_or_transition | The state that must hold, or the transition that must have occurred, when the scenario is complete, stated in domain-neutral terms. | free text |
| observable_oracle_class | The class of observation by which attainment of the target state is verified. | `UI_STATE`; `API_RESPONSE`; `BUSINESS_STATE`; `VISUAL_STATE`; `ACCESSIBILITY_FINDING`; `PERFORMANCE_MEASURE`; `SECURITY_CONDITION`; `LOCALIZATION_STATE`; `OTHER` (requires a free-text explanation; covers an oracle class not yet named here, for example a cross-layer consistency check used by E07-cross-layer-continuity) |
| reset_requirement | What must be restored after the scenario so that it can be re-executed. | `NONE`; `SESSION_RESET`; `DATA_RESET`; `APP_RESET`; `ENVIRONMENT_RESET`; `OTHER` (requires a free-text explanation). Distinct from, and not to be conflated with, the per-run `reset_mechanisms` vocabulary of protocol/setup-effort-v1.md, section 10, which records how a realization actually met this requirement. |
| applicable_surfaces | The surfaces on which the intent can, in principle, be realized. A scenario may list more than one applicable surface. An ecosystem lacking every listed surface is NOT_COMPARABLE for this scenario. | `WEB`; `API`; `ANDROID`; `IOS` — this scenario-applicability vocabulary is distinct from the lowercase `web`/`api`/`android`/`ios` component-surface keys used in manifests/sut-manifest.yaml and schemas/, which record an ecosystem's actual surfaces, not a scenario's applicable ones |
| allowed_domain_mapping | What may vary between realizations without breaking equivalence, and what may not; kept flexible rather than an enum. Must explicitly document permissible semantic substitutions (for example pizza ↔ backpack; product ↔ room; cart ↔ basket), allowed only when they preserve the canonical experimental intent. At minimum: business object type may vary; vocabulary may vary; identifiers, selectors, and endpoint names may vary; number of steps may vary; the actor class, the intent, the target transition, the oracle class, and the reset requirement may not vary. Scenario-specific constraints are added here (for example "the item must be purchasable and priced"). | free text |

Additional fields permitted: description, campaigns_using (E02 … E12), notes. Record-level lifecycle fields (they belong to the whole record, not to a per-ecosystem entry): version (integer, starts at 1), mapping_status (DRAFT or FROZEN), and frozen_at and approved_by (Section 6), the last two null while the record is DRAFT.

The controlled vocabulary values above fix what may be *written* in each field; they do not themselves establish comparability. The COMPARABLE / NOT_COMPARABLE decision rule (Section 5) remains authoritative and is unaffected by this vocabulary freeze.

The canonical record is written by the ORCHESTRATOR under experiments/ (Section 6). It cites no ecosystem and is not adjusted after per-ecosystem mappings exist except by a new record version with a change-log row.

## 4. Per-ecosystem mapping

For each canonical scenario, one mapping entry exists per evaluated ecosystem, SUT-01 to SUT-06, without exception. An entry states either how the ecosystem realizes the intent or why it cannot.

| Field | Definition |
|---|---|
| sut_id | SUT-01 … SUT-06 |
| comparability | COMPARABLE or NOT_COMPARABLE |
| surfaces_used | The subset of applicable_surfaces on which this ecosystem realizes the intent (empty when NOT_COMPARABLE) |
| domain_object | The business object used (for example the item type), in the ecosystem's own vocabulary |
| precondition_realization | How the precondition class is established in this ecosystem (mechanism, with the evidence_id(s) from E01 that document it) |
| actor_realization | How the actor state is established (for example a documented test account; evidence_id(s)) |
| entry_and_steps | The ordered steps, stated so that they can be executed and counted under protocol/setup-effort-v1.md; step count may differ from other ecosystems |
| oracle_realization | The concrete observation that instantiates the observable_oracle_class (for example the UI element, the endpoint and field, the entity query) |
| reset_realization | How the reset_requirement is met (mechanism; evidence_id(s)); or a statement that it cannot be met, which makes the scenario NOT_COMPARABLE for campaigns whose design requires the reset |
| environment_type | The environment in which the mapping is executed (protocol/study-design-v1.md, section 10); if a required controlled instance cannot be established, the affected campaigns record NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE, which is distinct from NOT_COMPARABLE |
| not_comparable_reason | Required when NOT_COMPARABLE: one of NO_APPLICABLE_SURFACE; NO_EQUIVALENT_INTENT (the ecosystem's domain has no defensible semantic equivalent of the business intent); ORACLE_CLASS_UNOBSERVABLE; RESET_REQUIREMENT_UNSATISFIABLE; OTHER (described), plus free text |
| evidence_ids | Every E01 evidence_id cited above |
| justification | Why this realization expresses the same intent, or why no defensible equivalent exists |

## 5. Comparability decision rule

An ecosystem is COMPARABLE on a canonical scenario only when all of the following hold, each supported by E01 evidence cited by evidence_id:

1. at least one applicable surface exists in the evaluated version;
2. the precondition class and the actor state can be established through mechanisms the evaluated version exposes;
3. a business object exists that satisfies the business intent within the allowed domain mapping;
4. the target state or transition can be reached;
5. an observation of the required oracle class is available;
6. the reset requirement can be met, or the campaign's design does not require it.

If any condition fails, or if the mapping would require modifying the ecosystem (AGENT-INSTRUCTIONS.md, rule 3), stretching the intent, or substituting a different intent, the ecosystem is marked NOT_COMPARABLE with the reason. No artificial comparison is forced.

NOT_COMPARABLE:

- is not a capability score and is never converted into one; the ecosystem's rubric levels are unaffected;
- is not a zero, a failure, or a missing value in any count or rate; the ecosystem is excluded from inferential comparison on that scenario only and is reported side by side with the reason (protocol/statistical-analysis-plan-v1.md, section 5);
- does not remove the ecosystem from the campaign; other scenarios may still be COMPARABLE;
- is recorded with the same discipline for every ecosystem, including SUT-01. A candidate ecosystem that lacks a defensible equivalent is marked NOT_COMPARABLE exactly as a baseline would be.

The decision is made from the canonical record and the E01 evidence, never from a campaign result. A mapping is never revised because an ecosystem performed well or poorly on it.

## 6. Lifecycle and freeze

- Author: the ORCHESTRATOR writes canonical records and mapping entries under experiments/scenario-mappings/<canonical_scenario_id>.yaml. This directory path is fixed, not candidate; no separate freeze of the bare path is needed because, per the Freeze rule immediately below, each record stored there is itself locked at the start of the first campaign that uses it (protocol/change-control-v1.md, section 7), which is the applicable freeze point for its content. Auditors do not write mapping records; their E01 evidence is the input. Auditors do not compare ecosystems (protocol/agent-governance-v1.md).
- Order: the canonical record is written first, then the six mapping entries. The canonical intent is never derived from one ecosystem's implementation and then generalized; an intent that can be expressed only in one ecosystem's vocabulary is not canonical.
- Freeze: before E02–E07 execution, every cross-ecosystem scenario used for inferential comparison must have a mapping record in state FROZEN, approved by an explicit human decision and recorded by one change-log row per frozen mapping record in the mapping-record row form of protocol/change-control-v1.md, section 5, no later than the campaign-start row of the first campaign that uses it (protocol/change-control-v1.md, section 7). Later campaigns reuse the frozen record. A campaign may not execute a scenario whose mapping record is DRAFT.
- Change: a frozen mapping record is never edited. A change creates a new record version: a new file `experiments/scenario-mappings/<canonical_scenario_id>-v<N>.yaml` for N >= 2 (version 1 has no suffix) with `version` set to N, and a mapping-record change-log row (`mapping v<N> -> v<M>`, protocol/change-control-v1.md, section 5) stating the reason and the affected campaigns; results already collected under the earlier version are analyzed under that version.
- Ecosystem versions: a mapping record cites the evaluated version pinned in manifests/sut-manifest.yaml. If the pinned version changes (which itself requires change control), the mapping entry is re-validated and re-frozen.

## 7. Mapping record template

The record below is a template. No field is populated with study content; the placeholders `<...>` are to be replaced when a record is created, and the six mapping entries must all be present.

```yaml
# experiments/scenario-mappings/<canonical_scenario_id>.yaml
# Location fixed (Section 6); the directory path is no longer candidate. Every mappings[] entry has the identical form.
# comparability is COMPARABLE or NOT_COMPARABLE and is required in every entry at freeze;
# not_comparable_reason is required when NOT_COMPARABLE. null means not yet decided (DRAFT only).
version: 1
canonical_scenario_id: <CS-nnn>
description: <one paragraph, domain-neutral>
precondition_class: <CLEAN_SESSION | AUTHENTICATED_SESSION | SEEDED_BUSINESS_STATE | EXISTING_RESOURCE | CONFIGURED_CONTEXT | OTHER>
actor_state: <ANONYMOUS | AUTHENTICATED_STANDARD | AUTHENTICATED_SPECIAL | NOT_APPLICABLE | OTHER>
business_intent: <one sentence, domain-neutral>
target_state_or_transition: <domain-neutral statement>
observable_oracle_class: <UI_STATE | API_RESPONSE | BUSINESS_STATE | VISUAL_STATE | ACCESSIBILITY_FINDING | PERFORMANCE_MEASURE | SECURITY_CONDITION | LOCALIZATION_STATE | OTHER>
reset_requirement: <NONE | SESSION_RESET | DATA_RESET | APP_RESET | ENVIRONMENT_RESET | OTHER>
applicable_surfaces: [<WEB | API | ANDROID | IOS>, ...]
allowed_domain_mapping: |
  <what may vary; what may not vary; permissible semantic substitutions (e.g. pizza <-> backpack); scenario-specific constraints>
campaigns_using: [<E02-state-establishment>, ...]
mapping_status: DRAFT
frozen_at: null
approved_by: null
mappings:
  - sut_id: SUT-01
    comparability: null
    surfaces_used: []
    domain_object: null
    precondition_realization: null
    actor_realization: null
    entry_and_steps: []
    oracle_realization: null
    reset_realization: null
    environment_type: null
    not_comparable_reason: null
    evidence_ids: []
    justification: null
  - sut_id: SUT-02
    comparability: null
    surfaces_used: []
    domain_object: null
    precondition_realization: null
    actor_realization: null
    entry_and_steps: []
    oracle_realization: null
    reset_realization: null
    environment_type: null
    not_comparable_reason: null
    evidence_ids: []
    justification: null
  - sut_id: SUT-03
    comparability: null
    surfaces_used: []
    domain_object: null
    precondition_realization: null
    actor_realization: null
    entry_and_steps: []
    oracle_realization: null
    reset_realization: null
    environment_type: null
    not_comparable_reason: null
    evidence_ids: []
    justification: null
  - sut_id: SUT-04
    comparability: null
    surfaces_used: []
    domain_object: null
    precondition_realization: null
    actor_realization: null
    entry_and_steps: []
    oracle_realization: null
    reset_realization: null
    environment_type: null
    not_comparable_reason: null
    evidence_ids: []
    justification: null
  - sut_id: SUT-05
    comparability: null
    surfaces_used: []
    domain_object: null
    precondition_realization: null
    actor_realization: null
    entry_and_steps: []
    oracle_realization: null
    reset_realization: null
    environment_type: null
    not_comparable_reason: null
    evidence_ids: []
    justification: null
  - sut_id: SUT-06
    comparability: null
    surfaces_used: []
    domain_object: null
    precondition_realization: null
    actor_realization: null
    entry_and_steps: []
    oracle_realization: null
    reset_realization: null
    environment_type: null
    not_comparable_reason: null
    evidence_ids: []
    justification: null
notes: null
```

## 8. Relation to other documents

- protocol/statistical-analysis-plan-v1.md, section 4: between-ecosystem comparisons are made only on canonical scenarios for which both ecosystems are COMPARABLE; pairing is by canonical_scenario_id; NOT_COMPARABLE scenarios are reported side by side, not compared.
- protocol/setup-effort-v1.md, counting rule 7: Required Actions counts are comparable only on COMPARABLE mappings; step counts legitimately differ between realizations and that difference is the measurement, not a mapping defect.
- protocol/cross-cutting-properties-v1.md, Cross-platform Scenario Parity: parity within one ecosystem across its own surfaces uses the same semantic-equivalence criterion (same business intent, same preconditions, same expected observable outcome), applied to surfaces of one ecosystem rather than to different ecosystems.
- protocol/repeatability-determinism-v1.md: an E04/E05 condition is defined per ecosystem; when such conditions are compared between ecosystems, the comparison is made on a canonical scenario under this document.
- experiments/E02 … E07: each campaign README lists the canonical scenarios it uses and requires their mapping records to be FROZEN before execution.
- protocol/study-design-v1.md, section 11, rule 9: NOT_COMPARABLE is not a capability score.

## 9. Status

- No canonical scenario has been defined. No mapping record exists. experiments/scenario-mappings/ does not exist yet.
- No comparability decision has been made for any ecosystem.

## 10. Versioning

This is protocol version v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6), created during the pre-freeze hardening iteration of 2026-09-15. The Section 3 controlled vocabularies (precondition_class, actor_state, observable_oracle_class, reset_requirement, applicable_surfaces) were frozen with this document, and the experiments/scenario-mappings/ directory path was resolved as fixed rather than candidate, during the final pre-freeze checklist closure of 2026-09-16 (explicit human decision), while the document was still DRAFT (protocol/change-control-v1.md, section 2, DRAFT -> DRAFT); the comparability decision rule (Section 5) is unchanged. It follows the lifecycle in protocol/change-control-v1.md. This document is never overwritten in place; any modification creates protocol/equivalent-scenario-mapping-v2.md. Individual canonical-scenario and mapping records under experiments/scenario-mappings/ remain unwritten and are frozen separately, per record, at their own campaign-start freeze (Section 6); the method this document defines is frozen now, but no record yet exists.
