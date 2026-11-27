# E08-performance: DRY_RUN plan (DRAFT-1, 2026-11-26 UTC)

**DRAFT. Nothing here dispatches, starts, authorizes or freezes anything.** A DRY_RUN is a non-measured verification: its bundles are reviewed, never imported into raw-data/ and never counted. Workflow: `.github/workflows/e08-environment-verification.yml` (dispatch-only). Executor: experiments/E08-performance/executor/. Conditions: conditions-draft.json (four conditions).

## 1. What must be public first

GitHub Actions evaluates only the public repository (the agent-instructions file, "E03 CI/CD infrastructure"). The two workflows, the executor, `conditions-draft.json`, the working prompt `prompts/working/ORCHESTRATOR-E08-performance-v1.md` and the decision records reach the public repository only through a public export (next: v90; PUBLIC-EXPORT-MANIFEST.yaml). Each export push needs the human research lead's yes to its exact line. The first export that carries a new workflow file also shows whether GitHub accepts it (the validation workflow checks the run-script length limit of OP-CI-15).

## 2. Round 1 (proposed)

| Input | Value |
|---|---|
| target | `all` (four jobs; each provisions its own SUT; the two SUT-03 jobs build the Next.js application twice) |
| executions | `3` (the check requires exactly this many run manifests per condition; three executions show each of the three load orders once) |
| executor_prompt_version | `ORCHESTRATOR-E08-performance-v1` (working copy; the workflow's gate requires it to exist) |
| executor_implementation_sha256 | sha256 of `experiments/E08-performance/executor/run-condition.sh` at the commit that is public at the dispatch (recomputed at dispatch; it changes with any edit of an executor file because the digests of the files are embedded) |
| dry_run | `true` |

The dispatch line is offered to the human research lead in its exact form, with the then-current hash, before it is made; one dispatch per round, no re-run.

## 3. What round 1 must show (the open items; executor/IMPLEMENTATION-NOTES.md, section 3)

1. SUT-01: the first catalogue item of D appears about 3 s after that of Ba (V-1); the login of both accounts answers with the expected behavior; the ready signal appears in every load.
2. SUT-02: the Long Tasks API reports the 5000 ms render of the inventory page as one long task in the pinned Chromium (V-2); the inventory list appears after the login for both accounts; the session cookie names the account.
3. SUT-03: the `/sut/login` flow sets the cookie in a fresh context and the three pages load without redirect (V-3). The login form is hydrated before the click (`form_hydrated_before_click` in each activation record); a `START_ACTIVATION_NOT_CONFIRMED` whose URL carries a query string means that the click came before the hydration, a harness defect and not a finding about the SUT. What the zero-cls page records as its largest paint (V-4); whether `picsum.photos` answers from the runner and the image paints as a largest-paint candidate, and the literal `url` of that largest-paint entry in the probe snapshot (the rule matches the host `picsum.photos` as a substring, so a redirect to a subdomain still counts, and the literal value is recorded to confirm it).
4. SUT-03 CLS: the observed value on the high-CLS page (predicted 0; V-4b). The expectation is not changed after the observation (E08-D-8).
5. V-6: the spread of the baseline loads of the same condition (Ba against Bb of each execution) compared with the tolerances of 500 ms; the first view of the baseline-against-baseline false-positive record.
6. The durations of an execution of each condition, from `duration_s` in the attempt records: the basis of E08-D-13 (the measured job limit and the watchdog are set from them).
7. The version strings of Playwright and Chromium in the run manifests, for the entry of `tools.performance` (E08-D-11).

## 3b. Round 1 happened (2026-11-26, run 45878792738)

Its outcome is in manifests/e08-environment-verification-rounds-v1.yaml (all jobs success; 12 executions; four conditions VERIFIED in experiments/E08-performance/controlled-instance-status.yaml). Whether round 1 can serve as the START candidate depends on whether the implementation or the workflows change before the START (E08-D-13 time budgets are the open item): an unchanged implementation hash `da24b1326d8ef55711fe077ac7363efccbf4c9d0277e6943e19649b9b1d7e4b2` keeps the verification valid, a change needs a further round.

## 4. After round 1

A red job is information, not a failure of the study: the bundle is uploaded with `if: always()`. The corrections are executor, workflow or configuration changes; each is a commit, a new public export and a new round (a third round is the START candidate, as for E05, E09 and E11). A START, the dispatch authorizations, the frozen prompt, the lock of the configuration and the freeze each need the human research lead's explicit approval.

## 5. Not done by a DRY_RUN

It measures nothing, imports nothing, records no entry in manifests/toolchain-manifest.yaml, changes no expectation, and produces no detection rate.
