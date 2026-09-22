# E01 — Pre-Adjudication Integrity Review

Operational record, not a protocol document. Written by ORCHESTRATOR / INTEGRITY REVIEWER, 2026-09-17T10:50:29Z, after the six independent E01 audits completed. Every count below was recomputed directly from the six committed auditor branches (via `git show <sha>:<path>`), not taken from any prior orchestration report. Structured, machine-readable duplicate: `manifests/e01-pre-adjudication-snapshot-v1.yaml`.

## 1. Git integrity

| auditor_id | branch | expected_commit | actual_commit | parent == 82b7a26 | worktree clean | changed_files_valid |
|---|---|---|---|---|---|---|
| AUDITOR-SUT01-OMNIPIZZA | audit/e01-sut01-omnipizza | fa807da4...5dbb8 | match | yes (sole parent) | yes | yes — only its own 5 files |
| AUDITOR-SUT02-SAUCELABS | audit/e01-sut02-saucelabs | bdef52b1...8226 | match | yes (sole parent) | yes | yes — only its own 5 files |
| AUDITOR-SUT03-BROWSERSTACK | audit/e01-sut03-browserstack | f04fe3fc...2986 | match | yes (sole parent) | yes | yes — only its own 5 files |
| AUDITOR-SUT04-RESTFULBOOKER | audit/e01-sut04-restful-booker | 97ecae19...0dbbb | match | yes (sole parent) | yes | yes — only its own 5 files |
| AUDITOR-SUT05-JUICESHOP | audit/e01-sut05-juice-shop | 57a82d43...5297a | match | yes (sole parent) | yes | yes — only its own 5 files |
| AUDITOR-SUT06-WEBDRIVERIO | audit/e01-sut06-webdriverio | 2bb26399...dacd36 | match | yes (sole parent) | yes | yes — only its own 5 files |

Main (`experimental-utility-testing-labs`) remains exactly at START commit `89b23f2787c7717f357b8031a798389c2b9ca335`, clean, and does not contain any of the six auditor commits (verified with `git merge-base --is-ancestor`). Each of the six commits' sole parent is `82b7a26ba9d03aa860adf4a3b102c79d815cce89`. Each commit's `git show --stat` shows exactly `README.md, audit.md, evidence.csv, limitations.md, unresolved.md` under its own `audits/SUT-0N-.../`, and nothing else — no other SUT directory, `protocol/`, `prompts/frozen/`, any `manifests/*.yaml`, or campaign configuration file appears in any of the six diffs.

## 2. Evidence counts (recomputed with Python's `csv` module against each committed CSV, not a line-count approximation)

| SUT | DOCUMENTED | SOURCE_VERIFIED | EXECUTION_VERIFIED | INFERRED | TOTAL |
|---|---|---|---|---|---|
| SUT-01 | 8 | 22 | 0 | 0 | 30 |
| SUT-02 | 0 | 21 | 0 | 0 | 21 |
| SUT-03 | 2 | 30 | 0 | 0 | 32 |
| SUT-04 | 8 | 23 | 0 | 0 | 31 |
| SUT-05 | 4 | 25 | 0 | 0 | 29 |
| SUT-06 | 7 | 22 | 0 | 0 | 29 |
| **Total** | **29** | **143** | **0** | **0** | **172** |

**Grand total: 172 data rows** (header excluded), confirmed two independent ways: `csv.DictReader` row count and `wc -l` minus 1 per file. **The prior orchestration report's "163 evidence rows total" was a plain arithmetic error** — 30+21+32+31+29+29 = 172, and no alternative counting rule (excluding a row class, deduplicating, etc.) was found that produces 163. There is no missing-row explanation; the figure was simply wrong and is corrected here. All six CSVs parse cleanly as CSV, match the frozen 13-field header exactly, every `evidence_status` token is one of the four allowed values (no unexpected token found), every row populates all six schema-required fields (`evidence_id, ecosystem_id, modality, evidence_type, mechanism, evidence_status` — `schemas/evidence.schema.json`), no `evidence_id` is duplicated within any SUT, and **no `evidence_id` collides across SUTs** (172 distinct IDs, zero collisions). Every `ecosystem_id` value in every file is exactly and only that file's own SUT id.

## 3. Score structure (mechanical only — no score adjudicated or changed)

54 scored cells (6 SUTs × 9 modalities). Every `provisional_score`/`confirmed_score` value found is within the frozen 0–3 range; no malformed score token exists anywhere.

**Provisional/confirmed divergence — resolves the prior report's contradiction.** The prior report simultaneously listed a SUT-01 Visual Testing divergence (3→2) *and* called SUT-04 Security Testing (3→2) "the one cell across all six audits where provisional and confirmed scores actually diverge" — those two statements contradict each other. The actual, recomputed count is **2 divergent cells**, not 1 and not 0:

| SUT | modality | provisional_score | confirmed_score | confirmation_state |
|---|---|---|---|---|
| SUT-01 | Visual Testing | 3 | 2 | null (tie-break; step 3 itself undecided) |
| SUT-04 | Security Testing | 3 | 2 | null (tie-break; step 3 itself undecided) |

**Confirmed Score 3 cells: 26**, all mechanically compliant (every one has at least one `SOURCE_VERIFIED` evidence reference; none rests on `DOCUMENTED` or `INFERRED` alone). Full compliance table in the snapshot YAML (`score3_compliance`). Per SUT: SUT-01=8, SUT-02=6, SUT-03=4, SUT-04=2, SUT-05=4, SUT-06=2.

**Data-quality flag (not a divergence, not adjudicated here): SUT-02 and SUT-06 left the `confirmed_score` table column blank on every one of their 9 rows**, including rows where `confirmation_state = CONFIRMED` (which, per the frozen prompt's own "Score 3 handling" section, is definitionally only used when `confirmed_score = 3`). Every other audit (SUT-01, 03, 04, 05) populates `confirmed_score` on every row, mirroring `provisional_score` except at a tie-break. Because the field is literally blank, a strict mechanical read cannot compute "provisional != confirmed" for SUT-02/06's rows at all (blank is neither equal nor unequal to a score); the 26-cell Score-3 count above and its compliance check use `confirmation_state = CONFIRMED` as the (unambiguous, per the frozen prompt's own vocabulary) fallback for these two SUTs' 6 and 2 cells respectively. This is flagged for a data-hygiene correction, not resolved or adjudicated here, and is not evidence of contamination.

## 4. Completeness

All six SUTs: all nine required modalities present exactly once (no missing, no duplicate modality rows in the table); `README.md`, `audit.md`, `evidence.csv`, `limitations.md`, `unresolved.md` all present and non-empty; `audit.md` section 4 "Cross-cutting properties" and a contradictions-related section both present in every audit. Every Score-0 cell across the study carries a populated `structural_scope_note` **except one**: SUT-06's Localization/i18n cell (`provisional_score = 0`) has an empty `structural_scope_note` token, with an explicit auditor rationale in the same row ("This is a plain capability absence, not a missing-surface-type reason, so no `structural_scope_note` token applies"). This is a reasoned interpretive position, not a data-entry omission — whether the schema's "Score 0 cells... structural_scope_note" language requires a token for every Score-0 cell or only for structurally-absent surfaces is an open interpretive question, flagged for adjudicator/ORCHESTRATOR decision, not resolved here.

## 5. Provenance

No genuine repository/commit mismatch found in any of the 172 rows against the pinned provenance in `manifests/sut-manifest.yaml` (3 apparent mismatches in SUT-02 were a false positive of the review script's exact-match logic against rows that legitimately cite multiple pinned repositories in one semicolon-separated field — each individual repository cited is itself correctly pinned).

**SUT-02 iOS and SUT-06 android/ios annotated-tag observations — independently re-verified, not just taken from the auditors' self-reports**, by inspecting the auditors' own read-only source clones directly (`git cat-file -t`, `git rev-parse ...^{commit}`):
- SUT-02 iOS pin `031358f56903742103a02d086f8af76735bb31a7` (`manifests/sut-manifest.yaml`) is confirmed to be a git **tag** object; it dereferences deterministically to commit `ede6fa4b7f57a75bc31f626b6ca531339e83d5c0`, matching exactly what AUDITOR-SUT02-SAUCELABS reported.
- SUT-06 android/ios pin `470b89ec09afac8b28d32cb8ea953071fb7e138a` is likewise confirmed a **tag** object; it dereferences deterministically to commit `4770f471177fecfe2b4e01f4cffee65aaa663060`, matching exactly what AUDITOR-SUT06-WEBDRIVERIO reported.

In both cases the auditor examined source at the correctly-dereferenced commit; no version substitution occurred and no evidence provenance is actually ambiguous. This is a `manifests/sut-manifest.yaml` field-naming imprecision (labeling a tag object id as `commit_sha`) — flagged for the ORCHESTRATOR, not corrected here (this operation does not modify manifests).

## 6. Independence — both incidents investigated from the actual subagent transcripts, not the prior summary

**Incident 1 — SUT-05 wrong-target write.** Exact timeline reconstructed from the SUT-05 and SUT-03 auditors' full tool-call transcripts from the launch workflow (internal harness transcript identifiers withheld in this public snapshot):
- 09:16:38.379Z — SUT-05 writes its own `gen_evidence.py` to the shared session scratchpad path.
- 09:16:53.586Z — SUT-03 writes *its own* `gen_evidence.py` to the *same* shared path, overwriting SUT-05's copy on disk.
- 09:17:18.805Z — SUT-05 invokes `python3 gen_evidence.py`; by this point the file on disk is SUT-03's script.
- 09:17:40.307Z — SUT-03, independently and deliberately, runs its own script.
- 09:17:46.675Z — SUT-05's invocation (from 09:17:18) completes: "wrote 32 evidence records to .../e01-sut03-browserstack/audits/SUT-03-browserstack/evidence.csv" — SUT-03's own script, executed via SUT-05's shell due to the race, correctly targeting SUT-03's own real path with SUT-03's own real content.
- 09:17:52.906Z — SUT-03's own explicit run (started 09:17:40) completes, independently reproducing the identical 32-row result, which SUT-03 verified itself (row count, status counts, sequential IDs) and later revisited (09:25:58–09:26:41) with an edit and a second independent re-run, again reproducing the same content.

Facts established: the *content* of SUT-03's evidence.csv was 100% authored by SUT-03's own agent (it wrote the Python source encoding its own BrowserStack findings — modality names, mechanisms, `evidence_id`s, citations to specific source files it had read); SUT-05 never authored, edited, or chose any part of it. SUT-03's own explicit, deliberate re-run independently reproduces the exact same committed content, so the final result does not depend on the accidental execution at all. SUT-05 recognized the anomaly, did not touch, read further, or revert the SUT-03 path (correct per the write-boundary rule), reported it factually in its own `unresolved.md`, and switched its remaining work to direct-Write-plus-read-back verification. Independently re-verified by this review: SUT-05's own worktree copy of `audits/SUT-03-browserstack/evidence.csv` is currently clean and header-only (never persisted a change there); the real SUT-03 worktree's evidence.csv is intact, 32 rows, `ecosystem_id` purely `SUT-03`; SUT-05's own final committed `audit.md`/`evidence.csv` contain zero mentions of BrowserStack or SUT-03. **Independence is established for both SUT-03 and SUT-05** with respect to this incident: it was an execution-attribution race on a shared scratchpad filename, not a content leak in either direction, and the underlying infrastructure bug is flagged separately as a workflow/tooling issue.

**Incident 2 — SUT-01 scratchpad collision.** Exact timeline reconstructed from SUT-01's full harness transcript (internal identifier withheld in this public snapshot), including the raw `edited_text_file` attachment the harness surfaced to it:
- SUT-01 wrote and ran its own `gen_evidence.py` (09:15:48–09:16:09), producing its own `evidence.csv` (30 rows, all `SUT-01`) *before* any collision.
- An `edited_text_file` system attachment then informed SUT-01 that its scratchpad script file had been externally modified, and **included a partial snippet of the new content**: a script clearly authored by AUDITOR-SUT03-BROWSERSTACK (its real pinned repository URL and commit SHA, and the beginning of one evidence row — modality "Web UI Functional", score 3, a source-verified mechanism description about deterministic test accounts). This is genuine fragmentary SUT-03 content, not merely a filename, and it did appear in SUT-01's context via this automatic notification — this review does not minimize that fact.
- SUT-01's own text response at that point states it did not read the content intentionally, and it immediately re-verified its own `evidence.csv` (30 rows, `ecosystem_id` set `{SUT-01}` only, sequential IDs 0001–0030) — confirmed unchanged.
- SUT-01's `audit.md` (containing the modality scores and narrative) was written **after** this exposure, not before.

Facts established, independently re-verified by this review (not merely asserted): SUT-01's evidence.csv — where every modality score actually originates — was complete before the exposure. SUT-01's final committed `audit.md` and `evidence.csv` contain zero mentions of BrowserStack, SUT-03, or any other SUT (checked by direct grep of the committed content). The exposed snippet was about a structurally unrelated ecosystem (a different tech stack, different modality-3 mechanism) with no plausible transfer path into OmniPizza-specific findings. Given this, **independence is established for SUT-01's actual scored content**, but this review does not describe the incident as "harmless" outright: a fragment of another auditor's real content was present in SUT-01's context after its scores were fixed but before its narrative was drafted, and while no trace of it appears anywhere in the committed output, the exposure itself is a genuine, non-hypothetical event that an adjudicator should be aware of, not a purely git-clean non-event.

**Root cause (both incidents):** a session-wide scratchpad directory with a fixed, non-unique filename (`gen_evidence.py`) shared across all six concurrently-running auditor subagents in the same Workflow run — a workflow/tooling isolation gap, not a scientific-process failure by any auditor. Reported as product feedback separately.

## 7. Known scientific flags (carried forward, not resolved or adjudicated)

- SUT-01 Visual Testing: `provisional_score=3` -> `confirmed_score=2` (tie-break; step 3 undecided).
- SUT-04 Security Testing: `provisional_score=3` -> `confirmed_score=2` (tie-break; plaintext password storage verified but not documented as an intentional vulnerability).
- SUT-06 Android/iOS Native Score 3: rests on the auditor's considered-but-contestable reading of a "Clear (test hook)" UI control as a dedicated experimental hook rather than incidental end-user UI (auditor's own flag, SUT-06-U05).
- SUT-03 documentation-vs-implementation contradiction: 8 documented "API Metric Control Endpoints" always return 401 because no route populates the session store their gate depends on; excluded from the Performance score.
- SUT-02/SUT-06 blank `confirmed_score` table column (section 3 above) — data-hygiene flag.
- SUT-06 Localization/i18n missing `structural_scope_note` with a stated rationale (section 4 above) — interpretive flag.
- SUT-02 iOS / SUT-06 android-ios `commit_sha` fields are tag-object ids, not raw commit SHAs (section 5 above) — manifest field-naming flag, no evidentiary ambiguity.
- Both independence incidents (section 6) — infrastructure flag, independence established but exposure was real for SUT-01.
- All six auditors independently flagged the frozen prompt's own stale "Status: WORKING. Not yet frozen" header text as a known, already-logged (commit `637abe7`) inconsistency; none treated it as blocking.

## 8. Frozen integrity

Re-verified after all six audits: `prompts/frozen/e01-capability-auditor-v1.md` SHA-256 `b504b5f720a6fe8b2a7255b3fe0509d8d18a244fb8114b485c9a2e4fbfe6c358`, 17,057 bytes — unchanged. No file under `protocol/` (other than the append-only `protocol/CHANGELOG.md`, untouched by this review), `manifests/e01-source-provenance.yaml`, `manifests/sut-manifest.yaml`, or `experiments/E01-capability-audit/README.md` "Campaign configuration" was modified by any of the six auditor commits or by this review. No RQ, hypothesis, or rubric text changed.

## 9. Decision gate

**E01 PRE-ADJUDICATION INTEGRITY PASSED — auditor provenance, independence, and structural evidence integrity are established; adjudicator-prompt review may begin.**

Passing does not resolve any flag in section 7; all remain open for ADJUDICATOR-EU-01 / human review. No score was changed, no comparison was made, and no auditor branch was merged by this operation.
