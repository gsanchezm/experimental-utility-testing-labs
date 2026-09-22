# SUT-06 — WebdriverIO Native Demo App — Limitations

| Field | Value |
|---|---|
| SUT id | SUT-06 |
| Auditor role | AUDITOR-SUT06-WEBDRIVERIO |
| Audit status | SUBMITTED |

## Purpose

Records, neutrally and descriptively, what bounds the audit of the system under test (SUT) SUT-06: what the ecosystem intentionally does not cover, what the auditor could not verify and why, environment constraints, and environment considerations. Entries are cross-referenced from audit.md (structural_scope_note column and section 6) and from evidence.csv notes. Nothing here is a score, a finding, or a ranking input.

Intentionally narrow scope is not a penalty. An ecosystem that deliberately does not cover a modality is described here in neutral terms; the corresponding row in audit.md section 3 carries a structural_scope_note, the score remains the rubric score (Score 0 for a structurally absent surface; no N/A level), and the capability rubric (protocol/capability-rubric-v1.md) is applied unchanged. Experimental Breadth and Modality Depth answer different questions (protocol/study-design-v1.md, section 11).

## Scope limitations of the ecosystem (intentional)

SUT-06 is documented (README.md) as a mobile-only demo app "for iOS and Android," built specifically to exercise WebdriverIO/Appium mobile automation together with the companion `appium-boilerplate` project. It has no Web and no API surface (audit.md section 2; evidence.csv SUT06-EV-0001–0004). This is the ecosystem's own documented scope, not a defect: it is treated as a mobile specialist baseline (manifests/sut-manifest.yaml, `role`) and scored the same rubric as every other SUT (protocol/capability-rubric-v1.md, "Equal treatment"). The iOS build is distributed for the iOS Simulator only — README.md states explicitly there is no build for a physical iOS device, "a (security) limitation from Apple." This does not reduce the iOS Native score; environment is provenance, not utility (protocol/study-design-v1.md, section 10).

## Evaluation limitations (what the auditor could not verify and why)

- **No execution verification was performed.** All findings in this audit are DOCUMENTED or SOURCE_VERIFIED. This SUT is fully open source at the pinned commit, so SOURCE_VERIFIED was fully obtainable for every candidate mechanism examined, including the Score 3 determination for Android Native and iOS Native (Data Management screen, SUT06-EV-0007/SUT06-EV-0015); no evidence ceiling (protocol/evidence-rules-v1.md, "Evidence ceiling") applies to this SUT. Standing up an Android emulator or iOS Simulator and actually running the built app was judged unnecessary to answer any specific unresolved claim (prompt "Evidence collection order," step 4: execution only when needed), so `environment_types_used` in audit.md section 1 is empty. This is a scope choice by this auditor, not a capability ceiling of the SUT; a future EXECUTION_VERIFIED pass remains possible and would strengthen, not change, the Score 3 determinations already reached.
- **Deep-link routing behavior was not executed.** The native URL scheme `wdio://` is registered at both the Android intent-filter and iOS `CFBundleURLTypes` level, and Expo Router's file-based routes exist for every tab screen (SUT06-EV-0009, SUT06-EV-0017), but whether opening a `wdio://<route>` URL actually navigates to that screen was not observed by execution in this audit — it rests on Expo Router's documented (external) linking behavior applied to this app's own source-confirmed scheme/route registration. This evidence supports Score 2 material only and was not used to raise any cell to Score 3 on its own (the Score 3 determination rests on the Data Management mechanism instead, which required no such external-framework-behavior assumption).
- **`controlled_instance_available` (audit.md section 1) is left null**, per protocol/study-design-v1.md section 10.5 ("it is null until verified and is never inferred"). Verifying it would require actually running the pinned Android build in an emulator and the pinned iOS build in a Simulator, which was not done (see above).
- **`src/App.tsx` is dead code.** It defines a legacy React-Navigation-based `linking` config for `wdio://` that partially overlaps with, but is not identical to, the active Expo Router routes. It is imported by neither `index.js` (`expo-router/entry`) nor anything under `app/`. This was confirmed by an explicit import-graph check (`grep` for references to it across `index.js`, `app/`, `src/`) and is recorded so a later audit or adjudication pass does not mistake it for the app's active behavior (see unresolved.md, SUT-06-U02).
- **Screens not individually source-cited beyond the README inventory:** Forms (dropdown/switch/input beyond what FormComponents.tsx shows), Swipe (carousel), and Drag (puzzle) were read at the file level (FormComponents.tsx in full; Drag.tsx and Swipe.tsx partially, for the Functional Complexity inventory) but were not each given a dedicated per-mechanism evidence row, since they did not change any modality's provisional_score beyond what SUT06-EV-0005/0013 (README inventory) and the already-established Score 3 mechanism already support. Their presence is documented (SUT06-EV-0005, SUT06-EV-0013) and their existence in source was visually confirmed during directory listing, but a claim about their specific internal behavior beyond what is stated in audit.md section 4 is not separately evidenced and should not be inferred beyond what is written there.

No evidence-ceiling limitation applies to this SUT (it is fully open source; SOURCE_VERIFIED was obtainable and used throughout).

## Environment limitations

No emulator, simulator, or physical device was used in this audit. All evaluation was performed by reading official documentation and the source tree of a local, read-only, out-of-repository clone of `https://github.com/webdriverio/native-demo-app`, checked out at the pinned identifier and left unmodified (`git status` clean throughout; verified immediately before and after the audit). No network access to a running instance of SUT-06 was needed or used, since SUT-06 has no hosted endpoint (it ships only as downloadable Android/iOS binaries).

## Environment considerations

`environment_types_used`: none (see "Evaluation limitations," above — no EXECUTION_VERIFIED evidence was produced). No PUBLIC_HOSTED instance of SUT-06 exists to begin with (manifests/sut-manifest.yaml records `endpoint: null` for both android and ios). `controlled_instance_available`: null, not inferred (see above). Environment is provenance, not utility (protocol/study-design-v1.md, section 10): none of the above raises or lowers any score in audit.md section 3.
