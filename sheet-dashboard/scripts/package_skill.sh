#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PARENT_DIR="$(cd "${SKILL_DIR}/.." && pwd)"
SKILL_NAME="$(basename "${SKILL_DIR}")"
OUTPUT_DIR="${1:-${PARENT_DIR}/dist}"

mkdir -p "${OUTPUT_DIR}"
ARCHIVE_PATH="${OUTPUT_DIR}/${SKILL_NAME}.tgz"
TMP_DIR="$(mktemp -d)"
TMP_ARCHIVE="${TMP_DIR}/${SKILL_NAME}.tgz"

cleanup() {
  rm -rf "${TMP_DIR}"
}

trap cleanup EXIT

tar --exclude="${SKILL_NAME}/dist" -C "${PARENT_DIR}" -czf "${TMP_ARCHIVE}" "${SKILL_NAME}"
mv "${TMP_ARCHIVE}" "${ARCHIVE_PATH}"
echo "${ARCHIVE_PATH}"
