# E02 State Establishment -- design brief (DRAFT)

| Field | Value |
|---|---|
| Status | **DRAFT.** Not frozen, not a campaign configuration, not a START, not a dispatch authorization. Nothing here starts, authorizes, or dispatches anything. |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Campaign | E02-state-establishment (`experiments/E02-state-establishment/README.md`, status NOT STARTED) |
| Date | 2026-11-05 |
| Companion files | `CS-004.yaml` (DRAFT second establish-side canonical scenario); `h2-reset-side-options-draft.md` (DRAFT options for the reset side) |
| Read for this brief | `experiments/E02-state-establishment/README.md`; `experiments/scenario-mappings/CS-003.yaml` and `CS-001.yaml` (full); `protocol/equivalent-scenario-mapping-v1.md`; `protocol/setup-effort-v2.md`; `experiments/E03-resetability/README.md`; `experiments/E03-resetability/campaign-configuration-draft.md`; `experiments/E03-resetability/executor/README.md`; `experiments/E03-resetability/ci-cd-execution-model.md`; `manifests/e03-campaign-start-package-v2.yaml` (structure); `protocol/change-control-v1.md` (sections 2, 5, 7, 8); `protocol/statistical-analysis-plan-v1.md` (sections 3 to 6); `protocol/study-design-v1.md` (sections 6, 10.3); `protocol/repeatability-determinism-v1.md` (section 3); `protocol/agent-governance-v5.md` (section 3.6); `manifests/sut-manifest.yaml` (flags); `manifests/campaign-resumption-v1.yaml`; `experiments/README.md`; `.github/workflows/e03-measured-execution.yml` (gate comments); `schemas/run-manifest.schema.v2.json` (top-level fields); E01 evidence rows on the six `audit/e01-sut0N-*` branches; the E01 adjudicated matrix (see section 0). |
| Not read | `raw-data/` (all); every H1 and H2 result and analysis output; `derived-data/` other than the adjudicated matrix named in the brief. |
| Hygiene | English; the human research lead is the only role named for people; no local paths, assistant or vendor names, or conversation identifiers; the agent-instructions file is referred to by role only. |

## 0. Reading notes and conflicts

1. **E01 evidence location.** The E01 evidence rows are not on `main`. Each SUT's rows are on its own branch, `audit/e01-sut0N-*`, path `audits/SUT-0N-*/evidence.csv`. The `audits/` directories on `main` are unmerged templates (`protocol/unresolved.md`, PROTO-U07). All E01 citations below were read from those branches.
2. **Conflict with the common read rule.** The brief's common rule 2 excludes derived-data results, but its reading list names `derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json`. This brief read only that one file, for the confirmed scores of the web and API cells. It did not read the H1 result or the H2 result. The human research lead should confirm this reading.
3. **"Campaign version" is undefined.** The phrase "current E03 campaign version" appears in `experiments/E03-resetability/canonical-scenario-catalogue.md` and in the CS-001 notes. `protocol/change-control-v1.md` does not define it (grep of `protocol/`: no definition). Relevant to `h2-reset-side-options-draft.md`.
4. **Order of items.** The brief asks for the items in the order of the "Common rules" of `experiments/README.md`. That section's bullets run in a different order (environment type, environment control, configuration, scenario equivalence, classification, setup effort, raw data, derived data, all six SUTs, repetition, analysis, tooling, substrate, evidence). This brief follows the order of the campaign-configuration items in `protocol/change-control-v1.md`, section 7 (moment 1), which the brief lists.
5. **Gaps.** "Not stated" marks a point that the repository does not state. Numbers derived by this brief are labelled as derived.

## 1. Summary

- E02 measures the per-run Required Actions (establish side) to reach a canonical target state from a declared starting state, per `protocol/setup-effort-v2.md`, sections 3 and 5. Its only inferential use is H2 (`protocol/study-design-v1.md`, section 6; `protocol/statistical-analysis-plan-v1.md`, section 4.3): SUT-01 versus SUT-02 and SUT-01 versus SUT-03, on the WEB surface, paired per canonical scenario.
- The only frozen establish-side scenario is CS-003. A second one is needed so the H2 pairs are not n = 1. The draft CS-004 targets a **checkout-ready** state, not a committed order. The reason is evidence: the E01 rows support checkout entry on all three web surfaces, but none of them documents a completed commitment on SUT-02 (`CS-004.yaml`, DP-2). With the precondition as the independence lever (SEEDED, not CLEAN), CS-004 is COMPARABLE for SUT-01, SUT-02, and SUT-03 on WEB, NOT_COMPARABLE for SUT-04 and SUT-06, and pending for SUT-05.
- With two scenarios per side, the H2 comparisons stay **descriptive**. Derived here (not stated in the repository): with n non-tied pairs the smallest two-sided exact Wilcoxon p-value is 2 x 2^-n, i.e. 0.5 at n = 2, 0.0625 at n = 5, and 0.03125 at n = 6. Two scenarios cannot reach significance under any data. `protocol/statistical-analysis-plan-v1.md`, section 3, applies Wilcoxon only where "the number of non-tied pairs is adequate", a term the document does not define. Verify the arithmetic before relying on it.
- E02 inverts E03's counting convention. E03 counts reset-side actions only; E02 counts establish-side actions, which include logins, seeding, navigation, and verification. This needs its own counting realization and its own executor.
- Every E02 condition needs a deterministic reset between runs (`protocol/study-design-v1.md`, section 10.3, list item 1), and most change state that persists beyond the client session (list item 5). So each needs a controlled instance and its own GitHub-verified status (gate G-8 analogue).
- Governance: the per-SUT dispatch authorization the human research lead intends for E02 does not exist yet. `protocol/agent-governance-v5.md`, section 3.6, requires approval of each dispatch. A governance successor is needed.
- Two issues in the frozen CS-003 are not ruled on (HUMAN DECISION, section 8): the SUT-02 oracle is also UI-only, but CS-003 DP-3 names only SUT-03; and the SUT-04 account in CS-003 is an administrator under an intent that says "standard".
- Mobile: no mobile surface is mapped in CS-003 (DP-4) or in CS-004. SUT-03 has no mobile code (SUT03-EV-0010, SUT03-EV-0011). Mobile cells also need an admissible runner and an exact SUT x platform x runner compatibility smoke (`protocol/mobile-runner-policy-v3.md`; the E03 README "Mobile qualification" row). Mobile is outside H2 and is not in this proposal.

## 2. (a) Campaign-configuration items, in change-control order

Each item gives a proposed value and its source, or HUMAN DECISION (HD). Numbers are proposals, not predeclared results.

### 2.1 Canonical scenarios and mapping records

| Scenario | Status | Use |
|---|---|---|
| CS-003 | FROZEN 2026-11-02 (`E02-CS003-FREEZE-AUTH-01`; `experiments/scenario-mappings/CS-003.yaml`; `manifests/cs-003-freeze-v1.yaml`). Precondition CLEAN_SESSION; target: one item held in its container; oracle BUSINESS_STATE with SUT-03 realized as UI_STATE. | Establish side, first scenario. Used by the first pair of H2. |
| CS-004 | DRAFT (`CS-004.yaml`). Precondition SEEDED_BUSINESS_STATE; target: checkout-ready; oracle UI_STATE; WEB mapped for SUT-01, SUT-02, SUT-03. | Establish side, second scenario. Not an input until frozen (`protocol/equivalent-scenario-mapping-v1.md`, section 6). |
| CS-001 | FROZEN, E03 only. | Not an E02 input (`experiments/E02-state-establishment/README.md`, Preparation paragraph). |
| CS-002 | EXCLUDED_FROM_CAMPAIGN (2026-09-22). | Not an input to any campaign (`manifests/e03-cs002-exclusion-v1.yaml`). |

- **HD-1 (adopt the CS-004 target).** Options: (a) checkout-ready, supported by existing evidence (recommended); (b) committed order or booking, which needs new evidence rows (SUT-02 completion page; SUT-01 create request) and adds a persisted record. Recommendation: (a).
- **HD-2 to HD-8 (CS-004 decision points DP-1 to DP-8).** See `CS-004.yaml`, `notes`. The independence lever is DP-1 (SEEDED versus CLEAN).
- **HD-9 (freeze).** CS-004 must be FROZEN before any E02 START, by one mapping-record row in `protocol/CHANGELOG.md` (`protocol/change-control-v1.md`, section 5 row form). Not decided here.
- **Comparability summary for CS-004 (DRAFT):** SUT-01 WEB COMPARABLE; SUT-02 WEB COMPARABLE; SUT-03 WEB COMPARABLE; SUT-04 NOT_COMPARABLE (NO_EQUIVALENT_INTENT, DP-7); SUT-05 pending (DP-8); SUT-06 NOT_COMPARABLE (NO_EQUIVALENT_INTENT). Source: E01 rows named in the mapping entries.
- **Evidence gaps (none closed by this brief):** order-creating request on SUT-01; commit page on SUT-02; basket checkout route on SUT-05; line-level display of SUT-02 checkout views. Closing a gap means a new evidence record, not an edit of the frozen E01 record (E01 is FROZEN; `manifests/e01-campaign-freeze-v1.yaml`).

### 2.2 Population and conditions

Proposed conditions (one per COMPARABLE SUT x surface x scenario, the E03 rule). Mechanisms are recorded per run, not per condition (`protocol/setup-effort-v2.md`, section 10).

| Condition (proposed id) | SUT | Surface | Scenario | Precondition (counted or not, see section 3.1) | Proposed N |
|---|---|---|---|---|---|
| E02-CS003-SUT01-WEB | SUT-01 | WEB | CS-003 | clean session (counted login under DP-1 of CS-003) | 50 |
| E02-CS003-SUT01-API | SUT-01 | API | CS-003 | clean session | 50 |
| E02-CS003-SUT02-WEB | SUT-02 | WEB | CS-003 | clean session | 50 |
| E02-CS003-SUT03-WEB | SUT-03 | WEB | CS-003 | clean session | 50 |
| E02-CS003-SUT04-WEB | SUT-04 | WEB | CS-003 | clean session | 50 |
| E02-CS003-SUT04-API | SUT-04 | API | CS-003 | clean session | 50 |
| E02-CS003-SUT05-API | SUT-05 | API | CS-003 | clean session | 50 |
| E02-CS004-SUT01-WEB | SUT-01 | WEB | CS-004 | seeded cart and session, not counted | 50 |
| E02-CS004-SUT02-WEB | SUT-02 | WEB | CS-004 | seeded cart and session, not counted | 50 |
| E02-CS004-SUT03-WEB | SUT-03 | WEB | CS-004 | seeded cart and session, not counted | 50 |

- **HD-10 (the set).** Recommended: all 10 above (500 executions). Minimum for H2: the six SUT-01/02/03 WEB conditions. Two-level choice: CS-003 has seven COMPARABLE conditions in total, and CS-004 has three. Specialist conditions (SUT-04, SUT-05) stay EXPLORATORY (`protocol/statistical-analysis-plan-v1.md`, section 4.2).
- **HD-11 (mechanisms).** Recommended: one realization per SUT x surface x scenario, with the establishment mechanism recorded per run (the E03 precedent). The alternative, one condition per mechanism, multiplies conditions and adds unpredeclared comparisons.
- **Mobile suite:** no condition proposed (HD-21). Mapping for ANDROID and IOS would need a new record version (CS-003 DP-4 excluded them).
- **Reuse of E03 realizations.** The reset-side realizations of E03 (`executor/README.md`, section 4) are not reusable as establish-side. Their web and API route notes are reusable as evidence of provisioning routes only.

### 2.3 Pinned SUT versions

- Pins are the E03 values in `experiments/E03-resetability/README.md` ("Pinned SUT versions", from `manifests/sut-manifest.yaml`): SUT-01 web and api `9ca37674d374e9303912e259641ee86baf3aabe1`; SUT-02 web `60fdd634bb111c092282fa07977513a0a7765593`; SUT-03 web `7ab934d733f2f74d4b912e94e86f59ae0f6b7609`; SUT-04 web and api `d36bd3f8647a091d406e53bad463c5e3e5d2ece1` (release 2.2); SUT-05 api `1618a611b173b4bf114028e6e02549950606e29d` (release v20.2.0, packaged distribution, whose tag differs from the pin in one screenshot file, per the E03 README).
- `manifests/sut-manifest.yaml` sets `evaluated_version_frozen: true` for SUT-01 to SUT-05, at the E03 START (2026-10-28). The E02 configuration copies these values. Changing a pin requires change control and re-validation of each mapping that cites it (`protocol/equivalent-scenario-mapping-v1.md`, section 6).

### 2.4 Toolchain

- Web runner: Playwright for Python 1.63.0 with the hash-pinned dependencies in `experiments/E03-resetability/executor/requirements.txt`, `--require-hashes --only-binary :all:`; Chromium as named by that version, observed per run (E03 README, "Toolchain versions").
- API client: Python 3 standard library, observed version per run (E03 README).
- Substrate: GitHub Actions, ubuntu-24.04 hosted runners (and macOS for iOS-simulator conditions, only if a mobile suite is approved). `experiments/README.md` (common rules, "Execution substrate") and the agent-instructions file (CAMPAIGN-CI-WRITE-AUTH-01) name this substrate for E02; `protocol/agent-governance-v5.md`, section 3.6, repeats it.
- Run manifest: `schemas/run-manifest.schema.v2.json` (its sha256 is as recorded in `experiments/E03-resetability/README.md`, "Dispatch procedure prompt, implementation, schema"; not re-typed here). It carries `establishment_mechanisms`, `starting_state_id`, and `target_state_id`, which E02 needs; `actions[].outcome` is required by campaign convention.
- Node.js for SUT builds: 24.21.0 for the SUT-01 web and SUT-04 assets, as provisioned (E03 README and executor README, section 12). Not stated for E02 beyond E03's record.
- Mobile runner: Appium 3, pinned 3.7.0, selected (`manifests/toolchain-manifest.yaml`, `mobile_runner_selection`; the E03 README "Mobile qualification" row). Its compatibility pins are in `manifests/appium3-compat-smoke-preparation-v1.yaml`, not re-read for this brief. Only SUT-02 has a compatibility-smoke record: under APPIUM3-COMPAT-SMOKE-AUTH-02, SUT-02 android PASS and SUT-02 iOS FAIL_RUNNER (E03 README, "Mobile qualification" row); the iOS remediation result is recorded under `protocol/mobile-runner-policy-v3.md`, section 9.7 and its restoration table. The two SUT-02 iOS observations are reported together (same policy, section 9.7). No other SUT has a smoke record.

### 2.5 Dispatch procedure prompt and implementation

- **Prompt.** A new dispatch procedure prompt for E02 is needed. Candidate id: `ORCHESTRATOR-E02-state-establishment-v1` (candidate, not frozen). It is frozen by copy at the START, as the E03 prompt was (`prompts/README.md`, rule 2; E03 README, "Dispatch procedure prompt").
- **Implementation.** A new E02 executor, with its own entry point and its own sha256 lock. The E03 implementation hash (`9662bd5c...`) locks only E03 (E03 README, "Campaign configuration"). New realization rows are needed for each condition, establish-side counting, establish oracle predicates, starting-state checks, and the between-run reset (harness, not counted).

### 2.6 Conditions with environment types

- `protocol/study-design-v1.md`, section 10.3, requires a controlled instance for conditions that involve deterministic reset or state-changing operations, and never a PUBLIC_HOSTED instance. The E02 conditions run a between-run reset and change state that persists (SUT-01 session cart, SUT-04 booking, SUT-05 basket). So the proposed environment_type is SELF_HOSTED on a GitHub-hosted runner, the E03 convention (E03 README, Conditions table).
- **HD-12 (verification).** The E03 verification records are per E03 condition id (`experiments/E03-resetability/controlled-instance-status.yaml`). Option (a): reuse the E03 verified instances by a recorded decision. Option (b): a new ENVIRONMENT_VERIFICATION dispatch per E02 condition id (the E03 precedent: nine verification runs to reach all-VERIFIED, E03 README). Recommendation: (b), using the same provisioning routes, because the verification records are keyed by condition id and the E02 realization differs.

### 2.7 Sample size

- N = 50 per repeatable condition when operationally feasible (`protocol/repeatability-determinism-v1.md`, section 3, "Standard"). N = 30 only for expensive mobile conditions with a justification recorded before execution (same section, "Reduced"). Proposed N = 50 for all ten web and API conditions, which is 500 measured executions, against E03's 350 (E03 README, "Sample size"; dispatched between 2026-10-29T01:26Z and 2026-10-29T16:03Z).
- **HD-13.** Confirm N = 50, or a smaller pre-registered N with a stated reason.

### 2.8 Exclusion and attribution rules

- Proposed: none beyond the frozen discipline, as in E03 (E03 README, "Exclusion and attribution rules"): no run is excluded after the fact; a failed attempt keeps its outcome; attempt 1 is immutable; a further attempt needs its own explicit instruction.
- **HD-14 (starting-state check).** Proposed: if the declared starting state does not hold, the run stops as ABORTED with the cause recorded, as E03 does (`executor/README.md`, section 3, item 11). A starting-state read is a precondition, not counted (setup-effort-v2, section 5, rule 6), so no Required Action enters for it. Confirm.
- Issue (xix), the attribution question, is deferred to E04 and E05 (`protocol/study-design-v1.md`, section 13; `protocol/statistical-analysis-plan-v1.md`, section 6), so no attribution rule is introduced for E02.

### 2.9 CONFIRMATORY list

- H2 pairs (`protocol/statistical-analysis-plan-v1.md`, section 4.3): SUT-01 versus SUT-02 and SUT-01 versus SUT-03, on Required Actions (establish), per COMPARABLE canonical scenario (CS-003, CS-004), paired on the WEB surface. The E03 pairing decision (D2, 2026-10-05, E03 README) applies to E03; **HD-17** asks the human research lead to confirm the same pairing for E02.
- Method (SAP, section 3 and 4.3): paired per-scenario differences, with a Wilcoxon test only where pairing is adequate, otherwise descriptive. Recommendation: descriptive, because "adequate" is undefined in the SAP and two scenarios cannot reach significance (section 1). Changing that rule after data collection starts needs a new SAP version (`protocol/change-control-v1.md`, section 5). **HD-16.**
- Every other comparison (SUT-04, SUT-05, API pairs) is EXPLORATORY (SAP, section 4.2).
- The exact specification (hypothesis, RQ, variable, pair, scenario ids, method, effect size) must be in the configuration before START (SAP, section 4.2).

### 2.10 Dispatch order and authorization

- **Authorization.** Today: each dispatch needs explicit human approval (`protocol/agent-governance-v5.md`, section 3.6, "Dispatch"). The per-SUT dispatch authorization the human research lead intends does not exist: it appears only in v4 section 3.5 for E03. A governance successor (not drafted here) is needed. **HD-18.**
- **Order (proposed; E03 precedent).** Within an assigned SUT, conditions in configuration order; each condition's executions E0001 to E0050 in ascending order, each after the previous run concluded; no cross-SUT order; no decision depending on any measured output (`protocol/agent-governance-v5.md`, section 3.6, "Isolation"). **HD-19.**

## 3. (b) Counting and recording of establish-side Required Actions

### 3.1 The inversion

| Item | E03 (reset side, FROZEN) | E02 (establish side, proposed) |
|---|---|---|
| Counted in `actions[]` | reset-side operations only (executor README, section 3, item 1) | every experimenter-initiated operation with an observable effect from the declared starting state to the target state (`protocol/setup-effort-v2.md`, section 5, rules 1 to 3) |
| Login | in precondition, not counted (CS-001 starts AUTHENTICATED_SESSION) | counted under CLEAN_SESSION (rule 3); not counted under SEEDED (CS-004 DP-1, rule 6) |
| Verification | recorded, not counted (executor README, section 3, item 1) | counted, classified by mechanism (rule 8; human ruling A2, `protocol/setup-effort-v2.md`, section 5) |
| Partial success | outcome recorded, counted once (rule 9, human ruling B1) | same |

The E03 conventions that carry over unchanged as principles: evidence capture is not an action (executor README, section 3, item 4); completion waits are evidence, not actions (item 5); no retry is predeclared (item 6); manual actions carry a reason (rule 5).

### 3.2 Illustration (not a predeclared count)

CS-003, SUT-01, WEB, CLEAN_SESSION (the CS-003 DP-1 choice), from `experiments/scenario-mappings/CS-003.yaml`, mapping entry SUT-01:

| Pos | Operation | Class (setup-effort-v2, section 4) | Mechanism for `establishment_mechanisms` | Counted | Outcome criterion |
|---|---|---|---|---|---|
| 1 | API login with documented account (SUT01-EV-0007) | API action | PREDEFINED_ACCOUNT | yes (rule 3) | HTTP 200 with a token |
| 2 | Inject token and username into client storage (SUT01-EV-0001, SUT01-EV-0002) | state/configuration action | APP_STATE_CONTROL (or OTHER with notes) | yes (rule 1) | storage read-back |
| 3 | Seed one cart line, POST /api/cart (SUT01-EV-0004, SUT01-EV-0005) | API action | API_SEED | yes | HTTP 200 |
| 4 | Open the Checkout route (SUT01-EV-0001) | navigation action | DIRECT_ROUTE | yes | route rendered |
| 5 | Read the Checkout view for the line (SUT01-EV-0004) | UI action (verification) | UI_FLOW | yes (rule 8) | line present in view |
| 6 | Optional: GET /api/session or /api/cart (SUT01-EV-0005) | API action (verification) | API_SEED | if adopted | body contains line |

CS-003 gives "5 or more" for SUT-01 web as indicative; the table gives 5 counted operations without the optional read. These are illustrations of the rule, not predeclared counts.

### 3.3 Outcomes, run status, and duration

- Each action carries `outcome` SUCCESS, PARTIAL_SUCCESS, or FAILURE, decided by the criterion stated for that action (rule 9). A failed attempt does not become a retry unless the same action is performed again (rule 4).
- Run `outcome.status` is distinct from per-action outcome (setup-effort-v2, section 6.3): SUCCESS when the oracle predicate holds after the establish, FAILURE when evaluated and not holding, INCONCLUSIVE, ABORTED (starting state failed, or no action), ERROR (runner fault).
- **Duration (secondary, never combined with the count):** START immediately before the first counted action; STOP when the target state is independently verified (`protocol/setup-effort-v2.md`, section 6.1). The verification that ends the duration is also a counted verification (section 6.1, last paragraph).
- Provisioning is not counted, and the provisioning record is written once per instance (section 8; `manifests/provisioning/`).

### 3.4 Navigation and surface-control rules

E03 fixed a navigation rule and a surface-control rule (executor README, section 3, items 3 and 10) for reset observation. E02 needs their establish-side analogues: whether a page load needed to observe the target is a counted navigation, and whether a documented control is used in preference to an endpoint. **HD-15.** Until decided, the configuration cannot fix the counts for SUT-01 and SUT-02, whose checkout entries are navigations.

### 3.5 Run record

Per run (`protocol/setup-effort-v2.md`, section 9): run manifest with `establishment_mechanisms` (mandatory, non-empty, section 10), `starting_state_id`, `target_state_id`, `scenario`, `condition`, `environment_type`, `actions[]` (class, position, is_retry, outcome, manual_reason when manual), `artifacts[]`, and `notes` (provisioning record reference, per setup-effort-v2 section 8). Verification evidence is captured as evidence, not as an action.

## 4. (c) Reuse and new work

| Area | Reuse from E03 | New for E02 |
|---|---|---|
| Substrate and gates | GitHub Actions model; public repository; fail-closed guards (`ci-cd-execution-model.md`, section 3, items 1 to 11); gate outputs (item 11) | Workflow file with its own name (the E03 one hard-codes `E03-resetability` in G-1, the nine CS-001 condition ids, and G-3's CS-001 and CS-002 checks) |
| Import and isolation | Digest-verified import; per-SUT output isolation (agent-governance-v5, section 3.6) | E02 output path `raw-data/E02-state-establishment/<SUT>/` |
| Dispatch record | One append-only YAML per condition, events appended only (E03 README, "Execution") | Same format under an E02 directory |
| Executor core | `run-condition.sh` pattern; embedded digest list; instance interface v1; scrubber and RFC 1918 redaction; bundle layout; HTTP client; web runner with network logging and bounded settle (executor README, sections 6, 7, 9, 10) | Establish realization rows; establish counting; oracle predicates for checkout-ready, cart, booking, basket; seeding before the starting state; CLEAN and SEEDED starting-state checks |
| Environment verification | Provisioning routes per SUT (`experiments/E03-resetability/controlled-instance-status.yaml` and the verification workflow); SUT-04 route decision | Per E02 condition id; reverification record |
| Schema | `schemas/run-manifest.schema.v2.json` | None needed for the fields listed above (section 2.4) |
| Mobile | Runner selection and compatibility-smoke records | Nothing proposed (HD-21) |
| Analysis | `analysis/h2-analysis/` exists per the E03 README (not read); the H2 reset-side analysis was descriptive | E02 establish-side analysis script (new), following SAP section 3 |

## 5. (d) Gate list for the E02 measured workflow (names only; derived from the E03 gates)

Reused, by the E03 gate that they mirror (`experiments/E03-resetability/ci-cd-execution-model.md`, section 3):

- Guard 1: ref is the default branch and run attempt is 1 (no GitHub re-run).
- G-A: inputs self-consistent (E03 workflow gate step, "G-A").
- G-1: campaign START recorded as IN_PROGRESS in the study manifest, with exactly one `NOT_STARTED -> IN_PROGRESS` change-log row for the E02 README that carries the START authorization id.
- G-2: locked "Campaign configuration" record names the condition, the schema, the prompt version, and the implementation hash (E03 gate 3).
- G-3: each canonical scenario the condition uses is FROZEN; the assigned SUT is COMPARABLE on it for the condition's surface (E03 gate 4, applied to CS-003 and CS-004).
- G-4: no excluded mapping is referenced (CS-002 row, E03 gate 4).
- G-5: run-manifest schema v2 exists with the v2 identifier (E03 gate 5).
- G-6: governance document in force is FROZEN-PRE-DATA or AMENDED, never DRAFT (E03 gate 6; the E02 path reads agent-governance-v5 until a successor exists).
- G-7: mobile runner gate; not used in this proposal.
- G-8: controlled instance recorded CONTROLLED and VERIFIED on GitHub Actions for this condition id, with no reverification flag (E03 gate 8).
- G-9: executor prompt frozen copy exists (E03 gate 9).
- G-10: E02 entry point exists and its sha256 equals the locked hash; embedded digests verified (E03 gate 10).
- G-11: pinned revisions captured as outputs (repository SHA, workflow sha256, configuration sha256, mapping sha256, schema sha256, prompt sha256, governance sha256) (E03 gate 11).

New gates, names only (proposed):

- G-E02-A: dispatch authorization for the assigned SUT exists and is VALID (depends on the governance successor, HD-18).
- G-E02-B: the precondition realization for the condition's precondition_class is locked (CLEAN or SEEDED).
- G-E02-C: the write path is only the assigned SUT's raw-data subtree.
- G-E02-D: the H2 comparison specification (pair, scenario ids, surface, method) is recorded in the configuration.
- G-E02-E: environment_type is controlled (SELF_HOSTED or LOCAL) for every condition with deterministic reset or state change; PUBLIC_HOSTED is refused (`protocol/study-design-v1.md`, section 10.3).
- G-E02-F: the public repository carries the START state (E03 gate reads the public tree; `PUBLIC-EXPORT-MANIFEST.yaml`).

## 6. (e) Stale or missing text in `experiments/E02-state-establishment/README.md`

A START would need these corrected (a README correction under the campaign-status rule, not a change to frozen text).

| # | Current text (quoted or located) | Stale because | Correction |
|---|---|---|---|
| 1 | Objective: "(protocol/setup-effort-v1.md)" | v1 is AMENDED (`protocol/setup-effort-v2.md`, header) | cite v2 |
| 2 | Future IVs, `establishment_mechanisms`: "protocol/setup-effort-v1.md, section 10" | v2 section 10 carries the same vocabulary | cite v2, section 10 |
| 3 | Future IVs: "Target state ... candidate" | CS-003 is FROZEN; CS-004 is DRAFT | state the frozen record required |
| 4 | Future IVs: "Surface ... candidate" | surfaces are mapped in CS-003 (WEB and API for the listed SUTs) | state the mapped surfaces |
| 5 | Future DVs: "six action classes ... setup-effort-v1 section 4 (counting rules are candidate — not frozen)" | v2 sections 4 and 5 are FROZEN-PRE-DATA, rules 1 to 9 | cite v2; remove "candidate" |
| 6 | Required evidence: "schemas/run-manifest.schema.json" (two places) | the E02 version is v2 (`schemas/README.md`; the E03 README) | v2 |
| 7 | Required evidence: "protocol/setup-effort-v1.md, section 8" for provisioning | v2 section 8 | cite v2 |
| 8 | Required evidence: "Verification artifact ... (form TBD before freeze)" | open item | decide the form before START (HD-22) |
| 9 | Required evidence: "Raw observations in raw-data/E02-state-establishment/" | isolation requires the SUT subtree (agent-governance-v5, section 3.6; experiments/README, common rules) | `raw-data/E02-state-establishment/<SUT>/<run_id>/` |
| 10 | Missing: execution path | the README does not say GitHub Actions under CAMPAIGN-CI-WRITE-AUTH-01 (agent-governance-v5, section 3.6; experiments/README, common rules) | add at START |
| 11 | Missing: H2 pairing and the CS-003/CS-004 pair | SAP section 4.3 names E02 for H2 | add at START |
| 12 | Preparation paragraph: "CS-003 ... not yet an input to any configuration" | still true; CS-004 needs a line | add CS-004 status |

## 7. Controlled instances, dispatch, and governance (summary)

- Controlled instance: required for every E02 condition (section 2.6). The E03 verified instances are per E03 condition id. The status file's latest-run rule (E03 README) governs E03 only.
- Dispatch: per dispatch, under agent-governance-v5, section 3.6. The per-SUT authorization needs a successor (HD-18).
- Freeze and START: CS-004 freeze (HD-9), E02 configuration lock and START (`protocol/change-control-v1.md`, section 7, moment 1), and the frozen dispatch prompt each need explicit human approval of that exact action (agent-governance-v5, section 3.6, "Human-gated").

## 8. HUMAN DECISIONS (consolidated)

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| HD-1 | CS-004 target | checkout-ready / committed order or booking | checkout-ready |
| HD-2 | CS-004 precondition (DP-1) | SEEDED / CLEAN | SEEDED (independence) |
| HD-3 | CS-004 oracle (DP-3) | UI_STATE / BUSINESS_STATE | UI_STATE (BUSINESS_STATE makes SUT-02 and SUT-03 NOT_COMPARABLE) |
| HD-4 | CS-004 surfaces (DP-4) | WEB only / WEB and API | WEB only for H2 |
| HD-5 | CS-004 reset (DP-6) | DATA_RESET / NONE | DATA_RESET |
| HD-6 | CS-004 SUT-04 (DP-7) | NOT_COMPARABLE / COMPARABLE by stretch | NOT_COMPARABLE |
| HD-7 | CS-004 SUT-05 (DP-8) | leave pending and exclude / new evidence row / NOT_COMPARABLE | leave pending, exclude for E02 |
| HD-8 | CS-003 discrepancies (SUT-02 oracle not named in DP-3; SUT-04 administrator under "standard") | accept as disclosed by a recorded note / define CS-003-v2 | decide before E02 START; a substantive change needs a new version |
| HD-9 | Freeze CS-004 | freeze / keep DRAFT | after HD-1 to HD-8 |
| HD-10 | E02 condition set | the ten conditions / H2 six only / other | ten; no mobile |
| HD-11 | Mechanisms per condition | one per SUT x surface x scenario / one per mechanism | one, mechanism per run |
| HD-12 | Controlled-instance verification | reuse E03 / new verification per E02 condition | new verification per E02 condition |
| HD-13 | N | 50 / smaller pre-registered N | 50 |
| HD-14 | Starting-state check | not counted, ABORTED on failure / counted | not counted, ABORTED on failure |
| HD-15 | Navigation and surface-control analogues | copy E03 items 3 and 10 / other | decide before lock |
| HD-16 | H2 method | descriptive / Wilcoxon with a defined adequacy threshold (needs SAP successor) | descriptive |
| HD-17 | H2 pairing on WEB | confirm for E02 / other | confirm |
| HD-18 | Dispatch model | governance successor with per-SUT authorization / per-dispatch under v5 | per-SUT, in a successor drafted and approved separately |
| HD-19 | Dispatch order | configuration order within SUT / other | configuration order |
| HD-20 | E02 workflow file | new file / reuse E03 file with parameters | new file (G-1 is hard-coded to E03) |
| HD-21 | Mobile suite | none in this proposal / mapping for ANDROID and IOS and smoke per SUT x platform x runner | none in this proposal |
| HD-22 | Verification-artifact form and START date and authorization id | decide | decide before START |
| HD-23 | Reading of the adjudicated matrix (section 0, item 2) | confirm / withdraw | confirm |

## 9. Open gaps (not closed by this brief)

1. E01 rows absent for: SUT-01 order-creating request; SUT-02 commit page and line-level checkout display; SUT-05 basket checkout route; SUT-05 web checkout entry.
2. CS-003 and CS-004 do not map mobile surfaces for any SUT.
3. SUT-05 has no CS-004 comparability decision (HD-7).
4. The E02 governance successor (HD-18) and the E02 dispatch prompt are not drafted.
5. The H2 adequacy term is undefined (HD-16).
6. The "navigation rule" and "surface-control rule" analogues are not decided (HD-15).
