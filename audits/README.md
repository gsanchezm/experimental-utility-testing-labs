# Audit Workspaces

| Field | Value |
|---|---|
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Protocol version | v1 |
| Protocol state | DRAFT |
| Repository phase | SETUP |
| Campaign | E01-capability-audit (experiments/E01-capability-audit/) — NOT_STARTED |

## Purpose

This directory holds one audit workspace per evaluated ecosystem. The unit of comparison is the testing laboratory ecosystem, not an individual repository: an ecosystem that spans several repositories or artifacts (for example separate Web, Android, and iOS repositories) is still one system under test (SUT) and has exactly one workspace.

Each workspace records, for its SUT, component provenance, per-modality assessments, cross-cutting property descriptions, evidence records, limitations, and open questions. The rubric, evidence rules, and property definitions are owned by protocol/ and are only referenced here.

## Workspaces

| Directory | SUT id | Ecosystem | Role | Auditor role |
|---|---|---|---|---|
| audits/SUT-01-omnipizza | SUT-01 | OmniPizza | general-purpose candidate | AUDITOR-SUT01-OMNIPIZZA |
| audits/SUT-02-saucelabs | SUT-02 | Sauce Labs Demo Ecosystem | general-purpose baseline | AUDITOR-SUT02-SAUCELABS |
| audits/SUT-03-browserstack | SUT-03 | BrowserStack Demo Ecosystem | general-purpose / Web / API baseline | AUDITOR-SUT03-BROWSERSTACK |
| audits/SUT-04-restful-booker | SUT-04 | Restful Booker Platform | Web/API specialist baseline | AUDITOR-SUT04-RESTFULBOOKER |
| audits/SUT-05-juice-shop | SUT-05 | OWASP Juice Shop | security specialist baseline | AUDITOR-SUT05-JUICESHOP |
| audits/SUT-06-webdriverio | SUT-06 | WebdriverIO Native Demo App | mobile specialist baseline | AUDITOR-SUT06-WEBDRIVERIO |

## Files in each workspace

| File | Purpose |
|---|---|
| README.md | Workspace status and instructions |
| audit.md | Structured audit template: header (including environment_types_used and controlled_instance_available), components and provenance, modality assessments (with evidence_refs by evidence_id, verification_refs, structural_scope_note, confirmed_score, and confirmation_state for Score 3 cells), cross-cutting properties, documentation vs implementation contradictions, negative evidence summary, auditor declaration |
| evidence.csv | Evidence records, one per row, using the exact 13-field header below; positive and negative evidence alike; every record has a stable evidence_id |
| limitations.md | Scope, evaluation, environment, and evidence-ceiling limitations, described neutrally |
| unresolved.md | Open questions and cells disputed during adjudication |
| verifications/ | Execution verification records for EXECUTION_VERIFIED evidence (run manifests per schemas/run-manifest.schema.json; file name = verification_id SUT0n-VR-nnnn); created on first use |
| artifacts/ | Retained artifacts referenced by verification records; created on first use |

evidence.csv header (exact field names, exact order):

```
evidence_id,ecosystem_id,modality,provisional_score,evidence_type,repository,commit_sha_or_release,file_path_or_endpoint,mechanism,expected_behavior,evidence_status,structural_scope_note,notes
```

evidence_id convention: SUT01-EV-0001, SUT02-EV-0001, … SUT06-EV-0001, sequential per ecosystem, never reused (protocol/evidence-rules-v1.md). Every reference to an evidence record, in any file, uses evidence_id; CSV row and line numbers are never used.

## Write boundaries

- Each auditor role writes only inside its own workspace directory (table above) and nowhere else in the repository.
- No other role writes inside an audit workspace. Provenance sequence (authoritative text in manifests/README.md): the ORCHESTRATOR pins the evaluated version of every component surface in manifests/sut-manifest.yaml before E01 starts; the auditor copies that record unchanged into audit.md section 2, verifies surface presence during E01, and records any discrepancy in unresolved.md rather than editing the manifest.
- ADJUDICATOR-EU-01 reads all six workspaces but writes its output outside audits/ (see protocol/agent-governance-v1.md). Cells it disputes are cross-referenced by the auditor in unresolved.md.
- Any SUT is a read-only object of study: auditors never modify, patch, configure beyond documented setup, or extend the SUT they evaluate.

## Rules recap

- Capability scale: Score 0 — UNSUPPORTED; Score 1 — TECHNICALLY EXECUTABLE; Score 2 — EXPERIMENTALLY USABLE; Score 3 — EXPERIMENTALLY CONTROLLABLE. Defined in protocol/capability-rubric-v1.md; applied unchanged to every modality of every SUT.
- Evidence statuses: DOCUMENTED, SOURCE_VERIFIED, EXECUTION_VERIFIED, INFERRED. Record requirements are defined in protocol/evidence-rules-v1.md.
- Cross-cutting properties (State Controllability; Resetability; Determinism; Observability; Automation Affordances; Cross-platform Scenario Parity; Cross-layer State Continuity; Functional Complexity) are described, not scored. Defined in protocol/cross-cutting-properties-v1.md.
- Frozen modality list, research questions, and hypotheses: protocol/study-design-v1.md.
- Every non-zero provisional score requires evidence records in evidence.csv, cited by evidence_id. INFERRED evidence alone cannot justify score 3. Generic tool reachability never justifies a score >= 2. Local deployability never justifies any score. The evaluated version, as pinned by the ORCHESTRATOR, must already expose any mechanism claimed for score 3; auditors never switch to another version because it exposes a more favorable capability.
- A Score 3 cell also carries a `confirmation_state`, derived from the evidence_status of its supporting records, not chosen independently: `UNCONFIRMED_SCORE_3` when the only supporting record is DOCUMENTED; `CONFIRMED` when at least one SOURCE_VERIFIED or EXECUTION_VERIFIED record supports the mechanism (EXECUTION_VERIFIED where SOURCE_VERIFIED is unobtainable). An UNCONFIRMED_SCORE_3 cell stays visible in the matrix but is never counted as a confirmed / adjudicated Score 3 (protocol/capability-rubric-v1.md, "Score 3 confirmation"; schemas/sut-audit.schema.json).
- Every cell also carries `confirmed_score`, per the general tie-break rule ("Tie-break rule for undecidable adjacent scores", protocol/capability-rubric-v1.md): the highest rubric level whose complete requirements are fully supported by the evidence. When no tie-break ambiguity exists (the ordinary case) `confirmed_score` equals `provisional_score`; when the auditor's `provisional_score` is a higher, unresolved candidate (as with an UNCONFIRMED_SCORE_3 cell, where `confirmed_score = 2` and `provisional_score = 3`), only `confirmed_score` enters counts, frequency tables, and comparisons (protocol/statistical-analysis-plan-v1.md). Averaging, rounding up, plausibility, source-code modifiability, and vendor reputation are never used to pick between adjacent levels.
- Evidence status reflects the strongest evidence actually obtainable. DOCUMENTED, SOURCE_VERIFIED, and INFERRED records need no run manifest; every EXECUTION_VERIFIED record needs an execution verification record in verifications/ carrying environment_type (protocol/evidence-rules-v1.md). An ecosystem is not penalized because SOURCE_VERIFIED is unobtainable for a closed-source hosted component.
- Environment discipline: auditing may use documentation, source, PUBLIC_HOSTED deployments (non-destructive, session-scoped, within documented use only), and controlled local execution when necessary (protocol/study-design-v1.md, section 10).
- Manual and exploratory testing may be described but never contribute to the quantitative primary comparison.
- Intentionally narrow scope is not a penalty. A structurally absent surface is Score 0 (no N/A level exists), annotated with a structural_scope_note in audit.md and in the evidence record, and described neutrally in limitations.md. Score 0 means the ecosystem does not provide that modality; it is not evidence that the ecosystem is poor within its specialty (protocol/study-design-v1.md, section 11).
- These rules apply identically to all six workspaces, including audits/SUT-01-omnipizza. No SUT receives a privileged interpretation, a different rubric, or a different procedure.

## Status

Status: all audits NOT_STARTED; no findings, scores, or evidence exist. Every file in this directory is a template.

## Do not start

Audits must not begin until (1) the protocol files are in state FROZEN-PRE-DATA per protocol/change-control-v1.md, which requires explicit human approval, and (2) ORCHESTRATOR issues an explicit start instruction. Populating any cell before both conditions hold invalidates that workspace.
