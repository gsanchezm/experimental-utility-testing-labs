# axe-core pin proposal

**DRAFT proposal, not a pin.** The ORCHESTRATOR records a pin in manifests/toolchain-manifest.yaml only after explicit human approval. Nothing here installs, freezes, or authorizes a run.

## 1. Pinning policy that applies

- manifests/toolchain-manifest.yaml, `policy`: no tool is installed at initialization; every version field is null and must be recorded (exact version, install date, platform) before the first run that uses the tool.
- Current entry, `tools.accessibility`: candidate axe-core; version, install_date, platform, notes all null.
- Mobile candidates in the same file record a pinned candidate with `package`, `version`, `npm_integrity`, `source_commit`, `engines`, `pinned_by`, and `pinned_at`. This proposal mirrors that structure.
- Playwright (already pinned): `tools.web_runner` in the same file gives Playwright 1.63.0 for Python, pinned in experiments/E03-resetability/executor/requirements.txt by exact version and sha256 hashes. The Chromium build is named by that Playwright version, is not hash-pinned by the study, and its observed version is recorded per run.

## 2. Proposed pin

| Field | Proposed value | Source |
|---|---|---|
| package | axe-core | registry metadata |
| version | **4.14.0** (HUMAN DECISION HD-16) | `https://registry.npmjs.org/axe-core/latest` |
| npm_integrity (sha512) | `sha512-9WTZxEjsZ7b13TH8JPmbV2z8CHbl80/2hm3XPEG4JgNdQLK81IBRXmSxHfMAOkSqQeRxT/0dwNDz2GOm3zzpcQ==` | `dist.integrity` in the packument, `https://registry.npmjs.org/axe-core` |
| shasum (sha1, registry) | a9819d3932a8198fbe935d8cbd8afcdfecbcf31d | `dist.shasum` (registry) |
| tarball URL | https://registry.npmjs.org/axe-core/-/axe-core-4.14.0.tgz | `dist.tarball` (registry) |
| published (registry `time`) | 2026-10-05T17:43:36.099Z | packument `time` |
| deprecated | none | packument |
| dist-tag at retrieval | `latest` = 4.14.0 | packument `dist-tags` |
| license | MPL-2.0 | package.json inside the tarball |
| engines | node >=4 | package.json inside the tarball |
| repository | https://github.com/dequelabs/axe-core.git | package.json inside the tarball |
| source_commit | **not stated** (the registry record has no `gitHead` for 4.14.0; left null, not guessed) | packument |
| browser build file (candidate) | `package/axe.min.js`, 652140 bytes, sha256 `20c09fe157a8a34a30e241aaa1fcdade657734f08ab379ecfbeb7d45cc46e878` | tarball, computed 2026-11-06 |
| unminified build (reference) | `package/axe.js`, 1477661 bytes, sha256 `aae0b8b36278089962105b2351ea64f4da7d3d440b54e162e21616d597aa0d6f` | tarball |
| pinned_by / pinned_at | null (proposal only) | — |

**Retrieval.** Registry metadata for `latest`: 2026-11-06T01:25:42Z (UTC), which is 2026-11-05 local time (UTC-6). Full packument (release history, integrity values): https://registry.npmjs.org/axe-core, same retrieval window. Tarball: https://registry.npmjs.org/axe-core/-/axe-core-4.14.0.tgz, retrieved 2026-11-06T01:31:09Z (UTC).

**Integrity verification performed.** The downloaded tarball (706680 bytes) gives sha512 and sha1 values equal to the registry's `dist.integrity` and `dist.shasum`. The archive has 31 members under `package/`. Nothing from the package was executed; files were read as text only.

## 3. Release context (registry `time` and `dist`)

| Version | Published (UTC) | Note |
|---|---|---|
| 4.12.0 | 2026-06-01T17:21:03.669Z | earlier |
| 4.12.1 | 2026-06-10T10:27:03.257Z | earlier |
| 4.13.0 | 2026-08-05T16:53:07.262Z | alternative (HD-16); sha512 `UzGt8zg7Ny8djbYMhxl2zuEevVa7r2gJjYY5Lwr1xM7+XU2nd6CkIWFTVcCIbAP63vSz71NaVyyuSk9lHKcy0A==` |
| 4.14.0 | 2026-10-05T17:43:36.099Z | proposed |

Recommendation: 4.14.0, the latest stable release at retrieval. It is about a month old at retrieval. The protocol states no minimum-age rule for tool pins (manifests/toolchain-manifest.yaml states none), so the age question is a human choice. Re-check the `latest` tag on the pin date; a published version's integrity values do not change.

## 4. Rule behavior in the pinned source (static reading, not executed)

Line numbers refer to `package/axe.js` in the verified tarball.

| Rule or function | Line | What the source says |
|---|---|---|
| `image-alt` (rule) | 37401 | impact critical; tags include `cat.text-alternatives`, `wcag2a`, `wcag111`; `any`: `has-alt`, `aria-label`, `aria-labelledby`, `non-empty-title`, `presentational-role`; `none`: `alt-space-value` |
| `has-alt` evaluate | 28501 | returns `virtualNode.hasAttr('alt')` for `img`, `input`, `area` (presence of the attribute, not its value) |
| `alt-space-value` evaluate | 31013 | true only when `alt` matches `/^\s+$/` (whitespace only; an empty string does not match) |
| `empty-heading` (rule) | 37234 | impact minor; selector `h1, h2, h3, h4, h5, h6, [role="heading"]`; matches `heading-matches`; `any`: `has-visible-text`, `aria-label`, `aria-labelledby`, `non-empty-title`; tags `cat.name-role-value`, `best-practice`; no `enabled: false` in its block |
| `heading-matches` | 33011 | `get_role` equals `heading` |
| `has-visible-text` check (refers to `has-text-content-evaluate`) | 38539 (reference) | subtree text, sanitized, not empty |
| result types | 34920 | `passes`, `violations`, `incomplete`, `inapplicable` |

**Consequences for E09.**

1. For `<img alt="">` (what the `missing_name` mode produces for the product image), `image-alt` passes: `has-alt` is true because the attribute exists, and `alt-space-value` does not flag an empty string. The E01 expectation (SUT01-EV-0019, which names `image-alt`) is **not supported** by this pinned source.
2. For an empty `h2` (the same mode), `empty-heading` fails unless the heading has `aria-label`, `aria-labelledby`, or a non-empty `title`. Whether the pinned OmniPizza frontend adds any of these is **not verified** here.
3. `empty-heading` is tagged best-practice, not WCAG. A run restricted to WCAG tags would never execute it. The scan configuration must include it explicitly or include best-practice tags (HUMAN DECISION HD-4).
4. The predeclared expected rule set for the `missing_name` condition therefore reads `empty-heading` only (HUMAN DECISION HD-3). Confirm by probe before lock.

## 5. Loading route into the Python executor (HUMAN DECISION HD-12)

**Route T (recommended).** Python only; no Node in the measured job.
1. The measured job downloads the tarball URL in section 2 and verifies its sha512 against `npm_integrity`. Fail closed on mismatch.
2. Extract `package/axe.min.js` (or the reference `axe.js`; the configuration names the file and its sha256).
3. Inject with Playwright for Python 1.63.0 by adding a script tag from the file (for example the page method `add_script_tag` with a path argument), then call `axe.run` from `page.evaluate` with the predeclared options. The exact method names and option handling are to be verified against Playwright 1.63.0 in the first probe; not verified here.
4. Record `toolchain.accessibility` = axe-core 4.14.0 and the file sha256 in each run manifest and its artifacts.

**Route N (alternative).** `npm ci` from a lock file kept under the campaign's executor directory, with an exact version (no caret). Requires Node.js in the measured job. The lock carries the same integrity value. The study already uses a lock-file `npm ci` pattern for its mobile compatibility harness (manifests/toolchain-manifest.yaml, `tools.mobile_fallback.install_method`), so the route is consistent with existing practice.

**Not evaluated.** Python packages that bundle axe-core were not fetched or evaluated. They would need their own pin and a verified bundled version.

## 6. What this proposal does not establish

- Browser behavior of `axe.run` against the OmniPizza catalog (visibility, computed roles, scope). Only static source reading was done.
- Whether the affected `h2` carries an ARIA name or title (pinned frontend source; not read here).
- Compatibility of axe-core 4.14.0 with Playwright 1.63.0 in a browser. Expected to be independent (axe-core is injected as a script), but not tested.
- Whether a default run includes best-practice rules (the rule carries no `enabled: false`; the default rule configuration is to be confirmed in the probe).

## 7. Hygiene

Sources are the registry URLs and retrieval stamps above. No local path, assistant or vendor name, or session identifier is recorded here. The downloaded files are kept in a scratch folder outside the repository and are not part of any repository change.
