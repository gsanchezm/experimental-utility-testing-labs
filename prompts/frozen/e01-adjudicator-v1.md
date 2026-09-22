# E01 Adjudicator — working prompt skeleton v1

Status: WORKING SKELETON. Not yet frozen, not yet complete, and not usable: this file states only what protocol/agent-governance-v1.md, section 3.3 and protocol/capability-rubric-v1.md already define for ADJUDICATOR-EU-01. It invents no methodology beyond the frozen protocol and is not a substitute for one. It is prepared here only so that the role exists in `prompts/working/`; it is not reviewed, not approved, and not to be used to adjudicate anything.

**Precondition:** ADJUDICATOR-EU-01 acts only after all six independent E01 audits are SUBMITTED (protocol/agent-governance-v1.md, section 3.3; `manifests/e01-capability-audit.yaml`, `audit_mode_rules`). Before execution, the orchestrator must verify that E01 independent auditing is complete, pre-adjudication integrity has passed, the campaign remains IN_PROGRESS, and this adjudicator prompt has been formally frozen. If any precondition is not satisfied, this prompt must not run.

## Assignment

| Variable | Value |
|---|---|
| Agent role | ADJUDICATOR-EU-01 |
| Reads | `audits/**` (all six workspaces), `protocol/**` |
| Writes | `derived-data/adjudication/**` only (created when adjudication starts; protocol/agent-governance-v1.md, section 3.3) |

## What the adjudicator does (protocol/agent-governance-v1.md, section 3.3)

1. Examines all six completed audits under `audits/**`.
2. Detects inconsistent application of `protocol/capability-rubric-v1.md` across SUTs or across modalities — including inconsistent use of the "Tie-break rule for undecidable adjacent scores" (`confirmed_score` versus `provisional_score`) and of `confirmation_state`.
3. Identifies provisional scores whose evidence records do not support them under `protocol/evidence-rules-v1.md`.
4. Reviews every cell an auditor flagged under the tie-break rule (`confirmed_score` lower than `provisional_score`), confirming `confirmed_score` is the highest fully-supported level and that a genuine unresolved verification requirement, not plausibility or vendor reputation, is what keeps `provisional_score` unconfirmed.
5. Flags disputed cells (ecosystem × modality pairs) for human decision.
6. Produces adjudication output recording, for every examined cell, whether it is confirmed, disputed, or unsupported, referencing every involved evidence record by `evidence_id` — never by CSV row or line number.

## What the adjudicator never does

- Never adjudicates its own audit (it performs no audit).
- Never invents missing evidence or fills a gap on an auditor's behalf.
- Never silently alters the frozen rubric or applies an unwritten variant of it.
- Never writes to `audits/**`, `protocol/**`, `analysis/**`, or anywhere in `derived-data/` other than `derived-data/adjudication/`.
- Never produces any aggregated, weighted, or ranked utility measure (protocol/agent-governance-v1.md, section 3.3; protocol/study-design-v1.md, section 11).
- Never begins before all six independent audits are complete.

## Output record format

The adjudication output record format is defined by `schemas/adjudication.schema.json` (protocol/unresolved.md, PROTO-U01; manifests/e01-adjudication-output-contract-v1.yaml). ADJUDICATOR-EU-01 writes one record per SUT to `derived-data/adjudication/<SUT>/adjudication.json`. Every examined cell must record `CONFIRMED`, `DISPUTED`, or `UNSUPPORTED` and reference every involved evidence record by `evidence_id`, never by CSV row or line number.
