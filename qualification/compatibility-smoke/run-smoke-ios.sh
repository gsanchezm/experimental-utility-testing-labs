# qualification/compatibility-smoke/run-smoke-ios.sh
# SUT-02 x iOS x Appium 3 compatibility smoke: one clean execution on the pinned iPhone 16 / iOS 18.5 Simulator with
# Xcode 16.4 (build 16F6) on the GitHub-hosted macos-15 runner of the dispatch-only workflow.
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/smoke-common.sh"

smoke_init ios SIMULATED
XCODE="$(xcodebuild -version | tr '\n' ' ')" || XCODE=""
[[ "$XCODE" == *"Xcode 16.4"*"Build version 16F6"* ]] || smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED SUBSTRATE "Xcode is not the pinned 16.4 (16F6): $XCODE"
UDID="$(xcrun simctl list devices available -j | python3 -c '
import json, sys
d = json.load(sys.stdin)["devices"]
m = [x["udid"] for rt, xs in d.items() if rt.endswith("SimRuntime.iOS-18-5") for x in xs if x.get("name") == "iPhone 16"]
print(m[0] if len(m) == 1 else "")')" || UDID=""
[[ -n "$UDID" ]] || smoke_stop NOT_EXECUTED INFRASTRUCTURE DEMONSTRATED SUBSTRATE "expected exactly one available iPhone 16 simulator with the iOS 18.5 runtime"
python3 - "$SMOKE_OUT/environment/device.json" "$UDID" "$XCODE" "$(sw_vers -productVersion)" <<'PY'
import json, sys
out, udid, xcode, macos = sys.argv[1:5]
json.dump({"kind": "iOS Simulator", "environment_type": "SIMULATED", "udid": udid, "device": "iPhone 16", "runtime": "iOS 18.5",
           "xcode": xcode.strip(), "host_macos": macos,
           "pinned_identity": "iPhone 16, iOS 18.5 runtime, Xcode 16.4 build 16F6 (manifests/toolchain-manifest.yaml environments.ios_simulator)"},
          open(out, "w"), indent=2)
PY
smoke_download_build
rm -rf "$SMOKE_CACHE/ios-app" && mkdir -p "$SMOKE_CACHE/ios-app"
( cd "$SMOKE_CACHE/ios-app" && unzip -q "$SMOKE_BUILD" ) || smoke_stop NOT_EXECUTED SUT_BUILD DEMONSTRATED BUILD_VERIFICATION "the pinned simulator build could not be unpacked"
APP="$SMOKE_CACHE/ios-app/$SMOKE_IOS_APP_REL"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$APP/Info.plist" 2>/dev/null)" == "$SMOKE_IOS_BUNDLE_ID" ]] || smoke_stop NOT_EXECUTED SUT_BUILD DEMONSTRATED BUILD_VERIFICATION "unpacked app is not $SMOKE_IOS_BUNDLE_ID"
[[ "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleSupportedPlatforms:0' "$APP/Info.plist" 2>/dev/null)" == "iPhoneSimulator" ]] || smoke_stop NOT_EXECUTED SUT_BUILD DEMONSTRATED BUILD_VERIFICATION "unpacked app is not a simulator build"
smoke_install_toolchain
# Clean start: the pinned app must not be present before the runner installs it.
xcrun simctl uninstall "$UDID" "$SMOKE_IOS_BUNDLE_ID" >/dev/null 2>&1 || true
smoke_start_server
smoke_run "$APP" "$UDID"
