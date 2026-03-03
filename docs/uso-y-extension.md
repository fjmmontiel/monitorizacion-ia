# Uso y extensión

## Cómo usarlo
1. Arranca con `make run`.
2. Abre `/home`.
3. Entra en una pestaña de sistema.
4. Usa `/admin` si quieres cambiar layouts.

## Cómo funciona
- El backend define sistemas en `use_cases.yaml`.
- El backend define vistas en `view_configs.json`.
- El backend sirve datos mock en `data/<caso_de_uso>/`.
- El frontend lee `GET /ui/shell` y renderiza.

## Cómo añadir un sistema
1. Añade el sistema en [use_cases.yaml](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/config/use_cases.yaml).
2. Crea:
   - `cards.json`
   - `dashboard.json`
   - `dashboard_detail.json`
   en `monitorizacion-ia-python/src/orchestrator/data/<nuevo>/`.
3. Crea una vista en [view_configs.json](/Users/usuario/personal/monitorizacion-ia/monitorizacion-ia-python/src/orchestrator/config/view_configs.json) o en `/admin`.
4. Verifica que `GET /ui/shell` lo lista y aparece una nueva pestaña.

## Cómo añadir o cambiar una vista
Tipos soportados:
- `cards`
- `table`
- `text`
- `chart`
- `stack`
- `split`

Reglas:
- `stack` y `split` usan `children`.
- `cards` usa `/cards`.
- `table` usa `/dashboard`.
- La tabla exige `id` y `detail`.

## Qué puede cambiar por datos
- Las cards aceptan `title`, `subtitle`, `value`, `format`, `unit`, `variant`.
- La tabla acepta columnas dinámicas.
- El detalle puede declararse en `table.config.detail_view`.
