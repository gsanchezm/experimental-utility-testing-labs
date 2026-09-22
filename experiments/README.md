# Experiments — Campaign Skeleton

| Field | Value |
|---|---|
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Protocol version | v1 |
| Repository phase | SETUP (initialization) |
| Created | 2026-09-15 |

## Purpose

This directory holds the twelve experimental campaigns of the study. Before the protocol reached FROZEN-PRE-DATA, each campaign directory contained only its `README.md` (candidate objective, related research question(s), candidate variables, and the evidence a run must produce). That constraint applied only pre-freeze: the protocol has been FROZEN-PRE-DATA since 2026-09-16 (see protocol/change-control-v1.md), and campaign directories now also hold the FROZEN, human-approved artifacts their own campaigns have produced — for example E01-capability-audit's locked "Campaign configuration" record, or E03-resetability's PRE-START preparation material (issue-xviii-analysis.md, canonical-scenario-catalogue.md, controlled-instance-determination.md, controlled-instance-status.yaml, environment-verification/, ci-cd-execution-model.md, campaign-configuration-draft.md — none of it a campaign-start artifact; E03 remains NOT_STARTED).

The unit of comparison in every campaign is the testing laboratory ecosystem (the system under test, SUT), not an individual repository. All six evaluated ecosystems are listed in manifests/sut-manifest.yaml and are treated under identical rules.

## Campaign map

| Campaign id | Name | Primary RQ | Dimension(s) informed | Status |
|---|---|---|---|---|
| E01 | Capability Audit | RQ1 Experimental Breadth; secondary RQ2 (descriptive: Observability and Automation Affordances) | 1 Experimental Breadth (primarily); 5 Observability and Automation Affordances (descriptive); feeds all dimensions | FROZEN (2026-09-18) |
| E02 | State Establishment | RQ2 Controllability, Observability, Automation Affordances, and Setup Effort | 2 Experimental Controllability; 6 Setup Effort | NOT STARTED |
| E03 | Resetability | RQ2 Controllability, Observability, Automation Affordances, and Setup Effort | 2 Experimental Controllability; 6 Setup Effort | NOT STARTED (human-selected for PRE-START preparation 2026-09-21; non-measured provisioning/environment verification and GitHub Actions infrastructure 2026-09-22; START not authorized) |
| E04 | Repeatability | RQ3 Repeatability and Determinism | 3 Repeatability and Determinism | NOT STARTED |
| E05 | Determinism | RQ3 Repeatability and Determinism | 3 Repeatability and Determinism | NOT STARTED |
| E06 | Cross-platform Parity | RQ4 Cross-platform and Cross-layer Integration | 4 Cross-platform and Cross-layer Integration | NOT STARTED |
| E07 | Cross-layer Continuity | RQ4 Cross-platform and Cross-layer Integration | 4 Cross-platform and Cross-layer Integration | NOT STARTED |
| E08 | Performance | RQ5 Controlled Non-functional Experimentation | 1 Experimental Breadth; 2 Experimental Controllability | NOT STARTED |
| E09 | Accessibility | RQ5 Controlled Non-functional Experimentation | 1 Experimental Breadth; 2 Experimental Controllability | NOT STARTED |
| E10 | Visual | RQ5 Controlled Non-functional Experimentation | 1 Experimental Breadth; 2 Experimental Controllability | NOT STARTED |
| E11 | Security | RQ5 Controlled Non-functional Experimentation | 1 Experimental Breadth; 2 Experimental Controllability | NOT STARTED |
| E12 | Localization / i18n | RQ1 Experimental Breadth (controllability of selected locale conditions); secondary RQ4 Cross-platform and Cross-layer Integration (locale parity) | 1 Experimental Breadth; 4 Cross-platform and Cross-layer Integration | NOT STARTED |

Dimension 5 (Observability and Automation Affordances) has no dedicated campaign; it is answered descriptively under RQ2 from the E01 cross-cutting property descriptions (protocol/cross-cutting-properties-v1.md) and informed cross-cuttingly by all campaigns. The E01 Localization / i18n capability level and the E12 observations are different evidence layers and are never summed or counted twice (protocol/study-design-v1.md, section 9).

Dimension names and order are defined in protocol/study-design-v1.md. Experimental Utility is a multidimensional profile; no campaign, and no combination of campaigns, produces a single aggregated utility score.

## Common rules for all campaigns

- Every run produces a run manifest conforming to schemas/run-manifest.schema.json, carrying `environment_type` (PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, OTHER; protocol/study-design-v1.md, section 10). E01 is an audit: its evidence records need a run manifest only for EXECUTION_VERIFIED evidence, in the form of an execution verification record (protocol/evidence-rules-v1.md).
- Environment control: conditions requiring deterministic reset, intentional fault activation, active security testing, significant load, or destructive or state-changing operations run on a controlled instance when an open-source deployment of the evaluated version is available, and never against a PUBLIC_HOSTED instance; where no controlled instance can be established, the condition is NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE and is reported as "no data" with reason (protocol/study-design-v1.md, section 10.3). This is an experimental-control decision, not a utility score.
- Campaign configuration: at campaign start the ORCHESTRATOR records, under a "Campaign configuration" heading in the campaign README, the frozen scenario mapping records, pinned SUT versions, toolchain versions, prompt version(s), conditions and their environment types, sample size, exclusion and attribution rules, and the list of CONFIRMATORY comparisons; these are locked for the campaign (protocol/change-control-v1.md, section 7).
- Scenario equivalence: every cross-ecosystem scenario used for inferential comparison in E02–E07 has a FROZEN mapping record under protocol/equivalent-scenario-mapping-v1.md before execution; equivalence is semantic, and an ecosystem without a defensible semantic equivalent is NOT_COMPARABLE for that scenario (not a score, not a zero).
- Comparison classification: between-ecosystem comparisons are CONFIRMATORY when pre-registered for H1, H2, H4, or H5 (SUT-01 versus SUT-02, SUT-01 versus SUT-03; H3 is a single-ecosystem prediction with no pair) or when explicitly pre-registered as CONFIRMATORY in the campaign configuration under protocol/statistical-analysis-plan-v1.md, section 4.2, rule 3; all other comparisons, including every specialist comparison not so pre-registered, are EXPLORATORY.
- Setup effort: one-time provisioning is recorded descriptively in a provisioning record; only per-run / per-condition setup enters Required Actions (protocol/setup-effort-v2.md, which supersedes v1). Verification counts as an action classified by its mechanism, and a partially successful action counts once with its outcome recorded separately in the run manifest's `actions[].outcome` (schemas/run-manifest.schema.v2.json).
- Raw observations are written to `raw-data/<campaign-id>/`. After campaign freeze (defined in protocol/change-control-v1.md, section 7), the raw data of that campaign is append-only.
- Derived results are written to `derived-data/`, separated from raw observations.
- Every campaign applies to all six ecosystems under identical rules wherever the relevant testing modality is in scope for that ecosystem. Cells that are not executed (Score 0 in E01, NOT_COMPARABLE, NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE, or no ground-truth condition available) are recorded as such with the reason, never skipped silently, and remain visible in every table (protocol/study-design-v1.md, section 11).
- Repetition targets follow protocol/repeatability-determinism-v1.md (N = 50 per repeatable condition when operationally feasible; N = 30 for expensive mobile conditions only with a justification recorded before that campaign executes).
- Analysis follows protocol/statistical-analysis-plan-v1.md.
- Tooling is not decided; candidates are listed in manifests/toolchain-manifest.yaml with all versions null. Mobile execution follows protocol/mobile-runner-policy-v1.md: the selected runner must have passed the qualification gate, and each mobile-capable ecosystem must have passed the per-SUT compatibility smoke, before it participates in E06, E07, or any other mobile campaign.
- Evidence produced by any campaign is classified per protocol/evidence-rules-v1.md.

## Global warning

NO campaign may execute before the protocol is FROZEN-PRE-DATA and an explicit instruction to execute has been given. Campaign READMEs are placeholders; their candidate variables are not frozen.

## Current state

No experiment (E02–E12) has been executed and no raw-data exists for any of them. E01-capability-audit is the sole exception: it is a completed, FROZEN audit (not a repeated-execution experiment), with its 54-cell adjudicated capability matrix and H1 confirmatory analysis committed under derived-data/ (protocol/change-control-v1.md, section 7; manifests/e01-campaign-freeze-v1.yaml). experiments/scenario-mappings/ now exists: CS-001.yaml (FROZEN; the sole accepted canonical scenario for the current E03 campaign version) and CS-002.yaml (FROZEN 2026-09-21, then EXCLUDED_FROM_CAMPAIGN 2026-09-22 by human ruling; preserved unchanged; not an input to any campaign — manifests/e03-cs002-exclusion-v1.yaml). Every E03 MEASURED_EXPERIMENT must run through `.github/workflows/e03-measured-execution.yml` (AGENT-INSTRUCTIONS.md, E03-CI-WRITE-AUTH-01); local executions never enter the measured dataset. No score, result, or ranking exists for any SUT beyond what E01/H1 already established; H2–H5 remain not analyzed.
