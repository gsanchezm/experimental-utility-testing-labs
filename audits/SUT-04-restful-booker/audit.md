# SUT-04 — Restful Booker Platform — Audit

Audit status: SUBMITTED. Performed by AUDITOR-SUT04-RESTFULBOOKER under campaign E01-capability-audit. Rules: audits/README.md, protocol/capability-rubric-v1.md, protocol/evidence-rules-v1.md, protocol/cross-cutting-properties-v1.md.

## 1. Header

| Field | Value |
|---|---|
| ecosystem_id | SUT-04 |
| ecosystem_name | Restful Booker Platform |
| role | Web/API specialist baseline |
| auditor_role | AUDITOR-SUT04-RESTFULBOOKER |
| protocol_version | v1 |
| rubric_version | v1 |
| evidence_rules_version | v1 |
| audit_status | SUBMITTED |
| started_at | 2026-09-17 |
| submitted_at | 2026-09-17 |
| environment_types_used | (none — no EXECUTION_VERIFIED evidence was produced; see limitations.md) |
| controlled_instance_available | null (not verified by execution in this audit; see limitations.md — not inferred from local deployability) |

## 2. Components and provenance

Provenance copied verbatim from manifests/sut-manifest.yaml, SUT-04 entry.

| component | presence | repository | commit_sha_or_release | endpoint | verified_by | verified_at |
|---|---|---|---|---|---|---|
| web | CONFIRMED | https://github.com/mwinteringham/restful-booker-platform | d36bd3f8647a091d406e53bad463c5e3e5d2ece1 | http://www.automationintesting.online | AUDITOR-SUT04-RESTFULBOOKER | 2026-09-17 |
| api | CONFIRMED | https://github.com/mwinteringham/restful-booker-platform | d36bd3f8647a091d406e53bad463c5e3e5d2ece1 | | AUDITOR-SUT04-RESTFULBOOKER | 2026-09-17 |
| android | ABSENT | | | | AUDITOR-SUT04-RESTFULBOOKER | 2026-09-17 |
| ios | ABSENT | | | | AUDITOR-SUT04-RESTFULBOOKER | 2026-09-17 |

Verification method: local read-only clone of `https://github.com/mwinteringham/restful-booker-platform` outside this repository, checked out at commit `d36bd3f8647a091d406e53bad463c5e3e5d2ece1` (confirmed with `git rev-parse HEAD`; see limitations.md on `git log` tooling unreliability in this environment). The repository is a single monorepo (auth/, booking/, room/, message/, branding/, report/, assets/) built via Maven and run via docker-compose.yml, which defines exactly seven services (rbp-booking, rbp-room, rbp-branding, rbp-assets, rbp-auth, rbp-report, rbp-message) — no android or ios service. No Android or iOS project files (build.gradle, AndroidManifest.xml, *.xcodeproj, Podfile) exist anywhere in the pinned-commit tree (evidence_id SUT04-EV-0011, SUT04-EV-0013). The hosted endpoint for `web` was not accessed; its exact correspondence to the pinned commit is unverified (see limitations.md, "HOSTED_MAPPING_UNVERIFIED").

Surfaces/components actually examined: `assets/` (web, Next.js/React), and all six API services `auth/`, `booking/`, `room/`, `message/`, `branding/`, `report/` — source code, `pom.xml` build files, `application*.properties`, seed/schema SQL, Dockerfiles, docker-compose.yml, root and per-service README.md, `.github/workflows/*.yml`, and `.utilities/` (mocking, monitor, wirebridge). No Android or iOS component exists to examine (see Section 3).

## 3. Modality assessments

| modality | provisional_score | confirmed_score | confirmation_state | evidence_status_summary | evidence_record_count | evidence_refs | verification_refs | rationale | structural_scope_note |
|---|---|---|---|---|---|---|---|---|---|
| Web UI Functional | 3 | 3 | CONFIRMED | DOCUMENTED:1, SOURCE_VERIFIED:3 | 4 | SUT04-EV-0001, SUT04-EV-0002, SUT04-EV-0003, SUT04-EV-0004 | | Decision procedure: (1) surface exists — yes, a Next.js web application (`assets/`) is served on port 3003 (dev) / 80 (docker); (2) specific support — yes, the home page renders a deterministic seeded room catalog; (3) control + expected outcome — yes: the admin Login.tsx form, using the documented and source-verified deterministic test account admin/password (SUT04-EV-0001, SUT04-EV-0003), deterministically redirects to /admin/rooms on success and shows a visible error with no redirect on failure (SUT04-EV-0002) — a "deterministic test account" mechanism (capability-rubric-v1.md, Score 3 examples), with SOURCE_VERIFIED evidence confirming the mechanism is implemented at the pinned commit. No execution was performed; confirmation rests on SOURCE_VERIFIED evidence, which capability-rubric-v1.md ("Score 3 confirmation") treats as sufficient to confirm Score 3. | |
| API | 3 | 3 | CONFIRMED | DOCUMENTED:2, SOURCE_VERIFIED:4 | 6 | SUT04-EV-0005, SUT04-EV-0006, SUT04-EV-0007, SUT04-EV-0008, SUT04-EV-0009, SUT04-EV-0010 | | Decision procedure: (1) surface exists — yes, six documented Spring Boot REST services; (2) specific support — yes, documented Swagger/OpenAPI per service, actuator health/logfile; (3) control + expected outcome — yes: full REST CRUD (SUT04-EV-0006) against a deterministic seeded dataset (SUT04-EV-0007), a documented, deterministic test account for token-based authorization with a defined 200/201/202-vs-403 outcome (SUT04-EV-0008), and a second, independently shipped state-seeding mechanism (Wirebridge, SQL-mapped HTTP endpoints, SUT04-EV-0009/SUT04-EV-0010) — this is "API-based state seeding" (capability-rubric-v1.md, Score 3 examples), directly and repeatedly source-verified. No execution was performed; SOURCE_VERIFIED evidence confirms Score 3. | |
| Android Native | 0 | 0 | | SOURCE_VERIFIED:1, DOCUMENTED:1 (both negative) | 2 | SUT04-EV-0011, SUT04-EV-0012 | | Decision procedure step 1 answered no: no reasonable surface for this modality exists in the evaluated version. Structurally absent, not a deficiency (AGENT-INSTRUCTIONS.md, rule 11; protocol/study-design-v1.md, section 11). | NO_MOBILE_SURFACE |
| iOS Native | 0 | 0 | | SOURCE_VERIFIED:1, DOCUMENTED:1 (both negative) | 2 | SUT04-EV-0013, SUT04-EV-0014 | | Decision procedure step 1 answered no: no reasonable surface for this modality exists in the evaluated version. Structurally absent, not a deficiency (AGENT-INSTRUCTIONS.md, rule 11; protocol/study-design-v1.md, section 11). | NO_MOBILE_SURFACE |
| Performance | 2 | 2 | | DOCUMENTED:1, SOURCE_VERIFIED:2 (1 negative) | 3 | SUT04-EV-0015, SUT04-EV-0016, SUT04-EV-0017 | | Decision procedure: (1) surface exists — yes, HTTP REST endpoints and actuator health checks; (2) specific support — yes: a stable, documented REST surface backed by a small, fixed, deterministically re-establishable seed dataset gives a known, repeatable data volume and response shape across runs, which is more than mere generic-tool reachability (SUT04-EV-0016); (3) control + expected outcome — no: no documented or source-verified performance-specific threshold, load profile, or controlled-degradation condition exists anywhere in the repository (SUT04-EV-0017; only basic liveness polling, SUT04-EV-0015). Answered with confidence at each step; no tie-break needed. | |
| Accessibility — Web only | 2 | 2 | | SOURCE_VERIFIED:2 (1 negative) | 2 | SUT04-EV-0018, SUT04-EV-0019 | | Decision procedure: (1) surface exists — yes, the web UI; (2) specific support — yes: aria-label attributes, role=status/role=alert regions, and associated <label htmlFor> elements are consistently applied across the reservation and admin-login forms (SUT04-EV-0018), more than generic scanner reachability; (3) control + expected outcome — no: no documented or source-verified controlled accessibility fault, or known accessibility violation used as a test fixture, was found (SUT04-EV-0019). Answered with confidence at each step; no tie-break needed. | |
| Visual Testing | 1 | 1 | | SOURCE_VERIFIED:2 (1 negative) | 2 | SUT04-EV-0020, SUT04-EV-0021 | | Decision procedure: (1) surface exists — yes, rendered web pages a generic screenshot-diff tool (e.g. Pixelmatch, Percy) could technically point at; (2) specific support — no: the only test-fixture evidence found is Jest DOM/markup snapshot testing (SUT04-EV-0020), which is explicitly not a pixel-level visual-testing mechanism and is not treated as one here; no visual-regression tooling, baseline images, or documented visual-perturbation condition exist (SUT04-EV-0021). Stops at Score 1. | |
| Security Testing | 3 | 2 | | SOURCE_VERIFIED:3 (1 negative) | 3 | SUT04-EV-0022, SUT04-EV-0023, SUT04-EV-0024 | | Decision procedure: (1) surface exists — yes; (2) specific support — yes: a real, stable, deterministic token-based authorization boundary exists (valid token → success, missing/invalid token → 403 FORBIDDEN, SUT04-EV-0022), well beyond generic-tool reachability, so at minimum Score 2 is fully supported and is recorded as `confirmed_score`. (3) control + expected outcome at Score 3 — undecided, not "no": all database-access code uses parameterized queries (no source-verified SQL-injection condition, SUT04-EV-0023), and no documentation anywhere describes an intentional/known vulnerability. However, SOURCE_VERIFIED evidence does show ACCOUNTS.password is stored and compared as plaintext, with no hashing dependency in auth/pom.xml (SUT04-EV-0024) — a verifiable condition with a defined, observable outcome (a direct DB/H2 inspection or this source reveals the plaintext credential), matching the *form* of the Ground Truth Rule's own example ("known vulnerable authorization condition -> security verification -> detected / not detected", protocol/study-design-v1.md section 8). Whether an undocumented, non-pedagogical implementation characteristic satisfies capability-rubric-v1.md Decision procedure step 3's "known experimental condition" the same way a documented/designed mechanism would (as in every one of the rubric's own Score 3 security examples: "fault injection", "documented intentional vulnerability") is a genuine interpretive question this auditor does not resolve either way (see unresolved.md, SUT-04-U01). Per capability-rubric-v1.md, "Tie-break rule for undecidable adjacent scores" and its "Relation to Score 3 confirmation" paragraph (the doubt concerns whether the mechanism/outcome meets the rubric's Score 3 criteria at all, not the evidence status), `confirmed_score` is capped at 2 (the highest fully-supported level), `provisional_score` is retained at 3 as the candidate, and `confirmation_state` is left null rather than forced to UNCONFIRMED_SCORE_3 or CONFIRMED. Flagged for adjudication. | |
| Localization / i18n | 0 | 0 | | SOURCE_VERIFIED:1, DOCUMENTED:1 (both negative) | 2 | SUT04-EV-0025, SUT04-EV-0026 | | Decision procedure step 1 answered no with confidence: the only locale-related code in the repository fixes react-datepicker to a single hardcoded locale (en-GB) for date formatting; there is no locale/market selector, no translation catalog, and no i18n library anywhere in assets/package.json or assets/src (SUT04-EV-0025). This is a complete absence of a locale-selection surface, not merely narrow support — Score 0, not Score 1. | OTHER_STRUCTURAL_REASON: single hardcoded date-format locale (en-GB); no locale/market-selection surface exists in the evaluated version (SUT04-EV-0025, SUT04-EV-0026) |

No cell in this table rests on INFERRED evidence alone or on DOCUMENTED evidence alone for a confirmed Score 3. Every non-zero cell cites at least one evidence record; every Score 0 cell cites at least one negative-evidence record. No global, weighted, or composite score was computed. No comparison to any other SUT was made.

## 4. Cross-cutting properties

Descriptive only; no property is scored (protocol/cross-cutting-properties-v1.md).

### State Controllability

Description (descriptive only, no score): Restful Booker Platform exposes state-establishment through three independent, source-verified mechanisms. (1) Direct REST CRUD on each service (auth, booking, room, message, branding, report), with `POST`/`PUT`/`DELETE` writing to each service's own H2 database (SUT04-EV-0006). (2) A deterministic, documented test account (admin/password) that issues an authorization token via `POST /auth/login`, reachable both from the API directly and from the Web UI's own login form (SUT04-EV-0002, SUT04-EV-0003, SUT04-EV-0008). (3) Wirebridge, a shipped, documented, configurable HTTP-to-SQL bridge with mapping files present in-repo for one-call creation of a booking or a room (SUT04-EV-0009, SUT04-EV-0010). Every service also starts from a fixed, deterministic seed dataset (SUT04-EV-0007). States reachable only through the web UI's own screens (for example, the multi-step reservation confirmation flow's own client-side state) were not separately inventoried at the level of each individual screen transition; this is a descriptive limitation of the audit's depth, not a claim that no such states exist.
Evidence refs (evidence_id): SUT04-EV-0002, SUT04-EV-0003, SUT04-EV-0006, SUT04-EV-0007, SUT04-EV-0008, SUT04-EV-0009, SUT04-EV-0010

### Resetability

Description (descriptive only, no score): Each of auth, booking, room, message and branding implements a `resetDB()` method that deletes that service's own mutable rows and re-executes its `seed.sql`. This is invoked only by an internal `DatabaseScheduler`, which runs on a fixed period set by the `dbRefresh` environment variable (interpreted in minutes) and is disabled by default when `dbRefresh` is unset or 0; it is not exposed as an HTTP route in any controller, and its only other caller is each service's own unit test suite. `report` has no scheduler or reset (it is a read-only aggregation service). Scope: each service resets only its own table(s) — there is no single, cross-service reset action. Auth's reset also clears all issued `TOKENS`, invalidating every active session platform-wide when it fires. No experimenter-triggered, on-demand reset endpoint exists; reset is available only as a periodic, env-var-configured background action (or via the service's own unit tests, which are not part of the SUT's runtime surface).
Evidence refs (evidence_id): SUT04-EV-0027

### Determinism

Description (descriptive only, no score):
- deterministic: REST CRUD responses for a given, unmodified seeded entity (e.g. `GET /booking/1`) are fully determined by the seeded initial state and the request, until the entity is modified (SUT04-EV-0006, SUT04-EV-0007).
- stochastic: authorization token values are generated with `java.security.SecureRandom` (`auth/src/main/java/com/automationintesting/service/RandomString.java`) — each successful login issues a different, unpredictable token value, though this does not change the deterministically observable business outcome (valid-token vs. invalid-token behavior).
- time-dependent: the `dbRefresh`-driven scheduled `resetDB()` (SUT04-EV-0027) makes a service's observable state a function of elapsed wall-clock time when `dbRefresh` is configured; booking creation also performs check-in/check-out date-conflict validation (`DateCheckValidator`) against the dates supplied in the request.
- external dependency: `BookingService.createBooking` synchronously calls the message service (`MessageRequests.postMessage`) when the booking includes an email and phone, so booking creation's full observable side effects depend on the message service being reachable; the web asset service depends on all six backend services being reachable via Docker-network environment variables (SUT04-EV-0028). A WireMock-based virtualization mechanism is shipped in-repo to substitute controlled doubles for such dependencies (SUT04-EV-0029).
Evidence refs (evidence_id): SUT04-EV-0006, SUT04-EV-0007, SUT04-EV-0027, SUT04-EV-0028, SUT04-EV-0029

### Observability

Description (descriptive only, no score): Every one of the six API services documents and exposes, at the pinned commit, an actuator `health` endpoint and an actuator `logfile` endpoint (`management.endpoints.web.exposure.include=health,logfile`, source-verified per-service in `application.properties`), plus a Swagger/OpenAPI UI (springdoc dependency present in every service's `pom.xml`) (SUT04-EV-0005, SUT04-EV-0015). Responses are structured JSON with stable, auto-incrementing numeric entity IDs (bookingid, roomid, messageid, brandingid). Two lightweight liveness-polling scripts (`.utilities/monitor/local_monitor.js`, `prod_monitor.js`) are shipped in-repo, polling every service's health endpoint. No deeper diagnostic/tracing endpoint (beyond health and logfile) or structured metrics endpoint (e.g. `/actuator/metrics`) was found documented or exposed.
Evidence refs (evidence_id): SUT04-EV-0005, SUT04-EV-0006, SUT04-EV-0015

### Automation Affordances

Description (descriptive only, no score): Stable, semantic HTML element ids are used for key interactive controls (e.g. `id="username"`, `id="password"`, `id="doLogin"` in the admin login form); `data-testid` attributes appear in 8 web-UI source files (a minority of components, not applied uniformly across every screen); `aria-label` attributes label reservation-form inputs (SUT04-EV-0018). Every API service ships a machine-readable OpenAPI/Swagger schema (SUT04-EV-0005). A deterministic test account and two independent, documented state-seeding mechanisms (direct REST CRUD; Wirebridge) exist (see State Controllability, above). These affordances are present but not applied with full, documented consistency across every screen: `data-testid` coverage is partial (8 files out of the full component tree), and some components rely on `aria-label`/`role` while others were not source-verified for the same pattern.
Evidence refs (evidence_id): SUT04-EV-0002, SUT04-EV-0005, SUT04-EV-0009, SUT04-EV-0010, SUT04-EV-0018

### Cross-platform Scenario Parity

Description (descriptive only, no score): Not applicable in the sense of comparing platforms: the evaluated version has only a Web surface (SUT04-EV-0011 through SUT04-EV-0014 confirm no Android or iOS surface exists). Cross-platform scenario parity, as defined (whether a logically equivalent scenario exists across Web, Android and iOS), cannot be evaluated for an ecosystem that structurally has only one of those three platforms. This is a descriptive, structural fact about ecosystem scope, stated neutrally per protocol/study-design-v1.md, section 11 (rules 1 and 3) and AGENT-INSTRUCTIONS.md, rule 11 — it is not a finding about the quality of the Web surface itself.
Evidence refs (evidence_id): SUT04-EV-0011, SUT04-EV-0013

### Cross-layer State Continuity

Description (descriptive only, no score): The web asset service's own server-side Next.js route handlers (`assets/src/app/api/*`) proxy directly, over the Docker network, to the same backend services (booking, room, branding, auth, message, report) that the API modality exercises directly, using environment variables set in `assets/Dockerfile` (e.g. `BOOKING_API=http://rbp-booking:3000`) (SUT04-EV-0028). Because both the Web UI and the direct API reach the identical backend service and H2 database instance for a given entity, a record created through one layer is visible through the other (Web -> API and API -> Web) for booking, room, message and branding entities. No separate persistence layer or cache sits between the Web proxy and the backend services that could desynchronize the two views, as far as this source-only review determined.
Evidence refs (evidence_id): SUT04-EV-0028

### Functional Complexity

Description (descriptive only, no score): Entities: Booking (roomid, firstname, lastname, depositpaid, checkin, checkout), Room (name, type, beds, accessible flag, image, description, features array, price), Message (name, email, phone, subject, description, read flag), Branding (name, geocoordinates, directions, logo, description, contact details, address), and Auth accounts/tokens. Operations: full CRUD on Booking, Room and Message; read + update on Branding; read-only aggregation on Report (room/booking summaries, SUT04-EV-0006); login/validate/logout only on Auth (no account CRUD). Rules observed in source: booking date-conflict validation (`DateCheckValidator`, `checkForBookingConflict`) rejects overlapping bookings for the same room; cookie-token authorization gates read/update/delete on booking/room/message/branding while booking creation is intentionally public (SUT04-EV-0006, SUT04-EV-0008, SUT04-EV-0022); creating a booking with an email and phone automatically generates and posts a message to the message service (cross-entity side effect, `MessageBuilder`); each service's data can be periodically reset on a schedule (`dbRefresh`, SUT04-EV-0027). This is reported as an inventory; it is not used to rank this ecosystem against any other (protocol/cross-cutting-properties-v1.md, "Functional Complexity").
Evidence refs (evidence_id): SUT04-EV-0006, SUT04-EV-0007, SUT04-EV-0008, SUT04-EV-0022, SUT04-EV-0027

## 5. Documentation vs implementation contradictions

| claim | documentation source | implementation observation | evidence refs |
|---|---|---|---|
| The built API jar is named `restful-booker-platform-{service}-1.0-SNAPSHOT.jar` | booking/README.md, room/README.md, message/README.md, branding/README.md, report/README.md ("Running the API" sections) | The root aggregator `pom.xml` and every service `pom.xml` declare `<version>2.2.${revision}</version>` with `<revision>SNAPSHOT</revision>`, so the actual Maven-built artifact at the pinned commit is named `restful-booker-platform-{service}-2.2.SNAPSHOT.jar`, not `...-1.0-SNAPSHOT.jar` | SUT04-EV-0030, SUT04-EV-0031 |

This cell (API modality) is otherwise unaffected: the contradiction concerns a stale run-instruction filename in five of six service READMEs, not the CRUD/state-seeding mechanism the Score 3 determination rests on. Flagged for adjudication per protocol/capability-rubric-v1.md, "Evidence requirement" ("the auditor does not resolve a contradiction by choosing the evidence that favors the SUT").

## 6. Negative evidence summary

- Android Native (Score 0): searched and not found — no `build.gradle`, `AndroidManifest.xml`, or android module anywhere in the pinned-commit tree; no Android build/run documentation. Records: SUT04-EV-0011, SUT04-EV-0012.
- iOS Native (Score 0): searched and not found — no `*.xcodeproj`, `*.xcworkspace`, or `Podfile` anywhere in the pinned-commit tree; no iOS build/run documentation. Records: SUT04-EV-0013, SUT04-EV-0014.
- Performance Score 3 candidate: searched and not found — no k6/Gatling/JMeter/Locust script or documented performance threshold/degradation condition. Record: SUT04-EV-0017.
- Accessibility Score 3 candidate: searched and not found — no axe-core integration or documented/known accessibility violation used as a test fixture. Record: SUT04-EV-0019.
- Visual Testing Score 2/3 candidate: searched and not found — no Percy/Applitools/Pixelmatch dependency or documented visual-regression baseline. Record: SUT04-EV-0021.
- Security Testing SQL-injection candidate: searched and not found — every database-access query observed uses parameterized `PreparedStatement` binding. Record: SUT04-EV-0023.
- Localization / i18n (Score 0): searched and not found — no locale/market selector, translation catalog, or i18n library; only a single hardcoded date-format locale. Records: SUT04-EV-0025, SUT04-EV-0026.

All records above are retained in evidence.csv and are not deleted (protocol/evidence-rules-v1.md, "Retention"). See limitations.md for evaluation, environment, and evidence-ceiling limitations that are not themselves negative-evidence records.

## 7. Auditor declaration

- [x] The same rubric (protocol/capability-rubric-v1.md) was applied to every modality.
- [x] The SUT was not modified.
- [x] No capability was inferred from vendor commercial products.
- [x] All evidence has provenance (repository and commit SHA / release, or endpoint) against the pinned target.
- [x] Every evidence record has a unique evidence_id, and every reference uses evidence_id.
- [ ] Every EXECUTION_VERIFIED record is linked to an execution verification record with environment_type. — Not applicable: no EXECUTION_VERIFIED record was produced in this audit, so this requirement did not arise (see limitations.md).
- [x] Negative evidence was retained, and structural absences carry a structural_scope_note.
- [x] No fault activation, active security testing, load, or state change visible to other users was performed against a PUBLIC_HOSTED instance. (Vacuously true: no PUBLIC_HOSTED interaction of any kind was performed in this audit; see limitations.md.)
