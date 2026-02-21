import { DashboardDetailResponse } from '#/shell/shared/contracts/monitor.contracts';
import { ViewConfig } from '#/shell/shared/config/views';

type Props = {
  data: DashboardDetailResponse | null;
  loading: boolean;
  error: string | null;
  selectedId: string | null;
  onClose: () => void;
  view: ViewConfig;
};

export const DashboardDetail = ({ data, loading, error, selectedId, onClose, view }: Props) => {
  if (!selectedId) {
    return null;
  }

  return (
    <section
      style={{
        border: `1px solid ${view.theme.surfaceBorder}`,
        borderTop: `4px solid ${view.theme.accent}`,
        background: view.theme.surfaceBackground,
        marginTop: 16,
        padding: 12,
      }}
    >
      <h3>Detalle {selectedId}</h3>
      <button onClick={onClose}>Cerrar</button>
      {loading && <p>Cargando detalle...</p>}
      {error && <p>Error detalle: {error}</p>}
      {data && (
        <div style={{ display: 'grid', gridTemplateColumns: '4fr 1fr', gap: 16 }}>
          <div>
            <h4>Transcript</h4>
            {data.left.messages.map((message, index) => (
              <p key={`${message.role}-${index}`}>
                <strong>{message.role}</strong>: {message.text} {message.timestamp ? `(${message.timestamp})` : ''}
              </p>
            ))}
          </div>
          <aside>
            {data.right.map((panel, index) => (
              <div key={`${panel.title}-${index}`}>
                <h5>{panel.title}</h5>
                {panel.type === 'kv' && panel.items.map(item => <p key={item.key}>{item.key}: {item.value}</p>)}
                {panel.type === 'list' && panel.items.map(item => <p key={item}>{item}</p>)}
                {panel.type === 'timeline' && panel.events.map(event => <p key={event.label}>{event.label} {event.time ?? ''}</p>)}
                {panel.type === 'metrics' && panel.metrics.map(metric => <p key={metric.label}>{metric.label}: {metric.value}</p>)}
              </div>
            ))}
          </aside>
        </div>
      )}
    </section>
  );
};
