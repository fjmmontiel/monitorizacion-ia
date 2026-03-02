import { CardsResponse } from '#/shell/shared/contracts/monitor.contracts';
import { MonitorStyleConfig } from '#/shell/features/monitor/config/monitorStyle';

const formatters: Record<string, (value: string | number) => string> = {
  seconds: value => `${Number(value).toFixed(2)} s`,
  percent: value => `${(Number(value) * 100).toFixed(1)} %`,
  currencyEUR: value => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(Number(value)),
  int: value => `${Math.trunc(Number(value))}`,
  float: value => `${Number(value).toFixed(2)}`,
};

type Props = {
  data: CardsResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
  view: MonitorStyleConfig;
  config?: Record<string, unknown>;
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

  const maxCards = typeof config?.max_cards === 'number' ? Math.max(1, Math.trunc(config.max_cards)) : data.cards.length;
  const columns = typeof config?.columns === 'number' ? Math.max(1, Math.trunc(config.columns)) : view.cards.columns;
  const cards = data.cards.slice(0, maxCards);

  return (
    <section>
      <div style={{ alignItems: 'center', display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
        <p style={{ margin: 0 }}>Indicadores principales</p>
        <button onClick={onRefresh}>Actualizar cards</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`, gap: 10 }}>
        {cards.map(card => {
          const formatter = card.format ? formatters[card.format] : undefined;
          const value = formatter ? formatter(card.value) : card.value;
          const title = view.cards.titleAliases[card.title] ?? card.title;
          return (
            <article
              key={card.title}
              style={{
                border: `1px solid ${view.theme.surfaceBorder}`,
                borderTop: `4px solid ${view.theme.accent}`,
                borderRadius: 8,
                padding: 12,
              }}
            >
              <h3 style={{ marginBottom: 8 }}>{title}</h3>
              {view.cards.showSubtitle && card.subtitle && <small style={{ display: 'block', marginBottom: 10 }}>{card.subtitle}</small>}
              <p style={{ fontSize: 28, fontWeight: 700, margin: 0 }}>{value}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
};
