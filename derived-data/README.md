# derived-data/ — Reproducible Transformations of Raw Data

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). Protocol v1/v2 FROZEN-PRE-DATA (protocol/change-control-v1.md). This directory holds datasets derived from raw-data/ for each campaign and system under test (SUT).

## Rules

1. **Derived datasets are reproducible transformations of raw data.** Every file here can be regenerated from raw-data/ by running the named transformation script. A file that cannot be regenerated that way is not a derived dataset and does not belong here.
2. **Transformation scripts must be version controlled** and live in analysis/ (analysis/README.md). A dataset produced by an unversioned or ad-hoc step is invalid.
3. **Every derived dataset must identify its source campaign and raw inputs.** Each dataset carries a provenance header (a leading comment block, for formats that allow one) or a sidecar file `<dataset>.provenance.yaml` listing:
   - raw input paths, relative to the repository root, under raw-data/
   - campaign id(s) and SUT id(s) covered
   - transformation script path (under analysis/) and its version identifier
   - date generated (YYYY-MM-DD)
   - protocol version the inputs were collected under
   - correction records applied, if any (raw-data/README.md, "Correction records")
4. Derived data never replaces raw evidence (AGENT-INSTRUCTIONS.md rules 6–8). Regenerating a derived dataset overwrites only the derived file; raw inputs are untouched.
5. Derived datasets are per-dimension. No file here may contain a composite, weighted, or aggregated Experimental Utility score, index, or ranking (protocol/statistical-analysis-plan-v1.md).

## Layout (candidate — not frozen)

- derived-data/<campaign-id>/... — datasets derived from the corresponding raw-data/<campaign-id>/ tree.
- derived-data/adjudication/ — output of ADJUDICATOR-EU-01 (protocol/agent-governance-v1.md); created when adjudication starts, not before.
- derived-data/corrections/ — candidate location for correction records (raw-data/README.md).

Exact layout: TBD before freeze.

## Current status

- E01 derived data exists and is closed to ordinary modification (E01 campaign FROZEN 2026-09-18): `derived-data/adjudication/<SUT>/adjudication.json` (six first-run ADJUDICATOR-EU-01 outputs), `derived-data/adjudication-rulings/E01-HR-01.json` and `E01-HR-02.json` (human rulings), `derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json` (sha256 88a062ebac5af2a659c8396d70b36137c8a8d4d9c30569a325b742f98ccbe589) with its provenance sidecar, and `derived-data/h1-analysis/H1-result.json` (sha256 8684deefc09faa4ba209546c4223f0cd1ec969de0a4d091bb92e3b6dbf137be5) with its sidecar. Transformation scripts live in analysis/. No E02–E12 derived data exists.
- Tracked by git; .gitignore re-includes derived-data/** after its noise patterns.
