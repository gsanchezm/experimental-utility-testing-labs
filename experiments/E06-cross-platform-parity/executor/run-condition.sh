#!/usr/bin/env bash
# E06-cross-platform-parity executor entry (DRAFT, operation OP-PREP-E06-EXECUTOR). Not frozen, not locked, not dispatched.
#
# One condition per invocation; N executions of attempt 1, or, for a further attempt, executions FIRST_EXECUTION to N (the measured workflow admits a further attempt only under a recorded approval of the human research lead; the non-measured records are attempt 1 only). The implementation digests below
# are verified before anything else; an unlisted Python file under executor/ is refused. A DRY_RUN writes 3 executions and an
# ENVIRONMENT_VERIFICATION writes 1; both are labelled non-measured and never enter raw-data/ (the workflow decides where the output goes).
#
# Required environment: CONDITION_ID, ATTEMPT (1 or more), FIRST_EXECUTION (optional, default 1), RECORD_CLASS (MEASURED_EXPERIMENT | DRY_RUN | ENVIRONMENT_VERIFICATION),
# EXPECTED_IDENTITY_ORACLE (item_identity | arrival_only, the value of the locked configuration), OUTPUT_DIR, PROVENANCE_JSON,
# RUNTIME_ENVIRONMENT_JSON. Optional: EXECUTOR_PROMPT_VERSION (empty for a non-measured draft), CONDITIONS_FILE, NODE_BIN, ADB_BIN.
# Android conditions also need APK_PATH (the APK already verified by the workflow), APPIUM_SERVER_URL, and ANDROID_UDID.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DIGESTS='
892bc6b2579e39e5c32defd115aea900634b3aa4605fae70b04348a760dc657c  executor/__init__.py
24760ecf052d8ac9247b0ee4bc2737583387139f545b352404f9c5ea7baeac8e  executor/android.py
f86917d1071de55dfa14f5b9bd2c2c9d9c69806129b668e11f1c2f81c74251b3  executor/classify.py
308a539ff01e628ca69722badaf996b8741465375002352715b5dbeafd1f7c9d  executor/common.py
8bece1447b9549c88d593a5c25bd33bdcd4b0b581a5c0a5eb9b6c9cf3322faab  executor/config.py
4cd9b9b84ed564c560d9448c3500814ecd9e0a45cf4fc6bb6cd4c144a1f40c7c  executor/identity.py
b0b1e1de395e831df3231e3b00b0f4cee5b7305282c28c1d014a42b3640b7cdf  executor/run.py
197ce02d746879304f6cf67281ea813485527726d21170f053c5a80f0bf451be  executor/web.py
589b920c552fae45dbc4c9507e42a21344d250abb2573c5412e2aea8cca62de2  requirements.txt
31e6b25c2fa63d98242b92280c804bb902720439ce03b3c26387299a884e0d0b  android-job.sh
46eadda02e2fae0756492e06b78be834396e71bfedbbf79a0963a965b93ae790  ../harness/e06-android.mjs
cf1b286f79585c654c631038194170e1f5a32840b15a446384bcc79d30a7ffeb  ../harness/wd.mjs
b97c492af7c9be1f5716b05cf29666b7b7dff6588f9788b63499203dfa3a1fcd  ../conditions-draft.json
0c7807598f7b5a2e80aed27a8bdf7aed71b23d0ab3a21a48a764c8b347770242  ../../../qualification/compatibility-smoke-sut01/harness/package.json
8a4a02cafa1edec0e8eb7704cec107ab6a2c398dd1e0c8e8a9df3dcb9ac3b3f5  ../../../qualification/compatibility-smoke-sut01/harness/package-lock.json
'

for name in CONDITION_ID ATTEMPT RECORD_CLASS EXPECTED_IDENTITY_ORACLE OUTPUT_DIR PROVENANCE_JSON RUNTIME_ENVIRONMENT_JSON; do
  if [ -z "${!name:-}" ]; then
    echo "run-condition.sh: required environment variable ${name} is not set" >&2
    exit 1
  fi
done

export FIRST_EXECUTION="${FIRST_EXECUTION:-1}"
for name in ATTEMPT FIRST_EXECUTION; do
  case "${!name}" in
    ''|*[!0-9]*|0|0[0-9]*) echo "run-condition.sh: ${name} must be a positive integer (got ${!name})" >&2; exit 1 ;;
    *) ;;
  esac
done
if [ "${ATTEMPT}" = "1" ] && [ "${FIRST_EXECUTION}" != "1" ]; then
  echo "run-condition.sh: attempt 1 starts at execution 1 (FIRST_EXECUTION ${FIRST_EXECUTION} refused); a later first execution belongs to a further attempt" >&2
  exit 1
fi

case "${RECORD_CLASS}" in
  MEASURED_EXPERIMENT|DRY_RUN|ENVIRONMENT_VERIFICATION) ;;
  *) echo "run-condition.sh: record class ${RECORD_CLASS} is not allowed" >&2; exit 1 ;;
esac

case "${EXPECTED_IDENTITY_ORACLE}" in
  item_identity|arrival_only) ;;
  *) echo "run-condition.sh: identity oracle ${EXPECTED_IDENTITY_ORACLE} is not an allowed value" >&2; exit 1 ;;
esac

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -c1-64
  else
    shasum -a 256 "$1" | cut -c1-64
  fi
}

listed=""
while read -r digest path; do
  if [ -z "${digest}" ]; then
    continue
  fi
  if [ ! -f "${HERE}/${path}" ]; then
    echo "run-condition.sh: implementation file missing: ${path}" >&2
    exit 1
  fi
  actual="$(sha256_of "${HERE}/${path}")"
  if [ "${actual}" != "${digest}" ]; then
    echo "run-condition.sh: digest mismatch for ${path}" >&2
    exit 1
  fi
  listed="${listed}${path}"$'\n'
done <<< "${DIGESTS}"

while IFS= read -r file; do
  rel="${file#"${HERE}/"}"
  if ! printf '%s' "${listed}" | grep -Fqx -- "${rel}"; then
    echo "run-condition.sh: unlisted Python file under executor/: ${rel}" >&2
    exit 1
  fi
done < <(find "${HERE}/executor" -type f -name '*.py' | LC_ALL=C sort)

if [ -e "${OUTPUT_DIR}/condition-summary.json" ]; then
  echo "run-condition.sh: ${OUTPUT_DIR}/condition-summary.json already exists; attempts are immutable" >&2
  exit 1
fi
mkdir -p "${OUTPUT_DIR}"

export CONDITIONS_FILE="${CONDITIONS_FILE:-${HERE}/../conditions-draft.json}"
export EXECUTOR_DIR="${HERE}"
export HARNESS_DIR="${HERE}/../harness"
export EXECUTOR_BASH_VERSION="${BASH_VERSION}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${HERE}${PYTHONPATH:+:${PYTHONPATH}}"

set +e
python3 -m executor.run
status=$?
set -e

if [ "${status}" -ne 0 ]; then
  exit "${status}"
fi
if [ -f "${OUTPUT_DIR}/condition-summary.json" ]; then
  exit 0
fi
echo "run-condition.sh: no condition summary was written" >&2
exit 1
