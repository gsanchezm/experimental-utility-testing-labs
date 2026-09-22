# SUT-05 — OWASP Juice Shop — Limitations

| Field | Value |
|---|---|
| SUT id | SUT-05 |
| Auditor role | AUDITOR-SUT05-JUICESHOP |
| Audit status | SUBMITTED |

## Purpose

Records, neutrally and descriptively, what bounds the audit of the system under test (SUT) SUT-05: what the ecosystem intentionally does not cover, what the auditor could not verify and why, environment constraints, and environment considerations. Entries are cross-referenced from audit.md (structural_scope_note column and section 6) and from evidence.csv notes. Nothing here is a score, a finding, or a ranking input.

Intentionally narrow scope is not a penalty. An ecosystem that deliberately does not cover a modality is described here in neutral terms; the corresponding row in audit.md section 3 carries a structural_scope_note, the score remains the rubric score (Score 0 for a structurally absent surface; no N/A level), and the capability rubric (protocol/capability-rubric-v1.md) is applied unchanged. Experimental Breadth and Modality Depth answer different questions (protocol/study-design-v1.md, section 11).

## Scope limitations of the ecosystem (intentional)

- OWASP Juice Shop's own documented purpose is as a security-training/CTF/awareness target for an intentionally insecure web application (package.json description; README.md; SUT05-EV-0009), not a general-purpose or cross-platform testing demo. Its ecosystem does not include an Android or iOS component: the evaluated commit's full source tree and package.json dependencies were searched and no Android/iOS build artifact or cross-platform mobile framework was found (SUT05-EV-0021, SUT05-EV-0022). This is recorded as NO_MOBILE_SURFACE in audit.md section 3, per protocol/capability-rubric-v1.md.
- No accessibility-testing tooling (axe-core, pa11y, lighthouse, or equivalent) and no documented or code-level accessibility-specific ground-truth condition were found in the evaluated version (SUT05-EV-0018, SUT05-EV-0019). This is a scope observation, not a structural absence: the web surface itself fully exists, so audit.md records Accessibility — Web only at Score 1 (Decision procedure step 1 answers yes; only step 2 answers no), not Score 0, and carries no structural_scope_note.
- No documented or code-level, controllable performance-degradation condition, and no in-session/runtime-activatable documented visual-perturbation mechanism, were found (SUT05-EV-0016, SUT05-EV-0020). Both surfaces (the reachable REST API and the rendered web UI) exist; these are likewise Score 1 determinations, not structural absences.

## Evaluation limitations (what the auditor could not verify and why)

Includes the evidence ceiling where SOURCE_VERIFIED is unobtainable for a closed-source or hosted-only component (protocol/evidence-rules-v1.md): the ecosystem is not penalized; the strongest obtainable status is recorded.

- No evidence ceiling applies to this SUT. The evaluated component (juice-shop/juice-shop) is fully open-source at the pinned commit; SOURCE_VERIFIED was obtainable for every mechanism this audit examined, and protocol/evidence-rules-v1.md's "Evidence ceiling" provision therefore did not constrain any cell.
- This audit relied on DOCUMENTED and SOURCE_VERIFIED evidence only; no EXECUTION_VERIFIED record was produced. Per the "Evidence collection order" of the auditor prompt, execution verification is required only to settle a specific unresolved claim after documentation and source review; because SOURCE_VERIFIED evidence was obtainable and sufficient for every candidate Score 3 mechanism identified (Web UI Functional, API, Security Testing, Localization / i18n), no claim remained that required it. `environment_types_used` in audit.md is therefore empty and every `verification_refs` list in audit.md section 3 is empty.
- The application itself was not installed, started, or interacted with at runtime: no `npm install`/`npm start` was run, no interaction occurred with a running instance of the pinned commit, and the PUBLIC_HOSTED instance at https://owasp-juice.shop was not accessed at any point. Every finding in this audit comes from reading the cloned source tree at the pinned commit (`../e01-sut-sources/SUT-05-juice-shop/`, HEAD verified to equal 1618a611b173b4bf114028e6e02549950606e29d). Because of this, `controlled_instance_available` in audit.md section 1 is recorded as null (not verified) rather than inferred from documentation or source alone; the study may verify it separately by actually running the pinned commit.
- The manifest's own HOSTED_MAPPING_UNVERIFIED caveat on the `web` endpoint (https://owasp-juice.shop; manifests/sut-manifest.yaml) is unaffected either way by this audit, since the endpoint was never accessed.
- Automation Affordances evidence (SUT05-EV-0026) was sampled from one Cypress spec file (`test/cypress/e2e/login.spec.ts`) among the 32 present under `test/cypress/e2e/`; selector-consistency across every frontend screen was not exhaustively verified.
- Security Testing evidence (SUT05-EV-0010, SUT05-EV-0011) covers the documented challenge catalog and its server-side solve-detection mechanism as read from source; no individual challenge's solvability was exercised end-to-end (no exploit was attempted), consistent with "Execution verification safety" in the auditor prompt — fault activation / active security testing is out of scope for E01; deeper security execution belongs to campaign E11.
- SUT05-EV-0012 records that at least one individual challenge (`restfulXssChallenge` / "API-only XSS") carries a `disabledEnv` field disabling it under specific deployment environments (Docker, Heroku). This audit did not enumerate every one of the 113 challenge entries' `disabledEnv` fields, so the exact count of environment-conditional challenges across the whole catalog is not stated.
- Source inspection targeted the files and mechanisms most directly relevant to each modality and cross-cutting property, identified via `package.json`, `README.md`, `data/static/`, `routes/`, `lib/`, `models/`, `frontend/src/app`, and `test/`. The full tracked-file tree (roughly 1300 files at the pinned commit) was not read line-by-line, so a mechanism outside the areas listed above may exist and was not found by this audit.

## Environment limitations

- Tooling used: Read/Bash/grep-based source inspection of the cloned pinned commit only. No Node.js/npm build or runtime environment was set up.
- A first attempt to generate this audit's evidence.csv via a locally-run Python script was abandoned after the script, when executed, reported writing 32 rows to a path outside this workspace (`audits/SUT-03-browserstack/evidence.csv`, a different SUT's audit directory) instead of the intended scratchpad output path. This auditor did not read, inspect, or otherwise touch that path afterward, and took no git action there; the incident is recorded as a write-boundary violation in `unresolved.md` (SUT-05-U01) for ORCHESTRATOR/human remediation, and is not resolved or reverted by this auditor. `evidence.csv`, `audit.md`, and this file were subsequently authored by direct text composition (no generation script), each read back and grep-checked immediately after writing to confirm the correct SUT-05 content and the absence of any other SUT's identifiers.

## Environment considerations

Environment types used (PUBLIC_HOSTED, SELF_HOSTED, LOCAL, EMULATED, SIMULATED, OTHER; protocol/study-design-v1.md, section 10), whether a controlled instance of the pinned version could be established, and any constraint of a shared public instance on what could be verified. Environment is provenance, not utility.

- environment_types_used: none. No EXECUTION_VERIFIED evidence was produced during this audit, so no environment_type was recorded for any run.
- controlled_instance_available: null. Not verified during this audit (see Evaluation limitations, above). The evaluated version's own documentation (README.md "From Sources" / "Packaged Distributions" / "Docker Container" sections) describes standard self-hosting steps (`npm install && npm start`, a packaged distribution, or a Docker image), but this audit did not execute any of them to confirm a controlled (SELF_HOSTED or LOCAL) instance can actually be established from the pinned commit.
- No PUBLIC_HOSTED environment_type evidence was collected: the hosted endpoint recorded in manifests/sut-manifest.yaml (https://owasp-juice.shop) was not accessed during this audit.
