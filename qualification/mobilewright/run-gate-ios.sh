#!/usr/bin/env bash
# qualification/mobilewright/run-gate-ios.sh
# Mobilewright qualification gate implementation, iOS Simulator (environment_type SIMULATED).
# Authored by QUALIFIER-MOBILE-01 under prompt version qualifier-mobile-01-mobilewright-gate-v1.
# Executed by .github/workflows/e03-mobile-qualification.yml on macos-15 with Xcode 16.4 (16F6) selected
# (iPhone 16, iOS 18.5 simulator runtime), or locally in DEVELOPMENT mode only. Record class
# QUALIFICATION; tool qualification only, never SUT evidence.
set -euo pipefail
# shellcheck source=qualification/mobilewright/gate-common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/gate-common.sh"

gate_init ios SIMULATED
gate_download_build
gate_install_runner

GATE_IOS_RUNTIME_ID="com.apple.CoreSimulator.SimRuntime.iOS-18-5"
GATE_IOS_DEVICE_TYPE="com.apple.CoreSimulator.SimDeviceType.iPhone-16"
xcode_version="$(xcodebuild -version 2>/dev/null | tr '\n' ' ')"
gate_log "xcode: $xcode_version"

if [[ -n "${GATE_DEVICE_ID:-}" ]]; then
  GATE_DEVICE_ID="${GATE_DEVICE_ID}"
else
  # The pinned identity: an iPhone 16 on the iOS 18.5 runtime (created if the image ships none).
  GATE_DEVICE_ID="$(xcrun simctl list -j devices available | python3 -c '
import json, sys
d = json.load(sys.stdin)["devices"]
for rt, devs in d.items():
    if rt == sys.argv[1]:
        for dev in devs:
            if dev.get("name") == "iPhone 16" and dev.get("isAvailable", True):
                print(dev["udid"]); sys.exit(0)
print("")' "$GATE_IOS_RUNTIME_ID")"
  if [[ -z "$GATE_DEVICE_ID" ]]; then
    gate_log "no available iPhone 16 on $GATE_IOS_RUNTIME_ID; creating one"
    GATE_DEVICE_ID="$(xcrun simctl create "EUS-Qualification-iPhone-16" "$GATE_IOS_DEVICE_TYPE" "$GATE_IOS_RUNTIME_ID")"
  fi
fi
xcrun simctl boot "$GATE_DEVICE_ID" >/dev/null 2>&1 || true
xcrun simctl bootstatus "$GATE_DEVICE_ID" -b
device_json="$(xcrun simctl list -j | python3 -c '
import json, sys, subprocess
udid, xcode = sys.argv[1], sys.argv[2]
d = json.load(sys.stdin)
entry, runtime_id = None, None
for rt, devs in d["devices"].items():
    for dev in devs:
        if dev["udid"] == udid: entry, runtime_id = dev, rt
rt = next((r for r in d["runtimes"] if r.get("identifier") == runtime_id), {})
sw = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True).stdout.strip()
print(json.dumps({"udid": udid, "kind": "iOS Simulator", "name": entry.get("name") if entry else None, "state": entry.get("state") if entry else None,
                  "device_type": entry.get("deviceTypeIdentifier") if entry else None, "runtime_identifier": runtime_id,
                  "runtime_name": rt.get("name"), "runtime_version": rt.get("version"), "runtime_build": rt.get("buildversion"),
                  "xcode": xcode.strip(), "macos_version": sw,
                  "pinned_identity": "iPhone 16, iOS 18.5 simulator runtime, Xcode 16.4 build 16F6 (manifests/toolchain-manifest.yaml environments.ios_simulator)"}))
' "$GATE_DEVICE_ID" "$xcode_version")"
gate_write_environment "$device_json"
# The runner's on-device agent (mobilecli "DeviceKit", required on iOS for input, capture, and UI-tree inspection)
# is installed on the simulator as part of installing the runner, before the first connection: the runner's
# own status probe exits non-zero when the agent is absent, which its driver reports as a connection error
# instead of installing automatically. Its status (agent version, bundle id) is recorded in the environment.
arch_suffix="$(uname -m)"; [[ "$arch_suffix" == "x86_64" ]] && arch_suffix="amd64"
GATE_MOBILECLI="$GATE_HARNESS/node_modules/@mobilenext/mobilecli-darwin-$arch_suffix/mobilecli-darwin-$arch_suffix"
if ! "$GATE_MOBILECLI" agent status --device "$GATE_DEVICE_ID" > "$GATE_OUT/environment/ios-agent-status.json" 2>&1; then
  gate_log "installing the runner's on-device agent on $GATE_DEVICE_ID"
  "$GATE_MOBILECLI" agent install --device "$GATE_DEVICE_ID" --verbose > "$GATE_OUT/environment/ios-agent-install.log" 2>&1 || true
  "$GATE_MOBILECLI" agent status --device "$GATE_DEVICE_ID" > "$GATE_OUT/environment/ios-agent-status.json" 2>&1 || { gate_log "runner agent not installed after install attempt (see environment/ios-agent-install.log)"; cat "$GATE_OUT/environment/ios-agent-status.json"; }
fi
gate_log "runner agent status: $(tr -d '\n' < "$GATE_OUT/environment/ios-agent-status.json" | cut -c1-200)"
if [[ "$GATE_MODE" == "QUALIFICATION" ]]; then
  if [[ "$xcode_version" != *"Xcode 16.4"* ]] || [[ "$xcode_version" != *"16F6"* ]]; then gate_log "Xcode is not 16.4 (16F6): failing closed (INFRASTRUCTURE)"; exit 1; fi
  if [[ "$device_json" != *'"runtime_version": "18.5"'* ]]; then gate_log "simulator runtime is not iOS 18.5: failing closed (INFRASTRUCTURE)"; exit 1; fi
fi
gate_run
