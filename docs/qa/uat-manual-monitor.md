# UAT manual monitor (checklist corta)

Precondición:
- Stack levantado con `./scripts/up-local.sh`.
- Abrir `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas`.

## Checklist
1. Vista inicial:
   - Se ve título `Monitor dashboard`.
   - Se renderizan cards y tabla sin error.
2. Cambio de caso de uso:
   - Cambiar selector a `Prestamos`.
   - La URL queda con `caso_de_uso=prestamos`.
   - Se recargan cards/tabla.
3. Filtro en tabla:
   - Escribir un valor en un filtro visible.
   - La tabla se actualiza sin romper render.
4. Ordenación:
   - Pulsar `Ordenar` sobre una columna sortable.
   - La query se actualiza y la tabla se refresca.
5. Detalle:
   - Pulsar `Ver detalle` en una fila.
   - Aparece panel de detalle con bloques `left`/`right`.
   - Pulsar `Cerrar` y comprobar que se oculta.
6. Error controlado backend:
   - Abrir `/monitor?caso_de_uso=no_existe`.
   - La UI no se cae; muestra error controlado.

## Resultado esperado
- Flujo estable de monitor (`cards + tabla + detalle`) para `hipotecas` y `prestamos`.
