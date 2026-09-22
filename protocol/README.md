# Protocol Directory

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). Protocol version v1. Created 2026-09-15.

**Protocol state of all listed documents: FROZEN-PRE-DATA** (frozen 2026-09-16, approved by gilbertosanchez; manifests/protocol-freeze-v1.yaml). No data has been collected, no audit has been performed, and no score, result, or ranking exists for any system under test (SUT); freezing the protocol does not by itself start data collection (manifests/README.md, "Data-collection gate").

This file is an index, not a protocol document; it carries no protocol header block and is not itself versioned or frozen.

## Purpose

The protocol directory holds the pre-registered rules of the study: what is compared, how it is measured, what counts as evidence, how repetitions are run, how results are analyzed, which tools may be used, who may change what, and how changes are recorded. Every audit, campaign, and analysis in this repository must cite the protocol version it ran under.

## Documents

| File | Purpose | Version | State |
|---|---|---|---|
| protocol/study-design-v1.md | Unit of comparison, evaluated ecosystems, the six-dimension Experimental Utility profile, RQ1–RQ5, provisional hypotheses H1–H5, frozen modality list, ground-truth rule, campaign mapping, environment provenance and experimental control, interpretation rules, Open-Issue Register | v1 | FROZEN-PRE-DATA |
| protocol/capability-rubric-v1.md | Four-level capability scale (Score 0 — UNSUPPORTED; Score 1 — TECHNICALLY EXECUTABLE; Score 2 — EXPERIMENTALLY USABLE; Score 3 — EXPERIMENTALLY CONTROLLABLE) applied per modality per ecosystem; structural_scope_note annotation | v1 | FROZEN-PRE-DATA |
| protocol/cross-cutting-properties-v1.md | The eight cross-cutting properties assessed across modalities | v1 | FROZEN-PRE-DATA |
| protocol/setup-effort-v1.md | Recording rules for per-run / per-condition preparation and reset effort (Dimension 6, RQ2); one-time provisioning recorded separately | v1 | AMENDED (superseded by v2, 2026-09-21) |
| protocol/setup-effort-v2.md | Same scope as v1; resolves issue (xviii) — verification-as-action, partial-success counting (human ruling `ISSUE-XVIII-RULING-01`) | v2 | FROZEN-PRE-DATA |
| protocol/repeatability-determinism-v1.md | Repetition targets and determinism procedures for RQ3 | v1 | FROZEN-PRE-DATA |
| protocol/statistical-analysis-plan-v1.md | Pre-registered analysis plan; CONFIRMATORY versus EXPLORATORY comparison classification | v1 | FROZEN-PRE-DATA |
| protocol/equivalent-scenario-mapping-v1.md | Semantic equivalence of cross-ecosystem scenarios, canonical experimental intent, NOT_COMPARABLE marker, mapping-record template | v1 | FROZEN-PRE-DATA |
| protocol/mobile-runner-policy-v1.md | Mobile runner candidates, fallback, qualification gate (MQ1, MQ2, MQ3; qualification SUT; pass criteria), per-SUT compatibility smoke | v1 | FROZEN-PRE-DATA |
| protocol/evidence-rules-v1.md | Evidence statuses, evidence record fields with evidence_id, execution verification records | v1 | FROZEN-PRE-DATA |
| protocol/change-control-v1.md | Protocol state lifecycle, versioning rule, protocol freeze versus campaign freeze | v1 | FROZEN-PRE-DATA |
| protocol/agent-governance-v1.md | Agent roles and their write permissions | v1 | AMENDED (2026-09-22; superseded by protocol/agent-governance-v2.md) |
| protocol/agent-governance-v2.md | Adds role EXECUTOR-E03-RESETABILITY (E03-resetability only) with explicit READ and WRITE boundaries and GitHub Actions permissions (revised 2026-09-22); carries the `.github/workflows/**` boundary granted to ORCHESTRATOR by `E03-CI-WRITE-AUTH-01` (in force via AGENT-INSTRUCTIONS.md) for incorporation at freeze | v2 | FROZEN-PRE-DATA (2026-09-22, at its exact pre-freeze content hash; authorization id AGENT-GOVERNANCE-V2-FREEZE-AUTH-01; record manifests/agent-governance-v2-freeze-v1.yaml; body text unchanged at freeze, its section-7 DRAFT narration retained as a historical snapshot). Defines roles and boundaries; authorizes no execution |

## Lifecycle

Authoritative definitions are in protocol/change-control-v1.md. Summary:

DRAFT -> FROZEN-PRE-DATA -> (SUPERSEDED | AMENDED)

- **DRAFT** — editable; not yet approved; no data may be collected under it.
- **FROZEN-PRE-DATA** — approved by explicit human decision before data collection; content is immutable from this point.
- **AMENDED** — terminal state of a frozen version replaced by a successor created after data collection began under it; the file stays on disk unchanged apart from its header, and the change (rationale, affected campaigns) is recorded in the change log.
- **SUPERSEDED** — terminal state of a frozen version replaced by a successor before data collection began under it; retained for the record, no longer governs any campaign.

## Versioning rule

Two stateless, unversioned log files carry no protocol state: protocol/CHANGELOG.md (approved changes, protocol/change-control-v1.md section 5) and protocol/unresolved.md (protocol-level escalations mirrored by the ORCHESTRATOR, protocol/agent-governance-v1.md section 6). protocol/CHANGELOG.md was created by the protocol v1 pre-data freeze of 2026-09-16; protocol/unresolved.md was created on first use (PROTO-U01, 2026-09-17) and currently carries nine rows (PROTO-U01…U09), of which one (PROTO-U02) remains OPEN — deferred, non-blocking; the rest are RESOLVED (PROTO-U09, 2026-09-22: CS-002 canonical scenario excluded from E03 by human ruling). protocol/CHANGELOG.md additionally carries the 2026-09-22 rows for the CS-002 exclusion and for schemas/run-manifest.schema.v2.json.

A frozen version is never overwritten. Any modification to a frozen document creates a new version file with the version suffix incremented (for example, protocol/capability-rubric-v1.md -> protocol/capability-rubric-v2.md). The earlier file remains unchanged and its state is updated to AMENDED or SUPERSEDED per protocol/change-control-v1.md. Each version file carries its own header block stating its version and state.

## Who may edit

Per protocol/agent-governance-v1.md, only the ORCHESTRATOR role may write to this directory, and only with explicit human approval for any freeze or version change. AUDITOR roles (AUDITOR-SUT01-OMNIPIZZA through AUDITOR-SUT06-WEBDRIVERIO) cannot write here; they read the protocol. ADJUDICATOR-EU-01 and QUALIFIER-MOBILE-01 cannot write here either. Each role's permitted write locations are defined in protocol/agent-governance-v1.md.

## Freeze checklist (completed for protocol v1)

To move a document from DRAFT to FROZEN-PRE-DATA:

- [x] Every row of the Open-Issue Register (protocol/study-design-v1.md, section 13) is RESOLVED or DEFERRED-BEFORE-CAMPAIGN; no row is OPEN. (RESOLVED 18, OPEN 0, DEFERRED-BEFORE-CAMPAIGN 2 — (xviii), (xix).)
- [x] Every item marked "TBD before freeze" or "candidate — not frozen" under protocol/ and schemas/ is resolved and recorded, or explicitly deferred to a named campaign configuration with a written reason (protocol/change-control-v1.md, section 6, step 3).
- [x] Explicit human approval is obtained and recorded (approver, date). — gilbertosanchez, 2026-09-16.
- [x] The freeze is recorded in the change log per protocol/change-control-v1.md. — protocol/CHANGELOG.md.
- [x] The document's header block is updated: Protocol state = FROZEN-PRE-DATA; Freeze approval = approver and date. — done for all eleven protocol v1 documents.
- [x] manifests/study-manifest.yaml `protocol_state` is updated accordingly. — FROZEN-PRE-DATA, `protocol_frozen: true`.

This checklist was completed for protocol v1 on 2026-09-16 (protocol v1 pre-data freeze); see manifests/protocol-freeze-v1.yaml for the freeze provenance record. It remains governed by protocol/change-control-v1.md for any future version.

## Current status

Protocol v1 is FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6). The pre-freeze hardening iteration of 2026-09-15 edited the documents in place (DRAFT -> DRAFT) and added protocol/equivalent-scenario-mapping-v1.md. A second pre-freeze hardening iteration on 2026-09-16, by explicit human decision, resolved the three remaining Open-Issue Register rows — (x), (xi), (xx) (protocol/study-design-v1.md, section 13) — editing protocol/study-design-v1.md, protocol/capability-rubric-v1.md, protocol/evidence-rules-v1.md, protocol/repeatability-determinism-v1.md, protocol/statistical-analysis-plan-v1.md, and this file's own sibling protocol/change-control-v1.md in place (DRAFT -> DRAFT). The register stood at RESOLVED 18, OPEN 0, DEFERRED-BEFORE-CAMPAIGN 2. A final pre-freeze checklist closure on 2026-09-16, by explicit human decision, resolved the remaining step-3 freeze-checklist items (the capability-rubric tie-break rule; Setup Effort Duration start/stop boundaries; the one-time provisioning record location, manifests/provisioning/; the equivalent-scenario-mapping controlled vocabulary; the bootstrap and paired effect-size policy; the JSON Schema validator, Ajv v8; the establishment/reset mechanism vocabulary) across protocol/ and schemas/, editing the affected documents in place (DRAFT -> DRAFT); it surfaced no new Open-Issue Register row. Immediately before freezing, the stale "candidate — to be frozen" heading in protocol/repeatability-determinism-v1.md, section 5, was renamed to "Execution Rules — v1" (non-substantive; no rule's substance changed). All eleven documents were then moved DRAFT -> FROZEN-PRE-DATA. Issues (xviii) and (xix) remain DEFERRED-BEFORE-CAMPAIGN and are unaffected by this freeze; they block only E02/E03 and E04/E05 respectively, never E01. Freezing the protocol does not start data collection: `data_collection_started` in manifests/study-manifest.yaml remains false, E01 Capability Audit remains NOT_STARTED, and Mobilewright qualification remains NOT_STARTED.
