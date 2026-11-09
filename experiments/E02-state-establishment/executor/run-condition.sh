#!/usr/bin/env bash
set -euo pipefail

# E02-state-establishment executor entry point (DRAFT; derived from the E03 executor by copying; not locked).
# The DIGESTS block below is written by tools/refresh_embedded_digests.py (never typed); it lists every implementation file.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DIGESTS='
34cef61488934b6489a5f03cbd890c345e60073b32ee88d71ed3a4ce8e22982f  executor/__init__.py
469a5aad91b80f2d1f5d0a7555e2a7defb0479f4e2916fbcb7e640092b4f1fce  executor/common.py
f14fc691a8b9ab8282272ea8c1b8000a796ee0a9ae28a6bee21c8ae488bae207  executor/instance.py
cdaacc83e441960db37c2f256e5e44c92ceae4350a725f9baca80783d68f9ff5  executor/run.py
fdfcbb746374ae3915e77a937c0b3c95829abf366cd5a5a5636846465e9d16c2  executor/sut01.py
eb3c504c91409689ced96a9c74b75854dca5b4db1f01ab4bae90149eb3c95401  executor/sut02.py
5ce8e5857d15fb9c4a3bdd826b6de98e6b38742efd65208747451602457c8d12  executor/sut03.py
bef2be5a813ca2bec03274f6b5c8d186f8aef73c02458540c6a9991bfd21c6e7  executor/sut04.py
01336e73088cba8cd8b3d31a3f225e74df3084432c864c80fc9367306d44ae2c  executor/sut05.py
179f52679b94f966310ac3a1da540b4530d57acbecb26433eabf9f1937a9ee81  executor/web.py
7d8dafab6bda619c24cd690013386dc5c1a03ff7f97733aa644d774382dd435f  requirements.txt
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
