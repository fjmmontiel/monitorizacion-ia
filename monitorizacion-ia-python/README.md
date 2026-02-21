# monitorizacion-ia-python (Orquestador)

Backend orientado a orquestación por `caso_de_uso` con endpoints canónicos:

- `POST /cards?caso_de_uso=...`
- `POST /dashboard?caso_de_uso=...`
- `POST /dashboard_detail?caso_de_uso=...`
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
- `ORCH_CONFIG_PATH` (por defecto `src/orchestrator/config/use_cases.yaml`)
- `UPSTREAM_TIMEOUT_MS`

Ejemplo de `use_cases.yaml`:

```yaml
use_cases:
  piloto_native:
    adapter: native
  piloto_proxy:
    adapter: http_proxy
    upstream:
      base_url: http://localhost:9000
      routes:
        cards: /cards
        dashboard: /dashboard
        dashboard_detail: /dashboard_detail
```

## Ejecución

```bash
uvicorn src.main:app --reload --port 8002
```

## Curl de ejemplo

```bash
curl -X POST 'http://localhost:8002/cards?caso_de_uso=piloto_native' \
  -H 'content-type: application/json' \
  -d '{"query": {"limit": 10}}'
```

## Tests

```bash
pytest -q
```
