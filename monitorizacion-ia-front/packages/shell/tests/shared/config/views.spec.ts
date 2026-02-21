import { resolveView, viewsConfig } from '#/shell/shared/config/views';

describe('views config', () => {
  test('prioriza query param cuando es valido', () => {
    expect(resolveView('supervision', 'operativa').id).toBe('supervision');
  });

  test('usa selected cuando no hay query', () => {
    expect(resolveView(null, 'ejecutiva').id).toBe('ejecutiva');
  });

  test('usa default cuando no hay query ni selected', () => {
    const expectedDefault = viewsConfig.find(item => item.default && item.enabled)?.id ?? viewsConfig[0].id;
    expect(resolveView(null, undefined).id).toBe(expectedDefault);
  });
});
