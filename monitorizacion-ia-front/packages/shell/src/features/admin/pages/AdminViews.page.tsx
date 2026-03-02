import { FormEvent, useEffect, useMemo, useState } from 'react';

import { MonitorApi } from '#/shell/shared/api/MonitorApi';
import { ViewComponent, ViewConfiguration, viewComponentSchema } from '#/shell/shared/contracts/monitor.contracts';

type DraftComponent = {
  id: string;
  type: ViewComponent['type'];
  title: string;
  data_source: ViewComponent['data_source'];
  position: number;
  configJson: string;
};

const emptyComponent: DraftComponent = {
  id: '',
  type: 'cards',
  title: '',
  data_source: '/cards',
  position: 0,
  configJson: '{}',
};

const emptyForm: ViewConfiguration = {
  id: '',
  name: '',
  system: '',
  enabled: true,
  components: [],
};

const byPosition = (a: ViewComponent, b: ViewComponent) => a.position - b.position;


const componentDataSources: Record<ViewComponent['type'], ViewComponent['data_source'][]> = {
  cards: ['/cards'],
  table: ['/dashboard'],
  detail: ['/dashboard_detail', '/none'],
  chart: ['/dashboard', '/cards', '/none'],
  text: ['/none'],
};

const AdminViewsPage = () => {
  const [items, setItems] = useState<ViewConfiguration[]>([]);
  const [form, setForm] = useState<ViewConfiguration>(emptyForm);
  const [draftComponent, setDraftComponent] = useState<DraftComponent>(emptyComponent);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const isEditing = useMemo(() => editingId !== null, [editingId]);

  const load = async () => {
    try {
      const response = await MonitorApi.getViewConfigurations();
      setItems(response);
      setError(null);
    } catch (e) {
      setError(`No se pudieron cargar las vistas: ${String(e)}`);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const resetForm = () => {
    setForm(emptyForm);
    setDraftComponent(emptyComponent);
    setEditingId(null);
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

    let next: ViewComponent;
    try {
      next = viewComponentSchema.parse({
        id: draftComponent.id,
        type: draftComponent.type,
        title: draftComponent.title,
        data_source: draftComponent.data_source,
        position: Number(draftComponent.position),
        config,
      });
    } catch (schemaError) {
      setError(`Configuración inválida del componente: ${String(schemaError)}`);
      return;
    }

    setForm(prev => ({ ...prev, components: [...prev.components, next].sort(byPosition) }));
    setDraftComponent({ ...emptyComponent, position: draftComponent.position + 1 });
    setError(null);
  };

  const removeComponent = (componentId: string) => {
    setForm(prev => ({ ...prev, components: prev.components.filter(item => item.id !== componentId) }));
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSuccess(null);

    if (form.components.length === 0) {
      setError('Debes incluir al menos un componente en la vista.');
      return;
    }

    try {
      if (isEditing && editingId) {
        await MonitorApi.updateViewConfiguration(editingId, {
          name: form.name,
          system: form.system,
          enabled: form.enabled,
          components: form.components,
        });
        setSuccess(`Vista ${editingId} actualizada correctamente.`);
      } else {
        await MonitorApi.createViewConfiguration(form);
        setSuccess(`Vista ${form.id} creada correctamente.`);
      }
      resetForm();
      await load();
    } catch (e) {
      setError(`Error guardando vista: ${String(e)}`);
    }
  };

  const onEdit = (item: ViewConfiguration) => {
    setForm(item);
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
      <p>Define composición dinámica por JSON contractual para reutilizar componentes por sistema.</p>
      <a href='/home'>Volver a Home</a>
      {error && <p style={{ color: '#b42318' }}>{error}</p>}
      {success && <p style={{ color: '#027a48' }}>{success}</p>}

      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 8, maxWidth: 900 }}>
        <input placeholder='id de vista' value={form.id} onChange={e => setForm({ ...form, id: e.target.value })} disabled={isEditing} required />
        <input placeholder='nombre visible' value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
        <input placeholder='sistema' value={form.system} onChange={e => setForm({ ...form, system: e.target.value })} required />
        <label>
          <input type='checkbox' checked={form.enabled} onChange={e => setForm({ ...form, enabled: e.target.checked })} />
          habilitada
        </label>

        <fieldset style={{ border: '1px solid #d0d5dd', borderRadius: 8, padding: 12 }}>
          <legend>Componentes reutilizables</legend>
          <div style={{ display: 'grid', gap: 6, gridTemplateColumns: 'repeat(5, minmax(0, 1fr))' }}>
            <input placeholder='id componente' value={draftComponent.id} onChange={e => setDraftComponent(prev => ({ ...prev, id: e.target.value }))} />
            <select value={draftComponent.type} onChange={e => setDraftComponent(prev => { const nextType = e.target.value as DraftComponent['type']; return { ...prev, type: nextType, data_source: componentDataSources[nextType][0] }; })}>
              <option value='cards'>cards</option><option value='table'>table</option><option value='detail'>detail</option><option value='chart'>chart</option><option value='text'>text</option>
            </select>
            <input placeholder='título' value={draftComponent.title} onChange={e => setDraftComponent(prev => ({ ...prev, title: e.target.value }))} />
            <select value={draftComponent.data_source} onChange={e => setDraftComponent(prev => ({ ...prev, data_source: e.target.value as DraftComponent['data_source'] }))}>
              {componentDataSources[draftComponent.type].map(source => <option key={source} value={source}>{source}</option>)}
            </select>
            <input type='number' placeholder='posición' value={draftComponent.position} onChange={e => setDraftComponent(prev => ({ ...prev, position: Number(e.target.value) }))} />
          </div>
          <textarea
            placeholder='config JSON por componente, ej: {"height":220,"color":"#0b5fff"}'
            value={draftComponent.configJson}
            rows={4}
            onChange={e => setDraftComponent(prev => ({ ...prev, configJson: e.target.value }))}
            style={{ marginTop: 8, width: '100%' }}
          />
          <button type='button' onClick={addComponent} style={{ marginTop: 8 }}>Añadir componente</button>

          {form.components.length > 0 && (
            <ul style={{ marginTop: 12, paddingLeft: 16 }}>
              {form.components.map(component => (
                <li key={component.id}>
                  {component.position} · {component.type} · {component.title} ({component.data_source})
                  <button type='button' onClick={() => removeComponent(component.id)} style={{ marginLeft: 8 }}>Quitar</button>
                </li>
              ))}
            </ul>
          )}
        </fieldset>

        <div style={{ display: 'flex', gap: 8 }}>
          <button type='submit'>{isEditing ? 'Actualizar vista' : 'Crear vista'}</button>
          <button type='button' onClick={resetForm}>Limpiar</button>
        </div>
      </form>

      <section>
        <h2>Vistas configuradas</h2>
        {items.map(item => (
          <article key={item.id} style={{ border: '1px solid #ccc', borderRadius: 8, padding: 10, marginBottom: 8 }}>
            <p><strong>{item.name}</strong> ({item.system}) · {item.enabled ? 'Activa' : 'Inactiva'} · {item.components.length} componentes</p>
            <button onClick={() => onEdit(item)}>Editar</button>
            <button onClick={() => onDelete(item.id)} style={{ marginLeft: 8 }}>Eliminar</button>
          </article>
        ))}
      </section>
    </main>
  );
};

export default AdminViewsPage;
