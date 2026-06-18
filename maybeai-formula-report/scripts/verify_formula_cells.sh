#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "${SCRIPT_DIR}/common.sh"

# Verify that MaybeAI cells do not remain empty or as literal "=..." text
# after a formula-driven workflow.
#
# Single-cell usage:
#   bash scripts/verify_formula_cells.sh \
#     --doc 6a326bd0d4fb73e454cefda6 \
#     --worksheet "利润分析" \
#     --cell "F2" \
#     --expect-numeric
#
# Multi-cell usage:
#   bash scripts/verify_formula_cells.sh --doc 6a326bd0d4fb73e454cefda6 \
#     --checks-json /path/to/checks.json
#
# checks.json format:
# [
#   {"worksheet":"利润分析","cell":"F2","expect_numeric":true},
#   {"worksheet":"关键指标","cell":"B5","expected_value":"1.12"}
# ]

usage() {
  cat <<'EOF'
Usage:
  verify_formula_cells.sh [single-cell options] [--checks-json FILE]

Single-cell options:
  --doc DOC_ID            MaybeAI document id. Falls back to $DOC_ID.
  --worksheet NAME        Target worksheet name.
  --cell A1               Cell reference to read.
  --expect-numeric        Fail unless the readback is numeric.
  --expected-value VALUE  Fail unless the readback matches exactly.
  --allow-empty           Do not fail on empty readback.

General options:
  --checks-json FILE      JSON array of check objects.
  --base-url URL          API base URL. Defaults to $MAYBEAI_BASE_URL or production.
  -h, --help              Show help.
EOF
}

is_numeric() {
  [[ "$1" =~ ^-?[0-9]+([.][0-9]+)?$ ]]
}

maybeai_init_env

ARG_DOC_ID=""
SINGLE_WORKSHEET=""
SINGLE_CELL=""
SINGLE_EXPECT_NUMERIC=0
SINGLE_EXPECTED_VALUE=""
SINGLE_ALLOW_EMPTY=0
CHECKS_JSON=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --doc)
      ARG_DOC_ID="${2:?missing value for --doc}"
      shift 2
      ;;
    --worksheet)
      SINGLE_WORKSHEET="${2:?missing value for --worksheet}"
      shift 2
      ;;
    --cell)
      SINGLE_CELL="${2:?missing value for --cell}"
      shift 2
      ;;
    --expect-numeric)
      SINGLE_EXPECT_NUMERIC=1
      shift
      ;;
    --expected-value)
      SINGLE_EXPECTED_VALUE="${2:?missing value for --expected-value}"
      shift 2
      ;;
    --allow-empty)
      SINGLE_ALLOW_EMPTY=1
      shift
      ;;
    --checks-json)
      CHECKS_JSON="${2:?missing value for --checks-json}"
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
if [[ -z "$DOC_ID" ]]; then
  usage >&2
  exit 1
fi

DOC_URI="$(maybeai_doc_uri "$DOC_ID")"
TMP_CHECKS=""

cleanup() {
  [[ -n "$TMP_CHECKS" && -f "$TMP_CHECKS" ]] && rm -f "$TMP_CHECKS"
}
trap cleanup EXIT

if [[ -z "$CHECKS_JSON" ]]; then
  if [[ -z "$SINGLE_WORKSHEET" || -z "$SINGLE_CELL" ]]; then
    usage >&2
    exit 1
  fi
  TMP_CHECKS="$(mktemp)"
  jq -n \
    --arg worksheet "$SINGLE_WORKSHEET" \
    --arg cell "$SINGLE_CELL" \
    --arg expected_value "$SINGLE_EXPECTED_VALUE" \
    --argjson expect_numeric "$([[ "$SINGLE_EXPECT_NUMERIC" -eq 1 ]] && echo true || echo false)" \
    --argjson allow_empty "$([[ "$SINGLE_ALLOW_EMPTY" -eq 1 ]] && echo true || echo false)" \
    '[{
      worksheet: $worksheet,
      cell: $cell,
      expect_numeric: $expect_numeric,
      allow_empty: $allow_empty
    } + (if $expected_value == "" then {} else {expected_value: $expected_value} end)]' \
    > "$TMP_CHECKS"
  CHECKS_JSON="$TMP_CHECKS"
fi

failures=0
while IFS= read -r check; do
  worksheet=$(jq -r '.worksheet' <<<"$check")
  cell=$(jq -r '.cell' <<<"$check")
  expect_numeric=$(jq -r '.expect_numeric // false' <<<"$check")
  allow_empty=$(jq -r '.allow_empty // false' <<<"$check")
  expected_value=$(jq -r '.expected_value // ""' <<<"$check")

  payload=$(
    jq -n \
      --arg uri "$DOC_URI" \
      --arg worksheet_name "$worksheet" \
      --arg range_address "$cell" \
      '{uri: $uri, worksheet_name: $worksheet_name, range_address: $range_address}'
  )

  response="$(maybeai_post_json "/api/v1/excel/read_sheet" "$payload")"

  value=$(jq -r '.values[0][0] // ""' <<<"$response")

  if [[ -z "$value" && "$allow_empty" != "true" ]]; then
    echo "FAIL ${worksheet}!${cell}: empty value" >&2
    failures=$((failures + 1))
    continue
  fi

  if [[ "$value" == "="* ]]; then
    echo "FAIL ${worksheet}!${cell}: still shows literal formula text: $value" >&2
    failures=$((failures + 1))
    continue
  fi

  if [[ -n "$expected_value" && "$value" != "$expected_value" ]]; then
    echo "FAIL ${worksheet}!${cell}: expected '$expected_value' but got '$value'" >&2
    failures=$((failures + 1))
    continue
  fi

  if [[ "$expect_numeric" == "true" ]] && ! is_numeric "$value"; then
    echo "FAIL ${worksheet}!${cell}: expected numeric value but got '$value'" >&2
    failures=$((failures + 1))
    continue
  fi

  echo "OK ${worksheet}!${cell}: $value"
done < <(jq -c '.[]' "$CHECKS_JSON")

if [[ "$failures" -gt 0 ]]; then
  echo "Verification failed: $failures check(s) failed." >&2
  exit 1
fi

echo "Verification passed."
