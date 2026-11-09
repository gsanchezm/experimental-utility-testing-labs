# E07 Cross-layer Continuity (web and API): design brief

| Field | Value |
|---|---|
| Status | DRAFT. Not a protocol, not frozen, not a campaign configuration. Authorizes nothing: no START, freeze, record, workflow, or dispatch. |
| Campaign | E07-cross-layer-continuity (experiments/E07-cross-layer-continuity/README.md), NOT_STARTED |
| Scope | Web and API layers only, per the human research lead's decision of 2026-11-05. Mobile pairs are not evaluated here. |
| Hypothesis served | H4, continuity part (protocol/statistical-analysis-plan-v1.md, section 4.3; protocol/study-design-v1.md, section 6) |
| Prepared | 2026-11-05 |
| Companion files (same folder) | CS-006.yaml (DRAFT canonical scenario CS-005 with six mapping entries); campaign-configuration-draft.md (campaign configuration skeleton) |
| Abbreviations | SUT = system under test; SAP = protocol/statistical-analysis-plan-v1.md; DP = design point; E01 IDs = evidence_id values |

## 1. Findings

1. **The pair premise holds, as a pair-availability statement.** Every candidate layer pair in the E07 README (API -> Web, API -> Android, API -> iOS, Web -> API) involves the API layer. SUT-02 has no API (manifests/sut-manifest.yaml, SUT-02 api presence ABSENT; E01 API cell provisional Score 0 with SUT02-EV-0004 to SUT02-EV-0006). So SUT-02 has no E07 web/API pair. SUT-01 vs SUT-03 is the only H4 continuity pair (SAP 4.3) that avoids mobile.
2. **But SUT-03 cannot take part in continuity under the frozen mapping rules.** SUT-03's API has no write path that persists state (SUT03-EV-0031). Its cart and favourites are client-side only and never reach the API (SUT03-EV-0032). Its audit states that a change made through one layer "cannot be verified through the other layer", except for fixed accounts. So under the strict standard, SUT-03 is NOT_COMPARABLE in both directions, and **no CONFIRMATORY H4 continuity comparison is evaluable** in either direction. This must be reported as NOT_COMPARABLE with its reason, never as a zero or a failure (SAP section 5; protocol/equivalent-scenario-mapping-v1.md, section 5).
3. **The decisive design point is whether a "referenced" entity counts as established state (DP-4, HUMAN DECISION).** The E07 README (Required evidence) says identifiers are "created or referenced during establishment". The mapping rules and CS-001 and CS-003 require the business object to be established by the actor, not a fixture (CS-003 allowed_domain_mapping). Under the "referenced" reading, SUT-03 would be comparable through its fixed accounts (SUT03-EV-0006 to SUT03-EV-0008), and its consistency would hold by construction, not by continuity.
4. **Evidence gaps block three cells.** SUT-01 Web -> API has no E01 record: the audit gives only an architectural inference (audit section 4, Cross-layer State Continuity, branch audit/e01-sut01-omnipizza). SUT-04's admin booking listing has no E01 row. SUT-05's web basket has no E01 row. E01 is frozen, so closing these gaps needs a change-controlled supplement or an explicit human decision.
5. **Two canonical scenarios are needed, one per direction.** CS-005 (API -> WEB) is drafted. CS-006 (WEB -> API) is proposed and not drafted (section 5). A second scenario does not rescue SUT-03.
6. **Two controlled surfaces have no environment verification record.** SUT-03 API and SUT-05 WEB (section 13). E03 verified SUT-03 on the web surface and SUT-05 on the API surface only.
7. **Latency is not needed for H4.** Verification action counts are descriptive. Neither is in the H4 variable (section 7).
8. **Precision is limited.** At N = 50 per condition, the Wald approximation gives a 95% half-width of about 0.14 for one proportion near 0.5 and about 0.20 for a risk difference between two arms of 50. These are arithmetic values, not protocol values. The SAP names no minimum detectable difference and no interval method for the risk difference (section 8).

**Source limitation (HUMAN DECISION, section 17, item 1).** The common rules of this task forbid reading derived-data, but the task's reading list names derived-data/e01-adjudicated-matrix/E01-adjudicated-matrix.json. I followed the stricter rule and did not open that file. Every E01 value below comes from the SUBMITTED audit branches (audit/e01-sut0N-*), which are the matrix's inputs. The confirmed_score values quoted are the auditors' values and may differ from the adjudicated matrix. They must be checked before any freeze.

## 2. Scope, inputs, and method

- **Read:** experiments/E07-cross-layer-continuity/README.md; protocol/equivalent-scenario-mapping-v1.md (all); experiments/scenario-mappings/CS-001.yaml and CS-003.yaml; protocol/statistical-analysis-plan-v1.md (all, sections 2 to 6); protocol/study-design-v1.md (sections 4 to 11); protocol/repeatability-determinism-v1.md; protocol/cross-cutting-properties-v1.md; manifests/sut-manifest.yaml; manifests/toolchain-manifest.yaml; schemas/run-manifest.schema.v2.json (layer fields, lines 479 to 506); experiments/README.md; experiments/E03-resetability/README.md (campaign configuration headings, exclusion and CONFIRMATORY sections); experiments/E03-resetability/executor/README.md (sections 3, 4, 6); experiments/E03-resetability/controlled-instance-status.yaml (partial); E01 audit.md of SUT-01 and SUT-03 in full; the web and API modality rows and cross-layer sections of SUT-02, SUT-04 and SUT-05; evidence.csv rows for the IDs cited here, read from the audit/e01-sut0N-* branches (read-only git). SUT-06 is taken from manifests/sut-manifest.yaml only.
- **Not read:** derived-data/ (section 1, source limitation); raw-data/; the E03 measured workflow beyond its gate comments; ci-cd-execution-model.md (its gate design is summarized from the workflow comments only).
- **Citation form:** file path and section, or evidence_id with its branch. "Not stated" means the repository does not say it.

## 3. Layer pairs in scope per ecosystem

| SUT | Web / API (manifest presence) | Audit scores (SUBMITTED, provisional = confirmed unless noted) | Direction API -> WEB | Direction WEB -> API | Status |
|---|---|---|---|---|---|
| SUT-01 OmniPizza | CONFIRMED / CONFIRMED | Web UI 3, API 3 | Evidenced: establishment via POST /api/cart and GET /api/session (SUT01-EV-0004, -0006); token injection (SUT01-EV-0002); session authentication (SUT01-EV-0007). SOURCE_VERIFIED. | Not evidenced: no E01 row. The audit's cross-layer text is an architectural inference, not an executed trace (audit section 4). The E03 realization records a client-persisted web cart (experiments/E03-resetability/executor/README.md, section 4.2), so whether a UI add-to-cart reaches the server cart is not stated. | CS-005 candidate; CS-006 gap |
| SUT-02 Sauce Labs | CONFIRMED / ABSENT | Web UI 3; API 0 (structural) | Not applicable (no API) | Not applicable | NOT_COMPARABLE (NO_APPLICABLE_SURFACE) |
| SUT-03 BrowserStack | CONFIRMED / CONFIRMED (one Next.js process, same commit) | Web UI 3, API 3 | No state the actor can establish through the API (SUT03-EV-0031). Fixed-account responses only (SUT03-EV-0006 to -0008). | Cart and favourites are client-side (SUT03-EV-0032). The API cannot observe them. | NOT_COMPARABLE under the strict standard (DP-4) |
| SUT-04 Restful Booker | CONFIRMED / CONFIRMED (one monorepo) | Web UI 3, API 3 | Booking CRUD via API (SUT04-EV-0006, -0008, -0003). Admin login route (SUT04-EV-0002). Admin booking listing: no E01 row. | Reservation form inputs (SUT04-EV-0018, an accessibility row). Web proxies to the same backend (SUT04-EV-0028). | CS-005 candidate (DP-7); CS-006 candidate |
| SUT-05 OWASP Juice Shop | CONFIRMED / CONFIRMED (one Node process and datastore; SUT05-EV-0003) | Web UI 3, API 3 | Basket via API (SUT05-EV-0006, -0008, -0027). Web basket view: no E01 row. | Web add-to-basket: no E01 row. | CS-005 gap (DP-7); CS-006 gap |
| SUT-06 WebdriverIO native demo | ABSENT / ABSENT | mobile only | Not applicable | Not applicable | NOT_COMPARABLE (NO_APPLICABLE_SURFACE) |

Specialist ecosystems (SUT-04, SUT-05) are EXPLORATORY in any comparison unless pre-registered (SAP 4.2, rules 1 and 3). Their structural continuity is described in their audits' cross-layer sections: SUT-04 via SUT04-EV-0028 and SUT-05 via SUT05-EV-0003 and the account-state rows.

## 4. What continuity means, operationally

- **Observable (per attempt).** After establishment through the source layer, a read-only observation on the verification layer shows the same unit, with the identity keys and attributes declared before the attempt. The check is the cross-layer consistency check of OTHER (CS-006.yaml, `observable_oracle_class_text`).
- **Outcomes (proposed, X-2 and X-3 in the configuration):** VERIFIED (every key and attribute matches); NOT_VERIFIED (observation completed, a key or attribute is absent or different); ESTABLISHMENT_FAILED (the source-side check did not confirm the unit); INTERRUPTED; RUNNER_ERROR.
- **Continuity success** is a proportion per condition (SAP 4.3). Its denominator is not defined in the SAP. Recommendation: VERIFIED / all valid measured attempts (DP-8). The conditional version is reported descriptively.
- **Verification is read-only.** Any state change during verification would invalidate the attempt.
- **Timing is not part of the criterion.** Timing does not enter the success definition, as in protocol/repeatability-determinism-v1.md, section 6.

## 5. Second scenario, and why

- **Why a second scenario is needed.** H4 continuity is directional. The canonical record is one intent per record (protocol/equivalent-scenario-mapping-v1.md, sections 3 and 6), and the per-ecosystem mapping template has no direction field (section 7). So each direction needs its own canonical record (DP-3). The layer pair stays an independent variable of the campaign (E07 README, "Future independent variables").
- **CS-006 (WEB -> API), proposed, not drafted.** Intent: an actor establishes one unit through the user interface and the same unit is read back through the API. Status by SUT: SUT-04 likely COMPARABLE (reservation form, SUT04-EV-0018 and the proxy SUT04-EV-0028, read via SUT04-EV-0006; the form flow itself is not its own E01 row). SUT-01 gap (section 3). SUT-05 gap (no E01 row for web add-to-basket). SUT-03 NOT_COMPARABLE (SUT03-EV-0032). SUT-02 and SUT-06 NOT_COMPARABLE.
- **Does a second scenario help H4?** Only for SUT-04 and possibly SUT-01, which are specialists or the candidate. It does not give the confirmatory SUT-01 vs SUT-03 comparison any data, because SUT-03 is NOT_COMPARABLE in both directions.
- **Optional third scenario (not needed for H4).** An order-based scenario (checkout creates an order, read through the order listing) would give SUT-01 a second object (order_id, SUT01-EV-0023). It would not change SUT-03's status, because SUT-03 keeps its orders client-side (audit section 4, Functional Complexity).

## 6. Traceable identifiers

| SUT and direction | Identity keys (candidate) | Observable on the verification layer? | Note |
|---|---|---|---|
| SUT-01, API -> WEB | Session sid (JWT claim), which both layers share because the same token is used (SUT01-EV-0002, -0007); cart line pizza_id, size, quantity | sid: not visible in the UI (not stated); the line is visible on Checkout (SUT01-EV-0004) | Reset before each attempt. A stale line from an earlier attempt would be an identity risk, so the empty starting state must be checked (X-4). |
| SUT-01, WEB -> API | Session sid from the browser token; order_id (ORDER-<8 hex>, audit section 4) | Not evidenced | Gap (section 3) |
| SUT-04, API -> WEB | Run-unique guest names and check-in date (from the run id; E03 precedent, executor README section 4.6); bookingid (integer, from the 201 response) | Names and date: admin listing, not evidenced by an E01 row. bookingid: not stated in the UI. | DP-7 for the listing |
| SUT-04, WEB -> API | Same names and date; bookingid found by a GET on the room list matched on those values (E03 precedent) | API: yes (SUT04-EV-0006) | CS-006 candidate |
| SUT-05, API -> WEB | Basket id (bid, from the login response); ProductId, quantity | Web: not evidenced | DP-7 |

## 7. Latency (secondary): needed?

**Not needed for H4.** H4 uses only the continuity proportion (SAP 4.3). The SAP's duration rows name E02, E03, and E08 as sources (SAP section 2); E07 is not among them. If a duration is recorded, SAP section 3 gives its reporting (median and IQR, BCa bootstrap), and it would be EXPLORATORY. Its boundaries would also need definition (for example, from the establishing response to the first verification observation). Page-load timing on the web layer depends on the environment, so it would be confounded. **Recommendation:** do not record latency in the first campaign. HUMAN DECISION (section 17, item 6).

## 8. Sample size and precision

- **N = 50 per condition**, the standard target (protocol/repeatability-determinism-v1.md, section 3). The reduced N = 30 applies only to expensive mobile conditions, and E07 has none in scope (SAP 4.1 also refers to N = 50).
- **Conditions and attempts (candidate):** CS-005: SUT-01 (50), SUT-04 (50 if DP-7 resolves), SUT-05 (50 if DP-7 resolves). CS-006 if drafted: SUT-04 (50), SUT-01 (50 if its evidence gap closes). Maximum about 250 attempts for the two directions, with reset and verification per attempt. No confirmatory condition exists for SUT-03 under the strict standard.
- **Precision (arithmetic only):** section 1, item 8. The SAP gives Wilson intervals for proportions and a risk difference "with its 95% CI" but names no method for the difference. **Recommendation:** a Newcombe-type hybrid score interval built from the two Wilson intervals, fixed in the configuration (HUMAN DECISION).
- **Power:** not stated. HUMAN DECISION: pre-register a minimum detectable difference, or accept descriptive interpretation.

## 9. Exclusion and attribution rule (needed)

E04 and E05 have a deferred attribution rule (protocol/study-design-v1.md, section 13, issue (xix)), so E07 needs its own rule, frozen in its configuration before START (SAP 4.2, rule 3). Proposed (full text in campaign-configuration-draft.md, section 7): no valid attempt is excluded (repeatability section 5, rules 4 to 6); one outcome category per attempt; a failed starting-state check is an INTERRUPTED attempt, kept, followed by a reset; RUNNER_ERROR counts in every primary rate, with a sensitivity table reported as EXPLORATORY (HUMAN DECISION, item 7); cell-level no-data states (NOT_COMPARABLE, NOT_APPLICABLE_STRUCTURAL, NOT_EXECUTABLE_WITHOUT_CONTROLLED_INSTANCE) are not attempts and never zeros.

## 10. Confirmatory list and evaluability

H4 pairs (SAP 4.3): SUT-01 vs SUT-02 and SUT-01 vs SUT-03, on the continuity proportion per layer pair. The configuration pre-registers each comparison (section 13 of campaign-configuration-draft.md).

| Comparison | Scenario and direction | Evaluable today? |
|---|---|---|
| SUT-01 vs SUT-02 | CS-005 API -> WEB; CS-006 WEB -> API | No. SUT-02 has no API (A-1, A-4). |
| SUT-01 vs SUT-03 | CS-005 API -> WEB; CS-006 WEB -> API | No, under the strict standard (DP-4 option a) (A-3, A-6). |

So under the strict standard the H4 continuity comparisons have no evaluable data. The result is "no data, with reason", not "continuity absent". This is the main implication for the human research lead. Whether to keep the strict standard is the decision (DP-4); the consequences of the fixture-referencing option are in section 1, item 3.

Holm family (SAP 4.2): the family is defined per research question, and RQ4 also contains the E06 parity comparisons. Recommendation: list only evaluable comparisons in the family and name the others. HUMAN DECISION (item 9).

## 11. Structurally absent layers: how they are recorded

Each NOT_COMPARABLE pair gets a pair-level absence record, not a run manifest (E07 README, "Explicit record for every layer pair that is absent, not applicable, or not testable, with reason"). Records are listed in campaign-configuration-draft.md, section 9 (A-1 to A-7). Each record cites its reason and its evidence_ids and keeps the E01 structural_scope_note. These are reported as "no data — <reason>" (protocol/study-design-v1.md, section 11, rule 2). They never change a capability score, and they are never a zero (protocol/equivalent-scenario-mapping-v1.md, section 5).

## 12. Executor design, and what can be reused from E03

E03's realizations are locked by E03's own implementation hash and frozen records. E07 needs its own implementation, which may copy E03's code and must lock its own hash. Nothing is imported from the E03 path at run time.

| E07 need | Reuse from E03 (experiments/E03-resetability/executor/README.md) | Gap or change |
|---|---|---|
| SUT-01 API establishment and check | Section 4.1: login, POST /api/cart, GET /api/session (read-only) | Reset steps are not needed inside the scenario |
| SUT-01 WEB verification | Section 4.2: token injection (the W-A realization), navigation to Checkout, reading the Checkout view | The reset part is not needed. Navigation is counted descriptively (executor README, section 3, item 3: navigation rule). |
| SUT-01 WEB -> API | Not in E03. CS-001 used API seeding only. | New realization; needs E01 evidence (section 3) |
| SUT-04 API establishment and check | Section 4.5: login, POST /booking/, GET by id | None |
| SUT-04 WEB verification (admin listing) | Section 4.6, pre-reset verification part | Cookie: E03 logged in through the UI. The cookie injection of the API token is not evidenced (SUT04-EV-0002 only states that the login sets a token cookie). Choose option (a) or (b) (DP-7). |
| SUT-04 WEB establishment (reservation form, for CS-006) | Section 4.6, establishment part | Requires the CS-006 record |
| SUT-05 API establishment and check | Section 4.7, without the restart | The WEB surface is new (DP-7) |
| Between-attempt reset | Section 4.1 (POST /api/session/reset), 4.5 (DELETE booking), 4.7 (process restart, heavy) | Reset is outside the scenario and not counted |
| Instance interface, bundle, manifest | Section 6 (instance.json, interface version 1); section 3 (counting conventions); manifest schema v2 | Add source_layer and verification_layer (mandatory for E07 by campaign convention) |

Principles carried over from E03: read-only verification; the starting state checked before establishment; no retries except as predeclared; every API call recorded (request and response); run-unique values written to a precondition record; no PUBLIC_HOSTED instance.

## 13. Environment verification gaps

| Surface | Status (experiments/E03-resetability/controlled-instance-status.yaml) | Consequence for E07 |
|---|---|---|
| SUT-01 web and api | VERIFIED on GitHub Actions (E03 conditions) | Realization steps still need an ENVIRONMENT_VERIFICATION record |
| SUT-04 web and api | VERIFIED on GitHub Actions | Same; the admin listing was not part of E03's verification |
| SUT-05 api | VERIFIED on GitHub Actions (run 37354458611, manifest note) | Same |
| **SUT-05 web** | **No record** (E03 mapped SUT-05 on the API surface only; CS-001.yaml) | Required if SUT-05 is COMPARABLE on CS-005 or CS-006 |
| **SUT-03 api** | **No record** (E03 mapped SUT-03 on the web surface only; CS-001.yaml) | Required only if SUT-03 is reopened under DP-4 option (b). The web surface is verified. |

## 14. Pins

Values are in campaign-configuration-draft.md, sections 2 and 3, from manifests/sut-manifest.yaml and manifests/toolchain-manifest.yaml. In brief: SUT-01 9ca37674...; SUT-03 7ab934d7...; SUT-04 d36bd3f8... (release 2.2); SUT-05 1618a611... (release v20.2.0; the GitHub Actions route uses the packaged distribution). Toolchain: Playwright for Python 1.63.0 (web); Python 3 standard library urllib (API); Ajv major 8 (version null, not installed); Node.js v23.6.1 (analysis only). Chromium is not hash-pinned. The pins stay DRAFT until START.

## 15. Workflow gates (names only)

Fourteen gate names, E07-G-01 to E07-G-14, are listed in campaign-configuration-draft.md, section 11. They follow the E03 gate pattern (G-1 to G-11) and add E07-G-04 (pair-level absence records), E07-G-12 (per-SUT dispatch authorization, pending the governance successor), E07-G-13 (SUT isolation), and E07-G-14 (first attempt only). No workflow exists, and writing one authorizes no execution (experiments/README.md, execution substrate; CAMPAIGN-CI-WRITE-AUTH-01).

## 16. Effort estimate (ORCHESTRATOR estimate, not measured, not a protocol value)

| Step | Size | Human approval needed |
|---|---|---|
| 1. Decide DP-1 to DP-9 and the X rules | S | Yes (blocks all later steps) |
| 2. Close or accept the evidence gaps (DP-7; SUT-01 WEB -> API; SUT-04 listing; SUT-05 web) | M to L | Yes; may need a change-controlled supplement |
| 3. Freeze CS-005 (mapping record, change-log row) | S to M | Yes, per record |
| 4. Draft CS-006 (only if approved) | M | Yes |
| 5. Write the campaign configuration (identity keys, rules, conditions, CONFIRMATORY list) | M | Yes, at START |
| 6. Write the realizations (three to five, reusing E03) | M each | No, but they feed the configuration |
| 7. Write the E07 executor and instance and manifest handling | L | No |
| 8. Local DEVELOPMENT and SMOKE runs (never measured) | M | No |
| 9. Write the workflows (measured and environment verification) and DRY_RUN | M | Yes, per dispatch |
| 10. Environment verification of new realizations, per surface | M | Yes, per dispatch |
| 11. START record and configuration freeze | S | Yes |
| 12. Measured dispatches, one per SUT, N = 50 per condition; import and verification | M each | Yes, per dispatch |
| 13. Analysis per SAP (descriptive for non-evaluable comparisons) and tables | M | No, but results are reported under the SAP |

About 13 steps. Before the first measured dispatch, about six human approvals are needed: the design decisions, the CS-005 freeze, the configuration freeze, the START, the per-SUT dispatch authorizations, and the governance successor. The planning date (DATA FREEZE 2027-01-05, from the task brief) makes steps 1 to 3 the critical path.

## 17. HUMAN DECISIONS (consolidated)

Each item lists the options and the recommendation. The ORCHESTRATOR has decided none of them.

1. **Adjudicated matrix (source limitation).** Options: (a) keep the stricter rule and confirm the auditor values against the adjudicated matrix later; (b) permit a read of the adjudicated matrix for E07 design. Recommendation: (b), since the matrix is the study's confirmed-score record and the design depends on confirmed values.
2. **DP-4, the established-state standard (decisive).** Options: (a) strict: the actor establishes the unit through the programmatic interface, as CS-001 and CS-003 do; SUT-03 is NOT_COMPARABLE, so no H4 continuity comparison is evaluable. (b) referenced: a fixed entity counts; SUT-03 is comparable through its fixed accounts, and continuity holds by construction. Recommendation: (a). This is a protocol-level choice that changes what H4 can show, so it should be taken with the human research lead's view of H4.
3. **DP-1 precondition_class.** CLEAN_SESSION (login inside the scenario, as CS-003) or AUTHENTICATED_SESSION (as CS-001). Recommendation: CLEAN_SESSION.
4. **DP-2 actor_state.** AUTHENTICATED_STANDARD (as CS-003, including the SUT-04 administrator). Recommendation: keep.
5. **DP-3 direction records.** Options: separate CS-005 and CS-006 records, or one record with direction as a variable (needs a template change). Recommendation: separate records.
6. **Latency and verification counts.** Options: record latency (EXPLORATORY, with boundaries); record verification counts descriptively. Recommendation: no latency in the first campaign; verification counts descriptive, not Setup Effort.
7. **X-2 category set and X-5 RUNNER_ERROR treatment.** Recommendation: counted in primary rates; sensitivity table reported as EXPLORATORY.
8. **DP-7 evidence gaps (SUT-04 admin listing and cookie; SUT-05 web basket; SUT-01 WEB -> API).** Options: (a) a change-controlled E01 supplement; (b) source-line citations in the configuration, which departs from the mapping rule's E01-evidence wording; (c) NOT_COMPARABLE, reason OTHER, until closed. Recommendation: (c) for SUT-05; (a) for SUT-04 only if the specialist profile is wanted.
9. **Continuity denominator (DP-8) and interval method.** Recommendation: VERIFIED / all valid attempts for H4, conditional descriptive; a Newcombe-type hybrid interval for the risk difference.
10. **DP-5 identity keys and the exact-match rule.** Recommendation: declared per ecosystem before the first attempt; VERIFIED needs every key and attribute.
11. **Minimum detectable difference.** Options: pre-register, or descriptive only. Recommendation: pre-register if H4 is to be interpreted.
12. **Holm family and comparison identifiers (section 10).** Recommendation: family includes evaluable comparisons only, defined across E06 and E07; identifiers assigned by the human research lead.
13. **DP-9 scope.** The README's mobile pairs are outside this draft. Recommendation: add a scope note to the README by change control; a mobile record needs the mobile policy.
14. **Per-SUT dispatch authorization and governance successor.** Needed before any dispatch; the successor is not yet written.
15. **Campaign START and configuration freeze.** Not proposed here.
16. **CS-006 drafting.** Recommendation: draft after items 2, 5 and 8 are decided.
