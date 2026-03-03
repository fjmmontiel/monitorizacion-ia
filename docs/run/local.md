# Ejecución local

## Arranque

```bash
cd /Users/usuario/personal/monitorizacion-ia
make run
```

Alternativas:

```bash
./scripts/up-local.sh
./scripts/down-local.sh
```

## URLs
- Front: `http://127.0.0.1:3100/home`
- Monitor: `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas`
- Back: `http://127.0.0.1:8002/health`
- UI Shell: `http://127.0.0.1:8002/ui/shell`

## Comprobación rápida

```bash
cd /Users/usuario/personal/monitorizacion-ia
make smoke
make e2e
```

## Logs
- Front: `logs/fase-ejecucion-local/runtime/front.log`
- Back: `logs/fase-ejecucion-local/runtime/back.log`

## Más detalle
- [docs/uso-y-extension.md](/Users/usuario/personal/monitorizacion-ia/docs/uso-y-extension.md)
