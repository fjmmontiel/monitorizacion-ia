import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { CardsGrid } from '#/shell/features/monitor/components/CardsGrid/CardsGrid';
import { DashboardDetail } from '#/shell/features/monitor/components/DashboardDetail/DashboardDetail';
import { DynamicTable } from '#/shell/features/monitor/components/DynamicTable/DynamicTable';
import { defaultMonitorStyle } from '#/shell/features/monitor/config/monitorStyle';
import { resolveSystemLayout } from '#/shell/features/monitor/config/systemLayouts';
import { MonitorApi } from '#/shell/shared/api/MonitorApi';
import { resolveUseCase, useCasesConfig } from '#/shell/shared/config/useCases';
import {
  CardsResponse,
  DashboardDetailResponse,
  DashboardResponse,
  MonitorApiError,
  QueryRequest,
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

const emptySidebarFilters: SidebarFilters = {
  gestor: '',
  telefonoCliente: '',
  resolucion: '',
  fecha: '',
};

const parseLimit = (value: string | null): number | undefined => {
  if (!value) {
    return undefined;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return undefined;
  }
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
  if (filters.gestor.trim()) {
    payload.gestor = filters.gestor.trim();
  }
  if (filters.telefonoCliente.trim()) {
    payload.telefono_cliente = filters.telefonoCliente.trim();
  }
  if (filters.resolucion.trim()) {
    payload.resolucion = filters.resolucion.trim();
  }
  if (filters.fecha.trim()) {
    payload.fecha = filters.fecha.trim();
  }
  return Object.keys(payload).length > 0 ? payload : undefined;
};

const buildQueryFromSearchParams = (params: URLSearchParams): QueryRequest => {
  const filtersPayload: Record<string, string> = {};
  const gestor = params.get('gestor');
  const telefonoCliente = params.get('telefono_cliente');
  const resolucion = params.get('resolucion');
  const fecha = params.get('fecha');
  if (gestor) {
    filtersPayload.gestor = gestor;
  }
  if (telefonoCliente) {
    filtersPayload.telefono_cliente = telefonoCliente;
  }
  if (resolucion) {
    filtersPayload.resolucion = resolucion;
  }
  if (fecha) {
    filtersPayload.fecha = fecha;
  }

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
  if (query.timeRange) {
    params.set('timeRange', query.timeRange);
  }
  if (query.search) {
    params.set('search', query.search);
  }
  if (query.limit) {
    params.set('limit', String(query.limit));
  }
  if (typeof query.filters?.gestor === 'string') {
    params.set('gestor', query.filters.gestor);
  }
  if (typeof query.filters?.telefono_cliente === 'string') {
    params.set('telefono_cliente', query.filters.telefono_cliente);
  }
  if (typeof query.filters?.resolucion === 'string') {
    params.set('resolucion', query.filters.resolucion);
  }
  if (typeof query.filters?.fecha === 'string') {
    params.set('fecha', query.filters.fecha);
  }
  return `/monitor?${params.toString()}`;
};

const monitorLayoutCss = `
  .monitor-shell-grid {
    display: grid;
    grid-template-columns: 280px minmax(0, 1fr);
    gap: 16px;
  }
  .monitor-main-stack {
    display: grid;
    gap: 12px;
  }
  @media (max-width: 1100px) {
    .monitor-shell-grid {
      grid-template-columns: 1fr;
    }
  }
`;

const MonitorDashboardPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const styleConfig = defaultMonitorStyle;

  const [cards, setCards] = useState<CardsResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [detail, setDetail] = useState<DashboardDetailResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedRowSnapshot, setSelectedRowSnapshot] = useState<Record<string, unknown> | null>(null);

  const [query, setQuery] = useState<QueryRequest>(() => buildQueryFromSearchParams(searchParams));
  const [sidebarFilters, setSidebarFilters] = useState<SidebarFilters>(() =>
    queryFiltersToSidebar(buildQueryFromSearchParams(searchParams).filters),
  );
  const [selectedUseCase, setSelectedUseCase] = useState<string | undefined>(undefined);

  const [loadingCards, setLoadingCards] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [cardsError, setCardsError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  const casoDeUso = useMemo(() => {
    try {
      return resolveUseCase(searchParams.get('caso_de_uso'), selectedUseCase);
    } catch {
      return resolveUseCase(null, selectedUseCase);
    }
  }, [searchParams, selectedUseCase]);

  const systemLayout = useMemo(() => resolveSystemLayout(casoDeUso), [casoDeUso]);

  const loadCards = async () => {
    setLoadingCards(true);
    setCardsError(null);
    try {
      setCards(await MonitorApi.postCards(casoDeUso, query));
    } catch (error) {
      setCardsError(normalizeErrorMessage(error));
    } finally {
      setLoadingCards(false);
    }
  };

  const loadDashboard = async () => {
    setLoadingDashboard(true);
    setDashboardError(null);
    try {
      setDashboard(await MonitorApi.postDashboard(casoDeUso, query));
    } catch (error) {
      setDashboardError(normalizeErrorMessage(error));
    } finally {
      setLoadingDashboard(false);
    }
  };

  const loadDetail = async (id: string) => {
    setLoadingDetail(true);
    setDetailError(null);
    setSelectedId(id);
    setSelectedRowSnapshot(dashboard?.table.rows.find(row => row.id === id) ?? null);

    try {
      setDetail(await MonitorApi.postDashboardDetail(casoDeUso, id, query));
    } catch (error) {
      setDetailError(normalizeErrorMessage(error));
    } finally {
      setLoadingDetail(false);
    }
  };

  const applySidebarFilters = () => {
    const nextQuery: QueryRequest = {
      ...query,
      cursor: undefined,
      filters: sidebarToQueryFilters(sidebarFilters),
    };
    setQuery(nextQuery);
    navigate(buildMonitorUrl(casoDeUso, nextQuery));
  };

  const resetSidebarFilters = () => {
    setSidebarFilters(emptySidebarFilters);
    const nextQuery: QueryRequest = {
      ...query,
      cursor: undefined,
      search: undefined,
      filters: undefined,
    };
    setQuery(nextQuery);
    navigate(buildMonitorUrl(casoDeUso, nextQuery));
  };

  useEffect(() => {
    const urlQuery = buildQueryFromSearchParams(searchParams);
    setSidebarFilters(queryFiltersToSidebar(urlQuery.filters));
    setQuery(previous => {
      const nextFilters = JSON.stringify(urlQuery.filters ?? {});
      const previousFilters = JSON.stringify(previous.filters ?? {});
      if (
        previous.timeRange === urlQuery.timeRange &&
        previous.search === urlQuery.search &&
        previous.limit === urlQuery.limit &&
        previousFilters === nextFilters
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

  useEffect(() => {
    loadCards();
    loadDashboard();
    setDetail(null);
    setSelectedId(null);
    setSelectedRowSnapshot(null);
  }, [casoDeUso, query]);

  return (
    <main
      style={{
        background: styleConfig.theme.pageBackground,
        color: styleConfig.theme.text,
        minHeight: '100vh',
        padding: 24,
      }}
    >
      <style>{monitorLayoutCss}</style>
      <section
        style={{
          background: `linear-gradient(135deg, ${systemLayout.accent} 0%, ${styleConfig.theme.accent} 100%)`,
          borderRadius: 12,
          color: '#ffffff',
          marginBottom: 14,
          padding: 16,
        }}
      >
        <div style={{ alignItems: 'center', display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
          <div>
            <h1 style={{ marginBottom: 6 }}>{systemLayout.headerTitle}</h1>
            <p style={{ margin: 0, opacity: 0.9 }}>{systemLayout.headerSubtitle}</p>
          </div>
          <button onClick={() => navigate(`/home?caso_de_uso=${casoDeUso}`)}>Home general</button>
        </div>
      </section>

      <div className='monitor-shell-grid'>
        <aside
          style={{
            background: styleConfig.theme.surfaceBackground,
            border: `1px solid ${styleConfig.theme.surfaceBorder}`,
            borderRadius: 10,
            height: 'fit-content',
            padding: 14,
          }}
        >
          <h3 style={{ marginBottom: 6 }}>{systemLayout.sidebarTitle}</h3>
          <p style={{ margin: '0 0 12px 0', fontSize: 13 }}>{systemLayout.sidebarHint}</p>

          <section aria-label='Sistemas monitor' style={{ marginBottom: 12 }}>
            <p style={{ margin: '0 0 6px 0' }}>Sistemas</p>
            <div role='tablist' style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {useCasesConfig
                .filter(item => item.enabled)
                .map(item => {
                  const isActive = item.id === casoDeUso;
                  const systemAccent = resolveSystemLayout(item.id).accent;
                  return (
                    <button
                      key={item.id}
                      role='tab'
                      aria-selected={isActive}
                      onClick={() => {
                        setSelectedUseCase(item.id);
                        navigate(buildMonitorUrl(item.id, query));
                      }}
                      style={{
                        background: isActive ? systemAccent : styleConfig.theme.surfaceBackground,
                        border: `1px solid ${isActive ? systemAccent : styleConfig.theme.surfaceBorder}`,
                        borderRadius: 999,
                        color: isActive ? '#ffffff' : styleConfig.theme.text,
                        padding: '6px 12px',
                      }}
                    >
                      {item.label}
                    </button>
                  );
                })}
            </div>
          </section>

          <label htmlFor='timeRange' style={{ display: 'block', marginBottom: 8 }}>
            <span>Rango temporal</span>
            <input
              id='timeRange'
              style={{ marginTop: 4, width: '100%' }}
              value={query.timeRange ?? ''}
              onChange={event => setQuery({ ...query, timeRange: event.target.value })}
            />
          </label>

          <label htmlFor='search' style={{ display: 'block', marginBottom: 8 }}>
            <span>Buscar</span>
            <input
              id='search'
              style={{ marginTop: 4, width: '100%' }}
              value={query.search ?? ''}
              onChange={event => setQuery({ ...query, search: event.target.value || undefined })}
            />
          </label>

          <label htmlFor='limit' style={{ display: 'block', marginBottom: 8 }}>
            <span>Límite</span>
            <input
              id='limit'
              style={{ marginTop: 4, width: '100%' }}
              type='number'
              min={1}
              value={query.limit ?? ''}
              onChange={event => setQuery({ ...query, limit: parseLimit(event.target.value) })}
            />
          </label>

          <label htmlFor='gestor' style={{ display: 'block', marginBottom: 8 }}>
            <span>Gestor</span>
            <input
              id='gestor'
              style={{ marginTop: 4, width: '100%' }}
              value={sidebarFilters.gestor}
              onChange={event => setSidebarFilters({ ...sidebarFilters, gestor: event.target.value })}
            />
          </label>

          <label htmlFor='telefonoCliente' style={{ display: 'block', marginBottom: 8 }}>
            <span>Teléfono cliente</span>
            <input
              id='telefonoCliente'
              style={{ marginTop: 4, width: '100%' }}
              value={sidebarFilters.telefonoCliente}
              onChange={event => setSidebarFilters({ ...sidebarFilters, telefonoCliente: event.target.value })}
            />
          </label>

          <label htmlFor='resolucion' style={{ display: 'block', marginBottom: 8 }}>
            <span>Resolución</span>
            <input
              id='resolucion'
              style={{ marginTop: 4, width: '100%' }}
              value={sidebarFilters.resolucion}
              onChange={event => setSidebarFilters({ ...sidebarFilters, resolucion: event.target.value })}
            />
          </label>

          <label htmlFor='fecha' style={{ display: 'block', marginBottom: 12 }}>
            <span>Fecha</span>
            <input
              id='fecha'
              style={{ marginTop: 4, width: '100%' }}
              value={sidebarFilters.fecha}
              onChange={event => setSidebarFilters({ ...sidebarFilters, fecha: event.target.value })}
            />
          </label>

          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={applySidebarFilters}>Aplicar filtros</button>
            <button onClick={resetSidebarFilters}>Limpiar filtros</button>
          </div>
        </aside>

        <section className='monitor-main-stack'>
          <section
            style={{
              background: styleConfig.theme.surfaceBackground,
              border: `1px solid ${styleConfig.theme.surfaceBorder}`,
              borderRadius: 10,
              padding: 12,
            }}
          >
            <h2 style={{ marginBottom: 10 }}>Resumen de cards</h2>
            <CardsGrid data={cards} loading={loadingCards} error={cardsError} onRefresh={loadCards} view={styleConfig} />
          </section>

          <section
            style={{
              background: styleConfig.theme.surfaceBackground,
              border: `1px solid ${styleConfig.theme.surfaceBorder}`,
              borderRadius: 10,
              padding: 12,
            }}
          >
            <h2 style={{ marginBottom: 10 }}>{systemLayout.tableTitle}</h2>
            <DynamicTable
              data={dashboard}
              loading={loadingDashboard}
              error={dashboardError}
              query={query}
              onQueryChange={setQuery}
              onOpenDetail={loadDetail}
              view={styleConfig}
            />
          </section>
        </section>
      </div>

      <DashboardDetail
        data={detail}
        loading={loadingDetail}
        error={detailError}
        selectedId={selectedId}
        selectedRowSnapshot={selectedRowSnapshot}
        onClose={() => setSelectedId(null)}
        view={styleConfig}
      />
    </main>
  );
};

export default MonitorDashboardPage;
