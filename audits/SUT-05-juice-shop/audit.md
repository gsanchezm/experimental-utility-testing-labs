# SUT-05 — OWASP Juice Shop — Audit

Audit status: SUBMITTED. Performed by AUDITOR-SUT05-JUICESHOP under campaign E01-capability-audit, protocol v1 (FROZEN-PRE-DATA), against the pinned commit of juice-shop/juice-shop. Rules: audits/README.md, protocol/capability-rubric-v1.md, protocol/evidence-rules-v1.md, protocol/cross-cutting-properties-v1.md.

## 1. Header

| Field | Value |
|---|---|
| ecosystem_id | SUT-05 |
| ecosystem_name | OWASP Juice Shop |
| role | security specialist baseline |
| auditor_role | AUDITOR-SUT05-JUICESHOP |
| protocol_version | v1 |
| rubric_version | v1 |
| evidence_rules_version | v1 |
| audit_status | SUBMITTED |
| started_at | 2026-09-17 |
| submitted_at | 2026-09-17 |
| environment_types_used | (none — this audit produced no EXECUTION_VERIFIED evidence) |
| controlled_instance_available | null (not verified during this audit; see limitations.md) |

## 2. Components and provenance

Copied from manifests/sut-manifest.yaml (SUT-05 entry) and verified by this auditor against the cloned pinned commit in `../e01-sut-sources/SUT-05-juice-shop/`.

| component | presence | repository | commit_sha_or_release | endpoint | verified_by | verified_at |
|---|---|---|---|---|---|---|
| web | CONFIRMED | https://github.com/juice-shop/juice-shop | 1618a611b173b4bf114028e6e02549950606e29d | https://owasp-juice.shop | AUDITOR-SUT05-JUICESHOP | 2026-09-17 |
| api | CONFIRMED | https://github.com/juice-shop/juice-shop | 1618a611b173b4bf114028e6e02549950606e29d | | AUDITOR-SUT05-JUICESHOP | 2026-09-17 |
| android | ABSENT | | | | AUDITOR-SUT05-JUICESHOP | 2026-09-17 |
| ios | ABSENT | | | | AUDITOR-SUT05-JUICESHOP | 2026-09-17 |

web/api presence: confirmed by reading `package.json`, `server.ts`, `routes/` (61 modules), and `frontend/src/app` (Angular application) directly in the cloned pinned commit (SUT05-EV-0001, SUT05-EV-0005). The `web` endpoint (`https://owasp-juice.shop`) is copied verbatim from manifests/sut-manifest.yaml; its exact correspondence to the pinned commit was not independently verified by this audit (the manifest's own HOSTED_MAPPING_UNVERIFIED caveat applies, and this audit did not access the hosted endpoint — see limitations.md). `api` has no endpoint in the manifest (same repository, no separate hosted API endpoint recorded) and none is added here.

android/ios presence: recorded ABSENT (not UNCONFIRMED) because this audit actively searched the evaluated commit's full top-level tree and `package.json` dependencies for Android/iOS build artifacts and cross-platform mobile frameworks and found none (SUT05-EV-0021, SUT05-EV-0022). No discrepancy with manifests/sut-manifest.yaml was found (the manifest already records no android/ios component named for SUT-05).

## 3. Modality assessments

| modality | provisional_score | confirmed_score | confirmation_state | evidence_status_summary | evidence_record_count | evidence_refs | verification_refs | rationale | structural_scope_note |
|---|---|---|---|---|---|---|---|---|---|
| Web UI Functional | 3 | 3 | CONFIRMED | DOCUMENTED, SOURCE_VERIFIED | 6 | SUT05-EV-0001, SUT05-EV-0002, SUT05-EV-0003, SUT05-EV-0004, SUT05-EV-0023, SUT05-EV-0026 | | Surface exists (Angular SPA, SUT05-EV-0001). The evaluated version ships a fixed set of named accounts with deterministic credentials (SUT05-EV-0002), guaranteed to be re-seeded identically on every application start (SUT05-EV-0003), and role-gated UI rendering that produces a defined, observable outcome tied to a specific account (SUT05-EV-0004) — matching the Score 3 "deterministic test account" example and satisfying Decision procedure step 3 (establish a known condition + observe a defined expected outcome). All three supporting mechanisms are SOURCE_VERIFIED, so confirmation_state is CONFIRMED without invoking the tie-break rule. | |
| API | 3 | 3 | CONFIRMED | DOCUMENTED, SOURCE_VERIFIED | 7 | SUT05-EV-0005, SUT05-EV-0006, SUT05-EV-0007, SUT05-EV-0008, SUT05-EV-0024, SUT05-EV-0025, SUT05-EV-0027 | | Surface exists (documented OpenAPI B2B schema, SUT05-EV-0005; 61 route modules, SUT05-EV-0008). POST /rest/user/login (SUT05-EV-0006) establishes known account-scoped state via the same deterministic accounts as Web UI Functional (API-based state seeding, Score 3 example), and GET /api/Challenges (SUT05-EV-0007) gives a source-verified, machine-readable read-out of a defined expected outcome (challenge.solved). Both are SOURCE_VERIFIED; confirmation_state is CONFIRMED. | |
| Android Native | 0 | 0 | | SOURCE_VERIFIED | 1 | SUT05-EV-0021 | | No reasonable surface exists: the evaluated commit's full top-level tree and package.json dependencies were searched for Android build artifacts or cross-platform mobile frameworks; none found (SUT05-EV-0021). Decision procedure step 1 answers no. | NO_MOBILE_SURFACE: no Android application build exists in the evaluated version |
| iOS Native | 0 | 0 | | SOURCE_VERIFIED | 1 | SUT05-EV-0022 | | Same basis as Android Native: searched for iOS build artifacts / cross-platform frameworks; none found (SUT05-EV-0022). Decision procedure step 1 answers no. | NO_MOBILE_SURFACE: no iOS application build exists in the evaluated version |
| Performance | 1 | 1 | | SOURCE_VERIFIED | 2 | SUT05-EV-0016, SUT05-EV-0017 | | Surface exists (61 reachable REST routes, SUT05-EV-0017), satisfying Decision procedure step 1. No SUT-specific performance ground truth was found: the full 16-category, 113-entry challenge catalog, all route modules, and all config profiles were searched for a documented, controllable performance-degradation condition; none found (SUT05-EV-0016), so Decision procedure step 2 answers no. Generic reachability by a load-testing tool is exactly Score 1's definition. | |
| Accessibility — Web only | 1 | 1 | | SOURCE_VERIFIED | 2 | SUT05-EV-0018, SUT05-EV-0019 | | The web surface exists (section 2, CONFIRMED), so Decision procedure step 1 answers yes and Score 0 does not apply. No accessibility-testing dependency (axe-core, pa11y, lighthouse) is present in package.json (SUT05-EV-0018), and no documented/labeled accessibility violation or fixture was found in the challenge catalog or the Angular frontend (SUT05-EV-0019); Decision procedure step 2 answers no. The evaluated UI remains reachable by a generic accessibility scanner, which is Score 1's definition. | |
| Visual Testing | 1 | 1 | | SOURCE_VERIFIED | 1 | SUT05-EV-0020 | | Surface exists (rendered Angular UI). No in-session, documented visual-perturbation mechanism was found: the frontend was searched for a runtime theme/dark-mode toggle and the 14 config/*.yml branding profiles were checked, but those profiles are selected only at application startup, not activatable within a running session (SUT05-EV-0020); Decision procedure step 2 answers no. The rendered UI remains reachable by a generic screenshot-diff tool, which is Score 1's definition. | |
| Security Testing | 3 | 3 | CONFIRMED | DOCUMENTED, SOURCE_VERIFIED | 4 | SUT05-EV-0009, SUT05-EV-0010, SUT05-EV-0011, SUT05-EV-0012 | | Surface exists and the evaluated version documents its purpose as an intentionally insecure application (SUT05-EV-0009). The evaluated commit ships a catalog of 113 individually named, keyed, documented intentional vulnerabilities across 16 categories (SUT05-EV-0010 — matching the Score 3 "documented intentional vulnerability" example), each with server-side, automated, deterministic detection of whether the exact documented condition was triggered and an observable `solved` outcome (SUT05-EV-0011). Both are SOURCE_VERIFIED; confirmation_state is CONFIRMED. SUT05-EV-0012 records that a subset of individual challenges are disabled under specific deployment environments (Docker, Heroku); this does not change the modality-level determination, which rests on the catalog and detection mechanism as a whole. | |
| Localization / i18n | 3 | 3 | CONFIRMED | DOCUMENTED, SOURCE_VERIFIED | 3 | SUT05-EV-0013, SUT05-EV-0014, SUT05-EV-0015 | | Surface exists: 45 shipped locale JSON translation files and a documented locale list (SUT05-EV-0013). The evaluated version exposes an explicit, user-invokable runtime locale switch (`translate.use(langKey)`, SUT05-EV-0014 — matching the Score 3 "explicit market/locale selection" example) whose outcome (the selected locale's shipped, fixed translation content) is known in advance. SOURCE_VERIFIED; confirmation_state is CONFIRMED. SUT05-EV-0015 additionally shows a source-verified, API-observable translation-completeness measure per locale. | |

No cell in this table rests on the tie-break rule: every Score 3 determination has SOURCE_VERIFIED support for the mechanism and outcome (confirmed_score equals provisional_score in every row), and every Score 0/1 determination is a clean application of the Decision procedure with no unresolved ambiguity. No EXECUTION_VERIFIED evidence was produced or required (see "Evidence collection order" in the auditor prompt and limitations.md); `verification_refs` is empty throughout.

## 4. Cross-cutting properties

### State Controllability

Description (descriptive only, no score): The evaluated version provides two source-verified state-establishment mechanisms. First, a fixed set of named accounts with deterministic credentials (admin, jim, bender, chris, amy, support, mc.safesearch, and an accounting-role account) reaches the application in a known role/state on login, through either the Web UI or the API (SUT05-EV-0002, SUT05-EV-0006). Second, ordinary CRUD-style REST endpoints (basket, reviews, addresses, orders, and 23 underlying data entities) let an authenticated session build up further state (SUT05-EV-0008, SUT05-EV-0027). No dedicated fixture-loading or bulk-seed API distinct from these two mechanisms was found; state beyond the named accounts is established the same way an ordinary end user would establish it (through the UI or the equivalent API calls), not through a special setup endpoint.

Evidence refs (evidence_id): SUT05-EV-0002, SUT05-EV-0003, SUT05-EV-0006, SUT05-EV-0008, SUT05-EV-0027

### Resetability

Description (descriptive only, no score): The only reset mechanism this audit found is process-restart-triggered: `server.ts` runs `sequelize.sync({ force: true })` on every application start, dropping and recreating the entire database and reloading it from the static seed files (SUT05-EV-0003). Its scope is the whole application datastore (all 23 modeled entities); it requires restarting the process and is not something an experimenter can trigger mid-session over HTTP. This audit searched `routes/` (61 modules) and `server.ts` for an in-session, HTTP-triggerable full-state reset endpoint and found none — the only route matching a search for "reset" is `routes/resetPassword.ts`, a per-user password-reset flow unrelated to full application state (SUT05-EV-0028, negative evidence). Separately, authenticated session state expires automatically after 6 hours regardless of activity (SUT05-EV-0024), which is a time-based invalidation, not an experimenter-triggered reset.

Evidence refs (evidence_id): SUT05-EV-0003, SUT05-EV-0028, SUT05-EV-0024

### Determinism

Description (descriptive only, no score):
- deterministic: Login/account role gating (SUT05-EV-0002, SUT05-EV-0004), the API login handler (SUT05-EV-0006), and the challenge solve-detection mechanism (`solveIf`/`solve`, SUT05-EV-0011) all produce the same outcome for the same initial state and stimulus. Explicit locale switching (SUT05-EV-0014) likewise deterministically re-renders fixed, shipped translation content.
- stochastic: The math CAPTCHA served by `routes/captcha.ts` generates its operands and operators with `Math.random()` on every request, so the specific challenge/response pair is not reproducible run to run (SUT05-EV-0023).
- time-dependent: Authentication JWTs are signed with a fixed 6-hour expiry (`lib/insecurity.ts`); a previously-established authenticated state becomes invalid purely from elapsed time (SUT05-EV-0024).
- external dependency: The chatbot feature (`routes/chat.ts`) calls an external LLM-compatible API using a locally-configured API key; its behavior and availability depend on that external service and configuration, outside the evaluated version's own control (SUT05-EV-0025).

Evidence refs (evidence_id): SUT05-EV-0002, SUT05-EV-0004, SUT05-EV-0006, SUT05-EV-0011, SUT05-EV-0014, SUT05-EV-0023, SUT05-EV-0024, SUT05-EV-0025

### Observability

Description (descriptive only, no score): The evaluated version documents its API surface via an OpenAPI 3.0 schema for the B2B endpoint (SUT05-EV-0005) and exposes challenge/vulnerability state machine-readably through a REST resource, `GET /api/Challenges`, returning each challenge's `solved` boolean (SUT05-EV-0007). It also exposes two diagnostic endpoints without authentication: `GET /metrics` (Prometheus-format runtime metrics) and `GET /rest/admin/application-version` (running application version) (SUT05-EV-0029) — the `/metrics` exposure is itself one of the documented Security Testing challenges (`exposedMetricsChallenge`). A further endpoint reports per-locale translation completeness (SUT05-EV-0015). All of these affordances cover the API layer (the same backend that also serves the Web UI); no separate Android/iOS observability layer exists (no such surface, section 2).

Evidence refs (evidence_id): SUT05-EV-0005, SUT05-EV-0007, SUT05-EV-0008, SUT05-EV-0015, SUT05-EV-0029

### Automation Affordances

Description (descriptive only, no score): The Web UI uses stable, static `id` attributes on interactive elements (for example `#email`, `#password`, `#loginButton` on the login form), and the evaluated version ships a first-party automation harness of its own: 32 Cypress end-to-end spec files and 57 API test files, including a custom `cy.expectChallengeSolved()` command that queries the same challenge-state mechanism used for Security Testing (SUT05-EV-0026). The API additionally exposes a machine-readable OpenAPI schema (SUT05-EV-0005) and a REST-conventioned resource (`finale`) for challenge state (SUT05-EV-0007). This audit sampled one spec file among the 32 present; selector consistency across every screen of the frontend was not exhaustively verified (see limitations.md).

Evidence refs (evidence_id): SUT05-EV-0005, SUT05-EV-0007, SUT05-EV-0026

### Cross-platform Scenario Parity

Description (descriptive only, no score): Not applicable beyond the Web surface: the evaluated version has no Android or iOS surface to compare scenario parity against (SUT05-EV-0021, SUT05-EV-0022, section 2). With only one platform present, there is no cross-platform pair for which parity or partial parity could be assessed.

Evidence refs (evidence_id): SUT05-EV-0021, SUT05-EV-0022

### Cross-layer State Continuity

Description (descriptive only, no score): Web and API are two interfaces onto one Node.js/Express process and one Sequelize-backed datastore (SUT05-EV-0003); a state established via the API (for example authenticating as a named account, SUT05-EV-0006) is immediately visible through the Web UI (SUT05-EV-0002, SUT05-EV-0004), and vice versa, because both interfaces read and write the same tables. No Android or iOS layer exists to extend this continuity to (SUT05-EV-0021, SUT05-EV-0022).

Evidence refs (evidence_id): SUT05-EV-0003, SUT05-EV-0002, SUT05-EV-0004, SUT05-EV-0006, SUT05-EV-0021, SUT05-EV-0022

### Functional Complexity

Description (descriptive only, no score): The evaluated version defines 23 Sequelize-modeled data entities (address, basket, basketitem, captcha, card, challenge, challengeDependency, complaint, delivery, feedback, hint, imageCaptcha, memory, privacyRequests, product, quantity, recycle, securityAnswer, securityQuestion, user, wallet, plus index/relations modules; SUT05-EV-0027), exercised through 61 Express route modules covering login/2FA, basket and order management, product reviews, address management, coupons, file upload, and administrative/diagnostic endpoints (SUT05-EV-0008). Distinct from ordinary business logic, the evaluated version separately carries a 113-entry catalog of documented intentional vulnerability conditions across 16 categories as a first-class, keyed rule set of its own (SUT05-EV-0010).

Evidence refs (evidence_id): SUT05-EV-0008, SUT05-EV-0010, SUT05-EV-0027

## 5. Documentation vs implementation contradictions

| claim | documentation source | implementation observation | evidence refs |
|---|---|---|---|

None found. Every DOCUMENTED record this audit produced (SUT05-EV-0001, SUT05-EV-0005, SUT05-EV-0009, SUT05-EV-0013) was consistent with what the pinned-commit source itself shows; no case was found where documentation asserted a capability or behavior that source inspection contradicted.

## 6. Negative evidence summary

Negative-evidence records (searched and not found), retained in evidence.csv and not deleted:

- Performance: no documented/controllable performance-degradation condition found in the challenge catalog, routes, or config profiles (SUT05-EV-0016).
- Accessibility — Web only: no accessibility-testing dependency in package.json (SUT05-EV-0018); no documented/labeled accessibility violation or fixture found (SUT05-EV-0019).
- Visual Testing: no in-session, documented, runtime-activatable visual-condition mechanism found (SUT05-EV-0020).
- Android Native: no Android build artifact or cross-platform mobile framework found in the evaluated commit (SUT05-EV-0021).
- iOS Native: no iOS build artifact or cross-platform mobile framework found in the evaluated commit (SUT05-EV-0022).
- Resetability (cross-cutting): no in-session/API full-state reset endpoint found; only the process-restart-triggered reseed exists (SUT05-EV-0028).

See limitations.md for the scope of each search and the environmental/evaluation limitations of this audit.

## 7. Auditor declaration

- [x] The same rubric (protocol/capability-rubric-v1.md) was applied to every modality.
- [x] The SUT was not modified.
- [x] No capability was inferred from vendor commercial products.
- [x] All evidence has provenance (repository and commit SHA / release, or endpoint) against the pinned target.
- [x] Every evidence record has a unique evidence_id, and every reference uses evidence_id.
- [x] Every EXECUTION_VERIFIED record is linked to an execution verification record with environment_type. (N/A — no EXECUTION_VERIFIED record was produced.)
- [x] Negative evidence was retained, and structural absences carry a structural_scope_note.
- [x] No fault activation, active security testing, load, or state change visible to other users was performed against a PUBLIC_HOSTED instance. (No PUBLIC_HOSTED instance was accessed at all during this audit.)
