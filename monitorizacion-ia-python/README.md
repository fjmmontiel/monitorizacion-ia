# monitorizacion-ia-python

Backend orquestador del monitor. Expone una API FastAPI que decide:
- que sistemas estan disponibles
- que vista declarativa usa cada sistema
- si los datos salen de JSON local (`native`) o de un upstream HTTP (`http_proxy`)

La shell frontend no conoce los sistemas ni layouts por adelantado; todo sale de este servicio.

## Responsabilidades
- Servir contratos de UI para Home y monitor.
- Resolver `cards`, `dashboard` y `dashboard_detail` por `caso_de_uso`.
- Persistir y administrar `ViewConfiguration` en runtime.
- Exponer un inventario DatOps de sistemas activos.
- Registrar metricas y logs por request con `request_id`.

## Endpoints principales
### Salud y observabilidad
- `GET /health`: estado del servicio, nombre y version.
- `GET /metrics`: snapshot de metricas in-memory.

### Operacion del monitor
- `POST /cards?caso_de_uso=<id>`: KPIs de cabecera.
- `POST /dashboard?caso_de_uso=<id>`: tabla principal.
- `POST /dashboard_detail?caso_de_uso=<id>&id=<row_id>`: detalle de una fila.

Las tres operaciones aceptan `QueryRequest` con:
- `timeRange`
- `filters`
- `search`
- `sort`
- `cursor`
- `limit`

### Contratos para frontend
- `GET /ui/shell`: devuelve Home, sistemas y `ViewConfiguration` activa.
- `GET /datops/overview`: inventario operativo con adapter, timeout y rutas efectivas por sistema.

### Admin de vistas
- `GET /admin/view-configs`
- `GET /admin/view-configs/{view_id}`
- `POST /admin/view-configs`
- `PUT /admin/view-configs/{view_id}`
- `DELETE /admin/view-configs/{view_id}`

Las operaciones mutantes aplican rate limit in-memory por cliente.

## Contratos soportados
### `ViewConfiguration`
- `id`, `name`, `system`, `enabled`
- `runtime` opcional con `adapter=http_proxy` y `upstream_base_url`
- `components`: arbol declarativo de componentes

### Tipos de componente soportados
- `cards`
- `table`
- `detail`
- `chart`
- `text`
- `stack`
- `split`

### Reglas validadas
- Maximo `20` componentes por vista.
- Maximo `8` componentes por tipo.
- Profundidad maxima `4`.
- IDs de componente unicos.
- `stack` y `split` requieren `children`.
- Cada tipo solo admite sus `data_source` permitidos.

## Adapters de datos
### `native`
- Implementado en [src/orchestrator/adapters/native.py](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/adapters/native.py).
- Lee `cards.json`, `dashboard.json` y `dashboard_detail.json` desde `src/orchestrator/data/<caso_de_uso>/`.
- Valida cada payload con Pydantic antes de devolverlo.

### `http_proxy`
- Implementado en [src/orchestrator/adapters/http_proxy.py](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/adapters/http_proxy.py).
- Reenvia `POST` al upstream configurado en la vista.
- Propaga timeout y transforma errores de red en `UPSTREAM_TIMEOUT` o `UPSTREAM_ERROR`.

## Configuracion relevante
- [src/orchestrator/config/use_cases.yaml](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/config/use_cases.yaml): catalogo sincronizado de sistemas.
- [src/orchestrator/config/view_configs.json](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/config/view_configs.json): vistas persistidas que realmente habilitan sistemas en runtime.
- [src/orchestrator/data](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/data): payloads mock por caso de uso.
- [src/orchestrator/contracts/v1](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/contracts/v1): esquemas JSON versionados.

## Variables de entorno
- `ENVIRONMENT`: perfil del backend.
- `PROJECT_NAME`: nombre expuesto en `/health`.
- `PROJECT_VERSION`: version expuesta en `/health`.
- `VIEW_CONFIG_STORAGE_PATH`: ruta del JSON persistido de vistas.
- `UPSTREAM_TIMEOUT_MS`: timeout por defecto de llamadas a upstream.
- `UPSTREAM_LIMIT_DEFAULT`: limite default para consultas.
- `UPSTREAM_LIMIT_MAX`: limite maximo permitido.
- `ADMIN_RATE_LIMIT_REQUESTS`: maximo de llamadas admin en ventana.
- `ADMIN_RATE_LIMIT_WINDOW_SECONDS`: ventana del rate limit.

## Arranque local
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
uvicorn src.main:app --port 8002
```

Con el repositorio completo, el flujo normal es:
```bash
cd /Users/usuario/personal/monitorizacion-ia
make run
```

## Uso desde frontend
El frontend llama a:
- `GET /ui/shell` al cargar Home o monitor.
- `POST /cards`, `POST /dashboard` al entrar en un sistema.
- `POST /dashboard_detail` al abrir una fila de tabla.
- `GET/POST/PUT/DELETE /admin/view-configs` desde la pantalla `/admin`.

Si una vista define `runtime.http_proxy`, el frontend no cambia nada: este servicio sigue siendo el punto unico de entrada.

## Como extenderlo
### Nuevo sistema con mock local
1. Crea `src/orchestrator/data/<nuevo>/cards.json`.
2. Crea `src/orchestrator/data/<nuevo>/dashboard.json`.
3. Crea `src/orchestrator/data/<nuevo>/dashboard_detail.json`.
4. Da de alta una vista para `system=<nuevo>` en `view_configs.json` o via `/admin`.
5. Si quieres sincronizar catalogo compartido, actualiza `config/catalog/monitor_catalog.json` desde la raiz y ejecuta `make sync-config`.

### Nuevo sistema con backend remoto
1. Crea una `ViewConfiguration` con `runtime.adapter=http_proxy`.
2. Define `runtime.upstream_base_url`.
3. Asegura que el upstream responde con los mismos contratos de `cards`, `dashboard` y `dashboard_detail`.

### Nueva forma de validacion
- Extiende [src/orchestrator/api/schemas.py](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/api/schemas.py) si cambian contratos o restricciones.
- Mantiene la compatibilidad con [src/orchestrator/api/routes.py](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/api/routes.py).

## Tests
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python
source .venv/bin/activate
pytest -q
```

Cobertura actual por tipos de prueba:
- smoke del orquestador
- adapters
- validacion de `use_case_loader`
- persistencia de `view_config_store`

## Logs y diagnostico
- Cada request genera `x-request-id`.
- El middleware registra metodo, path, status, latencia, `caso_de_uso` y adapter activo.
- En ejecucion local integrada, el log runtime queda en `../logs/fase-ejecucion-local/runtime/back.log`.

## Referencias
- [README raiz](/Users/usuario/personal/monitorizacion-ia/README.md)
- [docs/uso-y-extension.md](/Users/usuario/personal/monitorizacion-ia/docs/uso-y-extension.md)
