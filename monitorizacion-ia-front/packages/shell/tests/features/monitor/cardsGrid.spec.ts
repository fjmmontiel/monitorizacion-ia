import { normalizeCards } from '#/shell/features/monitor/components/CardsGrid/CardsGrid';

describe('CardsGrid normalizeCards', () => {
  test('acepta cards válidas y rechaza cards incompatibles sin bloquear el resto', () => {
    const result = normalizeCards([
      { title: 'Conversaciones', value: 12, format: 'int', unit: 'casos', variant: 'neutral' },
      { foo: 'bar' },
    ]);

    expect(result.accepted).toHaveLength(1);
    expect(result.rejectedMessages).toHaveLength(1);
    expect(result.rejectedMessages[0]).toContain('Card 2 rechazada');
  });
});
