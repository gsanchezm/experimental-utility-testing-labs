#!/usr/bin/env bash
# preflight-android-driver.sh — LOCAL_DEVELOPMENT_PREFLIGHT driver, Android physical device (Samsung Galaxy Z Flip 6).
# Lives OUTSIDE the repository (session scratchpad). It edits nothing: it sources the locked
# qualification/mobilewright/gate-common.sh unchanged and invokes the locked harness/run-gate.mjs unchanged.
# The locked run-gate-android.sh is NOT used because it is emulator-only by construction (it fails closed on any
# adb serial that does not start with "emulator-" and derives the runner device id from ro.boot.qemu.avd_name);
# this driver reproduces its remaining steps (build download + digest verification, runner install exactly as
# pinned, environment record, explicit device id, orchestrator start) for a physical device.
# Mode DEVELOPMENT of the locked library: N = 1, no warm-up, output outside the repository, record class DEVELOPMENT
# (the LOCAL_DEVELOPMENT_PREFLIGHT classification is added by the sidecar records at import, never by editing the harness).
# Inputs (environment): EUS_REPO = repository root; PREFLIGHT_OUT = output directory outside the repository;
# PREFLIGHT_SERIAL = adb serial of the physical device (also the runner's device id for a real Android device).
set -euo pipefail
: "${EUS_REPO:?EUS_REPO (repository root) is required}"
: "${PREFLIGHT_OUT:?PREFLIGHT_OUT (output directory outside the repository) is required}"
: "${PREFLIGHT_SERIAL:?PREFLIGHT_SERIAL (adb serial of the physical device) is required}"

export GATE_MODE=DEVELOPMENT
export GATE_OUTPUT_DIR="$PREFLIGHT_OUT"
export GATE_N=1
export GATE_WARMUPS=0
export GATE_SCENARIOS="${GATE_SCENARIOS:-MQ1,MQ2,MQ3}"

# shellcheck source=/dev/null
source "$EUS_REPO/qualification/mobilewright/gate-common.sh"

# environment_type OTHER: a physical Android device is not covered by EMULATED (protocol/study-design-v1.md, section 10);
# the harness's own records label the platform "Android emulator" / EMULATED by construction (run-gate.mjs) — disclosed at import.
gate_init android OTHER
gate_download_build
gate_install_runner

ADB="${ANDROID_HOME:-$HOME/Library/Android/sdk}/platform-tools/adb"
"$ADB" start-server >/dev/null 2>&1 || true
"$ADB" -s "$PREFLIGHT_SERIAL" wait-for-device
prop() { "$ADB" -s "$PREFLIGHT_SERIAL" shell getprop "$1" 2>/dev/null | tr -d '\r'; }
transport="$("$ADB" devices -l | awk -v s="$PREFLIGHT_SERIAL" '$1==s {for (i=3;i<=NF;i++) if ($i ~ /^usb:/) print $i}')"
device_json="$(python3 - "$PREFLIGHT_SERIAL" "$(prop ro.product.manufacturer)" "$(prop ro.product.model)" "$(prop ro.product.name)" "$(prop ro.build.version.release)" "$(prop ro.build.version.sdk)" "$(prop ro.product.cpu.abi)" "$(prop ro.build.fingerprint)" "$(prop ro.kernel.qemu)" "$("$ADB" version | head -n 1)" "$(prop ro.build.version.security_patch)" "$(prop ro.build.display.id)" "$transport" "$(sysctl -n hw.model 2>/dev/null || echo "")" "$(sw_vers -productVersion 2>/dev/null || echo "")" "$(sysctl -n vm.loadavg 2>/dev/null || echo "")" <<'PY'
import json, sys
serial, manufacturer, model, name, rel, sdk, abi, fp, qemu, adbv, patch, display, transport, hostmodel, macos, load = sys.argv[1:17]
print(json.dumps({"serial": serial, "kind": "Android physical device (human-owned)", "manufacturer": manufacturer, "model": model, "product_name": name,
                  "android_release": rel, "api_level": sdk, "abi": abi, "build_fingerprint": fp, "build_display_id": display, "is_emulator": qemu == "1",
                  "connection_mode": "USB (adb transport " + transport + ")" if transport else "adb", "adb_version": adbv, "security_patch": patch,
                  "host": {"model": hostmodel, "macos_version": macos, "load_average_at_start": load},
                  "pinned_identity": "NONE — not the frozen Android qualification substrate (system-images;android-35;google_apis;x86_64, API 35, profile pixel_7); diagnostic only (LOCAL_DEVELOPMENT_PREFLIGHT)"}))
PY
)"
gate_write_environment "$device_json"

# The runner's device server identifies a real Android device by its adb serial (observed with `mobilecli devices`:
# id R5CX…, type real); the same serial is passed to the harness for the locked failure-time log capture.
GATE_ADB_SERIAL="$PREFLIGHT_SERIAL"
GATE_DEVICE_ID="$PREFLIGHT_SERIAL"
gate_log "runner device id (real device serial, partially shown): ${GATE_DEVICE_ID:0:4}…; adb serial identical"
gate_run
