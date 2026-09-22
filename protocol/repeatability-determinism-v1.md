# Repeatability and Determinism Measurement Approach

| Field | Value |
|---|---|
| Document | protocol/repeatability-determinism-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | first iteration instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT); second iteration (issue (xi), explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## 1. Purpose

This document specifies the intended future approach for measuring how reliably each evaluated testing laboratory ecosystem (each system under test, SUT) can re-establish a controlled condition and how consistently that condition produces the same outcome.

It informs:

- RQ3 Repeatability and Determinism (full text in protocol/study-design-v1.md; STATUS: PROVISIONAL — PRE-DATA-COLLECTION).
- Dimension 3, Repeatability and Determinism, of the Experimental Utility profile.
- Campaign E02-state-establishment (as a prerequisite: a condition must be establishable before it can be repeated), campaign E04-repeatability, and campaign E05-determinism.

Repeatability and determinism are reported as separate quantities within the per-dimension profile: Target-State Reproduction Rate (TSRR) for repeatability, and Conditional Exact Outcome Rate (CEOR), End-to-End Reproducible Outcome Rate (E2E-ROR), and Outcome Entropy for determinism (Section 4). They are never combined into a single value, and no aggregate or weighted utility score exists in this study.

Nothing in this document is a measurement. It describes what will be measured, how, and under which rules, once the protocol is frozen and data collection begins.

## 2. Definitions

| Term | Definition |
|---|---|
| Repeatable condition | A controlled initial state plus a defined stimulus that can be re-established on demand by a declared procedure. A condition is identified by an ecosystem id (SUT-01 to SUT-06), a modality from the frozen modality list, and a condition id assigned within the campaign. |
| Target state | The initial state that the declared procedure is intended to produce before the stimulus is applied (for example: a specific data fixture loaded, a specific session state, a specific configuration). |
| Target-state reproduction | One attempt at re-establishing the target state that is verified successful by a pre-declared verification check. The verification check is part of the condition definition and is written before any attempt. |
| Expected outcome | The pre-declared categorical outcome that the stimulus is expected to produce when applied to the target state. Expected outcomes are written before execution; they are never derived from observed executions. |
| Exact outcome match | An execution whose observed categorical outcome equals the expected outcome under the pre-declared comparison rule for that condition. What counts as "equal" (for example, which response fields, which UI state, which artifacts) is fixed per condition before execution. |
| Outcome category | One of a closed set of categorical labels defined for a condition before execution, into which every observed execution is classified. The set must include labels for every failure mode that can be distinguished. |

### Relation to the Determinism cross-cutting property

Determinism is a cross-cutting property defined in protocol/cross-cutting-properties-v1.md. This document operationalizes how that property is measured for RQ3; the property definition is not restated here.

For each condition, the behavior class is documented separately from the measured rates, using the classes named in protocol/cross-cutting-properties-v1.md: deterministic, stochastic, time-dependent, or external dependency. The documented class is a description of the mechanism as understood before execution, declared as an independent variable of the campaign that measures the condition (for example experiments/E05-determinism/README.md) and locked, per condition, in that campaign's configuration at campaign start (protocol/change-control-v1.md, section 7); the measured rates are observations made afterward. A condition's declared class is not revised once execution has begun, even if the observed rates suggest a different class; a condition documented as one class and measured as another is itself a recorded finding once data exists, not a reclassification. "Classified a priori as deterministic" (protocol/study-design-v1.md, H3) means declared deterministic under this rule, before execution.

Statistically reproducible randomness is not determinism. A condition whose outcomes follow a stable distribution across repetitions (for example, a randomized fixture that yields outcome A in about half of executions) is stochastic, even when the distribution is stable. Only a condition whose categorical outcome is the same across all executions is treated as deterministic under this measurement.

## 3. Repetition targets

| Target | Value | Applicability |
|---|---|---|
| Standard | N = 50 executions per repeatable condition | All conditions when operationally feasible |
| Reduced | N = 30 executions per repeatable condition | Expensive mobile conditions (Android Native, iOS Native modalities) only, if justified |

Rules for the reduced target:

- The justification must be recorded BEFORE executing that campaign for that condition. "Before" means: the justification appears in the campaign README (under experiments/E04-repeatability/ or experiments/E05-determinism/) and in the run manifests for that condition prior to the first attempt.
- A justification written after any attempt has run is not valid; the condition then falls under the standard target.
- The justification must state the operational constraint (for example, device or emulator time cost) in concrete terms. The justification must rest on operational cost, never on anticipated results.
- The reduced target applies per condition, not per ecosystem. An ecosystem with both mobile and non-mobile conditions uses N = 50 for the non-mobile conditions.

Any deviation from these targets after freeze is a protocol deviation under protocol/change-control-v1.md.

## 4. Candidate metrics

All metrics are computed per condition per ecosystem. No metric is computed across ecosystems or across dimensions. Formulas are stated here for pre-specification only; no value exists.

Resolves protocol/study-design-v1.md, section 13, issue (xi) (explicit human decision, 2026-09-16): rather than choosing a single denominator for the previously named "Exact Outcome Rate," both readings are kept, as three distinct, separately reported metrics.

A **valid measured attempt** is an attempt executed under the rules of Section 5 (started from the declared reset procedure, recorded with a run manifest, not discarded) and counted toward the condition's N; this includes attempts whose target-state establishment failed.

### Target-State Reproduction Rate — TSRR (primary, campaign E04)

```
TSRR = successful target-state establishments / all valid measured attempts
```

A target-state establishment is successful when the pre-declared verification check passes. Target-state establishment failure counts as a TSRR failure. The denominator includes every valid measured attempt, including those whose target-state establishment failed, was interrupted, or produced an unverifiable state (Section 5).

Interpretation: can the experiment reliably establish the required state?

TSRR is the metric previously named Repeatability Rate in this document; the formula and meaning are unchanged; it is renamed here for terminological consistency with CEOR and E2E-ROR below.

### Conditional Exact Outcome Rate — CEOR (primary, campaign E05)

```
CEOR = executions producing the exact predefined expected outcome / executions in which the required target state was successfully established
```

The denominator counts only executions whose target-state establishment succeeded — the same set counted in the TSRR numerator. Target-state establishment failures are excluded from the CEOR denominator by definition, not by discretion.

If no valid measured attempt for a condition successfully establishes the target state, **CEOR = NOT_ESTIMABLE** for that condition. NOT_ESTIMABLE is not encoded as 0; it is not a capability score; it is reported and propagated as NOT_ESTIMABLE in every table, interval, and comparison that would otherwise use CEOR for that condition (protocol/statistical-analysis-plan-v1.md). No confidence interval is computed for a NOT_ESTIMABLE condition.

Interpretation: given that the intended state was correctly established, does the SUT produce the exact expected outcome?

### End-to-End Reproducible Outcome Rate — E2E-ROR (secondary, campaign E05)

```
E2E-ROR = executions producing the exact predefined expected outcome / all valid measured attempts
```

The denominator is the same as TSRR's: every valid measured attempt, including those whose target-state establishment failed. A target-state establishment failure therefore counts against E2E-ROR, unlike CEOR.

Interpretation: does the complete experiment reproduce successfully from setup through outcome?

### Relationship between the three rates

TSRR, CEOR, and E2E-ROR are three distinct metrics, computed from the same set of valid measured attempts but with different numerators and denominators, and are never collapsed into one value or substituted for one another. TSRR answers whether the target state can be reliably established; CEOR answers whether the SUT is deterministic given a correctly established state; E2E-ROR answers whether the whole condition, setup through outcome, reproduces successfully end to end. Campaign-specific tooling-versus-SUT exclusion and attribution rules for deviations remain DEFERRED-BEFORE-CAMPAIGN (protocol/study-design-v1.md, section 13, issue (xix); Section 6 below) and apply identically to all three rates once fixed.

### Outcome Entropy (secondary determinism measure, campaign E05)

```
H(Y) = -Σ p(y) log2 p(y)
```

- Y is the categorical outcome variable for one condition, computed over the same execution set as the CEOR denominator (executions whose target-state establishment succeeded). H(Y) is computed over the outcomes actually produced by the condition, not diluted by target-state establishment failures that are unrelated to outcome determinism and are already captured by TSRR and E2E-ROR; this alignment is what keeps the H3 conjunction (CEOR = 1.00 and H(Y) = 0, protocol/study-design-v1.md, section 6) satisfiable on a condition's own outcome behavior rather than forced positive by an unrelated establishment failure.
- p(y) is the empirical proportion of those executions that fall in outcome category y.
- The sum runs over all outcome categories defined for the condition before execution. Categories with p(y) = 0 contribute 0 by convention.
- Perfectly deterministic categorical outcomes produce H(Y) = 0. The maximum value for k categories is log2 k.
- H(Y) is NOT_ESTIMABLE under the same condition as CEOR: no valid measured attempt successfully establishes the target state.

Constraints:

- Outcome Entropy is a secondary measure. It supplements CEOR and does not replace it; a condition with high CEOR and low entropy and a condition with low CEOR and low entropy are different situations (consistently correct versus consistently wrong) and are reported as such.
- Outcome categories must be defined before execution. Post-hoc merging or splitting of categories changes the entropy value and is not permitted without a recorded deviation under protocol/change-control-v1.md.
- Entropy is not compared across conditions with different category counts without stating the category count alongside it.

## 5. Execution Rules — v1

The following rules are frozen with protocol v1. They apply to every attempt in campaigns E04-repeatability and E05-determinism.

1. Each attempt starts from the declared reset procedure for that condition. The reset procedure is the one recorded for that ecosystem in campaign E03-resetability; if no reset procedure exists for the condition, the condition is not a repeatable condition and is not executed. Because deterministic reset is required, attempts are executed on a controlled instance (environment_type SELF_HOSTED, LOCAL, EMULATED, or SIMULATED) when an open-source deployment of the evaluated version is available, and never against a PUBLIC_HOSTED instance; a condition for which no controlled instance can be established is recorded as NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE (protocol/study-design-v1.md, section 10.3).
2. Attempts are sequential unless parallelism is documented. If attempts run in parallel, the degree of parallelism, the isolation mechanism, and the reason are recorded in the campaign README and in every affected run manifest before execution.
3. Every attempt is recorded with a run manifest containing at minimum: `campaign_id`, `condition`, `attempt`, `seed` (where applicable; null otherwise), `environment_type`, `outcome`, and `artifacts` (paths under raw-data/). The manifest schema is schemas/run-manifest.schema.json (DRAFT; frozen together with the protocol). `condition`, `seed`, and `outcome.outcome_category` are optional in the generic schema and mandatory for every E04/E05 attempt under this rule.
4. Failures are outcomes, not exclusions. A failed reset, a failed stimulus, a crash, or a timeout is classified into a pre-declared outcome category and counted.
5. No attempt is discarded. There is no re-run to replace an attempt. If an attempt is re-executed for any reason, both the original and the re-execution are recorded, each with its own attempt number, and the reason is recorded.
6. Interruptions are recorded. An attempt interrupted by the operator, the infrastructure, or the tooling is recorded as an attempt with an interruption outcome category and a note describing the cause as far as it is known.
7. Seeds, where the SUT or the tooling exposes them, are recorded per attempt. Whether seeds are held constant or varied within a condition is part of the condition definition and is fixed before execution.
8. Wall-clock timestamps are recorded per attempt for traceability only. Timing values are not used in any metric in this document (see Section 6).

## 6. What is NOT measured here

- Speed is not a determinism criterion. Execution duration and reset duration are recorded and analyzed under Setup Effort (dimension 6) and campaign E08-performance where relevant; they do not enter TSRR, CEOR, E2E-ROR, or Outcome Entropy.
- Tool flakiness versus SUT non-determinism. When an outcome deviation can be attributed to the test runner, driver, device, or infrastructure rather than to the SUT, that attribution is recorded separately in the run manifest notes. The attribution rule — the criteria under which a deviation is assigned to tooling rather than to the SUT, and how attributed deviations are reported alongside the raw rates — is DEFERRED-BEFORE-CAMPAIGN to the campaign configuration of E04 and E05 (protocol/study-design-v1.md, section 13, issue (xix)); exclusion and attribution rules are locked at campaign start under protocol/change-control-v1.md, section 7. Until that rule is fixed, every deviation counts in the raw rates regardless of suspected cause, and the suspected cause is a note only.
- Mobile runner qualification. Whether Mobilewright passes MQ1–MQ3 is decided under protocol/mobile-runner-policy-v1.md, not here. Mobile conditions are executed only with a runner permitted by that policy.
- Cross-platform parity and cross-layer continuity are measured in campaigns E06 and E07 under their own documents, not through the metrics in this document.
- Between-ecosystem comparison of conditions. A condition is defined per ecosystem. When conditions are compared between ecosystems, the comparison is made on a canonical scenario with a frozen mapping record under protocol/equivalent-scenario-mapping-v1.md and is classified CONFIRMATORY or EXPLORATORY under protocol/statistical-analysis-plan-v1.md, section 4.
- Manual and exploratory testing are not repeatable conditions under this document and do not contribute to these metrics.

## 7. Statement of current status

No repetitions have been executed. No attempt exists. No TSRR, CEOR, E2E-ROR, or Outcome Entropy value exists for any ecosystem, any modality, or any condition. No condition has yet been defined. This document specifies intent only.

## 8. Versioning

This is protocol version v1. Section 4 was rewritten during the second pre-freeze hardening iteration of 2026-09-16, replacing the candidate Repeatability Rate / Exact Outcome Rate pair with TSRR, CEOR, and E2E-ROR, resolving protocol/study-design-v1.md, section 13, issue (xi), while the document was DRAFT (protocol/change-control-v1.md, section 2, DRAFT -> DRAFT). The Section 5 heading was renamed from "Execution rules (candidate — to be frozen)" to "Execution Rules — v1" during the protocol v1 pre-data freeze of 2026-09-16: the eight execution rules were already fully specified and governed by no OPEN or DEFERRED issue, so the heading's "candidate" status was stale; no rule's substance changed. Changes after freeze create protocol/repeatability-determinism-v2.md per protocol/change-control-v1.md.
