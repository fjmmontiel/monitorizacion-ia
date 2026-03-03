import { envVariables } from '#/shell/config/env';
import {
  CardsResponse,
  DatopsOverviewResponse,
  DashboardDetailResponse,
  DashboardResponse,
  MonitorApiError,
  QueryRequest,
  UIShellResponse,
  ViewConfiguration,
  cardsResponseSchema,
  datopsOverviewResponseSchema,
  dashboardDetailResponseSchema,
  dashboardResponseSchema,
  queryRequestSchema,
  uiShellResponseSchema,
  viewConfigurationListSchema,
  viewConfigurationSchema,
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
  if (!casoDeUso.trim()) {
    throw new MonitorApiError('VALIDATION_ERROR', 'caso_de_uso is required');
  }
};

const buildUrl = (path: string, params: Record<string, string>) => {
  const url = new URL(path, envVariables.MONITOR_API_BASE_URL);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  return url.toString();
};

const request = async <T>(
  url: string,
  body?: unknown,
  method: 'POST' | 'GET' | 'PUT' | 'DELETE' = 'POST',
): Promise<T> => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: method === 'GET' || method === 'DELETE' ? undefined : JSON.stringify(body ?? {}),
      signal: controller.signal,
    });

    if (!response.ok) {
      let payload: { code?: string; message?: string; detail?: string } | undefined;
      try {
        payload = (await response.json()) as { code?: string; message?: string; detail?: string };
      } catch {
        payload = undefined;
      }
      throw new MonitorApiError(
        mapBackendErrorCode(payload?.code),
        payload?.message ?? payload?.detail ?? `HTTP ${response.status}`,
      );
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } catch (error) {
    throw normalizeError(error);
  } finally {
    clearTimeout(timeout);
  }
};

export const MonitorApi = {
  async postCards(casoDeUso: string, body?: QueryRequest): Promise<CardsResponse> {
    assertUseCase(casoDeUso);
    assertQuery(body);
    const payload = await request<CardsResponse>(buildUrl('/cards', { caso_de_uso: casoDeUso }), body);
    return cardsResponseSchema.parse(payload);
  },

  async postDashboard(casoDeUso: string, body?: QueryRequest): Promise<DashboardResponse> {
    assertUseCase(casoDeUso);
    assertQuery(body);
    const payload = await request<DashboardResponse>(buildUrl('/dashboard', { caso_de_uso: casoDeUso }), body);
    return dashboardResponseSchema.parse(payload);
  },

  async postDashboardDetail(casoDeUso: string, id: string, body?: QueryRequest): Promise<DashboardDetailResponse> {
    assertUseCase(casoDeUso);
    if (!id) {
      throw new MonitorApiError('VALIDATION_ERROR', 'id is required');
    }
    assertQuery(body);
    const payload = await request<DashboardDetailResponse>(
      buildUrl('/dashboard_detail', { caso_de_uso: casoDeUso, id }),
      body,
    );
    return dashboardDetailResponseSchema.parse(payload);
  },

  async getDatopsOverview(): Promise<DatopsOverviewResponse> {
    const payload = await request<DatopsOverviewResponse>(buildUrl('/datops/overview', {}), undefined, 'GET');
    return datopsOverviewResponseSchema.parse(payload);
  },

  async getUIShell(): Promise<UIShellResponse> {
    const payload = await request<UIShellResponse>(buildUrl('/ui/shell', {}), undefined, 'GET');
    return uiShellResponseSchema.parse(payload);
  },

  async getViewConfigurations(filters?: { system?: string; enabled?: boolean }): Promise<ViewConfiguration[]> {
    const params: Record<string, string> = {};
    if (filters?.system) {
      params.system = filters.system;
    }
    if (typeof filters?.enabled === 'boolean') {
      params.enabled = String(filters.enabled);
    }
    const payload = await request<ViewConfiguration[]>(buildUrl('/admin/view-configs', params), undefined, 'GET');
    return viewConfigurationListSchema.parse(payload);
  },

  async createViewConfiguration(body: ViewConfiguration): Promise<ViewConfiguration> {
    const payload = await request<ViewConfiguration>(buildUrl('/admin/view-configs', {}), body);
    return viewConfigurationSchema.parse(payload);
  },

  async updateViewConfiguration(viewId: string, body: Partial<ViewConfiguration>): Promise<ViewConfiguration> {
    const payload = await request<ViewConfiguration>(
      buildUrl(`/admin/view-configs/${viewId}`, {}),
      body,
      'PUT',
    );
    return viewConfigurationSchema.parse(payload);
  },

  async deleteViewConfiguration(viewId: string): Promise<void> {
    await request(buildUrl(`/admin/view-configs/${viewId}`, {}), undefined, 'DELETE');
  },
};
