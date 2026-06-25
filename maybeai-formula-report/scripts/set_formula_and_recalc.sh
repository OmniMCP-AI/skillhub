#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "${SCRIPT_DIR}/common.sh"

# Set one formula cell or one batch of formula blocks in a MaybeAI workbook
# and optionally recalculate the doc.
#
# Usage:
#   bash scripts/set_formula_and_recalc.sh \
#     --doc 6a326bd0d4fb73e454cefda6 \
#     --worksheet "利润分析" \
#     --cell "F2" \
#     --formula "=SUM(B2:E2)"
#
#   bash scripts/set_formula_and_recalc.sh \
#     --worksheet "关键指标" \
#     --cell "B5" \
#     --formula "=利润分析!B11" \
#     --no-recalc
#
#   bash scripts/set_formula_and_recalc.sh \
#     --doc 6a326bd0d4fb73e454cefda6 \
#     --operations-json /path/to/formula_blocks.json

usage() {
  cat <<'EOF'
Usage:
  set_formula_and_recalc.sh --worksheet SHEET --cell A1 --formula '=SUM(B2:E2)' [options]
  set_formula_and_recalc.sh --operations-json FILE [options]

Options:
  --doc DOC_ID          MaybeAI document id. Falls back to $DOC_ID.
  --worksheet NAME      Target worksheet name.
  --cell A1             Target cell reference.
  --formula TEXT        Formula text beginning with "=".
  --operations-json FILE
                       JSON file containing formula/batch_set operations.
  --no-recalc           Skip the final workbook recalculation call.
  --base-url URL        API base URL. Defaults to $MAYBEAI_BASE_URL or production.
  -h, --help            Show help.
EOF
}

maybeai_init_env

ARG_DOC_ID=""
WORKSHEET=""
CELL=""
FORMULA=""
OPERATIONS_JSON=""
RUN_RECALC=1

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
    --cell)
      CELL="${2:?missing value for --cell}"
      shift 2
      ;;
    --formula)
      FORMULA="${2:?missing value for --formula}"
      shift 2
      ;;
    --operations-json)
      OPERATIONS_JSON="${2:?missing value for --operations-json}"
      shift 2
      ;;
    --no-recalc)
      RUN_RECALC=0
      shift
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
if [[ -z "$DOC_ID" ]]; then
  usage >&2
  exit 1
fi

if [[ -n "$OPERATIONS_JSON" ]]; then
  if [[ -n "$WORKSHEET" || -n "$CELL" || -n "$FORMULA" ]]; then
    echo "ERROR: --operations-json cannot be combined with --worksheet/--cell/--formula" >&2
    exit 1
  fi
  if [[ ! -f "$OPERATIONS_JSON" ]]; then
    echo "ERROR: operations file not found: $OPERATIONS_JSON" >&2
    exit 1
  fi
elif [[ -z "$WORKSHEET" || -z "$CELL" || -z "$FORMULA" ]]; then
  usage >&2
  exit 1
fi

DOC_URI="$(maybeai_doc_uri "$DOC_ID")"

if [[ -n "$OPERATIONS_JSON" ]]; then
  BATCH_PAYLOAD=$(
    jq -n \
      --arg uri "$DOC_URI" \
      --argjson operations "$(jq -c . "$OPERATIONS_JSON")" \
      --arg recalc_mode "$([[ "$RUN_RECALC" -eq 1 ]] && echo workbook || echo none)" \
      '{
        uri: $uri,
        skip_recalculation: true,
        recalculate_mode: $recalc_mode,
        operations: $operations
      }'
  )

  echo "=== formula/batch_set $(basename "$OPERATIONS_JSON") ==="
  maybeai_post_json "/api/v1/excel/formula/batch_set" "$BATCH_PAYLOAD" | jq .
else
  SET_PAYLOAD=$(
    jq -n \
      --arg uri "$DOC_URI" \
      --arg worksheet_name "$WORKSHEET" \
      --arg cell "$CELL" \
      --arg formula "$FORMULA" \
      '{
        uri: $uri,
        worksheet_name: $worksheet_name,
        cell: $cell,
        formula: $formula,
        skip_recalculation: true
      }'
  )

  echo "=== formula/set ${WORKSHEET}!${CELL} ==="
  maybeai_post_json "/api/v1/excel/formula/set" "$SET_PAYLOAD" | jq .

  if [[ "$RUN_RECALC" -eq 1 ]]; then
    RECALC_PAYLOAD=$(jq -n --arg uri "$DOC_URI" '{uri: $uri}')
    echo "=== recalculate_formulas ==="
    maybeai_post_json "/api/v1/excel/recalculate_formulas" "$RECALC_PAYLOAD" | jq .
  fi
fi
