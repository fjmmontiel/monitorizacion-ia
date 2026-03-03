import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { ShellTabs } from '#/shell/shared/components/ShellTabs';
import { MonitorApi } from '#/shell/shared/api/MonitorApi';
import { DatopsOverviewResponse, MonitorApiError, UIShellResponse } from '#/shell/shared/contracts/monitor.contracts';

const normalizeErrorMessage = (error: unknown) => {
  if (error instanceof MonitorApiError) {
    return `${error.code}: ${error.message}`;
  }
  return 'INTERNAL_ERROR: Unexpected error';
};

const HomePage = () => {
  const navigate = useNavigate();

  const [shell, setShell] = useState<UIShellResponse | null>(null);
  const [datops, setDatops] = useState<DatopsOverviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [shellError, setShellError] = useState<string | null>(null);
  const [datopsError, setDatopsError] = useState<string | null>(null);

  const defaultSystem = useMemo(() => {
    const explicitDefault = shell?.systems.find(item => item.default);
    return explicitDefault ?? shell?.systems[0] ?? null;
  }, [shell]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [shellResult, datopsResult] = await Promise.allSettled([
        MonitorApi.getUIShell(),
        MonitorApi.getDatopsOverview(),
      ]);

      if (shellResult.status === 'fulfilled') {
        setShell(shellResult.value);
        setShellError(null);
      } else {
        setShellError(normalizeErrorMessage(shellResult.reason));
      }

      if (datopsResult.status === 'fulfilled') {
        setDatops(datopsResult.value);
        setDatopsError(null);
      } else {
        setDatopsError(normalizeErrorMessage(datopsResult.reason));
      }

      setLoading(false);
    };

    void load();
  }, []);

  return (
    <main
      style={{
        minHeight: '100vh',
        padding: 24,
        color: '#102a43',
        background:
          'radial-gradient(circle at top left, rgba(11,95,255,0.14), transparent 35%), radial-gradient(circle at 85% 0%, rgba(31,143,77,0.12), transparent 35%), #f4f7fb',
      }}
    >
      {shell && (
        <ShellTabs
          shell={shell}
          activeTab='home'
          onSelectHome={() => navigate('/home')}
          onSelectSystem={systemId => navigate(`/monitor?caso_de_uso=${systemId}`)}
        />
      )}

      <section
        style={{
          background: 'linear-gradient(135deg, #102a43 0%, #1f3a56 100%)',
          borderRadius: 14,
          boxShadow: '0 10px 30px rgba(16,42,67,0.2)',
          color: '#f8fbff',
          marginBottom: 16,
          padding: 20,
        }}
      >
        <h1 style={{ marginBottom: 8 }}>Home de monitorización</h1>
        <p style={{ margin: '0 0 10px 0' }}>
          Shell único con navegación por sistema desde backend. Cada nueva configuración habilitada aparece como pestaña sin tocar el frontend.
        </p>
        {defaultSystem && (
          <button onClick={() => navigate(`/monitor?caso_de_uso=${defaultSystem.id}`)}>
            Abrir sistema por defecto: {defaultSystem.label}
          </button>
        )}
      </section>

      <section
        style={{
          background: '#ffffff',
          border: '1px solid #d9e2ec',
          borderRadius: 10,
          marginBottom: 12,
          padding: 14,
        }}
      >
        <h2 style={{ marginBottom: 8 }}>Sistemas disponibles</h2>
        {loading && <p>Cargando shell...</p>}
        {shellError && <p>Error shell: {shellError}</p>}
        {shell && (
          <div style={{ display: 'grid', gap: 10, gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
            {shell.systems.map(system => (
              <article
                key={system.id}
                style={{
                  border: '1px solid #d9e2ec',
                  borderRadius: 10,
                  padding: 14,
                }}
              >
                <h3 style={{ marginBottom: 6 }}>{system.label}</h3>
                <p style={{ margin: '0 0 8px 0' }}>Vista activa: {system.view.name}</p>
                <p style={{ margin: '0 0 12px 0' }}>{system.view.components.length} componente(s) raíz declarados desde backend.</p>
                <button onClick={() => navigate(`/monitor?caso_de_uso=${system.id}`)}>Abrir vista</button>
              </article>
            ))}
          </div>
        )}
      </section>

      <section
        style={{
          background: '#ffffff',
          border: '1px solid #d9e2ec',
          borderRadius: 10,
          padding: 14,
        }}
      >
        <h2 style={{ marginBottom: 8 }}>Inventario DatOps</h2>
        {loading && <p>Cargando DatOps...</p>}
        {datopsError && <p>Error DatOps: {datopsError}</p>}
        {!loading && !datopsError && !datops && <p>Sin inventario disponible.</p>}
        {datops?.use_cases.map(item => (
          <article key={item.id} style={{ borderTop: '1px solid #e8eef5', padding: '8px 0' }}>
            <p style={{ margin: '0 0 2px 0' }}>
              <strong>{item.label}</strong> ({item.adapter})
            </p>
            <p style={{ margin: '0 0 2px 0' }}>
              <code>{item.routes.cards}</code>
            </p>
            <p style={{ margin: '0 0 2px 0' }}>
              <code>{item.routes.dashboard}</code>
            </p>
            <p style={{ margin: 0 }}>
              <code>{item.routes.dashboard_detail}</code>
            </p>
          </article>
        ))}
      </section>
    </main>
  );
};

export default HomePage;
