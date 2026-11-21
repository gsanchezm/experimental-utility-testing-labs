# E06 Cross-platform Parity: design brief for the full campaign after a smoke PASS (DRAFT)

| Field | Value |
|---|---|
| Status | DRAFT, preparation only. It decides, freezes, starts, authorizes, and dispatches nothing. Every "recommended" below is a proposal for the human research lead. |
| Date | 2026-11-20 |
| Precondition | A recorded PASS of the SUT-01 × Android compatibility smoke (APPIUM3-COMPAT-SMOKE-AUTH-04). With a FAIL_RUNNER the mobile cells of E06 are reported as no data with the reason (manifests/campaign-execution-decisions-v16.yaml, D-E06-4; the plan of 2026-11-05) and this brief is not used. |
| Builds on | experiments/E06-cross-platform-parity/mobile-path-brief-draft.md (decisions HD-1 to HD-14), experiments/scenario-mappings/CS-007.yaml (DRAFT; points DP-1 to DP-9), experiments/E06-cross-platform-parity/static-reading-oracle-draft.md, manifests/campaign-execution-decisions-v16.yaml, protocol/statistical-analysis-plan-v1.md (section 4.3, H4), protocol/mobile-runner-policy-v3.md. |

## 1. Proposed shape

| Item | Proposal |
|---|---|
| Scenario | CS-007 only (read-only sign-in and arrival at the authenticated catalogue, identity of the first catalogue position; reset SESSION_RESET), frozen first under its own approval (DP-1 to DP-9). |
| Measured conditions | Four: E06-CS007-SUT01-WEB, E06-CS007-SUT01-ANDROID, E06-CS007-SUT02-WEB, E06-CS007-SUT02-ANDROID. N = 50 each, 200 executions, attempt 1. |
| Cells without executions | SUT-03 and SUT-04 (web only): parity cells recorded not applicable with the reason (no mobile surface; SUT03-EV-0010, SUT03-EV-0011, SUT04-EV-0011 to SUT04-EV-0014). SUT-05 and SUT-06: NOT_COMPARABLE as drafted in CS-007. iOS of every ecosystem: deferred (HD-1), recorded untested. |
| Pairs | Per ecosystem, execution k of the WEB condition is paired with execution k of the ANDROID condition (same account, same market, same index). |
| Parity | Present for pair k when both executions reach the authenticated catalogue and the identity of the first catalogue position is the same on both surfaces. Absent otherwise; an execution that did not arrive is recorded with its reason and is a non-parity, never excluded after the fact. |
| Estimand | Parity proportion per ecosystem = pairs with parity / 50, with a Wilson 95% interval; effect SUT-01 versus SUT-02 by risk difference with an interval and Fisher's exact test (protocol/statistical-analysis-plan-v1.md, section 4.3). SUT-01 versus SUT-03: no data, reason: no mobile surface (not estimable; HD-11 option a). Descriptive only where the plan has no criterion. |
| Identity key | SUT-01: the pizza id (web `pizza-name-<id>`, SUT01-EV-0003; Android card identifier `card-pizza-<id>` with the name as accessibility label, static reading). SUT-02: the product title of the first entry in the default ascending name order (web inventory item name, SUT02-EV-0013; Android `titleTV` text, static reading). |
| Backend of SUT-01 | Both surfaces on the hosted deployment: web at https://omnipizza-frontend.onrender.com and the release APK's fixed origin https://omnipizza-backend.onrender.com, environment_type PUBLIC_HOSTED, HOSTED_MAPPING_UNVERIFIED disclosed. The same backend serves both surfaces, so a difference of item data between a pinned web instance and a hosted mobile backend cannot masquerade as a platform difference. Read-only sign-in needs no controlled instance (protocol/study-design-v1.md, section 10.3, classified under D-E06-2 of the decisions of 2026-11-20). |
| Backend of SUT-02 | Web: the hosted sample site (HOSTED_MAPPING_UNVERIFIED, as in manifests/sut-manifest.yaml); Android: the local database of the pinned build. |
| Platforms | WEB through the browser executor of the earlier campaigns; ANDROID through Appium 3.7.0 on the GitHub-hosted emulator (API 35, pixel_7), each execution from a clean install (adb uninstall, reinstall, new session). |
| Workflows | Dispatch-only and fail-closed, under CAMPAIGN-CI-WRITE-AUTH-01: an environment-verification workflow (non-measured DRY_RUN) and a measured-execution workflow with a G-7 copy that admits an Android condition only with a smoke PASS recorded in the mirror for its exact SUT, platform and runner, and the study-level mobile-runner status SELECTED. |
| Dispatch authorizations | Two, one per assigned SUT (SUT-01: WEB and ANDROID conditions; SUT-02: the same), issued by the human research lead under protocol/agent-governance-v6.md, Section 3.7; SUT-02 Android additionally needs its own smoke PASS (recorded: APPIUM3-COMPAT-SMOKE-AUTH-02), SUT-01 Android needs AUTH-04. |

## 2. Risks to disclose

1. The mobile smoke is a tool prerequisite and not evidence (policy section 3); a smoke PASS says nothing about parity.
2. SUT-01 hosted deployments are not pinned (HOSTED_MAPPING_UNVERIFIED): item data may change between executions or days. The paired design reads both surfaces within the same cycle to limit this, and a drift is visible as a non-parity that the record explains.
3. The hosted backend has a user limit that answers 429 `users_limit` (LoginScreen.tsx lines 92 to 93 at the pinned commit): a refusal during a measured execution is recorded as an infrastructure-caused non-arrival with its message, never repaired and never excluded silently.
4. The catalogue order of SUT-01 depends on the market, language and the backend; the market and account are fixed per condition (DP-9).
5. The mobile identity reading rests on a static reading of the pinned source; a non-measured DRY_RUN decides whether each surface exposes it, and the fallback to arrival-only is decided before the START.
6. One canonical scenario gives one scenario pair per comparison: H4 rests on CS-007 whichever reading is used, so any between-ecosystem result is descriptive in weight.

## 3. Decisions for the human research lead (HUMAN DECISION; recommended in bold)

| ID | Decision | Options | Recommended |
|---|---|---|---|
| E06-D-1 | CS-007 design points DP-1 to DP-9 (read-only intent; identifier CS-007; mobile oracle accepted with the static reading; disclosure of differing sign-in mechanisms; web-only ecosystems COMPARABLE on WEB with mobile cells not applicable; SUT-05 and SUT-06 NOT_COMPARABLE; backend classification; WEB and ANDROID; one market and account per ecosystem) | as drafted; change any point | **as drafted** (DP-7 resolved by the decision D-E06-2 of 2026-11-20) |
| E06-D-2 | Measured conditions and N | four conditions, N = 50 | **four, N = 50** |
| E06-D-3 | SUT-01 backend for both surfaces | hosted web and hosted backend; pinned controlled web with hosted mobile backend | **hosted both** |
| E06-D-4 | Estimand and pairing (section 1) | paired per index, parity proportion per ecosystem; per-platform descriptive only | **paired per index** |
| E06-D-5 | Identity key (section 1) | as proposed; arrival only | **as proposed, with arrival-only as the recorded fallback** |
| E06-D-6 | Non-measured DRY_RUN rounds on GitHub Actions before the START | at least one round per condition, each on its own approval of the exact line | **yes** |
| E06-D-7 | Dispatch authorizations | two (SUT-01, SUT-02) | **two** |

## 4. Path after a smoke PASS (each step on its own approval)

1. Decisions E06-D-1 to E06-D-7, and the freeze of CS-007 with its change-log row (authorization id E06-CS007-FREEZE-AUTH-01, as the earlier mapping freezes).
2. Executor, environment-verification workflow and measured-execution workflow (a DRAFT, then lint and static tests), the E06 conditions record.
3. DRY_RUN rounds on the public repository (export, then the exact dispatch line, per round); a DRY_RUN never enters raw-data/.
4. START package and START (change-control, section 7); export; the two dispatch authorizations; export; the dispatches by the ORCHESTRATOR; the import byte-exact under raw-data/E06-cross-platform-parity/; freeze; export; the descriptive analysis only on the human research lead's instruction.

## 5. Scope of this brief

It names no ecosystem as the reference; SUT-01 is treated like every other SUT (the agent-instructions file, rule 12). It writes only this file and changes no protocol, mapping, workflow, or record.
