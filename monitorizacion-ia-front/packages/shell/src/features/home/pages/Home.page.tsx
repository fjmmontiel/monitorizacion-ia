import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { MonitorApi } from '#/shell/shared/api/MonitorApi';
import { useCasesConfig } from '#/shell/shared/config/useCases';
import { DatopsOverviewResponse, MonitorApiError } from '#/shell/shared/contracts/monitor.contracts';
import { buildMonitorUrl, resolveInitialUseCase } from '../home.helpers';

const normalizeErrorMessage = (error: unknown) => {
  if (error instanceof MonitorApiError) {
    return `${error.code}: ${error.message}`;
  }
  return 'INTERNAL_ERROR: Unexpected error';
};

const HomePage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [selectedUseCase, setSelectedUseCase] = useState<string>(() => resolveInitialUseCase(searchParams));
  const [datops, setDatops] = useState<DatopsOverviewResponse | null>(null);
  const [loadingDatops, setLoadingDatops] = useState(false);
  const [datopsError, setDatopsError] = useState<string | null>(null);

  const selectedDatopsUseCase = useMemo(() => {
    return datops?.use_cases.find(item => item.id === selectedUseCase) ?? null;
  }, [datops, selectedUseCase]);

  useEffect(() => {
    const loadDatops = async () => {
      setLoadingDatops(true);
      setDatopsError(null);
      try {
        setDatops(await MonitorApi.getDatopsOverview());
      } catch (error) {
        setDatopsError(normalizeErrorMessage(error));
      } finally {
        setLoadingDatops(false);
      }
    };

    loadDatops();
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
        <p style={{ margin: 0 }}>
          Vista general por sistema para navegar al monitor con `caso_de_uso` preconfigurado y trazabilidad DatOps.
        </p>
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
        <p style={{ margin: '0 0 8px 0' }}>Sistemas</p>
        <div role='tablist' style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {useCasesConfig
            .filter(item => item.enabled)
            .map(item => {
              const isActive = item.id === selectedUseCase;
              return (
                <button
                  key={item.id}
                  role='tab'
                  aria-selected={isActive}
                  onClick={() => setSelectedUseCase(item.id)}
                  style={{
                    background: isActive ? '#0b5fff' : '#ffffff',
                    border: `1px solid ${isActive ? '#0b5fff' : '#d9e2ec'}`,
                    borderRadius: 999,
                    color: isActive ? '#ffffff' : '#102a43',
                    padding: '8px 14px',
                  }}
                >
                  {item.label}
                </button>
              );
            })}
        </div>
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
        <h2 style={{ marginBottom: 8 }}>Sistema seleccionado: {selectedUseCase}</h2>
        {loadingDatops && <p>Cargando DatOps...</p>}
        {datopsError && <p>Error DatOps: {datopsError}</p>}
        {!loadingDatops && !datopsError && selectedDatopsUseCase && (
          <>
            <p style={{ marginBottom: 10 }}>
              Adapter: <strong>{selectedDatopsUseCase.adapter}</strong> | Timeout: <strong>{selectedDatopsUseCase.timeout_ms} ms</strong>
            </p>
            <p style={{ margin: '0 0 6px 0' }}>Llamadas hardcodeadas por componente:</p>
            <p style={{ margin: '0 0 4px 0' }}>
              `CardsGrid` {'->'} <code>{selectedDatopsUseCase.routes.cards}</code>
            </p>
            <p style={{ margin: '0 0 4px 0' }}>
              `DynamicTable` {'->'} <code>{selectedDatopsUseCase.routes.dashboard}</code>
            </p>
            <p style={{ margin: '0 0 12px 0' }}>
              `DashboardDetail` {'->'} <code>{selectedDatopsUseCase.routes.dashboard_detail}</code>
            </p>
            <button onClick={() => navigate(buildMonitorUrl(selectedUseCase))}>Abrir monitor</button>
          </>
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
        {!datops && !loadingDatops && !datopsError && <p>Sin inventario disponible.</p>}
        {datops?.use_cases.map(item => (
          <article key={item.id} style={{ borderTop: '1px solid #e8eef5', padding: '8px 0' }}>
            <p style={{ margin: '0 0 2px 0' }}>
              <strong>{item.id}</strong> ({item.adapter})
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
