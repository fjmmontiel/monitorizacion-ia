SHELL := /bin/bash

ROOT_DIR := $(CURDIR)
BACK_DIR := $(ROOT_DIR)/monitorizacion-ia-python
FRONT_SHELL_DIR := $(ROOT_DIR)/monitorizacion-ia-front/packages/shell
PY_VENV := $(BACK_DIR)/.venv

PYTHON ?= python3
FRONT_PORT ?= 3100
BACK_PORT ?= 8002
BACK_ORCH_CONFIG_PATH ?= src/orchestrator/config/dev.yaml

<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
.PHONY: help install install-back install-front setup-env sync-config add-system add-view run up stop restart status smoke e2e logs show-config
=======
.PHONY: help install install-back install-front setup-env run up stop restart status smoke e2e logs show-config
>>>>>>> theirs
=======
.PHONY: help install install-back install-front setup-env run up stop restart status smoke e2e logs show-config
>>>>>>> theirs
=======
.PHONY: help install install-back install-front setup-env run up stop restart status smoke e2e logs show-config
>>>>>>> theirs

help:
	@echo "Targets disponibles:"
	@echo "  make run      -> instala dependencias locales y levanta toda la app"
	@echo "  make install  -> instala backend (venv) + frontend shell"
	@echo "  make up       -> levanta backend + frontend"
	@echo "  make stop     -> para backend + frontend"
	@echo "  make restart  -> reinicia stack local"
	@echo "  make smoke    -> ejecuta smoke e2e minimo"
	@echo "  make e2e      -> ejecuta casos e2e multi-configuracion"
	@echo "  make status   -> estado de puertos/procesos"
	@echo "  make logs     -> tail de logs runtime"
	@echo "  make show-config -> muestra sistemas/vistas y urls de ejemplo"
	@echo "  make sync-config -> regenera config BE/FE desde config/catalog/monitor_catalog.json"
	@echo "  make add-system ARGS="--id nuevo --label Nuevo" -> alta automatizada de sistema"
	@echo "  make add-view ARGS="--id ejecutiva --label Ejecutiva" -> alta automatizada de vista"

install: install-back install-front

setup-env:
	@cd "$(ROOT_DIR)" && ./scripts/setup-local.sh

install-back:
	@test -d "$(PY_VENV)" || $(PYTHON) -m venv "$(PY_VENV)"
	@cd "$(BACK_DIR)" && source .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

install-front:
	@cd "$(FRONT_SHELL_DIR)" && npm install --workspaces=false

run: install sync-config up show-config
	@echo "Stack lista. Usa 'make logs' para ver runtime logs."

sync-config:
	@cd "$(ROOT_DIR)" && python3 scripts/catalog_manager.py sync

add-system:
	@cd "$(ROOT_DIR)" && python3 scripts/catalog_manager.py add-system $(ARGS)

add-view:
	@cd "$(ROOT_DIR)" && python3 scripts/catalog_manager.py add-view $(ARGS)

up:
	@cd "$(ROOT_DIR)" && FRONT_PORT="$(FRONT_PORT)" BACK_PORT="$(BACK_PORT)" BACK_ORCH_CONFIG_PATH="$(BACK_ORCH_CONFIG_PATH)" ./scripts/up-local.sh

stop:
	@cd "$(ROOT_DIR)" && FRONT_PORT="$(FRONT_PORT)" BACK_PORT="$(BACK_PORT)" ./scripts/down-local.sh

restart: stop up

smoke:
	@cd "$(ROOT_DIR)" && FRONT_PORT="$(FRONT_PORT)" BACK_PORT="$(BACK_PORT)" BACK_ORCH_CONFIG_PATH="$(BACK_ORCH_CONFIG_PATH)" ./scripts/smoke-local.sh

e2e:
	@cd "$(ROOT_DIR)" && FRONT_PORT="$(FRONT_PORT)" BACK_PORT="$(BACK_PORT)" BACK_ORCH_CONFIG_PATH="$(BACK_ORCH_CONFIG_PATH)" ./scripts/e2e-cases-local.sh

status:
	@echo "Estado de puertos:"
	@echo "--- FRONT ($(FRONT_PORT))"
	@lsof -nP -iTCP:$(FRONT_PORT) -sTCP:LISTEN | sed -n '1,20p' || true
	@echo "--- BACK ($(BACK_PORT))"
	@lsof -nP -iTCP:$(BACK_PORT) -sTCP:LISTEN | sed -n '1,20p' || true

logs:
	@echo "--- Front runtime log"
	@tail -n 80 "$(ROOT_DIR)/logs/fase-ejecucion-local/runtime/front.log" || true
	@echo "--- Back runtime log"
	@tail -n 80 "$(ROOT_DIR)/logs/fase-ejecucion-local/runtime/back.log" || true

show-config:
	@echo "Sistemas habilitados:"
	@node -e "const c=require('./monitorizacion-ia-front/packages/shell/src/shared/config/use_cases.json'); console.log(c.filter(x=>x.enabled).map(x=>'- '+x.id+' ('+x.label+')').join('\n'));"
	@echo "Vistas habilitadas:"
	@node -e "const v=require('./monitorizacion-ia-front/packages/shell/src/shared/config/views.json'); console.log(v.filter(x=>x.enabled).map(x=>'- '+x.id+' ('+x.label+')').join('\n'));"
	@echo "URL base monitor:"
	@echo "http://127.0.0.1:$(FRONT_PORT)/monitor?caso_de_uso=hipotecas&vista=operativa&timeRange=24h&limit=25"
