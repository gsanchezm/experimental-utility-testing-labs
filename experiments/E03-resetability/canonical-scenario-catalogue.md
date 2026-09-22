# E03-resetability — PRE-DATA Canonical-Scenario Catalogue

| Field | Value |
|---|---|
| Prepared by | ORCHESTRATOR |
| Date | 2026-09-21; corrected 2026-09-22 (human ruling `E03-CS002-EXCLUSION-RULING-01`, `manifests/e03-cs002-exclusion-v1.yaml`; `protocol/unresolved.md`, PROTO-U09) |
| Status | **Active catalogue: 1 scenario (CS-001).** CS-002 is EXCLUDED_FROM_CAMPAIGN (historical record preserved; see "Correction record" below). |

## Methodological rule (binding for this catalogue)

A canonical scenario's intent is defined **before, and independently of, any SUT-specific implementation evidence**. SUT-specific (E01) evidence may establish only whether a system under test (SUT) maps to an already independently defined canonical intent — the COMPARABLE / NOT_COMPARABLE decision of `protocol/equivalent-scenario-mapping-v1.md`, section 5 — never the intent itself. This restates the frozen protocol, section 6: *"the canonical record is written first, then the six mapping entries. The canonical intent is never derived from one ecosystem's implementation and then generalized; an intent that can be expressed only in one ecosystem's vocabulary is not canonical."* It was fixed for E03 by explicit human ruling on 2026-09-22 (`E03-CS002-EXCLUSION-RULING-01`) after the 2026-09-21 version of this catalogue was found to have derived one scenario in the forbidden order (below). No protocol document changes.

Consequences applied here:

- No scenario is created, kept, or removed because of an E01 capability score, and no scenario is invented so that a particular SUT receives a measured condition.
- Surface and domain-object details drawn from E01 evidence populate each mapping entry as comparability support only.
- A SUT with no defensible semantic equivalent of a canonical intent is NOT_COMPARABLE for that scenario and remains in the campaign population (`protocol/study-design-v1.md`, section 11, rule 9).

## Active catalogue (current E03 campaign version)

| canonical_scenario_id | Intent | Origin of the intent | Comparable SUTs | Path | Status |
|---|---|---|---|---|---|
| CS-001 | Business-object establish-then-reset: an authenticated actor establishes one unit of session- or resource-scoped business state (cart, basket, or booking), then a reset restores the declared clean starting state | `protocol/equivalent-scenario-mapping-v1.md`, section 2, pre-existing illustrative pattern ("An authenticated user places one purchasable item into a cart…"), independent of any SUT's implementation | SUT-01, SUT-02, SUT-03, SUT-04, SUT-05 (SUT-06 NOT_COMPARABLE, NO_EQUIVALENT_INTENT) | `experiments/scenario-mappings/CS-001.yaml` | FROZEN 2026-09-21 (`E03-CS001-FREEZE-AUTH-01`); sole accepted canonical scenario for the current E03 campaign version |

Every SUT in the E03 population (SUT-01 through SUT-06) has an explicit mapping entry in CS-001, COMPARABLE or NOT_COMPARABLE with a frozen-vocabulary reason. SUT-06 is NOT_COMPARABLE on CS-001 and **remains a member of the E03 six-SUT population**; in the current configuration it has no measured E03 condition, and none is invented to give it one.

Candidate conditions derived from this catalogue (one per COMPARABLE SUT × `surfaces_used` entry in CS-001; recomputed from the frozen record on 2026-09-22): **9** — `E03-CS001-SUT01-WEB`, `-SUT01-API`, `-SUT02-WEB`, `-SUT02-ANDROID`, `-SUT02-IOS`, `-SUT03-WEB`, `-SUT04-WEB`, `-SUT04-API`, `-SUT05-API` (`experiments/E03-resetability/campaign-configuration-draft.md`, section 5).

## Excluded record (historical, preserved)

| canonical_scenario_id | Path | Record state | Campaign status | Reason |
|---|---|---|---|---|
| CS-002 | `experiments/scenario-mappings/CS-002.yaml` | File unchanged, byte-identical to its 2026-09-21 freeze (`mapping_status: FROZEN`, `E03-CS002-FREEZE-AUTH-01`, commit `b67ac64`); SHA-256 `aa5bd4a71c02348b48c4fc7cda086ceb5519d848081080db995d6a6aa5f4a7fe` | **EXCLUDED_FROM_CAMPAIGN** — not admissible for measured E03 execution; not an active input to any E03 configuration, workflow, or executor (`protocol/CHANGELOG.md`, 2026-09-22 row) | Its canonical intent (generic per-tier persistence Save/Clear) was written after, and generalized from, SUT-06's specific E01 evidence (SUT06-EV-0007, SUT06-EV-0015), contrary to `protocol/equivalent-scenario-mapping-v1.md`, section 6. Ruling: `E03-CS002-EXCLUSION-RULING-01`. |

A future executor, workflow, or configuration must not consume CS-002: the authoritative list of active E03 scenarios is this section's "Active catalogue" table, mirrored in `experiments/E03-resetability/campaign-configuration-draft.md` and, at campaign start, in the locked "Campaign configuration" record. The frozen `notes` field of `CS-001.yaml`, which says SUT-06's mechanism "is instead realized in … CS-002.yaml, completing the … catalogue", is a historical snapshot inside a frozen record and is not current status (`manifests/e03-cs002-exclusion-v1.yaml`, `cs001_stale_pointer_note`).

## Correction record (2026-09-22)

The 2026-09-21 version of this document (commit `b67ac64`, retained in git history) stated that the catalogue was "Complete (2 scenarios)", described a method that *began* by reading the six E01 audits' Resetability sections and grouping the evidenced reset mechanisms into scenario classes, and declared a self-authored "stop rule" (one scenario per evidenced state-class × mechanism combination). That method is the order `protocol/equivalent-scenario-mapping-v1.md`, section 6, forbids, and the stop rule had no frozen basis (`protocol/unresolved.md`, PROTO-U09). This version replaces both with the methodological rule above. What survives unchanged: CS-001's intent, which the same audit traced to the protocol's own pre-existing illustrative pattern rather than to any SUT, and every CS-001 mapping entry, which uses E01 evidence only as comparability support. What is withdrawn: CS-002 from campaign use, and the stop rule. Nothing frozen bounds how many canonical scenarios a campaign needs; any further scenario for E03 would have to be independently specified, separately human-authorized, and frozen by its own change-log row before use.

## What this catalogue does not do

- Does not select or exclude any E03 condition by SUT score.
- Does not force SUT-06 into CS-001, or remove SUT-06 from the E03 population.
- Does not delete, rewrite, unfreeze, or re-version CS-002.
- Does not freeze `environment_type` or controlled-instance status for any condition (`experiments/E03-resetability/controlled-instance-determination.md`; `protocol/study-design-v1.md`, section 10.3).
- Does not start E03, execute any run, or authorize mobile qualification.
