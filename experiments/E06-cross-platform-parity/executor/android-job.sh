#!/usr/bin/env bash
# E06-cross-platform-parity Android job body (DRAFT, operation OP-PREP-E06-EXECUTOR). Runs inside the emulator action of the measured
# and environment-verification workflows, after the emulator has booted and after the APK was verified by SHA-256 by the workflow.
# It starts the Appium 3.7.0 server, waits until it answers, runs one condition through run-condition.sh, and stops the server.
# Required environment: APPIUM_BIN, APK_PATH, CONDITION_ID, ATTEMPT, RECORD_CLASS, EXPECTED_IDENTITY_ORACLE, OUTPUT_DIR, PROVENANCE_JSON,
# RUNTIME_ENVIRONMENT_JSON, EXECUTOR_PROMPT_VERSION (may be empty). Optional: ANDROID_UDID (default emulator-5554).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${APPIUM_PORT:-4723}"
export APPIUM_SERVER_URL="http://127.0.0.1:${PORT}"
export ANDROID_UDID="${ANDROID_UDID:-emulator-5554}"

for name in APPIUM_BIN APK_PATH OUTPUT_DIR; do
  if [ -z "${!name:-}" ]; then
    echo "android-job.sh: required environment variable ${name} is not set" >&2
    exit 1
  fi
done
if [ ! -f "${APK_PATH}" ]; then
  echo "android-job.sh: the APK is absent" >&2
  exit 1
fi
mkdir -p "${OUTPUT_DIR}"

# Appium 3 finds the installed drivers under APPIUM_HOME (the smoke sets it to its harness directory, qualification/compatibility-smoke-sut01/
# smoke-common.sh line 102); the default is the prefix the workflow installed the packages into.
APPIUM_HOME="${APPIUM_HOME:-$(cd "$(dirname "${APPIUM_BIN}")/../.." && pwd)}"
export APPIUM_HOME

# The hosted backend of the release build (SUT-01 only): a pre-runner reachability probe recorded beside the bundles, as the smoke does
# (smoke-common.sh, smoke_probe_backend). The probe is evidence; a refusal of the backend is then recorded per execution, not here.
if [ -n "${BACKEND_ORIGIN:-}" ]; then
  probe_code="$(curl -sS -o "${OUTPUT_DIR}/backend-health.body" -w '%{http_code}' --max-time 60 --retry 2 --retry-delay 10 "${BACKEND_ORIGIN}/health" || true)"
  printf '{"record_class": "ANDROID_JOB_ENVIRONMENT", "probe": "PRE_RUNNER_BACKEND_REACHABILITY", "health_path": "/health", "health_http_status": "%s"}\n' "${probe_code:-none}" > "${OUTPUT_DIR}/backend-probe.json"
fi

# shellcheck disable=SC2153 # APPIUM_BIN is assigned by the environment and checked by the loop above
"${APPIUM_BIN}" --address 127.0.0.1 --port "${PORT}" --log-level warn > "${OUTPUT_DIR}/appium-server.log" 2>&1 &
APPIUM_PID=$!
# shellcheck disable=SC2317 # the function is called by the EXIT trap below
cleanup() {
  kill "${APPIUM_PID}" 2>/dev/null || true
}
trap cleanup EXIT

ready=0
for _ in $(seq 1 60); do
  if curl --silent --fail "${APPIUM_SERVER_URL}/status" > /dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done
if [ "${ready}" -ne 1 ]; then
  echo "android-job.sh: the Appium server did not answer within 120 s" >&2
  exit 1
fi

set +e
bash "${HERE}/run-condition.sh"
status=$?
set -e
exit "${status}"
