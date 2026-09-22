# Capability Rubric

| Field | Value |
|---|---|
| Document | protocol/capability-rubric-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | first iteration instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT); second iteration (issue (x), explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT); final pre-freeze checklist closure (tie-break rule, explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## Purpose and scope

This rubric defines how an auditor assigns a capability score to one cell of the capability matrix. A cell is one (ecosystem, modality) pair, where the ecosystem is one of the six evaluated ecosystems, each a system under test (SUT; SUT-01 to SUT-06, identities in manifests/) and the modality is one of the nine frozen testing modalities defined in protocol/study-design-v1.md: Web UI Functional; API; Android Native; iOS Native; Performance; Accessibility — Web only; Visual Testing; Security Testing; Localization / i18n.

The rubric is applied in campaign experiments/E01-capability-audit. How its outputs feed the Experimental Utility profile is defined in protocol/study-design-v1.md, not here.

Scope rules:

- A score is PROVISIONAL when assigned by an auditor. It becomes adjudicated only after review by ADJUDICATOR-EU-01 (protocol/agent-governance-v1.md).
- Scores are per modality only. They are NEVER summed, averaged, weighted, or otherwise aggregated into a single index, score, or ranking. A capability matrix is reported as a matrix.
- Manual and exploratory testing are not modalities and are not scored. They may be described in audits/<SUT>/audit.md but contribute nothing to the quantitative primary comparison.
- The rubric scores what the evaluated version of the SUT exposes, not what a testing tool can do, and not what the SUT could be modified to do.

## The scale

The four levels below are the complete scale. No intermediate, fractional, or additional level exists in v1. There is no N/A level.

## Score 0 — UNSUPPORTED

No reasonable surface exists for the testing modality.

Score 0 is the valid score when the ecosystem structurally lacks the surface a modality requires (for example, a mobile-only ecosystem with no Web surface scores 0 on Accessibility — Web only). The score means that the ecosystem does not provide that experimental modality. It must NOT be interpreted as evidence that the ecosystem is poor within its intended specialty; the interpretation rules in protocol/study-design-v1.md, section 11, apply. A structurally absent surface is annotated with a `structural_scope_note` (see "Structural scope note" below); the annotation is descriptive and never replaces or modifies the score.

## Score 1 — TECHNICALLY EXECUTABLE

An open-source testing tool can technically target the SUT, but the SUT provides no specific experimental support, known condition, stable scenario, or meaningful ground truth for that modality.

Simply being able to point Playwright, k6, axe-core, Pixelmatch, ZAP, Appium, Mobilewright, or another generic tool at the application must NOT justify a score >= 2.

## Score 2 — EXPERIMENTALLY USABLE

The SUT exposes meaningful and reasonably stable states, scenarios, data, behavior, or interfaces that permit a repeatable experiment in the modality, but direct experimental control, deterministic state establishment/reset, or known ground truth is absent or incomplete.

## Score 3 — EXPERIMENTALLY CONTROLLABLE

The SUT exposes an existing documented or verifiable mechanism that enables the experimenter to establish, activate, configure, seed, or reset a known experimental condition and observe a defined expected outcome.

Examples:

* API-based state seeding
* reset endpoint
* deterministic test account
* fault injection
* documented intentional vulnerability
* controlled performance degradation
* controlled accessibility fault
* controlled visual condition
* explicit market/locale selection
* deep link into a prepared state

A SUT must NOT receive score 3 merely because its source code could be modified to add such a capability.

The evaluated version must already expose it.

### Score 3 confirmation

Resolves protocol/study-design-v1.md, section 13, issue (x) (explicit human decision, 2026-09-16). A Score 3 answer under the decision procedure below carries one of two `confirmation_state` values, derived from the evidence_status of the record(s) that support it (protocol/evidence-rules-v1.md); the auditor does not choose it independently of the evidence:

- `UNCONFIRMED_SCORE_3` — the only evidence supporting the mechanism is DOCUMENTED (official documentation of the evaluated version explicitly describes a mechanism that would qualify for Score 3 under this rubric). Recorded as `provisional_score = 3`, `confirmation_state = UNCONFIRMED_SCORE_3`. This candidate is visible in the audit matrix but is NOT an adjudicated Score 3 and does not enter any confirmed Score 3 count, table, or comparison (protocol/statistical-analysis-plan-v1.md, section 4.3).
- `CONFIRMED` — at least one SOURCE_VERIFIED or EXECUTION_VERIFIED record supports the same mechanism: SOURCE_VERIFIED confirms Score 3 when inspection of the pinned evaluated version's source demonstrates the mechanism is implemented; EXECUTION_VERIFIED confirms Score 3 when execution provenance demonstrates the mechanism and its expected observable outcome. Only a CONFIRMED Score 3 is an adjudicated Score 3.

`confirmation_state` is null for `provisional_score` 0, 1, or 2; it is set only when the cell's score is 3.

For a closed-source or hosted-only component (protocol/study-design-v1.md, section 10.4), SOURCE_VERIFIED is unobtainable; EXECUTION_VERIFIED is then the required confirming status. DOCUMENTED evidence alone never confirms Score 3, for any ecosystem, including a closed-source one.

If DOCUMENTED evidence and SOURCE_VERIFIED or EXECUTION_VERIFIED evidence disagree about the same mechanism, both records are retained (protocol/evidence-rules-v1.md, contradiction rule) and the contradiction is stated in audits/<SUT>/unresolved.md. For the purpose of Score 3 confirmation, the stronger empirical evidence — SOURCE_VERIFIED or EXECUTION_VERIFIED — governs over DOCUMENTED. This does not create an ordering between SOURCE_VERIFIED and EXECUTION_VERIFIED themselves, which remain equally preferred (protocol/evidence-rules-v1.md).

## Structural scope note

`structural_scope_note` is a descriptive annotation attached to a cell (audits/<SUT>/audit.md, section 3; schemas/sut-audit.schema.json) and to the evidence records of that cell (protocol/evidence-rules-v1.md, field 12; schemas/evidence.schema.json). It explains a structural reason why a modality is absent or narrow in the evaluated ecosystem. Its value is one of the following tokens, optionally followed by a colon and free text:

| Token | Meaning |
|---|---|
| NO_WEB_SURFACE | The evaluated version has no Web surface. |
| NO_MOBILE_SURFACE | The evaluated version has no Android and no iOS surface (free text names which, if only one is absent). |
| NO_API_SURFACE | The evaluated version has no programmatic API surface. |
| INTENTIONAL_SPECIALIST_SCOPE | The ecosystem's documented purpose intentionally excludes the modality (cite the documentation in the evidence record). |
| OTHER_STRUCTURAL_REASON | Any other structural reason; the free text is required. |

Rules:

- The note is filled when the score is 0 for a structural reason, and may be filled for a Score 1 cell whose narrowness is structural. It is left empty for every other cell.
- The note never changes the score, never creates an exemption, and never removes the cell from any table. Score 0 with a note and Score 0 without a note are the same score.
- The note is evidence-backed: the structural absence is recorded as negative evidence (protocol/evidence-rules-v1.md, "Negative evidence") with the same evidence-status discipline as any other record.
- The same vocabulary applies to every ecosystem, including SUT-01. A general-purpose ecosystem that lacks a surface records the note exactly as a specialist does.

## Decision procedure

The auditor answers the following questions in order for each cell, against the evaluated version pinned in manifests/ and cited in the supporting evidence records. The first question answered "no" fixes the score.

1. **Surface.** Does any reasonable surface for this modality exist in the evaluated version? If no, the score is 0; record the negative evidence and, when the absence is structural, the `structural_scope_note`. Stop.
2. **Specific support.** Does the SUT itself provide specific experimental support for this modality — a known condition, a stable scenario, meaningful data, or ground truth — beyond the fact that a generic tool can reach it? If no, the score is 1. Stop.
3. **Control and expected outcome.** Does the evaluated version expose a mechanism to establish, activate, configure, seed, or reset a known condition, AND a defined expected outcome for that condition, with evidence at the status required by protocol/evidence-rules-v1.md? If yes, the score is 3, with `confirmation_state` set per "Score 3 confirmation" above. Otherwise the score is 2.

If any question above cannot be answered with confidence either way, do not force a yes/no answer: apply "Tie-break rule for undecidable adjacent scores", below.

Constraints on every step:

- Potential capability does not count. A mechanism that could be added by modifying source code, configuration, or infrastructure is treated as absent.
- Vendor products do not count. A vendor's commercial testing platform, cloud device grid, or service does not confer capability on the vendor's demo SUT. Only what the evaluated demo ecosystem itself exposes is scored (see protocol/evidence-rules-v1.md).
- Tool reachability does not count. That a runner, scanner, or comparison tool from the intended toolchain can be pointed at the SUT is the definition of Score 1, not evidence for a higher score.
- Local deployability does not count. That an ecosystem can be cloned, built, self-hosted, or run locally is environment provenance (protocol/study-design-v1.md, section 10), not a capability; it justifies no score and no part of a score. Conversely, that an ecosystem is only available hosted justifies no deduction.
- The evidence ceiling does not lower the score. Where SOURCE_VERIFIED evidence is unobtainable for a closed-source or hosted-only component, the score is decided by what the evaluated version demonstrably exposes, with the evidence status reflecting the strongest evidence actually obtainable (protocol/evidence-rules-v1.md).
- The evaluated version counts. Each answer refers to the version pinned by the ORCHESTRATOR in manifests/sut-manifest.yaml and cited in the evidence record (commit SHA, release, or the strongest reproducible identifier available), not to a newer, older, or forked version. An auditor never switches to another version because it exposes a more favorable capability (manifests/README.md; protocol/agent-governance-v1.md).
- Undecidable adjacent scores. Apply the tie-break rule ("Tie-break rule for undecidable adjacent scores", below) rather than deciding by estimate or plausibility.

## Tie-break rule for undecidable adjacent scores

Resolves the tie-break freeze-checklist item of protocol/study-design-v1.md, section 13 (explicit human decision, 2026-09-16). This rule is general: it governs any adjacent pair of rubric levels (0/1, 1/2, 2/3) whenever a Decision procedure question above cannot be answered with confidence. "Score 3 confirmation" above is this rule's named, evidence-status-specific special case for the 2/3 boundary once Decision procedure step 3 has already been answered "yes" at Score 3 (see "Relation to Score 3 confirmation" below).

**Rule.** The confirmed capability score for a cell — the value recorded as `confirmed_score` and entered into every count, frequency table, and comparison (protocol/statistical-analysis-plan-v1.md; analysis/README.md) — is the highest rubric level whose complete requirements are fully supported by the available admissible evidence (protocol/evidence-rules-v1.md) under the Decision procedure above.

- If the evidence fully supports level N (every requirement of level N's Decision procedure question is met) but only partially supports the adjacent higher level N+1 (the auditor cannot answer "yes" with confidence to the question that would raise the score to N+1), the recorded `confirmed_score` is N.
- The higher, unresolved level N+1 may be retained as a candidate in `provisional_score` (audits/<SUT>/audit.md; schemas/sut-audit.schema.json), stated explicitly as unresolved, together with the specific unresolved verification requirement that would need to be met to raise it, in the notes of the supporting evidence record and in audits/<SUT>/limitations.md. The cell is flagged for adjudication.
- If the evidence cannot fully establish even the lower of the two candidate levels, the rule applies one level down: `confirmed_score` is the highest level below that whose complete requirements are fully supported.
- `confirmed_score` and `provisional_score` coincide whenever no tie-break ambiguity exists for the cell (the ordinary case); `confirmed_score` is recorded as a distinct value only when the tie-break rule caps it below the auditor's `provisional_score`.

**This is a determination, not an estimate.** Applying the rule, the auditor never:

- averages two adjacent levels;
- rounds up to the higher level;
- selects the higher level because it is plausible or likely;
- awards the higher level on the basis that the SUT's source code could be modified to satisfy it (already excluded by "Potential capability does not count", above);
- uses a vendor's reputation, market position, or commercial product as a tie-breaker (already excluded by "Vendor products do not count", above).

This rule applies identically to every SUT, including SUT-01 ("Equal treatment", below), and to every adjacent pair of levels, not only 2/3.

"Provisional" carries two independent senses in this rubric; they are not to be conflated. In the lifecycle sense (Scope rules, above), both `confirmed_score` and `provisional_score` are auditor-assigned and "provisional" until adjudicated by ADJUDICATOR-EU-01 — the tie-break distinction is orthogonal to, and exists entirely within, that pre-adjudication stage. In the tie-break sense used in this section, `provisional_score` specifically denotes the auditor's candidate level, which `confirmed_score` may cap below it.

**Relation to Score 3 confirmation.** "Score 3 confirmation" above is the named special case of this rule for the situation where Decision procedure step 3 has already been answered "yes" at Score 3 — the auditor is not in doubt that the mechanism and outcome exist — and the remaining question is only the strength of the evidence status behind that answer: `confirmation_state = CONFIRMED` corresponds to `confirmed_score = 3` (no gap from `provisional_score`); `confirmation_state = UNCONFIRMED_SCORE_3` corresponds to `confirmed_score = 2`, `provisional_score = 3` (DOCUMENTED-only evidence is treated as not fully supporting Score 3, so it does not enter a Score 3 count anywhere, including "number of modalities per level" tables, not only the H1 confirmed-Score-3 count). Where Decision procedure step 3's answer is itself undecidable — a doubt about whether the mechanism or outcome meets the rubric's criteria at all, not an evidence-status question — this general tie-break rule applies directly and `confirmation_state` stays null (it is defined only once step 3 is answered "yes"); the reason for the gap is stated in free text in the supporting evidence record's notes and in audits/<SUT>/limitations.md, per "Evidence requirement" below.

## Evidence requirement

- Every non-zero score requires at least one evidence record in audits/<SUT>/evidence.csv that conforms to protocol/evidence-rules-v1.md and is cited by its `evidence_id`. A cell with no evidence record is scored 0. A Score 0 cell also carries at least one negative-evidence record.
- Score 3 cannot rest on INFERRED evidence alone. DOCUMENTED evidence alone supports only a provisional Score 3 candidate (`confirmation_state = UNCONFIRMED_SCORE_3`); it never supports a confirmed / adjudicated Score 3 (protocol/study-design-v1.md, section 13, issue (x), RESOLVED; see "Score 3 confirmation" above).
- A Score 3 supported by EXECUTION_VERIFIED evidence cites the execution verification record(s) through the evidence record (protocol/evidence-rules-v1.md, "Execution verification records").
- A cell may have several evidence records supporting different scores. The auditor's judgement under the decision procedure is recorded in audits/<SUT>/audit.md as `provisional_score`, capped where the tie-break rule applies to produce `confirmed_score` ("Tie-break rule for undecidable adjacent scores", above); neither is automatically the maximum of the records' provisional_score values.
- Contradictions between documentation and implementation are recorded as separate evidence records and the cell is flagged for adjudication. The auditor does not resolve a contradiction by choosing the evidence that favors the SUT.
- Negative evidence (searched and not found) is recorded and retained even when the resulting score is 0.

## Ground truth linkage

The ground truth rule is defined in protocol/study-design-v1.md; this section only states how it enters the rubric.

- Ground truth is a defined expected outcome, known before execution, against which observed behavior can be compared. In the rubric it is the property that separates Score 3 from Scores 1 and 2: Score 1 has no ground truth; Score 2 has ground truth that is absent or incomplete; Score 3 requires a defined expected outcome tied to a mechanism the SUT exposes.
- Generic tool compatibility never constitutes ground truth. The output of a runner, scanner, or comparison tool (a test report, a scan result, a screenshot diff, a load-test summary) is an observation, not an expected outcome. Ground truth must originate from the SUT: its documentation, source, seed data, test accounts, intentional faults, or equivalent artifacts of the evaluated version.
- The evidence record's expected_behavior field carries the ground truth claim; a Score 3 record with an empty expected_behavior field does not support Score 3.

## Equal treatment

- Every ecosystem is scored with the same rubric, the same decision procedure, the same evidence requirements, and the same adjudication path.
- Specialist SUTs (Web/API, security, mobile baselines) are not penalized for intentionally narrow scope. A modality outside a specialist SUT's intended scope is scored under the same decision procedure as any other cell (typically Score 0 with a `structural_scope_note`), remains visible in the matrix, and is interpreted under protocol/study-design-v1.md, section 11: Experimental Breadth and Modality Depth answer different questions, and no weighted global score exists in which narrow breadth could be traded against depth. This rubric adds no level, marker, or exemption beyond the descriptive note.
- The role assigned to an ecosystem (candidate or baseline) has no effect on scoring.
- OmniPizza (SUT-01) receives no privileged interpretation. It is one evaluated SUT and is scored exactly as the other five.
- Adjudication is performed by ADJUDICATOR-EU-01, never by the auditor that produced the provisional score.

## Output

- Provisional scores are recorded in audits/<SUT>/audit.md, one row per modality, each row naming by `evidence_id` the evidence records in audits/<SUT>/evidence.csv that support it, and carrying the `structural_scope_note` where applicable. Each row also carries `confirmed_score` when the tie-break rule caps it below `provisional_score` ("Tie-break rule for undecidable adjacent scores", above); `confirmed_score` is the value used by every count, frequency table, and comparison.
- Evidence records are recorded in audits/<SUT>/evidence.csv per protocol/evidence-rules-v1.md.
- Adjudicated scores are produced only by ADJUDICATOR-EU-01, only after all six audits are complete, and are recorded where protocol/agent-governance-v1.md specifies, referencing evidence by `evidence_id`.
- No provisional or adjudicated score exists at this time. The repository is in the SETUP phase and no audit has been performed.

## Versioning

This document is capability-rubric v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6). The "Score 3 confirmation" section and the `confirmation_state` value were added during the second pre-freeze hardening iteration of 2026-09-16, while the document was DRAFT (protocol/change-control-v1.md, section 2, DRAFT -> DRAFT), resolving protocol/study-design-v1.md, section 13, issue (x). The "Tie-break rule for undecidable adjacent scores" section and the `confirmed_score` value were added during the final pre-freeze checklist closure of 2026-09-16 (explicit human decision), while the document was still DRAFT (DRAFT -> DRAFT), generalizing the same evidence-completeness principle to every adjacent pair of rubric levels; it changed no rubric level, no decision-procedure question, and no Score 3 confirmation rule. Any change to the levels, their wording, the decision procedure, or the evidence requirement now that the document is frozen creates protocol/capability-rubric-v2.md per protocol/change-control-v1.md; this frozen version is never overwritten in place, except for the header state field and successor pointer. Audits cite the rubric version they were scored under.
