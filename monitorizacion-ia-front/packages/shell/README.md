# monitorizacion-ia-front / shell (monitor-only)

Frontend reducido a `MonitorDashboard` con ruta única:

- `http://localhost:3100/monitor?caso_de_uso=hipotecas`

En `home /monitor` los sistemas habilitados se cargan como tabs navegables.

## Requisitos

- Node 18+

## Instalación local (sin registry privado)

```bash
cd packages/shell
npm install --workspaces=false
```

## Ejecución

```bash
cd packages/shell
npm run start
```

`npm run start` usa el perfil local (`.env.mock`) y no requiere dependencias corporativas.

## Perfiles de entorno

### Local (default)

Archivo: `.env.mock`

- `MONITOR_PROFILE=local`
- `PORT_NUMBER=3100`
- `MONITOR_API_BASE_URL=http://localhost:8002`
- `REACT_APP_MONITOR_MOCK_MODE=false` (usa backend orquestador local)

### Corporativo (preservado)

Archivos: `.env.development`, `.env.integration`, `.env.preproduction`, `.env.production`

- Mantienen variables corporativas legacy (auth/hosts/client ids) para retomarlas en fases futuras.
- Incluyen `MONITOR_PROFILE=corporate`.
- No se usan por defecto en arranque local.

## Conmutación de perfil

```bash
cd packages/shell
npm run start                    # local (default)
npm run start:development        # corporativo development
npm run start:integration        # corporativo integration
npm run start:production         # corporativo production
```

## Vista configurable por query param

- `vista=operativa` (default)
- `vista=supervision`
- `vista=ejecutiva`

Ejemplo:

```bash
http://127.0.0.1:3100/monitor?caso_de_uso=prestamos&vista=supervision&timeRange=7d&search=Pendiente&limit=10
```
