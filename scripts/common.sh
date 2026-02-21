#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_ROOT="${ROOT_DIR}/logs/fase-ejecucion-local"
RUNTIME_LOG_DIR="${LOG_ROOT}/runtime"
PID_DIR="${RUNTIME_LOG_DIR}/pids"

FRONT_DIR="${ROOT_DIR}/monitorizacion-ia-front/packages/shell"
BACK_DIR="${ROOT_DIR}/monitorizacion-ia-python"

FRONT_PORT="${FRONT_PORT:-3100}"
BACK_PORT="${BACK_PORT:-8002}"
BACK_ORCH_CONFIG_PATH="${BACK_ORCH_CONFIG_PATH:-src/orchestrator/config/dev.yaml}"

FRONT_PID_FILE="${PID_DIR}/front.pid"
BACK_PID_FILE="${PID_DIR}/back.pid"
FRONT_LOG_FILE="${RUNTIME_LOG_DIR}/front.log"
BACK_LOG_FILE="${RUNTIME_LOG_DIR}/back.log"

mkdir -p "${RUNTIME_LOG_DIR}" "${PID_DIR}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

is_pid_alive() {
  local pid="$1"
  kill -0 "${pid}" >/dev/null 2>&1
}

read_pid_file() {
  local pid_file="$1"
  if [ -f "${pid_file}" ]; then
    cat "${pid_file}"
  fi
}

is_port_listening() {
  local port="$1"
  lsof -nP -iTCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1
}

listener_pid() {
  local port="$1"
  lsof -nP -iTCP:"${port}" -sTCP:LISTEN -t 2>/dev/null | head -n 1
}

wait_http_ok() {
  local url="$1"
  local max_attempts="${2:-40}"
  local delay_seconds="${3:-1}"
  local attempt=1

  while [ "${attempt}" -le "${max_attempts}" ]; do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep "${delay_seconds}"
    attempt=$((attempt + 1))
  done

  return 1
}

start_backend() {
  bash -lc "cd '${BACK_DIR}' && source .venv/bin/activate && ORCH_CONFIG_PATH='${BACK_ORCH_CONFIG_PATH}' uvicorn src.main:app --port '${BACK_PORT}'" >"${BACK_LOG_FILE}" 2>&1 &
  echo $! > "${BACK_PID_FILE}"
}

start_front() {
  bash -lc "cd '${FRONT_DIR}' && PORT_NUMBER='${FRONT_PORT}' npm run start" >"${FRONT_LOG_FILE}" 2>&1 &
  echo $! > "${FRONT_PID_FILE}"
}

stop_by_pid_file() {
  local pid_file="$1"
  local service_name="$2"
  local pid

  pid="$(read_pid_file "${pid_file}")"
  if [ -z "${pid}" ]; then
    rm -f "${pid_file}"
    return 0
  fi

  if is_pid_alive "${pid}"; then
    pkill -TERM -P "${pid}" >/dev/null 2>&1 || true
    kill -TERM "${pid}" >/dev/null 2>&1 || true
    sleep 1
    if is_pid_alive "${pid}"; then
      pkill -KILL -P "${pid}" >/dev/null 2>&1 || true
      kill -9 "${pid}" >/dev/null 2>&1 || true
    fi
  fi

  rm -f "${pid_file}"
  echo "Stopped ${service_name} (pid=${pid})"
}
