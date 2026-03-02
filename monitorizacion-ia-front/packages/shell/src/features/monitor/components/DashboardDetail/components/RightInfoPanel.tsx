import { DashboardDetailResponse } from '#/shell/shared/contracts/monitor.contracts';
import { MonitorStyleConfig } from '#/shell/features/monitor/config/monitorStyle';

type Props = {
  panels: DashboardDetailResponse['right'];
  view: MonitorStyleConfig;
};

export const RightInfoPanel = ({ panels, view }: Props) => (
  <aside style={{ maxHeight: '72vh', overflowY: 'auto', paddingRight: 4, position: 'sticky', top: 0 }}>
    <h4 style={{ marginBottom: 8 }}>Información fija: productos y servicios</h4>
    {panels.map((panel, index) => (
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
);
