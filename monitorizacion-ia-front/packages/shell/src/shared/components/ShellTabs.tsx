import { UIShellResponse } from '#/shell/shared/contracts/monitor.contracts';

type Props = {
  shell: UIShellResponse;
  activeTab: 'home' | string;
  onSelectHome: () => void;
  onSelectSystem: (systemId: string) => void;
};

export const ShellTabs = ({ shell, activeTab, onSelectHome, onSelectSystem }: Props) => {
  return (
    <section
      style={{
        background: '#ffffff',
        border: '1px solid #d9e2ec',
        borderRadius: 14,
        boxShadow: '0 10px 24px rgba(15, 23, 42, 0.08)',
        marginBottom: 16,
        padding: 16,
      }}
    >
      <div style={{ alignItems: 'center', display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        <button
          role='tab'
          aria-selected={activeTab === shell.home.id}
          onClick={onSelectHome}
          style={{
            background: activeTab === shell.home.id ? '#102a43' : '#ffffff',
            border: `1px solid ${activeTab === shell.home.id ? '#102a43' : '#d9e2ec'}`,
            borderRadius: 999,
            color: activeTab === shell.home.id ? '#ffffff' : '#102a43',
            fontWeight: 700,
            padding: '8px 16px',
          }}
        >
          {shell.home.label}
        </button>
        {shell.systems.map(system => {
          const isActive = activeTab === system.id;
          return (
            <button
              key={system.id}
              role='tab'
              aria-selected={isActive}
              onClick={() => onSelectSystem(system.id)}
              style={{
                background: isActive ? '#0b5fff' : '#ffffff',
                border: `1px solid ${isActive ? '#0b5fff' : '#d9e2ec'}`,
                borderRadius: 999,
                color: isActive ? '#ffffff' : '#102a43',
                padding: '8px 16px',
              }}
            >
              {system.label}
            </button>
          );
        })}
      </div>
    </section>
  );
};
