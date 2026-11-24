# OWASP ZAP pin proposal

**DRAFT proposal, not a pin.** The ORCHESTRATOR records a pin in manifests/toolchain-manifest.yaml only after explicit human approval. Nothing here installs a tool, starts a container, freezes, authorizes, or dispatches anything. Every fact below was read from a registry, an API, or source text; nothing was executed.

## 1. Pinning policy that applies

- manifests/toolchain-manifest.yaml, `policy`: no tool is installed at initialization; every version field is null and must be recorded (exact version, install date, platform) before the first run that uses the tool.
- Current entry, `tools.security`: candidate "OWASP ZAP"; version, install_date, platform, notes all null (unchanged by this proposal).
- Precedent: experiments/E09-accessibility/axe-core-pin-proposal-draft.md (version, integrity values, retrieval stamps, static reading of the rules the condition depends on, loading routes as a human decision).
- Ground truth rule (protocol/study-design-v1.md, section 8): the known condition and its expected outcome are fixed before the instrument runs. This proposal therefore fixes the condition → rule → URL mapping (section 6) from the rule's class and source, and the DRY_RUN may confirm or contradict it but never chooses it.

## 2. Retrieval

All retrieval is read-only (HTTP GET/HEAD of metadata and text sources; anonymous registry tokens). Window: 2026-11-24T01:33Z to 2026-11-24T01:47Z (UTC), which is 2026-11-23 19:33 to 19:47 local time (UTC-6).

Sources: GitHub REST API for the repositories zaproxy/zaproxy, zaproxy/zap-extensions and zaproxy/zap-admin; the container registry `ghcr.io` (repository zaproxy/zaproxy) and Docker Hub (repository zaproxy/zap-stable), manifests and image configuration only (no layer was downloaded); raw source files at the commits and tags named below; the npm registry and package files for `serve-index`.

## 3. Release

| Field | Value | Source |
|---|---|---|
| latest stable release | **v2.17.0**, published 2025-12-15T14:41:51Z, not a pre-release | GitHub releases, `releases/latest` |
| earlier stable releases (in the last 100 releases) | v2.16.1 (2025-03-25), v2.16.0 (2025-01-10) | GitHub releases |
| pre-releases | weekly builds `w2026-11-19` and earlier; not proposed (pre-release) | GitHub releases |
| tag object | `04c5d8be093eb050f4f4444883b950efd9afd0f7` (annotated, tagger date 2025-12-15T13:03:36Z) | git tag ref |
| source commit of the tag | **`8a1bff313f4d183dba5aa154ecbe89ad751c9153`** | git tag object |
| Linux archive | `ZAP_2.17.0_Linux.tar.gz`, 243895361 bytes, sha256 `efe799aaa3627db683b43f00c9c210aea0b75c00cc8f0a0f0434d12bb3ddde5a` | release asset digest as listed by GitHub (not recomputed here: the archive was not downloaded) |
| Core archive | `ZAP_2.17.0_Core.zip`, sha256 `0cb73b7f72d12c263fb61de304edb82a455d7aa4e1813c216c061765c306f5b7` | release asset digest |
| SBOM | `bom.json`, CycloneDX 1.6, 95 components, sha256 `c91137d66c34a7e2803cbd4fbaf41f2e16201f754b9fc7c954293939a32371bf` (recomputed on the downloaded file; equals the listed digest) | release asset |
| license | Apache-2.0 | image annotation (section 4) |

The SBOM lists the core's own dependencies; it names no scan-rule add-on. The release alone does therefore not state which rules a run uses (section 5).

## 4. Container image

| Field | Value | Source |
|---|---|---|
| reference | `ghcr.io/zaproxy/zaproxy:2.17.0` (the tag `stable` resolves to the same digest at retrieval) | registry HEAD |
| index digest | **`sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af`** (OCI image index, 2 manifests) | registry |
| amd64 manifest | **`sha256:c2d63bbb2d907a5c5257914fb20e26e969c92b25f265def7f89f08203f912882`** (20 layers, 1202475445 bytes compressed in all) | registry |
| arm64 manifest | `sha256:0b8847b2c722b16f0964431aabcbb499560a1f17e8698d52326d82db29efac1d` | registry |
| image created (amd64 config) | 2026-11-03T12:25:54Z; user `zap`; Java 17 | image configuration |
| build source | the Dockerfile `docker/Dockerfile-stable` at zaproxy/zaproxy commit `528bdf4c8c808342cb1f12314a2492c8d3e0b551` (named by an image label; commit date 2026-11-02) | image configuration, source file |
| same digest on Docker Hub | `zaproxy/zap-stable:2.17.0`, last updated 2026-11-03T12:34:20Z; the date tag `20261103` and `latest` carry the same digest | Docker Hub tag API |

**Finding: the version tag is mutable.** The tag `2.17.0` points to the image of 2026-11-03, but the date tag of the release day, `20251215-stable`, resolves to a different index (amd64 manifest `sha256:ed838010114ba7671f7ddb6d75d6a9ce9bcdb7bc8f2f994df2b075e631b8ced1`), and Docker Hub shows further date tags (`20261008`, `20261016`, `20261026`, `20261103`) pushed on a rolling basis. The same version number is rebuilt from time to time. A tag is not a pin; only the digest is.

**Why the rebuilds matter.** The Dockerfile at the build commit downloads the stable release and then runs `./zap.sh -cmd -silent -addonupdate` and copies the updated add-ons into the installation. The scan rules of an image are therefore the marketplace state at its build time, not the state of the release.

## 5. Scan rules: what is bundled and what it depends on

| Artifact | ascanrules | pscanrules | commonlib | Basis |
|---|---|---|---|---|
| image at digest 9624669d… (derived, **not observed**) | 84 (2026-10-08) | 77 (2026-10-22) | 1.44.0 | the add-on registry file `ZapVersions-2.17.xml` of zap-admin at commit `cb4ad4616fef0153ff8f4eaa74f69804f9aec015` (2026-11-03T11:19:34Z, the last commit of that file before the build at 12:25Z); the file's sha256 is `7890fc53a5277c6c6500bb12fbe952b314f83cd64eec6f3db1acaa8f3489e785` |
| registry at retrieval (reference only) | 84 | 79 (2026-11-18) | n/a | the same file at zap-admin commit `bb5e306bfa8d77a5a6cbcdb6d9102a251ddd5553` (2026-11-24T00:11:29Z) |
| release tarball of 2025-12-15 | not read | not read | not read | the tarball was not downloaded (about 244 MB); its add-on set was not read |

The registry file is the marketplace, not a bundle manifest; the derived row says what the build step would have fetched, and the add-on files that the image really holds are read in the DRY_RUN (the installed add-ons list of the running pinned image) and recorded in the run manifest. Add-on files named by the registry: ascanrules-release-84.zap, sha256 `f3c0f8a9c1bcac5a8b43b63d219a698fc5656f96cf4ad4197f8b088d089d2d84`; pscanrules-release-77.zap, sha256 `d10b7efa8dd11c94d695cf61fc8658ba71c15d2c660d27e12063d53bd5f81352`.

Tags in zap-extensions used for the source reading: `ascanrules-v84` (tag object `f3c5d1ac2212dd8c7c4fc273a917b38fd58ee5d3`) and `pscanrules-v77` (read from the tag name; its tag object was not queried; `pscanrules-v79` is `e76ff50d4a0367c6cab98e628d462e138dcff989`, shown for the retrieval state only).

**How updates are suppressed (read in the core at tag v2.17.0).** `OptionsParamCheckForUpdates` defines `start.checkForUpdates` (default true), `start.checkAddonUpdates` (default true) and `start.installAddonUpdates` (default **false**); the command-line option `-addonupdate` exists, and the method `updateAddOnsInline` of the same extension builds temporary options with check and install both true (read; the call chain from the option to that method was not traced). The paths that install an update unattended were not enumerated beyond those. The expectation is that a run which sets `-config start.checkForUpdates=false` and never passes `-addonupdate` neither checks nor installs; this is an expectation from the option names, not a verified guarantee. Setting the option keys on the command line is the executor's job and is checked in the DRY_RUN (the installed add-ons list before and after the run must be equal); it is not tested here. The key `start.installScannerRules` also exists and its default was not read.

## 6. Rules the three SUT-05 conditions rest on (static reading, not executed)

Read at `ascanrules-v84` (identical to the derived add-on set of the image) and `pscanrules-v77`.

| Class | Rule | Id | Source file | What the source says |
|---|---|---|---|---|
| SQL injection | SQL Injection (generic) | **40018** | `SqlInjectionScanRule.java` (`getId` returns 40018) | strength-dependent attack lists; an RDBMS table that includes SQLite (error marker `SQLITE_ERROR`); the add-on's directory at this tag (55 source files, helpers included) has no SQLite-named rule file (the siblings are timing rules for Hypersonic, MsSQL, MySQL, Oracle and PostgreSQL) |
| directory browsing (active) | Directory Browsing | **0** (`return 00000`) | `DirectoryBrowsingScanRule.java` | requests the URL with its query removed and a trailing slash added; needs HTTP 200; matches (a) `Parent Directory` (IIS technology in scope), (b) `Directory Listing` … `Tomcat` or `Apache` (those technologies in scope), (c) `Parent directory` (low confidence), (d) `\bDirectory\b` together with `[\s<]+IMG\s*=` (low confidence) |
| directory browsing (passive) | Directory Browsing | 10033 | `pscanrules/…/DirectoryBrowsingScanRule.java` | matches `<title>Index of /…</title>` (Apache style) and `[To Parent Directory]` (IIS style) |
| external redirect | External Redirect | 20019 | `ExternalRedirectScanRule.java` | not used by the minimal set |
| access control (IDOR) | none | none | the 55 source files of the add-on at this tag | no file name suggests object-level authorization (names only; the file contents and other add-ons were not searched) |

**Proposed expectation per condition (fixed from class and source; HUMAN DECISION E11-D-9).**

| Condition | Expected rule | Expected target URL | Notes |
|---|---|---|---|
| E11-SUT05-SQLI-LOGIN | 40018 | `POST /rest/user/login` on the controlled instance | the body is JSON |
| E11-SUT05-SQLI-SEARCH | 40018 | `GET /rest/products/search?q=` | query parameter |
| E11-SUT05-DIRLIST-FTP | 0 | `/ftp/` (the rule adds the trailing slash) | see the reading below |
| E11-SUT01-IDOR-ORDER | none in the add-on set (M2 not applicable) | n/a | recorded as "no rule of the pinned set targets this class", never as a detection failure; M1 carries the condition |

**Reading for E11-SUT05-DIRLIST-FTP (the analogue of the `image-alt` finding of E09).** The route of SUT-05 at the pinned commit is `app.use('/ftp', serveIndexMiddleware, serveIndex('ftp', { icons: true }))` (`server.ts`, line 288); the `serveIndexMiddleware` rewrites the `href` values of the page. `serve-index` is declared `^1.9.1`; no lock file is committed at the pinned commit, so the resolved version is the one the packaged v20.2.0 distribution ships, not read here; the two candidates in range, 1.9.1 (2017-09-29) and 1.9.2 (2026-01-22), have byte-identical `directory.html` and `style.css` (the `index.js` files differ). None of `directory.html`, `style.css` and `index.js` of either version contains the text `Parent directory` (checked case-insensitively) or the string `<img =` (the check is a text search of the package files, not of a rendered page), and the page title reads `listing directory {directory}`, not `Index of /`. By this reading the active rule 0 and the passive rule 10033 would **not** match the page that the instance serves (the page also lists the file names of the `ftp` folder; their text was not read). This is a prediction from source, not an observation: **not established** until the DRY_RUN. If it holds, E11-SUT05-DIRLIST-FTP records "not detected" for M2 in every execution, which is a valid outcome under the ground truth rule and is not a reason to change the expected rule; the human decision is whether to keep the condition (recommended: keep, as the honest result of the instrument) or to drop it before the START.

## 7. Pin routes (HUMAN DECISION E11-D-8)

**Route A (recommended): the container image by digest.**
1. The measured job pulls `ghcr.io/zaproxy/zaproxy@sha256:c2d63bbb2d907a5c5257914fb20e26e969c92b25f265def7f89f08203f912882` (amd64) by digest and fails closed if the digest it resolved differs. The index digest `9624669d…` is recorded beside it.
2. The run manifest records the release v2.17.0, the digest, the image creation time, and the installed add-on list read from the running instance (not the derived set of section 5).
3. The record says that the tag moved (section 4) so that nobody re-resolves the tag later.
4. Cost: about 1.2 GB compressed per pull; to be measured in the DRY_RUN. GHCR still served the older date-tagged image on retrieval, so superseded digests were not removed, but retention is not guaranteed.

**Route B (alternative): the release archive plus hash-pinned add-ons.**
1. The job downloads `ZAP_2.17.0_Linux.tar.gz` and checks sha256 `efe799aa…`.
2. It installs the add-on files named in section 5 by sha256 (with their dependency add-ons, whose files must also be named) and runs with updates off.
3. Needs Java 17 on the runner and an explicit dependency list that this proposal does not resolve. More moving parts than Route A; the pin does not depend on a registry tag.

In both routes the pin is void unless the update options of section 5 are set and the DRY_RUN shows the installed add-on list unchanged across a run.

## 8. What this proposal does not establish

- The add-on files the image actually holds (derived only); the tarball's add-on set.
- That a GitHub-hosted runner pulls the image from GHCR anonymously and fast enough (V-2).
- Whether rule 40018 fires against the login and the search of SUT-05 in the restricted run: not predicted here; the DRY_RUN observes it and does not choose the expectation.
- How a restricted run is seeded without a spider. For the executor draft, not the pin: the injectable targets of the core default to query string, POST data and plain body (`TARGET_INJECTABLE_DEFAULT`) and the enabled RPC variants include JSON (`TARGET_ENABLED_RPC_DEFAULT`, `VariantJSONQuery` for `application/json`), so a JSON login body should be a vector by default, but this is not tested; the API parameters that start a scan of one request (target URL, method, body, policy) are not verified here and are read from the pinned release.
- That the SQL injection scan on the login does not itself solve `loginAdminChallenge` (it can); M1 and M2 never share an instance, and every execution starts from a fresh instance (E11 brief, section 6).
- The protocol requirement to record install_date and platform: both stay null until the human approves a pin and the first run records them.

## 9. Hygiene

Sources are the registry URLs and the retrieval stamps above. The downloaded files are kept in a scratch folder outside the repository and are not part of any repository change. Third-party contact details that appear in the image configuration (a maintainer address) are omitted.
