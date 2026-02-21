import { MonitorApi } from '#/shell/shared/api/MonitorApi';

describe('MonitorApi mock mode', () => {
  test('carga cards para hipotecas', async () => {
    const payload = await MonitorApi.postCards('hipotecas', { timeRange: '24h' });
    expect(payload.cards.length).toBeGreaterThan(0);
  });

  test('carga dashboard con columnas id/detail', async () => {
    const payload = await MonitorApi.postDashboard('prestamos', { timeRange: '24h' });
    const keys = payload.table.columns.map(col => col.key);
    expect(keys).toContain('id');
    expect(keys).toContain('detail');
  });
});
