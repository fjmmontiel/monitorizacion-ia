import { DashboardDetailResponse } from '#/shell/shared/contracts/monitor.contracts';
import { MonitorStyleConfig } from '#/shell/features/monitor/config/monitorStyle';

type Props = {
  data: DashboardDetailResponse | null;
  loading: boolean;
  error: string | null;
  selectedId: string | null;
  selectedRowSnapshot: Record<string, unknown> | null;
  onClose: () => void;
  view: MonitorStyleConfig;
};

const detailLayoutCss = `
  .monitor-detail-layout {
    display: grid;
    grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
    gap: 14px;
  }
  @media (max-width: 980px) {
    .monitor-detail-layout {
      grid-template-columns: 1fr;
    }
  }
`;

export const DashboardDetail = ({
  data,
  loading,
  error,
  selectedId,
  selectedRowSnapshot,
  onClose,
  view,
}: Props) => {
  if (!selectedId) {
    return null;
  }

  const summaryEntries = selectedRowSnapshot
    ? Object.entries(selectedRowSnapshot).filter(([key]) => key !== 'detail').slice(0, 6)
    : [];

  return (
    <section
      style={{
        alignItems: 'center',
        background: 'rgba(16, 42, 67, 0.45)',
        display: 'flex',
        inset: 0,
        justifyContent: 'center',
        padding: 16,
        position: 'fixed',
        zIndex: 1200,
      }}
      onClick={onClose}
    >
      <style>{detailLayoutCss}</style>
      <div
        style={{
          background: view.theme.surfaceBackground,
          border: `1px solid ${view.theme.surfaceBorder}`,
          borderTop: `4px solid ${view.theme.accent}`,
          borderRadius: 10,
          maxHeight: '86vh',
          maxWidth: 1180,
          overflow: 'auto',
          padding: 14,
          width: '100%',
        }}
        onClick={event => event.stopPropagation()}
      >
        <div style={{ alignItems: 'center', display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
          <h3 style={{ margin: 0 }}>Detalle {selectedId}</h3>
          <button onClick={onClose}>Cerrar</button>
        </div>

        {summaryEntries.length > 0 && (
          <div style={{ display: 'grid', gap: 8, gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', marginBottom: 12 }}>
            {summaryEntries.map(([key, value]) => (
              <article
                key={key}
                style={{
                  border: `1px solid ${view.theme.surfaceBorder}`,
                  borderRadius: 8,
                  padding: 10,
                }}
              >
                <small style={{ display: 'block', marginBottom: 4, opacity: 0.7 }}>{key}</small>
                <strong>{typeof value === 'string' || typeof value === 'number' ? value : '-'}</strong>
              </article>
            ))}
          </div>
        )}

        {loading && <p>Cargando detalle...</p>}
        {error && <p>Error detalle: {error}</p>}
        {data && (
          <div className='monitor-detail-layout'>
            <div>
              <h4 style={{ marginBottom: 8 }}>Transcripción</h4>
              {data.left.messages.map((message, index) => (
                <article
                  key={`${message.role}-${index}`}
                  style={{
                    border: `1px solid ${view.theme.surfaceBorder}`,
                    borderRadius: 8,
                    marginBottom: 8,
                    padding: 10,
                  }}
                >
                  <p style={{ margin: 0 }}>
                    <strong>{message.role}</strong> {message.timestamp ? `· ${message.timestamp}` : ''}
                  </p>
                  <p style={{ margin: '6px 0 0 0' }}>{message.text}</p>
                </article>
              ))}
            </div>

            <aside>
              {data.right.map((panel, index) => (
                <article
                  key={`${panel.title}-${index}`}
                  style={{
                    border: `1px solid ${view.theme.surfaceBorder}`,
                    borderRadius: 8,
                    marginBottom: 10,
                    padding: 10,
                  }}
                >
                  <h5 style={{ marginBottom: 8 }}>{panel.title}</h5>
                  {panel.type === 'kv' &&
                    panel.items.map(item => (
                      <p key={item.key} style={{ margin: '0 0 4px 0' }}>
                        <strong>{item.key}:</strong> {item.value}
                      </p>
                    ))}
                  {panel.type === 'list' &&
                    panel.items.map(item => (
                      <p key={item} style={{ margin: '0 0 4px 0' }}>
                        • {item}
                      </p>
                    ))}
                  {panel.type === 'timeline' &&
                    panel.events.map(event => (
                      <p key={event.label} style={{ margin: '0 0 4px 0' }}>
                        <strong>{event.label}</strong> {event.time ?? ''}
                      </p>
                    ))}
                  {panel.type === 'metrics' && (
                    <div style={{ display: 'grid', gap: 6, gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))' }}>
                      {panel.metrics.map(metric => (
                        <div
                          key={metric.label}
                          style={{
                            background: view.theme.pageBackground,
                            borderRadius: 6,
                            padding: 8,
                          }}
                        >
                          <small style={{ display: 'block', opacity: 0.7 }}>{metric.label}</small>
                          <strong>{metric.value}</strong>
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </aside>
          </div>
        )}
      </div>
    </section>
  );
};
