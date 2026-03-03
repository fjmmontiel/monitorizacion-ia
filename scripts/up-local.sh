#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_cmd curl
require_cmd npm

free_port "${BACK_PORT}" "backend"
rm -f "${BACK_PID_FILE}"

BACK_PID="$(read_pid_file "${BACK_PID_FILE}")"
if [ -n "${BACK_PID}" ] && is_pid_alive "${BACK_PID}"; then
  echo "Backend already running (pid=${BACK_PID})"
else
  echo "Starting backend on port ${BACK_PORT}"
  start_backend
fi

if ! wait_http_ok "http://127.0.0.1:${BACK_PORT}/health"; then
  echo "Backend did not become healthy on port ${BACK_PORT}" >&2
  tail -n 50 "${BACK_LOG_FILE}" || true
  exit 1
fi

free_port "${FRONT_PORT}" "frontend"
rm -f "${FRONT_PID_FILE}"

FRONT_PID="$(read_pid_file "${FRONT_PID_FILE}")"
if [ -n "${FRONT_PID}" ] && is_pid_alive "${FRONT_PID}"; then
  echo "Frontend already running (pid=${FRONT_PID})"
else
  echo "Starting frontend on port ${FRONT_PORT}"
  start_front
fi

if ! wait_http_ok "http://127.0.0.1:${FRONT_PORT}/monitor?caso_de_uso=hipotecas"; then
  echo "Frontend did not become reachable on port ${FRONT_PORT}" >&2
  tail -n 50 "${FRONT_LOG_FILE}" || true
  exit 1
fi

echo "Stack up:"
echo "- Frontend: http://127.0.0.1:${FRONT_PORT}/monitor?caso_de_uso=hipotecas"
echo "- Backend:  http://127.0.0.1:${BACK_PORT}/health"
echo "- Front log: ${FRONT_LOG_FILE}"
echo "- Back log:  ${BACK_LOG_FILE}"
