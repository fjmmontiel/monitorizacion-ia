import { MonitorApi } from '#/shell/shared/api/MonitorApi';

const fetchMock = jest.fn();

const buildResponse = (payload: unknown, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: async () => payload,
});

describe('MonitorApi backend mode', () => {
  beforeEach(() => {
    fetchMock.mockReset();
    global.fetch = fetchMock as unknown as typeof fetch;
  });

  test('carga cards desde backend', async () => {
    fetchMock.mockResolvedValue(buildResponse({
      cards: [
        { title: 'Conversaciones', value: 12, format: 'int', unit: null, variant: 'neutral' },
        { invalid: true },
      ],
    }));

    const payload = await MonitorApi.postCards('hipotecas', { timeRange: '24h' });

    expect(payload.cards.length).toBe(2);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('carga dashboard con columnas id/detail', async () => {
    fetchMock.mockResolvedValue(buildResponse({
      table: {
        columns: [
          { key: 'id', label: 'Id', filterable: null, sortable: true },
          { key: 'detail', label: 'Detalle', filterable: null, sortable: null },
        ],
        rows: [
          { id: 'pres-1', detail: { action: 'Ver detalle' } },
        ],
      },
    }));

    const payload = await MonitorApi.postDashboard('prestamos', { timeRange: '24h' });
    const keys = payload.table.columns.map(col => col.key);

    expect(keys).toContain('id');
    expect(keys).toContain('detail');
  });

  test('carga shell ui', async () => {
    fetchMock.mockResolvedValue(buildResponse({
      schema_version: 'v1',
      generated_at: '2026-03-02T10:00:00Z',
      home: { id: 'home', label: 'HOME', path: '/home' },
      systems: [
        {
          id: 'hipotecas',
          label: 'Hipotecas',
          default: true,
          route_path: '/monitor?caso_de_uso=hipotecas',
          view: {
            id: 'vista-hipotecas',
            name: 'Hipotecas · Operativa',
            system: 'hipotecas',
            enabled: true,
            components: [
              {
                id: 'layout-root',
                type: 'stack',
                title: 'Layout',
                data_source: '/none',
                position: 0,
                config: null,
                children: [
                  { id: 'cards', type: 'cards', title: 'KPIs', data_source: '/cards', position: 0, config: null, children: null },
                ],
              },
            ],
          },
        },
      ],
    }));

    const payload = await MonitorApi.getUIShell();

    expect(payload.home.label).toBe('HOME');
    expect(payload.systems[0].view.components[0].type).toBe('stack');
  });
});
