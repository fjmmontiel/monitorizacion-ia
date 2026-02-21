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

const bySystem: Record<string, SystemLayoutConfig> = {
  hipotecas: {
    id: 'hipotecas',
    headerTitle: 'Panel de seguimiento de hipotecas',
    headerSubtitle: 'Resumen operativo con foco en conversaciones y resoluciones.',
    sidebarTitle: 'Filtros de hipotecas',
    sidebarHint: 'Configura gestor, cliente y resolución para el análisis diario.',
    tableTitle: 'Historial de conversaciones',
    detailTitle: 'Detalle de conversación',
    accent: '#0a7d3b',
  },
  prestamos: {
    id: 'prestamos',
    headerTitle: 'Panel de seguimiento de préstamos',
    headerSubtitle: 'Vista de solicitudes, aprobaciones y trazabilidad de hitos.',
    sidebarTitle: 'Filtros de préstamos',
    sidebarHint: 'Ajusta resolución y fecha para revisar el flujo de aprobación.',
    tableTitle: 'Historial de solicitudes',
    detailTitle: 'Detalle de solicitud',
    accent: '#0b5fff',
  },
};

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
