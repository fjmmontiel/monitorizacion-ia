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

URLs:
- Front: `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas`
- Back: `http://127.0.0.1:8002/health`

En `home /monitor` los sistemas configurados quedan cargados como tabs y se puede navegar entre ellos.

## Parada

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/down-local.sh
```

## Smoke rápido

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/smoke-local.sh
```

## E2E multi-configuración (sistema + vista)

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/e2e-cases-local.sh
```

## Logs runtime
- Front: `logs/fase-ejecucion-local/runtime/front.log`
- Back: `logs/fase-ejecucion-local/runtime/back.log`
