import { resolveSystemLayout } from '#/shell/features/monitor/config/systemLayouts';

describe('system layouts', () => {
  test('resuelve layout específico de hipotecas', () => {
    const layout = resolveSystemLayout('hipotecas');
    expect(layout.headerTitle).toContain('hipotecas');
    expect(layout.tableTitle).toContain('Historial');
  });

  test('aplica fallback para sistema desconocido', () => {
    const layout = resolveSystemLayout('sistema-x');
    expect(layout.id).toBe('sistema-x');
    expect(layout.headerTitle).toContain('sistema-x');
  });
});
