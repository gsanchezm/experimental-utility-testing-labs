# E12 Localization / i18n: design brief

**DRAFT.** Nothing in this file freezes, starts, authorizes, or dispatches anything. Every unknown is a HUMAN DECISION (section 7) or an open verification item (section 8). Minimal scope in the style of E09.

| Field | Value |
|---|---|
| Campaign | E12-localization-i18n (experiments/E12-localization-i18n/README.md; status NOT_STARTED) |
| Modality | Localization / i18n (protocol/study-design-v1.md, section 7) |
| Research question | RQ1 (primary: controllability of the selected locale conditions) and RQ4 (secondary: cross-surface locale consistency); no hypothesis is attached (protocol/study-design-v1.md, section 9), so every comparison is EXPLORATORY |
| Date | 2026-11-23 (local) |
| Basis | E01 adjudicated matrix and the evidence of its Localization / i18n cells |

## 1. Summary

- Localization / i18n is effective Score 3 for SUT-01, SUT-02 and SUT-05, SUT-03 is Score 1, SUT-04 is Score 0 (structural scope note: a single hardcoded date-format locale, SUT04-EV-0025 and -0026) and SUT-06 is Score 0. No hypothesis covers E12 (protocol/statistical-analysis-plan-v1.md, section 4.3 maps H1 to H5 to other campaigns), so every E12 comparison is EXPLORATORY. SUT-02 has no locale variants in its Android build and no i18n library in its web source (SUT02-EV-0021); only its iOS build ships English and German strings (SUT02-EV-0020), so its Score 3 rests on a mobile cell, which needs an admissible runner and a compatibility smoke of the exact cell (protocol/mobile-runner-policy-v3.md). Recommended minimal scope: SUT-01 web and api, no mobile cell. Because SUT-02 and SUT-05 are Score 3 as well, their cells are recorded as "not executed, scope and time" with that reason (rule 10: a modality that does not apply is recorded as such, never skipped silently); they are never reported as "no ground-truth condition available".
- E12 observations and the E01 level are two evidence layers, reported in separate tables, never summed or counted twice in any count of modalities per level (protocol/statistical-analysis-plan-v1.md, section 5).
- SUT-01 fixes per market its currency, required fields, tax rate, tip field and default language (SUT01-EV-0026, SUT01-EV-0027): five markets (MX, US, CH, JP, SA), a market chosen at login, the language derived from it unless an explicit header overrides it, every catalogue item stored in six languages. The expected locale-specific outcomes are therefore readable from the pinned source before any execution, which is the ground truth rule (protocol/study-design-v1.md, section 8).

## 2. What the evidence establishes

| Evidence | SUT | Mechanism | Status | Use in E12 |
|---|---|---|---|---|
| SUT01-EV-0026 | SUT-01 | README: five markets with their currency, required fields, tax, tip field, language behaviour | DOCUMENTED | candidate identification |
| SUT01-EV-0027 | SUT-01 | per-market configuration; language resolved from the market unless `X-Language` overrides; items translated per request | SOURCE_VERIFIED | the expected outcomes |
| SUT01-EV-0028 | SUT-01 | mobile market selector and deep-link parameters | SOURCE_VERIFIED | mobile parity, excluded from the minimal scope |
| SUT05-EV-0013 to -0015 | SUT-05 | 45 shipped locale files, an explicit runtime switch, a per-locale completeness endpoint | DOCUMENTED / SOURCE_VERIFIED | candidate for a later addition |
| SUT02-EV-0020, -0021 | SUT-02 | iOS English and German strings; no locale variants on Android | SOURCE_VERIFIED | candidate only if a mobile path is opened |

Pin: SUT-01 commit 9ca37674d374e9303912e259641ee86baf3aabe1. Its web and api surfaces were verified as controlled instances on GitHub Actions for conditions of E03; the study-level flag `controlled_instance_available` is null for SUT-01 (its mobile surfaces were not provisioned), so the per-condition decision goes in the campaign configuration and is confirmed by this campaign's DRY_RUN rounds.

## 3. Proposed conditions (candidate, not frozen)

Ten cells: five markets times two surfaces (web, api). A cell is one market on one surface.

| Surface | Action | Expected outcome, read from the pinned source before execution |
|---|---|---|
| api | GET /api/pizzas with the market header and no language header | prices in the market currency with the market's decimals, names and descriptions in the market's default language |
| api | the same request with an explicit language header | text in that language, currency unchanged (CH with French as the case in SUT01-EV-0027) |
| web | log in choosing the market, open the catalogue | the same currency and language, the market's required checkout fields, and a right-to-left layout for SA |

The exact expected strings, decimals and fields per market are fixed in a table before the first run from COUNTRY_CONFIG and the translation dictionary at the pinned commit; a cell where a surface cannot show an outcome is recorded as not applicable with its reason.

## 4. Measurement (candidate)

- Outcome per execution and cell: expected locale-specific outcome observed / not observed / not applicable, compared with the pre-registered table. Locale selection controllability per ecosystem: explicit selectable (SUT01-EV-0027, -0028).
- Cross-surface consistency (RQ4, web against api): per market, whether the observed currency and language agree between surfaces.
- N = 50 executions per cell (protocol/repeatability-determinism-v1.md, section 3, standard target; no mobile cell), 500 executions in all. API cells are cheap; web cells need a browser session each.
- Reporting: proportion observed per cell with a Wilson 95% interval, descriptive, an E12 table under RQ1 and RQ4, never mixed with the E01 level; no ranking, no composite, no hypothesis label.

## 5. Environment and safety

- A locale choice is not a fault activation and does not change state seen by others, but the study runs SUT-01 as a controlled instance (LOCAL or SELF_HOSTED on a GitHub Actions runner), the same as the other campaigns, and records the instance in every run manifest. No PUBLIC_HOSTED instance is used.

## 6. Execution model

- GitHub Actions under CAMPAIGN-CI-WRITE-AUTH-01: dispatch-only environment-verification and measured-execution workflows, a frozen executor with its implementation hash, a frozen dispatch prompt, one dispatch authorization for SUT-01 (agent-governance-v6, Section 3.7), first attempt only; non-measured DRY_RUN rounds before the START, never entering raw-data/.

## 7. HUMAN DECISIONS (recommended defaults; each can be vetoed by its id)

| Id | Decision | Recommended default |
|---|---|---|
| E12-D-1 | Which ecosystems carry measured cells | SUT-01 web and api only, with the consequence stated in section 1 for SUT-02 and SUT-05; SUT-05 web (a few locales) is the candidate to add if time remains; no mobile cell |
| E12-D-2 | Markets | all five, MX, US, CH, JP, SA |
| E12-D-3 | Expected-outcome table | built from COUNTRY_CONFIG and the translation dictionary at the pinned commit, frozen before the first run |
| E12-D-4 | Language override case | CH with French (SUT01-EV-0027) as the only override case |
| E12-D-5 | N | 50 executions per cell |
| E12-D-6 | Cross-surface consistency | web against api per market, reported under RQ4 |
| E12-D-7 | Relation to E01 | reported in its own E12 table; the E01 level stays untouched |

## 8. Open verification items

- V-1 Where each expected outcome is observable on the web surface (the rendered currency, the translated name, the required fields, the direction of the layout), and which are observable only on the api.
- V-2 That the market cannot be changed after login (SUT01-EV-0026), so each execution logs in again, and that a language toggle exists where the README says (CH).
- V-3 Whether a web cell and its api cell can share one session or need two.
- V-4 That no scenario mapping record is needed (each ecosystem is compared with its own pre-registered expectations, not a canonical scenario); a decision may say otherwise.
- V-5 For a later SUT-05 addition: the locale list to choose and the Angular language switch as the action.
