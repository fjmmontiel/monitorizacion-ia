#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACK_DIR="${ROOT_DIR}/monitorizacion-ia-python"
FRONT_SHELL_DIR="${ROOT_DIR}/monitorizacion-ia-front/packages/shell"

python3 -m venv "${BACK_DIR}/.venv"
source "${BACK_DIR}/.venv/bin/activate"
pip install -U pip
pip install -e "${BACK_DIR}[dev]"

cd "${FRONT_SHELL_DIR}"
npm install --workspaces=false

echo "Entorno local listo: backend venv + frontend shell dependencias instaladas."
