#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_cmd curl

cleanup() {
  "${ROOT_DIR}/scripts/down-local.sh" >/dev/null 2>&1 || true
}
trap cleanup EXIT

"${ROOT_DIR}/scripts/up-local.sh" >/dev/null

HEALTH_PAYLOAD="$(curl -fsS "http://127.0.0.1:${BACK_PORT}/health")"
echo "${HEALTH_PAYLOAD}" | grep -q '"status":"ok"'

CARDS_PAYLOAD="$(curl -fsS -X POST "http://127.0.0.1:${BACK_PORT}/cards?caso_de_uso=hipotecas" -H 'content-type: application/json' -d '{"timeRange":"24h"}')"
echo "${CARDS_PAYLOAD}" | grep -q '"cards"'

DASHBOARD_PAYLOAD="$(curl -fsS -X POST "http://127.0.0.1:${BACK_PORT}/dashboard?caso_de_uso=prestamos" -H 'content-type: application/json' -d '{"timeRange":"24h"}')"
echo "${DASHBOARD_PAYLOAD}" | grep -q '"table"'
echo "${DASHBOARD_PAYLOAD}" | grep -q '"rows"'

DETAIL_PAYLOAD="$(curl -fsS -X POST "http://127.0.0.1:${BACK_PORT}/dashboard_detail?caso_de_uso=hipotecas&id=conv-001" -H 'content-type: application/json' -d '{"timeRange":"24h"}')"
echo "${DETAIL_PAYLOAD}" | grep -q '"left"'
echo "${DETAIL_PAYLOAD}" | grep -q '"right"'

UNKNOWN_BODY_FILE="$(mktemp)"
UNKNOWN_CODE="$(
  curl -sS -o "${UNKNOWN_BODY_FILE}" -w '%{http_code}' \
    -X POST "http://127.0.0.1:${BACK_PORT}/cards?caso_de_uso=no_existe" \
    -H 'content-type: application/json' -d '{"timeRange":"24h"}'
)"
[ "${UNKNOWN_CODE}" = "404" ]
grep -q '"code":"UNKNOWN_USE_CASE"' "${UNKNOWN_BODY_FILE}"
rm -f "${UNKNOWN_BODY_FILE}"

FRONT_BODY_FILE="$(mktemp)"
FRONT_CODE="$(
  curl -sS -o "${FRONT_BODY_FILE}" -w '%{http_code}' \
    "http://127.0.0.1:${FRONT_PORT}/monitor?caso_de_uso=hipotecas"
)"
[ "${FRONT_CODE}" = "200" ]
grep -q '<div id="root"></div>' "${FRONT_BODY_FILE}"
rm -f "${FRONT_BODY_FILE}"

echo "Smoke local OK"
