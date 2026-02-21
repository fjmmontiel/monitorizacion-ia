# Scope cut FE (Fase 0)

## Se conserva
- `src/features/monitor/*` (MonitorDashboard + CardsGrid + DynamicTable + DashboardDetail).
- `src/shared/api/MonitorApi.ts`.
- `src/shared/contracts/*` (contratos TS/Zod monitor).
- `src/shared/config/*` (resolución de `caso_de_uso`).
- `src/router/router.tsx` con `/monitor` + wildcard redirect.
- `src/App.tsx`, `src/bootstrap.tsx`, `src/index.tsx`, `src/config/env.ts`, `src/theme/*`.

## Se elimina
- Rutas/páginas legacy de chat/sesiones/auth/home/about.
- Servicios legacy (`ChatService`, `SesionService`, `ContextService`, etc.).
- Componentes/hook/context/domain/locales/layouts del flujo legacy.
- Config legacy de channel manager/login por entorno no usada en monitor.
- Router config legacy (`router.config.ts`).
- Tests/Cypress centrados en flujos legacy.

## Resultado
- Shell FE queda orientada a un único caso de uso de producto: monitor.
- Flujo HTTP centralizado en `MonitorApi` para `/cards`, `/dashboard`, `/dashboard_detail`.
