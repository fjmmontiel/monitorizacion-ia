import { DashboardDetailResponse } from '#/shell/shared/contracts/monitor.contracts';

export const dashboardDetailFixture: DashboardDetailResponse = {
  left: {
    messages: [
      { role: 'cliente', text: 'Necesito información sobre una hipoteca fija', timestamp: '10:01' },
      { role: 'agente', text: 'Claro, ¿qué importe necesitas?', timestamp: '10:02' },
    ],
  },
  right: [
    {
      type: 'kv',
      title: 'Contexto',
      items: [
        { key: 'Canal', value: 'Web' },
        { key: 'País', value: 'ES' },
      ],
    },
    {
      type: 'metrics',
      title: 'Métricas',
      metrics: [
        { label: 'Sentimiento', value: 'Positivo' },
        { label: 'Mensajes', value: 12 },
      ],
    },
  ],
};
