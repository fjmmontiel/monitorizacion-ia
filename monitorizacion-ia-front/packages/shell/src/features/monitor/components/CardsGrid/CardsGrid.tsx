import { CardsResponse } from '#/shell/shared/contracts/monitor.contracts';

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
};

export const CardsGrid = ({ data, loading, error, onRefresh }: Props) => {
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

  return (
    <section>
      <button onClick={onRefresh}>Refresh tarjetas</button>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 12 }}>
        {data.cards.map(card => {
          const formatter = card.format ? formatters[card.format] : undefined;
          const value = formatter ? formatter(card.value) : card.value;
          return (
            <article key={card.title} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
              <h3>{card.title}</h3>
              {card.subtitle && <small>{card.subtitle}</small>}
              <p>{value}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
};
