#!/usr/bin/env bash
# qualification/mobilewright/gate-common.sh
# Shared shell library of the Mobilewright qualification gate implementation (sourced by
# run-gate-android.sh and run-gate-ios.sh). Authored by QUALIFIER-MOBILE-01 under prompt version
# qualifier-mobile-01-mobilewright-gate-v1. Governing policy: protocol/mobile-runner-policy-v1.md;
# frozen inputs: manifests/mobile-qualification-package-v1.yaml and manifests/toolchain-manifest.yaml.
#
# Modes (GATE_MODE): QUALIFICATION (default; the gate; N = 10, one warm-up per combination; output under the
# authorization-specific formal namespace qualification/mobilewright/formal/<QUALIFICATION_INSTRUCTION_ID>/, which
# must be absent or empty before the first execution; requires QUALIFICATION_INSTRUCTION_ID and
# QUALIFICATION_PROMPT_VERSION_ID) or DEVELOPMENT (harness development on the operator workstation; never counted;
# output must be OUTSIDE the repository via GATE_OUTPUT_DIR; GATE_N / GATE_WARMUPS / GATE_DEVICE_ID /
# GATE_SCENARIOS may override).
# Record class is written into every record. Nothing here is evidence about any system under test.
#
# Revised 2026-09-23 under manifests/mobile-qualification-implementation-lock-v2.yaml (PROTO-U12, pre-dispatch
# execution-integrity / provenance correction): formal output is isolated from qualification/mobilewright/output/
# (the quarantined HISTORICAL_UNAUTHORIZED_EXECUTION records of 2026-09-22, never read or written by a formal run),
# and the active prompt version id is supplied by the workflow from the authorization record instead of being
# hardcoded. No scenario, runner call, pin, N, warm-up, timeout, or attribution semantics changed.

set -euo pipefail

# Pins copied from manifests/toolchain-manifest.yaml (tools.mobile_primary_candidate.qualification_build).
# The gate fails closed on any digest mismatch (policy section 3: never corrected here).
GATE_APK_URL="https://github.com/gsanchezm/OmniPizza/releases/download/v1.1.8/omnipizza-release.apk"
GATE_APK_SHA256="1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4"
GATE_IOS_URL="https://github.com/gsanchezm/OmniPizza/releases/download/v1.1.8/OmniPizza-Simulator.zip"
GATE_IOS_SHA256="de2e8c21b0788cef1ba4654378449d16e958574b33a2b4ef8a07cb698dbc6eb1"
GATE_RUNNER_PIN="0.0.60"
# Active execution prompt version: supplied by the workflow from the authorization record (never hardcoded).
GATE_PROMPT_VERSION_ID="${QUALIFICATION_PROMPT_VERSION_ID:-}"
GATE_BUNDLE_ID="com.omnipizza.app"

gate_log() { printf '[gate %s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

gate_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; else shasum -a 256 "$1" | awk '{print $1}'; fi
}

# gate_init <platform> <environment_type>
gate_init() {
  GATE_PLATFORM="$1"
  GATE_ENV_TYPE="$2"
  GATE_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  GATE_REPO="$(cd "$GATE_HERE/../.." && pwd)"
  GATE_HARNESS="$GATE_HERE/harness"
  GATE_MODE="${GATE_MODE:-QUALIFICATION}"
  GATE_CACHE="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/eus-mobile-qualification"
  mkdir -p "$GATE_CACHE"
  case "$GATE_MODE" in
    QUALIFICATION)
      if [[ -z "${QUALIFICATION_INSTRUCTION_ID:-}" ]]; then
        gate_log "QUALIFICATION mode requires QUALIFICATION_INSTRUCTION_ID (the explicit human instruction id); failing closed"; exit 1
      fi
      if [[ ! "$QUALIFICATION_INSTRUCTION_ID" =~ ^MOBILE-QUALIFICATION-EXEC-AUTH-[0-9]+$ ]]; then
        gate_log "QUALIFICATION_INSTRUCTION_ID '$QUALIFICATION_INSTRUCTION_ID' is not a MOBILE-QUALIFICATION-EXEC-AUTH-<n> id; failing closed"; exit 1
      fi
      if [[ ! "$GATE_PROMPT_VERSION_ID" =~ ^qualifier-mobile-01-mobilewright-gate-v[0-9]+$ ]]; then
        gate_log "QUALIFICATION mode requires QUALIFICATION_PROMPT_VERSION_ID (the authorization's frozen prompt version id); failing closed"; exit 1
      fi
      # Formal output isolation (PROTO-U12): an authorization-specific namespace, never the quarantined output/.
      GATE_OUT="$GATE_HERE/formal/$QUALIFICATION_INSTRUCTION_ID"
      if [[ "$GATE_OUT" == "$GATE_HERE/output" ]] || [[ "$GATE_OUT" == "$GATE_HERE/output/"* ]]; then
        gate_log "formal output namespace resolves into the quarantined output/; failing closed"; exit 1
      fi
      # Must be absent or empty (only .gitkeep allowed) BEFORE anything is written: no inherited files.
      if [[ -e "$GATE_OUT" ]]; then
        if [[ ! -d "$GATE_OUT" ]] || [[ -n "$(find "$GATE_OUT" -mindepth 1 ! -name .gitkeep -print -quit)" ]]; then
          gate_log "formal output namespace $GATE_OUT is not empty before the first execution; failing closed"; exit 1
        fi
      fi
      GATE_N=10; GATE_WARMUPS=1
      GATE_SCENARIOS="MQ1,MQ2,MQ3"
      ;;
    DEVELOPMENT)
      GATE_OUT="${GATE_OUTPUT_DIR:-}"
      if [[ -z "$GATE_OUT" ]] || [[ "$GATE_OUT" == "$GATE_REPO"* ]]; then
        gate_log "DEVELOPMENT mode requires GATE_OUTPUT_DIR outside the repository; failing closed"; exit 1
      fi
      GATE_N="${GATE_N:-1}"; GATE_WARMUPS="${GATE_WARMUPS:-0}"
      GATE_SCENARIOS="${GATE_SCENARIOS:-MQ1,MQ2,MQ3}"
      ;;
    *) gate_log "unknown GATE_MODE '$GATE_MODE'"; exit 1 ;;
  esac
  mkdir -p "$GATE_OUT/environment"
  # Every kept artifact is scrubbed of these host prefixes by run-gate.mjs (publication hygiene).
  GATE_SCRUB_PATHS="$GATE_REPO:$GATE_CACHE:$GATE_OUT:${HOME:-}:${TMPDIR:-}:${RUNNER_TEMP:-}:${GITHUB_WORKSPACE:-}"
  export GATE_SCRUB_PATHS MOBILEWRIGHT_DISABLE_TELEMETRY=1 DO_NOT_TRACK=1
  gate_log "mode=$GATE_MODE platform=$GATE_PLATFORM environment_type=$GATE_ENV_TYPE N=$GATE_N warm-ups=$GATE_WARMUPS scenarios=$GATE_SCENARIOS"
}

# gate_download_build: obtains the pinned build and verifies its digest (launch prompt, step 3).
gate_download_build() {
  local url sha file
  if [[ "$GATE_PLATFORM" == "android" ]]; then url="$GATE_APK_URL"; sha="$GATE_APK_SHA256"; file="omnipizza-release.apk"; else url="$GATE_IOS_URL"; sha="$GATE_IOS_SHA256"; file="OmniPizza-Simulator.zip"; fi
  GATE_BUILD="$GATE_CACHE/$file"
  if [[ ! -f "$GATE_BUILD" ]] || [[ "$(gate_sha256 "$GATE_BUILD")" != "$sha" ]]; then
    gate_log "downloading the pinned build $file"
    curl -fsSL --retry 3 --retry-delay 5 -o "$GATE_BUILD" "$url"
  fi
  local observed
  observed="$(gate_sha256 "$GATE_BUILD")"
  local ok=false; [[ "$observed" == "$sha" ]] && ok=true
  python3 - "$GATE_OUT/environment/$GATE_PLATFORM-build-verification.json" "$file" "$url" "$sha" "$observed" "$ok" "$(stat -c %s "$GATE_BUILD" 2>/dev/null || stat -f %z "$GATE_BUILD")" <<'PY'
import json, sys, datetime
out, name, url, expected, observed, ok, size = sys.argv[1:8]
json.dump({"record_class": "QUALIFICATION_ENVIRONMENT", "at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"), "asset": name, "source": url,
           "pinned_sha256": expected, "observed_sha256": observed, "size_bytes": int(size), "digest_match": ok == "true",
           "pin_source": "manifests/toolchain-manifest.yaml, tools.mobile_primary_candidate.qualification_build"}, open(out, "w"), indent=2)
PY
  if [[ "$ok" != "true" ]]; then
    gate_log "DIGEST MISMATCH for $file (expected $sha, observed $observed): failing closed; record the discrepancy in qualification/unresolved.md"; exit 1
  fi
  gate_log "pinned build verified: $file sha256=$observed"
}

# gate_install_runner: installs the runner exactly as pinned (lockfile) and records the observed install.
gate_install_runner() {
  local nodev
  nodev="$(node -v)"
  node -e 'const [a,b]=process.versions.node.split(".").map(Number); if (a<22||(a===22&&b<12)) { console.error("Node.js >= 22.12 required, found " + process.version); process.exit(1) }'
  ( cd "$GATE_HARNESS" && npm ci --no-audit --no-fund --loglevel=error )
  ( cd "$GATE_HARNESS" && npm ls --json --depth=2 > "$GATE_CACHE/npm-ls-$GATE_PLATFORM.json" ) || true
  python3 - "$GATE_CACHE/npm-ls-$GATE_PLATFORM.json" "$GATE_OUT/environment/$GATE_PLATFORM-runner-install.json" "$nodev" "$(npm -v)" "$GATE_RUNNER_PIN" "$(uname -s)" "$(uname -m)" "${ImageOS:-}" "${ImageVersion:-}" "$GATE_MODE" <<'PY'
import json, sys, datetime
src, out, nodev, npmv, pin, osname, arch, image_os, image_version, mode = sys.argv[1:11]
try:
    ls = json.load(open(src))
except Exception:
    ls = {}
deps = ls.get("dependencies", {})
mw = deps.get("mobilewright", {})
def find(tree, name):
    for k, v in (tree or {}).items():
        if k == name: return v.get("version")
        r = find(v.get("dependencies"), name)
        if r: return r
    return None
rec = {"record_class": "QUALIFICATION_ENVIRONMENT" if mode == "QUALIFICATION" else "DEVELOPMENT", "install_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
       "at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"), "runner_candidate": "Mobilewright", "pinned_version": pin,
       "mobilewright_version": mw.get("version"), "mobilewright_resolved": mw.get("resolved"),
       "mobilecli_version": find(deps, "mobilecli"), "driver_mobilecli_version": find(deps, "@mobilewright/driver-mobilecli"),
       "core_version": find(deps, "@mobilewright/core"), "playwright_version": find(deps, "playwright"),
       "install_method": "npm ci from qualification/mobilewright/harness/package-lock.json", "node_version": nodev, "npm_version": npmv,
       "host_platform": {"os": osname, "arch": arch, "image_os": image_os or None, "image_version": image_version or None},
       "pin_matches_observed": mw.get("version") == pin}
json.dump(rec, open(out, "w"), indent=2)
print("mobilewright observed version:", mw.get("version"), "| mobilecli:", rec["mobilecli_version"])
if mw.get("version") != pin:
    print("OBSERVED RUNNER VERSION DOES NOT MATCH THE PIN; failing closed"); sys.exit(1)
PY
}

# gate_write_environment <json-of-device-fields>: writes the platform environment record.
gate_write_environment() {
  python3 - "$GATE_OUT/environment/$GATE_PLATFORM-environment.json" "$GATE_PLATFORM" "$GATE_ENV_TYPE" "$GATE_MODE" "${QUALIFICATION_INSTRUCTION_ID:-}" "$GATE_PROMPT_VERSION_ID" "${GITHUB_RUN_ID:-}" "${GITHUB_RUN_ATTEMPT:-}" "${ImageOS:-}" "${ImageVersion:-}" "$(uname -s)" "$(uname -m)" "$(uname -r)" "$1" <<'PY'
import json, sys, datetime
out, platform, env_type, mode, instr, pv, run_id, attempt, image_os, image_version, osname, arch, kernel, device = sys.argv[1:15]
rec = {"record_class": "QUALIFICATION_ENVIRONMENT" if mode == "QUALIFICATION" else "DEVELOPMENT", "at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
       "platform": platform, "environment_type": env_type, "instruction_id": instr or None, "prompt_version_id": pv or None,
       "github": {"run_id": run_id or None, "run_attempt": attempt or None, "image_os": image_os or None, "image_version": image_version or None},
       "host": {"os": osname, "arch": arch, "kernel": kernel}, "device": json.loads(device)}
json.dump(rec, open(out, "w"), indent=2)
print(json.dumps(rec["device"]))
PY
}

# gate_run: runs the orchestrator for this platform (all combinations, sequentially).
gate_run() {
  # macOS ships bash 3.2, where expanding an empty array with "${extra[@]}" aborts under `set -u`
  # (the iOS QUALIFICATION dispatch 35763331095 failed here before any execution); the
  # ${extra[@]+"${extra[@]}"} idiom is safe in every bash version.
  local extra=()
  if [[ "$GATE_MODE" == "DEVELOPMENT" ]]; then extra=(--mode=DEVELOPMENT "--n=$GATE_N" "--warmups=$GATE_WARMUPS"); fi
  if [[ -n "${GATE_ADB_SERIAL:-}" ]]; then extra+=("--adb-serial=$GATE_ADB_SERIAL"); fi
  node "$GATE_HARNESS/run-gate.mjs" "--platform=$GATE_PLATFORM" "--device=$GATE_DEVICE_ID" "--build=$GATE_BUILD" "--out=$GATE_OUT" "--scenarios=$GATE_SCENARIOS" ${extra[@]+"${extra[@]}"}
}
