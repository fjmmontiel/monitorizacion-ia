#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

require_cmd curl
require_cmd lsof
require_cmd npm

BACK_PID="$(read_pid_file "${BACK_PID_FILE}")"
if [ -n "${BACK_PID}" ] && is_pid_alive "${BACK_PID}"; then
  echo "Backend already running (pid=${BACK_PID})"
else
  if is_port_listening "${BACK_PORT}"; then
    echo "Port ${BACK_PORT} is already in use by pid $(listener_pid "${BACK_PORT}")" >&2
    exit 1
  fi
  echo "Starting backend on port ${BACK_PORT}"
  start_backend
fi

if ! wait_http_ok "http://127.0.0.1:${BACK_PORT}/health"; then
  echo "Backend did not become healthy on port ${BACK_PORT}" >&2
  tail -n 50 "${BACK_LOG_FILE}" || true
  exit 1
fi

FRONT_PID="$(read_pid_file "${FRONT_PID_FILE}")"
if [ -n "${FRONT_PID}" ] && is_pid_alive "${FRONT_PID}"; then
  echo "Frontend already running (pid=${FRONT_PID})"
else
  if is_port_listening "${FRONT_PORT}"; then
    echo "Port ${FRONT_PORT} is already in use by pid $(listener_pid "${FRONT_PORT}")" >&2
    exit 1
  fi
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
