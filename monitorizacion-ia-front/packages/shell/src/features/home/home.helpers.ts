import { resolveUseCase } from '#/shell/shared/config/useCases';

export const resolveInitialUseCase = (searchParams: URLSearchParams): string => {
  try {
    return resolveUseCase(searchParams.get('caso_de_uso'), undefined);
  } catch {
    return resolveUseCase(null, undefined);
  }
};

export const buildMonitorUrl = (casoDeUso: string) => {
  const params = new URLSearchParams();
  params.set('caso_de_uso', casoDeUso);
  params.set('timeRange', '24h');
  return `/monitor?${params.toString()}`;
};
