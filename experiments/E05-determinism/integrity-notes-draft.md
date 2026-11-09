# H3 validity: integrity notes for E05 (and E04)

| Field | Value |
|---|---|
| Document | integrity-notes-draft.md |
| State | DRAFT. Advisory only. It changes no protocol, no manifest and no campaign state, and it decides nothing. |
| Scope | Risks to the validity of H3 (protocol/study-design-v1.md, section 6, note (e): for SUT-01 conditions classified a priori as deterministic, CEOR = 1.00 and H(Y) = 0) and the controls that exist or are recommended. |
| Companions | design-brief-draft.md (brief s.N), campaign-configuration-draft.md (config s.N) |
| Provenance | Same disclosure as brief s.0. The human research lead has seen the descriptive E03 H2 reset-side result, and DEVELOPMENT and DRY_RUN observations are documented in the executor README (sections 11 and 12). None of the classes, categories or expected values below is derived from them. |

Terms: SUT = system under test. S, M, T, CEOR, H(Y) are defined in brief s.5.

## 1. Risk register

Status column: P = a protocol control already exists; R = recommended here; HUMAN DECISION = needs a human decision (brief s.11 item in parentheses).

| ID | Risk | How it could enter | Effect on H3 | Control | Status |
|---|---|---|---|---|---|
| R1 | Conditions chosen after outcomes are seen | DEVELOPMENT runs happen before the catalogue is locked. The executor README records that a realization was ruled after its DEVELOPMENT run's outcome was observed (executor README, section 11, item Q9). | A condition kept or dropped by its result inflates or deflates H3. | P: protocol section 2 (classes declared before execution); section 4 (expected outcome written before execution); change-control section 7 (locking at START). R: freeze the catalogue with a dated record before any E05 DEVELOPMENT run; keep DEVELOPMENT output out of every classification; list in the record the DEVELOPMENT runs that preceded the freeze. | P + R |
| R2 | Class chosen after outcomes are seen | A stochastic condition reads as deterministic after a run of identical categories. | Confirms H3 on a condition whose mechanism is random. | P: protocol section 2 says a declared class is not revised after execution begins, and a mismatch is itself a finding. R: class by mechanism only, with the evidence_id, and no class field editable after START. | P + R |
| R3 | Deterministic by construction | The stimulus returns what the harness wrote (an echo), or a static constant of the source, so CEOR = 1 is near-certain. | H3 is satisfied without exercising SUT logic. | R: a stimulus must exercise SUT logic, not echo the harness input (brief s.4.1). Static reads are flagged and their H3 inclusion is a human decision (D-10). Keep SUT01-API-06 as a discriminant control: a classifier that reports CEOR = 1 there has a defect. | R + HUMAN DECISION (D-10) |
| R4 | Outcome-category granularity | Too coarse: a random mechanism collapses into one category (CAPTCHA_ISSUED; VISUAL_MARKER_PRESENT with the price excluded). Too fine: run-varying fields (ORDER-<hex>, ITEM-<hex>, timestamps, tokens) make a deterministic SUT look non-deterministic. | Coarse hides non-determinism from H(Y) and CEOR. Fine yields CEOR below 1 by construction. | P: protocol section 2 (exact-match rule fixed per condition); section 4 (categories closed and pre-declared; no post hoc merge or split). R: explicit projection and exclusion list per condition (config s.7, s.9); the class follows the mechanism, not category variance (protocol section 2, "statistically reproducible randomness is not determinism"). | P + R |
| R5 | Residual state and reset adequacy | Orders survive the SUT-01 reset (SUT01-EV-0006); accepted bookings survive the SUT-04 CS-001 reset (executor README, 4.5 and 4.6); the SUT-03 Sign-Out question (PROTO-U21) is open. | Variance from the experimenter's procedure is recorded as SUT non-determinism, or hidden. | P: protocol section 5, rule 1 (start from the declared reset); executor README, section 3, item 11 (starting-state check, ABORTED with cause). R: residual inventory in config s.4 (brief s.4.4); HUMAN DECISION D-02 and D-03 before START; no SUT-03 condition until PROTO-U21 is resolved. | P + R + HUMAN DECISION |
| R6 | Small denominators | Establishment succeeds in only a few attempts; CEOR = M / S on a small S can be 1 by chance. | H3 is "satisfied" on very little. | P: protocol section 4 (CEOR denominator is S; NOT_ESTIMABLE only at S = 0). Gap: protocol sets no minimum S. R: S = T as the minimum (HUMAN DECISION D-06). | P gap + HUMAN DECISION |
| R7 | Point criterion at N = 50 | A condition with a small unexpected-outcome rate can satisfy M = S with substantial probability (brief s.5.6, formula q^S). | H3 "satisfied" is weaker evidence than its wording suggests. | P: SAP section 3 (Wilson interval per rate). R: report the interval beside every H3 result, and word a satisfied H3 as "no unexpected outcome in S executions", never as a proof of determinism. | P + R |
| R8 | Time-dependent confounds | Client timeouts (SUT01-API-04, if its timeout is set near the 3.0 s delay); the SUT-05 readiness budget of 180 s and the 6 h token expiry (audit section 4 Determinism, row SUT05-EV-0024); the SUT-04 date validation (D-13). | A timing boundary turns into an outcome difference. | P: protocol section 5, rule 8 (timestamps not in metrics); section 6 (speed is not a determinism criterion). R: timeout values declared before START; timeout as its own category; the time-dependent class where a timer or timeout decides the category (E05-SUT04-WEB-01 and -API-01, pending D-13). | P + R |
| R9 | Tool drift over N attempts | Browser build, CPython, runner image or Node version changes between attempts (brief s.8). | Drift looks like SUT non-determinism. | P: protocol section 5, rule 3 (manifest with toolchain). R: pin P1 to P6 before START; a per-condition drift report in the script (brief s.5.7). | P + R |
| R10 | Attribution after seeing a pattern | Tooling labels are chosen to remove unexpected outcomes, or attempts are excluded from denominators. | Selective denominators. | P: protocol section 5, rules 4 and 5 (failures are outcomes; no discard). R: mechanical criteria fixed before START, uncertain goes to SUT, raw rates primary (brief s.6). Option C of brief s.6 rejected. | P + R + HUMAN DECISION (D-16) |
| R11 | Pre-executor failures handled selectively | Failed attempts before the manifest exists are dropped, or re-dispatched under the same index. The E03 precedent is attempt 2 after two attempts left no bundle (E03 README, Current status). | Attempts disappear from TSRR and E2E-ROR; CEOR is unaffected by design. | P: protocol section 5, rules 5 and 6; section 4 (valid measured attempt needs a manifest). Gap: the rules conflict for this case. R: stub record counted as interrupted in T (brief s.5.9). | P gap + HUMAN DECISION (D-09) |
| R12 | Expected category anchored on the first result | The expected category is set to whatever the first attempt produced. | CEOR = 1 becomes a tautology. | P: protocol section 4 (expected outcome never derived from observed executions). R: expected value and its source line recorded before START and frozen with the configuration; a changed expected value is a deviation. | P + R |
| R13 | Undocumented randomness in a deterministic class | The E01 evidence is documentation and source reading; no run tested the deterministic classes. A rare random branch can be missed. | A deterministic class is wrong and H3 is confirmed on it. | P: E01 is SOURCE_VERIFIED or DOCUMENTED per row (protocol evidence rules); E05 is the first test of these classes. R: a source check of each deterministic mechanism before START (absence-based classes first, brief D-11). Note that N = 50 with a rare branch of rate q may show none (formula (1 - q)^N). | P gap + R + HUMAN DECISION (D-11) |
| R14 | Provenance of E04 data | E04 TSRR derived from E05 attempts without an E04 raw-data path, or E05 data written under E04. | Provenance break. | P: protocol section 9 (raw-data/<campaign-id>/). R: D-20; no derived E04 table without its own raw path. | P + HUMAN DECISION (D-20) |
| R15 | Cross-ecosystem reading of H3 | SUT-02 or SUT-05 deterministic results read as support or refutation of H3, or CEOR compared across ecosystems. | H3 is a SUT-01 prediction only; the comparison is a new, unplanned claim. | P: protocol section 6, note (d); SAP section 4.2 (any other comparison EXPLORATORY). R: config s.11 states that no cross-ecosystem comparison is confirmatory; every table shows class and k. | P + R |
| R16 | Unequal evidence depth across ecosystems | The E01 rows per SUT differ (for example SUT-01 has 30 rows; SUT-02 has 21 rows in its evidence file). Some classes rest on an audit statement with no row. | Classes are confirmed to different depths. | P: protocol/cross-cutting-properties-v1.md, "Recording" (every property cites evidence_id; absence recorded as absence). R: mark every class "row" or "audit s4, no evidence row" (brief s.4.1) and report the mark with each result. | P + R |
| R17 | Analysis code or runtime drift | The script changes after results are seen, or runs on an unpinned runtime (the E01 generator ran before its runtime pin was recorded: manifests/toolchain-manifest.yaml, PROTO-U06). | Results can't be reproduced. | P: analysis/README.md rule 3 (runtime recorded before the first run). R: script hash and runtime recorded before its first run; fail-closed consistency checks (brief s.5.7). | P + R |
| R18 | Publication of tokens or identifiers | Evidence and categories carry tokens, cookies or private addresses. | Disclosure; export failure. | P: executor scrubber (executor README, section 9); export invariance and the publication classes (PUBLIC-EXPORT-MANIFEST.yaml). R: the scrubber applies to E05 evidence without change. | P + R |
| R19 | Run without the required approvals | A job runs N attempts under a dispatch that did not name N or the condition; or a dispatch is re-run. | Governance breach; unrecorded attempts. | P: agent-instructions file, CAMPAIGN-CI-WRITE-AUTH-01 (dispatch needs explicit approval; no re-run; first attempt only). R: a per-SUT dispatch authorization that names the conditions and N, as announced for the minimum set. | P + R |
| R20 | Mobile conditions added without admissibility | A mobile E05 condition runs without the runner and the per-SUT compatibility smoke. | Non-admissible data. | P: protocol/mobile-runner-policy-v3.md; experiments/README.md, Common rules. R: no mobile condition in this configuration (config s.13, item 10). | P + R |

## 2. Controls the protocol already provides

- **Declared before execution:** behavior classes (protocol/repeatability-determinism-v1.md, section 2), expected outcomes and categories (section 4), repetition targets and sample size (section 3), and comparison classes (SAP section 4.2).
- **Locked at START:** campaign configuration, classes and comparisons (protocol/change-control-v1.md, section 7; SAP section 4.2 and section 6). A change after START is a protocol deviation, reported as such.
- **No discard:** every attempt counts; failures are outcomes; interruptions are recorded (protocol section 5, rules 4 to 6).
- **Denominator definitions:** TSRR over all valid measured attempts, CEOR over successful establishments, E2E-ROR over all attempts, H(Y) over the successful establishments with k stated (protocol section 4).
- **NOT_ESTIMABLE is not zero:** protocol section 4 and SAP section 3 forbid an interval for it.
- **Single-ecosystem H3 with a point criterion, and a falsification rule:** protocol/study-design-v1.md, section 6, note (e): one valid unexpected categorical outcome on a condition that established its target state means the condition does not satisfy H3.
- **Reporting of negatives:** SAP section 5 (contradicting results reported with equal prominence).
- **Speed and timestamps excluded from metrics:** protocol section 5, rule 8, and section 6.
- **Interval for every rate:** SAP section 3 (Wilson, 95 percent).
- **Controlled instance:** protocol/study-design-v1.md, section 10.3 (reset and state-changing operations on controlled instances only; never PUBLIC_HOSTED).

## 3. Controls recommended beyond the protocol

Each one is a proposal and needs a human decision where marked (brief s.11).

1. **Freeze the catalogue before any E05 DEVELOPMENT run** and keep a list of the DEVELOPMENT runs that happened before it (R1). Not a protocol change; a configuration record.
2. **Mechanism-based class, with the evidence mark** (row or audit s4, no evidence row) written next to each class (R2, R16).
3. **Source check of each deterministic mechanism before START** (R13, D-11). The check is an authorized read of the pinned source, not a clone, and its outcome is recorded before START.
4. **Explicit projections and an exclusion list** per condition, reviewed once before START (R4).
5. **A minimum denominator** (R6, D-06). Recommended S = T.
6. **Uncorrected Wilson intervals**, stated in the record (R7, D-05).
7. **Pinned browser build and interpreter, and a drift report** (R9; pins P1 to P6 in brief s.8).
8. **Mechanical attribution labels fixed before START, uncertain goes to SUT** (R10, D-16).
9. **Stub records for pre-executor failures counted as interrupted attempts** (R11, D-09).
10. **Expected values with their source line, computed before START** (R12).
11. **Fail-closed consistency checks in the analysis script** (R17; brief s.5.7).
12. **A residual-state inventory and its controls before the dispatch model is chosen** (R5; D-02, D-03).
13. **Explicit wording rules** for H3 results: "no unexpected outcome in S executions", the interval beside the point value, and no cross-ecosystem reading (R7, R15).
14. **Discriminant control** SUT01-API-06 in every E05 report: it must show a non-deterministic class, or the classifier is defective (R3).

## 4. What H3 can and cannot show

- **It can:** show that, in the executions made, a deterministic-classified condition produced no unexpected outcome in S establishment-successful executions. A single unexpected outcome falsifies it (protocol section 6, note (e)).
- **It cannot:** show that the SUT is deterministic. An absent failure over N attempts is compatible with a small non-zero rate (brief s.5.6). The interval, not the point value, carries the uncertainty.
- **It cannot separate tooling from SUT** unless the attribution rule of issue (xix) is decided and applied as a label (brief s.6). A tooling-attributed unexpected outcome still counts toward the H3 result under the recommended reading (D-16b).
- **It cannot compare ecosystems.** The same metrics for SUT-02 and SUT-05 are descriptive. Cross-ecosystem reading of CEOR is EXPLORATORY unless pre-registered.
- **It depends on the classes.** A class wrongly declared deterministic is the largest single threat (R13). The classes in brief s.4.2 rest on E01 rows for SUT-01 and on audit statements for some other conditions.

## 5. Pre-START checklist for the human research lead

The checklist lists what must be true before the START record is issued. It does not decide anything.

- [ ] Catalogue frozen with a dated record; DEVELOPMENT runs before it listed (R1).
- [ ] D-01 to D-20 decided and recorded (brief s.11).
- [ ] Each class has its evidence mark and, where marked "audit s4, no evidence row", a source check (R2, R13).
- [ ] Residual-state controls chosen for SUT-01 and SUT-04 (R5; D-02, D-03).
- [ ] No SUT-03 condition until PROTO-U21 is resolved or explicitly excluded (R5).
- [ ] Expected values and selectors that are "TBD" in the configuration have their source lines recorded (R12; D-12).
- [ ] Pins P1 to P6 recorded (brief s.8; R9).
- [ ] Analysis script written and hashed before its first run; its runtime recorded (R17).
- [ ] Controlled instance verified on GitHub Actions for every condition (config s.6; R19).
- [ ] Per-SUT dispatch authorization issued for the campaign, naming conditions and N (R19).
- [ ] Mobile conditions absent (R20).
