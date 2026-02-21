import { envVariables } from '#/shell/config/env';
import { getFixtureByUseCase } from '#/shell/features/monitor/fixtures';
import { isAllowedUseCase, useCasesConfig } from '#/shell/shared/config/useCases';
import {
  CardsResponse,
  DatopsOverviewResponse,
  DashboardDetailResponse,
  DashboardResponse,
  MonitorApiError,
  QueryRequest,
  cardsResponseSchema,
  datopsOverviewResponseSchema,
  dashboardDetailResponseSchema,
  dashboardResponseSchema,
  queryRequestSchema,
} from '#/shell/shared/contracts/monitor.contracts';

const normalizeError = (error: unknown): MonitorApiError => {
  if (error instanceof MonitorApiError) {
    return error;
  }

  if (error instanceof Error && error.name === 'AbortError') {
    return new MonitorApiError('UPSTREAM_TIMEOUT', 'The upstream request timed out');
  }

  return new MonitorApiError('INTERNAL_ERROR', 'Unexpected monitor API error');
};

const mapBackendErrorCode = (code?: string): MonitorApiError['code'] => {
  switch (code) {
    case 'UNKNOWN_USE_CASE':
      return 'UNKNOWN_USE_CASE';
    case 'VALIDATION_ERROR':
      return 'VALIDATION_ERROR';
    case 'UPSTREAM_TIMEOUT':
      return 'UPSTREAM_TIMEOUT';
    case 'UPSTREAM_ERROR':
      return 'UPSTREAM_ERROR';
    default:
      return 'INTERNAL_ERROR';
  }
};

const assertQuery = (body?: QueryRequest) => {
  if (!body) {
    return;
  }

  const parsed = queryRequestSchema.safeParse(body);
  if (!parsed.success) {
    throw new MonitorApiError('VALIDATION_ERROR', parsed.error.message);
  }
};

const assertUseCase = (casoDeUso: string) => {
  if (!isAllowedUseCase(casoDeUso)) {
    throw new MonitorApiError('UNKNOWN_USE_CASE', `Use case not allowed: ${casoDeUso}`);
  }
};

const buildUrl = (path: string, params: Record<string, string>) => {
  const url = new URL(path, envVariables.MONITOR_API_BASE_URL);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  return url.toString();
};

const request = async <T>(url: string, body?: QueryRequest, method: 'POST' | 'GET' = 'POST'): Promise<T> => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: method === 'POST' ? JSON.stringify(body ?? {}) : undefined,
      signal: controller.signal,
    });

    if (!response.ok) {
      let payload: { code?: string; message?: string } | undefined;
      try {
        payload = (await response.json()) as { code?: string; message?: string };
      } catch {
        payload = undefined;
      }
      throw new MonitorApiError(
        mapBackendErrorCode(payload?.code),
        payload?.message ?? `HTTP ${response.status}`,
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    throw normalizeError(error);
  } finally {
    clearTimeout(timeout);
  }
};

const inMockMode = envVariables.REACT_APP_MONITOR_MOCK_MODE;
const enableFailoverToMock = envVariables.REACT_APP_MONITOR_FAILOVER_TO_MOCK;

const getMockDatopsOverview = (): DatopsOverviewResponse =>
  datopsOverviewResponseSchema.parse({
    schema_version: 'v1',
    generated_at: new Date().toISOString(),
    profile: 'local-mock',
    use_cases: useCasesConfig
      .filter(item => item.enabled)
      .map(item => ({
        id: item.id,
        adapter: 'native',
        timeout_ms: 2500,
        upstream_base_url: null,
        routes: {
          cards: `/cards?caso_de_uso=${item.id}`,
          dashboard: `/dashboard?caso_de_uso=${item.id}`,
          dashboard_detail: `/dashboard_detail?caso_de_uso=${item.id}&id={id}`,
        },
      })),
  });

export const MonitorApi = {
  async postCards(casoDeUso: string, body?: QueryRequest): Promise<CardsResponse> {
    assertUseCase(casoDeUso);
    assertQuery(body);
    if (inMockMode) {
      return cardsResponseSchema.parse(getFixtureByUseCase(casoDeUso).cards);
    }
    try {
      const payload = await request<CardsResponse>(buildUrl('/cards', { caso_de_uso: casoDeUso }), body);
      return cardsResponseSchema.parse(payload);
    } catch (error) {
      if (enableFailoverToMock) {
        return cardsResponseSchema.parse(getFixtureByUseCase(casoDeUso).cards);
      }
      throw normalizeError(error);
    }
  },

  async postDashboard(casoDeUso: string, body?: QueryRequest): Promise<DashboardResponse> {
    assertUseCase(casoDeUso);
    assertQuery(body);
    if (inMockMode) {
      return dashboardResponseSchema.parse(getFixtureByUseCase(casoDeUso).dashboard);
    }
    try {
      const payload = await request<DashboardResponse>(buildUrl('/dashboard', { caso_de_uso: casoDeUso }), body);
      return dashboardResponseSchema.parse(payload);
    } catch (error) {
      if (enableFailoverToMock) {
        return dashboardResponseSchema.parse(getFixtureByUseCase(casoDeUso).dashboard);
      }
      throw normalizeError(error);
    }
  },

  async postDashboardDetail(casoDeUso: string, id: string, body?: QueryRequest): Promise<DashboardDetailResponse> {
    assertUseCase(casoDeUso);
    if (!id) {
      throw new MonitorApiError('VALIDATION_ERROR', 'id is required');
    }
    assertQuery(body);
    if (inMockMode) {
      return dashboardDetailResponseSchema.parse(getFixtureByUseCase(casoDeUso).dashboardDetail);
    }
    try {
      const payload = await request<DashboardDetailResponse>(
        buildUrl('/dashboard_detail', { caso_de_uso: casoDeUso, id }),
        body,
      );
      return dashboardDetailResponseSchema.parse(payload);
    } catch (error) {
      if (enableFailoverToMock) {
        return dashboardDetailResponseSchema.parse(getFixtureByUseCase(casoDeUso).dashboardDetail);
      }
      throw normalizeError(error);
    }
  },

  async getDatopsOverview(): Promise<DatopsOverviewResponse> {
    if (inMockMode) {
      return getMockDatopsOverview();
    }
    try {
      const payload = await request<DatopsOverviewResponse>(buildUrl('/datops/overview', {}), undefined, 'GET');
      return datopsOverviewResponseSchema.parse(payload);
    } catch (error) {
      if (enableFailoverToMock) {
        return getMockDatopsOverview();
      }
      throw normalizeError(error);
    }
  },
};
