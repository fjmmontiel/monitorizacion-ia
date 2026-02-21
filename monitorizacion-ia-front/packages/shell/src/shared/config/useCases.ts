import { z } from 'zod';

import { MonitorApiError } from '../contracts/monitor.contracts';

export type UseCaseConfig = {
  id: string;
  label: string;
  enabled: boolean;
  default?: boolean;
};

export const useCasesConfig: UseCaseConfig[] = [
  { id: 'hipotecas', label: 'Hipotecas', enabled: true, default: true },
  { id: 'prestamos', label: 'Préstamos', enabled: true },
];

const allowedUseCases = useCasesConfig.filter(item => item.enabled).map(item => item.id);

const useCaseSchema = z.string().refine(value => allowedUseCases.includes(value), {
  message: 'UNKNOWN_USE_CASE',
});

export const resolveUseCase = (
  queryValue: string | null,
  selectedValue: string | undefined,
): string => {
  const defaultUseCase = useCasesConfig.find(item => item.default && item.enabled)?.id ?? allowedUseCases[0];

  const candidate = queryValue ?? selectedValue ?? defaultUseCase;
  const parsed = useCaseSchema.safeParse(candidate);

  if (!parsed.success) {
    throw new MonitorApiError('UNKNOWN_USE_CASE', `Use case not allowed: ${candidate}`);
  }

  return parsed.data;
};

export const isAllowedUseCase = (candidate: string) => useCaseSchema.safeParse(candidate).success;
