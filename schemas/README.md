# Schemas

| Field | Value |
|---|---|
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Protocol version | v1 |
| Repository phase | SETUP (literal manifests/study-manifest.yaml value; E01 is FROZEN and E03-resetability is in PRE-START preparation, NOT_STARTED) — no run-manifest instance data exists yet |
| Created | 2026-09-15 |

This directory holds the JSON Schemas (draft 2020-12) that describe the machine-readable records the study will produce. They exist so that evidence records, run manifests, and audit summaries can be validated automatically once data collection starts. No run manifest has been written for any system under test (SUT); the E01 evidence records, adjudication outputs, and the adjudicated matrix exist and were validated against their schemas (protocol/CHANGELOG.md, PROTO-U05/U06 rows).

## Schemas

| Schema | Validates | Purpose |
|---|---|---|
| `schemas/evidence.schema.json` | One row of `audits/<SUT>/evidence.csv` (after CSV-to-JSON conversion) | The thirteen evidence fields of protocol/evidence-rules-v1.md, in order, beginning with the stable `evidence_id` (SUT0n-EV-nnnn) and including the descriptive `structural_scope_note`, with the frozen vocabularies for ecosystem ids, modalities, evidence statuses, and the 0–3 rubric scale of protocol/capability-rubric-v1.md. |
| `schemas/run-manifest.schema.json` | One run record under `raw-data/`; also one E01 execution verification record under `audits/<SUT>/verifications/` | **v1** (`urn:eus-2026-001:schemas:run-manifest:v1`), preserved unchanged. Provenance (ecosystem components, toolchain versions, `environment_type`, environment descriptors), condition, attempt, seed, and outcome of a single execution in any campaign E01–E12 under `experiments/`. E01 verification records reuse this schema with the conventions of protocol/evidence-rules-v1.md (run_id = verification_id SUT0n-VR-nnnn; modality and related_evidence_ids mandatory). Remains valid for any instance written under v1. |
| `schemas/run-manifest.schema.v2.json` | Same instances as v1; the version future E02 and E03 run manifests conform to | **v2** (`urn:eus-2026-001:schemas:run-manifest:v2`, 2026-09-22; `manifests/run-manifest-schema-v2-provenance.yaml`; protocol/CHANGELOG.md). Adds exactly one property to v1: `actions[].outcome` (string; `SUCCESS`, `PARTIAL_SUCCESS`, `FAILURE`), the per-action outcome recorded separately from the Required Actions count (protocol/setup-effort-v2.md, section 5, rule 9 — human ruling B1). Optional at schema level for backward compatibility; mandatory on every emitted action record by E02/E03 campaign convention. Nothing else changes: same required list, same enumerations, same `additionalProperties: false`; every v1-valid instance is v2-valid, and an instance carrying `actions[].outcome` is valid under v2 only (v1's closed action-item object rejects it). No instance data existed to migrate. |
| `schemas/sut-audit.schema.json` | The structured summary of `audits/<SUT>/audit.md`, and a future `audits/<SUT>/audit.json` | Per-modality provisional levels with evidence references by evidence_id, `structural_scope_note`, verification references, environment types used, descriptive cross-cutting properties (protocol/cross-cutting-properties-v1.md), limitations, unresolved questions, and adjudication. |

None of the schemas defines an aggregated or weighted score; Experimental Utility is a multidimensional profile (protocol/study-design-v1.md).

## Conventions

- `$id` is a URN of the form `urn:eus-2026-001:schemas:<name>:v<n>`; the trailing `v<n>` is the schema version.
- Every root object sets `additionalProperties: false`; `required` lists only fields that apply to every instance.
- Unknown provenance is `null`, never a placeholder string. When converting `evidence.csv` rows to JSON, an empty cell becomes `null` and `provisional_score` becomes an integer.
- Enumerations reproduce frozen vocabularies exactly (ecosystem ids, modality names, evidence statuses, agent roles, campaign id pattern, environment types, structural-scope tokens). The schemas add no values of their own.
- Identifiers: evidence records are referenced only by `evidence_id` (pattern `^SUT0[1-6]-EV-[0-9]{4}$`); E01 execution verification records by `verification_id` (pattern `^SUT0[1-6]-VR-[0-9]{4}$`). Row and line numbers are never used as references.

## Checking the schema files

No validation tooling is installed, and none is mandated at this phase. The schema files themselves can be checked for JSON syntax with tools already present on most systems:

```
python3 -m json.tool schemas/evidence.schema.json
python3 -m json.tool schemas/run-manifest.schema.json
python3 -m json.tool schemas/sut-audit.schema.json
```

or

```
node -e 'JSON.parse(require("fs").readFileSync("schemas/evidence.schema.json", "utf8"))'
```

A syntax check confirms only that the file is well-formed JSON. Validating instance data against a schema requires a draft 2020-12 validator. Frozen by explicit human decision, 2026-09-16: the normative schema standard is JSON Schema Draft 2020-12 (unchanged), and the default validator implementation is Ajv v8. Schema semantics are defined by Draft 2020-12, not by implementation-specific Ajv behavior; if Ajv exposes an incompatibility with a valid Draft 2020-12 construct, that incompatibility is recorded rather than modifying scientific data to satisfy the validator. The exact Ajv version is pinned in manifests/toolchain-manifest.yaml before the first campaign or validation operation that depends on schema validation; it is not installed at this phase.

## Changing a schema

Schemas are protocol artifacts and follow protocol/change-control-v1.md:

- A schema in use by a frozen campaign is never overwritten. A change creates a new file with an incremented version (for example `evidence.schema.json` with `$id` `...:evidence:v2`, stored as `schemas/evidence.schema.v2.json`), and the campaign's experiment plan records which version its data conforms to.
- Data produced under an earlier schema version stays valid against that version; a new version must not retroactively invalidate it.
- Vocabulary changes (modalities, evidence statuses, rubric levels, agent roles, environment types, structural-scope tokens) originate in the corresponding protocol document and are mirrored into the schema in the same change, never introduced in the schema alone.
- The pre-freeze hardening iteration of 2026-09-15 edited all three DRAFT schemas in place (evidence_id, structural_scope_note, environment_type, modality, related_evidence_ids, environment_types_used, controlled_instance_available; deployment_mode removed) before any instance data exists; no schema version increment was needed.
- The final pre-freeze checklist closure of 2026-09-16 (explicit human decision) edited two DRAFT schemas in place before any instance data exists; no schema version increment was needed: `sut-audit.schema.json` gained `confirmed_score` on each modality assessment (protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores"); `run-manifest.schema.json` replaced the single, candidate `mechanism_class` string with two frozen, multi-value array fields, `establishment_mechanisms` and `reset_mechanisms` (protocol/setup-effort-v1.md, section 10), and resolved the `target_state_id` and provisioning-note candidate conventions in prose.
- Versioned successors created under the freeze-locked-schemas procedure (PROTO-U01 precedent), each additive, each leaving the prior file byte-for-byte unmodified: `schemas/adjudication.schema.json` (2026-09-17, PROTO-U01); `schemas/adjudicated-matrix.schema.json` (2026-09-18, PROTO-U05) and its successor `schemas/adjudicated-matrix.schema.v2.json` (2026-09-18, PROTO-U06); `schemas/run-manifest.schema.v2.json` (2026-09-22, explicit human authorization; `manifests/run-manifest-schema-v2-provenance.yaml`). A campaign's configuration names the schema version its run manifests conform to; E03-resetability's PRE-START configuration names v2 (experiments/E03-resetability/README.md).
