import { DashboardResponse } from '#/shell/shared/contracts/monitor.contracts';

export const dashboardFixture: DashboardResponse = {
  table: {
    columns: [
      { key: 'id', label: 'Id', sortable: true },
      { key: 'cliente', label: 'Cliente', filterable: true },
      { key: 'estado', label: 'Estado', filterable: true, sortable: true },
      { key: 'detalle', label: 'Detalle' },
    ],
    rows: [
      { id: 'conv-001', cliente: 'Ana López', estado: 'Completada', detail: { action: 'Ver detalle' } },
      { id: 'conv-002', cliente: 'Luis Pérez', estado: 'En curso', detail: { action: 'Ver detalle' } },
    ],
    nextCursor: 'page-2',
  },
};
