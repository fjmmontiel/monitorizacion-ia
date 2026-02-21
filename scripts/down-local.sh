#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

stop_by_pid_file "${FRONT_PID_FILE}" "frontend"
stop_by_pid_file "${BACK_PID_FILE}" "backend"

if is_port_listening "${FRONT_PORT}"; then
  FRONT_RESIDUAL_PID="$(listener_pid "${FRONT_PORT}")"
  echo "Warning: port ${FRONT_PORT} still in use by pid ${FRONT_RESIDUAL_PID}. Forcing stop." >&2
  kill -TERM "${FRONT_RESIDUAL_PID}" >/dev/null 2>&1 || true
  sleep 1
  if is_port_listening "${FRONT_PORT}"; then
    kill -9 "${FRONT_RESIDUAL_PID}" >/dev/null 2>&1 || true
  fi
fi

if is_port_listening "${BACK_PORT}"; then
  BACK_RESIDUAL_PID="$(listener_pid "${BACK_PORT}")"
  echo "Warning: port ${BACK_PORT} still in use by pid ${BACK_RESIDUAL_PID}. Forcing stop." >&2
  kill -TERM "${BACK_RESIDUAL_PID}" >/dev/null 2>&1 || true
  sleep 1
  if is_port_listening "${BACK_PORT}"; then
    kill -9 "${BACK_RESIDUAL_PID}" >/dev/null 2>&1 || true
  fi
fi

echo "Stack down."
