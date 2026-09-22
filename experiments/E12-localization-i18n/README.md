# E12 — Localization / i18n

## Objective

Determine whether each evaluated ecosystem (each a system under test, SUT) exposes explicit market or locale selection as a controllable experimental condition, and whether locale-dependent observable outcomes follow from that selection. Where more than one surface is present, the campaign also records whether locale selection and its observable effects are consistent across surfaces. E12 evaluates selected localization / i18n conditions experimentally; the Localization / i18n capability level (0, 1, 2, or 3) is assigned by E01 under protocol/capability-rubric-v1.md. The two are different evidence layers: the E01 level and the E12 observations are reported separately and are never summed or counted twice in any aggregate or in any count of modalities per level (protocol/study-design-v1.md, section 9). No research question is dedicated to localization, and no global aggregate Experimental Utility Score exists.

## Related research question(s)

- RQ1 Experimental Breadth (primary: controllability of the selected locale conditions).
- RQ4 Cross-platform and Cross-layer Integration (secondary: cross-platform locale parity).
- Informs dimensions 1 Experimental Breadth and 4 Cross-platform and Cross-layer Integration.

## Future independent variables (candidate — not frozen)

- Ecosystem (SUT-01 through SUT-06) — candidate.
- Locale / market (set TBD before freeze, drawn from what each ecosystem exposes as recorded in E01) — candidate.
- Surface (web / api / android / ios) — candidate.

## Future dependent variables (candidate — not frozen)

- Locale selection controllability (categorical: explicit selectable / implicit only / not available; criteria TBD before freeze) — candidate.
- Expected locale-specific outcome observed (categorical: observed / not observed / not applicable) — candidate.
- Cross-platform locale parity (categorical, for ecosystems with more than one surface) — candidate.

## Required evidence

- Locale activation record showing how the locale or market was selected, with provenance of the mechanism.
- Expected locale-specific outcome defined before execution for each locale × surface cell.
- Screenshots (UI surfaces) and response records (API surface) capturing the observed outcome.
- One run manifest per locale × surface execution conforming to schemas/run-manifest.schema.json, carrying `environment_type`.
- Explicit record for every locale × surface cell that is not applicable or not testable, with reason.
- Mobile executions comply with protocol/mobile-runner-policy-v1.md, including the per-SUT compatibility smoke.
- Raw observations in `raw-data/E12-localization-i18n/`.

## Current status

NOT STARTED

## Warning

Protocol must be finalized (FROZEN-PRE-DATA) before execution. Do not execute without explicit instruction.
