import { envVariables } from '#/shell/config/env';
import { cardsFixture } from '#/shell/features/monitor/fixtures/default/cards';
import { dashboardFixture } from '#/shell/features/monitor/fixtures/default/dashboard';
import { dashboardDetailFixture } from '#/shell/features/monitor/fixtures/default/dashboardDetail';
import {
  CardsResponse,
  DashboardDetailResponse,
  DashboardResponse,
  MonitorApiError,
  QueryRequest,
  cardsResponseSchema,
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

const assertQuery = (body?: QueryRequest) => {
  if (!body) {
    return;
  }

  const parsed = queryRequestSchema.safeParse(body);
  if (!parsed.success) {
    throw new MonitorApiError('VALIDATION_ERROR', parsed.error.message);
  }
};

const buildUrl = (path: string, params: Record<string, string>) => {
  const url = new URL(path, envVariables.MONITOR_API_BASE_URL);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  return url.toString();
};

const request = async <T>(url: string, body?: QueryRequest): Promise<T> => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body ?? {}),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new MonitorApiError('UPSTREAM_ERROR', `HTTP ${response.status}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    throw normalizeError(error);
  } finally {
    clearTimeout(timeout);
  }
};

const inMockMode = envVariables.REACT_APP_MONITOR_MOCK_MODE;

export const MonitorApi = {
  async postCards(casoDeUso: string, body?: QueryRequest): Promise<CardsResponse> {
    assertQuery(body);
    if (inMockMode) {
      return cardsResponseSchema.parse(cardsFixture);
    }

    const payload = await request<CardsResponse>(buildUrl('/cards', { caso_de_uso: casoDeUso }), body);
    return cardsResponseSchema.parse(payload);
  },

  async postDashboard(casoDeUso: string, body?: QueryRequest): Promise<DashboardResponse> {
    assertQuery(body);
    if (inMockMode) {
      return dashboardResponseSchema.parse(dashboardFixture);
    }

    const payload = await request<DashboardResponse>(buildUrl('/dashboard', { caso_de_uso: casoDeUso }), body);
    return dashboardResponseSchema.parse(payload);
  },

  async postDashboardDetail(casoDeUso: string, id: string, body?: QueryRequest): Promise<DashboardDetailResponse> {
    assertQuery(body);
    if (inMockMode) {
      return dashboardDetailResponseSchema.parse(dashboardDetailFixture);
    }

    const payload = await request<DashboardDetailResponse>(
      buildUrl('/dashboard_detail', { caso_de_uso: casoDeUso, id }),
      body,
    );
    return dashboardDetailResponseSchema.parse(payload);
  },
};
