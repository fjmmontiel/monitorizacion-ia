# Monitorización IA — Estado actual y guía de uso/escalado

Este repositorio implementa un **monitor frontend configurable por JSON** y un **backend orquestador mínimo** que enruta por `caso_de_uso` y sirve datos mock desde JSON locales.

---

## 1) Estado actual (resumen ejecutivo)

- **Frontend (shell React)**
  - Home con navegación a sistemas/casos de uso.
  - Monitor con render dinámico por componentes (`cards`, `table`, `text`, `chart`) definidos en configuración de vistas.
  - Detalle por fila con layout compuesto **60/40**:
    - Conversación (60%).
    - Panel fijo (40%) con productos/servicios e información contextual.
  - Página **Admin** con CRUD de vistas para crear composiciones sin tocar código.

- **Backend (FastAPI)**
  - API principal de monitor:
    - `POST /cards`
    - `POST /dashboard`
    - `POST /dashboard_detail`
  - API Admin para vistas:
    - `GET/POST/PUT/DELETE /admin/view-configs`
  - Persistencia de vistas en JSON local (`view_configs.json`).
  - Datos de negocio mock por sistema en JSON local:
    - `cards.json`
    - `dashboard.json`
    - `dashboard_detail.json`

- **Objetivo cubierto**
  - Arquitectura mínima y mantenible.
  - Nuevos sistemas/vistas añadibles por configuración.
  - Contrato JSON flexible para variar número de cards y columnas de tabla por vista.

---

## 2) Estructura del proyecto

```text
.
├─ monitorizacion-ia-front/
│  └─ packages/shell/                # Frontend principal (React)
├─ monitorizacion-ia-python/
│  └─ src/orchestrator/              # Backend FastAPI + adapters + datos JSON
├─ scripts/                          # Scripts de arranque/parada/smoke/e2e
├─ docs/qa/                          # Guías QA/UAT
├─ Makefile                          # Comandos unificados
└─ README.md                         # Este documento
```

---

## 3) Arquitectura funcional

### Frontend

1. El usuario entra en Home y selecciona sistema.
2. Monitor carga la vista activa (`/admin/view-configs?system=...&enabled=true`).
3. Se renderizan componentes según contrato JSON y `position`.
4. `cards` y `table` consumen backend por `caso_de_uso`.
5. Al abrir detalle de una fila, se carga `dashboard_detail` y se pinta el layout 60/40.

### Backend

1. Recibe petición con `caso_de_uso`.
2. `AdapterRegistry` resuelve el adapter configurado para ese caso.
3. Adapter nativo lee JSON local del sistema.
4. Devuelve respuesta bajo contrato (cards/dashboard/detail).
5. API Admin persiste configuraciones de vistas en JSON local.

---

## 4) Contratos de configuración de vistas

Cada vista define componentes ordenados por `position`.

Ejemplo base:

```json
{
  "id": "vista-hipotecas-5-cards",
  "name": "Hipotecas · 5 KPIs",
  "system": "hipotecas",
  "enabled": true,
  "components": [
    {
      "id": "cards-hipo-5",
      "type": "cards",
      "title": "KPIs Hipotecas (5)",
      "data_source": "/cards",
      "position": 0,
      "config": { "max_cards": 5, "columns": 5 }
    },
    {
      "id": "table-hipo",
      "type": "table",
      "title": "Conversaciones Hipotecas",
      "data_source": "/dashboard",
      "position": 1,
      "config": {
        "required_columns": ["detail"],
        "visible_columns": ["fecha_hora", "nombre_cliente", "razones_llamada", "resolucion", "detail"]
      }
    }
  ]
}
```

### Reglas actuales por tipo

- `cards`
  - `config.max_cards` (opcional)
  - `config.columns` (opcional)
- `table`
  - `config.visible_columns` (opcional)
  - `config.required_columns` (opcional, por defecto `detail`)
- `text`
  - `config.text`
- `chart`
  - `config.height`
  - `config.color`

---

## 5) Puesta en marcha local

### Opción recomendada (todo preparado)

```bash
make setup-env
make up
```

URLs por defecto:
- Front: `http://127.0.0.1:3100/monitor?caso_de_uso=hipotecas`
- Back: `http://127.0.0.1:8002/health`

### Operaciones útiles

```bash
make stop
make restart
make status
make logs
make show-config
```

---

## 6) Validación y pruebas

### Backend

```bash
cd monitorizacion-ia-python
PYTHONPATH=src pytest -q
```

### Frontend (tipado)

```bash
cd monitorizacion-ia-front/packages/shell
npm run typecheck
```

### Smoke y E2E del repositorio

```bash
make smoke
make e2e
```

> Nota: si `make smoke` falla por tiempos/arranque del entorno, revisar logs (`make logs`) y volver a ejecutar con stack previamente levantado.

---

## 7) Cómo escalar: alta de un nuevo sistema (backend + frontend)

### Paso A — Backend

1. Añadir nuevo `use_case` en `monitorizacion-ia-python/src/orchestrator/config/dev.yaml`.
2. Crear carpeta:
   - `monitorizacion-ia-python/src/orchestrator/data/<nuevo_sistema>/`
3. Añadir JSON mínimos:
   - `cards.json`
   - `dashboard.json`
   - `dashboard_detail.json`

### Paso B — Frontend

1. Registrar sistema en:
   - `monitorizacion-ia-front/packages/shell/src/shared/config/use_cases.json`
2. Crear vista desde Admin o precargarla en `view_configs.json`.

### Paso C — QA funcional

1. Abrir Home y comprobar que aparece el nuevo sistema.
2. Abrir Monitor con `?caso_de_uso=<nuevo_sistema>`.
3. Crear/editar vista en Admin y activar sus componentes.
4. Validar detalle 60/40 por fila.

---

## 8) Principios de mantenibilidad aplicados

- Configuración por contrato JSON (sin hardcode de layouts).
- Adapter registry inyectable y extensible.
- Persistencia local simple para entornos de validación.
- Componentes UI reutilizables con `config` declarativa.
- Rutas backend compactas y reutilización de ejecución por operación.

---

## 9) Roadmap recomendado (alto nivel)

Las mejoras priorizadas del antiguo plan `evolution` ya están integradas en el código base (excepto autenticación, pospuesta por alcance):
- validación semántica fuerte de vistas en backend/frontend,
- persistencia JSON con escritura atómica y backup,
- métricas in-memory de requests (`/metrics`) y trazas enriquecidas por adapter,
- limitación de ritmo en endpoints administrativos,
- contratos de configuración tipados por componente en frontend.

