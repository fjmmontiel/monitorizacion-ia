import { z } from 'zod';

import { MonitorApiError } from '../contracts/monitor.contracts';

export type ViewConfig = {
  id: string;
  label: string;
  enabled: boolean;
  default?: boolean;
  pageTitle: string;
  description?: string;
  theme: {
    pageBackground: string;
    surfaceBackground: string;
    surfaceBorder: string;
    accent: string;
    text: string;
  };
  cards: {
    columns: number;
    showSubtitle: boolean;
    titleAliases: Record<string, string>;
  };
};

const viewsConfigSchema = z.array(
  z.object({
    id: z.string().min(1),
    label: z.string().min(1),
    enabled: z.boolean(),
    default: z.boolean().optional(),
    pageTitle: z.string().min(1),
    description: z.string().optional(),
    theme: z.object({
      pageBackground: z.string().min(1),
      surfaceBackground: z.string().min(1),
      surfaceBorder: z.string().min(1),
      accent: z.string().min(1),
      text: z.string().min(1),
    }),
    cards: z.object({
      columns: z.number().int().min(1).max(4),
      showSubtitle: z.boolean(),
      titleAliases: z.record(z.string(), z.string()),
    }),
  }),
);

// eslint-disable-next-line @typescript-eslint/no-var-requires
const rawViews = require('./views.json') as unknown;

export const viewsConfig = viewsConfigSchema.parse(rawViews) as ViewConfig[];

const allowedViews = viewsConfig.filter(view => view.enabled).map(view => view.id);

const viewSchema = z.string().refine(value => allowedViews.includes(value), {
  message: 'UNKNOWN_VIEW',
});

export const resolveView = (queryValue: string | null, selectedValue: string | undefined): ViewConfig => {
  const defaultView = viewsConfig.find(view => view.default && view.enabled)?.id ?? allowedViews[0];
  const candidate = queryValue ?? selectedValue ?? defaultView;
  const parsed = viewSchema.safeParse(candidate);

  if (!parsed.success) {
    throw new MonitorApiError('VALIDATION_ERROR', `View not allowed: ${candidate}`);
  }

  return viewsConfig.find(view => view.id === parsed.data) as ViewConfig;
};

export const isAllowedView = (candidate: string) => viewSchema.safeParse(candidate).success;
