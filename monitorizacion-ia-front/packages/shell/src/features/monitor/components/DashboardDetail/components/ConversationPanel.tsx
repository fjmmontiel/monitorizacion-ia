import { DashboardDetailResponse } from '#/shell/shared/contracts/monitor.contracts';
import { MonitorStyleConfig } from '#/shell/features/monitor/config/monitorStyle';

type Props = {
  messages: DashboardDetailResponse['left']['messages'];
  view: MonitorStyleConfig;
};

export const ConversationPanel = ({ messages, view }: Props) => (
  <section>
    <h4 style={{ marginBottom: 8 }}>Transcripción de conversación</h4>
    {messages.map((message, index) => (
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
  </section>
);
