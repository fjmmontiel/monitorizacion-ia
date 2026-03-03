import { buildDefaultViewComponents } from '#/shell/features/admin/pages/AdminViews.page';

describe('AdminViews buildDefaultViewComponents', () => {
  test('genera una estructura base válida para una vista nueva', () => {
    const components = buildDefaultViewComponents('seguros', 'Seguros · Operativa');

    expect(components).toHaveLength(1);
    expect(components[0].type).toBe('stack');
    expect(components[0].children).toHaveLength(2);
    expect(components[0].children?.[0].type).toBe('cards');
    expect(components[0].children?.[1].type).toBe('table');
  });
});
