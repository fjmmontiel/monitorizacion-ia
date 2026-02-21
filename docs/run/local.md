# Ejecución local end-to-end

## Requisitos
- Python virtualenv preparado en `monitorizacion-ia-python/.venv`.
- Dependencias instaladas en `monitorizacion-ia-front/packages/shell/node_modules`.
- Puertos libres por defecto:
  - Front: `3100`
  - Back: `8002`

## Arranque de toda la app

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/up-local.sh
```

## Arranque unificado con Make

```bash
cd /Users/usuario/personal/monitorizacion-ia
make run
```

`make run` ejecuta:
- creación/uso de `monitorizacion-ia-python/.venv`
- instalación backend (`pip install -e ".[dev]"`)
- instalación frontend shell (`npm install --workspaces=false`)
- arranque backend + frontend
- impresión de sistemas habilitados

URLs:
- Front Home: `http://127.0.0.1:3100/home`
- Front Monitor: `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas`
- Back: `http://127.0.0.1:8002/health`
- DatOps mock overview: `http://127.0.0.1:8002/datops/overview`

En `home` los sistemas configurados quedan cargados como tabs y se puede navegar al monitor.

En `monitor` el layout operativo queda fijo en este orden:
- cards (arriba)
- tabla (debajo)
- detalle de fila en modal pop-up (al pulsar `Ver detalle`)

Para entorno local se activa fallback mock del frontend:
- `REACT_APP_MONITOR_FAILOVER_TO_MOCK=true` en `monitorizacion-ia-front/packages/shell/.env.mock`

## Parada

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/down-local.sh
```

Con Make:

```bash
cd /Users/usuario/personal/monitorizacion-ia
make stop
```

## Smoke rápido

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/smoke-local.sh
```

## E2E multi-configuración (sistema)

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/e2e-cases-local.sh
```

Con Make:

```bash
cd /Users/usuario/personal/monitorizacion-ia
make e2e
```

## Otros comandos Make útiles

```bash
make status
make logs
make smoke
make show-config
```

## Logs runtime
- Front: `logs/fase-ejecucion-local/runtime/front.log`
- Back: `logs/fase-ejecucion-local/runtime/back.log`
