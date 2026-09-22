#!/usr/bin/env node
'use strict';
/*
 * analysis/e01-adjudicated-matrix/generate-matrix.js
 *
 * PROTO-U05 (protocol/unresolved.md) deterministic transformation script, corrected by PROTO-U06
 * (representation/provenance only -- protocol/unresolved.md). Produces
 * derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json, validated against
 * schemas/adjudicated-matrix.schema.v2.json, from, and only from:
 *   1. the six immutable auditor result commits (git objects; SHAs below, cross-verified against
 *      experiments/E01-capability-audit/adjudication-input-view.yaml, committed 8ac2a2dd);
 *   2. the six immutable ADJUDICATOR-EU-01 first-run outputs
 *      (derived-data/adjudication/<SUT>/adjudication.json, committed d6939dea);
 *   3. the two human-ruling records (derived-data/adjudication-rulings/E01-HR-01.json, E01-HR-02.json,
 *      committed 1270bc1c);
 *   4. frozen confirmed_score / tie-break semantics (protocol/capability-rubric-v1.md).
 *
 * Implements only the precedence rule already defined by PROTO-U04
 * (manifests/e01-proto-u04-correction.yaml, downstream_consumption_semantics). Makes no scientific
 * decision. Fails loudly and exits non-zero on any missing, duplicate, or unresolved cell, on any
 * source-hash mismatch, or on any value outside the frozen vocabularies.
 *
 * PROTO-U06 correction: v1 of this script substituted provisional_score for a blank audit.md
 * confirmed_score cell at parse time and stored that substituted value in confirmed_score_as_stored,
 * losing the fact that the source cell was blank (observed, by direct inspection of the immutable
 * auditor commits: all 9 SUT-02 cells, all 9 SUT-06 cells, and the SUT-03 Android Native / iOS Native
 * cells). This version preserves the literal blank as null in confirmed_score_as_stored and performs
 * the already-frozen provisional_score fallback only when computing effective_confirmed_score, which
 * is scientifically unchanged from v1 for all 54 cells.
 *
 * Runtime: Node.js (manifests/toolchain-manifest.yaml, scripting_runtime). Standard library only
 * (fs, path, crypto, child_process) -- no package manager, no third-party dependency.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

const REPO_ROOT = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();

// Hardcoded, not derived at run time: this is the actual UTC calendar date this script was authored
// and first run, matching the convention used by derived-data/adjudication-rulings/E01-HR-0{1,2}.json.
const GENERATED_AT = '2026-09-18';

const CANONICAL_MODALITIES = [
  'Web UI Functional', 'API', 'Android Native', 'iOS Native', 'Performance',
  'Accessibility — Web only', 'Visual Testing', 'Security Testing', 'Localization / i18n',
];

const SUTS = {
  'SUT-01': { commit: 'fa807da45c3210e4659c231a7326890ed0a5dbb8', dir: 'SUT-01-omnipizza',
    adjudication_sha256: '989e728ad7fba848d655aa1722cc01ec910953f91d3f2a78ff1992f1d03f5981' },
  'SUT-02': { commit: 'bdef52b12bbdad3ca1746c0f4c74f0d9ca248226', dir: 'SUT-02-saucelabs',
    adjudication_sha256: '3785205d7090c7c66395be1ad7db719f59da8f2912327b7d066fb6f5ca49bd9b' },
  'SUT-03': { commit: 'f04fe3fc5e25b2c9f4660b2e425a3eba08382986', dir: 'SUT-03-browserstack',
    adjudication_sha256: '054de3bd2338c85a3d9f63975d4594d151a1e0a1a4311903fa4de5934c445a1d' },
  'SUT-04': { commit: '97ecae19151e8232f9992ee12f0944ce3120dbbb', dir: 'SUT-04-restful-booker',
    adjudication_sha256: '70083fce6db33fb5ec1b6bfce65fe4565471c72d060c12a66154b32d49b2b897' },
  'SUT-05': { commit: '57a82d43307eeb8f4ab5ba413cacd97ddd25297a', dir: 'SUT-05-juice-shop',
    adjudication_sha256: 'd838675ae2293314b26ef7f9e841d115df85afc7e0a4025f48fefaec8f58d1a6' },
  'SUT-06': { commit: '2bb26399f82f4bc1841d712b50fe8c1679dacd36', dir: 'SUT-06-webdriverio',
    adjudication_sha256: '43d5380c1092bae59057d340783d827207713c5ec0b3a522fb3ce5748159bfc2' },
};

const HUMAN_RULING_FILES = [
  'derived-data/adjudication-rulings/E01-HR-01.json',
  'derived-data/adjudication-rulings/E01-HR-02.json',
];

function fail(msg) {
  console.error('FAIL: ' + msg);
  process.exit(1);
}

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function gitShow(ref) {
  return execFileSync('git', ['show', ref], { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
}

// --- Parse the "## 3. Modality assessments" markdown table by header column name, not position. ---
function parseAuditTable(mdText, sutId) {
  const lines = mdText.split('\n');
  const start = lines.findIndex((l) => /^##\s*3\./.test(l));
  if (start === -1) fail(`${sutId}: could not find "## 3." section in audit.md`);

  const tableLines = [];
  for (let i = start; i < lines.length; i++) {
    if (/^\|/.test(lines[i])) {
      tableLines.push(lines[i]);
      if (tableLines.length >= 11) break; // header + separator + 9 modality rows
    } else if (tableLines.length > 0) {
      break;
    }
  }
  if (tableLines.length !== 11) {
    fail(`${sutId}: expected 11 modality-table lines (header+separator+9 rows), found ${tableLines.length}`);
  }

  const splitRow = (line) => line.split('|').slice(1, -1).map((s) => s.trim());
  const header = splitRow(tableLines[0]);
  const colIndex = (name) => {
    const idx = header.indexOf(name);
    if (idx === -1) fail(`${sutId}: audit.md modality table missing column "${name}"`);
    return idx;
  };
  const iModality = colIndex('modality');
  const iProvisional = colIndex('provisional_score');
  const iConfirmed = colIndex('confirmed_score');
  const iConfState = colIndex('confirmation_state');
  const iScopeNote = colIndex('structural_scope_note');

  const parseScore = (raw, modality, colName) => {
    if (!/^[0-3]$/.test(raw)) {
      fail(`${sutId}/${modality}: ${colName} is not a clean 0-3 integer literal: "${raw}"`);
    }
    return parseInt(raw, 10);
  };

  const byModality = {};
  const dataRows = tableLines.slice(2); // skip header + markdown separator row
  for (const line of dataRows) {
    const cells = splitRow(line);
    if (cells.length !== header.length) {
      fail(`${sutId}: table row has ${cells.length} columns, expected ${header.length}: ${line}`);
    }
    const modality = cells[iModality];
    if (byModality[modality]) fail(`${sutId}: duplicate modality row "${modality}" in audit.md`);

    const provisional_score = parseScore(cells[iProvisional], modality, 'provisional_score');
    // protocol/capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores": confirmed_score
    // and provisional_score coincide whenever no tie-break ambiguity exists; confirmed_score is recorded
    // as a distinct value only when the tie-break rule caps it below provisional_score. Some auditors
    // (e.g. SUT-02, SUT-06, and two SUT-03 cells) leave the confirmed_score cell blank in that ordinary
    // case rather than repeating the value. PROTO-U06 (protocol/unresolved.md): confirmed_score_as_stored
    // preserves that blank as null -- it is the literal audit.md cell, not a derived value. The
    // provisional_score fallback (analysis/README.md rule 7: "confirmed_score where it is recorded,
    // otherwise provisional_score") is applied separately, only when computing effective_confirmed_score
    // below, so the fact that a given row's confirmed_score was left blank is never lost. Any non-blank
    // cell must still be a clean 0-3 integer literal.
    const confirmed_score_as_stored = cells[iConfirmed] === '' ? null : parseScore(cells[iConfirmed], modality, 'confirmed_score');

    let confirmation_state = cells[iConfState];
    if (confirmation_state === 'null' || confirmation_state === '') confirmation_state = null;
    if (confirmation_state !== null && confirmation_state !== 'CONFIRMED' && confirmation_state !== 'UNCONFIRMED_SCORE_3') {
      fail(`${sutId}/${modality}: unrecognized confirmation_state "${confirmation_state}"`);
    }

    let structural_scope_note = cells[iScopeNote];
    if (structural_scope_note === '') structural_scope_note = null;

    byModality[modality] = { provisional_score, confirmed_score_as_stored, confirmation_state, structural_scope_note };
  }

  for (const m of CANONICAL_MODALITIES) {
    if (!byModality[m]) fail(`${sutId}: audit.md modality table missing canonical modality "${m}"`);
  }
  if (Object.keys(byModality).length !== 9) {
    fail(`${sutId}: audit.md modality table has ${Object.keys(byModality).length} modalities, expected 9`);
  }
  return byModality;
}

function loadHumanRulings() {
  const list = HUMAN_RULING_FILES.map((relPath) => {
    const abs = path.join(REPO_ROOT, relPath);
    const buf = fs.readFileSync(abs);
    const hash = sha256(buf);
    const ruling = JSON.parse(buf.toString('utf8'));
    if (ruling.decision_authority !== 'HUMAN') fail(`${relPath}: decision_authority is not HUMAN`);
    if (ruling.original_adjudicator_outcome !== 'DISPUTED') {
      fail(`${relPath}: original_adjudicator_outcome is not DISPUTED`);
    }
    return {
      ruling_id: ruling.ruling_id,
      ecosystem_id: ruling.ecosystem_id,
      modality: ruling.modality,
      effective_confirmed_score: ruling.human_effective_confirmed_score,
      path: relPath,
      sha256: hash,
    };
  });
  const byKey = {};
  for (const r of list) {
    const key = r.ecosystem_id + '::' + r.modality;
    if (byKey[key]) fail(`duplicate human ruling for ${key}`);
    byKey[key] = r;
  }
  return { list, byKey };
}

function main() {
  const rulings = loadHumanRulings();
  const usedRulingKeys = new Set();
  const cells = [];
  const sourcesAuditorCommits = {};
  const sourcesAdjudicationFiles = {};
  const outcomeTally = { CONFIRMED: 0, DISPUTED: 0, UNSUPPORTED: 0 };

  for (const sutId of Object.keys(SUTS)) {
    const meta = SUTS[sutId];
    sourcesAuditorCommits[sutId] = meta.commit;

    const adjPath = `derived-data/adjudication/${sutId}/adjudication.json`;
    const adjBuf = fs.readFileSync(path.join(REPO_ROOT, adjPath));
    const adjHash = sha256(adjBuf);
    if (adjHash !== meta.adjudication_sha256) {
      fail(`${sutId}: adjudication.json SHA-256 mismatch. expected ${meta.adjudication_sha256} got ${adjHash}`);
    }
    sourcesAdjudicationFiles[sutId] = { path: adjPath, sha256: adjHash };

    const adjudication = JSON.parse(adjBuf.toString('utf8'));
    if (adjudication.ecosystem_id !== sutId) fail(`${sutId}: adjudication.json ecosystem_id mismatch`);

    const outcomesByModality = {};
    for (const co of adjudication.cell_outcomes) {
      if (outcomesByModality[co.modality]) fail(`${sutId}: duplicate cell_outcome for modality "${co.modality}"`);
      outcomesByModality[co.modality] = co;
    }
    for (const m of CANONICAL_MODALITIES) {
      if (!outcomesByModality[m]) fail(`${sutId}: adjudication.json missing canonical modality "${m}"`);
    }
    if (Object.keys(outcomesByModality).length !== 9) {
      fail(`${sutId}: adjudication.json has ${Object.keys(outcomesByModality).length} cell_outcomes, expected 9`);
    }

    const ref = `${meta.commit}:audits/${meta.dir}/audit.md`;
    const auditByModality = parseAuditTable(gitShow(ref), sutId);

    for (const modality of CANONICAL_MODALITIES) {
      const outcome = outcomesByModality[modality];
      const auditRow = auditByModality[modality];
      outcomeTally[outcome.outcome] = (outcomeTally[outcome.outcome] || 0) + 1;

      let effective_confirmed_score;
      let resolution_source;
      let resolution_source_id;

      if (outcome.outcome === 'CONFIRMED') {
        // Already-frozen fallback (protocol/capability-rubric-v1.md; analysis/README.md rule 7):
        // effective_confirmed_score is the literal confirmed_score when the auditor recorded one,
        // otherwise provisional_score. confirmed_score_as_stored itself stays null in that case
        // (PROTO-U06) -- the fallback is applied here, not baked into the stored field.
        effective_confirmed_score = auditRow.confirmed_score_as_stored !== null ? auditRow.confirmed_score_as_stored : auditRow.provisional_score;
        resolution_source = 'AUDITOR_ADJUDICATION';
        resolution_source_id = meta.commit;
      } else if (outcome.outcome === 'DISPUTED') {
        const key = sutId + '::' + modality;
        const hr = rulings.byKey[key];
        if (!hr) fail(`${sutId}/${modality}: DISPUTED with no matching human-ruling record -- unresolved cell`);
        usedRulingKeys.add(key);
        effective_confirmed_score = hr.effective_confirmed_score;
        resolution_source = 'HUMAN_RULING';
        resolution_source_id = hr.ruling_id;
      } else {
        // schemas/adjudicated-matrix.schema.v2.json (PROTO-U06) permits UNSUPPORTED in
        // original_adjudicator_outcome as part of the frozen source vocabulary, but defines no
        // effective-score precedence rule for it; this remains a hard stop, not a schema-version gap.
        fail(`${sutId}/${modality}: outcome "${outcome.outcome}" has no defined effective-score derivation rule`);
      }

      if (!Number.isInteger(effective_confirmed_score) || effective_confirmed_score < 0 || effective_confirmed_score > 3) {
        fail(`${sutId}/${modality}: effective_confirmed_score out of range: ${effective_confirmed_score}`);
      }

      cells.push({
        ecosystem_id: sutId,
        modality,
        effective_confirmed_score,
        confirmed_score_as_stored: auditRow.confirmed_score_as_stored,
        provisional_score: auditRow.provisional_score,
        confirmation_state: auditRow.confirmation_state,
        structural_scope_note: auditRow.structural_scope_note,
        original_adjudicator_outcome: outcome.outcome,
        evidence_ids: outcome.evidence_ids,
        resolution_source,
        resolution_source_id,
      });
    }
  }

  // --- Global validation ---
  if (cells.length !== 54) fail(`expected 54 cells, got ${cells.length}`);
  const seen = new Set();
  for (const c of cells) {
    const key = c.ecosystem_id + '::' + c.modality;
    if (seen.has(key)) fail(`duplicate cell ${key}`);
    seen.add(key);
  }
  if (Object.keys(SUTS).length !== 6) fail('expected 6 ecosystems');

  const humanRulingCells = cells.filter((c) => c.resolution_source === 'HUMAN_RULING');
  if (humanRulingCells.length !== 2) fail(`expected exactly 2 HUMAN_RULING cells, got ${humanRulingCells.length}`);
  for (const key of Object.keys(rulings.byKey)) {
    if (!usedRulingKeys.has(key)) fail(`human ruling for ${key} was never applied to any cell (orphaned ruling)`);
  }

  const sut01Visual = cells.find((c) => c.ecosystem_id === 'SUT-01' && c.modality === 'Visual Testing');
  if (!sut01Visual || sut01Visual.resolution_source !== 'HUMAN_RULING' || sut01Visual.effective_confirmed_score !== 3) {
    fail('SUT-01 Visual Testing does not match the expected human ruling (HUMAN_RULING, effective_confirmed_score=3)');
  }
  const sut04Security = cells.find((c) => c.ecosystem_id === 'SUT-04' && c.modality === 'Security Testing');
  if (!sut04Security || sut04Security.resolution_source !== 'HUMAN_RULING' || sut04Security.effective_confirmed_score !== 2) {
    fail('SUT-04 Security Testing does not match the expected human ruling (HUMAN_RULING, effective_confirmed_score=2)');
  }
  for (const c of cells) {
    const isOneOfTheTwo =
      (c.ecosystem_id === 'SUT-01' && c.modality === 'Visual Testing') ||
      (c.ecosystem_id === 'SUT-04' && c.modality === 'Security Testing');
    if (c.resolution_source === 'HUMAN_RULING' && !isOneOfTheTwo) {
      fail(`unexpected HUMAN_RULING-sourced cell outside the two authorized rulings: ${c.ecosystem_id}/${c.modality}`);
    }
  }

  const matrix = {
    study_id: 'EUS-2026-001',
    campaign_id: 'E01-capability-audit',
    generated_at: GENERATED_AT,
    sources: {
      auditor_result_commits: sourcesAuditorCommits,
      adjudication_first_run: sourcesAdjudicationFiles,
      human_rulings: Object.fromEntries(
        rulings.list.map((r) => [r.ruling_id, { path: r.path, sha256: r.sha256, ecosystem_id: r.ecosystem_id, modality: r.modality }])
      ),
    },
    cells,
  };

  const outDir = path.join(REPO_ROOT, 'derived-data/e01-adjudicated-matrix');
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, 'E01-adjudicated-matrix.json');
  fs.writeFileSync(outPath, JSON.stringify(matrix, null, 2) + '\n');

  const bySut = {};
  const byScore = { 0: 0, 1: 0, 2: 0, 3: 0 };
  for (const c of cells) {
    bySut[c.ecosystem_id] = (bySut[c.ecosystem_id] || 0) + 1;
    byScore[c.effective_confirmed_score]++;
  }

  console.log('OK: wrote ' + outPath);
  console.log('outcome tally (from first-run adjudication.json): ' + JSON.stringify(outcomeTally));
  console.log('cells: ' + cells.length);
  console.log('cells by SUT: ' + JSON.stringify(bySut));
  console.log('cells by effective_confirmed_score: ' + JSON.stringify(byScore));
  console.log('human-ruling-sourced cells: ' + humanRulingCells.length);
  console.log('matrix file sha256: ' + sha256(fs.readFileSync(outPath)));
}

main();
