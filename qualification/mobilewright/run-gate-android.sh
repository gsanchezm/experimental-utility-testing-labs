#!/usr/bin/env bash
# qualification/mobilewright/run-gate-android.sh
# Mobilewright qualification gate implementation, Android emulator (environment_type EMULATED).
# Authored by QUALIFIER-MOBILE-01 under prompt version qualifier-mobile-01-mobilewright-gate-v1.
# Executed by .github/workflows/e03-mobile-qualification.yml inside the pinned emulator-runner step
# (system-images;android-35;google_apis;x86_64, profile pixel_7, ubuntu-24.04), or locally in
# DEVELOPMENT mode only. Record class QUALIFICATION; tool qualification only, never SUT evidence.
set -euo pipefail
# shellcheck source=qualification/mobilewright/gate-common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/gate-common.sh"

gate_init android EMULATED
gate_download_build
gate_install_runner

# Device: the single booted emulator (explicit serial; auto-discovery is never used).
adb start-server >/dev/null 2>&1 || true
if [[ -n "${GATE_DEVICE_ID:-}" ]]; then
  GATE_DEVICE_ID="${GATE_DEVICE_ID}"
else
  mapfile -t serials < <(adb devices | awk 'NR>1 && $2=="device" {print $1}')
  if [[ "${#serials[@]}" -ne 1 ]]; then gate_log "expected exactly one online device, found ${#serials[@]}: ${serials[*]:-none}; failing closed (INFRASTRUCTURE)"; exit 1; fi
  GATE_DEVICE_ID="${serials[0]}"
fi
case "$GATE_DEVICE_ID" in emulator-*) ;; *) gate_log "device $GATE_DEVICE_ID is not an emulator serial; failing closed"; exit 1 ;; esac
adb -s "$GATE_DEVICE_ID" wait-for-device
until [[ "$(adb -s "$GATE_DEVICE_ID" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" == "1" ]]; do sleep 5; done
prop() { adb -s "$GATE_DEVICE_ID" shell getprop "$1" 2>/dev/null | tr -d '\r'; }
emulator_version="$("${ANDROID_HOME:-$HOME/Library/Android/sdk}/emulator/emulator" -version 2>/dev/null | head -n 1 || echo "")"
device_json="$(python3 - "$GATE_DEVICE_ID" "$(prop ro.build.version.release)" "$(prop ro.build.version.sdk)" "$(prop ro.product.model)" "$(prop ro.product.cpu.abi)" "$(prop ro.boot.qemu.avd_name)" "$(prop ro.build.fingerprint)" "$(prop ro.kernel.qemu)" "$(adb version | head -n 1)" "$emulator_version" "$(prop ro.build.version.security_patch)" <<'PY'
import json, sys
serial, rel, sdk, model, abi, avd, fp, qemu, adbv, emuv, patch = sys.argv[1:12]
print(json.dumps({"serial": serial, "kind": "Android emulator", "android_release": rel, "api_level": sdk, "model": model, "abi": abi, "avd_name": avd,
                  "build_fingerprint": fp, "is_emulator": qemu == "1", "adb_version": adbv, "emulator_version": emuv, "security_patch": patch,
                  "pinned_identity": "system-images;android-35;google_apis;x86_64, API 35, profile pixel_7 (manifests/toolchain-manifest.yaml environments.android_emulator)"}))
PY
)"
gate_write_environment "$device_json"
if [[ "$GATE_MODE" == "QUALIFICATION" ]] && [[ "$(prop ro.build.version.sdk)" != "35" ]]; then
  gate_log "API level $(prop ro.build.version.sdk) does not match the pinned API 35; failing closed (INFRASTRUCTURE)"; exit 1
fi
# The runner's device server (mobilecli) identifies an emulator by its AVD name, not by the adb serial:
# the runner is given the AVD name as the explicit device id; the adb serial is used only by the harness.
GATE_ADB_SERIAL="$GATE_DEVICE_ID"
GATE_DEVICE_ID="$(prop ro.boot.qemu.avd_name)"
if [[ -z "$GATE_DEVICE_ID" ]]; then gate_log "cannot read the AVD name (ro.boot.qemu.avd_name); failing closed (INFRASTRUCTURE)"; exit 1; fi
gate_log "runner device id (AVD name): $GATE_DEVICE_ID; adb serial: $GATE_ADB_SERIAL"
gate_run
