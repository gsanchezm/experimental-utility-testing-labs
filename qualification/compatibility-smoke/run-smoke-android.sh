# qualification/compatibility-smoke/run-smoke-android.sh
# SUT-02 x Android x Appium 3 compatibility smoke: one clean execution on the pinned emulator (API 35,
# google_apis x86_64, pixel_7), started inside the pinned emulator-runner step of the dispatch-only workflow.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/smoke-common.sh"

smoke_init android EMULATED
adb start-server >/dev/null 2>&1 || true
mapfile -t serials < <(adb devices | awk 'NR>1 && $2=="device" {print $1}')
[[ "${#serials[@]}" -eq 1 ]] || smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED SUBSTRATE "expected exactly one online device, found ${#serials[@]}"
SERIAL="${serials[0]}"
case "$SERIAL" in emulator-*) ;; *) smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED SUBSTRATE "device $SERIAL is not an emulator serial" ;; esac
adb -s "$SERIAL" wait-for-device
for _ in $(seq 1 180); do [[ "$(adb -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" == "1" ]] && break; sleep 5; done
[[ "$(adb -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" == "1" ]] || smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED SUBSTRATE "emulator $SERIAL did not complete boot within 900 s"
prop() { adb -s "$SERIAL" shell getprop "$1" 2>/dev/null | tr -d '\r'; }
python3 - "$SMOKE_OUT/environment/device.json" "$SERIAL" "$(prop ro.build.version.release)" "$(prop ro.build.version.sdk)" "$(prop ro.product.model)" \
  "$(prop ro.product.cpu.abi)" "$(prop ro.boot.qemu.avd_name)" "$(prop ro.build.fingerprint)" "$(java -version 2>&1 | head -n 1)" <<'PY'
import json, sys
out, serial, rel, sdk, model, abi, avd, fp, java = sys.argv[1:10]
json.dump({"kind": "Android emulator", "environment_type": "EMULATED", "serial": serial, "android_release": rel, "api_level": sdk, "model": model,
           "abi": abi, "avd_name": avd, "build_fingerprint": fp, "java": java,
           "pinned_identity": "system-images;android-35;google_apis;x86_64, API 35, profile pixel_7 (manifests/toolchain-manifest.yaml environments.android_emulator)"},
          open(out, "w"), indent=2)
PY
[[ "$(prop ro.build.version.sdk)" == "35" ]] || smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED SUBSTRATE "API level $(prop ro.build.version.sdk) does not match the pinned API 35 (environment/device.json)"
smoke_download_build
smoke_install_toolchain
# Clean start: the pinned app must not be present before the runner installs it (a freshly created AVD).
adb -s "$SERIAL" uninstall "$SMOKE_ANDROID_PACKAGE" >/dev/null 2>&1 || true
smoke_start_server
smoke_run "$SMOKE_BUILD" "$SERIAL"
