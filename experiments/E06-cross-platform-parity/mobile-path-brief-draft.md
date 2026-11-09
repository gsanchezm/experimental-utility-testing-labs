# Mobile path brief: SUT-01 compatibility smoke and a minimal E06 mobile suite (DRAFT)

| Field | Value |
|---|---|
| Status | DRAFT, preparation only. Nothing here freezes, starts, authorizes, dispatches, or decides anything. |
| Date | 2026-11-05 |
| Basis | Read-only review of the study repository (working copy at commit 9ca29e5). No run, no build, no workflow or gh command that changes state. |
| Governing text | protocol/mobile-runner-policy-v3.md (FROZEN-PRE-DATA, in force), sections 3, 5, 7, 8, 9, 9.1 to 9.7.13 |
| Companion | CS-007.yaml (same folder): DRAFT candidate canonical scenario CS-007 with six mapping entries and nine design points |
| Reading scope | derived-data/ and raw-data/ were not read (common rule 2). The brief's list named derived-data/e01-adjudicated-matrix; it was not opened for that reason. E01 cell values here are the auditors' provisional scores from the E01 evidence files on the audit branches, not confirmed scores. Confirmed scores must be taken from the matrix by the orchestrator. |

## 0. Summary

- **No SUT-01 mobile smoke exists, and the historical workflow cannot be reused.** `.github/workflows/e03-compatibility-smoke.yml` is hard-coded to SUT-02 (section 4) and refuses every dispatch: line 242 admits the mirror only with NOT_STARTED or preserved NOT_EXECUTED entries, and line 246 requires E03 to be NOT_STARTED, while E03 is FROZEN (experiments/E03-resetability/README.md, line 9). A new dispatch-only workflow, a SUT-01 realization, a new lock, a new authorization, and mirror entries are all needed.
- **The critical path is SUT-01 Android's realization and backend, not the smoke.** The smoke itself takes minutes (section 3.2). The SUT-01 mobile backend is the blocker: the repository does not state where the release build's backend endpoint is configured (HD-3).
- **The risk core is policy 9.5 and 9.7.11.** One FAIL_RUNNER of the selected runner, on any ecosystem and platform, returns the study to UNRESOLVED_AFTER_FALLBACK_FAILURE. That blocks every mobile condition, including the SUT-02 PASSes already recorded, and no second remediation exists under v3 (section 6).
- **Recommended minimal suite:** one candidate canonical scenario, CS-007 (no business state altered; sign in, reach the authenticated catalogue, observe one identity; session reset per run), on WEB and ANDROID. The between-ecosystem comparison is SUT-01 versus SUT-02, which is the H4 pair and therefore CONFIRMATORY (protocol/statistical-analysis-plan-v1.md, section 4.2). N = 50. iOS is deferred.
- **H4 cannot be tested on SUT-01 versus SUT-03 for mobile parity:** SUT-03 has no mobile surface (SUT03-EV-0010, SUT03-EV-0011). That is a structural fact to be reported, not a reason to change the pairs without change control (HD-11).
- **Earliest realistic dates (planning estimates, section 7.2):** smoke result on the push day, if the SUT-01 package is ready by 2026-11-13 (an assumption; section 7.2). E06 measured data in late December 2026 is the best case. DATA FREEZE is 2027-01-05 (manifests/planning-deadlines-v2.yaml, line 22).

## 1. Verified facts (path and location)

| Fact | Source |
|---|---|
| The smoke workflow's gate requires SUT-02, Android and iOS, Appium 3 at 3.7.0 | .github/workflows/e03-compatibility-smoke.yml, line 128 |
| The smoke workflow's job names and artifact names are SUT-02 | same file, lines 257, 316, 322, 352 |
| The realization check is the SUT-02 table string | same file, line 172 |
| Mirror gate (admits only NOT_STARTED or preserved NOT_EXECUTED) | same file, line 242 |
| E03-resetability must be NOT_STARTED | same file, line 246; experiments/E03-resetability/README.md, line 9 (FROZEN since 2026-10-29) |
| SUT-02 URLs, digests, package and bundle identifiers, and the output directory `SUT-02-<platform>` are literals | qualification/compatibility-smoke/smoke-common.sh, lines 11 to 17, 42, 71, 81 |
| The smoke harness realization is SUT-02 only (sut_id, component, identities, locators, expected state) | qualification/compatibility-smoke/harness/smoke.mjs, lines 25 to 91 and 140 |
| Entry scripts and their headers name SUT-02 | run-smoke-android.sh, run-smoke-ios.sh (header lines) |
| The remediation workflow is SUT-02 iOS only and names the AUTH-02 FAIL_RUNNER as its trigger | .github/workflows/e03-mobile-remediation.yml, line 213; consumed (manifests/compatibility-smoke-execution-auth-v3-prepared.yaml) |
| The compatibility-smoke mirror has SUT-02 android PASS and SUT-02 ios PASS and no SUT-01 entry | manifests/compatibility-smoke-status.yaml, entries at lines 47 and 58; grep count of SUT-01 = 0 |
| Study mobile-runner status is SELECTED, restored 2026-11-02 | manifests/toolchain-manifest.yaml, `mobile_runner_selection`, lines 57 to 63 |
| Appium 3 pins: core 3.7.0; uiautomator2 driver 8.7.0; xcuitest driver 12.13.2; Node 22.23.2 | manifests/toolchain-manifest.yaml, `mobile_fallback`; qualification/compatibility-smoke/README.md, line 30 |
| SUT-01 android and ios are CONFIRMED surfaces at release v1.1.8 (commit 3cdbe65) | manifests/sut-manifest.yaml, SUT-01 components (lines 70 to 95) |
| SUT-01 pinned builds: `omnipizza-release.apk` 84930726 bytes, SHA-256 1059e946…a6a4; `OmniPizza-Simulator.zip` 26921522 bytes, SHA-256 de2e8c21…dbc6eb1 | manifests/toolchain-manifest.yaml, `qualification_build`, lines 26 to 33 |
| Published digests of those two assets equal the pins (read-only fetch of the public release record, 2026-11-05; binaries not downloaded) | public release record for tag v1.1.8 (GitHub API metadata, stored only in the scratch folder) |
| SUT-01 controlled instance: web and API verified on GitHub Actions at pinned commit 9ca3767; SUT-01 mobile not provisioned | experiments/E03-resetability/controlled-instance-status.yaml, lines 102 to 141; manifests/sut-manifest.yaml, SUT-01 `controlled_instance_available` (null) |
| Where the release APK's backend endpoint is configured | not stated in the repository or in the E01 rows read |
| SUT-01 has account-specific behaviour modes that alter responses (latency, glitches) | SUT01-EV-0015, SUT01-EV-0018 to SUT01-EV-0021 (backend source rows) |
| SUT-01 android and ios E01 rows: deep links, login testIDs, market selector, cart hydration on mobile | SUT01-EV-0008 to SUT01-EV-0013, SUT01-EV-0028, SUT01-EV-0030 (audit branch evidence file) |
| SUT-02 android and ios E01 rows: login, reset, catalogue, locked-out rule; iOS login accepts any credential | SUT02-EV-0007 to SUT02-EV-0010, SUT02-EV-0016, SUT02-EV-0017 (audit branch evidence file) |
| SUT-02 web catalogue: fixed, non-randomized product catalogue with deterministic accounts (row read in full) | SUT02-EV-0013 (audit branch evidence file; its modality is Accessibility, Web only) |
| SUT-05 web: all 29 E01 rows read in full; SUT05-EV-0001 documents only a browsable web application; SUT05-EV-0026 documents sign-in selectors; no row documents a web catalogue or listing | audit branch evidence file for SUT-05 |
| No E01 row documents add-to-cart on any mobile surface (SUT-01 and SUT-02) | experiments/scenario-mappings/CS-003.yaml, SUT-01 justification (lines 79 to 81) and SUT-02 justification (lines 104 to 107) |
| SUT-03 has no mobile surface | SUT03-EV-0010 and SUT03-EV-0011 (NO_MOBILE_SURFACE); manifests/sut-manifest.yaml, SUT-03 android and ios ABSENT |
| SUT-04 and SUT-05 have no mobile surface | SUT04-EV-0011 to SUT04-EV-0014; SUT05-EV-0021 and SUT05-EV-0022 (NO_MOBILE_SURFACE) |
| SUT-06 has android and ios (v2.2.0), no web, no API; evaluated version not frozen | manifests/sut-manifest.yaml, SUT-06 (lines 302 to 347), `evaluated_version_frozen: false` at line 307 |
| CS-001 maps mobile only for SUT-02 (android, ios); SUT-01 maps WEB and API; SUT-06 NOT_COMPARABLE | experiments/scenario-mappings/CS-001.yaml, `mappings` |
| CS-003 maps no mobile surface for any SUT | experiments/scenario-mappings/CS-003.yaml, `mappings` (SUT-02 WEB only) |
| H4 pairs are SUT-01 versus SUT-02 and SUT-01 versus SUT-03; both CONFIRMATORY | protocol/statistical-analysis-plan-v1.md, sections 4.2 (line 75) and 4.3 (line 95) |
| The parity variable is "parity presence proportion per canonical scenario (E06)"; the denominator is not stated anywhere in the protocol | protocol/statistical-analysis-plan-v1.md, section 4.3; experiments/E06-cross-platform-parity/README.md, line 20 |
| N = 30 reduced target: "Expensive mobile conditions (Android Native, iOS Native modalities) only, if justified"; justification recorded before the first attempt, in the campaign README under E04 or E05 | protocol/repeatability-determinism-v1.md, section 3 (table line 51; rules lines 53 to 58). Applying it to E06 is an interpretation (HD-10). |
| Controlled-instance rule: state-changing, reset, fault, load, and security conditions run on a controlled instance, never PUBLIC_HOSTED; others may run on PUBLIC_HOSTED with environment_type recorded | protocol/study-design-v1.md, section 10.3 |
| E06 has no configuration; "protocol must be finalized before execution" | experiments/E06-cross-platform-parity/README.md, lines 35 to 41 |
| CI scope: E03-CI-WRITE-AUTH-01 names "mobile-qualification preparation"; CAMPAIGN-CI-WRITE-AUTH-01 names validation, provisioning and environment verification, and gated measured execution for E02 and E04 to E12. Neither names a compatibility smoke. | the agent-instructions file (CI sections) |
| Policy 9: the smoke "applies to every ecosystem, SUT-01 included"; scope "each platform for which E01 confirmed a surface" | protocol/mobile-runner-policy-v3.md, section 9 (lines 151 to 158) |
| Neutrality: qualification runs on SUT-01 give no evidence about SUT-01, and no qualification artifact may be cited as evidence | protocol/mobile-runner-policy-v3.md, section 3 (lines 59 to 64) |
| G-7 of the measured workflow requires an admitted mobile runner with no unresolved FAIL_RUNNER of the selected runner on any SUT and platform | .github/workflows/e03-measured-execution.yml, G-7 block (lines 188 to 237) |
| Repeatability and per-run record fields: environment_type; run manifest schema; schema v2 exists | schemas/run-manifest.schema.json; schemas/run-manifest.schema.v2.json (both present) |
| Planning: DATA FREEZE 2027-01-05; FINAL FREEZE 2027-01-22; campaigns not completed are reported as no data | manifests/planning-deadlines-v2.yaml, lines 22, 23, 29 |

## 2. Confirmed behaviour of the smoke chain (precedents)

| Precedent | Dates and times (UTC) | Source |
|---|---|---|
| APPIUM3-COMPAT-SMOKE-AUTH-01 | prepared 2026-09-24; issued 2026-09-26; export v27 pushed 2026-09-27T11:08:06Z; run created 2026-09-27T18:28:28Z (run 36340774530); Android NOT_EXECUTED (HARNESS_ORCHESTRATION) | manifests/appium3-compat-smoke-preparation-v1.yaml, line 11; manifests/compatibility-smoke-execution-auth-v1-prepared.yaml, line 50; PUBLIC-EXPORT-MANIFEST.yaml, line 546; manifests/appium3-compat-smoke-auth-01-run-v1.yaml, line 26; qualification/compatibility-smoke/README.md, line 99 |
| APPIUM3-COMPAT-SMOKE-AUTH-02 | issued 2026-09-28; export v29 pushed 2026-09-29T02:17:57Z; run created 2026-09-29T07:58:02Z (run 36539790536); Android PASS in 35 s; iOS FAIL_RUNNER (conservative tie-break) | manifests/compatibility-smoke-execution-auth-v2-prepared.yaml, line 47; PUBLIC-EXPORT-MANIFEST.yaml, line 566; manifests/appium3-compat-smoke-auth-02-run-v1.yaml, line 26; compatibility-smoke README, lines 100 to 101 |
| APPIUM3-COMPAT-SMOKE-AUTH-03 | lock v4 created and authorization issued 2026-11-02; export v43 pushed 2026-11-02T18:34:57Z; run created 2026-11-02T19:41:55Z (run 41512347186); iOS PASS; session start 266,216 ms | manifests/compatibility-smoke-execution-auth-v3-prepared.yaml, lines 27 to 28 and 44; manifests/compatibility-smoke-implementation-lock-v4.yaml, line 15; PUBLIC-EXPORT-MANIFEST.yaml, line 757; manifests/appium3-compat-smoke-auth-03-run-v1.yaml, line 28; compatibility-smoke README, line 102 |
| Correction precedent | AUTH-01 Android defect (titleTV not the navigation target) found after the run on 2026-09-27; corrected preparation and AUTH-02 issuance on 2026-09-28 | compatibility-smoke README, lines 39 and 99 |
| Qualification timing (Mobilewright, a different runner and scenario: not an Appium 3 duration and not SUT evidence) | Android job: 33 executions (3 warm-ups and 30 measured) in a 27 min 10 s window, about 49 s per execution with reset and install | qualification/mobilewright/README.md, environment table and line 273 |

Pattern: issuance, publication, dispatch, and recording each took place within about one day in all three cycles. Publication-to-run gaps were 7 h 20 min, 5 h 40 min, and 1 h 7 min. A new realization, a new workflow, and a new lock have no precedent duration; the AUTH-02 correction (one day) is the nearest and is a single locator change, not a new realization.

## 3. (a) Artifacts and approvals for a SUT-01 smoke

### 3.1 Sequence

Each step names the artifact or the approval, the nearest precedent, and whether a human acts. [H] marks a human approval or instruction.

| Step | Artifact or approval | Precedent | Gate in the repository |
|---|---|---|---|
| S1 | [H] Decisions HD-1 to HD-14 (section 6.2) | none | none |
| S2 | Static realization of SUT-01 Android (and iOS only if decided) from the pinned source at 3cdbe65 and from E01 rows: login identifiers, catalogue arrival, item identifiers, account behaviour mode, backend endpoint | AUTH-01 realization written from static evidence (2026-09-24) | the realization section must be locked (S5) |
| S3 | Controlled-instance decision for the backend (DP-7); if controlled, a provisioning record and a GitHub Actions verification of the SUT-01 backend | controlled-instance-status.yaml lines 102 to 141 (SUT-01 web and API) | study-design section 10.3 |
| S4 | Harness copy: a SUT-01 realization object in a new directory; the SUT-02 files stay byte-unchanged | none (SUT-02 files are locked; policy 9.7.12 depends on the shared wd.mjs) | lock |
| S5 | Implementation lock for the SUT-01 smoke: SHA-256 of every execution-critical file, the realization section hash, pins, the build digests | lock v2 (2026-09-26), v3 (2026-09-28), v4 (2026-11-02) | the lock's own gate |
| S6 | New dispatch-only workflow (for example `.github/workflows/e06-compatibility-smoke-sut01.yml`): gate for the authorization id, the SUT-01 pins and digests, the mirror entries, and the policy version | e03-compatibility-smoke.yml (prepared 2026-09-24) | the new gate; the authorization scope needs HD-7 |
| S7 | Local static validation: YAML parse, lint, a dry run of the gate on a copy of the public tree | export log static gate runs (PUBLIC-EXPORT-MANIFEST.yaml, lines 544 and 554) | the validation workflow |
| S8 | [H] Authorization record, id APPIUM3-COMPAT-SMOKE-AUTH-04 (next free number), issued VALID / ISSUED / ELIGIBLE with dispatch_performed false; frozen launch prompt | issuance of 2026-09-26, 2026-09-28, 2026-11-02 | the record's gate |
| S9 | [H] Public export containing the workflow, the lock, the authorization, and the realization (GitHub evaluates only the public repository); the human pushes | v27 at 2026-09-27T11:08:06Z; v29 at 2026-09-29T02:17:57Z; v43 at 2026-11-02T18:34:57Z | export builder and validation workflow |
| S10 | [H] Dispatch: a separate explicit instruction; the dispatch record is written first; one run; never re-run | runs 2026-09-27, 2026-09-29, 2026-11-02 | the workflow's own gate and single-attempt rule |
| S11 | Import byte-exact with digests; post-run record approved by the human research lead; mirror transcription by the orchestrator | same day in all three cycles | policy 9.7.8 pattern; the mirror rule |
| S12 | Export of the recorded result (publication) | export v44 and v45 after AUTH-03 | export log |
| S13 | E06 path, after S11 (see 7.1): CS-007 mapping review and freeze with a change-log row; E06 configuration and START approval; E06 workflow and a G-7 for SUT-01 (CI approval, HD-7); controlled or hosted verification per condition; a dispatch approval per condition run set | CS-003 drafted and frozen on 2026-11-02 (manifests/cs-003-freeze-v1.yaml) | protocol/equivalent-scenario-mapping-v1.md, section 6; protocol/change-control-v1.md, section 7 |

### 3.2 Time per smoke execution

The Android smoke execution took 35 s (AUTH-02, README line 100) and about 2 min (AUTH-01, README line 99); each job took longer with setup. The iOS smoke session start took 266 s in AUTH-03 against a declared session-start limit of 1200 s (README lines 46, 102). The smoke is not the bottleneck; the human-gated steps are.

### 3.3 Required fields of each run record

Environment records for every execution: environment_type (EMULATED for Android; SIMULATED for iOS; the backend's own environment_type, SELF_HOSTED or PUBLIC_HOSTED); the SUT component id and the pinned build's SHA-256 verified before any runner action; the runner pins and observed versions; the emulator identity (API 35, google_apis x86_64, pixel_7, the emulator-runner action at its pinned commit) and the runner image version; the backend commit and endpoint; the GitHub run id and attempt; the authorization id; the launch prompt id, which must be non-null for an automated run (the agent-instructions file, rule 9, citing prompts/README.md rule 5); UTC timestamps; each excluded execution with its attribution (policy 7.3 pattern).

## 4. (b) SUT-02-specific items: generalize or duplicate

| Item | SUT-02 literal or assumption | Action |
|---|---|---|
| .github/workflows/e03-compatibility-smoke.yml | gate line 128; job names (257, 322); artifacts (316, 352); realization string (172); mirror (242); E03 NOT_STARTED (246) | duplicate into a new file; do not edit the historical file, which is execution provenance |
| .github/workflows/e03-mobile-remediation.yml | SUT-02 iOS only; trigger AUTH-02 (line 213); consumed | not reusable |
| qualification/compatibility-smoke/smoke-common.sh | URLs (11, 13); package and bundle (16, 17); output directory (71); sut_id in records (42) | duplicate with SUT-01 values; leave the SUT-02 copy byte-unchanged |
| run-smoke-android.sh, run-smoke-ios.sh | headers and device identities for SUT-02 | rewrite as SUT-01 copies with the same substrates (ReactiveCircus emulator-runner and Xcode 16.4 / iOS 18.5 simulator, both pinned in manifests/toolchain-manifest.yaml, `environments`) |
| harness/smoke.mjs | sut_id, component, app identity, capabilities, locators and expected state (lines 25 to 91, 140) | the step runner is generic; add a SUT-01 realization object in a copy; do not edit the SUT-02 realization |
| harness/wd.mjs | generic W3C client; QUAL-U06 correction (lock v4); policy 9.7.12 relies on this file for the Android PASS | do not edit the SUT-02 copy; any SUT-01 copy starts from the lock v4 bytes |
| harness/package.json and package-lock.json | exact Appium 3.7.0 and drivers | reuse byte-identical; they are pins, not realization |
| manifests/compatibility-smoke-status.yaml | only SUT-02 entries | add SUT-01 entries (android; ios only if decided) as NOT_STARTED; transcribe only after a recorded result |
| e03-measured-execution.yml, G-7 and condition list (lines 36 to 44, 188 to 237) | E03 condition ids; G-7 reads the mirror generically | E06 needs its own measured workflow with its own G-7 copy; changing the E03 workflow needs its own approval |

Recommendation: duplicate everything that a SUT-01 run executes; change no SUT-02 file. This keeps the AUTH-02 and AUTH-03 evidence and the 9.7.12 basis unchanged.

## 5. (c) The smallest defensible E06 suite (recommended, not decided)

### 5.1 Scenario and comparability

Canonical scenario: CS-007 (candidate id; see CS-007.yaml). Intent: sign in with the standard identity and reach the authenticated catalogue, observing one object's identity. No business state is altered. The reset is the per-run session end that the CLEAN_SESSION precondition requires (SESSION_RESET; CS-003 DP-2 gives the same reasoning). The controlled-instance question of section 10.3 depends on how the sign-in is classified (DP-7).

| SUT | Provisional reading | Surfaces in the first wave | Reason and evidence |
|---|---|---|---|
| SUT-01 | COMPARABLE | WEB, ANDROID | Web sign-in, catalogue identifier, item name (SUT01-EV-0003, -0007, -0019). Android login identifiers and catalogue route (SUT01-EV-0009, -0010, -0011, -0028). Mobile item identity not evidenced (DP-3). |
| SUT-02 | COMPARABLE | WEB, ANDROID (iOS deferred) | Web sign-in and fixed catalogue (SUT02-EV-0001, -0013). Android sign-in and arrival (SUT02-EV-0007); catalogue construction (SUT02-EV-0016); item name for the standard account partial (DP-3). |
| SUT-03 | COMPARABLE on WEB; mobile cells not applicable | WEB | Web sign-in and listing (SUT03-EV-0001, -0003, -0005, -0006); no mobile surface (SUT03-EV-0010, -0011). Rule 1 of the protocol is satisfied on WEB (DP-5). |
| SUT-04 | COMPARABLE on WEB; mobile cells not applicable | WEB | Web sign-in and room listing (SUT04-EV-0002, -0004); no mobile surface (SUT04-EV-0011 to -0014). The administrator account is a CS-003 choice carried over. |
| SUT-05 | NOT_COMPARABLE (provisional; evidence absent) | none | All 29 rows read in full: a browsable web application (SUT05-EV-0001) and sign-in selectors (SUT05-EV-0026); no row documents a web catalogue or listing (DP-6); no mobile surface (SUT05-EV-0021, -0022). |
| SUT-06 | NOT_COMPARABLE (NO_EQUIVALENT_INTENT) | none | No catalogue of business objects (SUT06-EV-0005, -0007); login validation local only (SUT06-EV-0011); no web surface. |

### 5.2 Platforms

WEB and ANDROID in the first wave. iOS is deferred for four reasons: (1) the iOS path has the only FAIL_RUNNER of the Appium 3 history (AUTH-02; cause NOT_ESTABLISHED, qualification/unresolved.md QUAL-U06, cited by policy 9.7.1); (2) the AUTH-03 iOS session took 266 s of a 1200 s limit, on macos-15; (3) SUT-01 iOS is a simulator-only build (SUT01-EV-0013); (4) iOS adds a second smoke and a second FAIL_RUNNER exposure without adding a second H4 pair, because the H4 variable is per scenario. The iOS substrate is the same pinned macOS and Xcode 16.4 setup, so an iOS cell can be added later under its own smoke.

### 5.3 Comparisons

| Comparison | Class | Note |
|---|---|---|
| SUT-01 versus SUT-02 | CONFIRMATORY (H4), protocol/statistical-analysis-plan-v1.md section 4.2 | only if both are COMPARABLE on the cells used; Holm across the RQ4 family |
| SUT-01 versus SUT-03 | CONFIRMATORY (H4) by the SAP, but no mobile parity cell exists for SUT-03 | the parity measure for this pair is "no data, reason: no mobile surface" (SAP section 5, line 107); see HD-11 |
| SUT-04 and SUT-05 | none in E06 mobile | web-only; any comparison is EXPLORATORY (SAP section 4.2) |
| Any comparison with SUT-06 | EXPLORATORY | NOT_COMPARABLE on CS-007 |

### 5.4 N

Recommended N = 50 per condition. The protocol's reduced target (N = 30) is written for E04 and E05 repeatable conditions and requires a justification "based on operational cost, never on anticipated results", recorded in the campaign README and in the run manifests before the first attempt (protocol/repeatability-determinism-v1.md, section 3). Whether that rule covers E06 is an interpretation (HD-10). The cost does not support a reduction. The only timing available is Mobilewright's (about 49 s per execution, section 2; not an Appium 3 duration), which gives about 41 min for 50 executions per Android condition. Appium 3 and web timings were not measured. N = 50 avoids the interpretation question.

### 5.5 Observables and estimand

- Per execution: the sign-in outcome; arrival at the catalogue; the identity of the catalogue position fixed for the run (UI_STATE); the environment and attribution records. Duration is secondary and enters no parity measure (policy section 7.4, by analogy).
- Parity presence (the SAP variable): proportion of paired executions, same clean cycle, same account and market, on which the identities match on both surfaces, computed per ecosystem and scenario; interval by Wilson; effect by risk difference between SUT-01 and SUT-02 (SAP sections 3 and 4.3). The denominator is not stated in the protocol (HD-12).
- A second reading, per platform with two cells, gives no interval and is descriptive only.
- With one canonical scenario, each between-ecosystem comparison has one scenario pair (SAP section 4.1), so H4 rests on one scenario whichever reading is chosen.

### 5.6 Records that E06 needs

Per cell: the scenario id and its FROZEN mapping record; the platform's environment_type; the pinned build SHA-256; the runner pins; the backend commit and classification; the authorization id, the launch prompt id, the GitHub run id and attempt; one run manifest per execution (schemas/run-manifest.schema.json; the v2 schema adds per-action outcomes); the screenshots and logs per execution (experiments/E06-cross-platform-parity/README.md, Required evidence).

## 6. (d) Risk analysis and pre-decisions

### 6.1 What each smoke outcome means

| Outcome | For SUT-01 Android | For SUT-01 iOS (if ever) | For SUT-02 and every other mobile condition | Study-level status |
|---|---|---|---|---|
| PASS | satisfies the SUT-01 Android requirement only (policy 9.5, 9.6); E06 Android cells become admissible subject to S13 | unchanged: unresolved until its own PASS | no effect on SUT-02 PASSes; admission still needs each condition's own gates | SELECTED stays |
| NOT_EXECUTED | no pass and no fail; SUT-01 Android conditions stay blocked. A further attempt needs the demonstrated cause corrected, a successor lock if execution-critical code changed, and a new authorization. No CI re-run substitutes (9.5) | same | none | unchanged |
| FAIL_RUNNER | the fallback is exhausted again (9.5, final paragraph: one FAIL_RUNNER is sufficient) | same | every mobile condition is blocked from START and measurement, including SUT-02 Android and iOS PASSes (9.5 and 9.7.11; G-7 block) | UNRESOLVED_AFTER_FALLBACK_FAILURE (9.5) |

Points that follow from the table:

- A FAIL_RUNNER is the default when attribution is uncertain (9.4). A realization that has never run on SUT-01 can fail for reasons the harness cannot separate from the runner, so the probability of FAIL_RUNNER is not small and is not estimated here.
- A positively demonstrated harness defect (as with AUTH-01 titleTV) gives NOT_EXECUTED, not FAIL_RUNNER. The realization must therefore be checked on static evidence before dispatch, which is S2.
- After a FAIL_RUNNER, no second remediation exists under v3 (9.7.5, 9.7.11). Recovery needs a new explicit protocol amendment deciding the mobile strategy (9.5). Appium 2 is never introduced; another runner needs its own protocol decision (9.7.13).
- Consequences of a FAIL_RUNNER for E06: its mobile cells are reported as no data with the reason; web-only parity remains if DP-5 is accepted. For other campaigns (E02, E05, E07, E09, E12) any mobile condition is blocked.
- E03's two mobile conditions stay frozen; the human research lead decided on 2026-11-03 not to reopen them (the agent-instructions file, Rule 14).

### 6.2 Pre-decisions before the first dispatch (HUMAN DECISION)

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| HD-1 | Accept the minimal scope: CS-007, WEB and ANDROID, SUT-01 versus SUT-02; iOS deferred | accept; add iOS now; drop mobile | accept |
| HD-2 | Risk acceptance and post-FAIL_RUNNER policy | (a) accept and report mobile E06 cells as no data with the reason; (b) draft a v4 amendment now (not frozen); (c) stop the mobile path for E06 | (a); draft nothing in advance; decide only if the event occurs |
| HD-3 | Backend for SUT-01 mobile (DP-7) | (a) endpoint configurable: controlled backend; (b) not configurable: read-only sign-in classified as non-state-changing, PUBLIC_HOSTED disclosed, with the HOSTED_MAPPING_UNVERIFIED caveat (manifests/sut-manifest.yaml, SUT-01 web and api notes); (c) drop | check the endpoint first; then (a) or (b) |
| HD-4 | Canonical intent, reset SESSION_RESET, id CS-007 (DP-1, DP-2, DP-9) | as drafted; state-changing (DP-1) | as drafted |
| HD-5 | Mobile oracle reading (DP-3) | accept with static reading recorded before freeze; narrow to arrival; new E01 rows under change control | accept with the static reading; fall back to arrival if the reading fails |
| HD-6 | Disclosure of differing sign-in mechanisms (DP-4) | disclose; exclude | disclose |
| HD-7 | CI authorization for the smoke workflow and the E06 workflow and G-7 copy | the existing grants (E03-CI-WRITE-AUTH-01 names mobile-qualification preparation; CAMPAIGN-CI-WRITE-AUTH-01 does not name a smoke); or a new narrow grant | obtain an explicit grant that names both workflows before drafting them |
| HD-8 | Realization source: derive afresh from E01 rows and the pinned SUT-01 source | derive afresh; reuse the Mobilewright identifiers | derive afresh. The qualification realization (for example `screen-login`, `card-pizza-p01`, `btn-add-pizza-p12`, package `com.omnipizza.app`) is an implementation reference to cross-check only, never evidence (policy section 3) |
| HD-9 | Harness: duplicate; SUT-02 files unchanged | duplicate; generalize in place | duplicate |
| HD-10 | N (and whether the reduced-N rule applies to E06) | 50; 30 with a recorded cost justification | 50 |
| HD-11 | H4 for SUT-01 versus SUT-03 on mobile parity | (a) structurally not estimable, reported as no data with the reason, no protocol change; (b) change the pair (change control, post-data); (c) define web-versus-API parity (a different intent; E07 territory) | (a) |
| HD-12 | Parity estimand and denominator | per-execution paired reading (inferential); per-platform reading (descriptive) | per-execution, defined before the freeze |
| HD-13 | Authorization id and namespace for the SUT-01 smoke | APPIUM3-COMPAT-SMOKE-AUTH-04 in the existing namespace; a SUT-01 namespace | AUTH-04 in the existing namespace, unless HD-7 says otherwise |
| HD-14 | Public export before dispatch | yes (precedent); no | yes; the human pushes |

Design-point mapping: DP-1 and DP-2 to HD-4; DP-3 to HD-5; DP-4 to HD-6; DP-5 to HD-11; DP-6 and DP-8 to HD-1; DP-7 to HD-3; DP-9 to HD-4 (the nine design points are in CS-007.yaml).

Open items the human research lead should know (not decisions): SUT-02's standard-account Android catalogue identity is not evidenced as a row; SUT-02 iOS sign-in accepts any credential; SUT-06 has evaluated_version_frozen false, so any SUT-06 campaign needs its version frozen first (manifests/sut-manifest.yaml, line 307).

## 7. (e) Steps, approvals, and dates

### 7.1 Steps

| Step | Approval | Duration basis | Earliest realistic date (planning estimate) |
|---|---|---|---|
| 1. Decisions HD-1 to HD-14 | [H] | none | 2026-11-06 if taken on the day received |
| 2. Static realization SUT-01 Android (and the backend question, HD-3) | none | no precedent for a new SUT; the AUTH-01 realization was one document from static evidence | not estimable from precedent |
| 3. Harness copy, workflow, lock, validation (S4 to S7) | [H] for the CI grant (HD-7) | no precedent; the nearest is lock v3 with its gate validated on its issuance day | not estimable from precedent |
| 4. Issuance (S8) | [H] | same day as the package is complete | same day as step 3 |
| 5. Public export and push (S9) | [H] push | publication to run: 1 h to 7 h 20 min | same day or next working day after step 4 |
| 6. Dispatch and record (S10, S11) | [H] dispatch; [H] recording | run within hours of the push; recording the same day | the smoke result on the day of step 5, at the earliest |
| 7. CS-007 mapping review and freeze (DP and HD decisions) | [H] | CS-003: drafted and frozen the same day, after its five design points were decided (manifests/cs-003-freeze-v1.yaml) | can run in parallel with steps 2 to 6 |
| 8. E06 configuration, START, E06 workflow and SUT-01 G-7 | [H] START; [H] CI grant | no precedent for E06; the E03 START was approved on 2026-10-28 (the agent-instructions file, Current phase) | not estimable from precedent; parallel with 2 to 6 |
| 9. Controlled or hosted verification per E06 condition | none (verification) | SUT-01 web and API verified on GitHub Actions (run 40628631086, controlled-instance-status.yaml, lines 102 to 141) | not estimable for the mobile conditions |
| 10. Dispatch of each E06 run set | [H] per dispatch | E03 dispatch authorizations were issued the day the START was approved | one per condition; per-run approval |
| 11. Import, descriptive analysis, E06 report | none | per the SAP | before DATA FREEZE 2027-01-05 |

### 7.2 Earliest realistic dates

- Smoke result: if the decisions are taken on 2026-11-06 and the package (steps 2 and 3) is ready by 2026-11-13, the earliest result is the push day, 2026-11-13, with the run within hours of the push (precedent: 1 h to 7 h 20 min between publication and run). The readiness date is an assumption with no precedent; it is a planning estimate, not a forecast.
- E06 measured data: after a smoke PASS, steps 7 to 10 must finish. Without precedent for steps 7 and 8, the best case is the last week of December 2026. Four conditions at N = 50 are small in run time; the constraint is approvals and the G-7 copy.
- DATA FREEZE 2027-01-05 leaves little slack after the best case. A NOT_EXECUTED outcome adds one cycle (correction, successor lock if needed, authorization, publication, dispatch); by precedent that cycle took about two days, but a new realization may take longer. A FAIL_RUNNER ends the mobile path (section 6.1), and the campaigns would be reported as no data with that reason (manifests/planning-deadlines-v2.yaml, line 29).

## 8. Items not established

- The SUT-01 release build's backend endpoint configuration (not stated in the repository).
- SUT-01 mobile catalogue item identifiers and rendering, and the Android arrival after sign-in (no E01 row).
- The MC-08 state read on SUT-01 Android for the smoke: not evidenced; the market selector is the candidate.
- SUT-02 Android standard-account catalogue identity (no row for the standard account).
- SUT-06 evaluated_version_frozen is false and its controlled-instance status is null.
- The confirmed (adjudicated) E01 scores: not read (common rule 2).
- The binary digests were compared with the published record only; the study has not downloaded or verified the binaries.

## 9. Scope of this brief

This brief decides nothing, freezes nothing, and authorizes nothing. It runs no smoke, build, emulator, simulator, or campaign, and it changes no repository file. It writes only to the scratch folder. The companion file is the candidate mapping record in DRAFT. The brief names no ecosystem as the reference; SUT-01 is treated like every other SUT (policy section 3; the agent-instructions file, rule 12).
