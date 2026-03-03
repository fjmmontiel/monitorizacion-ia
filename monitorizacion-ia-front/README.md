# monitorizacion-ia-front

Monorepo frontend del monitor. Su objetivo es empaquetar la shell runtime y las piezas auxiliares para desarrollo, build y pruebas.

El runtime principal esta en `packages/shell`, pero el repositorio incluye tambien una libreria compartida y un workspace de Cypress.

## Estructura
- [packages/shell](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/README.md): aplicacion React que renderiza Home, monitor y admin.
- [packages/shared-library](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shared-library): utilidades compartidas entre paquetes; hoy expone hooks comunes.
- [cypress](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/cypress): soporte de pruebas E2E/funcionales del workspace.

## Que soporta este monorepo
- Workspaces npm para aislar paquetes.
- Orquestacion con `lerna` para ejecutar scripts por paquete.
- Build y start por perfiles (`development`, `integration`, `production` y variantes).
- Mock server local con Mockoon para escenarios funcionales y E2E del workspace.
- Predeploy que consolida el artefacto final partiendo de `packages/shell`.

## Requisitos
- Node `>=18`
- npm `>=8`

## Scripts principales
### Desarrollo
- `npm run start`: arranca todos los paquetes que implementan `start`.
- `npm run start:development`
- `npm run start:integration`
- `npm run start:production`
- `npm run start:mock`: levanta Mockoon y el runtime.

### Calidad
- `npm run typecheck`
- `npm run lint`
- `npm run test`
- `npm run complete-check`

### Build
- `npm run build`
- `npm run build:development`
- `npm run build:integration`
- `npm run build:production`
- `npm run predeploy`

### Testing con Cypress
- `npm run cypress:functional`
- `npm run cypress:e2e`
- `npm run cypress:report`

## Arranque como desarrollador
### Instalar dependencias del monorepo
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front
npm install
```

### Trabajar solo con la shell
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell
npm install --workspaces=false
npm run start
```

### Flujo integrado recomendado
```bash
cd /Users/usuario/personal/monitorizacion-ia
make run
```

## Como se integra con el backend
- La shell resuelve `MONITOR_API_BASE_URL` por entorno.
- Consume `GET /ui/shell` para descubrir sistemas y vistas.
- Consume `POST /cards`, `POST /dashboard` y `POST /dashboard_detail` para poblar el monitor.
- Consume `/admin/view-configs` para la consola administrativa.

La capa de API y contratos vive en `packages/shell/src/shared`.

## Perfiles y entornos
La shell incluye archivos `.env` para:
- `.env.mock`
- `.env.development`
- `.env.integration`
- `.env.preproduction`
- `.env.production`

`packages/shell` selecciona el perfil adecuado con `dotenv-cli` segun el script que ejecutes.

## Artefacto generado
- El build de `packages/shell` deja salida en `packages/shell/build`.
- `npm run predeploy` agrega los `build` de paquetes relevantes en un unico directorio `build/` del monorepo.

## Desarrollo de nuevos cambios
### Cambios en runtime
- Trabaja en `packages/shell`.
- Ajusta contratos en `packages/shell/src/shared/contracts`.
- Mantiene alineado el backend con el contrato JSON esperado.

### Cambios compartidos
- Publica utilidades comunes en `packages/shared-library`.
- Ejecuta `npm run typecheck` y, si aplica, `npm run test`.

### Cambios de configuracion declarativa
- El origen funcional esta en el backend.
- La shell interpreta configuracion; no debe duplicar catalogos ni vistas como fuente primaria.

## Verificacion recomendada
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front
npm run typecheck
```

```bash
cd /Users/usuario/personal/monitorizacion-ia
make smoke
make e2e
```

## Referencias
- [README raiz](/Users/usuario/personal/monitorizacion-ia/README.md)
- [README de packages/shell](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/README.md)
