import { CardsResponse } from '#/shell/shared/contracts/monitor.contracts';

export const cardsFixture: CardsResponse = {
  cards: [
    { title: 'Conversaciones activas', value: 128, format: 'int' },
    { title: 'Tiempo medio de respuesta', value: 2.31, format: 'seconds' },
    { title: 'Tasa de resolución', value: 0.92, format: 'percent' },
  ],
};
