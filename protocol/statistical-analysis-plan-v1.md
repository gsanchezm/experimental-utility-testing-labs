# Statistical Analysis Plan

| Field | Value |
|---|---|
| Document | protocol/statistical-analysis-plan-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | first iteration instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT); second iteration (issues (x), (xi), (xx), explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT); final pre-freeze checklist closure (bootstrap policy, paired effect size, confirmed_score cross-reference, explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## 1. Purpose and principles

This document states the currently intended analysis for study EUS-2026-001. It describes how data that does not yet exist will be analyzed once the protocol is frozen and data collection begins. It performs no analysis.

Principles:

- Effect sizes are prioritized over significance-only reporting. A p-value without an accompanying point estimate, interval, and effect size is not a reportable result in this study.
- All analysis is reproducible from raw-data/ via version-controlled transformations. Derived tables live in derived-data/ and analysis outputs in analysis/; each is regenerable from raw-data/ by a recorded transformation. No number is reported that cannot be traced to raw-data/ or, for E01, to audits/.
- Experimental Utility is reported as a descriptive profile per dimension (the six dimensions listed in protocol/study-design-v1.md). There is no aggregate index, no weighted score, and no ranking of ecosystems across dimensions. None will be defined in a later version without a protocol amendment, and this plan does not anticipate one.
- Every evaluated testing laboratory ecosystem (each system under test, SUT, SUT-01 to SUT-06) is analyzed by the same procedures. No ecosystem receives a different analysis path, a different threshold, or a different reporting treatment. The CONFIRMATORY / EXPLORATORY classification of Section 4 changes only the inferential label and the multiplicity family of a comparison, never the estimation procedure, the threshold, or the reporting prominence.
- The interpretation rules of protocol/study-design-v1.md, section 11, bind every table, figure, and sentence produced under this plan.

## 2. Data types expected

| Data type | Examples | Source campaigns |
|---|---|---|
| Proportions | Target-State Reproduction Rate (TSRR); Conditional Exact Outcome Rate (CEOR); End-to-End Reproducible Outcome Rate (E2E-ROR) (protocol/repeatability-determinism-v1.md); detection rates for ground-truth conditions (for example, whether a seeded accessibility, visual, or security condition is detected); parity presence and continuity success proportions | E04, E05, E06, E07, E09, E10, E11 |
| Durations | Setup duration; reset duration; execution duration | E02, E03, E08, Setup Effort observations |
| Counts | Number of Required Actions to reach a target state (per-run / per-condition setup only, protocol/setup-effort-v1.md); number of modalities at each rubric level per ecosystem; number of controlled non-functional ground-truth conditions per ecosystem | E01, E02, E03, E08–E11 |
| Ordinal scores | Capability rubric score 0–3 per cell (ecosystem × modality), per protocol/capability-rubric-v1.md, with its `structural_scope_note` | E01 |
| Categorical outcomes | Outcome category per execution, used for Outcome Entropy (protocol/repeatability-determinism-v1.md); locale-condition outcomes (E12); "no ground-truth condition available" (E08–E11); comparability marker per scenario (protocol/equivalent-scenario-mapping-v1.md) | E04, E05, E08–E12 |
| Descriptive text | Cross-cutting property descriptions (Observability, Automation Affordances, and the other six properties), provisioning records | E01, E02, E03 |

Which specific variables are collected in each campaign is fixed in that campaign's configuration before it starts (protocol/change-control-v1.md, section 7); this table lists the types the plan is prepared to handle.

## 3. Planned methods

| Data type | Method | When it applies in this study |
|---|---|---|
| Proportions | Wilson 95% confidence interval | Per condition per ecosystem, for every reported rate (TSRR, CEOR, E2E-ROR, detection rate, parity or continuity proportion). No interval is computed for a condition where CEOR (or, correspondingly, H(Y)) is NOT_ESTIMABLE (protocol/repeatability-determinism-v1.md, section 4). |
| Proportions | Risk difference (with its 95% confidence interval) | Between two ecosystems on the same equivalent condition or scenario (protocol/equivalent-scenario-mapping-v1.md), when both have data on that condition. |
| Proportions | Fisher's exact test | For 2×2 detection tables (ecosystem A vs ecosystem B × detected vs not detected) on the same ground-truth condition, where cell counts are small enough that asymptotic tests are inappropriate. Reported alongside the risk difference, never alone. |
| Durations | Median and interquartile range (IQR) | For every duration variable per condition per ecosystem. Means are reported only as supplementary descriptives. |
| Durations | Bootstrap 95% confidence interval | For the median of every duration variable: BCa bootstrap, 10,000 resamples by default (frozen by explicit human decision, 2026-09-16). A campaign's statistical configuration may pre-register a different resample count with a written justification before that campaign's execution begins; absent such a pre-registration, the default applies. For paired measurements (for example a per-scenario difference between two ecosystems), the bootstrap resamples PAIRS together, never individual observations independently; for independent samples, resampling is within each group independently. The random seed used for each bootstrap is recorded in analysis/ alongside the result. Bootstrap is not used where the statistic or design makes it inappropriate merely to satisfy this default; any such exception is justified in the campaign's statistical configuration before analysis. |
| Counts (Required Actions) | Per-scenario counts with median and IQR across scenarios per ecosystem; paired per-scenario differences between two ecosystems | For H2 and every other between-ecosystem Required Actions comparison; each count refers to a canonical scenario mapped as COMPARABLE for both ecosystems. |
| Paired continuous or ordinal observations | Wilcoxon signed-rank test | For paired per-scenario observations across two ecosystems where the same canonical scenario set is COMPARABLE for both and the pairing is by canonical_scenario_id. Applied only when the design justifies pairing and the number of non-tied pairs is adequate; otherwise the comparison is reported descriptively. |
| Multiple comparisons | Holm correction | Across the family of CONFIRMATORY comparisons under one research question (Section 4). Exploratory comparisons form no confirmatory family; if any p-value is reported for an exploratory comparison it is labeled exploratory and uncorrected, and is never used to claim confirmation. |
| Ordinal scores | Descriptive frequency tables only | Rubric scores per cell are reported as counts per level and as the full cell table, including every Score 0 cell with its `structural_scope_note`. No test is applied to rubric scores; they are not treated as interval data. |
| Categorical outcomes | Outcome Entropy H(Y) | Per condition per ecosystem, as a secondary determinism measure per protocol/repeatability-determinism-v1.md. Reported with the category count. No test is applied to entropy values. |
| Descriptive text | Structured narrative, per ecosystem, per property | Observability and Automation Affordances (Dimension 5, RQ2 descriptive component) and the other cross-cutting properties are reported as descriptions citing evidence_ids. No score, weight, or metric is derived from them at protocol v1. |

Effect sizes:

- For proportions, the effect size is the risk difference. A risk ratio may be added as supplementary when the baseline proportion is small; whether it is added for a given comparison is decided and pre-registered in that campaign's configuration (protocol/change-control-v1.md, section 7) before the campaign begins — the same pattern as the bootstrap resample-count override above. Absent such a pre-registration, only the risk difference is reported.
- For paired ordinal or continuous comparisons where the Wilcoxon signed-rank test is used (Section 4.2, H2 and any other paired comparison), frozen by explicit human decision, 2026-09-16: the primary, interpretable effect estimate is the paired difference in the original measurement unit, summarized with its median and confidence interval; it is never replaced by a standardized effect size. The matched-pairs rank-biserial correlation is reported additionally as a standardized, nonparametric effect size, alongside the original-unit estimate, not instead of it. Where Wilcoxon is not the appropriate test for a paired comparison, the rank-biserial correlation is not mechanically reported. For capability rubric scores, no parametric effect size is invented; Ordinal scores in the table above remain descriptive frequency tables only.

Software and versions used for computation are recorded in analysis/ at the time of analysis; none are selected now.

## 4. Unit of analysis, pairing, and comparison classification

### 4.1 Unit of analysis

- Within an ecosystem, the inferential unit is the repetition within a condition. The N executions of one condition (N = 50, or N = 30 for justified mobile conditions, per protocol/repeatability-determinism-v1.md) are the observations from which that condition's rate and interval are computed. Conditions are not pooled across modalities to form a larger N.
- Between ecosystems, comparisons are made only on equivalent conditions or scenarios. Equivalence is semantic equivalence as defined in protocol/equivalent-scenario-mapping-v1.md: a canonical scenario with a frozen mapping record in which both ecosystems are marked COMPARABLE. A scenario marked NOT_COMPARABLE for an ecosystem is reported side by side with its reason but is never compared inferentially for that ecosystem; NOT_COMPARABLE is not a capability score and is not a zero.
- With six ecosystems, between-ecosystem inference is descriptive and interval-based rather than omnibus-test driven. No Kruskal–Wallis, ANOVA, or chi-square across all six ecosystems is planned. The small number of ecosystems is an accepted design limitation and is disclosed in every report.

### 4.2 Classification of between-ecosystem comparisons

Every between-ecosystem comparison is classified, before the associated campaign begins, as exactly one of:

| Class | Definition | Multiplicity treatment | Reporting label |
|---|---|---|---|
| CONFIRMATORY | A comparison that tests one of the pre-registered pairwise hypotheses H1, H2, H4, or H5 (protocol/study-design-v1.md, section 6): SUT-01 versus SUT-02, and SUT-01 versus SUT-03, on the equivalent conditions or scenarios and the variable named for that hypothesis in Section 4.3. H3 is a single-ecosystem prediction (Section 4.3) and defines no between-ecosystem comparison. Also CONFIRMATORY: a comparison explicitly pre-registered as such in the campaign configuration under rule 3 below (for example a specialist baseline as a positive control in its specialty), labeled with the pre-registered comparison id instead of an H<n>. Its exact specification (hypothesis, RQ, variable, ecosystem pair, canonical_scenario_id or condition ids, method, effect size) is recorded in the campaign configuration before the campaign starts (protocol/change-control-v1.md, section 7). | Holm-corrected within the family of confirmatory comparisons under the same RQ | "CONFIRMATORY (H<n>)" for a hypothesis comparison; "CONFIRMATORY (<pre-registered comparison id>)" for a comparison pre-registered under rule 3 |
| EXPLORATORY | Every other between-ecosystem comparison, including every comparison that involves a specialist baseline (SUT-04, SUT-05, SUT-06) and every comparison between two baselines, unless explicitly pre-registered as CONFIRMATORY in the campaign configuration under rule 3 below. | No confirmatory family; any p-value is labeled exploratory and uncorrected | "EXPLORATORY" |

Rules:

- H1, H2, H4, and H5 concern OmniPizza (SUT-01) versus the general-purpose baselines (SUT-02, SUT-03); H3 concerns SUT-01 alone (Section 4.3). Specialist ecosystems provide contextual / specialist reference comparisons: they remain in the study as positive-control / depth references in their specialty modality, a design role that states intent rather than a finding, and are reported in every table in which their modalities apply.
- No ecosystem pair is converted into a confirmatory hypothesis test merely because both have data. A comparison not listed as CONFIRMATORY in the campaign configuration before the campaign starts is EXPLORATORY, whatever its result.
- A specialist comparison may be pre-registered as CONFIRMATORY only by an explicit entry in the campaign configuration before the campaign starts (for example, a specialist baseline used as a positive control for a ground-truth detection condition in its specialty). Absent such an entry it is exploratory / contextual.
- The classification never removes an ecosystem from a campaign, a table, or a profile, and never changes how an ecosystem is audited, executed, estimated, or reported. Point estimate, interval, effect size, and N are reported for exploratory comparisons exactly as for confirmatory ones.
- Once a campaign has started, its comparison classification is locked with the campaign configuration; reclassification after seeing data is a protocol deviation and is reported as such.

### 4.3 Hypothesis-to-comparison mapping

The concrete scenario or condition ids are fixed in the campaign configuration before each campaign starts. The variable, method, and ecosystem pairs are fixed here.

| Hypothesis | RQ | Campaign(s) | Variable | Ecosystem pairs | Method |
|---|---|---|---|---|---|
| H1 | RQ1 | E01 | Number of modalities at CONFIRMED Score 3 per ecosystem (count from the adjudicated matrix; Score 0 cells remain in the matrix; a cell with `confirmation_state = UNCONFIRMED_SCORE_3` is excluded from this count — protocol/capability-rubric-v1.md, "Score 3 confirmation"; protocol/study-design-v1.md, section 13, issue (x); equivalently, a cell whose `confirmed_score` is not 3 is excluded, whatever its `provisional_score` — protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores") | SUT-01 vs SUT-02; SUT-01 vs SUT-03 | Descriptive count comparison only; no test is applied to rubric scores |
| H2 | RQ2 | E02, E03 | Required Actions (establish; reset) per COMPARABLE canonical scenario | SUT-01 vs SUT-02; SUT-01 vs SUT-03 | Paired per-scenario differences; Wilcoxon signed-rank where pairing is adequate, otherwise descriptive; effect size per Section 3 |
| H3 | RQ3 | E04, E05 | Conditional Exact Outcome Rate (CEOR) and Outcome Entropy H(Y) of conditions classified a priori as deterministic (protocol/repeatability-determinism-v1.md, sections 2 and 4); the H3 label attaches to SUT-01's conditions only | SUT-01 only (single-ecosystem prediction; no between-ecosystem pair) | Wilson interval for CEOR per condition (not computed when CEOR is NOT_ESTIMABLE), computed and reported identically for every ecosystem's a-priori-deterministic conditions; H3 is satisfied for a condition only when CEOR = 1.00 and H(Y) = 0 (protocol/study-design-v1.md, section 13, issue (xx), RESOLVED); TSRR and E2E-ROR are reported for the same conditions but are not the primary H3 criteria |
| H4 | RQ4 | E06, E07 | Parity presence proportion per canonical scenario (E06); continuity success proportion per layer pair (E07) | SUT-01 vs SUT-02; SUT-01 vs SUT-03 | Risk difference with interval; Fisher's exact test where applicable |
| H5 | RQ5 | E08, E09, E10, E11 | Number of controlled non-functional ground-truth conditions per ecosystem | SUT-01 vs SUT-02; SUT-01 vs SUT-03 | Descriptive count comparison; detection rates per condition are reported per Section 5 |

## 5. Reporting

For every comparison, the report states: point estimate, confidence interval, effect size, and N (per arm where applicable), and its classification (CONFIRMATORY (H<n>), CONFIRMATORY (<pre-registered comparison id>), or EXPLORATORY). A comparison missing any of these is not reported as a result.

- Negative and contradicting results are reported with the same prominence, in the same tables, and with the same level of detail as results consistent with any hypothesis in protocol/study-design-v1.md. A result that contradicts a hypothesis is not relegated to an appendix or a footnote.
- Results are presented as per-dimension profile tables: one table per dimension, rows per ecosystem, columns per modality or condition as appropriate. No table, figure, or sentence presents a composite across dimensions, computes an overall winner, or applies a weighting.
- The Experimental Breadth table (RQ1) shows the full E01 matrix. Every Score 0 cell is shown as 0 with its `structural_scope_note`; no cell is shown as N/A, hidden, or dropped. Every cell shows both `confirmed_score` and, where the tie-break rule caps it below the auditor's candidate level, `provisional_score` alongside it (protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores"); `confirmed_score` is never dropped or hidden. Counts of "modalities per level" (the frequency table by rubric level) are counts of `confirmed_score` where it is recorded, otherwise of `provisional_score`, which `confirmed_score` equals whenever the tie-break rule was not invoked (the ordinary case); the count is never of `provisional_score` when a distinct, lower `confirmed_score` is recorded. Counts include Score 0 cells in the denominator. A Score 3 cell shows its `confirmation_state` (CONFIRMED or UNCONFIRMED_SCORE_3) alongside the score; it stays visible in the matrix either way, but only a CONFIRMED Score 3 cell (equivalently, `confirmed_score = 3`) is included in any confirmed Score 3 count, table, or comparison, including H1 (protocol/capability-rubric-v1.md, "Score 3 confirmation"; protocol/study-design-v1.md, section 13, issue (x)).
- Experimental Breadth and Modality Depth are reported as different questions (protocol/study-design-v1.md, section 11): the breadth table reports levels per modality; depth results (E02–E12 and the cross-cutting property descriptions) are reported in their own dimension tables. A specialist ecosystem with low breadth and high depth in its specialty is reported as exactly that, in two tables, without reconciliation into a single figure.
- Localization / i18n is reported in two separate places that are never summed or counted twice: the E01 capability level in the Experimental Breadth table, and the E12 experimental observations in an E12 table under RQ1 (controllability of the locale condition) and RQ4 (cross-platform locale parity). No count of modalities per level uses E12 outcomes, and no E12 table restates the E01 level as a result.
- Where a cell has no data, the cell reports "no data" with the reason, not zero. Reasons include: modality rated Score 0 in E01 and therefore not executed in later campaigns; NOT_COMPARABLE scenario (protocol/equivalent-scenario-mapping-v1.md); NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE (protocol/study-design-v1.md, section 10.3); "no ground-truth condition available" (E08–E11).
- For E08–E11, an ecosystem for which no controllable ground-truth condition is available for a modality is reported twice, in separate places: as a recorded finding in the Experimental Breadth / Experimental Controllability tables (the E01 cell and the campaign's categorical outcome), and as "no data — no ground-truth condition available" in the RQ5 detection-rate comparison for that condition. It is never reported as a detection failure or as a detection rate of zero.
- Scenarios excluded from a comparison because they were NOT_COMPARABLE for an ecosystem are listed with the reason recorded in the mapping record.
- Every reported value cites the derived-data/ table and the transformation that produced it; E01 values cite the evidence_ids that support them.

## 6. Pre-specification

- This analysis plan is frozen before data collection begins. It was frozen 2026-09-16, approved by gilbertosanchez, per protocol/change-control-v1.md; no data may be collected under an unfrozen plan, and none has been collected under this one.
- Confirmatory comparisons are defined before the associated campaign begins, in the campaign configuration (Section 4.2). A confirmatory comparison cannot be added, removed, or re-specified after the campaign has started except as a recorded protocol deviation.
- Deviations from the frozen plan are recorded per protocol/change-control-v1.md: the deviation, its reason, when it was decided, and whether it was decided before or after seeing the affected data.
- Analyses not specified in the frozen version of this document are labeled exploratory in every table and figure in which they appear, and are reported separately from pre-specified analyses.
- Items marked "TBD before freeze" or "candidate — not frozen" in this document must be resolved and recorded before freeze, or explicitly deferred to a named campaign configuration with a written reason; they may not be resolved after data collection starts. As of the final pre-freeze checklist closure of 2026-09-16, the bootstrap variant and default resample count (Section 3) and the paired effect-size choice (Section 3) are resolved and frozen; whether a supplementary risk ratio is added alongside the risk difference (Section 3) is explicitly deferred to each campaign's configuration, decided before that campaign begins. Methodological issues that concerned this plan — (x), (xi), and (xx), protocol/study-design-v1.md, section 13 — were resolved in the second pre-freeze hardening iteration; issue (xix) (tooling-versus-SUT attribution for E04/E05) remains DEFERRED-BEFORE-CAMPAIGN to the configuration of those campaigns.

## 7. Statement of current status

No statistical test has been performed. No confidence interval, effect size, point estimate, or entropy value has been computed. No comparison has been classified for any campaign, because no campaign configuration exists. No data exists. raw-data/, derived-data/, and analysis/ contain no study data at initialization. This document specifies intent only.

## 8. Versioning

This is protocol version v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6). Sections 2–6 were updated during the second pre-freeze hardening iteration of 2026-09-16 to align with TSRR/CEOR/E2E-ROR (protocol/repeatability-determinism-v1.md) and Score 3 confirmation_state (protocol/capability-rubric-v1.md), resolving protocol/study-design-v1.md, section 13, issues (x), (xi), and (xx), while the document was DRAFT (protocol/change-control-v1.md, section 2, DRAFT -> DRAFT). Sections 3, 4.3, 5, and 6 were updated during the final pre-freeze checklist closure of 2026-09-16 (explicit human decision), while the document was still DRAFT (DRAFT -> DRAFT): the bootstrap policy (BCa, 10,000 resamples default, paired resampling, seed recording) and the paired effect-size policy (original-unit estimate primary, matched-pairs rank-biserial correlation additional) were frozen; the supplementary risk ratio was explicitly deferred to campaign configuration; the H1 count and the "modalities per level" frequency tables were cross-referenced to the general `confirmed_score` / `provisional_score` tie-break mechanism of protocol/capability-rubric-v1.md. This file is now immutable in place; any further change creates protocol/statistical-analysis-plan-v2.md per protocol/change-control-v1.md.
