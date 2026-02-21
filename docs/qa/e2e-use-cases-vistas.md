# Casos de uso E2E (sistemas + vistas)

## Objetivo
- Validar `home /monitor` con todos los sistemas navegables por tabs.
- Validar configuración de `vista` (composición/estética de componentes) sin romper contrato backend global.
- Validar envío de query params de negocio (`timeRange`, `search`, `limit`) al orquestador.

## Configuración de vistas
- Archivo: `monitorizacion-ia-front/packages/shell/src/shared/config/views.json`
- Resolver: `monitorizacion-ia-front/packages/shell/src/shared/config/views.ts`
- Vistas incluidas:
  - `operativa`
  - `supervision`
  - `ejecutiva`

Cada vista define:
- `pageTitle`, `description`
- `theme` (background/border/accent/text)
- `cards` (columnas, subtitulo, alias de titulo)

## Casos E2E preparados
1. `hipotecas + operativa`
   - URL: `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas&vista=operativa&timeRange=24h&limit=25`
   - Payload backend: `{"timeRange":"24h","limit":25}`
2. `prestamos + supervision`
   - URL: `http://127.0.0.1:3100/monitor?caso_de_uso=prestamos&vista=supervision&timeRange=7d&search=Pendiente&limit=10`
   - Payload backend: `{"timeRange":"7d","search":"Pendiente","limit":10}`
3. `hipotecas + ejecutiva`
   - URL: `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas&vista=ejecutiva&timeRange=30d&search=Ana&limit=5`
   - Payload backend: `{"timeRange":"30d","search":"Ana","limit":5}`

## Ejecución automática

```bash
cd /Users/usuario/personal/monitorizacion-ia
./scripts/e2e-cases-local.sh
```

## Criterio de éxito
- Respuesta 200 de frontend para cada URL de caso.
- `/cards`, `/dashboard`, `/dashboard_detail` responden payload válido para cada caso.
- Salida final del script: `E2E cases local OK`.
