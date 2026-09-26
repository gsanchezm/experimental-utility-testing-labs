# Experimental Utility of Software-Testing Laboratory Ecosystems — Study Repository

Study id: EUS-2026-001 (an internal study identifier; not a registration with any external registry). Protocol version: v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez; protocol/change-control-v1.md, section 6; manifests/protocol-freeze-v1.yaml). Repository initialized: 2026-09-15. Pre-freeze protocol hardening iteration: instructed 2026-09-15, completed 2026-09-16 (protocol state then unchanged: DRAFT); protocol v1 pre-data freeze: instructed and completed 2026-09-16.

## 1. Purpose

Working study concept: **Experimental Utility of Software-Testing Laboratory Ecosystems**.

The study evaluates whether software-testing laboratory ecosystems provide experimentally useful, controllable, repeatable, observable, and integrated conditions for modern software-testing research and practice.

The unit of comparison is the **testing laboratory ecosystem**, not an individual repository. An ecosystem may consist of several repositories, releases, hosted deployments, or platform-specific artifacts; all of them together form one system under test (SUT). Full design: protocol/study-design-v1.md.

## 2. Evaluated ecosystems

| SUT id | Ecosystem | Role |
|---|---|---|
| SUT-01 | OmniPizza | general-purpose candidate |
| SUT-02 | Sauce Labs Demo Ecosystem | general-purpose baseline (any separate Web, Android, or iOS repositories/artifacts it may comprise are treated as ONE ecosystem) |
| SUT-03 | BrowserStack Demo Ecosystem | general-purpose / Web / API baseline |
| SUT-04 | Restful Booker Platform | Web/API specialist baseline |
| SUT-05 | OWASP Juice Shop | security specialist baseline |
| SUT-06 | WebdriverIO Native Demo App | mobile specialist baseline |

Component repositories, releases, and deployment targets for each ecosystem are recorded in manifests/sut-manifest.yaml. At initialization all provenance fields there are null; they are filled when the ORCHESTRATOR pins the evaluated version of each ecosystem before the E01 audit starts (sequence in manifests/README.md), never by guess.

## 3. Primary construct

The primary research construct is **Experimental Utility**, treated as a **multidimensional profile** with six dimensions, in this order:

1. Experimental Breadth
2. Experimental Controllability
3. Repeatability and Determinism
4. Cross-platform and Cross-layer Integration
5. Observability and Automation Affordances
6. Setup Effort

**No single weighted score is defined.** No aggregated or weighted Experimental Utility Score, index, or ranking formula exists or may be defined. Each ecosystem is described by its per-dimension profile. Experimental Breadth and Modality Depth answer different questions: a specialist ecosystem may legitimately have low breadth and high depth in its intended modality; unsupported modalities stay visible as Score 0 with a structural scope note; no overall winner is computed; conclusions are dimension-specific (protocol/study-design-v1.md, section 11). The dimensions may evolve only through explicit protocol versioning (protocol/change-control-v1.md).

## 4. Current project phase

| Field | Value |
|---|---|
| Phase | SETUP (literal `manifests/study-manifest.yaml` value, unrenamed since freeze; substantial work has since occurred within it — see AGENT-INSTRUCTIONS.md, "Current phase") |
| Protocol state | FROZEN-PRE-DATA for every protocol v1 document (frozen 2026-09-16) and protocol/setup-effort-v2.md (frozen 2026-09-21; v1 AMENDED); protocol/agent-governance-v2.md FROZEN-PRE-DATA (2026-09-22; agent-governance-v1.md AMENDED); it defines roles and boundaries and authorizes no execution |
| data_collection_started | true (2026-09-17, E01 campaign start) |
| Audits performed | E01 Capability Audit complete and FROZEN (2026-09-18): six audits, adjudication, two human rulings, the adjudicated 54-cell matrix, and the H1 descriptive comparison (derived-data/) |
| Experiments executed | none; E02–E12 NOT_STARTED. E03-resetability is human-selected and in PRE-START preparation (CS-001 sole accepted scenario, nine candidate conditions, non-measured provisioning and environment verification 2026-09-22, GitHub Actions infrastructure published to the public repository 2026-09-22, mobile-qualification gate executed 2026-09-22 but quarantined as HISTORICAL_UNAUTHORIZED_EXECUTION — PROTO-U10; protocol-valid mobile-qualification gate executed once 2026-09-24 under MOBILE-QUALIFICATION-EXEC-AUTH-03 — FAIL, so the mobile runner is Appium 3, pinned 3.7.0, by the frozen switch rule, not yet installed or executed); no measured E03 execution |

Authoritative phase record: manifests/study-manifest.yaml.

## 5. Directory layout

```text
.
├── README.md            this file: study overview, phase, layout, governance pointers
├── AGENT-INSTRUCTIONS.md            binding project instructions for all agents and human operators
├── .gitignore           excludes tool noise, caches, IDE/OS files, secrets; never excludes scientific content
├── .github/workflows/   E03-resetability GitHub Actions infrastructure (validation, environment verification, mobile qualification, gated measured execution); ORCHESTRATOR-only under E03-CI-WRITE-AUTH-01
├── protocol/            pre-registered study rules, versioned (v1; setup-effort v2); FROZEN-PRE-DATA since the 2026-09-16 freeze (setup-effort v2 and agent-governance v2 frozen later; their v1 predecessors AMENDED)
├── manifests/           study, SUT, and toolchain manifests (YAML); unknown provenance is null
├── audits/              one directory per SUT for E01 capability-audit evidence (templates on main; SUBMITTED audits on the six audit/e01-sut0N-* branches)
├── qualification/       Mobilewright qualification gate (MQ1, MQ2, MQ3) and per-SUT compatibility-smoke records; the protocol-valid gate ran once on 2026-09-24 (MOBILE-QUALIFICATION-EXEC-AUTH-03; mobilewright/formal/MOBILE-QUALIFICATION-EXEC-AUTH-03/; result FAIL, runner switched to Appium 3) — the gate executed on 2026-09-22 is preserved but quarantined (PROTO-U10; output/QUARANTINE-RECORD.yaml); frozen-input package: manifests/mobile-qualification-package-v2.yaml (v1 history); local-preflight/ holds the non-qualification LOCAL_DEVELOPMENT_PREFLIGHT executed 2026-09-22
├── experiments/         one directory per campaign E01–E12 (E01 FROZEN; E03 in PRE-START preparation; others NOT STARTED); scenario-mappings/ (CS-001 active; CS-002 excluded)
├── raw-data/            immutable raw observations per campaign and SUT; append-only after campaign freeze; MEASURED_EXPERIMENT records only
├── derived-data/        reproducible transformations of raw data, each with provenance
├── analysis/            transformation and analysis scripts and outputs; per-dimension profiles only
├── prompts/
│   ├── frozen/          exact agent prompts used during data collection, versioned; provenance for runs
│   └── working/         draft agent prompts, editable before use
└── schemas/             JSON schemas for manifests and records (e.g. schemas/run-manifest.schema.json)
```

## 6. Status statements

- The only results are E01's frozen capability matrix and the H1 descriptive count comparison (derived-data/e01-adjudicated-matrix/, derived-data/h1-analysis/); no E02–E12 result exists and H2–H5 are not analyzed.
- No ranking exists, and none may be computed (section 3).
- Capability scores exist only as the per-cell E01 matrix; no score has been assigned by any later campaign.
- OmniPizza (SUT-01) is one evaluated SUT, not the experimental framework, and receives no privileged interpretation. It is treated exactly like every other evaluated SUT.
- Specialist baselines (SUT-04, SUT-05, SUT-06) are not expected to be weaker than OmniPizza (SUT-01) in their specialty. The study must allow results that contradict any provisional hypothesis.
- Data collection started 2026-09-17 (E01). No SUT has been modified. On 2026-09-22, under explicit human authorization, the pinned components of SUT-01 through SUT-05 were cloned or downloaded and provisioned as NON-MEASURED controlled instances for E03 environment verification (manifests/provisioning/; experiments/E03-resetability/controlled-instance-determination.md); that activity produced no measured data.
- No testing tool has been selected or qualified (manifests/toolchain-manifest.yaml: every runner version is null; Node.js is recorded as the analysis scripting runtime).
- One protocol-valid Mobilewright qualification gate has been executed: on 2026-09-24, under MOBILE-QUALIFICATION-EXEC-AUTH-03 (GitHub Actions run 35938250936, attempt 1; 6 warm-ups, 60 measured executions, 0 excluded). Result FAIL: MQ3 0/10 on the Android emulator (MC-07, deep link carrying parameters, not supported there), every other scenario × platform combination 10/10; the specific root cause is unresolved and the failures are runner-caused under the policy's conservative attribution rule. By the frozen switch rule the study's mobile runner is Appium 3, pinned 3.7.0 — not yet installed or executed; no compatibility smoke has been executed. An earlier Mobilewright gate executed on 2026-09-22 without a valid human authorization (protocol/unresolved.md, PROTO-U10) remains preserved and quarantined as HISTORICAL_UNAUTHORIZED_EXECUTION (observed but protocol-inadmissible for runner-selection authority). A separate, non-qualification LOCAL_DEVELOPMENT_PREFLIGHT ran 2026-09-22 by explicit human instruction (implementation baseline locked; Android on a physical device complete, iOS blocked on host infrastructure; qualification/mobilewright/local-preflight/); it changed no qualification status and selected no runner. A post-run artifact-hygiene escalation about incomplete, unusable token fragments in the MQ3 runner logs (qualification/unresolved.md, QUAL-U03; protocol/unresolved.md, PROTO-U13) is resolved as to publication handling: the canonical records stay unchanged and future public exports remove every textual token remnant in the qualification records by a fixed marker (transformation QUALIFICATION_TOKEN_FRAGMENT_REDACTION, PUBLIC-EXPORT-MANIFEST.yaml; first applied by export v25). Appium 2 is never used.
- The six E01 evidence.csv files on the auditor branches carry the audits' evidence records; the copies on `main` are the header-only templates (protocol/unresolved.md, PROTO-U07). Evidence records are identified by evidence_id (SUT0n-EV-nnnn), never by row number.
- Open-Issue Register (protocol/study-design-v1.md, section 13): live status 19 RESOLVED, 0 OPEN, 1 DEFERRED-BEFORE-CAMPAIGN ((xix), E04/E05); the frozen table text is a historical snapshot (AGENT-INSTRUCTIONS.md, "Current phase").
- Canonical scenarios: CS-001 is the sole accepted scenario for the current E03 campaign version; CS-002 is preserved unchanged but EXCLUDED_FROM_CAMPAIGN (2026-09-22; manifests/e03-cs002-exclusion-v1.yaml).

## 7. Governance

- AGENT-INSTRUCTIONS.md — binding instructions for every agent and human operator in this repository.
- protocol/agent-governance-v2.md (FROZEN-PRE-DATA 2026-09-22, authorization id AGENT-GOVERNANCE-V2-FREEZE-AUTH-01; record manifests/agent-governance-v2-freeze-v1.yaml) — the agent-governance document in force: agent roles (ORCHESTRATOR; AUDITOR-SUT01-OMNIPIZZA through AUDITOR-SUT06-WEBDRIVERIO; ADJUDICATOR-EU-01; QUALIFIER-MOBILE-01; EXECUTOR-E03-RESETABILITY, E03-resetability only) with explicit read and write boundaries, cross-SUT isolation, and GitHub Actions permissions and prohibitions. It authorizes no execution. protocol/agent-governance-v1.md is AMENDED (superseded by v2).
- AGENT-INSTRUCTIONS.md, "E03 CI/CD infrastructure" (E03-CI-WRITE-AUTH-01) — GitHub Actions as the E03 orchestrator; `.github/workflows/**` written by ORCHESTRATOR only; measured executions only through the frozen workflow; publication hygiene. Workflows: `.github/workflows/` (E03 Validate Configuration, E03 Environment Verification, E03 Mobile Qualification, E03 Measured Execution); model: experiments/E03-resetability/ci-cd-execution-model.md.
- PUBLIC-EXPORT-MANIFEST.yaml — public repository (https://github.com/gsanchezm/experimental-utility-testing-labs, PUBLIC), publication mode CLEAN_PROVIDER_NEUTRAL_REPRODUCIBILITY_EXPORT, inclusion/exclusion rules, transformation classes, the export log; the canonical history is preserved internally and never rewritten, and every exported branch carries a PUBLIC-EXPORT-MANIFEST.yaml tracing each file to its canonical blob.
- protocol/change-control-v1.md — protocol state lifecycle (DRAFT, FROZEN-PRE-DATA, AMENDED, SUPERSEDED), versioning rule, change log.
- protocol/evidence-rules-v1.md — evidence statuses (DOCUMENTED, SOURCE_VERIFIED, EXECUTION_VERIFIED, INFERRED), evidence record fields with evidence_id, execution verification records.
- protocol/equivalent-scenario-mapping-v1.md — semantic equivalence of cross-ecosystem scenarios and the NOT_COMPARABLE marker.
- protocol/statistical-analysis-plan-v1.md — CONFIRMATORY (H1, H2, H4, H5: SUT-01 versus SUT-02, SUT-01 versus SUT-03; H3 is a single-ecosystem prediction) versus EXPLORATORY (all other, including specialist, unless explicitly pre-registered as CONFIRMATORY in the campaign configuration before the campaign begins) comparison classification.

## 8. Mobile runner

Primary candidate: Mobilewright. Fallback: Appium 3. Appium 2 must not be used. Selected runner: Appium 3, pinned 3.7.0 (2026-09-24, by the frozen switch rule after Mobilewright failed the protocol-valid gate; not yet installed or executed; the 2026-09-22 gate remains quarantined, PROTO-U10). Mobilewright must pass a separate qualification gate before any experimental use: scenarios MQ1 Login → Catalog, MQ2 Catalog → Product Interaction, MQ3 API State Seed → Deep Link → Target UI State, on Android emulator and iOS Simulator, with OmniPizza (SUT-01) as the qualification SUT (no evidence, familiarity advantage, or privileged interpretation results from this; disclosed as a limitation), N = 10 clean measured executions per scenario × platform, and pass only on 100% mandatory-capability support, 10/10 per combination, no repeated runner-caused blocker, and no manual intervention. After runner selection each mobile-capable SUT receives a per-SUT compatibility smoke. The protocol-valid gate ran once, on 2026-09-24 (MOBILE-QUALIFICATION-EXEC-AUTH-03): FAIL; records and decision in qualification/mobilewright/. Mobilewright versus Appium is not a primary research question. Policy: protocol/mobile-runner-policy-v2.md (v1 AMENDED 2026-09-26; the qualification gate was executed under v1). Records: qualification/.

## 9. Next expected step

1. ~~Human review of every document under protocol/ and manifests/~~ — done. The Open-Issue Register (protocol/study-design-v1.md, section 13) has no OPEN row, and the freeze-checklist items of protocol/change-control-v1.md, section 6, step 3, were resolved or explicitly deferred to campaign configuration by the final pre-freeze checklist closure of 2026-09-16.
2. ~~Explicit human approval to freeze the protocol (DRAFT -> FROZEN-PRE-DATA)~~ — done. Protocol v1 was frozen 2026-09-16, approved by gilbertosanchez, recorded per protocol/change-control-v1.md, manifests/protocol-freeze-v1.yaml, and protocol/CHANGELOG.md. Every protocol v1 document now reads `Protocol state: FROZEN-PRE-DATA`. `data_collection_started` remains false: the protocol freeze does not by itself start data collection, select a mobile runner, or begin any campaign.
3. ~~E01 capability audit~~ — done and FROZEN (2026-09-18). Issue (xviii) was resolved by human ruling on 2026-09-21 (protocol/setup-effort-v2.md); issue (xix) remains DEFERRED-BEFORE-CAMPAIGN for E04/E05.
4. ~~Freeze of the exact `protocol/agent-governance-v2.md` content hash~~ — done 2026-09-22 (AGENT-GOVERNANCE-V2-FREEZE-AUTH-01). ~~Public-repository publication~~ — mode decided (CLEAN_PROVIDER_NEUTRAL_REPRODUCIBILITY_EXPORT) and the provider-neutral export published 2026-09-22: public main plus six audit snapshot branches, canonical history preserved, validation workflow passing (export log in PUBLIC-EXPORT-MANIFEST.yaml). E03-resetability PRE-START preparation is complete up to the gates that need a human: ~~mobile qualification EXECUTION~~ — done 2026-09-24 (MOBILE-QUALIFICATION-EXEC-AUTH-03: FAIL; Appium 3, pinned 3.7.0, selected by the frozen switch rule); ~~artifact-hygiene handling and measured-execution gate G-7 correction~~ — done 2026-09-24 (QUAL-U03 / PROTO-U13 publication-only redaction defined; G-7 corrected for the section 8 switch, PROTO-U14; manifests/pre-publication-corrections-v1.yaml); per-SUT × platform smoke readiness and selected-runner provenance in G-7 (PROTO-U15; manifests/compatibility-smoke-status.yaml) and public export v25 authorized 2026-09-24 (manifests/pre-e03-publication-completion-v1.yaml); Appium 3 compatibility smoke for SUT-02 (Android, iOS) prepared and locked 2026-09-24, then re-locked 2026-09-26 under protocol/mobile-runner-policy-v2.md (PROTO-U17 resolved; lock v2), not issued, not dispatched, not executed (manifests/appium3-compat-smoke-preparation-v1.yaml; manifests/mobile-runner-policy-v2-amendment-v1.yaml; APPIUM3-COMPAT-SMOKE-AUTH-01 PREPARED); then review of policy v2 and the re-locked package, PROTO-U18 resolved and the Mobilewright qualification path retired (2026-09-26; content of public export v26, whose publication is recorded in the export log); independent review of public export v26; a separate issuance of the smoke authorization and a separate dispatch instruction; the PROTO-U16 presence transcription; E03 campaign START; executor prompt freeze and launch. Only when explicitly instructed: the compatibility smoke (qualification/compatibility-smoke/), then E03 start.

No agent starts step 4's gated items, or any further protocol change, on its own initiative (AGENT-INSTRUCTIONS.md, rule 15; protocol/change-control-v1.md).

## 10. Note on naming

The working directory is named `experimental-utility-testing-labs`, while the study brief that initialized it (and the header comment of .gitignore) refers to the repository as `experimental-utility-study`. Both names denote the same repository. The working directory is treated as the repository root, and every path in this repository is relative to that root.
