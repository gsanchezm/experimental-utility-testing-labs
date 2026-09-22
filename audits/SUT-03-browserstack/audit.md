# SUT-03 — BrowserStack Demo Ecosystem — Audit

Audit status: SUBMITTED. Performed under campaign E01-capability-audit, protocol v1 (FROZEN-PRE-DATA), by AUDITOR-SUT03-BROWSERSTACK. Rules: audits/README.md, protocol/capability-rubric-v1.md, protocol/evidence-rules-v1.md, protocol/cross-cutting-properties-v1.md.

## 1. Header

| Field | Value |
|---|---|
| ecosystem_id | SUT-03 |
| ecosystem_name | BrowserStack Demo Ecosystem |
| role | general-purpose / Web / API baseline |
| auditor_role | AUDITOR-SUT03-BROWSERSTACK |
| protocol_version | v1 |
| rubric_version | v1 |
| evidence_rules_version | v1 |
| audit_status | SUBMITTED |
| started_at | 2026-09-17 |
| submitted_at | 2026-09-17 |
| environment_types_used | (none — no EXECUTION_VERIFIED evidence was collected; see limitations.md) |
| controlled_instance_available | null / TBD — not executed and therefore not verified in this session (protocol/study-design-v1.md, section 10.5: "null until verified and is never inferred"); see limitations.md |
| prompt_version | E01-CAPABILITY-AUDITOR-V1 (rendered launch package `experiments/E01-capability-audit/launch/AUDITOR-SUT03-BROWSERSTACK.md`, SHA-256 `323249c8bfe10a29d7c13e234cdc5a374ef79b596f839e63415aa0dff9514a4e`, verified before this audit began) |

Allowed values for audit_status: NOT_STARTED, IN_PROGRESS, SUBMITTED, ADJUDICATED. environment_types_used lists the distinct environment types (PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, OTHER; protocol/study-design-v1.md section 10) under which EXECUTION_VERIFIED evidence was collected; empty if none. controlled_instance_available is true or false once verified: true when every component surface that E01 confirmed present can be run by the study, from the pinned evaluated version, in a controlled environment (SELF_HOSTED or LOCAL for web and api service components; EMULATED or SIMULATED for android and ios application builds); false otherwise, naming the components that cannot in limitations.md (protocol/study-design-v1.md, sections 10.1 and 10.5); it is an experimental-control fact, never a score input. Dates as YYYY-MM-DD. Machine-readable form: schemas/sut-audit.schema.json.

## 2. Components and provenance

Each row is one surface to verify for the system under test (SUT); every ecosystem lists the same four surfaces so that presence and absence are verified identically. Provenance is copied from manifests/sut-manifest.yaml. presence values: CONFIRMED, ABSENT, UNCONFIRMED.

| component | presence | repository | commit_sha_or_release | endpoint | verified_by | verified_at |
|---|---|---|---|---|---|---|
| web | CONFIRMED | https://github.com/browserstack/browserstack-demo-app | 7ab934d733f2f74d4b912e94e86f59ae0f6b7609 (default branch master) | (none documented; manifest records endpoint: null) | AUDITOR-SUT03-BROWSERSTACK | 2026-09-17 |
| api | CONFIRMED | https://github.com/browserstack/browserstack-demo-app | 7ab934d733f2f74d4b912e94e86f59ae0f6b7609 (default branch master) | same origin, `pages/api/**` (Next.js API routes; no separate host) | AUDITOR-SUT03-BROWSERSTACK | 2026-09-17 |
| android | ABSENT | | | | AUDITOR-SUT03-BROWSERSTACK | 2026-09-17 |
| ios | ABSENT | | | | AUDITOR-SUT03-BROWSERSTACK | 2026-09-17 |

Notes:
- **web**: confirmed by cloning the pinned repository read-only to `../e01-sut-sources/SUT-03-browserstack/` and verifying `git rev-parse HEAD` equals the pinned commit `7ab934d733f2f74d4b912e94e86f59ae0f6b7609` exactly, matching `manifests/sut-manifest.yaml` and `manifests/e01-source-provenance.yaml`. It is a Next.js/React single-page application (`pages/`, `next.config.js`).
- **api**: `manifests/sut-manifest.yaml` and `manifests/e01-source-provenance.yaml` record no independently-pinned provenance artifact for SUT-03-api (repository/commit fields null, `eligibility_basis: "No component named for this study."`). This audit independently confirmed the api logical surface is CONFIRMED present by inspecting the pinned SUT-03-web commit itself: `pages/api/*.js` implements ten real API route handlers (signin, checkout, products, orders, offers, doc, plus five "control" sub-routes) at the same commit. Per `manifests/e01-source-provenance.yaml`'s own `terminology` note, "one provenance artifact may back more than one logical surface"; this audit therefore cites the SUT-03-web provenance artifact (same repository, same commit) for the api row above rather than leaving api provenance blank. See unresolved.md (row 1, non-blocking) for the resulting discrepancy against the still-null manifest api row, which only the ORCHESTRATOR may edit.
- **android / ios**: confirmed ABSENT by inspecting the full file tree of the pinned commit (128 tracked files) and `package.json`'s dependency list; see evidence SUT03-EV-0010 / SUT03-EV-0011 (structural_scope_note `NO_MOBILE_SURFACE`).

## 3. Modality assessments

| modality | provisional_score | confirmed_score | confirmation_state | evidence_status_summary | evidence_record_count | evidence_refs | verification_refs | rationale | structural_scope_note |
|---|---|---|---|---|---|---|---|---|---|
| Web UI Functional | 3 | 3 | CONFIRMED | SOURCE_VERIFIED (4), DOCUMENTED (1) | 5 | SUT03-EV-0001, SUT03-EV-0002, SUT03-EV-0003, SUT03-EV-0004, SUT03-EV-0005 | | Five named, deterministic test accounts (src/constants/users.js), each producing a distinct, pre-defined observable state on sign-in (broken images / pre-seeded orders / pre-favorited products / permanent lockout / baseline), directly match the rubric's Score 3 example "deterministic test account"; confirmed by reading the pinned source (pages/api/signin.js) without needing execution. | |
| API | 3 | 3 | CONFIRMED | SOURCE_VERIFIED (4) | 4 | SUT03-EV-0006, SUT03-EV-0007, SUT03-EV-0008, SUT03-EV-0009 | | The same account mechanism is exposed as API-based state seeding: `userName` query/body parameters on `/api/products`, `/api/orders`, `/api/checkout` deterministically select a pre-built response ("API-based state seeding", a rubric Score 3 example); documented via an auto-generated OpenAPI 3.0 schema at `/api/doc` and `/swagger`. | |
| Android Native | 0 | | | SOURCE_VERIFIED (1) | 1 | SUT03-EV-0010 | | No Android application code, build configuration, or cross-platform mobile framework dependency exists anywhere in the pinned commit; no Android component was named for this study (manifests/e01-source-provenance.yaml). | NO_MOBILE_SURFACE |
| iOS Native | 0 | | | SOURCE_VERIFIED (1) | 1 | SUT03-EV-0011 | | No iOS application code, build configuration, or cross-platform mobile framework dependency exists anywhere in the pinned commit; no iOS component was named for this study. | NO_MOBILE_SURFACE |
| Performance | 3 | 3 | CONFIRMED | SOURCE_VERIFIED (6), DOCUMENTED (1) | 7 | SUT03-EV-0012, SUT03-EV-0013, SUT03-EV-0014, SUT03-EV-0015, SUT03-EV-0016, SUT03-EV-0017, SUT03-EV-0018 | | Four `/sut/ui/*` pages implement fixed-duration, documented-in-copy Web Vitals conditions (a 4s layout shift, a 3s LCP delay, a zero-shift baseline, and a near-zero-INP baseline) gated only by a client-side cookie check, so they are genuinely reachable via the app's own documented `/sut/login` flow; `src/components/App/index.jsx` additionally branches deterministically on the Network Information API's `effectiveType`. A separate, larger family of "API Metric Control Endpoints" (documented in README.md and linked from `pages/sut/dashboard.jsx` as the intended way to drive controlled latency/error conditions "for k6/JMeter") is implemented with the documented deterministic and statistically-deterministic behavior in source, but is **never reachable**: its `checkSutAuth` gate depends on a server-side session that no code path in the pinned commit ever establishes (see section 5, contradiction). This audit's Score 3 rests only on the reachable `/sut/ui/*` + network-branch mechanisms (SUT03-EV-0012–0015); the unreachable API family (SUT03-EV-0016–0018) is documented but excluded from the score, per capability-rubric-v1.md ("the evaluated version must already expose it"). | |
| Accessibility — Web only | 2 | 2 | | SOURCE_VERIFIED (2) | 2 | SUT03-EV-0019, SUT03-EV-0020 | | The pinned commit has a stable, reasonably semantic page structure (some `aria-label`/`aria-live`/`alt` usage) that a scanner can evaluate deterministically across runs — beyond bare generic-tool reachability — but no documented or source-verified intentional accessibility fault with a pre-declared expected finding was found, so Score 3's "controlled accessibility fault" example is not met. | |
| Visual Testing | 3 | 3 | CONFIRMED | SOURCE_VERIFIED (3) | 3 | SUT03-EV-0021, SUT03-EV-0022, SUT03-EV-0023 | | `isImageNotLoadingUser()` (src/components/Shelf/Product/index.js), gated on the `image_not_loading_user` account, forces every product thumbnail to fail to render — a rubric Score 3 example ("controlled visual condition") verbatim, confirmed by reading the pinned source. A narrower Firefox-50-conditioned image-hide bug and the CLS/zero-CLS page pair (shared with Performance) corroborate. | |
| Security Testing | 2 | 2 | | SOURCE_VERIFIED (3) | 3 | SUT03-EV-0024, SUT03-EV-0025, SUT03-EV-0026 | | Real, stable, SUT-specific authentication/authorization logic exists (a fixed account allowlist, a permanently-locked test account with its own error message, an API-level `userName` gate on checkout) — more than generic tool reachability — but no documented or source-verified *intentional* vulnerability with an expected detection outcome was found anywhere in the pinned commit or its documentation, so Score 3's example ("documented intentional vulnerability") is not met. A repository CI workflow (Semgrep) statically scans the maintainers' own source and is not evidence of an application-level capability (AGENT-INSTRUCTIONS.md rule 4). See unresolved.md row 2 for a non-blocking note on this judgment. | |
| Localization / i18n | 1 | 1 | | SOURCE_VERIFIED (3) | 3 | SUT03-EV-0027, SUT03-EV-0028, SUT03-EV-0029 | | No language-switch UI, i18n library dependency, or non-USD currency value exists anywhere in the pinned commit (currency is hard-coded `USD`/`$` throughout). `/api/offers` gates content on real browser geolocation against 5 hard-coded city bounding boxes, but returns identical `offersData` for every matched city, so it provides no locale/market-*differentiated* ground truth and its selection is geolocation-derived rather than explicit. A generic tool can technically exercise this endpoint (e.g. by overriding geolocation via CDP), which is the definition of Score 1, not evidence for a higher score. | |

Scores are provisional until adjudicated by ADJUDICATOR-EU-01. No cell in this audit rests on DOCUMENTED-only evidence for a Score 3; every confirmed Score 3 above cites at least one SOURCE_VERIFIED record demonstrating the mechanism is implemented in the pinned commit, so no cell carries `confirmation_state = UNCONFIRMED_SCORE_3`.

## 4. Cross-cutting properties

Descriptive only; no property is scored (protocol/cross-cutting-properties-v1.md).

### State Controllability

Description (descriptive only, no score): The evaluated version's entire state-establishment surface is a small, fixed set of five named accounts (`image_not_loading_user`, `existing_orders_user`, `fav_user`, `demouser`, `locked_user`; src/constants/users.js). Passing one of these as the `userName` parameter to `/api/signin`, `/api/checkout`, `/api/products`, or `/api/orders` deterministically selects one of a small number of pre-built response states (broken product images, pre-seeded orders, pre-favorited products, a permanent lockout, or an ordinary baseline). There is no free-form fixture/seed API, no direct database write path, and no deep-link-to-arbitrary-state mechanism beyond this fixed account set: product/order/offer data are static, repository-bundled JSON, never mutated by any observed code path.
Evidence refs (evidence_id): SUT03-EV-0001, SUT03-EV-0003, SUT03-EV-0006, SUT03-EV-0007, SUT03-EV-0008, SUT03-EV-0031

### Resetability

Description (descriptive only, no score): State lives only in the browser (sessionStorage, via the `store2` library, plus a plain cookie for the separate `/sut/*` load-testing pages). The main app's Sign-Out action (`src/components/Header/index.jsx`) and the `/sut/dashboard` page's Logout button each clear this client-side state in one step (`store2.session.clearAll()`; cookie expiry). Because there is no server-side persisted state (no database; see State Controllability above), there is nothing beyond browser storage to reset, and product/order/offer seed data cannot become "dirty" in the first place. No dedicated reset API endpoint (e.g. a `/reset` or `/api/reset` route) exists in the pinned commit.
Evidence refs (evidence_id): SUT03-EV-0030, SUT03-EV-0031

### Determinism

Description (descriptive only, no score):
- deterministic: sign-in/checkout account gating; `/api/products`, `/api/orders`, `/api/offers` responses; the four `/sut/ui/*` fixed-duration Web Vitals conditions; the Firefox-50-conditioned image/click bug; the Network-Information-API 2G branch in `src/components/App/index.jsx`; the four non-latency "control" API handlers' fixed status codes (200/401/307/503) as coded.
- stochastic: `pages/api/control/latency/p99-outlier.js` selects a 5000ms vs. 200ms delay via `Math.random() < 0.01` (a fixed, documented 1%/99% split) — present in source but not reachable (see section 5).
- time-dependent: `pages/checkout/index.jsx` stamps each synthetic order with `new Date()` at submission time (`orderDate`/`deliveryDate` vary by calendar day); not used as a test oracle in any code path observed.
- external dependency: the `/sut/ui/high-lcp` page's largest element is fetched from the third-party host `https://picsum.photos`; `/offers` depends on the browser/OS geolocation service.
Evidence refs (evidence_id): SUT03-EV-0004, SUT03-EV-0012, SUT03-EV-0013, SUT03-EV-0015, SUT03-EV-0017, SUT03-EV-0029

### Observability

Description (descriptive only, no score): An OpenAPI 3.0 document is auto-generated (via `next-swagger-doc`) from JSDoc `@swagger` annotations present on every `pages/api/*.js` handler, and served both as JSON (`/api/doc`) and as an interactive UI (`/swagger`, via `swagger-ui-react`); every API response uses structured JSON with conventional HTTP status codes. No dedicated health-check endpoint, server-exposed logs, or request/response id scheme was found in the same full-repository review that produced the other records in this audit.
Evidence refs (evidence_id): SUT03-EV-0009

### Automation Affordances

Description (descriptive only, no score): Interactive elements carry stable `id` attributes (47 occurrences across `src/`/`pages/`) and a smaller number of `data-test`/`data-sku` attributes (no `data-testid` convention specifically); the OpenAPI schema (see Observability) is itself a machine-readable automation affordance for the API layer. The repository ships no example or end-to-end test suite of its own (no `test/`, `cypress/`, or `__tests__/` directory at the pinned commit) — a negative finding about what is *bundled*, not about whether the app is automatable.
Evidence refs (evidence_id): SUT03-EV-0005, SUT03-EV-0009, SUT03-EV-0032

### Cross-platform Scenario Parity

Description (descriptive only, no score): Not applicable in the multi-platform sense at this commit: only a Web surface is present (Android and iOS are structurally absent, SUT03-EV-0010/SUT03-EV-0011), so there is no second platform against which to assess whether a logically equivalent scenario exists. This is recorded as a structurally single-platform ecosystem rather than as "no parity mechanism found" on an otherwise multi-platform SUT.
Evidence refs (evidence_id): SUT03-EV-0010, SUT03-EV-0011

### Cross-layer State Continuity

Description (descriptive only, no score): Within the fixed account mechanism, Web UI and API are fully consistent by construction — the same `userName`-keyed logic determines what both layers show (positive continuity, but only for this one fixed mechanism). Beyond it, no UI-initiated action (favourite, cart, filter, sort) is ever sent to the API (`setFavProduct`, `addProduct`, `removeProduct`, `updateFilters`, `updateSort` are pure client-side Redux dispatches with no corresponding `axios`/`fetch` call), and no API call durably mutates product/order/offer data (no database; see State Controllability). A state change made through one layer that is not already baked into the static seed data therefore cannot be verified through the other layer.
Evidence refs (evidence_id): SUT03-EV-0006, SUT03-EV-0007, SUT03-EV-0008, SUT03-EV-0031, SUT03-EV-0032

### Functional Complexity

Description (descriptive only, no score): Entities: Products (14 seeded items: id, sku, title, price, currency, optional installment plan, available sizes, favourite flag), Orders (5 seeded orders, each with dated line items), Offers (5 city-gated promotional entries), Users (5 named accounts). Operations: browse / filter-by-vendor / sort-by-price products (client-side only), toggle favourite (client-side only), add/remove/adjust cart quantity (client-side only), sign in (server-validated), checkout (server-validated `userName` gate; client synthesizes an order record into browser storage on success), view orders (server-validated by account) and offers (server-validated by geolocation). Rules: sign-in requires an exact account+password match; checkout requires a currently-valid account; `locked_user` is recognized but permanently rejected with its own message; which products/orders/offers/images are shown is determined entirely by which of the fixed accounts is signed in, never by any other user action.
Evidence refs (evidence_id): SUT03-EV-0001, SUT03-EV-0003, SUT03-EV-0006, SUT03-EV-0007, SUT03-EV-0008, SUT03-EV-0029, SUT03-EV-0032

## 5. Documentation vs implementation contradictions

| claim | documentation source | implementation observation | evidence refs |
|---|---|---|---|
| The 8 "API Metric Control Endpoints" (`pages/api/control/error/*`, `pages/api/control/latency/*`, `pages/api/zero/errors.js`) are usable for load/monitoring-tool testing after signing in at `/sut/login`, per README.md's "Load Testing SUT" section ("Login with testuser/password", "Access dashboard and test endpoints") and the 8 links presented on `pages/sut/dashboard.jsx` under "API Metric Control Endpoints (For k6 / JMeter)". | README.md ("Load Testing SUT" section); `pages/sut/dashboard.jsx` | `pages/sut/login.jsx`'s only session-establishing code (`sessions[sessionId] = {...}`) runs exclusively in the browser (a React `onSubmit` handler) and is never transmitted to, or persisted by, the Node.js server; no `pages/api/sut/*` route or any other server-side code path ever writes to the server process's own `sessions` object, which `checkSutAuth` (`src/services/sut-utils.js`) reads for all 8 endpoints. As coded, these 8 endpoints therefore always return HTTP 401 "Authentication required", regardless of any prior login by any caller (browser or headless HTTP client). | SUT03-EV-0016, SUT03-EV-0017, SUT03-EV-0018 |

## 6. Negative evidence summary

Negative evidence recorded in evidence.csv (mechanisms searched for and not found, or a coded mechanism confirmed unreachable):

- **SUT03-EV-0010 / SUT03-EV-0011** — no Android / iOS application code, build configuration, or cross-platform mobile framework dependency exists at the pinned commit (Android Native / iOS Native, both Score 0, `NO_MOBILE_SURFACE`).
- **SUT03-EV-0018** — the server-side session bridge required by the 8 "API Metric Control Endpoints" is never established by any code path; those endpoints are permanently unreachable (excluded from the Performance score; see section 5).
- **SUT03-EV-0020** — no documented or source-verified intentional accessibility fault was found (caps Accessibility — Web only below Score 3).
- **SUT03-EV-0025** — no documented or source-verified intentional vulnerability was found (caps Security Testing below Score 3).
- **SUT03-EV-0027 / SUT03-EV-0028** — no non-USD currency value or i18n/language-switch mechanism exists anywhere in the pinned commit (caps Localization / i18n at Score 1).

See limitations.md for the evaluation and environment limitations under which this negative evidence was gathered (in particular: no EXECUTION_VERIFIED evidence was obtainable this session).

## 7. Auditor declaration

- [x] The same rubric (protocol/capability-rubric-v1.md) was applied to every modality.
- [x] The SUT was not modified.
- [x] No capability was inferred from vendor commercial products.
- [x] All evidence has provenance (repository and commit SHA / release, or endpoint) against the pinned target.
- [x] Every evidence record has a unique evidence_id, and every reference uses evidence_id.
- [x] Every EXECUTION_VERIFIED record is linked to an execution verification record with environment_type. (No EXECUTION_VERIFIED record exists in this audit; not applicable.)
- [x] Negative evidence was retained, and structural absences carry a structural_scope_note.
- [x] No fault activation, active security testing, load, or state change visible to other users was performed against a PUBLIC_HOSTED instance. (No PUBLIC_HOSTED instance of SUT-03 is documented; no execution of any kind was performed against SUT-03 in this audit — see limitations.md.)
