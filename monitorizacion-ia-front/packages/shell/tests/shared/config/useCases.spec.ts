import { MonitorApiError } from '#/shell/shared/contracts/monitor.contracts';
import { resolveUseCase, useCasesConfig } from '#/shell/shared/config/useCases';

describe('useCases config', () => {
  test('prioriza query param cuando es valido', () => {
    expect(resolveUseCase('prestamos', 'hipotecas')).toBe('prestamos');
  });

  test('usa selected cuando no hay query', () => {
    expect(resolveUseCase(null, 'prestamos')).toBe('prestamos');
  });

  test('usa default cuando no hay query ni selected', () => {
    const expectedDefault = useCasesConfig.find(item => item.default && item.enabled)?.id ?? useCasesConfig[0].id;
    expect(resolveUseCase(null, undefined)).toBe(expectedDefault);
  });

  test('lanza UNKNOWN_USE_CASE para query invalido', () => {
    expect(() => resolveUseCase('no-existe', undefined)).toThrow(MonitorApiError);
  });
});
