# E08-performance executor: implementation notes (DRAFT, operation OP-PREP-E08, 2026-11-26 UTC)

Not frozen, not locked. These notes say what the implementation derives from, what it decides, and what is open. They are not a result and not a decision of the human research lead.

## 1. Derivation

The framework (job context, run, scrubber, evidence, manifest builder, attempt loop, the digest lock) is copied from the E11 executor and, through it, from E05 (each campaign locks its own copy; nothing is imported from another campaign path at run time). The SUT-01 login and client-state seeding are those of the E09 executor (the E03 SUT-01 web realization). The provisioning steps of the workflows are those of E05 for SUT-01 and SUT-02 and those of E03 for SUT-03, assembled so that the verification and the measured workflow carry the same step text (the two files are the product, the generator is not part of the repository, and test_workflows.py enforces the equality). What is new in E08: the in-page measurement script (probe.py), the metrics and the rule (classify.py), one execution as three loads in fresh contexts in a rotating order (attempt.py, sut01.py to sut03.py), the false-positive record of a baseline against a baseline, and the gate G-10 that ties `tools.performance` of the toolchain manifest to the Playwright pin and the probe version of the implementation.

## 2. Choices made in the implementation (each is a HUMAN DECISION of campaign-configuration-draft.md, section 6, or a harness fact)

1. **Fresh context per load, one Chromium per job.** A context has its own cache, storage and cookies, so one load cannot warm another and a login of one load cannot leak into the next. The Chromium process is shared (starting it per load would add noise and time). E08-D-9.
2. **The measured navigation is a full document load** with the probe present from the start of the document, after the login and, for SUT-01, after the seeding of the client state. The login and the first load are not measured. For SUT-02 the application blocks 5 s while it renders the inventory page after the login of the glitch account; that block belongs to the unmeasured login and the list is awaited before the measured navigation.
3. **Times are `performance.now()` of the measured document**, whose origin is the start of the navigation. `wait_until='commit'` returns when the document is committed; the waits that follow run in that document.
4. **No sampling thresholds are tuned.** The thresholds are the expected effect of the evidence minus a tolerance of 500 ms, fixed in conditions-draft.json before any run. A DRY_RUN may show that a tolerance is not far enough above the spread of the baseline loads (V-6); a change is then a configuration change under its own approval, not an adaptation to an outcome.
5. **`required_ready`.** A load whose page never showed its own content cannot be a measurement; otherwise a login page, which has no long task and no layout shift, would be recorded as a non-detection. The watch selectors and the required keys are data of conditions-draft.json.
6. **The SUT-03 baseline is `/sut/ui/zero-cls` for both conditions** (SUT03-EV-0014 names it as the paired page of the CLS page; for the LCP condition the choice is E08-D-19). Its largest paint is expected to be the text of its card at hydration; round 1 shows whether it is.
7. **The external image.** `INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED` is returned only when the rule did not hold and the final largest-paint candidates of D do not include the image URL. When the image painted, the rule is applied to its time as it is.
8. **Screenshots** are taken for the degraded load only (viewport, not full page), to keep the raw data small (about 200 files for the campaign).
9. **The passwords of SUT-01 (`pizza123`) and SUT-02 (`secret_sauce`) are registered with the scrubber; the dummy password of SUT-03 (`password`) is not**: it is shown in the labels of the login page and is a word that occurs in every form field name, so registering it would corrupt the evidence without protecting anything.
10. **Time budgets.** Watchdog 420 s per execution (the worst case of an SUT-03 execution is three loads of a 30 s login wait, a 30 s navigation and the 8 s window); the measured job 120 min; both are re-set from the DRY_RUN durations before the START (E08-D-13).
11. **SUT-01 tokens** are obtained once per execution in the starting-state block and reused by the loads of that execution; every execution logs in again.
12. **`behavior_class`.** `deterministic` for DELAY, BLOCK and CLS; `external dependency` for LCP (the delayed element is an image of `picsum.photos`, SUT03-EV-0013). The schema enum is used as it is.

## 3. Open items that only a real run can close (DRY_RUN round 1; dry-run-plan-draft.md, section 3)

- Does the Long Tasks API report the 5000 ms render of the SUT-02 inventory page as one task in the pinned Chromium (V-2)? The executor treats an absent API as `INCONCLUSIVE_METRIC_ABSENT` and an observed API with no entry as 0 ms.
- Does `[data-test="inventory-list"]` appear after the login for both accounts, and does `h2[data-testid^="pizza-name-"]` appear on the catalogue for both (V-1)?
- Does `/sut/login` set the cookie in a fresh context and do the three pages load without a redirect (V-3)? What is the largest paint of `/sut/ui/zero-cls` (V-4)?
- Does `picsum.photos` answer from the runner, and does the image paint as a largest-paint candidate? If the host refuses runner traffic, the LCP condition is recorded `INCONCLUSIVE_EXTERNAL_IMAGE_NOT_LOADED` in every execution and the human research lead decides what that means for the configuration; the rule is not changed to fit.
- What does the high-CLS page record? The static reading predicts cls 0 (configuration draft, section 4c, V-4b); the expectation stays (E08-D-8).
- The spread of Ba against Bb on a GitHub-hosted runner (V-6), and the durations of the executions (E08-D-13).
- The version strings of Playwright and Chromium for the entry of `tools.performance` (E08-D-11).

## 4. Known limits

- The probe registers its observers at the start of the document; a long task or a shift that happens before the init script runs cannot occur (the script runs before any page script).
- The first Largest Contentful Paint entries can be superseded by later ones until user input or the end of the window; the executor reads the last one at the end of the window, and there is no user input.
- Playwright starts headless Chromium with its scrollbars hidden (to be confirmed in round 1 from the layout of the page), so no layout shift is expected from a scrollbar appearing.
- The script leaves three globals in the page (`__e08_config`, `__e08`, `__e08_flush`); the pages of the three SUTs do not read them.
- Nothing here measures load: one sequential client, no significant load (design brief, section 4).
