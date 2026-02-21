# Smoke local (automatizado)

Script: `/Users/usuario/personal/monitorizacion-ia/scripts/smoke-local.sh`

## Qué valida
1. Arranque coordinado de backend y frontend local.
2. `GET /health` devuelve `status=ok`.
3. `POST /cards?caso_de_uso=hipotecas` devuelve payload con `cards`.
4. `POST /dashboard?caso_de_uso=prestamos` devuelve `table` y `rows`.
5. `POST /dashboard_detail?caso_de_uso=hipotecas&id=conv-001` devuelve `left` y `right`.
6. `caso_de_uso` inválido devuelve `404` + `UNKNOWN_USE_CASE`.
7. La ruta FE `/monitor?caso_de_uso=hipotecas` responde `200` y contiene `#root`.

## Ejecución

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/smoke-local.sh
```

## Criterio de éxito
- Salida final: `Smoke local OK`.
- Código de salida: `0`.
