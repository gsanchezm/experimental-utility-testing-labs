# Implementation notes: SUT-01 (OmniPizza) Android compatibility smoke, Appium 3 3.7.0 (DRAFT)

Status: DRAFT preparation only. Nothing here issues an authorization, locks a baseline, applies a patch, merges a workflow, dispatches a run, or executes anything. Nothing was installed, built, started, or run: no emulator, simulator, Appium server, npm install, workflow dispatch, or SUT-01 launch. The only executions were static: the gate script of the new workflow on fixture trees, the lint and syntax tools, the YAML parser, the expression-length estimate, and one pure JavaScript function of the harness that computes a hash without starting any runner. The SUT-01 APK was not downloaded; the public release record and the pinned source were read.

## 1. Source finding

At the pinned commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a (tag v1.1.8, a lightweight tag that resolves directly to that commit; the release digests equal the toolchain pins), the Android app's backend origin is a compile-time constant: `frontend-mobile/src/api/client.ts` line 27, `const API_ORIGIN = "https://omnipizza-backend.onrender.com";`, used as the axios `baseURL` (lines 29 to 32). No environment variable, `expo.extra` entry, settings screen, launch argument other than the country code, or deep-link parameter changes it, and a search of the whole mobile source tree (80 files, fetched at the pinned commit) found no second API origin. So the endpoint is fixed in the APK: a controlled backend on the runner would require a changed build or a changed network path, both excluded by protocol rule 3 without a human decision; the default is a hosted, read-only sign-in with PUBLIC_HOSTED and HOSTED_MAPPING_UNVERIFIED disclosed (HD-3).

Retrieval: GitHub API (tag reference, release record, git tree of the pinned commit) and raw files of the pinned commit, all read on 2026-11-06T02:23Z UTC (2026-11-05 local). Files: `frontend-mobile/src/api/client.ts`, `app.json`, `package.json`, `src/screens/LoginScreen.tsx`, `src/screens/CatalogScreen.tsx`, `src/components/PrimaryButton.tsx`, `src/components/MobileProductCard.tsx`, `src/utils/qa.ts`, `src/store/useAppStore.ts`, `App.tsx`, and the 80-file mobile source set.

## 2. Done (new files only; no existing file edited)

| Path | What it is |
|---|---|
| `qualification/compatibility-smoke-sut01/README.md` | status, scope and topology, source finding, the concrete realization (locked by hash), implementation table, empty smoke records |
| `qualification/compatibility-smoke-sut01/run-smoke-android.sh` | Android entry: emulator checks, clean start, pre-runner backend probe, harness run |
| `qualification/compatibility-smoke-sut01/smoke-common.sh` | SUT-01 pins, output namespace `formal/<id>/SUT-01-android`, build digest check, toolchain check, backend probe (`/health` must answer 200 before any runner contact), Appium start, stop records |
| `qualification/compatibility-smoke-sut01/harness/smoke.mjs` | generated from the SUT-02 harness: REALIZATION.android only (sign-in and catalogue arrival), presence-based state reads, SUT-01 identifiers |
| `qualification/compatibility-smoke-sut01/harness/wd.mjs`, `harness/package.json`, `harness/package-lock.json` | byte-identical copies of the SUT-02 shared files (the lock v4 versions) |
| `.github/workflows/e06-compatibility-smoke-sut01.yml` | DRAFT dispatch-only fail-closed workflow: gate job, then one Android job on ubuntu-24.04; no iOS job; inputs only through `env:` |
| `manifests/compatibility-smoke-implementation-lock-v5.draft.yaml` | successor implementation lock (draft; new scope; supersedes nothing); hashes by script |
| `manifests/sut01-compatibility-smoke-execution-auth-v4-prepared.draft.yaml` | APPIUM3-COMPAT-SMOKE-AUTH-04, PREPARED, NOT ISSUED, dispatch_eligibility NOT_ELIGIBLE_UNTIL_ISSUED, issued_by null, launch prompt null |
| `qualification/compatibility-smoke-sut01/patches/compatibility-smoke-status.draft.patch` | mirror entry SUT-01 android NOT_STARTED; NOT applied |
| `qualification/compatibility-smoke-sut01/tests/make_draft_records.py` | computes the lock hashes, writes the lock, the PREPARED record, and the patch |
| `qualification/compatibility-smoke-sut01/tests/run_gate_matrix.py`, `tests/OUTPUT-gate-matrix.txt` | gate matrix: the gate script extracted from the workflow, run on the as-is repository, on a must-pass fixture, and on one-change mutations |
| `qualification/compatibility-smoke-sut01/tests/run_static_checks.py`, `tests/OUTPUT-static-checks.txt` | YAML parse, actionlint 1.7.7 with shellcheck 0.10.0, shellcheck -x, bash -n, node --check, realization hash, length estimate, git status, hygiene |
| `qualification/compatibility-smoke-sut01/tests/length_estimate.py` | OP-CI-15 estimate, the formula of the validation workflow, over every workflow file |

Gate design. The readiness gate of the new workflow checks, in order: the confirmation token; policy v3 FROZEN-PRE-DATA with section 9, and v2 AMENDED; exactly one authorization record for the id, ISSUED, VALID, human-issued, ELIGIBLE, not yet dispatched, scoped to SUT-01 Android, one execution; the frozen launch prompt; the lock (every artifact hash recomputed, the concrete-realization hash, the harness REALIZATION hash through `realizationSha256()` imported by node, and the step-sequence hash); the SUT-01 and toolchain pins; the output namespace; the README has no SUT-01 row; the mirror entry is NOT_STARTED with no pointers; E06 is NOT_STARTED. The study-wide mobile-runner admissibility check is copied, verbatim, from the G-7 block of the measured-execution workflow (its lines 207 to 388, extracted by `make_workflow.py`, not re-typed): status SELECTED, the retained AUTH-02 FAIL_RUNNER exempt only through the verified lineage record, fallback state ADMISSIBLE. On the as-is repository those 14 study-wide gates pass, and the gate refuses on the SUT-01 gates only (`tests/OUTPUT-gate-matrix.txt`). The per-condition PASS check of G-7 is deliberately not copied: this smoke is the step that produces that PASS.

Realization (DRAFT, locked by hash when issued). Sign-in path on the emulator: accessibility id `screen-login` (MC-02, displayed), `Standard` (the standard_user quick-login pill, MC-04), `Sign In` (btn-login, MC-04), then `screen-catalog` displayed (MC-06, MC-08). Artifacts (MC-10): screenshot, page source, record, harness log, server log, environment files, the backend probe. Each source reference is a line of the pinned files (see the README table).

## 3. Not done

- No frozen launch prompt (owed at issuance; the gate requires `prompts/frozen/<prompt_version_id>.md`; the naming is a draft choice).
- No application of the mirror patch (owed at issuance).
- No issuance, no publication, no dispatch, no run, no record, no mirror transcription.
- No merge of the workflow into the tracked tree (HD-7).
- No change to any validation step (see section 5).
- No E06 configuration, no CS-007 freeze, no E06 G-7 copy, no E06 START (the scenario CS-007 is a DRAFT in the brief, and E06 has no configuration).
- No iOS smoke (HD-1), no iOS realization.
- No APK download, no APK manifest read, no backend call. The backend probe exists only in the smoke, which does not run.
- No canonical recomputation of the policy hash: lock v5 records the policy hash that lock v4 recorded as canonical and, separately, the hash of the worktree copy, which differs because this worktree is a public-export snapshot. The ORCHESTRATOR recomputes the canonical value on the canonical repository (owed).
- No refresh of the status dashboard, the export log, or `qualification/unresolved.md` (new open items: section 4).

## 4. Blocked

- On the source finding and the endpoint (HD-3): the default is a hosted read-only sign-in. A controlled backend is blocked by rule 3 unless a human decides otherwise.
- On the launch activity (HD-16): `frontend-mobile/android/` is not in the pinned tree, so no `appActivity` can be read from source. The realization keeps `TBD` in that row, and the gate refuses on the TBD check until resolved (that refusal is intended).
- On the CI grant (HD-7): neither E03-CI-WRITE-AUTH-01 nor CAMPAIGN-CI-WRITE-AUTH-01 names a compatibility smoke or this workflow. The file must not be merged until the human research lead confirms a grant that names it.
- On the lock and the authorization: the lock is a draft (`active_execution_baseline: false`), the record is PREPARED, and the frozen prompt and the mirror patch are owed at issuance. Issuance needs an explicit human instruction.
- On the public export: GitHub Actions evaluates only the public repository. The issued files must be exported UNCHANGED. The export run is not performed here (the human research lead approves and pushes; HD-14). The validation workflow's export manifest must list the new files.
- On the human dispatch: one dispatch, on a separate explicit instruction, after issuance and publication.
- On the first-run risk (not blocked but open): the realization is checked only statically. Whether Android exposes `Standard` and `Sign In` as content descriptions with the expected match count, whether the release APK installs and launches on API 35, and whether the hosted backend answers within the 90 s arrival window are not evidenced by any artifact. A FAIL_RUNNER of the first run would return the study to UNRESOLVED_AFTER_FALLBACK_FAILURE (policy 9.5, 9.7.11). There is no second remediation under policy v3.

Items of the existing repository that name the SUT-02-only smoke scope (to be checked at issuance; none is edited here):
- Must change at issuance: `manifests/compatibility-smoke-status.yaml` (apply the patch, which is a new entry only); `qualification/compatibility-smoke/README.md` (its "Current scope" line names SUT-02 only; SUT-01 rows belong in the SUT-01 folder, so only a pointer may be added).
- Live status that describes the mobile path and would need its own status update after issuance: `manifests/study-manifest.yaml`, `manifests/toolchain-manifest.yaml` (`compatibility_smoke_status` is a non-authoritative scalar that names SUT-02 only), `manifests/README.md`, `qualification/unresolved.md` (new open items), `prompts/README.md` (frozen prompt listing), the root README, the status page, and the agent-instructions file (its mobile section lists the smoke scope).
- Not to be edited (historical or frozen): every `appium3-compat-smoke-*` record, every `compatibility-smoke-execution-auth-v*` and `compatibility-smoke-implementation-lock-v*` file, the formal folders, `.github/workflows/e03-compatibility-smoke.yml`, `.github/workflows/e03-mobile-remediation.yml`, `qualification/compatibility-smoke/**` (the SUT-02 copies), `manifests/mobile-runner-remediation-v1.yaml`, and the protocol files.
- Validation and gates: `.github/workflows/e03-validate.yml` lints every workflow file (passes), length-checks every workflow (passes), and checks mirror entries that are not NOT_STARTED (passes once the entry is transcribed). It does not validate the SUT-01 authorization family (the file prefix `sut01-` is outside its glob), and its smoke-workflow assertions cover the SUT-02 file only. A check for the SUT-01 record family would need a validate change under the CI grant (HD-7). The G-7 gate of the measured-execution workflow reads the mirror generically; a SUT-01 NOT_STARTED entry is never matched by an E03 condition, so it needs no change.

## 5. Approval sequence (earliest realistic)

Each step is one approval; precedent for issuance, publication, dispatch, and recording is about one day (AUTH-01 to AUTH-03; publication-to-run 1 h to 7 h 20 min). A new realization has no precedent duration.

1. Human decisions HD-2, HD-3, HD-7, HD-13 to HD-18 (same day if taken on receipt).
2. HD-16 resolved (driver-resolved launcher, or a human-approved static APK manifest read). ORCHESTRATOR: correct the realization and rerun `make_draft_records.py` and the matrix.
3. HD-7: explicit CI grant naming the SUT-01 smoke workflow. Then the ORCHESTRATOR merges the draft workflow, the lock, and the record into the tracked tree (canonical repository), with its validation run.
4. Explicit issuance of APPIUM3-COMPAT-SMOKE-AUTH-04: the frozen prompt is written, the mirror patch is applied, and the record is promoted in place (ISSUED, VALID, ELIGIBLE). Nothing dispatched.
5. Export (human approval; the human research lead pushes), so GitHub can read the workflow. Post-push verification.
6. Separate explicit dispatch instruction: the dispatch record is written first; one run; the run identity recorded; the record closed (CONSUMED_AFTER_DISPATCH).
7. Import byte-exact, record the result (human approval of the recording), transcribe the mirror, export the record.
8. Independent of this smoke: E06 mapping (CS-007) review and freeze, E06 configuration and START approval, E06 workflow and its G-7 copy for SUT-01, verification of the backend per condition, one dispatch approval per condition run set. None starts with this smoke.

## 6. Human decisions (HUMAN DECISION, with the default used)

| ID | Decision | Default used in this draft |
|---|---|---|
| HD-1 | Scope: Android only, iOS deferred (brief HD-1, DP-8) | Android only; no iOS job or realization |
| HD-2 | Risk acceptance: a FAIL_RUNNER returns the study to UNRESOLVED_AFTER_FALLBACK_FAILURE and blocks SUT-02 too (9.5, 9.7.11) | accept and report; nothing drafted in advance for a second remediation (none exists under v3) |
| HD-3 | Backend (source finding) | hosted read-only sign-in against the pinned origin, PUBLIC_HOSTED, HOSTED_MAPPING_UNVERIFIED disclosed; a controlled backend or a DNS or TLS redirect is NOT the default (rule 3) |
| HD-4 | Canonical intent for E06 (CS-007) | out of scope for the smoke; as drafted for E06 later |
| HD-5 | Mobile oracle for E06 (DP-3) | smoke uses presence only; catalogue item identity TBD |
| HD-6 | Disclosure of sign-in mechanisms (DP-4) | out of scope for the smoke |
| HD-7 | CI grant naming the smoke and E06 workflows | do not merge the workflow until granted |
| HD-8 | Realization source (brief HD-8) | derived from the pinned source; Mobilewright identifiers cross-check only (done) |
| HD-9 | Harness: duplicate, SUT-02 files unchanged (brief HD-9) | duplicated; SUT-02 files byte-unchanged (checked by git status) |
| HD-10 | N (brief HD-10) | smoke: one execution per policy 9.1; E06 N separate (brief default 50) |
| HD-11 | H4 for SUT-01 versus SUT-03 on mobile (brief HD-11) | out of scope for the smoke |
| HD-12 | Parity estimand (brief HD-12) | out of scope for the smoke |
| HD-13 | Authorization id and namespace (brief HD-13) | APPIUM3-COMPAT-SMOKE-AUTH-04 (next free id); record file prefix `sut01-` so the SUT-02 glob-based checks are not changed; lock v5 (next free lock number, not a successor of v4) |
| HD-14 | Public export before dispatch (brief HD-14) | yes; the human research lead pushes |
| HD-15 (added by the ORCHESTRATOR; not in the brief) | Attribution of a hosted-backend refusal (a 429 `users_limit`, a 5xx) observed after the session request: policy 9.4 gives FAIL_RUNNER, and 9.3 has no backend category | a probe failure before the runner is NOT_EXECUTED / INFRASTRUCTURE (demonstrated by backend-probe.json); a refusal after the session request is FAIL_RUNNER by default. A protocol gap: a decision is needed on whether a hosted-backend refusal is INFRASTRUCTURE |
| HD-16 (added by the ORCHESTRATOR; not in the brief) | Launch activity (not in the pinned tree) | none set; driver-resolved; the realization keeps TBD so the gate refuses until resolved |
| HD-17 (added by the ORCHESTRATOR; not in the brief) | Locator match rule for labels shared by a pill and its text node (`Standard`, `Sign In`) | first match in driver hierarchy order, match count recorded in the record |
| HD-18 (added by the ORCHESTRATOR; not in the brief) | E06 NOT_STARTED as a precondition of the smoke | yes (the smoke precedes the E06 START); the E03 NOT_STARTED check of the SUT-02 workflow is not copied because E03 is FROZEN |

Additional protocol point for the human research lead (not a default): the 90 s arrival window may be short for a hosted backend's cold start. It is set to the SUT-02 value; no evidence supports a different number.

## 7. Hygiene and provenance notes

- The SUT repository URL (`https://github.com/gsanchezm/OmniPizza`) appears because it is the pinned provenance recorded in `manifests/sut-manifest.yaml`; it is not a statement about any person.
- Hashes are computed over the bytes as they stand in this worktree, which is a public-export snapshot. The canonical policy hash differs (section 3).
- The matrix and static outputs contain repository-relative paths only; the scratch folder and temporary fixture paths are never written to the outputs.
- No assistant or vendor name appears in the new files (checked by `tests/run_static_checks.py`).

## 8. Reconciliation with the coordinator's files (2026-11-06)

Read-only sources, from the main checkout: `experiments/E06-cross-platform-parity/mobile-path-brief-draft.md`, `experiments/scenario-mappings/CS-007.yaml`, `protocol/agent-governance-v6.md` (DRAFT), and `manifests/campaign-execution-plan-v1.yaml` (the human research lead's decisions of 2026-11-05). The worktree was created from a public-export snapshot that lacks them. Between the commit that this draft first cited (3cf2a4f8) and main, the brief, CS-007, and governance v6 are unchanged; the execution plan is new. The draft was first built from the brief through read-only `git show` of main.

Kept, because it conforms: Android-only topology and iOS deferred (HD-1); the SUT-01 versus SUT-02 pairing of the plan; the authorization id APPIUM3-COMPAT-SMOKE-AUTH-04 (brief HD-13; the plan names it); realization derived from the pinned source, with Mobilewright identifiers as cross-check only (HD-8); a duplicated harness with the SUT-02 files byte-unchanged (HD-9); the hosted, read-only backend default (HD-3; brief DP-7 option 2); a FAIL_RUNNER means no data and no successor drafted in advance (plan, answer 3; no v4 policy or contingency record exists in the tree); the reset by clean reinstall (CS-007, SESSION_RESET on Android); no merge until the CI grant is confirmed (HD-7).

Changed in this reconciliation: the scenario reference CS-007 is recorded in the workflow header, the README realization table, the lock, and the authorization, as reference only; the gate's token for the copied study-wide block is `E06-CS007-SUT01-ANDROID` (its fourth field gives the surface); the governance route (protocol/agent-governance-v5.md, Section 3.4) and the plan reference are recorded; the hygiene scan now names the agent-instructions file in both spellings.

Deviations from the brief and from CS-007, each with its reason:
1. Selectors. CS-007 names the Android testIDs `input-username`, `input-password`, `btn-login`, and `btn-user-<id>`. The smoke uses the accessibility ids `Standard` and `Sign In` (content-description from accessibilityLabel), because the testID-to-resource-id mapping on Android is not evidenced by any artifact (the source comment in qa.ts is the only statement). CS-007 allows selector variation if it is disclosed; reconcile at the E06 mapping freeze.
2. State read (MC-08). The brief (section 8) names the market selector as a candidate. The smoke reads element presence (screen-login before the sign-in, screen-catalog after), because the selected-state exposure of the radio pills is not evidenced.
3. Item identity (DP-3). The brief's default is to accept the mobile item selector with a static reading recorded before the mapping freeze, and to fall back to arrival only if the reading fails. The selector family is source-traceable: `text-pizza-name-<id>` (accessibilityLabel = the pizza name) and `card-pizza-<id>` (MobileProductCard.tsx lines 19 and 38). The expected name at the fixed position depends on the hosted catalogue, which no pin governs, so no expected value can be fixed statically. Under HD-5 that is the arrival-only fallback unless the human research lead accepts the hosted-catalogue dependency. This affects the E06 mapping, not the smoke.
4. Account behaviour mode (brief section 4, S2). It is not verified from backend source for standard_user. The behaviour-mode rows SUT01-EV-0015 and -0018 to -0021 concern other accounts. CS-007 records that the default-behaviour account is not stated. Open.
5. CI grant (HD-7). The brief's default is to obtain an explicit grant that names both workflows before drafting them. The drafts exist as DRAFT files not to be merged, per the coordinator's instruction. The grant is still required before any merge.
6. Gate content. The E06 precondition (E06-cross-platform-parity NOT_STARTED, HD-18) is an ORCHESTRATOR addition, not in the brief. The E03 NOT_STARTED check of the SUT-02 workflow is not copied, since E03 is FROZEN. The copied study-wide G-7 half is not the per-condition half; the brief expects the E06 measured workflow to carry its own G-7 copy.
7. Decisions added by the ORCHESTRATOR and not in the brief: HD-15 (backend refusal attribution), HD-16 (launch activity), HD-17 (locator match rule), HD-18 (E06 precondition), HD-19 (governance route). The plan's "accept defaults" covers only the design records' defaults, so these need the human research lead's decision.
8. Lock number. The brief names no number. Lock v5 is the next free number; v4 is the 9.7 remediation baseline of AUTH-03, and v5 is not a successor of it (different SUT).
9. Market, language, and account. US and en are the application defaults (LoginScreen.tsx line 51; useAppStore.ts lines 88 to 89), matching CS-007 DP-9 (one market with its default language). The account standard_user is documented and pre-filled (LoginScreen.tsx lines 47 and 48).
10. N. The smoke runs once (policy 9.1). N = 50 applies to the E06 cells, per the plan.
11. Plan open item 1 (is the endpoint configurable?). Answered by the source finding: not configurable without changing the build or the network path. The choice of backend classification remains HD-3.

Conflicts and gaps that block issuance (not resolved in this draft):
A. protocol/agent-governance-v5.md, Section 3.4, line 74, says the compatibility smoke "is closed by the exhausted fallback". Governance v6 (DRAFT), Section 3.4, repeats it ("At this document's creation the policy in force admits one execution only"). But the mobile-runner status is SELECTED since 2026-11-02 (policy v3, 9.7.9 and 9.7.10), and policy v3 section 9 applies the smoke to every mobile-capable ecosystem, SUT-01 included. Section 3.4 names the smoke as an allowed task and closes it in the same paragraph. The sentence is stale. The human research lead must decide the reading before AUTH-04 is issued; a correction belongs in the v6 freeze or in a representation edit. This is not resolved here.
B. Governance v6, Section 3.7 (dispatch authorizations), covers E02 and E04 to E12 only. The AUTH-04 dispatch is governed by v5 Section 3.4: the human's explicit approval of that exact dispatch. The plan lists AUTH-04 among the approvals not given.
C. If the v6 freeze keeps Section 3.4's sentence, the smoke route is closed after the freeze. That is a blocker for the v6 freeze, which the ORCHESTRATOR must flag; this draft does not change v6.

## 11. Update of 2026-11-06 (after the human decisions of that date)

The human research lead approved, on 2026-11-06, the freeze of protocol/agent-governance-v6.md including open decision HD-8 (conflicts A and C of section 8 are resolved: the stale sentence of Section 3.4 was updated as representation only; conflict B stands: the AUTH-04 dispatch keeps the approval of that exact dispatch under Section 3.4), the narrow CI grant E06-SMOKE-CI-WRITE-AUTH-01 for this smoke's workflow only (HD-7 is granted; the workflow is installed in the tracked tree), and the acceptance of the FAIL_RUNNER risk under policy v3 as written (no policy successor, no plan B; HD-2 is answered). Records: manifests/campaign-execution-decisions-v2.yaml, lines A to E. Still open before issuance: HD-13 (namespace), HD-15, HD-16 (launch activity), HD-17, HD-18, and the human issuance of AUTH-04. The lock and authorization drafts were regenerated by tests/make_draft_records.py on the canonical tree (the governing policy hash is now the canonical value). Nothing was issued, authorized, or dispatched.
