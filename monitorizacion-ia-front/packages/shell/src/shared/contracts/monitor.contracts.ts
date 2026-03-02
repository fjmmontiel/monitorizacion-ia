import { z } from 'zod';

export const queryRequestSchema = z.object({
  timeRange: z.string().optional(),
  filters: z.record(z.string(), z.union([z.string(), z.number(), z.boolean(), z.null()])).optional(),
  search: z.string().optional(),
  sort: z
    .array(
      z.object({
        field: z.string(),
        direction: z.enum(['asc', 'desc']),
      }),
    )
    .optional(),
  cursor: z.string().optional(),
  limit: z.number().int().positive().optional(),
});

const cardSchema = z.object({
  title: z.string(),
  subtitle: z.string().optional(),
  value: z.union([z.string(), z.number()]),
  format: z.enum(['seconds', 'percent', 'currencyEUR', 'int', 'float']).optional(),
});

const tableColumnSchema = z.object({
  key: z.string(),
  label: z.string(),
  filterable: z.boolean().optional(),
  sortable: z.boolean().optional(),
});

const tableRowSchema = z
  .object({
    id: z.string(),
    detail: z.object({
      action: z.string().default('Ver detalle'),
    }),
  })
  .and(z.record(z.string(), z.unknown()));

export const cardsResponseSchema = z.object({
  cards: z.array(cardSchema),
});

export const dashboardResponseSchema = z.object({
  table: z.object({
    columns: z.array(tableColumnSchema),
    rows: z.array(tableRowSchema),
    nextCursor: z.string().optional(),
  }),
});

export const dashboardDetailResponseSchema = z.object({
  left: z.object({
    messages: z.array(
      z.object({
        role: z.string(),
        text: z.string(),
        timestamp: z.string().optional(),
      }),
    ),
  }),
  right: z.array(
    z.discriminatedUnion('type', [
      z.object({ type: z.literal('kv'), title: z.string(), items: z.array(z.object({ key: z.string(), value: z.string() })) }),
      z.object({ type: z.literal('list'), title: z.string(), items: z.array(z.string()) }),
      z.object({
        type: z.literal('timeline'),
        title: z.string(),
        events: z.array(z.object({ label: z.string(), time: z.string().optional() })),
      }),
      z.object({
        type: z.literal('metrics'),
        title: z.string(),
        metrics: z.array(z.object({ label: z.string(), value: z.union([z.string(), z.number()]) })),
      }),
    ]),
  ),
});

const datopsUseCaseSchema = z.object({
  id: z.string(),
  adapter: z.string(),
  timeout_ms: z.number().int().positive(),
  upstream_base_url: z.string().nullable().optional(),
  routes: z.object({
    cards: z.string(),
    dashboard: z.string(),
    dashboard_detail: z.string(),
  }),
});

export const datopsOverviewResponseSchema = z.object({
  schema_version: z.string(),
  generated_at: z.string(),
  profile: z.string(),
  use_cases: z.array(datopsUseCaseSchema),
});

const cardsComponentSchema = z.object({
  id: z.string().min(1),
  type: z.literal('cards'),
  title: z.string().min(1),
  data_source: z.literal('/cards'),
  position: z.number().int().nonnegative(),
  config: z.object({
    max_cards: z.number().int().positive().max(10).optional(),
    columns: z.number().int().positive().max(6).optional(),
  }).optional(),
});

const tableComponentSchema = z.object({
  id: z.string().min(1),
  type: z.literal('table'),
  title: z.string().min(1),
  data_source: z.literal('/dashboard'),
  position: z.number().int().nonnegative(),
  config: z.object({
    visible_columns: z.array(z.string().min(1)).max(20).optional(),
    required_columns: z.array(z.string().min(1)).max(10).optional(),
  }).optional(),
});

const detailComponentSchema = z.object({
  id: z.string().min(1),
  type: z.literal('detail'),
  title: z.string().min(1),
  data_source: z.enum(['/dashboard_detail', '/none']),
  position: z.number().int().nonnegative(),
  config: z.record(z.string(), z.unknown()).optional(),
});

const textComponentSchema = z.object({
  id: z.string().min(1),
  type: z.literal('text'),
  title: z.string().min(1),
  data_source: z.literal('/none'),
  position: z.number().int().nonnegative(),
  config: z.object({ text: z.string().max(3000).optional() }).optional(),
});

const chartComponentSchema = z.object({
  id: z.string().min(1),
  type: z.literal('chart'),
  title: z.string().min(1),
  data_source: z.enum(['/dashboard', '/cards', '/none']),
  position: z.number().int().nonnegative(),
  config: z.object({
    height: z.number().int().positive().max(700).optional(),
    color: z.string().min(3).max(30).optional(),
  }).optional(),
});

export const viewComponentSchema = z.discriminatedUnion('type', [
  cardsComponentSchema,
  tableComponentSchema,
  detailComponentSchema,
  textComponentSchema,
  chartComponentSchema,
]);

export const viewConfigurationSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  system: z.string().min(1),
  enabled: z.boolean(),
  components: z.array(viewComponentSchema).min(1).max(20),
});

export const viewConfigurationListSchema = z.array(viewConfigurationSchema);

export type QueryRequest = z.infer<typeof queryRequestSchema>;
export type CardsResponse = z.infer<typeof cardsResponseSchema>;
export type DashboardResponse = z.infer<typeof dashboardResponseSchema>;
export type DashboardDetailResponse = z.infer<typeof dashboardDetailResponseSchema>;
export type DatopsOverviewResponse = z.infer<typeof datopsOverviewResponseSchema>;
export type ViewComponent = z.infer<typeof viewComponentSchema>;
export type ViewConfiguration = z.infer<typeof viewConfigurationSchema>;

export type NormalizedApiErrorCode =
  | 'UNKNOWN_USE_CASE'
  | 'VALIDATION_ERROR'
  | 'UPSTREAM_TIMEOUT'
  | 'UPSTREAM_ERROR'
  | 'INTERNAL_ERROR';

export class MonitorApiError extends Error {
  constructor(
    public readonly code: NormalizedApiErrorCode,
    message: string,
  ) {
    super(message);
    this.name = 'MonitorApiError';
  }
}
