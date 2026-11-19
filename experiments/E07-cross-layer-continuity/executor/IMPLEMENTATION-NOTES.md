# E07-cross-layer-continuity executor: implementation notes (DRAFT, preparation only; operation OP-PREP-E07-04)

Status: draft. Nothing here is locked, hashed into a START, or authorized. The executor is derived from the E04 executor
(experiments/E04-repeatability/executor/) by copying, then changing the blocks to a cross-layer establishment and verification. The design
defaults are those of ../design-brief-draft.md (sections 17 and 18) and ../campaign-configuration-draft.md, with the decisions of
manifests/campaign-execution-decisions-v10.yaml, -v11.yaml and -v12.yaml. Every difference from E04 is listed below.

## 1. Shape

One job runs the N = 50 executions of ONE condition, sequentially, on one shared instance (the model B of E05, decision D-02, as decided for E07 in
D-E07-8). Four conditions (SUT-01 and SUT-04, each in the two directions), four jobs, 200 executions. Every execution establishes one unit on the
source layer and verifies it on the other layer: reset, starting-state check, establishment, establishment check, verification, record. Entry
point: `run-condition.sh`, which verifies the embedded digests and then runs `python3 -m executor.run`.

## 2. Points fixed here (each is a default pending the START package)

1. **Block order inside one execution.** reset, starting-state check, establishment (source layer), establishment check (source layer, read-only),
   verification (the other layer, read-only), record. The establishment check is the only new block: it confirms on the source layer that the unit is
   established and records in `run.identity['established']` what the verification must find. A failed establishment check is ESTABLISHMENT_FAILED
   ("the establishment or its source-side check did not confirm the unit", D-E07-10).
2. **Continuation rule.** E04 point 2, unchanged: a block that does not hold stops that execution with its pre-declared category; the job goes on with
   the next execution. Only a failure of the job itself stops the job.
3. **Attribution (D-E07-10, as E04: issue (xix), decision D-16 option B).** `classify.attribution(interrupted, infrastructure_interruption)` labels an
   execution TOOLING when a block was stopped by an exception of the executor, the browser or the client (`PhaseFailure.interrupted`, or an exception
   between blocks) or by the per-execution watchdog, and SUT otherwise, including every recorded failure and every execution whose cause cannot be assigned
   mechanically. The response clause of the design default of E04 is not implemented, for the reason E04 gives. A transport failure of an HTTP call made by
   `Run.http` (no status) reaches the block as a recorded failure and stays SUT (open item 7). The workflow-recorded infrastructure interruption is not an
   input of the executor (`infrastructure_interruption` is always False; open item 11).
4. **Categories (declared in conditions-draft.json, checked by `config.validate`).** VERIFIED (status SUCCESS; every declared key and attribute matches);
   NOT_VERIFIED (status FAILURE; the verification block did not hold: a key or attribute is absent or different, or the verification read answered an error
   or did not answer; attribution SUT; the cause names what differed); ESTABLISHMENT_FAILED (status ABORTED; the establishment or the establishment check did
   not hold; SUT); INTERRUPTED (status ABORTED) with the cause RESET_FAILED (the reset did not hold, SUT), STARTING_STATE_NOT_REACHED (the declared starting
   state does not hold after the reset, SUT) or WATCHDOG (the per-execution budget was exceeded in any block, TOOLING); RUNNER_ERROR (status ERROR; an exception of
   the executor, the browser, the client or the infrastructure in any block, TOOLING; `last_phase` is recorded). `config.validate` refuses a file whose categories,
   causes or attribution labels differ from the executor, so a sixth category cannot be added by editing the file alone. The cause of an INTERRUPTED execution is
   the field `interrupted_cause` of attempt-record.json (also in the log and in the manifest notes as `interrupted_cause=<cause>`), never a part of the category label.
   The mapping from block to category is `classify.PHASE_LABEL`; the statuses are `classify.OUTCOME_STATUS`.
5. **Manifest.** `outcome.expected` is VERIFIED for every condition; `matches_expected` compares the recorded label with it and never with an observation.
   `scenario` and `target_state_id` are the canonical scenario id (CS-005 or CS-006), `starting_state_id` is `<scenario>-STARTING`, `source_layer` and
   `verification_layer` are set on every record (the schema keeps them optional; the campaign convention makes them mandatory). `behavior_class` is not written.
   No `actions[]`. `outcome.observed` on success is the fixed text "continuity verified: every declared identity key and attribute matched on the verification
   layer". The values of `platform` and `modality` are those of the SOURCE layer (api and API; web and Web UI Functional): the schema describes `platform` as the
   platform layer the run exercised and has no cross-layer convention (open item 8). `establishment_mechanisms` and `reset_mechanisms` use the vocabulary of the schema.
6. **A new browser context per execution (D-E07-8).** E04 kept one context for the whole job, so that the reset of the condition was a real measurement. E07
   creates a new context in `web.Browser.bind` for every execution (the previous one is closed), so an execution starts with empty client storage and no cookie and the
   client state it uses is the state the scenario creates. A browser that is gone is relaunched and the event is recorded in the notes. Both SUT-01 conditions then
   inject the client state once per execution (the E03 realization W-A, copied by value), and both SUT-04 conditions log in to the admin web app once per execution.
7. **Reset (D-E07-8, outside the scenario, not counted, DATA_RESET).** SUT-01: POST /api/auth/login, then POST /api/session/reset with the session token (API_RESET,
   SESSION_RESET), then the injection of client state with an empty client cart. Orders persist beyond that reset (SUT01-EV-0006); E07 creates no order. SUT-04:
   delete through the booking API every booking of room 1 whose first name is the condition's first name (found by listing, so a booking left by an earlier execution
   is deleted), then the admin login in the new browser context. The starting-state check reads the server cart and the client cart (SUT-01) or the listing of room 1
   (SUT-04), so a reset that did not hold is seen by the next execution.
8. **Identity keys (D-E07-9).** SUT-01: the sid claim of the login token (recorded as a digest), the number of cart lines, the pizza_id and the quantity of the line.
   On the WEB layer the pizza_id is the order line `order-item-<pizza_id>` of the Checkout view, the quantity is the integer at the start of the text of
   `order-item-details-<pizza_id>` (`{quantity}x • {size}`), and the sid is the claim of the token held by the web client (`omnipizza-auth`); on the API layer they are
   `cart_items` of GET /api/session and the claim of the token presented. SUT-04: the number of bookings with the run's names, the first name, the last name and the
   check-in date and the check-out date on both layers (D-E07-15: DRY_RUN round 1 showed that the admin web row lists both dates, so the check-out date is observable on the WEB
   layer and is compared there). A key that a verification layer does not show is not used (D-E07-9) and would be listed under `identity.not_compared` with the reason; no
   key is listed there at present. The bookingid is not a key.
9. **Run-unique values.** The first name of the SUT-04 guest is derived from the condition id (stable across the executions of the condition: the marker that the
   reset and the starting-state check use); the last name, the check-in date (2031-01-01 plus fewer than 3000 days; check-out one day later) and the email are derived
   from the run id, so they are unique per execution and attempt (letters only, 8 and 9 characters, as E04). The phone value is the E04 value.
10. **Reuse.** The API login, the session read, the cart seed and the session reset of SUT-01, the client-state injection, the Checkout read, the SUT-04 login, listing,
    booking, delete, admin login, reservation form and admin room rows are the E04 and E03 code, copied by value (no import across campaigns). The selectors, endpoints
    and flows that have no source in an E01 row, a CS record or an E03 or E04 text are listed in open item 1; each is marked in the module docstring.
11. **Not carried from the E04 code.** The SUT-02 and SUT-05 modules, the SUT-01 API-only and process-restart realizations, the SUT-04 message-count baseline, `instance.restart`
    and its helpers (no E07 reset restarts a process), the restart logs of `instance.collect_logs`, `web.Browser.reload`, `responses_since` and `dom`, `web.session_storage`, the
    stub category STUB_NO_BUNDLE and the phase names of the establishment-only design. Not carried into the tests: the fake SUT-05, the restart tests and the SUT-02 and SUT-05 realization tests.
12. **Integrity.** `run-condition.sh` embeds the digests of executor/*.py and requirements.txt, generated by `tests/embed_digests.py`. `requirements.txt` keeps the pins and hashes
    of the E04 file unchanged (checked: every line that is not a comment is identical); only its header comment names E07.
13. **Web legs and tests.** The Playwright code is in the classes `Sut01Ui` (executor/sut01.py) and `Sut04Ui` (executor/sut04.py); a realization reaches it through `make_ui`, which a test
    overrides with a fake that talks to the fake SUT over HTTP. `test_ui_calls.py` runs the same classes against a recording stand-in for the browser. The static tests ran with Python 3.14;
    the CI interpreter of E04 is the 3.12 series, and no syntax newer than 3.8 is used.
14. **Not computed.** No rate, interval or comparison of any kind is computed by the executor. The continuity proportions (option A and option B of D-E07-10), the Wilson intervals and the
    NOT_COMPARABLE reporting belong to the analysis, which does not exist yet.

## 3. Open items (for the START package; none decided)

1. **Selectors and flows read from the pinned source.** The catalog route `/catalog`, the add control `add-to-cart-p02-desktop` (tid() appends `-desktop` at a viewport of 768 px or more), the confirm control
   `confirm-add-to-cart` of the customizer modal, the quantity text `order-item-details-p02`, and the persisted client cart `omnipizza-cart` are taken from the SUT-01 source at its pinned commit 9ca37674 (file and line
   references in the docstring of executor/sut01.py), read in a local clone, not from a CS record, an E01 row or an E03 or E04 text. They are unverified until the DRY_RUN rounds run them on GitHub Actions.
2. **The open cell E07-CS006-SUT01-WEB-API (D-E07-6).** The source says the UI add writes only the persisted client store and makes no request, so the server cart is expected to lack the line and the condition is expected to record NOT_VERIFIED.
   The executor records the observation and adjusts nothing. Whether the cell stays COMPARABLE, becomes NOT_COMPARABLE, or is measured as it is, is the human research lead's decision after the DRY_RUN rounds.
3. **The check-out date on the admin web row (E07-CS005-SUT04-API-WEB).** Resolved (D-E07-15, manifests/campaign-execution-decisions-v15.yaml): the row shows the date (DRY_RUN round 1, evidence `sut04-web-admin-rows`), the executor compares it on the WEB layer, and DRY_RUN round 2 verifies the change on GitHub Actions before the START.
4. **The quantity locator of the Checkout view.** The locator comes from open item 1; if it is absent, the quantity is not observed and the execution is NOT_VERIFIED on that key.
5. **The sid key is partly circular.** The web client holds the token that the executor injected, and the API verification presents the token of the login, so the key confirms that the session binding survived the layer (the web client's token still carries the sid of the establishment),
   not an independent derivation of the session. If a DRY_RUN shows the SUT rewriting the token on a page load, the key would differ and be recorded; whether the key stays in D-E07-9 is for the human research lead.
6. **A bundle that cannot be written.** E04 kept the category STUB_NO_BUNDLE, attributed SUT. The five categories of D-E07-10 have no place for it, so E07 writes a record of the category RUNNER_ERROR, attribution TOOLING, cause BUNDLE_NOT_WRITTEN. conditions-draft.json is not changed. Confirm or declare a sixth category.
7. **A verification read that does not answer.** An HTTP error answer of a verification read is a completed observation (NOT_VERIFIED, SUT, D-E07-10). A transport failure with no answer is recorded by `Run.http` as a failure without a status and is also NOT_VERIFIED, SUT (a recorded failure
   of the block; its cause cannot be assigned mechanically). An exception of the browser during the web verification is RUNNER_ERROR (TOOLING). Confirm the first two against the wording "the observation completed".
8. **`platform` and `modality` of a cross-layer record.** Both follow the source layer (point 5); the schema leaves the cross-layer convention open. Fix at the START.
9. **The budgets.** The per-execution watchdog (`common.WATCHDOG_S`, 600 s, inherited) and the job timeout of the workflow are E04 values; re-derive them from the DRY_RUN durations. A new browser context per execution adds time.
10. **The admin web session of SUT-04.** Both SUT-04 conditions log in to the admin web app in the reset block (CS-005 and CS-006 list it as a precondition); the reservation route may not need it. Confirm that the login stays in both.
11. **A runner cancelled or lost by the workflow.** Its recording as TOOLING is the ORCHESTRATOR's at import; the executor passes no infrastructure interruption.
12. **The controlled-instance status of the E07 conditions.** It does not exist; it is created from the DRY_RUN rounds and a decision of the human research lead (the workflow preparation drafts the file).
13. **The reservation form values.** The email and phone values of the SUT-04 web form follow E04 (the form fields are those of the E03 section 4.6); the booking made through the form also posts a message in the SUT, which no E07 block reads.

## 4. Not in this draft

Any analysis script, any START record, any dispatch authorization, any controlled-instance verification, any frozen prompt, any workflow, any change to E03, E04 or E05, and any E07 measured data. The E07 README, the design brief,
the configuration draft, the conditions file and the scenario records in experiments/ are not edited.
