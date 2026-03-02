import { z } from 'zod';

import { useCasesConfig } from '#/shell/shared/config/useCases';

export type SystemLayoutConfig = {
  id: string;
  headerTitle: string;
  headerSubtitle: string;
  sidebarTitle: string;
  sidebarHint: string;
  tableTitle: string;
  detailTitle: string;
  accent: string;
};

const layoutSchema = z.record(
  z.object({
    id: z.string().min(1),
    headerTitle: z.string().min(1),
    headerSubtitle: z.string().min(1),
    sidebarTitle: z.string().min(1),
    sidebarHint: z.string().min(1),
    tableTitle: z.string().min(1),
    detailTitle: z.string().min(1),
    accent: z.string().min(1),
  }),
);

// eslint-disable-next-line @typescript-eslint/no-var-requires
const rawLayouts = require('./system_layouts.json') as unknown;
const bySystem = layoutSchema.parse(rawLayouts) as Record<string, SystemLayoutConfig>;

export const resolveSystemLayout = (systemId: string): SystemLayoutConfig => {
  return bySystem[systemId] ?? {
    id: systemId,
    headerTitle: `Panel de seguimiento de ${systemId}`,
    headerSubtitle: 'Panel operativo del sistema seleccionado.',
    sidebarTitle: 'Filtros',
    sidebarHint: 'Configura los criterios y aplica.',
    tableTitle: 'Historial',
    detailTitle: 'Detalle',
    accent: '#0b5fff',
  };
};

export const getEnabledSystemLayouts = (): SystemLayoutConfig[] => {
  return useCasesConfig.filter(item => item.enabled).map(item => resolveSystemLayout(item.id));
};
