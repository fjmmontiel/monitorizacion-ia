# Legacy scope retirado para pivot a Orquestador

## Objetivo
Reducir el backend a un orquestador agnóstico de dominio basado en `caso_de_uso`, con contratos canónicos y routing por configuración.

## Elementos retirados del runtime
- Rutas legacy de conversación/sesión específicas de hipotecas.
- Managers, tools y services de dominio (`app/managers`, `app/tools`, `app/services`).
- Repositorios y conectores DB específicos (`app/repositories`).
- Modelos de dominio legacy (`app/models`, `app/schemas` legacy).
- Dependencias corporativas de runtime (`qgdiag-*`) para logging/auth durante Fase 0.

## Motivo
- El orquestador no debe conocer lógica de dominio.
- El backend debe enrutar por `caso_de_uso` mediante configuración.
- Se elimina acoplamiento a infra externa (JWKS/corporate middleware) para poder arrancar localmente sin credenciales.

## Resultado esperado tras limpieza
- Endpoints canónicos:
  - `POST /cards?caso_de_uso=...`
  - `POST /dashboard?caso_de_uso=...`
  - `POST /dashboard_detail?caso_de_uso=...`
- `/health` operativo.
- Errores estándar y contratos versionados v1.
