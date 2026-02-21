import { z } from 'zod';

import { MonitorApiError } from '../contracts/monitor.contracts';

export type UseCaseConfig = {
  id: string;
  label: string;
  enabled: boolean;
  default?: boolean;
};

const useCaseConfigSchema = z.array(
  z.object({
    id: z.string().min(1),
    label: z.string().min(1),
    enabled: z.boolean(),
    default: z.boolean().optional(),
  }),
);

// eslint-disable-next-line @typescript-eslint/no-var-requires
const rawUseCases = require('./use_cases.json') as unknown;

export const useCasesConfig = useCaseConfigSchema.parse(rawUseCases) as UseCaseConfig[];

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
