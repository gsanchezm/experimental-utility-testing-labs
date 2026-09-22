# Issue (xviii) — Setup Effort Counting Rules: Source-Backed Ambiguity Analysis

| Field | Value |
|---|---|
| Prepared by | ORCHESTRATOR |
| Date | 2026-09-21 |
| Context | E03-resetability PRE-START configuration preparation, human-authorized (pre-start preparation only; does not authorize campaign start) |
| Scope | protocol/study-design-v1.md, section 13, issue (xviii); protocol/setup-effort-v1.md, section 5 |
| Status of this document | Analysis only. It resolves nothing and creates no new protocol version. It is not itself change-controlled. |

## 1. What is already fixed (not ambiguous)

protocol/setup-effort-v1.md, section 5, "Counting rules," rules 1–7 are frozen (FROZEN-PRE-DATA) and unambiguous:

1. One action = one experimenter-initiated operation with an observable effect.
2. A scripted sequence counts each constituent action.
3. Authentication counts.
4. Retries caused by failure are counted and tagged as retries.
5. Manual actions are recorded with a reason.
6. The starting state is declared; provisioning precedes it and is never counted.
7. The same canonical scenario is used across ecosystems; a count is comparable only between two ecosystems both marked COMPARABLE on the same mapping record.

Section 4 (Action classes) is also frozen: API action, UI action, navigation action, state/configuration action, reset action, manual action — exactly six classes, exhaustive by stated purpose, not by mechanism.

None of the above is reopened by this analysis. Issue (xviii) concerns exactly two items left open beneath this frozen layer.

## 2. The two items Issue (xviii) actually names

protocol/study-design-v1.md, section 13, row (xviii) (verbatim scope): "Two Setup Effort counting rules remain open (protocol/setup-effort-v1.md, section 5): whether verification that the target state was reached counts as an action, and how a partially successful action is counted." Status: DEFERRED-BEFORE-CAMPAIGN. `requires_human_decision`: **yes** (register's own column, not this analysis's inference). protocol/setup-effort-v1.md, section 5, closing paragraph and section 11 state the same two items in the same words and add: "Until then no count may be used for analysis," and, if decided after protocol freeze (which already happened — protocol froze 2026-09-16 without resolving this), the decision "creates protocol/setup-effort-v2.md under protocol/change-control-v1.md; the human reviewer may instead decide it at protocol freeze" (not exercised).

### 2.1 Sub-item A — does verification that the target state was reached count as a Required Action?

**Textual evidence for two live readings, not one:**

- Rule 1 ("one experimenter-initiated operation with an observable effect... An operation with no observable effect on the ecosystem or the experimenter's position in it is not an action") is genuinely two-armed: a verification call (e.g. `GET /api/session` to confirm a reset succeeded) has *no effect on the ecosystem* (it is read-only) but plausibly *does* have "an observable effect on the experimenter's position in it" (it changes what the experimenter knows/can now do). The rule does not say which arm controls, and it is exactly the arm that was left open per section 5's own closing bullet.
- Section 4's six action classes contain no "verification" or "observation" class. This could mean verification is categorically outside Required Actions (it is not a class, so it is not counted) — or it could mean a verification call is simply classified under an existing class by mechanism (an API action or UI action whose purpose happens to be verification) and is counted like any other action of that class. The action-class rule ("classified by its purpose, not by its mechanism") does not resolve this because "verify" is not one of the purposes the six classes name (establish state, reach a screen, configure, reset, act manually) — verification fits none of them by purpose.
- Section 6.1 (Duration) explicitly *does* include verification time in the Duration boundary ("the duration includes the time to perform that verification, not merely to attempt the state change"). Section 6.4 explicitly disclaims that this settles the Required Actions question: "this section defines only the timing boundaries of Duration, not the Required Actions partial-success counting rule" (and, by the same logic used for verification generally, not the verification-as-action question either — Duration and Required Actions are stated throughout the document as two distinct metrics, never inferred from one another).
- `schemas/run-manifest.schema.json`'s `actions[].class` enum (API action, UI action, navigation action, state/configuration action, reset action, manual action) confirms the same gap operationally: there is no schema-level way to tag an action as "this was a verification, exclude/include per rule X" — a genuinely unresolved value, not an omission the schema quietly answers.

**Interpretation A1 — verification never counts.** Rationale: verification is read-only by construction (no state-changing effect on the ecosystem); "the experimenter's position" is stretched too far if it includes mere knowledge gain; Duration already captures verification cost separately, so Required Actions counting it too would double-count effort across the two metrics. Consequence: reset-procedure Required Actions counts include only state-changing steps; an ecosystem requiring an extra confirmatory read after every reset shows no penalty in the primary metric.

**Interpretation A2 — a verification call counts as one action of its underlying mechanism's class (typically API action or UI action).** Rationale: rule 1's "operation with an observable effect... on the experimenter's position" plainly covers a state check that changes what the experimenter now knows and can now do next; the six action classes are stated as covering "discrete per-run/per-condition actions," a verification step is a discrete per-run action an experimenter must perform, and nothing in section 4 excludes it. Consequence: an ecosystem requiring more verification calls (e.g. per-surface confirmation on a multi-surface reset) shows a higher Required Actions count for the identical underlying reset, directly affecting H2's per-scenario comparison.

These produce different Required Actions counts for the *same* observed reset procedure whenever a scenario's reset includes an explicit post-reset check (which E03's own Required evidence list mandates: "Post-reset state verification record... and the comparison against the known initial state" — README.md, line 29). The two readings are not a matter of degree; they diverge by exactly the number of verification calls in every E03 reset procedure.

### 2.2 Sub-item B — how is a partially successful action counted?

**Textual evidence for at least three live readings, not one:**

- Rule 4 addresses *retries* (a fully failed action, repeated) but is silent on an action that *partially* succeeds on a single attempt (for example, a UI form submission that updates 2 of 3 required fields, or an API call returning 207/partial success). Partial success is a distinct case from a clean success or a clean failure, and section 5 explicitly lists it separately from the retry rule as its own open item.
- Section 6.3 (Setup failure) establishes that "the outcome is recorded as a failure... and no successful setup duration is fabricated" for *Duration* when the target state is not successfully established — but this is a *Duration* rule (section 6, subordinate to Required Actions per section 3), and section 6.4 explicitly disclaims that it settles the Required Actions partial-success rule.

**Interpretation B1 — a partially successful action counts as one action, full stop (success/failure of the action is irrelevant to the count; count is of operations performed, not operations that fully succeeded).** Rationale: rule 1 counts "one experimenter-initiated operation," with no success qualifier attached to the base count (only retries — full re-attempts — get special tagging under rule 4); this is the most literal reading of "count of discrete... actions." Consequence: partial success is invisible to Required Actions; it would only show up qualitatively (via the run's `outcome.status` or notes) or in Duration/failure reporting.

**Interpretation B2 — a partially successful action is tagged and counted like a retry (i.e., the same class of special-case tagging rule 4 already applies to full failures is extended to partial ones), because it is not a "clean" attempt.** Rationale: rule 4's principle — that a non-clean attempt is recorded and tagged, not silently folded into an ordinary count — plausibly generalizes to a partial success, which is exactly as "not clean" as a full failure from the standpoint of measuring how much effort the ecosystem actually demanded before the target state was reached. Consequence: a further corrective action (needed to complete the partially-succeeded step) would then also need a rule for whether it is a fresh action or a tagged continuation of the same one — a rule that does not exist under either B1 or B2 and would need to be authored as part of resolving this sub-item.

**Interpretation B3 — a partial success is not countable in Required Actions at all until it resolves to a clean success or a clean failure; the campaign configuration must define, per action, what "counts as achieving the action's purpose" so partial success cannot arise ambiguously.** Rationale: rule 1 requires "an observable effect," and "partial" is not itself one of the frozen action classes or an outcome category defined anywhere in setup-effort-v1.md; treating it as underspecified until the campaign configuration pins an operational success criterion per action type avoids inventing a counting behavior the frozen document never stated. Consequence: campaign configuration would need to enumerate, in advance, an operational "did this action achieve its purpose" test per action class — additional configuration work not currently specified anywhere.

These three readings produce different Required Actions counts whenever any run's reset or establish procedure includes a step that only partially succeeds — a condition E03's own repeatability-determinism discipline (N = 50 repetitions per condition) makes likely to occur at least occasionally across a full campaign.

## 3. Why this is not resolvable from frozen sources alone

Both sub-items meet the bar the operating instruction sets for classification B (HUMAN_RULING_REQUIRED): the frozen artifacts leave **more than one operationally executable interpretation** for each sub-item, none of the six frozen counting rules (section 5, rules 1–7), the six action classes (section 4), the Duration rules (section 6, which repeatedly and explicitly disclaim settling Required Actions), or the run-manifest schema resolves either sub-item, and the Open-Issue Register row itself — written and frozen alongside the rest of protocol v1 — independently marks `requires_human_decision: yes` and status DEFERRED-BEFORE-CAMPAIGN (not RESOLVED), naming E02 and E03 configuration as the point of resolution. This analysis reaches the same conclusion as the frozen register through independent textual inspection: it is not merely repeating the register's label.

Neither this analysis nor the E03 draft configuration it accompanies chooses an interpretation, adds a metric, alters H2's variable definition, or resolves the register row. Under protocol/study-design-v1.md, section 13, row (xviii): "no count may be used for analysis" until this is resolved.

## 4. Classification

**ISSUE (xviii) = HUMAN_RULING_REQUIRED.**

## 5. Smallest human decision needed

Two independent binary/ternary choices, each with the consequence stated above:

- **A.** Does a post-reset (or post-establish) verification call count as a Required Action? → A1 (never counts) or A2 (counts, classified by its underlying mechanism).
- **B.** How is a per-attempt partially successful action counted? → B1 (counts as one ordinary action, no special tag), B2 (counted and tagged like a retry), or B3 (not countable until the campaign configuration defines a per-action-class success test — itself additional work).

A human decision on A and B, recorded under protocol/change-control-v1.md (creating protocol/setup-effort-v2.md, since protocol v1 is already frozen, per protocol/setup-effort-v1.md section 11 and section 13 row (xviii)'s own resolution path), is the minimum needed before any E03 (or E02) Required Actions count may be recorded for analysis, and before the E03 canonical-scenario mapping's `entry_and_steps` fields (protocol/equivalent-scenario-mapping-v1.md, section 4) can be frozen without leaving an unresolved counting rule baked into a frozen record.

No recommendation is made between A1/A2 or B1/B2/B3: nothing about OmniPizza (SUT-01) or any other SUT makes one interpretation more favorable in a way that would be knowable before data collection, and AGENT-INSTRUCTIONS.md rule 3 / this document's neutrality require that this analysis not select on behalf of the human research lead.
