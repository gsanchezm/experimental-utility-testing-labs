# Study Design

| Field | Value |
|---|---|
| Document | protocol/study-design-v1.md |
| Protocol version | v1 |
| Protocol state | FROZEN-PRE-DATA |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | first iteration instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT); second iteration (issues (x), (xi), (xx), explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT); final pre-freeze checklist closure (step-3 freeze-checklist items, explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |

## 1. Study concept

Working concept: **Experimental Utility of Software-Testing Laboratory Ecosystems**.

The study evaluates whether software-testing laboratory ecosystems provide experimentally useful, controllable, repeatable, observable, and integrated conditions for modern software-testing research and practice.

Informally, *experimental utility* is the usefulness of an ecosystem as a controlled experimental instrument for testing research and practice. It is distinct from the mere existence of an application that can be tested. An application that runs and accepts a test tool is not, by that fact alone, an experimental instrument; utility depends on whether target conditions can be established, reset, observed, and reproduced on demand, and whether their expected outcomes are known in advance.

Study identifier: EUS-2026-001 is an internal study identifier assigned at repository initialization. It is not a registration number with any external registry and carries no meaning beyond identifying this study in this repository and its outputs.

Purpose of this document: fix the unit of comparison, the evaluated ecosystems, the primary construct and its dimensions, the research questions, the provisional hypotheses, the modality list, the ground-truth rule, the mapping from experimental campaigns to research questions, the environment-provenance rules, the interpretation rules, and the register of open methodological issues, before any data is collected.

## 2. Unit of comparison

The unit of comparison is the **testing laboratory ecosystem**, not an individual repository.

- An ecosystem may consist of several repositories, releases, hosted deployments, or platform-specific artifacts (Web, Android, iOS, API). All of these together form one unit. SUT-02 (Sauce Labs Demo Ecosystem) is the canonical example: any separate Web, Android, or iOS repositories or artifacts it may comprise are treated as one ecosystem.
- The component repositories, releases, and deployment targets that constitute each ecosystem are recorded in manifests/sut-manifest.yaml. At initialization all provenance fields there are null; they are filled by the ORCHESTRATOR when the evaluated version of each ecosystem is pinned before E01 starts (sequence defined in manifests/README.md), never here and never by guess.
- Every comparison, evidence record, and campaign result is keyed by ecosystem id (SUT-01 … SUT-06), never by repository.

## 3. Evaluated ecosystems

SUT = system under test. Six ecosystems are evaluated.

| SUT id | Ecosystem name | Role | Role class | Audit directory |
|---|---|---|---|---|
| SUT-01 | OmniPizza | general-purpose candidate | candidate | audits/SUT-01-omnipizza |
| SUT-02 | Sauce Labs Demo Ecosystem | general-purpose baseline | general-purpose baseline | audits/SUT-02-saucelabs |
| SUT-03 | BrowserStack Demo Ecosystem | general-purpose / Web / API baseline | general-purpose baseline | audits/SUT-03-browserstack |
| SUT-04 | Restful Booker Platform | Web/API specialist baseline | specialist baseline (contextual / specialist reference) | audits/SUT-04-restful-booker |
| SUT-05 | OWASP Juice Shop | security specialist baseline | specialist baseline (contextual / specialist reference) | audits/SUT-05-juice-shop |
| SUT-06 | WebdriverIO Native Demo App | mobile specialist baseline | specialist baseline (contextual / specialist reference) | audits/SUT-06-webdriverio |

OmniPizza (SUT-01) is the candidate ecosystem whose evaluation motivates the study. It is evaluated under exactly the same rules, rubric, evidence requirements, and campaigns as every other SUT. OmniPizza is one evaluated SUT, not the experimental framework. The design must not be architected to favor it, and it receives no privileged interpretation in scoring, evidence assessment, or analysis. Any procedure that would apply differently to SUT-01 than to SUT-02 … SUT-06 is a protocol defect and must be corrected before freeze.

The role class determines only how a between-ecosystem comparison is classified in protocol/statistical-analysis-plan-v1.md (CONFIRMATORY for the pre-registered candidate-versus-general-purpose-baseline comparisons, EXPLORATORY otherwise unless a comparison is explicitly pre-registered as confirmatory before the campaign begins; Section 6, note (d)). It has no effect on how an ecosystem is audited, scored, executed, or reported.

No audit has been performed. No capability score, result, or ranking exists for any SUT.

## 4. Primary research construct

The primary construct is **Experimental Utility**, treated as a **multidimensional profile**. There is no single weighted Experimental Utility Score, and none may be defined in this or any later protocol version. Ecosystems are compared dimension by dimension; a profile is reported, not a total.

Dimensions (exact names, exact order):

1. Experimental Breadth
2. Experimental Controllability
3. Repeatability and Determinism
4. Cross-platform and Cross-layer Integration
5. Observability and Automation Affordances
6. Setup Effort

The dimension set may evolve only through explicit protocol versioning under protocol/change-control-v1.md. Adding, removing, renaming, or reordering a dimension requires a new version of this document.

Dimension-to-RQ and dimension-to-campaign mapping (campaign-level detail in Section 9):

| Dimension | Informing RQ(s) | Informing campaign(s) |
|---|---|---|
| Experimental Breadth | RQ1; RQ5 (non-functional breadth) | E01, E12; E08–E11 |
| Experimental Controllability | RQ2; RQ5 (ground-truth condition control) | E02, E03; E08–E11 |
| Repeatability and Determinism | RQ3 | E04, E05 |
| Cross-platform and Cross-layer Integration | RQ4 | E06, E07; E12 (secondary, locale parity) |
| Observability and Automation Affordances | RQ2 (descriptive component; not quantified at protocol v1) | E01 (primary, through the Observability and Automation Affordances cross-cutting properties in protocol/cross-cutting-properties-v1.md); informed cross-cuttingly by all campaigns |
| Setup Effort | RQ2 (per-run / per-condition setup; protocol/setup-effort-v1.md) | E02, E03 |

## 5. Research questions

RQ1 — Experimental Breadth
To what extent do software-testing laboratory ecosystems support experimentally usable and controllable conditions across functional and non-functional testing modalities?

STATUS: PROVISIONAL — PRE-DATA-COLLECTION

RQ2 — Controllability, Observability, Automation Affordances, and Setup Effort
To what extent, and in what respects, do software-testing laboratory ecosystems differ in state controllability, resetability, observability, automation affordances, and the effort required to establish and reset target test states?

STATUS: PROVISIONAL — PRE-DATA-COLLECTION

RQ3 — Repeatability and Determinism
How repeatable and deterministic are equivalent experimental conditions under repeated executions within each testing laboratory ecosystem?

STATUS: PROVISIONAL — PRE-DATA-COLLECTION

RQ4 — Cross-platform and Cross-layer Integration
To what extent can equivalent experimental states and scenarios be preserved across Web, API, Android, and iOS surfaces?

STATUS: PROVISIONAL — PRE-DATA-COLLECTION

RQ5 — Controlled Non-functional Experimentation
To what extent do testing laboratory ecosystems provide known, reproducible ground-truth conditions for performance, accessibility, visual, and security testing?

STATUS: PROVISIONAL — PRE-DATA-COLLECTION

Notes on the research questions:

- RQ2 was revised during the pre-freeze hardening iteration of 2026-09-15 (before any data collection) so that Dimension 5, Observability and Automation Affordances, has an explicit research-question connection. The observability and automation-affordance components of RQ2 are answered descriptively from the E01 cross-cutting property descriptions (protocol/cross-cutting-properties-v1.md); no score, weight, or metric is attached to them at protocol v1. The controllability, resetability, and setup-effort components are answered by E02 and E03 under protocol/setup-effort-v1.md.
- The number of research questions is five. No research question is dedicated to Localization / i18n; that modality is covered by RQ1 (capability level, E01; controllability of locale conditions, E12) and RQ4 (cross-platform locale parity, E12). See Section 9 and Section 11.

Research questions must not silently change after data collection begins. Any change to the wording, scope, or number of research questions follows protocol/change-control-v1.md and produces a new version of this document.

## 6. Provisional hypotheses

STATUS: PROVISIONAL — PRE-DATA-COLLECTION

H1:
OmniPizza will expose a greater number of testing modalities at the experimentally controllable level than the general-purpose baselines.

H2:
OmniPizza will require fewer preparation/reset actions to establish equivalent target states than the general-purpose baselines.

H3 — Determinism:
For OmniPizza conditions classified a priori as deterministic, every valid measured execution that successfully establishes the frozen target state will produce the same predefined expected categorical outcome (Conditional Exact Outcome Rate = 1.00 and Outcome Entropy H(Y) = 0).

H4:
OmniPizza will provide greater cross-platform scenario parity and cross-layer state continuity than the general-purpose baselines.

H5:
OmniPizza will expose a greater number of controlled non-functional ground-truth conditions than the general-purpose baselines.

Notes on the hypotheses:

- (a) Specialist baselines are NOT expected to be weaker than OmniPizza in their specialty. For example, OWASP Juice Shop (SUT-05) may provide deeper security experimentation than OmniPizza; Restful Booker Platform (SUT-04) may provide deeper Web/API experimentation; WebdriverIO Native Demo App (SUT-06) may provide deeper mobile experimentation. H1–H5 make no prediction about specialist baselines.
- (b) The study must allow results that contradict any hypothesis. Campaign procedures, evidence rules, and the analysis plan are designed so that a contradicting result is recorded and reported with the same weight as a confirming one.
- (c) Hypotheses are pre-registered directional predictions. They carry no evidential weight. No hypothesis has been tested. They are not expectations of the study team and are not findings. "General-purpose baselines" refers to SUT-02 (Sauce Labs Demo Ecosystem) and SUT-03 (BrowserStack Demo Ecosystem) only.
- (d) H1, H2, H4, and H5 define the pairwise CONFIRMATORY comparison set: SUT-01 versus SUT-02 and SUT-01 versus SUT-03, on equivalent conditions or scenarios, for the variables each hypothesis names. H3 is a single-ecosystem pre-registered prediction about SUT-01 and defines no between-ecosystem comparison; the quantities it concerns (Conditional Exact Outcome Rate and Outcome Entropy, protocol/repeatability-determinism-v1.md, section 4, with their intervals) are computed and reported identically for every ecosystem's conditions classified a priori as deterministic, and only the H3 label is specific to SUT-01. Every other between-ecosystem comparison, including every comparison involving a specialist baseline, is EXPLORATORY unless it is explicitly pre-registered as confirmatory before the associated campaign begins. The classification rule, the mapping from each hypothesis to its comparisons, and the reporting rules are defined in protocol/statistical-analysis-plan-v1.md, section 4. Specialist baselines are not removed from any campaign or table by this classification; they remain positive-control / depth references in their specialty, a design role that states intent, not a finding.
- (e) H3 (resolved by explicit human decision, 2026-09-16; Section 13, issue (xx)) replaces the earlier undefined phrase "high exact-outcome reproducibility" with an explicit, checkable criterion: Conditional Exact Outcome Rate (CEOR) = 1.00 and Outcome Entropy H(Y) = 0 (protocol/repeatability-determinism-v1.md, section 4), for conditions classified a priori as deterministic — meaning the behavior class declared before execution and locked in the campaign configuration at campaign start (protocol/repeatability-determinism-v1.md, section 2; protocol/change-control-v1.md, section 7). H3 does not claim that every OmniPizza condition is deterministic; stochastic, time-dependent, and external-dependency conditions are classified separately and excluded from H3 testing. Target-State Reproduction Rate (TSRR) and End-to-End Reproducible Outcome Rate (E2E-ROR) are still computed and reported for the same conditions but are not the primary H3 determinism criteria. One valid unexpected categorical outcome on a condition that successfully established its target state means that condition does not satisfy the preregistered H3 criterion.

## 7. Testing modalities

Frozen initial modality list (exact names, exact order):

1. Web UI Functional
2. API
3. Android Native
4. iOS Native
5. Performance
6. Accessibility — Web only
7. Visual Testing
8. Security Testing
9. Localization / i18n

The list is frozen at protocol v1. Adding, removing, renaming, or reordering a modality requires a new protocol version under protocol/change-control-v1.md.

Manual and exploratory testing may be discussed descriptively but must not contribute to the quantitative primary comparison.

Each modality is scored per ecosystem using the capability rubric in protocol/capability-rubric-v1.md (Score 0 — UNSUPPORTED; Score 1 — TECHNICALLY EXECUTABLE; Score 2 — EXPERIMENTALLY USABLE; Score 3 — EXPERIMENTALLY CONTROLLABLE). Scores are assigned only during E01-capability-audit, by the roles permitted to do so under protocol/agent-governance-v1.md, never in this document.

Structural absence of a surface is scored 0, not N/A. When an ecosystem structurally lacks the surface a modality requires (for example a mobile-only ecosystem with no Web surface, for which Accessibility — Web only is Score 0), the score 0 is valid and means that the ecosystem does not provide that experimental modality. It must not be read as evidence that the ecosystem is poor within its intended specialty. Such a cell carries a descriptive `structural_scope_note` (protocol/capability-rubric-v1.md; protocol/evidence-rules-v1.md) stating the structural reason. The note never modifies the score, and the rubric has no N/A level. How such cells are interpreted is fixed in Section 11.

## 8. Ground truth rule

Ground truth means that the experimental condition and expected observable outcome are known before the testing instrument is executed.

Examples:

```
known accessibility violation -> scanner -> detected / not detected
known vulnerable authorization condition -> security verification -> detected / not detected
known degraded performance condition -> performance measurement -> measurable expected degradation
known visual perturbation -> screenshot comparison -> expected difference detected
```

Ground truth must be separated from generic tool compatibility. Merely being able to point a generic tool at an application is not ground truth; it demonstrates only that the tool runs (capability rubric Score 1 — TECHNICALLY EXECUTABLE). Ground truth requires that the ecosystem lets the experimenter establish a known condition with a known expected outcome (capability rubric Score 3 — EXPERIMENTALLY CONTROLLABLE). See protocol/capability-rubric-v1.md for the level definitions.

## 9. Campaign mapping

Campaign directories live under experiments/. All campaigns have status NOT_STARTED.

| Campaign | Primary RQ | Secondary RQ | Dimension(s) |
|---|---|---|---|
| E01-capability-audit | RQ1 (feeds all RQs) | RQ2 (descriptive: Observability and Automation Affordances cross-cutting properties) | Experimental Breadth; Observability and Automation Affordances (descriptive); baseline evidence for all dimensions |
| E02-state-establishment | RQ2 | — | Experimental Controllability; Setup Effort |
| E03-resetability | RQ2 | — | Experimental Controllability; Setup Effort |
| E04-repeatability | RQ3 | — | Repeatability and Determinism |
| E05-determinism | RQ3 | — | Repeatability and Determinism |
| E06-cross-platform-parity | RQ4 | — | Cross-platform and Cross-layer Integration |
| E07-cross-layer-continuity | RQ4 | — | Cross-platform and Cross-layer Integration |
| E08-performance | RQ5 | — | Experimental Breadth; Experimental Controllability |
| E09-accessibility | RQ5 | — | Experimental Breadth; Experimental Controllability |
| E10-visual | RQ5 | — | Experimental Breadth; Experimental Controllability |
| E11-security | RQ5 | — | Experimental Breadth; Experimental Controllability |
| E12-localization-i18n | RQ1 (Experimental Breadth: controllability of selected locale conditions) | RQ4 (cross-platform locale parity) | Experimental Breadth; Cross-platform and Cross-layer Integration |

Localization / i18n is evaluated in two distinct evidence layers:

- E01 assigns the Localization / i18n capability level (Score 0, 1, 2, or 3) under protocol/capability-rubric-v1.md. This is the RQ1 breadth cell for that modality.
- E12 experimentally evaluates selected localization / i18n conditions (explicit locale or market selection, expected locale-dependent observable outcomes, and, where more than one surface exists, cross-platform locale parity). E12 contributes primarily to RQ1 (Experimental Breadth / controllability of the locale condition) and to RQ4 (Cross-platform and Cross-layer Integration).

The E01 capability level and the E12 experimental observations are different evidence layers. They are never summed, averaged, or counted twice in any aggregate measure or in any count of modalities per level; the reporting rule is in protocol/statistical-analysis-plan-v1.md, section 5. No global aggregate Experimental Utility Score exists. No research question is created solely for localization.

Repetition targets for E04 and E05 are set in protocol/repeatability-determinism-v1.md. Cross-ecosystem scenario equivalence for E02–E07 is governed by protocol/equivalent-scenario-mapping-v1.md.

## 10. Environment provenance and experimental control

Local deployability and self-hosting are NOT part of the Experimental Utility construct. No dimension, rubric level, or campaign variable awards capability because an ecosystem can run locally, and none penalizes an ecosystem because it is hosted. The environment in which an observation was made is provenance, recorded so that the observation is interpretable and reproducible, and the choice of environment for a campaign is an experimental-control decision.

### 10.1 Environment types

Every experimental run, E01 execution verification, provisioning record, and tool-qualification record classifies its environment with exactly one `environment_type`:

| environment_type | Definition |
|---|---|
| PUBLIC_HOSTED | An instance operated by the ecosystem's vendor or maintainers, reachable publicly, shared with other users, and not controlled by the study. |
| SELF_HOSTED | An instance of the pinned evaluated version deployed by the study on infrastructure under the study's control (server, container host, or cloud account). |
| LOCAL | An instance of the pinned evaluated version running on the operator's workstation. |
| EMULATED | An Android application build of the pinned evaluated version executing in an Android emulator under the study's control. |
| SIMULATED | An iOS application build of the pinned evaluated version executing in an iOS Simulator under the study's control. |
| OTHER | Any environment not covered above; the record's notes must describe it and state whether the study controls it. |

SELF_HOSTED, LOCAL, EMULATED, and SIMULATED are *controlled* environments. PUBLIC_HOSTED is *uncontrolled*. OTHER is uncontrolled unless the record states otherwise with justification. A *controlled instance* of an ecosystem, for a given condition, is the set of components whose state that condition acts on, each running in a controlled environment: SELF_HOSTED or LOCAL for service components (web, api), EMULATED or SIMULATED for mobile application builds (android, ios). A mobile build in an emulator whose backend is PUBLIC_HOSTED is therefore not a controlled instance for a condition that acts on backend state, but is one for a condition that acts only on in-app state. A run that touches components in different environments records the environment type of the surface it exercises and, per component, the environment type of each component it touched (schemas/run-manifest.schema.json).

### 10.2 Capability auditing (E01)

Capability auditing may use, for any ecosystem: official documentation; source inspection at the pinned version; public hosted deployments; and controlled local execution when necessary. Use of a PUBLIC_HOSTED instance during auditing is limited to non-destructive, session-scoped interactions within the instance's documented or intended use (for example logging in with a documented test account or reading a documented endpoint). No fault activation, active security testing, load, or state change visible to other users is performed against a PUBLIC_HOSTED instance under any circumstances. Every EXECUTION_VERIFIED evidence record links to an execution verification record that carries the `environment_type` (protocol/evidence-rules-v1.md).

### 10.3 Experimental campaigns (E02–E12)

Conditions that require any of the following are executed on a controlled instance when an open-source deployment of the evaluated version is available:

- deterministic reset;
- intentional fault activation;
- active security testing;
- significant load;
- destructive or state-changing operations (state visible to other users of a shared instance, or state persisting beyond the experimenter's own session).

Such conditions are never executed against a PUBLIC_HOSTED instance. When no controlled instance can be established for an ecosystem (for example a closed-source hosted component with no deployable artifact), the affected conditions are recorded, per condition, as NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE in the campaign configuration (protocol/change-control-v1.md, section 7) and are reported as "no data" with that reason (protocol/statistical-analysis-plan-v1.md, section 5). This outcome is an experimental-control fact, not a capability score and not a failure of the ecosystem.

Conditions outside that list may be executed against a PUBLIC_HOSTED instance, with `environment_type` recorded on every run and shared-instance interference disclosed as a limitation of the affected measurements. Whether a given condition is executed on a controlled or an uncontrolled instance is fixed per condition in the campaign configuration before the campaign starts and is the same decision rule for every ecosystem.

### 10.4 Evidence ceiling

For a closed-source or hosted-only component, SOURCE_VERIFIED evidence may be unobtainable. An ecosystem is not penalized solely because SOURCE_VERIFIED evidence is unavailable for such a component: its evidence status simply reflects the strongest evidence actually obtainable (DOCUMENTED or EXECUTION_VERIFIED), the capability score is decided by what the evaluated version exposes, and the limitation is recorded in audits/<SUT>/limitations.md (protocol/evidence-rules-v1.md).

### 10.5 Recording

`environment_type` is a required field of every run manifest (schemas/run-manifest.schema.json), every E01 execution verification record (protocol/evidence-rules-v1.md), every provisioning record (protocol/setup-effort-v1.md), and every tool-qualification record (protocol/mobile-runner-policy-v1.md). `controlled_instance_available` in manifests/sut-manifest.yaml is a per-ecosystem fact verified in E01 and transcribed by the ORCHESTRATOR: true when every component surface that E01 confirmed present can be run by the study, from the pinned evaluated version, in a controlled environment (SELF_HOSTED or LOCAL for web and api service components; EMULATED or SIMULATED for android and ios application builds); false otherwise, naming the components that cannot in the manifest notes. It is null until verified and is never inferred. Which conditions can then run on a controlled instance is decided per condition in the campaign configuration (Section 10.3), by the same rule for every ecosystem; the boolean summarizes, it does not decide.

## 11. Interpretation rules

These rules bind every audit, adjudication, analysis, and report of this study.

1. **Experimental Breadth and Modality Depth answer different questions.** Breadth is the number of modalities an ecosystem supports and at which rubric level (the E01 matrix, RQ1). Depth is how controllable, resettable, repeatable, observable, and integrable the ecosystem is within a modality (E02–E12 and the cross-cutting properties, RQ2–RQ5). A specialist SUT may legitimately have low breadth and high depth in its intended modality.
2. **Unsupported modalities remain visible.** A Score 0 cell is reported in the capability matrix as 0, together with its `structural_scope_note` where one exists. It is never hidden, converted to N/A, dropped from a table, or removed from the profile.
3. **Specialist ecosystems are not removed.** SUT-04, SUT-05, and SUT-06 remain in every campaign and every table in which their modalities apply. They serve as positive-control / depth references in their specialty (protocol/statistical-analysis-plan-v1.md); that role is a design intent, and whether an ecosystem actually shows depth is an empirical result.
4. **No overall winner is computed.** No ranking of ecosystems across dimensions is produced, stated, or implied.
5. **No weighted global Experimental Utility Score is used.** None exists at protocol v1 and none may be introduced without a new protocol version, which this document does not anticipate.
6. **Conclusions are dimension-specific.** Every statement about an ecosystem names the dimension, and within Experimental Breadth the modality or condition, to which it refers. A statement that pools dimensions is not a reportable conclusion.
7. **Conceptual illustration (not a finding; no evidence exists).** OWASP Juice Shop (SUT-05) may demonstrate deeper controlled security experimentation while providing narrower cross-platform breadth. If observed, both facts are reported side by side in their respective dimensions. This is not a methodological contradiction; it is the expected shape of a per-dimension profile. The same holds for any other ecosystem, including SUT-01.
8. **Evidence layers are not summed.** An E01 capability level and a later campaign observation about the same modality are different evidence layers (Section 9, Localization / i18n being the explicit case). No aggregate counts a capability twice.
9. **NOT_COMPARABLE is not a capability score.** When no defensible semantic equivalent of a canonical scenario exists for an ecosystem (protocol/equivalent-scenario-mapping-v1.md), the scenario is marked NOT_COMPARABLE for that ecosystem; it is excluded from inferential comparison on that scenario only, the exclusion is reported with its reason, and no artificial comparison is forced.
10. **Environment is provenance, not utility.** Section 10 applies: no dimension rewards local deployability, and no ecosystem is penalized for an evidence ceiling caused by closed-source hosting.
11. **Provisioning is not setup effort.** One-time provisioning is recorded descriptively; the primary Setup Effort metric counts per-run / per-condition setup only (protocol/setup-effort-v1.md).

## 12. Related protocol documents

- protocol/capability-rubric-v1.md — defines the four-level capability scale (Score 0–3) used to score each modality per ecosystem, and the `structural_scope_note` annotation.
- protocol/cross-cutting-properties-v1.md — defines the eight cross-cutting properties (State Controllability; Resetability; Determinism; Observability; Automation Affordances; Cross-platform Scenario Parity; Cross-layer State Continuity; Functional Complexity) assessed across modalities.
- protocol/setup-effort-v1.md — defines how per-run / per-condition preparation and reset effort (Dimension 6, RQ2) is recorded, and how one-time provisioning is recorded separately.
- protocol/repeatability-determinism-v1.md — defines repetition targets (N = 50 per repeatable condition when operationally feasible; N = 30 for expensive mobile conditions if justified and recorded before executing that campaign) and determinism procedures for RQ3.
- protocol/statistical-analysis-plan-v1.md — defines the pre-registered analysis: per-condition repetitions as the inferential unit within ecosystems, CONFIRMATORY versus EXPLORATORY classification of between-ecosystem comparisons, descriptive per-dimension profiles.
- protocol/equivalent-scenario-mapping-v1.md — defines semantic equivalence of cross-ecosystem scenarios, the canonical experimental intent record, the NOT_COMPARABLE marker, and the mapping-record template that must be frozen before E02–E07 execution.
- protocol/mobile-runner-policy-v1.md — defines the mobile runner candidates, the fallback, the qualification gate (MQ1, MQ2, MQ3; pass criteria; qualification SUT), and the per-SUT compatibility smoke.
- protocol/evidence-rules-v1.md — defines evidence statuses (DOCUMENTED, SOURCE_VERIFIED, EXECUTION_VERIFIED, INFERRED), the evidence record fields including `evidence_id`, and the execution verification record for E01.
- protocol/change-control-v1.md — defines the protocol state lifecycle (DRAFT, FROZEN-PRE-DATA, AMENDED, SUPERSEDED), the versioning rule, and the distinction between protocol freeze and campaign freeze.
- protocol/agent-governance-v1.md — defines agent roles (ORCHESTRATOR, six AUDITOR roles, ADJUDICATOR-EU-01, QUALIFIER-MOBILE-01) and their write permissions.

## 13. Open-Issue Register

This register lists every methodological issue recorded during repository initialization (issues i–xvii) and every methodological issue surfaced by the pre-freeze hardening iteration of 2026-09-15 (issues xviii–xx). The second pre-freeze hardening iteration of 2026-09-16 resolved issues (x), (xi), and (xx) by explicit human decision recorded below; it surfaced no new methodological issue. The final pre-freeze checklist closure of 2026-09-16, also by explicit human decision, resolved or explicitly deferred (to campaign configuration) the remaining step-3 freeze-checklist items under protocol/ and schemas/ — including the capability-rubric tie-break rule, the Setup Effort Duration start/stop boundaries, the one-time provisioning record location, the equivalent-scenario-mapping controlled vocabulary, the bootstrap variant and resample count, the paired effect-size choice, the run-id-adjacent target_state_id convention, the JSON Schema validator, and the establishment/reset mechanism vocabulary — without surfacing a new methodological issue for this register; the run-id format itself (raw-data/README.md) remains outside protocol/ and schemas/ and so outside step 3's scope. Allowed status values: RESOLVED (the resolution is written into the named protocol files); OPEN (must be decided before protocol freeze); DEFERRED-BEFORE-CAMPAIGN (explicitly deferred, with the reason, to the configuration of the named campaign(s) under protocol/change-control-v1.md, section 7). No issue is removed from this register; a resolved issue keeps its row. Remaining parameter and tooling choices marked "TBD before freeze" or "candidate — not frozen" inside individual protocol documents (for example the supplementary-risk-ratio pre-registration and the exact Ajv version, both deferred to campaign or pre-run configuration by design) are tracked in those documents and by step 3 of the freeze checklist in protocol/change-control-v1.md, section 6, which requires each of them to be resolved or explicitly deferred before freeze; they appear here only when they are methodological blockers.

| issue_id | description | status | resolution | protocol_files_affected | requires_human_decision |
|---|---|---|---|---|---|
| (i) | How to record a modality that is out of an ecosystem's intentional scope (e.g. "Accessibility — Web only" for a mobile-only specialist) without penalizing intentional narrowness, given that the rubric has no N/A level and the frozen rubric must not be altered silently. | RESOLVED | Score 0 remains valid and is not replaced by N/A. A descriptive `structural_scope_note` annotation (no Web surface; no mobile surface; no API surface; intentionally specialist scope; other structural reason) accompanies such cells in the audit, the evidence record, and the audit schema. Interpretation rules (Section 11): breadth and depth answer different questions; unsupported modalities stay visible; no weighted global score. | protocol/study-design-v1.md; protocol/capability-rubric-v1.md; protocol/evidence-rules-v1.md; protocol/statistical-analysis-plan-v1.md; schemas/evidence.schema.json; schemas/sut-audit.schema.json; audits/README.md; audits/*/audit.md; audits/*/limitations.md; analysis/README.md | no |
| (ii) | Whether each ecosystem is evaluated in a self-hosted deployment, a vendor-hosted public deployment, or both, and how shared public instances affect resetability and determinism measurements. | RESOLVED | Section 10: `environment_type` (PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, OTHER) is recorded on every run and verification. Auditing may use documentation, source, public hosted deployments, and controlled local execution. Conditions requiring deterministic reset, fault activation, active security testing, significant load, or destructive/state-changing operations use a controlled instance when an open-source deployment is available and are never run against a PUBLIC_HOSTED instance; otherwise they are NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE, reported as "no data" with reason. Environment is an experimental-control decision, not a utility score. `deployment_mode` is replaced by `environment_type` (runs, verifications) and `controlled_instance_available` (manifest, verified in E01). | protocol/study-design-v1.md; protocol/evidence-rules-v1.md; protocol/capability-rubric-v1.md; protocol/repeatability-determinism-v1.md; schemas/run-manifest.schema.json; schemas/sut-audit.schema.json; manifests/sut-manifest.yaml; manifests/README.md; experiments/README.md; audits/README.md; audits/*/audit.md; audits/*/limitations.md | no |
| (iii) | SOURCE_VERIFIED evidence may be unobtainable for hosted-only or closed-source components, so the evidence rules need an explicit handling for ecosystems where only DOCUMENTED and EXECUTION_VERIFIED are possible. | RESOLVED | Section 10.4 and protocol/evidence-rules-v1.md: the evidence status reflects the strongest evidence actually obtainable; the score is decided by what the evaluated version exposes; no penalty; the limitation is recorded in limitations.md and in the record's notes. | protocol/study-design-v1.md; protocol/evidence-rules-v1.md; protocol/capability-rubric-v1.md | no |
| (iv) | Localization / i18n is a frozen modality but is not named in RQ5; its RQ mapping is provisional. | RESOLVED | Section 9: no research question is created for localization. E01 assigns the Localization / i18n capability level (RQ1). E12 experimentally evaluates selected localization / i18n conditions and contributes primarily to RQ1 and RQ4. The mapping is no longer provisional. | protocol/study-design-v1.md; protocol/statistical-analysis-plan-v1.md; experiments/README.md; experiments/E12-localization-i18n/README.md | no |
| (v) | Dimension 5 (Observability and Automation Affordances) has no dedicated RQ and is informed cross-cuttingly. | RESOLVED | RQ2 revised conservatively to "Controllability, Observability, Automation Affordances, and Setup Effort" (Section 5). Dimension 5 is answered descriptively under RQ2 from the E01 cross-cutting property descriptions; RQ count remains five. | protocol/study-design-v1.md; protocol/cross-cutting-properties-v1.md; protocol/setup-effort-v1.md; manifests/study-manifest.yaml; experiments/README.md; experiments/E01-capability-audit/README.md; experiments/E02-state-establishment/README.md; experiments/E03-resetability/README.md; protocol/README.md | no |
| (vi) | "Equivalent target state" across ecosystems (RQ2, RQ4) needs an operational equivalence definition before E02/E06 can be frozen. | RESOLVED | protocol/equivalent-scenario-mapping-v1.md created: equivalence is semantic (canonical experimental intent: canonical_scenario_id, precondition_class, actor_state, business_intent, target_state_or_transition, observable_oracle_class, reset_requirement, applicable_surfaces, allowed_domain_mapping), not implementation equivalence; NOT_COMPARABLE marker; mapping-record template; every scenario used for inferential comparison must have a frozen mapping record before E02–E07 execution. | protocol/equivalent-scenario-mapping-v1.md (new); protocol/study-design-v1.md; protocol/statistical-analysis-plan-v1.md; protocol/setup-effort-v1.md; protocol/cross-cutting-properties-v1.md; protocol/change-control-v1.md; experiments/README.md; experiments/E02–E07 READMEs; AGENT-INSTRUCTIONS.md | no (each mapping record later requires human approval at its freeze) |
| (vii) | The small number of ecosystems (6) limits between-ecosystem inferential statistics; the analysis plan treats per-condition repetitions as the inferential unit within ecosystems and descriptive comparison between ecosystems. | RESOLVED | Accepted as a design limitation and disclosed in reporting. protocol/statistical-analysis-plan-v1.md, section 4: the inferential unit is the repetition within a condition; between-ecosystem inference is limited to pre-registered CONFIRMATORY pairwise comparisons on equivalent conditions (SUT-01 versus each general-purpose baseline) and interval-based descriptive comparison; all other comparisons are EXPLORATORY unless explicitly pre-registered as confirmatory before the campaign begins; no omnibus test across six ecosystems. | protocol/statistical-analysis-plan-v1.md; protocol/study-design-v1.md | no |
| (viii) | The qualification scenario labels in protocol/mobile-runner-policy-v1.md (MQ2 "Product/Pizza interaction", MQ3 "Atomic-style mobile testing") are inherited verbatim from the study brief and use vocabulary resembling one evaluated ecosystem's product domain; whether to neutralize the labels, and which app is used for runner qualification, must be decided and recorded before freeze. | RESOLVED | Labels neutralized: MQ1 Login → Catalog (navigation and selector compatibility); MQ2 Catalog → Product Interaction (native control interaction); MQ3 API State Seed → Deep Link → Target UI State (direct controlled mobile state establishment). "Atomic-style" terminology removed; Atomic Helix Model and Atomic Testing are not research subjects of this study. Qualification SUT: OmniPizza (SUT-01) on Android emulator and iOS Simulator, with the explicit statement that qualification runs produce no evidence, familiarity advantage, or privileged interpretation for that ecosystem, disclosed as a study limitation. | protocol/mobile-runner-policy-v1.md; protocol/study-design-v1.md; qualification/README.md; qualification/mobilewright/README.md; manifests/toolchain-manifest.yaml | no |
| (ix) | The frozen evidence record has no unique record identifier; references currently use evidence.csv line numbers (header is line 1), which is fragile. Whether a `record_id` field is added in a later evidence-rules version must be decided before freeze. | RESOLVED | `evidence_id` added as the first field of the evidence record (format SUT01-EV-0001 … SUT06-EV-0001; sequential per ecosystem; never reused). All evidence references (audit.md, unresolved.md, adjudication output, corrections, contradictions, verification records) use `evidence_id`, never CSV row or line numbers. Applied while the protocol is DRAFT, so no evidence-rules v2 is needed. | protocol/evidence-rules-v1.md; protocol/agent-governance-v1.md; protocol/capability-rubric-v1.md; schemas/evidence.schema.json; schemas/sut-audit.schema.json; schemas/README.md; audits/README.md; audits/*/evidence.csv; audits/*/audit.md; audits/*/unresolved.md; experiments/E01-capability-audit/README.md | no |
| (x) | Whether DOCUMENTED evidence alone can support an adjudicated Score 3 is unresolved: the rubric's Score 3 text accepts a "documented or verifiable mechanism", while the evidence rules state that documentation only identifies a candidate capability. | RESOLVED | Resolved by explicit human decision (2026-09-16). DOCUMENTED evidence alone supports only a provisional Score 3 candidate (`provisional_score = 3`, `confirmation_state = UNCONFIRMED_SCORE_3`); it never confirms an adjudicated Score 3, and an UNCONFIRMED_SCORE_3 cell is excluded from every confirmed Score 3 count (protocol/statistical-analysis-plan-v1.md, section 4.3, H1). SOURCE_VERIFIED confirms Score 3 when source inspection of the pinned evaluated version demonstrates the mechanism is implemented; EXECUTION_VERIFIED confirms Score 3 when execution provenance demonstrates the mechanism and its expected observable outcome; EXECUTION_VERIFIED is required where SOURCE_VERIFIED is unobtainable (closed-source / hosted-only components, Section 10.4). If DOCUMENTED evidence contradicts SOURCE_VERIFIED or EXECUTION_VERIFIED evidence for the same mechanism, both records are retained and the contradiction is recorded (protocol/evidence-rules-v1.md); the stronger empirical evidence (SOURCE_VERIFIED or EXECUTION_VERIFIED) governs Score 3 confirmation, without creating an ordering between SOURCE_VERIFIED and EXECUTION_VERIFIED themselves. | protocol/capability-rubric-v1.md; protocol/evidence-rules-v1.md; protocol/statistical-analysis-plan-v1.md; schemas/sut-audit.schema.json; audits/README.md; audits/*/audit.md | no |
| (xi) | The denominator of Exact Outcome Rate when target-state reproduction fails (counted under Repeatability Rate only, or also as a non-matching execution) must be fixed before E04/E05 are frozen, consistently with the rule that failures are outcomes, not exclusions. | RESOLVED | Resolved by explicit human decision (2026-09-16): both readings are kept, as two separately named, separately reported metrics, instead of choosing one. Three distinct rates replace the single ambiguous Exact Outcome Rate (protocol/repeatability-determinism-v1.md, section 4): Target-State Reproduction Rate (TSRR) = successful target-state establishments / all valid measured attempts (campaign E04, primary; target-state establishment failure counts as a TSRR failure; this is the metric previously named Repeatability Rate in this document, renamed here for terminological consistency with CEOR and E2E-ROR, formula and meaning unchanged); Conditional Exact Outcome Rate (CEOR) = executions producing the exact predefined expected outcome / executions in which the required target state was successfully established (campaign E05, primary; target-state establishment failures are excluded from the denominator by definition; CEOR = NOT_ESTIMABLE, never 0, when no measured attempt establishes the target state); End-to-End Reproducible Outcome Rate (E2E-ROR) = executions producing the exact predefined expected outcome / all valid measured attempts (campaign E05, secondary; target-state establishment failure counts against E2E-ROR). Outcome Entropy H(Y) is computed over the same execution set as CEOR's denominator (the successfully-established executions), so that the H3 conjunction (CEOR = 1.00 and H(Y) = 0) stays satisfiable on a condition's own outcomes and is not forced positive by an unrelated target-state establishment failure. The three rates are never collapsed into one. Issue (xix) (tooling-versus-SUT attribution for E04/E05) remains DEFERRED-BEFORE-CAMPAIGN and is unaffected by this resolution. | protocol/repeatability-determinism-v1.md; protocol/statistical-analysis-plan-v1.md; experiments/E04-repeatability/README.md; experiments/E05-determinism/README.md | no |
| (xii) | Initial environment provisioning effort (deploying or building an ecosystem before any campaign runs) is not captured by E02 or E03; whether it belongs to Setup Effort, and how it is recorded, must be decided before freeze. | RESOLVED | protocol/setup-effort-v1.md distinguishes ONE-TIME PROVISIONING (installing dependencies, building, first emulator setup, downloading binaries, starting services) from PER-RUN / PER-CONDITION SETUP (login, seed state, navigate, create cart, reset session, set locale, activate condition). The primary metric, Required Actions, covers per-run / per-condition setup only. Provisioning is recorded descriptively in a provisioning record for reproducibility and precedes the declared starting state; it never enters the primary setup-effort comparison. | protocol/setup-effort-v1.md; protocol/study-design-v1.md; experiments/E02-state-establishment/README.md; experiments/E03-resetability/README.md; raw-data/README.md | no |
| (xiii) | For E08–E11, the outcome "no controllable ground-truth condition available in this ecosystem" must be classified before freeze as either a finding about Experimental Controllability or an exclusion from the RQ5 comparison; the two readings lead to different reports. | RESOLVED | Both, in separate places, as the existing protocol already implies: the outcome is a recorded finding about Experimental Breadth / Experimental Controllability (the E01 cell and the campaign's categorical outcome "no ground-truth condition available"), and the ecosystem is reported as "no data" with that reason in the RQ5 detection-rate comparison for that condition (protocol/statistical-analysis-plan-v1.md, section 5). It is never reported as a detection failure and never as a zero detection rate. | protocol/statistical-analysis-plan-v1.md; experiments/E08–E11 READMEs | no |
| (xiv) | Localization / i18n informs Experimental Breadth twice (as an E01 rubric cell and as the E12 campaign outcome); the analysis plan must state how this is reported without double counting. | RESOLVED | Section 9 and Section 11, rule 8: the E01 level and the E12 observations are different evidence layers, reported in separate tables, never summed and never counted twice in any count of modalities per level. No global aggregate exists. | protocol/study-design-v1.md; protocol/statistical-analysis-plan-v1.md; experiments/E12-localization-i18n/README.md; analysis/README.md | no |
| (xv) | Pass thresholds and the number of repeated runs used to assess reliability in the Mobilewright qualification gate are undefined and must be fixed before the gate executes. | RESOLVED | protocol/mobile-runner-policy-v1.md, section 7: 3 mandatory scenarios × 2 platforms; N = 10 clean measured executions per combination; pass requires 100% support of the mandatory capabilities MC-01…MC-10, 10/10 successful measured executions per combination, no repeated runner-caused blocker for any required capability, and no manual intervention inside a measured scenario; warm-up allowed and not counted toward N (a runner-caused warm-up failure still counts under the repeated-blocker criterion); infrastructure failures unrelated to Mobilewright recorded separately with an attribution record and not an automatic runner failure; duration secondary only; failure on a required capability switches the runner to Appium 3 with the reason recorded. | protocol/mobile-runner-policy-v1.md; qualification/mobilewright/README.md | no |
| (xvi) | E01 is a structured audit rather than an execution campaign; whether an audit session requires a run manifest, and what its fields mean there, must be decided before freeze. | RESOLVED | protocol/evidence-rules-v1.md, "Execution verification records": DOCUMENTED, SOURCE_VERIFIED, and INFERRED records require no run manifest. Every EXECUTION_VERIFIED record requires an execution verification record, which is a run manifest (schemas/run-manifest.schema.json) with campaign_id E01-capability-audit carrying verification_id (run_id), sut_id, modality, environment_type, timestamp, sut_provenance, toolchain/probe, scenario_or_probe, outcome, artifact references, and related evidence_id(s), stored in audits/<SUT>/verifications/ with artifacts in audits/<SUT>/artifacts/. No second execution framework. | protocol/evidence-rules-v1.md; schemas/run-manifest.schema.json; experiments/E01-capability-audit/README.md; audits/README.md; raw-data/README.md | no |
| (xvii) | Which role issues the explicit instruction for QUALIFIER-MOBILE-01 to execute the gate, and which role proposes a campaign freeze, must be confirmed at freeze; the current text places the first with a human via protocol/agent-governance-v1.md (common rule on explicit instruction) and the second with the ORCHESTRATOR under human approval (protocol/change-control-v1.md section 7). | RESOLVED | The existing text is consistent and is now stated explicitly where it applies: the instruction to execute the gate is issued by a human and relayed by the ORCHESTRATOR (protocol/agent-governance-v1.md, section 2, rule 6; protocol/mobile-runner-policy-v1.md, section 2); a campaign start and a campaign freeze are proposed by the ORCHESTRATOR and approved by a human (protocol/change-control-v1.md, section 7). Confirmation at freeze happens through the ordinary freeze review of every protocol document. | protocol/mobile-runner-policy-v1.md; protocol/change-control-v1.md; protocol/agent-governance-v1.md; qualification/mobilewright/README.md | no |
| (xviii) | Two Setup Effort counting rules remain open (protocol/setup-effort-v1.md, section 5): whether verification that the target state was reached counts as an action, and how a partially successful action is counted. | DEFERRED-BEFORE-CAMPAIGN | Deferred to the campaign configuration of E02 and E03, where the counting rules are frozen before the first Required Actions count is recorded for analysis. Until then no count may be used for analysis. If the decision is taken after protocol freeze it creates protocol/setup-effort-v2.md under protocol/change-control-v1.md; the human reviewer may instead decide it at protocol freeze. | protocol/setup-effort-v1.md | yes |
| (xix) | The attribution rule for deviations caused by the test runner, driver, device, or infrastructure rather than by the SUT in E04/E05, and how attributed deviations are reported alongside raw rates, is TBD (protocol/repeatability-determinism-v1.md, section 6). | DEFERRED-BEFORE-CAMPAIGN | Deferred to the campaign configuration of E04 and E05: exclusion and attribution rules are items locked by the campaign freeze mechanism (protocol/change-control-v1.md, section 7). Until frozen, every deviation counts in the raw rates regardless of suspected cause and the suspected cause is a note only. | protocol/repeatability-determinism-v1.md; protocol/statistical-analysis-plan-v1.md; protocol/change-control-v1.md | yes |
| (xx) | H3 predicts "high exact-outcome reproducibility" for deterministic OmniPizza conditions but no operational threshold for "high" is pre-registered, so H3 cannot be evaluated as stated. | RESOLVED | Resolved by explicit human decision (2026-09-16). "High" is removed and H3 is restated with an explicit criterion (Section 6): "For OmniPizza conditions classified a priori as deterministic, every valid measured execution that successfully establishes the frozen target state will produce the same predefined expected categorical outcome (Conditional Exact Outcome Rate = 1.00 and Outcome Entropy H(Y) = 0)." H3 applies only to conditions classified as deterministic before execution and locked in the campaign configuration at campaign start (protocol/repeatability-determinism-v1.md, section 2; protocol/change-control-v1.md, section 7); it does not claim every OmniPizza condition is deterministic; stochastic, time-dependent, and external-dependency conditions are classified separately and excluded from H3 testing. TSRR and E2E-ROR are still reported for these conditions but are not the primary H3 criteria. One valid unexpected categorical outcome on a condition that successfully established its target state means that condition does not satisfy the preregistered H3 criterion. | protocol/study-design-v1.md; protocol/statistical-analysis-plan-v1.md | no |

Register totals at the end of the 2026-09-15 hardening iteration: RESOLVED 15; OPEN 3 ((x), (xi), (xx)); DEFERRED-BEFORE-CAMPAIGN 2 ((xviii), (xix)).

Register totals at the end of the 2026-09-16 second hardening iteration: RESOLVED 18; OPEN 0; DEFERRED-BEFORE-CAMPAIGN 2 ((xviii), (xix)). Twenty rows total (i)–(xx); none removed.

## 14. Status

- Protocol state: FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6). The hardening iteration instructed on 2026-09-15 and completed on 2026-09-16, the second hardening iteration instructed and completed on 2026-09-16 (issues (x), (xi), (xx)), and the final pre-freeze checklist closure instructed and completed on 2026-09-16 (step-3 freeze-checklist items, explicit human decision) all edited this document in place under protocol/change-control-v1.md, section 2 (DRAFT -> DRAFT), before the protocol v1 pre-data freeze of 2026-09-16 moved it, with the rest of protocol/, to FROZEN-PRE-DATA. This document is now immutable in place except for its header state field and successor pointer; any further substantive change creates protocol/study-design-v2.md.
- Data collected: none. data_collection_started is false (manifests/study-manifest.yaml).
- Results: none. No capability score, measurement, ranking, or finding exists for any SUT.
- Open-Issue Register (Section 13): OPEN 0; DEFERRED-BEFORE-CAMPAIGN 2 ((xviii), (xix)) — these two remain deferred to the E02/E03 and E04/E05 campaign configurations respectively and are not resolved here.
- Next step: human review of this document and its siblings (the Open-Issue Register itself no longer blocks freeze, and step 3 of the freeze checklist in protocol/change-control-v1.md, section 6 — the "TBD before freeze" / "candidate — not frozen" items under protocol/ and schemas/ — is now resolved or explicitly deferred to campaign configuration per the final pre-freeze checklist closure of 2026-09-16), then protocol freeze under protocol/change-control-v1.md.
