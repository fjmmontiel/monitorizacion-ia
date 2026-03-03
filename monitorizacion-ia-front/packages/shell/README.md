# packages/shell

Aplicacion React del monitor. Es la shell que un desarrollador ejecuta para navegar por:
- `/home`
- `/monitor`
- `/admin`

No define sistemas, vistas ni payloads en duro como fuente de verdad. Su responsabilidad es interpretar el contrato que expone el backend y renderizar la experiencia.

## Rutas runtime
- `/home`: landing con tabs dinamicas, resumen de sistemas y vista DatOps.
- `/monitor?caso_de_uso=<id>`: panel principal del sistema seleccionado.
- `/admin`: alta, edicion y borrado de `ViewConfiguration` en runtime.
- `/` y rutas desconocidas redirigen a `/home`.

## Que soporta funcionalmente
### Home
- Carga `GET /ui/shell`.
- Carga `GET /datops/overview`.
- Muestra tabs dinamicas por sistema.
- Permite abrir el sistema por defecto sin conocerlo por adelantado.

### Monitor
- Lee `caso_de_uso` y filtros desde query string.
- Dispara `POST /cards`, `POST /dashboard` y `POST /dashboard_detail`.
- Mantiene filtros sincronizados con la URL.
- Permite abrir detalle desde la tabla.
- Renderiza layouts declarativos con componentes anidados.

### Admin
- Lista vistas persistidas.
- Crea, actualiza y elimina vistas.
- Genera una vista base automaticamente para un sistema.
- Permite activar `http_proxy` y guardar `upstream_base_url`.
- Incluye editor JSON completo y constructor rapido de componentes.

## Componentes declarativos interpretados
- `cards`: grid de KPIs.
- `table`: tabla dinamica con accion de detalle.
- `text`: bloque de texto simple desde `config.text`.
- `chart`: placeholder visual configurable por contrato.
- `detail`: reserva funcional para detalle.
- `stack`: contenedor vertical.
- `split`: contenedor en columnas.

El detalle renderiza dos zonas logicas a partir de `DashboardDetailResponse`:
- conversacion (`left.messages`)
- paneles de datos (`right`)

## Integracion con el backend
La capa de integracion vive en [src/shared/api/MonitorApi.ts](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/src/shared/api/MonitorApi.ts).

Hace lo siguiente:
- valida entradas con Zod
- monta URLs con `MONITOR_API_BASE_URL`
- aplica timeout cliente de 10 segundos
- normaliza errores backend a `MonitorApiError`
- valida respuestas con esquemas Zod antes de pintarlas

## Configuracion de entorno
Variables clave:
- `PORT_NUMBER`: puerto del dev server.
- `MONITOR_API_BASE_URL`: base URL del backend.
- `REACT_APP_MONITOR_MOCK_MODE`: activa modo mock de cliente.
- `REACT_APP_MONITOR_FAILOVER_TO_MOCK`: fallback a mocks si falla backend.
- `REACT_APP_ENABLE_STRICT_MODE`: activa `StrictMode`.

Perfiles disponibles:
- `.env.mock`
- `.env.development`
- `.env.integration`
- `.env.preproduction`
- `.env.production`

## Estructura util para desarrollar
- [src/router/router.tsx](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/src/router/router.tsx): rutas de la app.
- [src/features/home](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/src/features/home): landing y resumen.
- [src/features/monitor](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/src/features/monitor): pagina principal, cards, tabla y detalle.
- [src/features/admin](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/src/features/admin): consola de configuracion de vistas.
- [src/shared/contracts](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell/src/shared/contracts/monitor.contracts.ts): contrato tipado frontend.

## Arranque local
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell
npm install --workspaces=false
npm run start
```

Otros comandos:
```bash
npm run start:development
npm run start:integration
npm run start:production
npm run build
npm run build:development
npm run typecheck
```

Con el stack completo:
```bash
cd /Users/usuario/personal/monitorizacion-ia
make run
```

## Como extenderla sin romper el modelo
### Nuevo caso de uso
No anadas una pagina nueva. El camino correcto es:
1. Dar de alta el sistema y sus datos en backend.
2. Crear o habilitar una `ViewConfiguration`.
3. Verificar que aparece solo en `/home` y abre `/monitor`.

### Nueva composicion visual
- Prioriza cambios en la configuracion de la vista backend.
- Añade logica de render solo si aparece un nuevo tipo de componente o un nuevo comportamiento transversal.

### Nuevo contrato de API
- Ajusta los esquemas Zod en `src/shared/contracts/monitor.contracts.ts`.
- Mantiene alineado `MonitorApi.ts` con el backend.
- Revisa el impacto en `Home.page.tsx`, `MonitorDashboard.page.tsx` y `AdminViews.page.tsx`.

## Verificacion recomendada
```bash
cd /Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-front/packages/shell
npm run typecheck
```

```bash
cd /Users/usuario/personal/monitorizacion-ia
make smoke
make e2e
```

## Referencias
- [README raiz](/Users/usuario/personal/monitorizacion-ia/README.md)
- [docs/uso-y-extension.md](/Users/usuario/personal/monitorizacion-ia/docs/uso-y-extension.md)
