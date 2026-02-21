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

const normalizeErrorMessage = (error: unknown) => {
  if (error instanceof MonitorApiError) {
    return `${error.code}: ${error.message}`;
  }
  return 'INTERNAL_ERROR: Unexpected error';
};

const MonitorDashboardPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [cards, setCards] = useState<CardsResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [detail, setDetail] = useState<DashboardDetailResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [query, setQuery] = useState<QueryRequest>({ timeRange: '24h' });

  const [loadingCards, setLoadingCards] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [cardsError, setCardsError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  const casoDeUso = useMemo(
    () => resolveUseCase(searchParams.get('caso_de_uso'), undefined),
    [searchParams],
  );

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
    loadDashboard();
  }, [query]);

  return (
    <main style={{ padding: 24 }}>
      <h1>Monitor dashboard</h1>
      <label htmlFor='caso_de_uso'>Caso de uso</label>
      <select
        id='caso_de_uso'
        value={casoDeUso}
        onChange={event => navigate(`/monitor?caso_de_uso=${event.target.value}`)}
      >
        {useCasesConfig.filter(item => item.enabled).map(item => (
          <option key={item.id} value={item.id}>
            {item.label}
          </option>
        ))}
      </select>

      <CardsGrid data={cards} loading={loadingCards} error={cardsError} onRefresh={loadCards} />
      <DynamicTable
        data={dashboard}
        loading={loadingDashboard}
        error={dashboardError}
        query={query}
        onQueryChange={setQuery}
        onOpenDetail={loadDetail}
      />
      <DashboardDetail
        data={detail}
        loading={loadingDetail}
        error={detailError}
        selectedId={selectedId}
        onClose={() => setSelectedId(null)}
      />
    </main>
  );
};

export default MonitorDashboardPage;
