#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_cmd curl

cleanup() {
  "${ROOT_DIR}/scripts/down-local.sh" >/dev/null 2>&1 || true
}
trap cleanup EXIT

"${ROOT_DIR}/scripts/up-local.sh" >/dev/null

declare -a CASES=(
  "hipotecas|operativa|24h||25"
  "prestamos|supervision|7d|Pendiente|10"
  "hipotecas|ejecutiva|30d|Ana|5"
)

for item in "${CASES[@]}"; do
  IFS='|' read -r caso vista time_range search_term limit <<< "${item}"
  echo "Running E2E case: caso_de_uso=${caso}, vista=${vista}, timeRange=${time_range}, search=${search_term:-<empty>}, limit=${limit}"

  QUERY_JSON="{\"timeRange\":\"${time_range}\",\"limit\":${limit}"
  if [ -n "${search_term}" ]; then
    QUERY_JSON="${QUERY_JSON},\"search\":\"${search_term}\""
  fi
  QUERY_JSON="${QUERY_JSON}}"

  FRONT_URL="http://127.0.0.1:${FRONT_PORT}/monitor?caso_de_uso=${caso}&vista=${vista}&timeRange=${time_range}&limit=${limit}"
  if [ -n "${search_term}" ]; then
    FRONT_URL="${FRONT_URL}&search=${search_term}"
  fi

  FRONT_CODE="$(curl -sS -o /tmp/front_case.html -w '%{http_code}' "${FRONT_URL}")"
  [ "${FRONT_CODE}" = "200" ]
  grep -q '<div id="root"></div>' /tmp/front_case.html
  rm -f /tmp/front_case.html

  CARDS_PAYLOAD="$(curl -fsS -X POST "http://127.0.0.1:${BACK_PORT}/cards?caso_de_uso=${caso}" -H 'content-type: application/json' -d "${QUERY_JSON}")"
  echo "${CARDS_PAYLOAD}" | grep -q '"cards"'

  DASHBOARD_PAYLOAD="$(curl -fsS -X POST "http://127.0.0.1:${BACK_PORT}/dashboard?caso_de_uso=${caso}" -H 'content-type: application/json' -d "${QUERY_JSON}")"
  echo "${DASHBOARD_PAYLOAD}" | grep -q '"table"'
  echo "${DASHBOARD_PAYLOAD}" | grep -q '"rows"'

  DETAIL_PAYLOAD="$(curl -fsS -X POST "http://127.0.0.1:${BACK_PORT}/dashboard_detail?caso_de_uso=${caso}&id=conv-001" -H 'content-type: application/json' -d "${QUERY_JSON}")"
  echo "${DETAIL_PAYLOAD}" | grep -q '"left"'
  echo "${DETAIL_PAYLOAD}" | grep -q '"right"'
done

echo "E2E cases local OK"
