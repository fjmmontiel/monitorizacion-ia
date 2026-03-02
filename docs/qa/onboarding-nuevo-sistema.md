# Análisis pantalla a pantalla y alta de nuevo sistema (JSON local)

## Fuente de datos backend
- El backend usa ahora JSON locales por sistema en `src/orchestrator/data/<sistema>/`.
- Archivos mínimos por sistema:
  - `cards.json`
  - `dashboard.json`
  - `dashboard_detail.json`

## Flujo validado (pantalla a pantalla)
1. **Home overview**
   - Carga de sistemas habilitados y navegación sin errores.
2. **Monitor Hipotecas**
   - Render de cards + tabla correcto con datos JSON locales.
3. **Monitor Préstamos**
   - Render de cards + tabla correcto con datos JSON locales.
4. **Monitor Seguros (nuevo sistema)**
   - Render correcto tras alta en backend + frontend.
5. **Admin inicial**
   - CRUD disponible para crear composiciones de vistas.
6. **Admin creando vista dinámica para Seguros**
   - Alta de vista `vista-seguros-dinamica` con componentes reutilizables.
7. **Monitor Seguros con vista dinámica**
   - Render en base a contrato JSON de la vista creada en Admin.

## Errores detectados y corregidos
- **Acoplamiento y hardcode del adapter nativo**: antes devolvía datos hardcodeados en Python.
  - Solución: `NativeAdapter` ahora lee JSON local por sistema y valida contratos.
- **Dependencia obligatoria de `lsof` para levantar entorno**.
  - Solución: fallback a `ss` en scripts de runtime (`scripts/common.sh`) y eliminación de hard requirement en `up-local.sh`.

## Pasos para dar de alta un nuevo sistema (backend + frontend)
1. Backend: añadir sistema en `src/orchestrator/config/dev.yaml` dentro de `use_cases`.
2. Backend: crear carpeta `src/orchestrator/data/<nuevo_sistema>/` con `cards.json`, `dashboard.json`, `dashboard_detail.json`.
3. Frontend: añadir sistema en `packages/shell/src/shared/config/use_cases.json`.
4. Arrancar stack (`make setup-env && make up`).
5. Verificar en Home y Monitor que aparece el sistema.
6. Crear vista específica en Admin y abrir Monitor con `?caso_de_uso=<nuevo_sistema>&vista=<id_vista>`.

## Resultado
- El flujo queda totalmente configurable por JSON local en backend y por configuración de vistas en frontend Admin.
