import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { CardsGrid } from '#/shell/features/monitor/components/CardsGrid/CardsGrid';
import { DashboardDetail } from '#/shell/features/monitor/components/DashboardDetail/DashboardDetail';
import { DynamicTable } from '#/shell/features/monitor/components/DynamicTable/DynamicTable';
import { defaultMonitorStyle } from '#/shell/features/monitor/config/monitorStyle';
import { MonitorApi } from '#/shell/shared/api/MonitorApi';
import { ShellTabs } from '#/shell/shared/components/ShellTabs';
import {
  CardsResponse,
  DashboardDetailResponse,
  DashboardResponse,
  MonitorApiError,
  QueryRequest,
  UIShellResponse,
  ViewComponent,
} from '#/shell/shared/contracts/monitor.contracts';

const normalizeErrorMessage = (error: unknown) => {
  if (error instanceof MonitorApiError) {
    return `${error.code}: ${error.message}`;
  }
  return 'INTERNAL_ERROR: Unexpected error';
};

type SidebarFilters = {
  gestor: string;
  telefonoCliente: string;
  resolucion: string;
  fecha: string;
};

type DetailViewLayout = Record<string, unknown> | null;

const emptySidebarFilters: SidebarFilters = { gestor: '', telefonoCliente: '', resolucion: '', fecha: '' };

const parseLimit = (value: string | null): number | undefined => {
  if (!value) return undefined;
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) return undefined;
  return Math.trunc(parsed);
};

const queryFiltersToSidebar = (filters?: QueryRequest['filters']): SidebarFilters => ({
  gestor: typeof filters?.gestor === 'string' ? filters.gestor : '',
  telefonoCliente: typeof filters?.telefono_cliente === 'string' ? filters.telefono_cliente : '',
  resolucion: typeof filters?.resolucion === 'string' ? filters.resolucion : '',
  fecha: typeof filters?.fecha === 'string' ? filters.fecha : '',
});

const sidebarToQueryFilters = (filters: SidebarFilters): QueryRequest['filters'] => {
  const payload: Record<string, string> = {};
  if (filters.gestor.trim()) payload.gestor = filters.gestor.trim();
  if (filters.telefonoCliente.trim()) payload.telefono_cliente = filters.telefonoCliente.trim();
  if (filters.resolucion.trim()) payload.resolucion = filters.resolucion.trim();
  if (filters.fecha.trim()) payload.fecha = filters.fecha.trim();
  return Object.keys(payload).length > 0 ? payload : undefined;
};

const buildQueryFromSearchParams = (params: URLSearchParams): QueryRequest => {
  const filtersPayload: Record<string, string> = {};
  const gestor = params.get('gestor');
  const telefonoCliente = params.get('telefono_cliente');
  const resolucion = params.get('resolucion');
  const fecha = params.get('fecha');
  if (gestor) filtersPayload.gestor = gestor;
  if (telefonoCliente) filtersPayload.telefono_cliente = telefonoCliente;
  if (resolucion) filtersPayload.resolucion = resolucion;
  if (fecha) filtersPayload.fecha = fecha;

  return {
    timeRange: params.get('timeRange') ?? '24h',
    search: params.get('search') ?? undefined,
    limit: parseLimit(params.get('limit')),
    filters: Object.keys(filtersPayload).length > 0 ? filtersPayload : undefined,
  };
};

const buildMonitorUrl = (casoDeUso: string, query: QueryRequest) => {
  const params = new URLSearchParams();
  params.set('caso_de_uso', casoDeUso);
  if (query.timeRange) params.set('timeRange', query.timeRange);
  if (query.search) params.set('search', query.search);
  if (query.limit) params.set('limit', String(query.limit));
  if (typeof query.filters?.gestor === 'string') params.set('gestor', query.filters.gestor);
  if (typeof query.filters?.telefono_cliente === 'string') params.set('telefono_cliente', query.filters.telefono_cliente);
  if (typeof query.filters?.resolucion === 'string') params.set('resolucion', query.filters.resolucion);
  if (typeof query.filters?.fecha === 'string') params.set('fecha', query.filters.fecha);
  return `/monitor?${params.toString()}`;
};

const monitorLayoutCss = `
  .monitor-shell-grid{display:grid;grid-template-columns:280px minmax(0,1fr);gap:16px}
  .monitor-main-stack{display:grid;gap:12px}
  .monitor-split{display:grid;gap:12px;grid-template-columns:repeat(2,minmax(0,1fr))}
  .monitor-split-single{grid-template-columns:1fr}
  @media (max-width:1100px){
    .monitor-shell-grid{grid-template-columns:1fr}
    .monitor-split{grid-template-columns:1fr}
  }
`;

const defaultDetailView: DetailViewLayout = {
  type: 'split',
  children: [
    { id: 'detail-conversation', type: 'detail_conversation', title: 'Conversación' },
    { id: 'detail-panels', type: 'detail_panels', title: 'Datos' },
  ],
};

const sortByPosition = <T extends { position: number }>(items: T[]) => [...items].sort((a, b) => a.position - b.position);

const MonitorDashboardPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const styleConfig = defaultMonitorStyle;

  const [shell, setShell] = useState<UIShellResponse | null>(null);
  const [shellError, setShellError] = useState<string | null>(null);

  const [cards, setCards] = useState<CardsResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [detail, setDetail] = useState<DashboardDetailResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedRowSnapshot, setSelectedRowSnapshot] = useState<Record<string, unknown> | null>(null);
  const [activeDetailLayout, setActiveDetailLayout] = useState<DetailViewLayout>(defaultDetailView);

  const [query, setQuery] = useState<QueryRequest>(() => buildQueryFromSearchParams(searchParams));
  const [sidebarFilters, setSidebarFilters] = useState<SidebarFilters>(() => queryFiltersToSidebar(buildQueryFromSearchParams(searchParams).filters));

  const [loadingCards, setLoadingCards] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [cardsError, setCardsError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  const defaultSystemId = useMemo(() => {
    const explicitDefault = shell?.systems.find(item => item.default);
    return explicitDefault?.id ?? shell?.systems[0]?.id ?? '';
  }, [shell]);

  const requestedUseCase = searchParams.get('caso_de_uso') ?? '';
  const casoDeUso = requestedUseCase || defaultSystemId;

  const activeSystem = useMemo(() => {
    if (!shell) {
      return null;
    }
    return shell.systems.find(item => item.id === casoDeUso) ?? shell.systems[0] ?? null;
  }, [shell, casoDeUso]);

  const activeView = activeSystem?.view ?? null;

  useEffect(() => {
    const loadShell = async () => {
      try {
        setShell(await MonitorApi.getUIShell());
        setShellError(null);
      } catch (error) {
        setShellError(normalizeErrorMessage(error));
        setShell(null);
      }
    };

    void loadShell();
  }, []);

  useEffect(() => {
    if (!requestedUseCase && defaultSystemId) {
      navigate(buildMonitorUrl(defaultSystemId, query), { replace: true });
    }
  }, [defaultSystemId, navigate, query, requestedUseCase]);

  useEffect(() => {
    const urlQuery = buildQueryFromSearchParams(searchParams);
    setSidebarFilters(queryFiltersToSidebar(urlQuery.filters));

    setQuery(previous => {
      const nextFilters = JSON.stringify(urlQuery.filters ?? {});
      const previousFilters = JSON.stringify(previous.filters ?? {});
      if (
        previous.timeRange === urlQuery.timeRange
        && previous.search === urlQuery.search
        && previous.limit === urlQuery.limit
        && previousFilters === nextFilters
      ) {
        return previous;
      }

      return {
        ...previous,
        timeRange: urlQuery.timeRange,
        search: urlQuery.search,
        limit: urlQuery.limit,
        filters: urlQuery.filters,
      };
    });
  }, [searchParams]);

  const loadCards = async (systemId: string, nextQuery: QueryRequest) => {
    setLoadingCards(true);
    setCardsError(null);
    try { setCards(await MonitorApi.postCards(systemId, nextQuery)); }
    catch (error) { setCardsError(normalizeErrorMessage(error)); }
    finally { setLoadingCards(false); }
  };

  const loadDashboard = async (systemId: string, nextQuery: QueryRequest) => {
    setLoadingDashboard(true);
    setDashboardError(null);
    try { setDashboard(await MonitorApi.postDashboard(systemId, nextQuery)); }
    catch (error) { setDashboardError(normalizeErrorMessage(error)); }
    finally { setLoadingDashboard(false); }
  };

  const loadDetail = async (systemId: string, id: string, detailView?: DetailViewLayout) => {
    setLoadingDetail(true);
    setDetailError(null);
    setSelectedId(id);
    setActiveDetailLayout(detailView ?? defaultDetailView);
    setSelectedRowSnapshot(dashboard?.table.rows.find(row => row.id === id) ?? null);
    try { setDetail(await MonitorApi.postDashboardDetail(systemId, id, query)); }
    catch (error) { setDetailError(normalizeErrorMessage(error)); }
    finally { setLoadingDetail(false); }
  };

  useEffect(() => {
    if (!activeSystem) {
      return;
    }

    void loadCards(activeSystem.id, query);
    void loadDashboard(activeSystem.id, query);
    setDetail(null);
    setSelectedId(null);
    setSelectedRowSnapshot(null);
    setActiveDetailLayout(defaultDetailView);
  }, [activeSystem, query]);

  const applySidebarFilters = () => {
    if (!activeSystem) {
      return;
    }
    const nextQuery: QueryRequest = { ...query, cursor: undefined, filters: sidebarToQueryFilters(sidebarFilters) };
    setQuery(nextQuery);
    navigate(buildMonitorUrl(activeSystem.id, nextQuery));
  };

  const resetSidebarFilters = () => {
    if (!activeSystem) {
      return;
    }
    setSidebarFilters(emptySidebarFilters);
    const nextQuery: QueryRequest = { ...query, cursor: undefined, search: undefined, filters: undefined };
    setQuery(nextQuery);
    navigate(buildMonitorUrl(activeSystem.id, nextQuery));
  };

  const renderComponent = (component: ViewComponent): JSX.Element => {
    const sortedChildren = component.children ? sortByPosition(component.children) : [];
    const surfaceStyle = {
      background: styleConfig.theme.surfaceBackground,
      border: `1px solid ${styleConfig.theme.surfaceBorder}`,
      borderRadius: 10,
      padding: 12,
    };

    if (component.type === 'stack') {
      return (
        <section key={component.id} className='monitor-main-stack'>
          {sortedChildren.map(renderComponent)}
        </section>
      );
    }

    if (component.type === 'split') {
      const splitClassName = sortedChildren.length <= 1 ? 'monitor-split monitor-split-single' : 'monitor-split';
      return (
        <section key={component.id} className={splitClassName}>
          {sortedChildren.map(renderComponent)}
        </section>
      );
    }

    if (component.type === 'cards') {
      return (
        <section key={component.id} style={surfaceStyle}>
          <h2 style={{ marginBottom: 10 }}>{component.title}</h2>
          <CardsGrid data={cards} loading={loadingCards} error={cardsError} onRefresh={() => activeSystem && void loadCards(activeSystem.id, query)} view={styleConfig} config={component.config ?? undefined} />
        </section>
      );
    }

    if (component.type === 'table') {
      const detailView = component.config && typeof component.config.detail_view === 'object'
        ? (component.config.detail_view as Record<string, unknown>)
        : defaultDetailView;
      return (
        <section key={component.id} style={surfaceStyle}>
          <h2 style={{ marginBottom: 10 }}>{component.title}</h2>
          <DynamicTable
            data={dashboard}
            loading={loadingDashboard}
            error={dashboardError}
            query={query}
            onQueryChange={setQuery}
            onOpenDetail={id => activeSystem && void loadDetail(activeSystem.id, id, detailView)}
            view={styleConfig}
            config={component.config ?? undefined}
          />
        </section>
      );
    }

    if (component.type === 'text') {
      return (
        <section key={component.id} style={surfaceStyle}>
          <h2 style={{ marginBottom: 8 }}>{component.title}</h2>
          <p style={{ margin: 0 }}>{typeof component.config?.text === 'string' ? component.config.text : 'Componente textual configurable desde backend.'}</p>
        </section>
      );
    }

    if (component.type === 'chart') {
      return (
        <section key={component.id} style={surfaceStyle}>
          <h2 style={{ marginBottom: 8 }}>{component.title}</h2>
          <p style={{ marginBottom: 8 }}>Placeholder de gráfico renderizado por contrato JSON.</p>
          <div style={{ height: Number(component.config?.height ?? 160), borderRadius: 8, background: String(component.config?.color ?? '#dbe7ff') }} />
        </section>
      );
    }

    return (
      <section key={component.id} style={surfaceStyle}>
        <h2 style={{ marginBottom: 8 }}>{component.title}</h2>
        <p style={{ margin: 0 }}>El detalle se abre desde la tabla (id seleccionado: {selectedId ?? 'ninguno'}).</p>
      </section>
    );
  };

  return (
    <main style={{ background: styleConfig.theme.pageBackground, color: styleConfig.theme.text, minHeight: '100vh', padding: 24 }}>
      <style>{monitorLayoutCss}</style>
      {shell && (
        <ShellTabs
          shell={shell}
          activeTab={activeSystem?.id ?? 'home'}
          onSelectHome={() => navigate('/home')}
          onSelectSystem={systemId => navigate(buildMonitorUrl(systemId, query))}
        />
      )}

      <section style={{ background: 'linear-gradient(135deg, #0b5fff 0%, #102a43 100%)', borderRadius: 12, color: '#fff', marginBottom: 14, padding: 16 }}>
        <div style={{ alignItems: 'center', display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
          <div>
            <h1 style={{ marginBottom: 6 }}>{activeSystem?.label ?? 'Monitor'}</h1>
            <p style={{ margin: 0, opacity: 0.9 }}>{activeView?.name ?? 'Cargando vista declarativa desde backend.'}</p>
          </div>
          <button onClick={() => navigate('/admin')}>Admin de vistas</button>
        </div>
      </section>

      {shellError && (
        <section style={{ background: '#fff4f2', border: '1px solid #fecdca', borderRadius: 10, marginBottom: 14, padding: 12 }}>
          Error shell: {shellError}
        </section>
      )}

      <div className='monitor-shell-grid'>
        <aside style={{ background: styleConfig.theme.surfaceBackground, border: `1px solid ${styleConfig.theme.surfaceBorder}`, borderRadius: 10, height: 'fit-content', padding: 14 }}>
          <h3 style={{ marginBottom: 6 }}>Filtros</h3>
          <p style={{ margin: '0 0 12px 0', fontSize: 13 }}>Todos los componentes se resuelven desde una vista backend. Los filtros se aplican sobre la tabla activa.</p>

          <label htmlFor='timeRange' style={{ display: 'block', marginBottom: 8 }}><span>Rango temporal</span><input id='timeRange' style={{ marginTop: 4, width: '100%' }} value={query.timeRange ?? ''} onChange={event => setQuery({ ...query, timeRange: event.target.value })} /></label>
          <label htmlFor='search' style={{ display: 'block', marginBottom: 8 }}><span>Buscar</span><input id='search' style={{ marginTop: 4, width: '100%' }} value={query.search ?? ''} onChange={event => setQuery({ ...query, search: event.target.value || undefined })} /></label>
          <label htmlFor='limit' style={{ display: 'block', marginBottom: 8 }}><span>Límite</span><input id='limit' style={{ marginTop: 4, width: '100%' }} type='number' min={1} value={query.limit ?? ''} onChange={event => setQuery({ ...query, limit: parseLimit(event.target.value) })} /></label>
          <label htmlFor='gestor' style={{ display: 'block', marginBottom: 8 }}><span>Gestor</span><input id='gestor' style={{ marginTop: 4, width: '100%' }} value={sidebarFilters.gestor} onChange={event => setSidebarFilters({ ...sidebarFilters, gestor: event.target.value })} /></label>
          <label htmlFor='telefonoCliente' style={{ display: 'block', marginBottom: 8 }}><span>Teléfono cliente</span><input id='telefonoCliente' style={{ marginTop: 4, width: '100%' }} value={sidebarFilters.telefonoCliente} onChange={event => setSidebarFilters({ ...sidebarFilters, telefonoCliente: event.target.value })} /></label>
          <label htmlFor='resolucion' style={{ display: 'block', marginBottom: 8 }}><span>Resolución</span><input id='resolucion' style={{ marginTop: 4, width: '100%' }} value={sidebarFilters.resolucion} onChange={event => setSidebarFilters({ ...sidebarFilters, resolucion: event.target.value })} /></label>
          <label htmlFor='fecha' style={{ display: 'block', marginBottom: 12 }}><span>Fecha</span><input id='fecha' style={{ marginTop: 4, width: '100%' }} value={sidebarFilters.fecha} onChange={event => setSidebarFilters({ ...sidebarFilters, fecha: event.target.value })} /></label>

          <div style={{ display: 'flex', gap: 8 }}><button onClick={applySidebarFilters}>Aplicar filtros</button><button onClick={resetSidebarFilters}>Limpiar filtros</button></div>
        </aside>

        <section className='monitor-main-stack'>
          {activeView?.components ? sortByPosition(activeView.components).map(renderComponent) : <p>Cargando vista...</p>}
        </section>
      </div>

      <DashboardDetail
        data={detail}
        loading={loadingDetail}
        error={detailError}
        selectedId={selectedId}
        selectedRowSnapshot={selectedRowSnapshot}
        detailView={activeDetailLayout}
        onClose={() => setSelectedId(null)}
        view={styleConfig}
      />
    </main>
  );
};

export default MonitorDashboardPage;
