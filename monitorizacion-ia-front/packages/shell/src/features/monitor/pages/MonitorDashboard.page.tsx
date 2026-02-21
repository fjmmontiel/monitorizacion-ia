import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { MonitorApi } from '#/shell/shared/api/MonitorApi';
import { CardsGrid } from '#/shell/features/monitor/components/CardsGrid/CardsGrid';
import { DashboardDetail } from '#/shell/features/monitor/components/DashboardDetail/DashboardDetail';
import { DynamicTable } from '#/shell/features/monitor/components/DynamicTable/DynamicTable';
import {
  CardsResponse,
  DashboardDetailResponse,
  DashboardResponse,
  MonitorApiError,
  QueryRequest,
} from '#/shell/shared/contracts/monitor.contracts';
import { resolveUseCase, useCasesConfig } from '#/shell/shared/config/useCases';
import { resolveView, viewsConfig } from '#/shell/shared/config/views';

const normalizeErrorMessage = (error: unknown) => {
  if (error instanceof MonitorApiError) {
    return `${error.code}: ${error.message}`;
  }
  return 'INTERNAL_ERROR: Unexpected error';
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

const buildQueryFromSearchParams = (params: URLSearchParams): QueryRequest => ({
  timeRange: params.get('timeRange') ?? '24h',
  search: params.get('search') ?? undefined,
  limit: parseLimit(params.get('limit')),
});

const buildMonitorUrl = (casoDeUso: string, vista: string, query: QueryRequest) => {
  const params = new URLSearchParams();
  params.set('caso_de_uso', casoDeUso);
  params.set('vista', vista);
  if (query.timeRange) {
    params.set('timeRange', query.timeRange);
  }
  if (query.search) {
    params.set('search', query.search);
  }
  if (query.limit) {
    params.set('limit', String(query.limit));
  }
  return `/monitor?${params.toString()}`;
};

const MonitorDashboardPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [cards, setCards] = useState<CardsResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [detail, setDetail] = useState<DashboardDetailResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [query, setQuery] = useState<QueryRequest>(() => buildQueryFromSearchParams(searchParams));
  const [selectedUseCase, setSelectedUseCase] = useState<string | undefined>(undefined);
  const [selectedView, setSelectedView] = useState<string | undefined>(undefined);

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

  const vista = useMemo(() => {
    try {
      return resolveView(searchParams.get('vista'), selectedView);
    } catch {
      return resolveView(null, selectedView);
    }
  }, [searchParams, selectedView]);

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

    try {
      setDetail(await MonitorApi.postDashboardDetail(casoDeUso, id, query));
    } catch (error) {
      setDetailError(normalizeErrorMessage(error));
    } finally {
      setLoadingDetail(false);
    }
  };

  useEffect(() => {
    loadCards();
    loadDashboard();
  }, [casoDeUso]);

  useEffect(() => {
    const urlQuery = buildQueryFromSearchParams(searchParams);
    setQuery(previous => {
      if (
        previous.timeRange === urlQuery.timeRange &&
        previous.search === urlQuery.search &&
        previous.limit === urlQuery.limit
      ) {
        return previous;
      }
      return {
        ...previous,
        timeRange: urlQuery.timeRange,
        search: urlQuery.search,
        limit: urlQuery.limit,
      };
    });
  }, [searchParams]);

  useEffect(() => {
    loadDashboard();
  }, [query]);

  return (
    <main style={{ background: vista.theme.pageBackground, color: vista.theme.text, minHeight: '100vh', padding: 24 }}>
      <h1>{vista.pageTitle}</h1>
      {vista.description && <p>{vista.description}</p>}
      <div
        style={{
          background: vista.theme.surfaceBackground,
          border: `1px solid ${vista.theme.surfaceBorder}`,
          borderRadius: 8,
          display: 'flex',
          flexWrap: 'wrap',
          gap: 12,
          marginBottom: 12,
          padding: 12,
        }}
      >
        <section aria-label='Sistemas monitor'>
          <p style={{ margin: '0 0 6px 0' }}>Sistemas</p>
          <div role='tablist' style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {useCasesConfig
              .filter(item => item.enabled)
              .map(item => {
                const isActive = item.id === casoDeUso;
                return (
                  <button
                    key={item.id}
                    role='tab'
                    aria-selected={isActive}
                    onClick={() => {
                      setSelectedUseCase(item.id);
                      navigate(buildMonitorUrl(item.id, vista.id, query));
                    }}
                    style={{
                      background: isActive ? vista.theme.accent : vista.theme.surfaceBackground,
                      border: `1px solid ${vista.theme.surfaceBorder}`,
                      borderRadius: 999,
                      color: isActive ? '#ffffff' : vista.theme.text,
                      padding: '6px 12px',
                    }}
                  >
                    {item.label}
                  </button>
                );
              })}
          </div>
        </section>
        <label htmlFor='vista'>
          <span>Vista</span>
          <select
            id='vista'
            value={vista.id}
            onChange={event => {
              setSelectedView(event.target.value);
              navigate(buildMonitorUrl(casoDeUso, event.target.value, query));
            }}
          >
            {viewsConfig.filter(item => item.enabled).map(item => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        <label htmlFor='timeRange'>
          <span>timeRange</span>
          <input
            id='timeRange'
            value={query.timeRange ?? ''}
            onChange={event => setQuery({ ...query, timeRange: event.target.value })}
          />
        </label>
        <label htmlFor='search'>
          <span>search</span>
          <input
            id='search'
            value={query.search ?? ''}
            onChange={event => setQuery({ ...query, search: event.target.value || undefined })}
          />
        </label>
        <label htmlFor='limit'>
          <span>limit</span>
          <input
            id='limit'
            type='number'
            min={1}
            value={query.limit ?? ''}
            onChange={event => setQuery({ ...query, limit: parseLimit(event.target.value) })}
          />
        </label>
        <button onClick={() => navigate(buildMonitorUrl(casoDeUso, vista.id, query))}>Aplicar query params</button>
      </div>

      <CardsGrid data={cards} loading={loadingCards} error={cardsError} onRefresh={loadCards} view={vista} />
      <DynamicTable
        data={dashboard}
        loading={loadingDashboard}
        error={dashboardError}
        query={query}
        onQueryChange={setQuery}
        onOpenDetail={loadDetail}
        view={vista}
      />
      <DashboardDetail
        data={detail}
        loading={loadingDetail}
        error={detailError}
        selectedId={selectedId}
        onClose={() => setSelectedId(null)}
        view={vista}
      />
    </main>
  );
};

export default MonitorDashboardPage;
