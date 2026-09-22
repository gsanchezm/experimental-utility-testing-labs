# analysis/ — Transformation and Analysis Scripts

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). Protocol v1/v2 FROZEN-PRE-DATA (protocol/change-control-v1.md). This directory holds the scripts that transform raw-data/ into derived-data/, the scripts that analyze derived data, and the outputs of those analyses, for every campaign and system under test (SUT).

## Purpose and rules

1. **Contents:** transformation scripts (raw -> derived), analysis scripts (derived -> tables, figures, statistical outputs), and their outputs.
2. **Reproducible end-to-end from raw-data/.** Running the scripts in this directory against raw-data/ must regenerate every file in derived-data/ and every output here with no manual step. A manual step is either replaced by a script or recorded as a correction record (raw-data/README.md).
3. **Language and tooling: TBD before freeze.** No package manager, runtime, or dependency has been introduced. When one is chosen, it is recorded in manifests/toolchain-manifest.yaml with exact versions before the first script runs. No framework abstraction beyond what the analysis needs.
4. **Follows protocol/statistical-analysis-plan-v1.md.** The plan, not this README, defines which analyses are primary, which are exploratory, and how each is reported.
5. **Outputs never replace raw evidence.** Analysis outputs are written here or to derived-data/, never to raw-data/ (AGENT-INSTRUCTIONS.md rules 6–8).
6. **Per-dimension profiles only, never a composite score.** Outputs report each of the six Experimental Utility dimensions separately per ecosystem. No script may compute, and no output may contain, a single weighted or aggregated utility score, index, ranking formula, or overall winner.
7. **Score 0 cells stay visible.** No script drops, reweights, filters, or converts to N/A a capability cell because of its structural_scope_note; the note is carried through to the output next to the score. Counts of "modalities per level" use each cell's `confirmed_score` where it is recorded, otherwise `provisional_score` (which `confirmed_score` equals whenever the tie-break rule was not invoked, the ordinary case), and include Score 0 cells in the denominator (protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores"). Where `confirmed_score` differs from `provisional_score` (the tie-break rule capped the recorded level), both are carried through to the output, never only the higher one. A Score 3 cell's `confirmation_state` (CONFIRMED or UNCONFIRMED_SCORE_3) is likewise carried through to the output next to the score and is never dropped; only a CONFIRMED Score 3 cell (equivalently, `confirmed_score = 3`, or `provisional_score = 3` with no recorded `confirmed_score`) enters a confirmed Score 3 count or comparison, including H1 (protocol/capability-rubric-v1.md, "Score 3 confirmation"; protocol/statistical-analysis-plan-v1.md, section 4.3).
8. **Evidence layers are never summed.** The E01 capability level of a modality and any later campaign observation about it (E12 for Localization / i18n in particular) are output in separate tables and never added, averaged, or counted twice (protocol/study-design-v1.md, section 9).
9. **Comparisons are labeled.** Every between-ecosystem comparison output carries its classification, CONFIRMATORY (H<n>), CONFIRMATORY (<pre-registered comparison id>), or EXPLORATORY, taken from the campaign configuration; a script never derives the classification from the data (protocol/statistical-analysis-plan-v1.md, section 4).
10. **NOT_COMPARABLE and no-data cells are reported with their reason.** NOT_COMPARABLE (protocol/equivalent-scenario-mapping-v1.md), NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE, and "no ground-truth condition available" are never coerced to zero or dropped; they appear as "no data" with the reason.
11. **Evidence is referenced by evidence_id.** Any output that cites E01 evidence cites evidence_id values, never CSV row or line numbers.
12. Manual and exploratory testing observations may be summarized descriptively but do not enter the quantitative primary comparison (protocol/study-design-v1.md).

## Layout

Internal layout: TBD before freeze. Candidate — not frozen: scripts and generated outputs are kept in separate subdirectories, and every generated output names the derived inputs and script version that produced it.

## Current status

- Two deterministic scripts exist, both for the FROZEN E01 campaign: `analysis/e01-adjudicated-matrix/generate-matrix.js` (adjudicated 54-cell matrix; PROTO-U05/U06) and `analysis/h1-analysis/compute-h1.js` (H1 descriptive count comparison; protocol/statistical-analysis-plan-v1.md, section 4.3). Runtime: Node.js v23.6.1 (manifests/toolchain-manifest.yaml, `scripting_runtime`).
- No statistical test has been performed (H1 is descriptive only by design); H2–H5 are not analyzed; no E02–E12 dataset exists. No script reads provisioning or environment-verification records, which are not experimental data.
