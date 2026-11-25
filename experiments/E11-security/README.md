# E11 — Security

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) provides a known vulnerable condition, such as a documented intentional vulnerability class, that can serve as ground truth, and whether a security verification method applied to the running instance detects it. Detection is judged against the known condition, not against the total number of findings a tool reports. All security testing is confined to the evaluated SUT instances that the study itself deploys and controls (environment_type SELF_HOSTED or LOCAL for the service components under test, EMULATED or SIMULATED for mobile application builds; protocol/study-design-v1.md, section 10.1); no verification may be directed at any third-party production system or PUBLIC_HOSTED instance. An ecosystem for which no controlled instance can be established records NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE for every active-testing condition (protocol/study-design-v1.md, section 10.3); this is an experimental-control fact, not a capability score. The outcome "no ground-truth condition available" is recorded as a categorical finding about Experimental Breadth / Experimental Controllability and is reported as "no data" with that reason in the RQ5 detection-rate comparison; it is never a detection failure and never a detection rate of zero (protocol/statistical-analysis-plan-v1.md, section 5).

## Related research question(s)

- RQ5 Controlled Non-functional Experimentation (primary).
- Informs dimensions 1 Experimental Breadth and 2 Experimental Controllability.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Known vulnerable condition (for example a documented intentional vulnerability class; catalogue built during E01 with provenance, TBD before freeze) — candidate.
- Verification method (for example automated scan vs targeted check; method list TBD before freeze) — candidate.

## Future dependent variables (candidate — not frozen)

- Detection outcome (categorical: detected / not detected / no ground-truth condition available) — candidate.
- Ground-truth availability (categorical: whether a documented, reproducible known vulnerable condition exists) — candidate.

## Required evidence

- Reference to the documentation of the known vulnerable condition, with provenance (repository, commit_sha_or_release, file_path_or_endpoint), recorded as null when unknown.
- Verification artifacts (raw tool output or targeted check records).
- Instance record confirming the target was a study-controlled deployment (deployment identifier, host, and time window), satisfying the authorized-testing scope.
- One run manifest per condition × verification method execution conforming to schemas/run-manifest.schema.json, carrying `environment_type` (controlled environments only: SELF_HOSTED or LOCAL for services, EMULATED or SIMULATED for mobile builds).
- Security tooling candidate per manifests/toolchain-manifest.yaml; tool and version used must be recorded in the run manifest.
- Raw observations in `raw-data/E11-security/`.

## Current status

FROZEN since the campaign freeze of 2026-11-24 (human authorization E11-FREEZE-AUTH-01; protocol/change-control-v1.md, section 7, moment 2; record manifests/e11-campaign-freeze-v1.yaml), after IN PROGRESS from the campaign START of 2026-11-24 (E11-START-AUTH-01; record manifests/e11-campaign-start-v1.yaml). The "Campaign configuration" section below is locked and immutable. The 700 executions (fourteen cells on SUT-01 (2) and SUT-05 (12), N = 50 each, all attempt 1) were imported unchanged under raw-data/E11-security/ on 2026-11-24 UTC within the two dispatch authorizations E11-DISPATCH-SUT01-AUTH-01 and E11-DISPATCH-SUT05-AUTH-01 (manifests/e11-dispatch-authorization-sut0N-v1.yaml; dispatch records manifests/e11-measured-dispatch/e11-sut0N.jsonl); raw-data/E11-security/ is append-only. The raw data are not yet published and the E11 contribution to H5 has not been analyzed.

Resumed by the human research lead's decision of 2026-11-02 (manifests/campaign-resumption-v1.yaml); the deferral of scope A (manifests/campaign-disposition-v1.yaml) no longer governs the schedule. Preparation record: manifests/campaign-execution-decisions-v19.yaml to -v22.yaml; environment verification: manifests/e11-environment-verification-rounds-v1.yaml (rounds 1 and 2).

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.

## Campaign configuration

This record is the "Campaign configuration" of E11-security. It is locked at the campaign START (protocol/change-control-v1.md, section 7, moment 1) under the human authorization named below, and is immutable from then on; a change after the START is a change-control row recorded before the affected execution. It authorizes no dispatch: each dispatch authorization (protocol/agent-governance-v6.md, Section 3.7) is issued separately by the human research lead. The decisions E11-D-1 to E11-D-15 of experiments/E11-security/design-brief-draft.md and campaign-configuration-draft.md are recorded in manifests/campaign-execution-decisions-v19.yaml to -v22.yaml (E11-D-1 to D-7, D-2b and D-2c reconfirmed in v21). A system under test (SUT) is one of the evaluated ecosystems of README.md.

### Identity and START

- Campaign: E11-security. Hypothesis label: H5 (protocol/statistical-analysis-plan-v1.md, section 4.3), a descriptive count comparison of controlled non-functional ground-truth conditions, SUT-01 against SUT-02 and SUT-01 against SUT-03 (the counts of SUT-02 and SUT-03 are 0 with "no data, no ground-truth condition available"); the SUT-05 cells are an EXPLORATORY specialist reference (E11-D-2); no support or non-support criterion is frozen for H5 and none is invented.
- START authorization id: E11-START-AUTH-01 (the human research lead's explicit approval of the START; the change-log row of protocol/CHANGELOG.md names it).
- Protocol: v1 FROZEN-PRE-DATA. Agent governance: protocol/agent-governance-v6.md, FROZEN-PRE-DATA since 2026-11-06 (Sections 3.6 and 3.7).
- Execution: GitHub Actions only (CAMPAIGN-CI-WRITE-AUTH-01), through .github/workflows/e11-measured-execution.yml, by the ORCHESTRATOR under dispatch authorizations; first attempt only, default branch only, no re-run; one dispatch per cell; the dispatch record of each SUT is manifests/e11-measured-dispatch/e11-sut0N.jsonl, written before each dispatch.
- Scenario mapping: none. E11 compares per ecosystem (design brief, V-6); there is no canonical scenario and no mapping record.

### Pinned versions

- SUT-01 api: https://github.com/gsanchezm/OmniPizza at commit 9ca37674d374e9303912e259641ee86baf3aabe1 (manifests/sut-manifest.yaml; no release).
- SUT-05 api: https://github.com/juice-shop/juice-shop at commit 1618a611b173b4bf114028e6e02549950606e29d, release v20.2.0, by the Packaged Distributions route (manifests/sut-manifest.yaml).
- SUT-02, SUT-03, SUT-04 and SUT-06: no cell (E11-D-1; SUT-04 by the ruling E01-HR-02).
- Run-manifest schema: schemas/run-manifest.schema.v2.json, sha256 9a86cf37c4ccd2abe3368866309e18a9f9554a2330f5dceeacda6d02a2932757 (E11-D-10).
- ZAP (M2 cells): OWASP ZAP 2.17.0 as the container image ghcr.io/zaproxy/zaproxy by digest, amd64 manifest sha256:c2d63bbb2d907a5c5257914fb20e26e969c92b25f265def7f89f08203f912882 (index sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af); 49 add-ons observed and recorded in manifests/toolchain-manifest.yaml, tools.security (decisions E11-D-8 and the entry of v22); update checks off; scan settings are the release defaults, never tuned.
- Python runtime of the executor: the runner's python3 (3.12 series on ubuntu-24.04), recorded per run. Runner image: ubuntu-24.04, version recorded per run. The executor uses the standard library only.

### Prompt version and implementation

- Dispatch procedure prompt: ORCHESTRATOR-E11-security-v1, frozen at the START as prompts/frozen/ORCHESTRATOR-E11-security-v1.md, a byte-identical copy of prompts/working/ORCHESTRATOR-E11-security-v1.md, sha256 6ed3211ef7c8c0f13a7e6d6d1d8663935bd10cb074dc55c6d8cfa5d0f94ed897 (E11-D-13).
- Implementation hash (sha256 of experiments/E11-security/executor/run-condition.sh, which embeds the digests of the executor files and refuses an unlisted one): 0ce7625b72899523ea41b296425e1d0a144fbcf26ec0ea896d85013c5f2670fc. This is the implementation that ran complete on GitHub Actions in the second environment-verification run (run 45417209148).
- Measured workflow: .github/workflows/e11-measured-execution.yml, sha256 3daa31ba8e0f7d93bf9377363a4b24e2f7dce20188cbf33555034c3f817c3bd8. Verification workflow: .github/workflows/e11-environment-verification.yml, sha256 9b208edcf9b481bf40e8ddf5a9de460410f4d653cc7400de005397b14b3385b7.
- Cells file: experiments/E11-security/conditions-draft.json, sha256 48beef74993b30b326a34c2f3844c38334bf61304f72a357a410f08fe21a5f48.
- agent_role in run manifests: ORCHESTRATOR.

### Cells (fourteen; N = 50 each; 700 executions; attempt 1)

| Cell | SUT | Kind | Method | Rule (M2) | Target | Expected category means | N |
|---|---|---|---|---|---|---|---|
| E11-SUT01-IDOR-ORDER-M1 | SUT-01 | CONDITION | M1 | - | GET /api/orders/{id} | the oracle is read as solved (SUT-05) or the GET answers 200 (SUT-01) | N = 50 |
| E11-SUT01-IDOR-ORDER-M1-CTRL | SUT-01 | CONTROL | M1 | - | GET /api/orders/{id} | the oracle stays unsolved (SUT-05) or the GET answers 403 (SUT-01) | N = 50 |
| E11-SUT05-SQLI-LOGIN-M1 | SUT-05 | CONDITION | M1 | - | M1 sequence | the oracle is read as solved (SUT-05) or the GET answers 200 (SUT-01) | N = 50 |
| E11-SUT05-SQLI-LOGIN-M1-CTRL | SUT-05 | CONTROL | M1 | - | M1 sequence | the oracle stays unsolved (SUT-05) or the GET answers 403 (SUT-01) | N = 50 |
| E11-SUT05-SQLI-LOGIN-M2 | SUT-05 | CONDITION | M2 | 40018 | POST /rest/user/login | an alert of the expected rule, method and normalized path | N = 50 |
| E11-SUT05-SQLI-LOGIN-M2-CTRL | SUT-05 | CONTROL | M2 | 40018 | POST /api/Users | no alert of that rule on the control endpoint | N = 50 |
| E11-SUT05-SQLI-SEARCH-M1 | SUT-05 | CONDITION | M1 | - | M1 sequence | the oracle is read as solved (SUT-05) or the GET answers 200 (SUT-01) | N = 50 |
| E11-SUT05-SQLI-SEARCH-M1-CTRL | SUT-05 | CONTROL | M1 | - | M1 sequence | the oracle stays unsolved (SUT-05) or the GET answers 403 (SUT-01) | N = 50 |
| E11-SUT05-SQLI-SEARCH-M2 | SUT-05 | CONDITION | M2 | 40018 | GET /rest/products/search | an alert of the expected rule, method and normalized path | N = 50 |
| E11-SUT05-SQLI-SEARCH-M2-CTRL | SUT-05 | CONTROL | M2 | 40018 | GET /rest/user/security-question?email= | no alert of that rule on the control endpoint | N = 50 |
| E11-SUT05-DIRLIST-FTP-M1 | SUT-05 | CONDITION | M1 | - | M1 sequence | the oracle is read as solved (SUT-05) or the GET answers 200 (SUT-01) | N = 50 |
| E11-SUT05-DIRLIST-FTP-M1-CTRL | SUT-05 | CONTROL | M1 | - | M1 sequence | the oracle stays unsolved (SUT-05) or the GET answers 403 (SUT-01) | N = 50 |
| E11-SUT05-DIRLIST-FTP-M2 | SUT-05 | CONDITION | M2 | 0 | /ftp/ | an alert of the expected rule, method and normalized path | N = 50 |
| E11-SUT05-DIRLIST-FTP-M2-CTRL | SUT-05 | CONTROL | M2 | 0 | GET /assets/ | no alert of that rule on the control endpoint | N = 50 |

- environment_type SELF_HOSTED for every cell, on a GitHub-hosted runner provisioned in the job; the controlled-instance record is experiments/E11-security/controlled-instance-status.yaml (all fourteen cells VERIFIED by DRY_RUN round 2, run 45417209148). No PUBLIC_HOSTED instance is ever a target.
- Matching rules (campaign-configuration-draft.md, section 4b): an M2 alert counts only when its rule id, request method and normalized path all equal the cell's expectation, every other alert is recorded and never counted; an M1 SUT-05 cell is decided by the solved flag read with a bounded wait of 5 s after one sequence; the SUT-01 cell is decided by the status of the GET. E11-SUT05-DIRLIST-FTP-M2 expects rule 0 on /ftp/ although the source reading predicted and two DRY_RUN rounds observed no alert; a non-detection is a valid outcome and the expectation is not changed.
- Order of dispatch within an authorization: the order of the cells file for the assigned SUT, one cell at a time (SUT-01: 2 cells; SUT-05: 12 cells); chains of the two SUTs are independent.
- Reporting: counts of each category per cell out of N = 50, with the Wilson 95% interval of each proportion, descriptive; the false-positive count on each control; the H5 count (each configured ground-truth condition counts once, the controls do not; E11-D-2b); no composite, ranking or hypothesis label beyond H5.
- Stop conditions: those of the frozen dispatch procedure (protocol/agent-governance-v6.md, Sections 3.5 and 3.7).
- Not decided by this record: any dispatch authorization, any further attempt, the campaign freeze.
