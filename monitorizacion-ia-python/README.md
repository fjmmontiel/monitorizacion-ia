# monitorizacion-ia-python (Orquestador)

Backend orientado a orquestación por `caso_de_uso` con endpoints canónicos:

- `POST /cards?caso_de_uso=...`
- `POST /dashboard?caso_de_uso=...`
- `POST /dashboard_detail?caso_de_uso=...&id=...`
- `GET /health`

## Requisitos

- Python 3.11+

## Instalación rápida

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

## Configuración

Variables mínimas:

- `ENVIRONMENT`
- `PROJECT_NAME`
- `PROJECT_VERSION`
- `ORCH_CONFIG_PATH` (por defecto `src/orchestrator/config/dev.yaml`)
- `UPSTREAM_TIMEOUT_MS`

Configuraciones por entorno disponibles:

- `src/orchestrator/config/dev.yaml`
- `src/orchestrator/config/stg.yaml`
- `src/orchestrator/config/prod.yaml`

### Perfiles duales (local/corporativo)

- **Local (default):**
  - `ORCH_CONFIG_PATH=src/orchestrator/config/dev.yaml`
  - Use cases `hipotecas` y `prestamos` con adapter `native`.
  - No requiere credenciales ni middleware corporativo.
- **Corporativo preservado:**
  - `ORCH_CONFIG_PATH=src/orchestrator/config/stg.yaml` o `src/orchestrator/config/prod.yaml`.
  - Routing `http_proxy` para recuperar integración corporativa en fases futuras.
  - En esta fase se preserva el contrato y la configuración, no se reactiva autenticación corporativa en runtime.

Ejemplo de `use_cases.yaml`:

```yaml
use_cases:
  hipotecas:
    adapter: native
  prestamos:
    adapter: native
  piloto_proxy:
    adapter: http_proxy
    upstream:
      base_url: http://localhost:9000
      routes:
        cards: /cards
        dashboard: /dashboard
        dashboard_detail: /dashboard_detail/{id}
```

## Ejecución

```bash
uvicorn src.main:app --reload --port 8002
```

Ejemplos por perfil:

```bash
# Local (default)
ORCH_CONFIG_PATH=src/orchestrator/config/dev.yaml uvicorn src.main:app --reload --port 8002

# Corporativo STG (preservado)
ORCH_CONFIG_PATH=src/orchestrator/config/stg.yaml uvicorn src.main:app --reload --port 8002
```

## Curl de ejemplo

```bash
curl -X POST 'http://localhost:8002/cards?caso_de_uso=hipotecas' \
  -H 'content-type: application/json' \
  -d '{"timeRange": "24h"}'
```

## Tests

```bash
pytest -q
```
