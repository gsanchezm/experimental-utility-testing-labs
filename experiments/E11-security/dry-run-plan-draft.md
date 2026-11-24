# E11-security: DRY_RUN plan (DRAFT-1, 2026-11-24 UTC)

**DRAFT. Nothing here dispatches, starts, authorizes or freezes anything.** A DRY_RUN is a non-measured verification: its bundles are reviewed, never imported into raw-data/ and never counted. Workflow: `.github/workflows/e11-environment-verification.yml` (dispatch-only). Executor: experiments/E11-security/executor/. Cells: conditions-draft.json (14 cells).

## 1. What must be public first

GitHub Actions evaluates only the public repository (the agent-instructions file, "E03 CI/CD infrastructure"). The workflow, the executor, `conditions-draft.json`, the working prompt `prompts/working/ORCHESTRATOR-E11-security-v1.md`, the pin proposal and the decision records reach the public repository only through a public export (next: v83; PUBLIC-EXPORT-MANIFEST.yaml). Each export push needs the human research lead's yes to its exact line. The first export that carries a new workflow file also shows whether GitHub accepts it (the measured workflows of E03 once had a file rejected for a run script over the length limit; the validation workflow now checks that limit).

## 2. Round 1 (proposed)

| Input | Value |
|---|---|
| target | `all` (fourteen jobs; the seven M2 jobs each pull the ZAP image, about 1.2 GB compressed) |
| executions | `2` (the check requires exactly this many run manifests per cell) |
| executor_prompt_version | `ORCHESTRATOR-E11-security-v1` (working copy; the workflow's gate requires it to exist) |
| executor_implementation_sha256 | sha256 of `experiments/E11-security/executor/run-condition.sh` at the commit that is public at the dispatch; at this draft: `298b728d1ca273dd15384a7d2550c65a359bc8e6cfb9bb4f0ecef1a100714c90` (recomputed at dispatch; it changes with any edit of an executor file because the digests of the files are embedded) |
| dry_run | `true` |

The dispatch line is offered to the human research lead in its exact form, with the then-current hash, before it is made; one dispatch per round, no re-run.

## 3. What round 1 must show (the open items; IMPLEMENTATION-NOTES.md, section 3)

1. ZAP API names and parameters: any `ZAP_API_ERROR` names the call that failed; corrections go in a new executor revision, never in a patched run.
2. The image pulled by digest on the runner (the step records the inspect line and the pull times) and `ZAP_START_FAILED` if not.
3. The installed add-ons (the `addons_before` and `addons_after` lists and `addons_unchanged` in the observation of the `method` step of each `attempt-record.json`): the values to record in manifests/toolchain-manifest.yaml, `tools.security`, together with the install date and the platform, after the human research lead approves the entry.
4. For each SUT-05 M1 condition cell: the oracle flips in both executions (V-3, V-4); for each control cell it does not.
5. V-7: the outcome of rule 0 on `/ftp/` (predicted: no alert). The expectation is not changed after the observation (E11-D-9).
6. V-8: whether rule 40018 acts on the JSON login body and on the search query; what the control endpoints answer (`/assets/` in particular).
7. The timing of an M2 execution (instance restart, container start, scan) from `duration_s` in the attempt records: the basis of E11-D-14 (50 sequential executions must fit the job limit with margin; the verification job limit is 120 minutes and the measured job limit is to be set from this).
8. The IDOR pair: GET as `security_glitch_user` is 200 and as `standard_user` is 403 (SUT01-EV-0023).

## 4. After round 1

A red job is information, not a failure of the study: the bundle is uploaded with `if: always()`. The corrections are executor, workflow or configuration changes; each is a commit, a new public export and a new round (a third round is the START candidate, as for E05 and E09). The measured workflow is written after round 1 or 2, from the same provisioning steps. A START, the dispatch authorizations, the frozen prompt, the lock of the configuration and the freeze each need the human research lead's explicit approval.

## 5. Not done by a DRY_RUN

It measures nothing, imports nothing, records no entry in manifests/toolchain-manifest.yaml, changes no expectation, and produces no detection rate.
