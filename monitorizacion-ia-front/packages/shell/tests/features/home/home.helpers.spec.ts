import { buildMonitorUrl, resolveInitialUseCase } from '#/shell/features/home/home.helpers';

describe('home helpers', () => {
  test('buildMonitorUrl arma query con caso_de_uso y timeRange', () => {
    expect(buildMonitorUrl('hipotecas')).toBe('/monitor?caso_de_uso=hipotecas&timeRange=24h');
  });

  test('resolveInitialUseCase usa default cuando query es invalida', () => {
    const params = new URLSearchParams('caso_de_uso=no-valido');
    expect(resolveInitialUseCase(params)).toBe('hipotecas');
  });
});
