import { CardItem, CardsResponse, cardSchema } from '#/shell/shared/contracts/monitor.contracts';
import { MonitorStyleConfig } from '#/shell/features/monitor/config/monitorStyle';

const formatters: Record<string, (value: string | number) => string> = {
  seconds: value => `${Number(value).toFixed(2)} s`,
  percent: value => `${(Number(value) * 100).toFixed(1)} %`,
  currencyEUR: value => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(Number(value)),
  int: value => `${Math.trunc(Number(value))}`,
  float: value => `${Number(value).toFixed(2)}`,
};

const accentByVariant: Record<string, string> = {
  neutral: '#0b5fff',
  positive: '#0a7d3b',
  warning: '#b54708',
  danger: '#b42318',
};

type Props = {
  data: CardsResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
  view: MonitorStyleConfig;
  config?: Record<string, unknown>;
};

type NormalizedCards = {
  accepted: CardItem[];
  rejectedMessages: string[];
};

export const normalizeCards = (cards: unknown[]): NormalizedCards => {
  const accepted: CardItem[] = [];
  const rejectedMessages: string[] = [];

  cards.forEach((candidate, index) => {
    const parsed = cardSchema.safeParse(candidate);
    if (parsed.success) {
      accepted.push(parsed.data);
      return;
    }

    const reason = parsed.error.issues[0]?.message ?? 'Formato inválido';
    rejectedMessages.push(`Card ${index + 1} rechazada: ${reason}`);
  });

  return { accepted, rejectedMessages };
};

export const CardsGrid = ({ data, loading, error, onRefresh, view, config }: Props) => {
  if (loading) {
    return <p>Cargando tarjetas...</p>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={onRefresh}>Reintentar</button>
      </div>
    );
  }

  if (!data || data.cards.length === 0) {
    return <p>Sin datos de tarjetas.</p>;
  }

  const normalized = normalizeCards(data.cards);

  if (normalized.accepted.length === 0) {
    return (
      <div>
        <p>Sin cards renderizables.</p>
        {normalized.rejectedMessages.length > 0 && (
          <p style={{ color: '#b54708', marginBottom: 0 }}>
            {normalized.rejectedMessages.join(' | ')}
          </p>
        )}
      </div>
    );
  }

  const maxCards = typeof config?.max_cards === 'number' ? Math.max(1, Math.trunc(config.max_cards)) : normalized.accepted.length;
  const configuredColumns = typeof config?.columns === 'number' ? Math.max(1, Math.trunc(config.columns)) : view.cards.columns;
  const cards = normalized.accepted.slice(0, maxCards);
  const columns = Math.min(configuredColumns, Math.max(1, cards.length));

  return (
    <section>
      <div style={{ alignItems: 'center', display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
        <p style={{ margin: 0 }}>Indicadores principales</p>
        <button onClick={onRefresh}>Actualizar cards</button>
      </div>
      {normalized.rejectedMessages.length > 0 && (
        <p style={{ color: '#b54708', margin: '0 0 10px 0' }}>
          Algunas cards no se han renderizado: {normalized.rejectedMessages.join(' | ')}
        </p>
      )}
      <div style={{ display: 'grid', gap: 10, gridTemplateColumns: `repeat(${columns}, minmax(180px, 1fr))` }}>
        {cards.map(card => {
          const formatter = card.format ? formatters[card.format] : undefined;
          const value = formatter ? formatter(card.value) : String(card.value);
          const title = view.cards.titleAliases[card.title] ?? card.title;
          const accent = accentByVariant[card.variant ?? 'neutral'] ?? view.theme.accent;
          const unit = card.unit && !formatter ? ` ${card.unit}` : '';
          return (
            <article
              key={card.title}
              style={{
                border: `1px solid ${view.theme.surfaceBorder}`,
                borderTop: `4px solid ${accent}`,
                borderRadius: 8,
                minWidth: 0,
                padding: 12,
              }}
            >
              <h3 style={{ marginBottom: 8 }}>{title}</h3>
              {view.cards.showSubtitle && card.subtitle && <small style={{ display: 'block', marginBottom: 10 }}>{card.subtitle}</small>}
              <p style={{ fontSize: 28, fontWeight: 700, margin: 0, overflowWrap: 'anywhere' }}>{value}{unit}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
};
