# Monitorizacion IA

Repositorio de referencia para un monitor declarativo de operaciones IA.

La solucion esta separada en dos piezas runtime:
- un backend FastAPI que orquesta datos, vistas y routing por `caso_de_uso`
- un frontend React que consume `GET /ui/shell` y renderiza Home, monitor y admin sin hardcodes por sistema

La idea central es simple: el backend decide que sistemas existen, que vista tiene cada uno y de donde salen los datos; el frontend solo interpreta ese contrato y lo pinta.

## Microservicios y paquetes
- [Backend orquestador](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/README.md): API FastAPI con adapters `native` y `http_proxy`, configuracion de vistas y mocks locales.
- [Frontend monorepo](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/README.md): workspace con la shell runtime, libreria compartida y soporte de Cypress.
- [Shell frontend](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/README.md): aplicacion React que renderiza `/home`, `/monitor` y `/admin`.

## Que soporta hoy
- Navegacion dinamica por sistemas desde backend.
- Vistas declarativas persistidas en JSON y editables en runtime desde `/admin`.
- Resolucion de datos por `caso_de_uso` mediante mock local (`native`) o proxy HTTP (`http_proxy`).
- Componentes de vista soportados: `cards`, `table`, `detail`, `chart`, `text`, `stack`, `split`.
- Inventario DatOps para descubrir sistemas, adapter activo, timeout y rutas operativas.
- Filtros de monitor por query string (`timeRange`, `search`, `limit`, `gestor`, `telefono_cliente`, `resolucion`, `fecha`).

## Flujo funcional
1. El frontend carga `GET /ui/shell`.
2. El backend devuelve Home, sistemas disponibles y la `ViewConfiguration` activa de cada sistema.
3. Al entrar en `/monitor?caso_de_uso=<id>`, la shell llama a `/cards`, `/dashboard` y `/dashboard_detail`.
4. El backend resuelve cada operacion con `NativeAdapter` (JSON local) o `HttpProxyAdapter` (upstream).
5. La vista se compone en cliente segun el arbol de componentes recibido.

## Fuentes de verdad
- Catalogo generable: [config/catalog/monitor_catalog.json](/Users/usuario/personal/monitorizacion-ia/config/catalog/monitor_catalog.json)
- Casos de uso backend: [monitorizacion-ia-python/src/orchestrator/config/use_cases.yaml](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/config/use_cases.yaml)
- Vistas persistidas en runtime: [monitorizacion-ia-python/src/orchestrator/config/view_configs.json](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/config/view_configs.json)
- Datos mock locales: [monitorizacion-ia-python/src/orchestrator/data](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/data)
- Configuracion derivada en frontend: [monitorizacion-ia-front/packages/shell/src/shared/config](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/src/shared/config)

## Sistemas y vistas incluidas
- Sistemas visibles por vista habilitada: `hipotecas`, `prestamos`, `seguros`.
- Catalogo sincronizado actualmente: `hipotecas` y `prestamos`.
- Vista base habilitada: `operativa`.

`seguros` ya tiene mocks y una vista activa en `view_configs.json`, aunque no forma parte del catalogo generado por [scripts/catalog_manager.py](/Users/usuario/personal/monitorizacion-ia/scripts/catalog_manager.py).

## Arranque local
```bash
cd /Users/usuario/personal/monitorizacion-ia
make run
```

Comandos utiles:
- `make install`: instala backend y frontend local.
- `make sync-config`: regenera config de backend y frontend desde el catalogo.
- `make up`: levanta backend y shell sin reinstalar.
- `make stop`: para ambos procesos.
- `make logs`: muestra logs runtime.
- `make show-config`: lista sistemas, vistas y URL base de ejemplo.

## URLs locales
- Home: `http://127.0.0.1:3100/home`
- Monitor: `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas`
- Admin: `http://127.0.0.1:3100/admin`
- Backend health: `http://127.0.0.1:8002/health`
- UI shell contract: `http://127.0.0.1:8002/ui/shell`
- DatOps overview: `http://127.0.0.1:8002/datops/overview`

## Desarrollo y extension
### Anadir un sistema
1. Registra el sistema en [config/catalog/monitor_catalog.json](/Users/usuario/personal/monitorizacion-ia/config/catalog/monitor_catalog.json) o usa `make add-system`.
2. Ejecuta `make sync-config`.
3. Crea `cards.json`, `dashboard.json` y `dashboard_detail.json` en `monitorizacion-ia-python/src/orchestrator/data/<nuevo>/`.
4. Crea o habilita una vista para ese `caso_de_uso` en `/admin` o en `view_configs.json`.
5. Verifica que aparece una nueva pestaña en `/home` y carga en `/monitor`.

### Anadir o cambiar una vista
- Edita [monitorizacion-ia-python/src/orchestrator/config/view_configs.json](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/config/view_configs.json) o usa `/admin`.
- Mantiene el contrato `ViewConfiguration` del backend.
- Usa `stack` y `split` para composicion; usa `cards`, `table`, `text`, `chart` y `detail` como nodos de negocio.

### Cambiar el origen de datos
- `native`: lee JSON local desde `data/<caso_de_uso>/`.
- `http_proxy`: la vista define `runtime.upstream_base_url` y el backend reenvia las llamadas.

## Verificacion recomendada
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python
source .venv/bin/activate && pytest -q
```

```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front
npm run typecheck
```

```bash
cd /Users/usuario/personal/monitorizacion-ia
make smoke
make e2e
```

## Logs
- Front runtime: `logs/fase-ejecucion-local/runtime/front.log`
- Back runtime: `logs/fase-ejecucion-local/runtime/back.log`

## Documentacion complementaria
- Ejecucion local: [docs/run/local.md](/Users/usuario/personal/monitorizacion-ia/docs/run/local.md)
- Uso y extension: [docs/uso-y-extension.md](/Users/usuario/personal/monitorizacion-ia/docs/uso-y-extension.md)
