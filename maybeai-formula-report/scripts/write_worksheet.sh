#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "${SCRIPT_DIR}/common.sh"

usage() {
  cat <<'EOF'
Usage:
  write_worksheet.sh --worksheet NAME --json-file FILE [options]

Options:
  --doc DOC_ID          MaybeAI document id. Falls back to $DOC_ID.
  --worksheet NAME      Worksheet name to create.
  --json-file FILE      JSON file containing a 2D values array.
  --base-url URL        API base URL. Defaults to $MAYBEAI_BASE_URL or production.
  -h, --help            Show help.

JSON file format:
  [
    ["指标", "Q1", "Q2"],
    ["收入", "100", "120"]
  ]
EOF
}

maybeai_init_env

ARG_DOC_ID=""
WORKSHEET=""
JSON_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --doc)
      ARG_DOC_ID="${2:?missing value for --doc}"
      shift 2
      ;;
    --worksheet)
      WORKSHEET="${2:?missing value for --worksheet}"
      shift 2
      ;;
    --json-file)
      JSON_FILE="${2:?missing value for --json-file}"
      shift 2
      ;;
    --base-url)
      MAYBEAI_BASE_URL="${2:?missing value for --base-url}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

DOC_ID="${ARG_DOC_ID:-${DOC_ID:-}}"
if [[ -z "$DOC_ID" || -z "$WORKSHEET" || -z "$JSON_FILE" ]]; then
  usage >&2
  exit 1
fi

if [[ ! -f "$JSON_FILE" ]]; then
  echo "ERROR: json file not found: $JSON_FILE" >&2
  exit 1
fi

if ! jq -e 'type == "array" and (length == 0 or .[0] | type == "array")' "$JSON_FILE" >/dev/null; then
  echo "ERROR: json file must be a 2D array." >&2
  exit 1
fi

DOC_URI="$(maybeai_doc_uri "$DOC_ID")"
PAYLOAD=$(
  jq -n \
    --arg uri "$DOC_URI" \
    --arg worksheet_name "$WORKSHEET" \
    --slurpfile values "$JSON_FILE" \
    '{
      uri: $uri,
      worksheet_name: $worksheet_name,
      values: $values[0]
    }'
)

echo "=== write_new_worksheet ${WORKSHEET} ==="
maybeai_post_json "/api/v1/excel/write_new_worksheet" "$PAYLOAD" | jq .
