# Agent Governance

| Field | Value |
|---|---|
| Document | protocol/agent-governance-v1.md |
| Protocol version | v1 |
| Protocol state | AMENDED |
| Study | Experimental Utility of Software-Testing Laboratory Ecosystems (EUS-2026-001) |
| Created | 2026-09-15 |
| Last pre-freeze hardening iteration | instructed 2026-09-15, completed 2026-09-16 (state unchanged: DRAFT); final pre-freeze checklist closure (adjudication guidance for the tie-break rule, explicit human decision) instructed 2026-09-16, completed 2026-09-16 (state unchanged: DRAFT) |
| Freeze approval | gilbertosanchez, 2026-09-16 (protocol v1 pre-data freeze; protocol/change-control-v1.md, section 6) |
| Superseded by | protocol/agent-governance-v2.md |

## 1. Purpose

This document defines the roles under which automated agents and humans operate this repository, what each role is responsible for, and where each role may and may not write. Its goal is to keep audit evidence, adjudication, qualification, and experimental data separable by origin, so that no result for any system under test (SUT) can be traced to a role that should not have produced it.

Nine agent roles exist. Their names are exact and are used as-is in provenance records, prompts, and change-log entries:

ORCHESTRATOR; AUDITOR-SUT01-OMNIPIZZA; AUDITOR-SUT02-SAUCELABS; AUDITOR-SUT03-BROWSERSTACK; AUDITOR-SUT04-RESTFULBOOKER; AUDITOR-SUT05-JUICESHOP; AUDITOR-SUT06-WEBDRIVERIO; ADJUDICATOR-EU-01; QUALIFIER-MOBILE-01.

Humans are not agent roles. Humans approve freezes, decide escalations, and may direct any role; human edits remain subject to `protocol/change-control-v1.md`.

## 2. Common rules for all agents

1. Read and follow the root `AGENT-INSTRUCTIONS.md` before acting.
2. Never invent evidence. Every claim about a SUT must be backed by an evidence record whose `evidence_status` is one of DOCUMENTED, SOURCE_VERIFIED, EXECUTION_VERIFIED, or INFERRED as defined in `protocol/evidence-rules-v1.md`, and is referenced by its `evidence_id`, never by a CSV row or line number. Unknown provenance is recorded as null or "null / TBD", never guessed.
3. Never modify a SUT. Agents observe, execute, and record; they do not patch, fork-and-alter, configure beyond documented mechanisms, or contribute to any evaluated ecosystem for the purposes of this study.
4. Never change a file whose protocol state is FROZEN-PRE-DATA, AMENDED, or SUPERSEDED, and never edit anything under `prompts/frozen/` or `raw-data/` after the relevant freeze (see `protocol/change-control-v1.md`).
5. Record provenance for every artifact written: role name, prompt version id (once prompts are frozen), date, and the protocol version in force.
6. Do not start any experimental campaign, audit, qualification run, or compatibility smoke unless explicitly instructed to do so by the ORCHESTRATOR under human direction; the instruction originates with a human and is relayed by the ORCHESTRATOR (see `protocol/mobile-runner-policy-v1.md`, section 2, for the qualification gate). At initialization all campaigns are NOT STARTED and no such instruction has been given.
7. Do not write outside the assigned workspace defined in section 3 and section 4. A write outside the workspace is a boundary violation and is escalated under section 6, regardless of the content written.
8. Treat all six SUTs identically. No SUT, including OmniPizza (SUT-01), is a reference, framework, or privileged case; every rule in this document applies to every role in the same way.

## 3. Roles

### 3.1 ORCHESTRATOR

Responsibilities: maintain `manifests/`; pin the evaluated version (repository SHA, release, binary, or the strongest reproducible identifier) of every ecosystem component in `manifests/sut-manifest.yaml` and of the qualification SUT build under `qualification_build` in `manifests/toolchain-manifest.yaml` before the relevant audit, qualification, or campaign (manifests/README.md), never by writing under `qualification/`; create and version protocol documents under change control; write canonical scenario records and mapping entries under `experiments/scenario-mappings/` and campaign configuration records (`protocol/equivalent-scenario-mapping-v1.md`; `protocol/change-control-v1.md`, section 7); coordinate campaigns E01–E12; maintain provenance records; integrate audit and adjudication outputs into derived data and analysis. Qualification outputs are never integrated into `derived-data/` or `analysis/`: the runner decision from `qualification/` is recorded only in `manifests/toolchain-manifest.yaml` and `protocol/CHANGELOG.md` and disclosed as a study limitation (`protocol/mobile-runner-policy-v1.md`, section 3; qualification/README.md).

May write: `manifests/**`; `protocol/**` (in place only while a document is DRAFT; once a document is frozen, new version files only); `experiments/**`; `prompts/**`; `schemas/**`; `derived-data/**` (only via version-controlled transformations whose inputs are traceable to `raw-data/` or `audits/`); `analysis/**`; root `README.md` and `AGENT-INSTRUCTIONS.md`.

Cannot: invent evidence; modify SUTs; alter frozen protocol files in place; edit `raw-data/` after campaign freeze; write to `audits/**` or `qualification/**`; assign or adjust any capability score.

### 3.2 Auditors

| Role | Assigned SUT id | Ecosystem | Audit directory |
|---|---|---|---|
| AUDITOR-SUT01-OMNIPIZZA | SUT-01 | OmniPizza | `audits/SUT-01-omnipizza/` |
| AUDITOR-SUT02-SAUCELABS | SUT-02 | Sauce Labs Demo Ecosystem | `audits/SUT-02-saucelabs/` |
| AUDITOR-SUT03-BROWSERSTACK | SUT-03 | BrowserStack Demo Ecosystem | `audits/SUT-03-browserstack/` |
| AUDITOR-SUT04-RESTFULBOOKER | SUT-04 | Restful Booker Platform | `audits/SUT-04-restful-booker/` |
| AUDITOR-SUT05-JUICESHOP | SUT-05 | OWASP Juice Shop | `audits/SUT-05-juice-shop/` |
| AUDITOR-SUT06-WEBDRIVERIO | SUT-06 | WebdriverIO Native Demo App | `audits/SUT-06-webdriverio/` |

Responsibilities (each auditor, for its assigned SUT only): perform campaign E01-capability-audit when instructed; verify the pinned target recorded by the ORCHESTRATOR and record evidence against it; produce evidence records with the exact fields and order defined in `protocol/evidence-rules-v1.md`, each with its `evidence_id`; write execution verification records and retain artifacts under `audits/<assigned-SUT>/verifications/` and `audits/<assigned-SUT>/artifacts/` for every EXECUTION_VERIFIED record; apply `protocol/capability-rubric-v1.md` exactly as written, without local reinterpretation, including the `structural_scope_note`; record negative evidence (what could not be found, executed, or verified) and limitations with the same care as positive evidence; record open questions in the audit directory's unresolved file for escalation.

May write: only `audits/<assigned-SUT>/**` as listed in the table above.

Cannot: write `protocol/**`; write any other SUT's audit directory; write `derived-data/**`; write `analysis/**`; modify the SUT; switch independently to a version, branch, fork, or deployment other than the pinned target because it exposes a more favorable capability (a discrepancy is recorded in `unresolved.md`, never acted on); perform fault activation, active security testing, load, or state changes visible to other users against a PUBLIC_HOSTED instance (`protocol/study-design-v1.md`, section 10.2); infer capability of an ecosystem from a vendor's commercial products or services rather than from the evaluated demo artifacts themselves; write scenario mapping records; compare its SUT to another SUT (comparison is adjudication and analysis work, not audit work).

The OmniPizza auditor (AUDITOR-SUT01-OMNIPIZZA) operates under exactly the same rules, rubric, evidence requirements, and write boundary as every other auditor. It receives no additional context, no relaxed evidence standard, and no interpretive latitude that the other five auditors do not receive.

### 3.3 ADJUDICATOR-EU-01

Responsibilities: examine completed audits under `audits/**`; detect inconsistent application of `protocol/capability-rubric-v1.md` across SUTs or across modalities; identify provisional scores whose evidence records do not support them under `protocol/evidence-rules-v1.md`; review every cell an auditor flagged under the tie-break rule (`protocol/capability-rubric-v1.md`, "Tie-break rule for undecidable adjacent scores" — a cell whose `confirmed_score` is lower than its `provisional_score`), confirming that `confirmed_score` is the highest fully-supported level and that the recorded unresolved verification requirement, not plausibility or vendor reputation, is what keeps `provisional_score` unconfirmed; flag disputed cells (ecosystem × modality pairs) for human decision; produce adjudication output that records, for every examined cell, whether it is confirmed, disputed, or unsupported, with reference to the `evidence_id` of every evidence record involved (`protocol/evidence-rules-v1.md`); never by CSV row or line number.

May write: only `derived-data/adjudication/**` (directory to be created when adjudication starts; it does not exist yet).

Reads: all of `audits/**` and all of `protocol/**`.

Cannot: modify SUTs; invent missing evidence or fill gaps on an auditor's behalf; silently alter the frozen rubric or apply an unwritten variant of it; write to `audits/**`, `protocol/**`, `analysis/**`, or anywhere else in `derived-data/`; produce any aggregated, weighted, or ranked utility measure.

### 3.4 QUALIFIER-MOBILE-01

Responsibilities: execute, on explicit instruction, the qualification gate (scenarios MQ1, MQ2, MQ3 on the qualification SUT, pass criteria of `protocol/mobile-runner-policy-v1.md`, section 7) and record every measured execution, warm-up, exclusion, and attribution record; execute, on explicit instruction, the per-SUT compatibility smoke for the selected runner (`protocol/mobile-runner-policy-v1.md`, section 9); record Android and iOS compatibility findings as tool-qualification records; recommend Mobilewright or the fallback Appium 3 strictly according to that policy. Appium 2 must NOT be used and must not be recommended under any outcome.

May write: only `qualification/**`.

Cannot: turn the Mobilewright-versus-Appium comparison into a new research question of the study unless explicitly authorized by a human through a protocol version change; select or change the qualification SUT build (the ORCHESTRATOR pins it); write to `audits/**`, `experiments/**`, `raw-data/**`, `derived-data/**`, `analysis/**`, or `protocol/**`; modify SUTs; make any claim about a SUT's mobile capability (that is audit work); cite any qualification or smoke artifact as evidence about a SUT.

## 4. Write-boundary matrix

"Allowed" means the role may create and edit files in that location within the limits stated in section 3. "—" means not allowed. The AUDITOR column applies identically to each of the six auditor roles.

| Location | ORCHESTRATOR | AUDITOR-SUT0X (each) | ADJUDICATOR-EU-01 | QUALIFIER-MOBILE-01 |
|---|---|---|---|---|
| `protocol/` | Allowed (in place while DRAFT; new version files only once frozen) | — | — | — |
| `manifests/` | Allowed | — | — | — |
| `audits/SUT-0X/` (including its `verifications/` and `artifacts/` subdirectories) | — | Allowed for own assigned SUT directory only; — for all others | — | — |
| `qualification/` (including `qualification/compatibility-smoke/`) | — | — | — | Allowed |
| `experiments/` (including `experiments/scenario-mappings/` and campaign configuration records) | Allowed | — | — | — |
| `raw-data/` | Campaign execution only, under ORCHESTRATOR coordination; append-only after campaign freeze | — | — | — |
| `derived-data/` | Allowed (version-controlled transformations only) | — | `derived-data/adjudication/` only | — |
| `analysis/` | Allowed | — | — | — |
| `prompts/` | Allowed (`prompts/frozen/` is write-once per version id) | — | — | — |
| `schemas/` | Allowed | — | — | — |
| root `README.md`, `AGENT-INSTRUCTIONS.md`, `.gitignore` | Allowed | — | — | — |

`raw-data/` is never written directly by any role as an editing action. It is populated only by the execution of a campaign defined in `experiments/`, coordinated by the ORCHESTRATOR, and becomes append-only once that campaign is frozen. No role deletes or rewrites raw data.

## 5. Prompt governance

Every agent prompt used to run any campaign is frozen in `prompts/frozen/` with a version id before that campaign starts, as described in `prompts/README.md`. Prompts under development live in `prompts/working/` and may not be used for data-producing runs. A frozen prompt is never edited; a change creates a new version id. Every artifact produced by an agent under a frozen prompt records that prompt's version id in its provenance. The freeze of prompts is step 6 of the freeze procedure in `protocol/change-control-v1.md`.

## 6. Escalation

The following are never resolved by an agent on its own authority:

- Conflicts between an auditor's evidence and the rubric or evidence rules as written.
- Disputed cells flagged by ADJUDICATOR-EU-01.
- Write-boundary violations by any role, whether accidental or instructed.
- Any situation in which following one protocol document would violate another.

Each is recorded, at the time it is noticed, in the `unresolved.md` file of the workspace where it arose (the relevant audit directory, `qualification/`, or the relevant campaign directory under `experiments/`), always by the noticing role in its own workspace, never elsewhere. When the escalation concerns a protocol document or a frozen file, the ORCHESTRATOR (the only role that may write under `protocol/`, section 4) mirrors it into `protocol/unresolved.md` (created on first use; same table format as the audit `unresolved.md` files; row ids `PROTO-U01`, `PROTO-U02`, ...; `raised_by` names the role that noticed it). `protocol/unresolved.md` carries no protocol state and is exempt from the lifecycle (`protocol/change-control-v1.md`, section 1). `protocol/CHANGELOG.md` records only approved decisions (`protocol/change-control-v1.md`, section 5) and never holds an open escalation. The record states what happened, which files and roles are involved, and what the agent did not do as a result. Humans decide the outcome; the decision and its date are appended to the same record.

## 7. Versioning

This is `protocol/agent-governance-v1.md`, version v1, state FROZEN-PRE-DATA (frozen 2026-09-16, approved by gilbertosanchez, protocol/change-control-v1.md, section 6). Roles, responsibilities, and write boundaries may change only through a new version of this document under `protocol/change-control-v1.md`; the frozen file is never edited in place except for the header state field and successor pointer.
