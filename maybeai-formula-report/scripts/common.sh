#!/usr/bin/env bash

if [[ -n "${MAYBEAI_FORMULA_REPORT_COMMON_SH_LOADED:-}" ]]; then
  return 0
fi
MAYBEAI_FORMULA_REPORT_COMMON_SH_LOADED=1

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $1" >&2
    exit 1
  }
}

maybeai_require_base_tools() {
  require_cmd curl
  require_cmd jq
}

maybeai_init_env() {
  maybeai_require_base_tools
  : "${MAYBEAI_API_TOKEN:?Please set MAYBEAI_API_TOKEN}"
  MAYBEAI_BASE_URL="${MAYBEAI_BASE_URL:-https://play-be.omnimcp.ai}"
}

maybeai_doc_uri() {
  local doc_id="$1"
  printf 'https://www.maybe.ai/docs/spreadsheets/d/%s' "$doc_id"
}

maybeai_post_json() {
  local endpoint="$1"
  local payload="$2"
  curl -sS -X POST "${MAYBEAI_BASE_URL}${endpoint}" \
    -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data-binary "$payload"
}

maybeai_bool_json() {
  if [[ "$1" -eq 1 ]]; then
    printf 'true'
  else
    printf 'false'
  fi
}
