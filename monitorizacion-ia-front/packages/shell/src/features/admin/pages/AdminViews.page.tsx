import { FormEvent, useEffect, useMemo, useState } from 'react';

import { MonitorApi } from '#/shell/shared/api/MonitorApi';
import { ViewComponent, ViewConfiguration, viewComponentSchema, viewConfigurationSchema } from '#/shell/shared/contracts/monitor.contracts';

type DraftComponent = {
  id: string;
  type: ViewComponent['type'];
  title: string;
  data_source: ViewComponent['data_source'];
  position: number;
  configJson: string;
  childrenJson: string;
};

const emptyComponent: DraftComponent = {
  id: '',
  type: 'cards',
  title: '',
  data_source: '/cards',
  position: 0,
  configJson: '{}',
  childrenJson: '[]',
};

const emptyForm: ViewConfiguration = {
  id: '',
  name: '',
  system: '',
  enabled: true,
  runtime: null,
  components: [],
};

const byPosition = (a: ViewComponent, b: ViewComponent) => a.position - b.position;

const formatJson = (value: unknown) => JSON.stringify(value, null, 2);

const toTitleSegment = (value: string) => {
  const normalized = value.split('·')[0]?.trim();
  return normalized || value.trim();
};

export const buildDefaultViewComponents = (system: string, viewName: string): ViewComponent[] => {
  const systemId = system.trim();
  const titleSegment = toTitleSegment(viewName || systemId) || systemId;

  return [
    {
      id: `layout-${systemId}`,
      type: 'stack',
      title: `Layout ${titleSegment}`,
      data_source: '/none',
      position: 0,
      children: [
        {
          id: `cards-${systemId}`,
          type: 'cards',
          title: `KPIs ${titleSegment}`,
          data_source: '/cards',
          position: 0,
          config: {
            max_cards: 4,
            columns: 4,
          },
        },
        {
          id: `table-${systemId}`,
          type: 'table',
          title: `Actividad ${titleSegment}`,
          data_source: '/dashboard',
          position: 1,
          config: {
            required_columns: ['id', 'detail'],
            detail_view: {
              type: 'split',
              children: [
                { id: 'detail-conversation', type: 'detail_conversation', title: 'Conversación' },
                { id: 'detail-panels', type: 'detail_panels', title: 'Datos' },
              ],
            },
          },
        },
      ],
    },
  ];
};

const parseComponentsJson = (raw: string): ViewComponent[] => {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw.trim() ? raw : '[]');
  } catch {
    throw new Error('El JSON completo de componentes no es válido.');
  }

  if (!Array.isArray(parsed)) {
    throw new Error('El JSON completo de componentes debe ser un array.');
  }

  return parsed.map((item, index) => {
    try {
      return viewComponentSchema.parse(item);
    } catch (error) {
      throw new Error(`Componente ${index}: ${String(error)}`);
    }
  });
};

const countComponents = (components: ViewComponent[]): number =>
  components.reduce((total, component) => total + 1 + countComponents(component.children ?? []), 0);

const componentDataSources: Record<ViewComponent['type'], ViewComponent['data_source'][]> = {
  cards: ['/cards'],
  table: ['/dashboard'],
  detail: ['/dashboard_detail', '/none'],
  chart: ['/dashboard', '/cards', '/none'],
  text: ['/none'],
  stack: ['/none'],
  split: ['/none'],
};

const AdminViewsPage = () => {
  const [items, setItems] = useState<ViewConfiguration[]>([]);
  const [form, setForm] = useState<ViewConfiguration>(emptyForm);
  const [componentsJson, setComponentsJson] = useState<string>(formatJson(emptyForm.components));
  const [draftComponent, setDraftComponent] = useState<DraftComponent>(emptyComponent);
  const [knownSystems, setKnownSystems] = useState<Array<{ id: string; label: string }>>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const isEditing = useMemo(() => editingId !== null, [editingId]);
  const runtimeMode = form.runtime?.adapter ?? 'backend_default';

  const load = async () => {
    const [viewsResult, datopsResult] = await Promise.allSettled([
      MonitorApi.getViewConfigurations(),
      MonitorApi.getDatopsOverview(),
    ]);

    if (viewsResult.status === 'fulfilled') {
      setItems(viewsResult.value);
      setError(null);
    } else {
      setError(`No se pudieron cargar las vistas: ${String(viewsResult.reason)}`);
    }

    if (datopsResult.status === 'fulfilled') {
      setKnownSystems(
        datopsResult.value.use_cases
          .map(item => ({ id: item.id, label: item.label }))
          .sort((a, b) => a.label.localeCompare(b.label)),
      );
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const resetForm = () => {
    setForm(emptyForm);
    setComponentsJson(formatJson(emptyForm.components));
    setDraftComponent(emptyComponent);
    setEditingId(null);
  };

  const syncComponents = (components: ViewComponent[]) => {
    setForm(prev => ({ ...prev, components }));
    setComponentsJson(formatJson(components));
  };

  const setRuntimeMode = (mode: 'backend_default' | 'http_proxy') => {
    if (mode === 'http_proxy') {
      setForm(prev => ({
        ...prev,
        runtime: {
          adapter: 'http_proxy',
          upstream_base_url: prev.runtime?.upstream_base_url ?? '',
        },
      }));
      return;
    }

    setForm(prev => ({ ...prev, runtime: null }));
  };

  const setRuntimeHost = (upstreamBaseUrl: string) => {
    setForm(prev => ({
      ...prev,
      runtime: {
        adapter: 'http_proxy',
        upstream_base_url: upstreamBaseUrl,
      },
    }));
  };

  const addComponent = () => {
    if (!draftComponent.id || !draftComponent.title || !draftComponent.data_source) {
      setError('Todos los campos del componente son obligatorios.');
      return;
    }

    const exists = form.components.some(item => item.id === draftComponent.id);
    if (exists) {
      setError(`Ya existe un componente con id ${draftComponent.id}`);
      return;
    }

    let config: Record<string, unknown> | undefined;
    try {
      const parsed = JSON.parse(draftComponent.configJson);
      config = parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : undefined;
    } catch {
      setError('El JSON de configuración del componente no es válido.');
      return;
    }

    let children: ViewComponent[] | undefined;
    try {
      const parsed = JSON.parse(draftComponent.childrenJson);
      if (Array.isArray(parsed) && parsed.length > 0) {
        children = parsed as ViewComponent[];
      }
    } catch {
      setError('El JSON de children no es válido.');
      return;
    }

    let next: ViewComponent;
    try {
      next = viewComponentSchema.parse({
        id: draftComponent.id,
        type: draftComponent.type,
        title: draftComponent.title,
        data_source: draftComponent.data_source,
        position: Number(draftComponent.position),
        config,
        children,
      });
    } catch (schemaError) {
      setError(`Configuración inválida del componente: ${String(schemaError)}`);
      return;
    }

    syncComponents([...form.components, next].sort(byPosition));
    setDraftComponent({ ...emptyComponent, position: draftComponent.position + 1 });
    setError(null);
  };

  const removeComponent = (componentId: string) => {
    syncComponents(form.components.filter(item => item.id !== componentId));
  };

  const applyComponentsJson = () => {
    try {
      const parsedComponents = parseComponentsJson(componentsJson).sort(byPosition);
      syncComponents(parsedComponents);
      setError(null);
    } catch (e) {
      setError(String(e));
    }
  };

  const applyDefaultComponents = () => {
    if (!form.system.trim()) {
      setError('Indica primero el sistema / caso_de_uso para generar una vista base.');
      return;
    }

    const generated = buildDefaultViewComponents(form.system, form.name.trim() || form.system);
    syncComponents(generated);
    setError(null);
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSuccess(null);

    try {
      const parsedComponents = parseComponentsJson(componentsJson).sort(byPosition);
      const resolvedComponents = !isEditing && parsedComponents.length === 0
        ? buildDefaultViewComponents(form.system, form.name.trim() || form.system)
        : parsedComponents;

      const payload = viewConfigurationSchema.parse({
        ...form,
        components: resolvedComponents,
      });

      setForm(payload);
      setComponentsJson(formatJson(payload.components));

      if (isEditing && editingId) {
        await MonitorApi.updateViewConfiguration(editingId, {
          name: payload.name,
          system: payload.system,
          enabled: payload.enabled,
          runtime: payload.runtime,
          components: payload.components,
        });
        setSuccess(`Vista ${editingId} actualizada correctamente.`);
      } else {
        await MonitorApi.createViewConfiguration(payload);
        setSuccess(`Vista ${payload.id} creada correctamente.`);
      }
      resetForm();
      await load();
    } catch (e) {
      setError(`Error guardando vista: ${String(e)}`);
    }
  };

  const onEdit = (item: ViewConfiguration) => {
    setForm(item);
    setComponentsJson(formatJson(item.components));
    setEditingId(item.id);
    setDraftComponent(emptyComponent);
    setError(null);
    setSuccess(null);
  };

  const onDelete = async (id: string) => {
    try {
      await MonitorApi.deleteViewConfiguration(id);
      setSuccess(`Vista ${id} eliminada correctamente.`);
      await load();
      if (editingId === id) {
        resetForm();
      }
    } catch (e) {
      setError(`Error eliminando vista: ${String(e)}`);
    }
  };

  return (
    <main style={{ padding: 24, display: 'grid', gap: 16 }}>
      <h1>ADMIN · Configuración de vistas</h1>
      <p style={{ margin: 0, maxWidth: 1100 }}>
        Crea o edita vistas en runtime y guárdalas. El backend persiste el JSON de la vista y, si lo defines aquí, también el routing `http_proxy`.
      </p>
      <div style={{ alignItems: 'center', display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <a href='/home'>Volver a Home</a>
        <small>
          Sistemas disponibles: {knownSystems.length > 0 ? knownSystems.map(item => `${item.label} (${item.id})`).join(', ') : 'no disponibles'}
        </small>
      </div>
      <details style={{ background: '#ffffff', border: '1px solid #d9e2ec', borderRadius: 10, maxWidth: 1100, padding: 12 }}>
        <summary style={{ cursor: 'pointer', fontWeight: 700 }}>Cómo funciona en runtime</summary>
        <p style={{ margin: '10px 0 6px 0' }}>
          Desde este ADMIN puedes crear, editar o eliminar vistas. Al guardar, el backend persiste la configuración y el listado de esta pantalla se recarga automáticamente.
        </p>
        <p style={{ margin: 0 }}>
          Si una vista define `http_proxy` con host, el orquestador usará ese destino para ese `caso_de_uso`. La shell solo carga la configuración declarativa al abrirse; los datos (`cards`, `dashboard` y `detail`) se piden al entrar en la vista del sistema.
        </p>
      </details>
      {error && <p style={{ color: '#b42318' }}>{error}</p>}
      {success && <p style={{ color: '#027a48' }}>{success}</p>}

      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 12, maxWidth: 1100 }}>
        <input placeholder='id de vista' value={form.id} onChange={e => setForm({ ...form, id: e.target.value })} disabled={isEditing} required />
        <input placeholder='nombre visible' value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
        <div style={{ display: 'grid', gap: 6 }}>
          <input list='admin-known-systems' placeholder='sistema / caso_de_uso' value={form.system} onChange={e => setForm({ ...form, system: e.target.value })} required />
          <datalist id='admin-known-systems'>
            {knownSystems.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}
          </datalist>
          <small>Puedes usar un `caso_de_uso` existente o escribir uno nuevo. La vista quedará disponible para ese sistema al navegar a su monitor.</small>
        </div>
        <fieldset style={{ border: '1px solid #d0d5dd', borderRadius: 8, padding: 12 }}>
          <legend>Orquestación del sistema</legend>
          <div style={{ display: 'grid', gap: 6 }}>
            <select value={runtimeMode} onChange={e => setRuntimeMode(e.target.value === 'http_proxy' ? 'http_proxy' : 'backend_default')}>
              <option value='backend_default'>Usar datos nativos locales</option>
              <option value='http_proxy'>Resolver como http_proxy desde esta vista</option>
            </select>
            {runtimeMode === 'http_proxy' && (
              <input
                placeholder='host upstream, ej: http://localhost:9000'
                value={form.runtime?.upstream_base_url ?? ''}
                onChange={e => setRuntimeHost(e.target.value)}
                required
              />
            )}
            <small>
              Si eliges `http_proxy`, esta vista centraliza el host del sistema y el orquestador redirigirá las llamadas a ese backend usando solo esta configuración persistida.
            </small>
          </div>
        </fieldset>
        <label>
          <input type='checkbox' checked={form.enabled} onChange={e => setForm({ ...form, enabled: e.target.checked })} />
          habilitada
        </label>

        <fieldset style={{ border: '1px solid #d0d5dd', borderRadius: 8, padding: 12 }}>
          <legend>Componentes de la vista (JSON completo recuperable)</legend>
          <p style={{ margin: '0 0 8px 0' }}>Aquí se carga la estructura completa, incluyendo `config` y `children`.</p>
          <textarea
            placeholder='[{"id":"layout-root","type":"stack","title":"Layout","data_source":"/none","position":0,"children":[...]}]'
            value={componentsJson}
            rows={14}
            onChange={e => setComponentsJson(e.target.value)}
            style={{ fontFamily: 'monospace', width: '100%' }}
          />
          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <button type='button' onClick={applyComponentsJson}>Aplicar JSON al formulario</button>
            {!isEditing && <button type='button' onClick={applyDefaultComponents}>Generar vista base</button>}
            <small style={{ alignSelf: 'center' }}>
              Componentes sincronizados: {countComponents(form.components)}
            </small>
          </div>
        </fieldset>

        <details style={{ border: '1px solid #d0d5dd', borderRadius: 8, padding: 12 }}>
          <summary style={{ cursor: 'pointer', fontWeight: 700 }}>Constructor rápido (opcional)</summary>
          <p style={{ margin: '10px 0 8px 0' }}>Añade componentes simples al JSON. Para estructuras complejas, edita el bloque superior.</p>
          <div style={{ display: 'grid', gap: 6, gridTemplateColumns: 'repeat(5, minmax(0, 1fr))' }}>
            <input placeholder='id componente' value={draftComponent.id} onChange={e => setDraftComponent(prev => ({ ...prev, id: e.target.value }))} />
            <select value={draftComponent.type} onChange={e => setDraftComponent(prev => { const nextType = e.target.value as DraftComponent['type']; return { ...prev, type: nextType, data_source: componentDataSources[nextType][0] }; })}>
              <option value='cards'>cards</option><option value='table'>table</option><option value='detail'>detail</option><option value='chart'>chart</option><option value='text'>text</option><option value='stack'>stack</option><option value='split'>split</option>
            </select>
            <input placeholder='título' value={draftComponent.title} onChange={e => setDraftComponent(prev => ({ ...prev, title: e.target.value }))} />
            <select value={draftComponent.data_source} onChange={e => setDraftComponent(prev => ({ ...prev, data_source: e.target.value as DraftComponent['data_source'] }))}>
              {componentDataSources[draftComponent.type].map(source => <option key={source} value={source}>{source}</option>)}
            </select>
            <input type='number' placeholder='posición' value={draftComponent.position} onChange={e => setDraftComponent(prev => ({ ...prev, position: Number(e.target.value) }))} />
          </div>
          <textarea
            placeholder='config JSON por componente, ej: {"required_columns":["id","detail"]}'
            value={draftComponent.configJson}
            rows={3}
            onChange={e => setDraftComponent(prev => ({ ...prev, configJson: e.target.value }))}
            style={{ marginTop: 8, width: '100%' }}
          />
          <textarea
            placeholder='children JSON para stack/split'
            value={draftComponent.childrenJson}
            rows={3}
            onChange={e => setDraftComponent(prev => ({ ...prev, childrenJson: e.target.value }))}
            style={{ marginTop: 8, width: '100%' }}
          />
          <button type='button' onClick={addComponent} style={{ marginTop: 8 }}>Añadir componente</button>

          {form.components.length > 0 && (
            <ul style={{ marginTop: 12, paddingLeft: 16 }}>
              {form.components.map(component => (
                <li key={component.id}>
                  {component.position} · {component.type} · {component.title} ({component.data_source}) · children: {component.children?.length ?? 0}
                  <button type='button' onClick={() => removeComponent(component.id)} style={{ marginLeft: 8 }}>Quitar</button>
                </li>
              ))}
            </ul>
          )}
        </details>

        <div style={{ display: 'flex', gap: 8 }}>
          <button type='submit'>{isEditing ? 'Actualizar vista' : 'Crear vista'}</button>
          <button type='button' onClick={resetForm}>Limpiar</button>
        </div>
      </form>

      <section>
        <h2>Vistas configuradas</h2>
        {items.map(item => (
          <article key={item.id} style={{ border: '1px solid #ccc', borderRadius: 8, padding: 10, marginBottom: 8 }}>
            <p>
              <strong>{item.name}</strong> ({item.system}) · {item.enabled ? 'Activa' : 'Inactiva'} · {item.components.length} componentes raíz · {countComponents(item.components)} componentes totales
            </p>
            {item.runtime?.adapter === 'http_proxy' && (
              <p style={{ marginTop: 0 }}>
                Orquestación: <code>http_proxy</code> → <code>{item.runtime.upstream_base_url}</code>
              </p>
            )}
            <button onClick={() => onEdit(item)}>Editar</button>
            <button onClick={() => onDelete(item.id)} style={{ marginLeft: 8 }}>Eliminar</button>
          </article>
        ))}
      </section>
    </main>
  );
};

export default AdminViewsPage;
