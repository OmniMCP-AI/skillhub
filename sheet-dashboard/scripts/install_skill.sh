#!/usr/bin/env bash
set -euo pipefail

MODE="copy"
FORCE="0"

usage() {
  cat <<'EOF'
Usage:
  install_skill.sh <skills-root> [--link] [--force]

Examples:
  ./install_skill.sh ~/.codex/skills
  ./install_skill.sh ~/.agents/skills --link
  ./install_skill.sh /path/to/openclaw/skills --force
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

TARGET_ROOT=""
for arg in "$@"; do
  case "$arg" in
    --link) MODE="link" ;;
    --force) FORCE="1" ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$TARGET_ROOT" ]]; then
        TARGET_ROOT="$arg"
      else
        echo "Unexpected argument: $arg" >&2
        exit 1
      fi
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILL_NAME="$(basename "${SKILL_DIR}")"
TARGET_ROOT="${TARGET_ROOT/#\~/${HOME}}"
TARGET_DIR="${TARGET_ROOT}/${SKILL_NAME}"

mkdir -p "${TARGET_ROOT}"

if [[ -e "${TARGET_DIR}" ]]; then
  if [[ "${FORCE}" != "1" ]]; then
    echo "Target already exists: ${TARGET_DIR}" >&2
    echo "Re-run with --force to replace it." >&2
    exit 1
  fi
  rm -rf "${TARGET_DIR}"
fi

if [[ "${MODE}" == "link" ]]; then
  ln -s "${SKILL_DIR}" "${TARGET_DIR}"
else
  cp -R "${SKILL_DIR}" "${TARGET_DIR}"
fi

echo "Installed ${SKILL_NAME} -> ${TARGET_DIR}"
