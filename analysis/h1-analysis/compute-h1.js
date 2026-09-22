#!/usr/bin/env node
'use strict';
/*
 * analysis/h1-analysis/compute-h1.js
 *
 * Frozen confirmatory H1 analysis for study EUS-2026-001, campaign E01-capability-audit.
 *
 * Implements exactly the H1 procedure frozen in protocol/statistical-analysis-plan-v1.md, section 4.3:
 *   "Number of modalities at CONFIRMED Score 3 per ecosystem (count from the adjudicated matrix; Score 0
 *   cells remain in the matrix; a cell with confirmation_state = UNCONFIRMED_SCORE_3 is excluded from this
 *   count -- protocol/capability-rubric-v1.md, 'Score 3 confirmation'; protocol/study-design-v1.md, section
 *   13, issue (x); equivalently, a cell whose confirmed_score is not 3 is excluded, whatever its
 *   provisional_score -- protocol/capability-rubric-v1.md, 'Tie-break rule for undecidable adjacent
 *   scores')." Ecosystem pairs: SUT-01 vs SUT-02, SUT-01 vs SUT-03 (protocol/statistical-analysis-plan-v1.md,
 *   section 4.2/4.3; protocol/study-design-v1.md, section 6, note (c): "General-purpose baselines" = SUT-02,
 *   SUT-03 only). Method: "Descriptive count comparison only; no test is applied to rubric scores." No
 *   satisfaction/support criterion is frozen for H1 (contrast H3); none is computed or emitted here.
 *
 * SAP-to-matrix field mapping (not a new rule; already-approved chain, cited explicitly):
 *   The SAP's "confirmed_score" is, for a CONFIRMED cell, the auditor's confirmed_score (confirmed_score_as_
 *   stored when non-null, else provisional_score by the rubric's own stated fallback -- PROTO-U04
 *   downstream_consumption_semantics, rule 5); for a DISPUTED-then-ruled cell, PROTO-U04
 *   downstream_consumption_semantics rule 4 substitutes the human ruling's effective score "in place of the
 *   auditor's confirmed_score." The matrix's effective_confirmed_score field (schemas/adjudicated-matrix.
 *   schema.v2.json) is exactly this already-substituted value for every cell. This script therefore counts
 *   effective_confirmed_score === 3, NOT confirmed_score_as_stored === 3: after PROTO-U06,
 *   confirmed_score_as_stored is null on 20 cells (including every SUT-02 cell) whose effective score is
 *   well-defined and, in several cases, exactly 3 -- confirmed_score_as_stored is literal auditor-row
 *   provenance only and is never a count input (protocol/unresolved.md, PROTO-U06).
 *
 * Fails loudly on: matrix SHA-256 mismatch; any cell with confirmation_state = UNCONFIRMED_SCORE_3 (no
 * count-exclusion branch is implemented for it because none is observed in this dataset -- see PROTO-U06's
 * own treatment of UNSUPPORTED for the same fail-loud-rather-than-guess principle); missing SUT-01/02/03
 * cells; any modality count other than 9 per ecosystem.
 *
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only (fs, path,
 * crypto) -- no package manager, no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

const REPO_ROOT = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();

const MATRIX_PATH = 'derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json';
const EXPECTED_MATRIX_SHA256 = '88a062ebac5af2a659c8396d70b36137c8a8d4d9c30569a325b742f98ccbe589';
const EXPECTED_MATRIX_COMMIT = '0722773b9090163b5c882fc5a5c9f748db1b0d19';

const GENERAL_PURPOSE_BASELINES = ['SUT-02', 'SUT-03'];
const OMNIPIZZA = 'SUT-01';

function fail(msg) {
  console.error('FAIL: ' + msg);
  process.exit(1);
}

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function main() {
  const matrixBuf = fs.readFileSync(path.join(REPO_ROOT, MATRIX_PATH));
  const matrixHash = sha256(matrixBuf);
  if (matrixHash !== EXPECTED_MATRIX_SHA256) {
    fail(`matrix SHA-256 mismatch. expected ${EXPECTED_MATRIX_SHA256} got ${matrixHash}`);
  }

  const matrix = JSON.parse(matrixBuf.toString('utf8'));
  const cells = matrix.cells;
  if (!Array.isArray(cells) || cells.length !== 54) fail(`expected 54 cells, got ${cells.length}`);

  const populationSuts = [OMNIPIZZA, ...GENERAL_PURPOSE_BASELINES];
  const perSut = {};

  for (const sutId of populationSuts) {
    const sutCells = cells.filter((c) => c.ecosystem_id === sutId);
    if (sutCells.length !== 9) fail(`${sutId}: expected 9 modality cells, got ${sutCells.length}`);

    const unconfirmedScore3 = sutCells.filter((c) => c.confirmation_state === 'UNCONFIRMED_SCORE_3');
    if (unconfirmedScore3.length > 0) {
      fail(`${sutId}: confirmation_state = UNCONFIRMED_SCORE_3 observed on ${unconfirmedScore3.length} cell(s) -- no exclusion branch implemented for this case (none was expected; do not guess the derivation)`);
    }

    const score3Cells = sutCells
      .filter((c) => c.effective_confirmed_score === 3)
      .map((c) => ({ modality: c.modality, resolution_source: c.resolution_source, resolution_source_id: c.resolution_source_id }))
      .sort((a, b) => a.modality.localeCompare(b.modality));

    const allCells = sutCells
      .map((c) => ({ modality: c.modality, effective_confirmed_score: c.effective_confirmed_score }))
      .sort((a, b) => a.modality.localeCompare(b.modality));

    perSut[sutId] = {
      n_modalities: sutCells.length,
      count_confirmed_score_3: score3Cells.length,
      confirmed_score_3_modalities: score3Cells,
      all_modality_scores: allCells,
    };
  }

  const omnipizzaCount = perSut[OMNIPIZZA].count_confirmed_score_3;
  const comparisons = GENERAL_PURPOSE_BASELINES.map((baseline) => ({
    comparison_id: `H1 (${OMNIPIZZA} vs ${baseline})`,
    classification: 'CONFIRMATORY (H1)',
    omnipizza_count: omnipizzaCount,
    baseline: baseline,
    baseline_count: perSut[baseline].count_confirmed_score_3,
    omnipizza_count_greater_than_baseline: omnipizzaCount > perSut[baseline].count_confirmed_score_3,
  }));

  const result = {
    study_id: 'EUS-2026-001',
    hypothesis_id: 'H1',
    frozen_hypothesis_text_verbatim: 'H1: OmniPizza will expose a greater number of testing modalities at the experimentally controllable level than the general-purpose baselines. (protocol/study-design-v1.md, section 6)',
    campaign_id: 'E01-capability-audit',
    matrix: {
      path: MATRIX_PATH,
      sha256: EXPECTED_MATRIX_SHA256,
      commit: EXPECTED_MATRIX_COMMIT,
    },
    included_suts: populationSuts,
    ecosystem_pairs: comparisons.map((c) => `${OMNIPIZZA} vs ${c.baseline}`),
    excluded_suts: {
      specialists_not_in_confirmatory_comparison: ['SUT-04', 'SUT-05', 'SUT-06'],
      reason: 'protocol/study-design-v1.md, section 6, notes (a) and (d): H1 makes no prediction about specialist baselines; they are not part of the SUT-01-vs-general-purpose-baseline confirmatory comparison set unless explicitly pre-registered as CONFIRMATORY in the campaign configuration, which experiments/E01-capability-audit/README.md does not do for H1.',
    },
    variable_definition: 'Number of modalities at CONFIRMED Score 3 per ecosystem (protocol/statistical-analysis-plan-v1.md, section 4.3), operationalized as matrix cells with effective_confirmed_score === 3 (see this script\'s header comment for the confirmed_score -> effective_confirmed_score mapping and its citation).',
    method: 'Descriptive count comparison only; no test is applied to rubric scores (protocol/statistical-analysis-plan-v1.md, section 4.3). No confidence interval, p-value, or effect size is computed: ordinal capability scores are reported as descriptive frequency tables only (section 3).',
    counts: perSut,
    comparisons,
    support_determination: null,
    support_determination_note: 'Not computed: protocol/statistical-analysis-plan-v1.md defines no support/non-support satisfaction criterion for H1 (contrast H3, section 4.3, which has an explicit CEOR=1.00/H(Y)=0 criterion). Only the descriptive counts and directional comparison above are reported.',
    limitations: [
      `${OMNIPIZZA}'s count of ${omnipizzaCount} includes one cell (Visual Testing) resolved via human ruling E01-HR-01 rather than auditor confirmation_state = CONFIRMED (confirmation_state is null for this cell; protocol/capability-rubric-v1.md, "Relation to Score 3 confirmation"). This script counts it per PROTO-U04 downstream_consumption_semantics rule 4 (manifests/e01-proto-u04-correction.yaml): a human ruling on a DISPUTED cell supplies the effective score "in place of the auditor's confirmed_score." Under a stricter, unfrozen reading that required confirmation_state = CONFIRMED specifically (excluding every human-ruling-sourced cell regardless of its effective score), SUT-01's count would be 8 rather than 9. The directional comparisons above are unchanged under either reading (8 or 9, both > 6 and > 4).`,
      'Descriptive count comparison only (protocol/statistical-analysis-plan-v1.md, section 4.3): no confidence interval, effect size, or significance test is computed or applicable to ordinal rubric scores, and no support/non-support satisfaction criterion is frozen for H1.',
      'The study has 6 ecosystems total, a disclosed small-N design limitation at the study level (protocol/statistical-analysis-plan-v1.md, section 4.1); H1 itself compares only 3 of the 6 (SUT-01 and the two general-purpose baselines, SUT-02 and SUT-03). The three specialist ecosystems (SUT-04, SUT-05, SUT-06) are outside H1\'s confirmatory comparison and are not counted here.',
    ],
  };

  const outDir = path.join(REPO_ROOT, 'derived-data/h1-analysis');
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, 'H1-result.json');
  fs.writeFileSync(outPath, JSON.stringify(result, null, 2) + '\n');

  console.log('OK: wrote ' + outPath);
  console.log('counts:', JSON.stringify(Object.fromEntries(populationSuts.map((s) => [s, perSut[s].count_confirmed_score_3]))));
  console.log('comparisons:', JSON.stringify(comparisons.map((c) => `${c.comparison_id}: ${c.omnipizza_count} vs ${c.baseline_count} -> greater=${c.omnipizza_count_greater_than_baseline}`)));
  console.log('result file sha256: ' + sha256(fs.readFileSync(outPath)));
}

main();
