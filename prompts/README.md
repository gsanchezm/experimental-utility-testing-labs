# prompts/ — Agent Prompts

Study: Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001). Protocol v1/v2 FROZEN-PRE-DATA (protocol/change-control-v1.md). This directory holds the prompts given to the agent roles defined in protocol/agent-governance-v1.md when they act on a system under test (SUT) or on study data.

## Directories

| Directory | Content | Editable |
|---|---|---|
| prompts/working/ | Draft agent prompts under development, before use in any campaign | yes |
| prompts/frozen/ | Exact prompts actually used during data collection, versioned | no — a change creates a new version |

## Rules

1. **working/ contains draft agent prompts.** Drafts may be edited freely until the moment they are used for a campaign.
2. **frozen/ contains prompts actually used during data collection.** Once an agent prompt is used for a campaign, the exact prompt text is copied into frozen/ with a version identifier, no later than the first run that uses it.
3. **Naming convention (candidate — not frozen):** `<role>-<campaign-id>-v<N>.md`, for example `AUDITOR-SUT03-BROWSERSTACK-E01-capability-audit-v1.md`. `<role>` is a role name from protocol/agent-governance-v1.md; `<campaign-id>` is the full campaign directory name (E01-capability-audit through E12-localization-i18n), as used in raw-data/ and in run manifests; `<N>` starts at 1 and increments with every change.
4. **Never silently edit a frozen prompt.** Any change creates a new version file (`v<N+1>`) and is recorded in the change log per protocol/change-control-v1.md. The earlier version stays on disk unchanged.
5. **Frozen prompts are provenance for the runs that used them.** Every run manifest (schemas/run-manifest.schema.json) references the `prompt_version` of the frozen prompt under which the run was executed. A run whose prompt_version does not resolve to a file in frozen/ is not attributable, with one exception: a run executed by a human operator without an agent prompt records prompt_version null, the operator in agent_role, and the reason in notes, and is attributable through its run manifest.
6. Prompts for the same campaign give every SUT the same task and the same rules (AGENT-INSTRUCTIONS.md rules 10–12). Per-role differences are limited to the assigned SUT, its workspace, and the modalities applicable to it. No prompt presupposes a score, result, or ranking for any SUT.

## Tracking

Both directories are tracked by git; each contains a .gitkeep so the empty directory is committed. .gitignore re-includes prompts/frozen/** and prompts/working/** after its noise patterns.

## Current status

- Three prompts are frozen (E01-capability-audit only): `prompts/frozen/e01-capability-auditor-v1.md` (used by all six auditors); `prompts/frozen/e01-adjudicator-v1.md` (superseded in place per PROTO-U03's remedy — a non-substantive correction to its self-disqualifying status line — and immediately followed by `prompts/frozen/e01-adjudicator-v2.md`, the version actually used by ADJUDICATOR-EU-01).
- No prompt exists yet for any other campaign, including E03-resetability: prompt authoring and freeze are an explicit, later step of E03's own campaign-start sequence, not performed during PRE-START preparation (`protocol/agent-governance-v2.md`, FROZEN-PRE-DATA 2026-09-22).
- One working prompt exists for the mobile qualification gate: `prompts/working/qualifier-mobile-01-mobilewright-gate-v1.md` (QUALIFIER-MOBILE-01; prepared 2026-09-22 with `manifests/mobile-qualification-package-v1.yaml`). It is not frozen and has not been used; it is frozen to `prompts/frozen/` with a version id only after the human MOBILE_QUALIFICATION_EXECUTION authorization and no later than the first run (rules 2–5).
