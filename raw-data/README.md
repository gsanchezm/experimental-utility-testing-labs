# raw-data/ — Raw Experimental Observations

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). Protocol v1/v2 FROZEN-PRE-DATA (protocol/change-control-v1.md). This directory holds the primary, unprocessed observations produced by experimental campaigns against each system under test (SUT). Only MEASURED_EXPERIMENT observations are ever written here; provisioning, environment-verification, qualification, smoke, dry-run, and development outputs never are (see "Measured versus non-measured" below).

## Rules

1. **Raw experimental data is append-only after campaign freeze.** Once a campaign is frozen, nothing already present may be modified, renamed, moved, or deleted; a further run may be appended only with a recorded reason in the change log (protocol/change-control-v1.md, section 7).
2. **Do not manually edit raw observations.** A raw file is written once by the run that produced it and is never touched again, not even to fix a typo.
3. **Corrections require a new derived dataset or an explicit correction record.** The original raw file stays untouched; the correction lives in derived-data/ (see "Correction records" below).
4. **Every raw record must be attributable to campaign/run provenance.** A raw file that cannot be linked to a campaign id, a SUT id, and a run manifest (with its environment_type) is not evidence and must not be used.
5. **Generated analysis must never replace raw evidence.** Outputs of analysis/ are derived products; they are stored in derived-data/ or analysis/, never here, and never overwrite a raw file.

These rules apply AGENT-INSTRUCTIONS.md rules 6–9 to this directory; AGENT-INSTRUCTIONS.md governs in case of conflict.

## Layout convention (candidate — not frozen)

```text
raw-data/
└── <campaign-id>/                e.g. E04-repeatability
    └── <sut-id>/                 e.g. SUT-04
        └── <run-id>/             one directory per run
            ├── run-manifest.json provenance, per schemas/run-manifest.schema.json
            └── ...               raw outputs of that run (logs, captures, tool reports, timings)
```

- `<campaign-id>` is one of the twelve campaign directory names in manifests/study-manifest.yaml (E01-capability-audit through E12-localization-i18n).
- `<sut-id>` is SUT-01 through SUT-06 as defined in manifests/sut-manifest.yaml.
- `<run-id>` format: unique within the campaign and equal to the `run_id` in the run manifest. **Candidate convention for E03-resetability (not frozen; locked only by E03's campaign-start "Campaign configuration" record):** `<condition_id>__<execution_id>__A<attempt>`, for example `E03-CS001-SUT01-API__EX0001__A1`, which encodes the hierarchy campaign → SUT → scenario → condition → execution → attempt in a flat directory name (the schema requires the run directory to sit directly under `<sut-id>/`). Under this convention the E03 tree reads `raw-data/E03-resetability/<sut-id>/<condition_id>__<execution_id>__A<attempt>/` (experiments/E03-resetability/ci-cd-execution-model.md, section 5).
- Every run is accompanied by a run manifest conforming to the schema version its campaign configuration names: schemas/run-manifest.schema.json (v1) or schemas/run-manifest.schema.v2.json (v2; future E02 and E03 runs, schemas/README.md). A run without a manifest is not attributable (rule 4). For E02/E03 runs, every entry of the manifest's `actions` list carries `outcome` (SUCCESS, PARTIAL_SUCCESS, FAILURE — protocol/setup-effort-v2.md, section 5, rule 9), recorded separately from the action count; a retry is a further action record with `is_retry` true, never a change to an earlier action's outcome.
- E01 is an audit, not an execution campaign: its execution verification records and artifacts live in audits/<SUT>/verifications/ and audits/<SUT>/artifacts/ (protocol/evidence-rules-v1.md), not here. raw-data/E01-capability-audit/ is not expected to be used.
- Provisioning records (protocol/setup-effort-v1.md, section 8) are NOT stored here. Frozen by explicit human decision, 2026-09-16: they are stored at manifests/provisioning/<sut-id>/<provisioning_id>.yaml (manifests/provisioning/README.md), authored by the ORCHESTRATOR, because they are configuration and reproducibility metadata rather than raw experimental observations. They are descriptive and never enter Required Actions. E01 execution verifications need no provisioning record (the verification record carries the instance provenance).
- The layout is frozen together with the protocol (protocol/change-control-v1.md). Changing it after the first campaign freeze requires a new protocol version.

## Measured versus non-measured (E03-resetability and later)

- **Immutable attempts.** Attempt 1 of an execution is never overwritten; a retry is a new attempt directory with `A<attempt+1>`. Every attempt keeps its run manifest, stdout, stderr, structured logs, Required Action records with per-action outcomes, pre-reset, reset, and post-reset evidence, API evidence, screenshots, browser and mobile logs, environment metadata, GitHub Actions metadata, exit status, timestamps, and the commit, configuration, and mapping hashes it ran under (the artifact package of experiments/E03-resetability/ci-cd-execution-model.md, section 5).
- **GitHub run provenance.** An E03 MEASURED_EXPERIMENT attempt is produced only by the frozen GitHub Actions workflow `.github/workflows/e03-measured-execution.yml` (AGENT-INSTRUCTIONS.md, "E03 CI/CD infrastructure"); the attempt bundle carries `ci-provenance.json` (repository SHA, canonical source commit in export mode, workflow revision, frozen-input hashes, runner image, GitHub run id / run attempt / job, condition, execution, and attempt ids) and `runtime-environment.json`. The workflow never commits: the ORCHESTRATOR imports the bundle here unchanged, with hash verification and an `import-record.yaml` naming the GitHub run id, run attempt, and artifact id (ci-cd-execution-model.md, section 7).
- **Separation.** PROVISIONING and ENVIRONMENT_VERIFICATION records live under `manifests/provisioning/` and `experiments/E03-resetability/environment-verification/`; QUALIFICATION records live under `qualification/`; SMOKE, DRY_RUN, DEVELOPMENT, and SYNTAX_VALIDATION outputs are not study records at all. None of them is written here, whatever produced them. Every record states its `record_class`; only `MEASURED_EXPERIMENT` belongs in this directory.

## Correction records

A correction never alters a raw file. A correction record contains:

| Field | Content |
|---|---|
| date | date the correction was recorded (YYYY-MM-DD) |
| affected run ids | the run ids (with campaign id and SUT id) the correction applies to |
| reason | why the raw value is considered wrong (for example clock skew, tool crash mid-run, mislabeled SUT) |
| corrected values | live in derived-data/, in a derived dataset that names this correction record as an input |
| original | untouched; the raw file paths remain exactly as written |

Storage location of correction records: TBD before freeze (candidate: derived-data/corrections/). This directory never contains a correction.

## Current status

- No raw data exists yet. No execution campaign has started: E01-capability-audit is FROZEN (an audit; its records live under audits/ and derived-data/, not here); E02–E12 are NOT_STARTED, including E03-resetability, which is in human-authorized PRE-START preparation (non-measured provisioning and environment verification completed 2026-09-22 for the CS-001 conditions; recorded outside this directory). No run manifest has been written.
- This directory is tracked by git and never ignored: .gitignore re-includes raw-data/** after its noise patterns, so tool output copied here with provenance is committed.
