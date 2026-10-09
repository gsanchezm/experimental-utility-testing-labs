#!/usr/bin/env bash
# E03-resetability executor entry point. DRAFT (operation OP-PREP-E03): not frozen, not locked.
# Invoked by .github/workflows/e03-measured-execution.yml (MEASURED_EXPERIMENT), by a DRY_RUN step, or by hand for a
# DEVELOPMENT run. It verifies every other implementation file against the digests below, then runs the condition with
# python3 -m executor.run. Exit status 0 whenever a run manifest was written (SUCCESS, FAILURE, INCONCLUSIVE, ABORTED,
# and ERROR are recorded outcomes); non-zero only when no manifest could be written. No retry logic anywhere.
# python3 on PATH must be the interpreter where requirements.txt is installed (--require-hashes).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Implementation digests (sha256 and repository path relative to this directory), verified before anything else.
DIGESTS='
d9fddf693e61c0f3dfd6c778e549da79ae4697ac987ed38e9068edb5e5b1294a  executor/__init__.py
18ff419043ed248b84a17c2b908bbb91b7f5ac6571018a5307ecd3862a29e4dd  executor/common.py
16a5f8b3cc601874f58895db92b4eb7fa3df6791b8ab14e7594c3c3a564e3630  executor/instance.py
058d90c7c26b22837adc147978fb882311eaaa138d47ae612acd4084bfa8ba30  executor/run.py
a94961ceb3d2868c8a8ef7b374d5df568c32876e3b2562963d73e9ea58e63d6d  executor/sut01_api.py
2d98650e3075413b73542a2daa68415a4c530253669a26ebd6b566d83fd9e777  executor/sut01_web.py
f798a7c564d82a43ddb18c461b27c52403c7c8472552b23b4c0d563875693000  executor/sut02_web.py
3ef1f1ca896cd43720d2268918857f36902d72cb536f68097ff14c0301ff2d4a  executor/sut03_web.py
fe3705d755ff0e63fb4b0082292415873f3fe05e249d9fa8d994462a9e69e783  executor/sut04_api.py
d5d9383219029479cfa7277c5c66c8d2f785c099e82c559c8ebf8f1a7e653a63  executor/sut04_web.py
a8ea9191aa59f781d690addbf26028d99fdbb0a647d0e1d12aba3fac5dda45c7  executor/sut05_api.py
59b3f211f1d6877729d3bb18fe271dc0f9fc019e3336cb52d539b49430e4cf3d  executor/web.py
a88067fa0f79f0b2a92f5a3aca79908d5b6436db3c961f3836b8e9551df7a4ed  requirements.txt
'

for name in CONDITION_ID ASSIGNED_SUT EXECUTION_ID ATTEMPT EXECUTOR_PROMPT_VERSION OUTPUT_DIR PROVENANCE_JSON RUNTIME_ENVIRONMENT_JSON RECORD_CLASS; do
  if [ -z "${!name:-}" ]; then
    echo "run-condition.sh: required environment variable ${name} is not set" >&2
    exit 1
  fi
done

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

if [ -e "${OUTPUT_DIR}/run-manifest.json" ]; then
  echo "run-condition.sh: ${OUTPUT_DIR}/run-manifest.json already exists; attempts are immutable" >&2
  exit 1
fi
mkdir -p "${OUTPUT_DIR}"

export INSTANCE_JSON="${INSTANCE_JSON:-instance.json}"
export EXECUTOR_DIR="${HERE}"
export EXECUTOR_BASH_VERSION="${BASH_VERSION}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${HERE}${PYTHONPATH:+:${PYTHONPATH}}"

set +e
python3 -m executor.run
status=$?
set -e

if [ -f "${OUTPUT_DIR}/run-manifest.json" ]; then
  exit 0
fi
echo "run-condition.sh: no run manifest was written (executor exit status ${status})" >&2
exit 1
