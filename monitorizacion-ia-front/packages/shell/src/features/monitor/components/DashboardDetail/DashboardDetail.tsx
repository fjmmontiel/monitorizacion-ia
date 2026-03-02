import { MonitorStyleConfig } from '#/shell/features/monitor/config/monitorStyle';
import { DashboardDetailResponse } from '#/shell/shared/contracts/monitor.contracts';
import { ConversationPanel } from './components/ConversationPanel';
import { RightInfoPanel } from './components/RightInfoPanel';

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
    grid-template-columns: 60% 40%;
    gap: 14px;
    align-items: start;
  }
  @media (max-width: 980px) {
    .monitor-detail-layout {
      grid-template-columns: 1fr;
    }
  }
`;

export const DashboardDetail = ({ data, loading, error, selectedId, selectedRowSnapshot, onClose, view }: Props) => {
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
          maxWidth: 1280,
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
              <article key={key} style={{ border: `1px solid ${view.theme.surfaceBorder}`, borderRadius: 8, padding: 10 }}>
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
            <ConversationPanel messages={data.left.messages} view={view} />
            <RightInfoPanel panels={data.right} view={view} />
          </div>
        )}
      </div>
    </section>
  );
};
