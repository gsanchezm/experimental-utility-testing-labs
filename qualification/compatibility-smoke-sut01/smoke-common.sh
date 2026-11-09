#!/usr/bin/env bash
# qualification/compatibility-smoke-sut01/smoke-common.sh
# DRAFT (prepared, not issued, not executed). Shared helpers of the SUT-01 (OmniPizza) Android compatibility smoke of
# protocol/mobile-runner-policy-v3.md, section 9 (9.1-9.4 and 9.6 as carried from v2; 9.5 applies). Sourced by
# run-smoke-android.sh, which runs inside the dispatch-only workflow .github/workflows/e06-compatibility-smoke-sut01.yml.
# Locked by a successor implementation lock (draft, manifests/compatibility-smoke-implementation-lock-v5.draft.yaml).
# Pinned SUT-01 build: release v1.1.8, tag commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a (manifests/sut-manifest.yaml, SUT-01
# android); asset omnipizza-release.apk, digest recorded in the lock. Pinned toolchain: harness/package.json and
# harness/package-lock.json carry the same exact versions as the SUT-02 smoke (appium 3.7.0; appium-uiautomator2-driver 8.7.0).
set -euo pipefail

# Pinned SUT-02 builds (manifests/sut-manifest.yaml SUT-02 android 2.2.0 / ios 2.2.2; artifact digests recorded in the lock).
SMOKE_APK_URL="https://github.com/gsanchezm/OmniPizza/releases/download/v1.1.8/omnipizza-release.apk"
SMOKE_APK_SHA256="1059e9468145761710c9884b37e9fbc76da8e75eb9666dc0867d82a546cda6a4"
# used by run-smoke-android.sh (sourced)
# shellcheck disable=SC2034
SMOKE_ANDROID_PACKAGE="com.omnipizza.app"
SMOKE_BACKEND_ORIGIN="https://omnipizza-backend.onrender.com"
# Pinned toolchain (harness/package.json and package-lock.json carry the same exact versions).
SMOKE_NODE_PIN="22.23.2"
SMOKE_APPIUM_PIN="3.7.0"
SMOKE_UIA2_PIN="8.7.0"
SMOKE_SERVER_PORT="4723"

smoke_log() { printf '[smoke %s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
smoke_sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; else shasum -a 256 "$1" | awk '{print $1}'; fi; }

# Writes a record for an execution that stopped before the first runner action, then exits non-zero.
# $1 outcome (NOT_RUN), $2 proposed result (NOT_EXECUTED or empty for none), $3 reason.
# Stop before or around the runner with a v3 attribution proposal (protocol/mobile-runner-policy-v3.md, section 9):
#   smoke_stop <proposed result> <category> <basis> <failed phase> <description>
# NOT_EXECUTED only where the runner stack was provably not yet exercised (SUT_BUILD: the pinned build; INFRASTRUCTURE:
# substrate or host runtime outside the runner). A failure of the pinned Appium stack's installation, version check, or
# server start is proposed as FAIL_RUNNER (conservative; in-stack incompatibility is runner/toolchain evidence), with the
# logs preserved for the ORCHESTRATOR. The result is recorded by the ORCHESTRATOR (protocol/agent-governance-v6.md, Section 3.4); nothing is repeated.
smoke_stop() {
  python3 - "$SMOKE_OUT" "$SMOKE_PLATFORM" "$1" "$2" "$3" "$4" "$5" "${SMOKE_INSTRUCTION_ID:-}" "${SMOKE_PROMPT_VERSION_ID:-}" <<'PY'
import json, os, sys, datetime
out, platform, proposed, category, basis, phase, description, instr, pv = sys.argv[1:10]
evidence = sorted(os.path.relpath(os.path.join(d, f), out) for d, _, fs in os.walk(out) for f in fs) + ['record.json', 'the GitHub Actions job log of this platform job']
json.dump({"record_class": "COMPATIBILITY_SMOKE", "study_id": "EUS-2026-001", "policy": "protocol/mobile-runner-policy-v3.md, section 9 (9.1-9.4 as carried from v2; no remediation qualification is authorized under this record)",
           "instruction_id": instr or None, "prompt_version_id": pv or None, "sut_id": "SUT-01", "platform": platform,
           "outcome": "NOT_RUN", "proposed_result": proposed,
           "attribution": {"proposed_category": category, "basis": basis, "failed_phase": phase, "failed_capabilities": [],
                           "description": description, "runner_action_started": False, "harness_exception": None, "evidence": evidence},
           "recording_role": "proposal by smoke-common.sh; the ORCHESTRATOR records the result under protocol/agent-governance-v6.md, Section 3.4 (policy v3, section 9: NOT_EXECUTED only on a positively demonstrated cause outside the runner; uncertain attribution is FAIL_RUNNER)",
           "automatic_repeat": "none (policy v3, 9.5)", "steps": [], "capabilities_exercised": [],
           "at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")}, open(os.path.join(out, "record.json"), "w"), indent=2)
PY
  smoke_log "stopped: $1 ($2, $4): $5"
  smoke_scrub
  exit 1
}

smoke_init() {
  SMOKE_PLATFORM="$1"; SMOKE_ENV_TYPE="$2"
  SMOKE_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  SMOKE_REPO="$(cd "$SMOKE_HERE/../.." && pwd)"
  SMOKE_HARNESS="$SMOKE_HERE/harness"
  SMOKE_CACHE="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/eus-compat-smoke"
  mkdir -p "$SMOKE_CACHE"
  if [[ ! "${SMOKE_INSTRUCTION_ID:-}" =~ ^APPIUM3-COMPAT-SMOKE-AUTH-[0-9]{2}$ ]]; then
    smoke_log "SMOKE_INSTRUCTION_ID '${SMOKE_INSTRUCTION_ID:-}' is not an APPIUM3-COMPAT-SMOKE-AUTH-<nn> id; failing closed"; exit 1
  fi
  if [[ ! "${SMOKE_PROMPT_VERSION_ID:-}" =~ ^orchestrator-compat-smoke-sut01-v[0-9]+$ ]]; then
    smoke_log "SMOKE_PROMPT_VERSION_ID missing or malformed (orchestrator-compat-smoke-sut01-v<n>); failing closed"; exit 1
  fi
  if [[ -n "${GITHUB_RUN_ATTEMPT:-}" ]] && [[ "$GITHUB_RUN_ATTEMPT" != "1" ]]; then
    smoke_log "GitHub re-run refused (run attempt $GITHUB_RUN_ATTEMPT): a repeat needs a new explicit human authorization; failing closed"; exit 1
  fi
  SMOKE_OUT="$SMOKE_HERE/formal/$SMOKE_INSTRUCTION_ID/SUT-01-$SMOKE_PLATFORM"
  if [[ -e "$SMOKE_OUT" ]] && [[ -n "$(find "$SMOKE_OUT" -mindepth 1 ! -name .gitkeep -print -quit)" ]]; then
    smoke_log "output namespace $SMOKE_OUT is not empty before the execution; failing closed"; exit 1
  fi
  mkdir -p "$SMOKE_OUT/environment"
  smoke_log "platform=$SMOKE_PLATFORM environment_type=$SMOKE_ENV_TYPE instruction=$SMOKE_INSTRUCTION_ID prompt=$SMOKE_PROMPT_VERSION_ID"
}

smoke_download_build() {
  local url sha file
  url="$SMOKE_APK_URL"; sha="$SMOKE_APK_SHA256"; file="omnipizza-release.apk"
  SMOKE_BUILD="$SMOKE_CACHE/$file"
  curl -fsSL --retry 3 --retry-delay 5 -o "$SMOKE_BUILD" "$url" || smoke_stop NOT_EXECUTED SUT_BUILD DEMONSTRATED BUILD_ACQUISITION "the pinned build $file could not be obtained from $url"
  local observed; observed="$(smoke_sha256 "$SMOKE_BUILD")"
  python3 - "$SMOKE_OUT/environment/build-verification.json" "$file" "$url" "$sha" "$observed" <<'PY'
import json, sys, datetime, os
out, name, url, expected, observed = sys.argv[1:6]
json.dump({"record_class": "COMPATIBILITY_SMOKE_ENVIRONMENT", "asset": name, "source": url, "pinned_sha256": expected,
           "observed_sha256": observed, "digest_match": expected == observed,
           "pin_source": "manifests/compatibility-smoke-implementation-lock-v5.draft.yaml, sut_builds",
           "at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")}, open(out, "w"), indent=2)
PY
  [[ "$observed" == "$sha" ]] || smoke_stop NOT_EXECUTED SUT_BUILD DEMONSTRATED BUILD_VERIFICATION "digest mismatch for $file (pinned $sha, observed $observed)"
  smoke_log "pinned build verified: $file sha256=$observed"
}

smoke_install_toolchain() {
  local nodev; nodev="$(node -v)"
  [[ "$nodev" == "v$SMOKE_NODE_PIN" ]] || smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED HOST_RUNTIME "Node.js $nodev does not match the pin v$SMOKE_NODE_PIN"
  ( cd "$SMOKE_HARNESS" && npm ci --no-audit --no-fund --loglevel=error ) > "$SMOKE_OUT/environment/npm-ci.log" 2>&1 \
    || smoke_stop FAIL_RUNNER SELECTED_RUNNER_STACK CONSERVATIVE_TIE_BREAK TOOLCHAIN_INSTALL "npm ci of the pinned Appium stack from the locked harness failed (environment/npm-ci.log; NOT_EXECUTED / INFRASTRUCTURE only if it demonstrates a registry or network outage)"
  export APPIUM_HOME="$SMOKE_HARNESS"
  local driver pin; driver="uiautomator2"; pin="$SMOKE_UIA2_PIN"
  local corev; corev="$(cd "$SMOKE_HARNESS" && npx --no-install appium --version | tail -n 1 | tr -d '[:space:]')" || corev=""
  ( cd "$SMOKE_HARNESS" && npx --no-install appium driver list --installed --json ) > "$SMOKE_CACHE/driver-list.json" 2>"$SMOKE_CACHE/driver-list.err" || true
  if ! python3 - "$SMOKE_CACHE/driver-list.json" "$SMOKE_OUT/environment/toolchain-install.json" "$corev" "$SMOKE_APPIUM_PIN" "$driver" "$pin" "$nodev" "$(npm -v)" "$(uname -s)" "$(uname -m)" "${ImageOS:-}" "${ImageVersion:-}" <<'PY'
import json, sys, datetime
src, out, corev, corepin, driver, pin, nodev, npmv, osname, arch, image_os, image_version = sys.argv[1:13]
try:
    drivers = json.load(open(src))
except Exception:
    drivers = {}
d = drivers.get(driver) or {}
rec = {"record_class": "COMPATIBILITY_SMOKE_ENVIRONMENT", "install_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
       "at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
       "runner": "Appium", "appium_core_pin": corepin, "appium_core_observed": corev,
       "driver": driver, "driver_pin": pin, "driver_observed": d.get("version"), "driver_install_type": d.get("installType"),
       "install_method": "npm ci from qualification/compatibility-smoke-sut01/harness/package-lock.json; APPIUM_HOME = the harness directory",
       "node_version": nodev, "npm_version": npmv,
       "host_platform": {"os": osname, "arch": arch, "image_os": image_os or None, "image_version": image_version or None}}
rec["pins_match_observed"] = rec["appium_core_observed"] == corepin and rec["driver_observed"] == pin
json.dump(rec, open(out, "w"), indent=2)
print("appium core", corev, "| driver", driver, d.get("version"), "| pins match:", rec["pins_match_observed"])
sys.exit(0 if rec["pins_match_observed"] else 1)
PY
  then
    smoke_stop FAIL_RUNNER SELECTED_RUNNER_STACK CONSERVATIVE_TIE_BREAK TOOLCHAIN_VERIFY "the installed Appium core or $driver driver does not match its pin (environment/toolchain-install.json)"
  fi
}

smoke_probe_backend() {
  # Pre-runner reachability probe of the hosted backend that the pinned build calls (frontend-mobile/src/api/client.ts, API_ORIGIN,
  # at the pinned commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a). It runs before the runner is contacted. An unreachable backend
  # stops the smoke here as NOT_EXECUTED / INFRASTRUCTURE, demonstrated by these artifacts (classification: HUMAN DECISION HD-15).
  local health_code version_code
  health_code="$(curl -sS -o "$SMOKE_OUT/environment/backend-health.body" -w '%{http_code}' --max-time 60 --retry 2 --retry-delay 10 "$SMOKE_BACKEND_ORIGIN/health" 2>"$SMOKE_CACHE/backend-health.err" || true)"
  version_code="$(curl -sS -o "$SMOKE_OUT/environment/backend-version.body" -w '%{http_code}' --max-time 60 "$SMOKE_BACKEND_ORIGIN/api/version" 2>>"$SMOKE_CACHE/backend-health.err" || true)"
  python3 - "$SMOKE_OUT/environment/backend-probe.json" "$SMOKE_BACKEND_ORIGIN" "$health_code" "$version_code" <<'PY'
import datetime, json, sys
out, origin, health, version = sys.argv[1:5]
json.dump({"record_class": "COMPATIBILITY_SMOKE_ENVIRONMENT", "probe": "PRE_RUNNER_BACKEND_REACHABILITY",
           "origin": origin, "origin_pin_source": "frontend-mobile/src/api/client.ts line 27 at commit 3cdbe6596a1ab5ef2058ba4259c44da96a0fa03a (API_ORIGIN, a build-time constant)",
           "health_path": "/health", "health_http_status": health or None, "version_path": "/api/version", "version_http_status": version or None,
           "hosted_mapping": "HOSTED_MAPPING_UNVERIFIED (manifests/sut-manifest.yaml, SUT-01 api notes); /api/version body recorded, not evaluated",
           "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")}, open(out, "w"), indent=2)
PY
  [[ "$health_code" == "200" ]] || smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED BACKEND_PROBE "the hosted backend $SMOKE_BACKEND_ORIGIN/health did not answer HTTP 200 before any runner action (environment/backend-probe.json; HTTP status ${health_code:-none})"
  smoke_log "hosted backend reachable: $SMOKE_BACKEND_ORIGIN/health HTTP $health_code"
}

smoke_start_server() {
  ( cd "$SMOKE_HARNESS" && APPIUM_HOME="$SMOKE_HARNESS" npx --no-install appium --address 127.0.0.1 --port "$SMOKE_SERVER_PORT" \
      --log-no-colors --log-timestamp --log "$SMOKE_OUT/appium-server.log" > "$SMOKE_CACHE/appium-stdout.log" 2>&1 ) &
  SMOKE_SERVER_PID=$!
  for _ in $(seq 1 120); do
    if curl -fsS "http://127.0.0.1:$SMOKE_SERVER_PORT/status" >/dev/null 2>&1; then smoke_log "Appium server ready"; return 0; fi
    sleep 1
  done
  smoke_stop FAIL_RUNNER SELECTED_RUNNER_STACK CONSERVATIVE_TIE_BREAK SERVER_START "the Appium server did not become ready within 120 s (appium-server.log)"
}

smoke_run() {
  local app="$1" udid="$2"
  python3 - "$SMOKE_CACHE/context.json" "$SMOKE_OUT/environment" "$SMOKE_INSTRUCTION_ID" "$SMOKE_PROMPT_VERSION_ID" <<'PY'
import json, sys, os
out, envdir, instr, pv = sys.argv[1:5]
load = lambda n: json.load(open(os.path.join(envdir, n))) if os.path.exists(os.path.join(envdir, n)) else None
b, t, dev = load("build-verification.json"), load("toolchain-install.json"), load("device.json")
json.dump({"instruction_id": instr, "prompt_version_id": pv,
           "build": {"asset": b and b.get("asset"), "sha256": b and b.get("observed_sha256"), "source": b and b.get("source")},
           "runner": {"name": "Appium", "core_pin": "3.7.0", "core_observed": t and t.get("appium_core_observed"),
                      "driver": t and t.get("driver"), "driver_pin": t and t.get("driver_pin"), "driver_observed": t and t.get("driver_observed")},
           "device": dev,
           "github": {k: os.environ.get(v) for k, v in [("run_id", "GITHUB_RUN_ID"), ("run_attempt", "GITHUB_RUN_ATTEMPT"), ("sha", "GITHUB_SHA"),
                                                        ("workflow_ref", "GITHUB_WORKFLOW_REF"), ("image_os", "ImageOS"), ("image_version", "ImageVersion")]}},
          open(out, "w"), indent=2)
PY
  local rc=0
  ( cd "$SMOKE_HARNESS" && timeout_cmd node smoke.mjs --platform="$SMOKE_PLATFORM" --server="http://127.0.0.1:$SMOKE_SERVER_PORT" \
      --app="$app" --udid="$udid" --out="$SMOKE_OUT" --context="$SMOKE_CACHE/context.json" ) 2>&1 | tee "$SMOKE_OUT/harness.log" || rc=$?
  kill "$SMOKE_SERVER_PID" >/dev/null 2>&1 || true
  wait "$SMOKE_SERVER_PID" 2>/dev/null || true
  smoke_scrub
  [[ -f "$SMOKE_OUT/record.json" ]] || smoke_stop FAIL_RUNNER SELECTED_RUNNER_STACK CONSERVATIVE_TIE_BREAK HARNESS_PROCESS "the harness process ended without a record (exit $rc; harness.log); attribution uncertain"
  smoke_log "record written; harness exit $rc"
  [[ $rc -eq 0 ]]
}

# 45-minute watchdog for the harness process (GNU timeout on Linux, perl alarm on macOS).
timeout_cmd() {
  if command -v timeout >/dev/null 2>&1; then timeout 2700 "$@"; else perl -e 'alarm shift; exec @ARGV' 2700 "$@"; fi
}

# Publication hygiene of kept text artifacts: host paths replaced by placeholders; no measurement changes.
smoke_scrub() {
  python3 - "$SMOKE_OUT" "${GITHUB_WORKSPACE:-}" "${RUNNER_TEMP:-}" "${HOME:-}" "$SMOKE_REPO" "$SMOKE_CACHE" <<'PY'
import os, re, sys
root, *prefixes = sys.argv[1:]
prefixes = sorted({p for p in prefixes if p and len(p) > 1}, key=len, reverse=True)
homes = re.compile(r'/(?:Users|home)/[A-Za-z0-9._-]+')
changed = 0
for d, _, fs in os.walk(root):
    for f in fs:
        p = os.path.join(d, f)
        with open(p, 'rb') as fh:
            b = fh.read()
        if b'\0' in b[:8000]:
            continue
        try:
            t = b.decode('utf-8')
        except UnicodeDecodeError:
            continue
        n = t
        for pre in prefixes:
            n = n.replace(pre, '<host-path>')
        n = homes.sub('<home>', n)
        if n != t:
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(n)
            changed += 1
print(f'scrubbed host paths in {changed} file(s)')
PY
}
