# E04-repeatability executor: implementation notes (DRAFT, preparation only; operation OP-PREP-E04)

Status: draft. Nothing here is locked, hashed into a START, or authorized. The executor is derived from the E05 executor
(experiments/E05-determinism/executor/, whose implementation hash is recorded in experiments/E05-determinism/README.md) by copying,
then removing the stimulus and classification blocks. The design defaults are those of ../design-notes-draft.md, section 2, and are
pending the human research lead's confirmation at the E04 START package. The reused code is unchanged in behavior; every difference is
listed below.

## 1. Shape

One job runs the N = 50 executions of ONE condition, sequentially, on one shared instance (the model B of E05, decision D-02, carried
over as a working default). Thirteen conditions, thirteen jobs. Every execution is establishment-only: reset, starting-state check,
establishment, target-state verification, record. Entry point: `run-condition.sh`, which verifies the embedded digests and then runs
`python3 -m executor.run`.

## 2. Points fixed here (each is a default pending the START package)

1. **Block order inside one execution.** reset, starting-state check, establishment, target-state verification, record. E05's stimulus
   and classification blocks are removed. No block after verification exists.
2. **Continuation rule.** E05 point 2, unchanged: a block that does not hold stops that execution with its pre-declared category; the job
   goes on with the next execution. Only a failure of the job itself stops the job.
3. **Attribution (issue (xix), decision D-16 option B; the response clause of design default 3 is not implemented).** `classify.attribution(interrupted, infrastructure_interruption)` labels an execution TOOLING when a block was interrupted by a harness or client exception (`PhaseFailure.interrupted`, or an exception between blocks), and SUT otherwise, including every recorded failure and every execution whose cause cannot be assigned mechanically. This is the E05 labeling of the reused blocks: E05's stimulus-request boundary (`stimulus_sent`) was never crossed inside them, so their interruptions were TOOLING. The response clause of design default 3 (an exception after a response of the SUT is SUT) is not implemented, because every realization receives a response before its first block that can raise (the login or the page load), so the clause would make TOOLING almost unreachable. It is open (section 3, item 4). Transport errors recorded by `Run.http` (no status) stay SUT, as in E05, because they reach the block as recorded failures, not as exceptions. The workflow-recorded infrastructure interruption is not an input of the executor (`infrastructure_interruption` is always False; open item 7).
4. **Categories.** Success: `TARGET_STATE_VERIFIED` (config.SUCCESS_CATEGORY), phase VERIFIED, status SUCCESS. Failures: `RESET_FAILED`,
   `RESET_STARTING_STATE_NOT_REACHED`, `ESTABLISHMENT_FAILED`, `ESTABLISHMENT_VERIFICATION_FAILED`, `ESTABLISHMENT_INTERRUPTED`,
   `STUB_NO_BUNDLE`. The success prefix `TARGET_STATE_` is distinct from every failure prefix, and `config.validate` refuses a file in which
   it is not; a test checks that only the success category yields status SUCCESS. `ESTABLISHMENT_INTERRUPTED` is the interruption category
   of E04 (there is no stimulus block, so no `INTERRUPTED_` category exists). A reset or starting-state interruption is `RESET_FAILED` or
   `RESET_STARTING_STATE_NOT_REACHED` with TOOLING attribution, as in E05. An unknown block or label is refused (ValueError), where E05
   mapped an undeclared label to a catch-all.
5. **Manifest.** `outcome.expected` is `TARGET_STATE_VERIFIED` for every condition; `matches_expected` compares the recorded label with it and
   never with an observation. `behavior_class` is not written: the schema lists it as optional (nullable, not required), and the E05 values
   were a stimulus-class declaration. No `actions[]` (the reset is a step, E05 decision D-08c). `outcome.observed` on success is the fixed
   text "target state verified: every block of the execution held".
6. **Reuse.** For each kept method of the thirteen realizations (reset, check_start, establish, verify_target, and their helpers), the AST
   of the E04 method is compared with the E05 method after normalizing only the campaign token (E05 to E04) and the renamed evidence label
   (point 8). The result: every reset, starting-state, establishment and verification method is identical, except the description string
   of the SUT-04 message-count step, which now reads "the baseline of the E05 stimulus". One identity change is normalized away by that
   comparison and is recorded here: the guest-name derivation salt is `E04|` (was `E05|`), so the names and contact values of an E04
   condition differ from those of its E05 counterpart. The comparison tool is a scratch script of the ORCHESTRATOR, not a repository file.
7. **Removed (stimulus or classification only).** In `sut01.py`: the `stimulus` and `classify` methods of API-01 to API-06 and WEB-01, the `get_catalog` helper, the `sut01_expected` import and the constant `MX_HEADERS` (the constant `CHECKOUT_BODY` lived in the deleted `sut01_expected.py`). In `sut02.py`: the `stimulus` and `classify` methods, the stub class `Web02`, `SPEC_WEB02`, `VISUAL_MARKER` and
   `NEXT_ITEM`. In `sut04.py`: the stimulus and classification methods of API-01, API-02 and WEB-01, `MESSAGE_WAIT_S`, `MESSAGE_POLL_S`, and
   the `time` import. In `sut05.py`: the stimulus and classification methods of API-01 and API-02, `_text`, `WRONG_PASSWORD`,
   `REJECTION_BODY` and `KEYS`. In `attempt.py`: the stimulus and classification calls, `finalize_label` and the catch-all lookup. In
   `classify.py`: the `S_` and `INTERRUPTED_` phases, `label_for_failure`'s catch-all, `finalize_label`. In `common.py`: `observe()` (it served
   only the stimulus and classification blocks), `mark_stimulus_sent`, the `stimulus_request_sent` record field, and `behavior_class` in
   the manifest. In `run.py`: the `classify` import. Deleted files: `executor/sut01_expected.py`, `expected-sut01.json` and
   `tools/derive_sut01_expected.py` (the expected values of the stimulus projections; used by no reset, check or verification).
   Deleted test file: `tests/test_web_classify.py` (stimulus classification only). The fake SUT-01 server drops its catalog and checkout
   routines and its lockout branch, which only the stimulus used.
8. **Evidence labels renamed.** The verification captures of the E05 realizations were labeled "pre-stimulus"; the label is now
   "target-state" in six places: `sut01-session-target-state`, `sut01-web-target-state`, `sut02-target-state`,
   `sut04-get-target-state`, `sut04-web-target-state` and `sut05-basket-target-state`. The names carry no meaning beyond the file name.
9. **Conditions.** Thirteen, mirroring E05's thirteen (`mirrors` field; `config.validate` checks the mirror's form, and a test checks the mirror's SUT, surface, account and reset against the E05 conditions file). Identical-block groups, derived from the executor code (the four block methods as resolved through inheritance, the mechanisms and components, and the reset kind; recorded in the `block_group` and `identical_blocks_with` fields of each condition): {E04-SUT01-API-01, -06} (restart; the accounts differ), {E04-SUT01-API-02, -03, -04, -05} (session clear; the accounts differ), {E04-SUT05-API-01, -02} (restart; the same account). No other pair of conditions runs identical blocks. The `pending` field of E04-SUT01-API-02, -03 and E04-SUT05-API-01, -02 states the open item (open item 1); E04-SUT04-API-02 is pending for its message-count read. E05-SUT02-WEB-02 has no mirror.
10. **Integrity.** `run-condition.sh` embeds the digests of executor/*.py and requirements.txt, generated by `tests/embed_digests.py`
    (`expected-sut01.json` is no longer a listed file). `requirements.txt` keeps the E05 pins and hashes unchanged; only its header comment was
    rewritten. The header of `run-condition.sh` names the E04 workflows and paths.
11. **Web helper.** `web.py` is unchanged in behavior; its docstring is rewritten. The shared browser context per job is unchanged. The response hook of an earlier draft is not present (point 3).
12. **Instance.** `instance.py` is unchanged in behavior. Its docstring is rewritten and the restart log prefix is `e04-restart-`.
    The restart sequence (SIGTERM to the process group, port refused, new session and group, readiness) is the E05 one.
13. **Workflows.** `.github/workflows/e04-measured-execution.yml` and `e04-environment-verification.yml` are E05's files renamed. Changes
    of content: the choice lists are the thirteen E04 conditions; the gate that required the H3 label in the configuration now requires
    the metric TSRR (proposed; the START decides the names); the controlled-instance path is proposed and names a file that does not exist,
    so the gate fails closed until the START creates it; the further-attempt gate is G-E04-A2; the timeout of 60 minutes is inherited from
    the E05 DRY_RUN rounds and is TBD for E04 (open item 5). The verification workflow has no IN_PROGRESS gate, as in E05: it is a
    DRY_RUN and needs no START. The measured workflow refuses every dispatch while E04 is NOT_STARTED, which is the intended state.
14. **Tests.** The suite is `tests/`; it runs with the documented command from this directory (section 5 of executor/README.md). Changed
    expectations: the attempt tests assert TARGET_STATE_VERIFIED and TOOLING for each interruption of a block; the configuration tests assert the
    mirror and the success and failure categories; the as-is gate test asserts that the NOT_STARTED repository state fails the START
    checks; the verification-gate test asserts the working prompt of E04 is present and that the check fails without it.

## 3. Open items (for the START package; none decided)

1. Identical-block groups (point 9): {E04-SUT01-API-01, -06}, {E04-SUT01-API-02, -03, -04, -05} and {E04-SUT05-API-01, -02}: keep the conditions as separate conditions, or merge them within a group.
2. The message-count baseline of E04-SUT04-API-02 (kept in verification, as E05's verification block contains it): confirm or remove.
3. The guest-name salt (`E04|`) and the reset's retained stimulus names of the SUT-04 conditions: confirm both.
4. The response clause of design default 3 (an exception after a response of the SUT is SUT): not implemented (point 3).
5. The timeout of 60 minutes: re-derive from E04 DRY_RUN durations; it is never raised before that.
6. The metric name TSRR in the configuration, and the E05-only quantities that E04 does not compute.
7. A runner cancelled or lost by the workflow: its recording as TOOLING (not implemented; the executor passes no infrastructure
   interruption).
8. The controlled-instance status file of E04: it does not exist; it is created only from the verification rounds and a decision of the
   human research lead.
9. The working prompt becomes a frozen copy only at the START (prompts/README.md).
10. Whether `ESTABLISHMENT_INTERRUPTED` also covers reset interruptions, which are recorded as RESET_FAILED here (as in E05).

## 4. Not in this draft

The TSRR analysis (no analysis script exists), any START record, any dispatch authorization, any controlled-instance verification, any
frozen prompt, any change to E05, and any E04 measured data. The E04 README in experiments/E04-repeatability/ is not edited.
