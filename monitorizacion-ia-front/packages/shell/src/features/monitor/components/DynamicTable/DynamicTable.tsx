import { DashboardResponse, QueryRequest } from '#/shell/shared/contracts/monitor.contracts';
import { MonitorStyleConfig } from '#/shell/features/monitor/config/monitorStyle';

type Props = {
  data: DashboardResponse | null;
  loading: boolean;
  error: string | null;
  query: QueryRequest;
  onQueryChange: (next: QueryRequest) => void;
  onOpenDetail: (id: string) => void;
  view: MonitorStyleConfig;
};

export const DynamicTable = ({ data, loading, error, query, onQueryChange, onOpenDetail, view }: Props) => {
  if (loading) {
    return <p>Cargando tabla...</p>;
  }

  if (error) {
    return <p>Error tabla: {error}</p>;
  }

  if (!data) {
    return null;
  }

  const { columns, rows, nextCursor } = data.table;
  const hasRequiredColumns = columns.some(column => column.key === 'detail');
  const filterableColumns = columns.filter(column => column.filterable);

  if (!hasRequiredColumns) {
    return <p>Configuración inválida: falta columna obligatoria detail.</p>;
  }

  return (
    <section
      style={{
        border: `1px solid ${view.theme.surfaceBorder}`,
        borderRadius: 8,
        padding: 10,
      }}
    >
      {filterableColumns.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
          {filterableColumns.map(column => (
            <label key={column.key}>
              <span>{column.label}</span>
              <input
                style={{ marginLeft: 6 }}
                value={String(query.filters?.[column.key] ?? '')}
                onChange={event =>
                  onQueryChange({
                    ...query,
                    cursor: undefined,
                    filters: {
                      ...(query.filters ?? {}),
                      [column.key]: event.target.value,
                    },
                  })
                }
              />
            </label>
          ))}
        </div>
      )}
      <table style={{ border: `1px solid ${view.theme.surfaceBorder}`, borderRadius: 6, overflow: 'hidden', width: '100%' }}>
        <thead>
          <tr style={{ background: view.theme.pageBackground, textAlign: 'left' }}>
            {columns.map(column => (
              <th key={column.key} style={{ borderBottom: `1px solid ${view.theme.surfaceBorder}`, padding: 10 }}>
                <span>{column.label}</span>
                {column.sortable && (
                  <button
                    style={{ marginLeft: 6 }}
                    onClick={() =>
                      onQueryChange({
                        ...query,
                        sort: [{ field: column.key, direction: query.sort?.[0]?.direction === 'asc' ? 'desc' : 'asc' }],
                      })
                    }
                  >
                    Ordenar
                  </button>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.id} style={{ borderBottom: `1px solid ${view.theme.surfaceBorder}` }}>
              {columns.map(column => {
                if (column.key === 'detail') {
                  return (
                    <td key={`${row.id}-${column.key}`} style={{ padding: 10 }}>
                      <button onClick={() => onOpenDetail(row.id)}>{row.detail.action}</button>
                    </td>
                  );
                }

                const value = row[column.key];
                return (
                  <td key={`${row.id}-${column.key}`} style={{ padding: 10 }}>
                    {typeof value === 'string' || typeof value === 'number' ? value : '-'}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {nextCursor && (
        <button onClick={() => onQueryChange({ ...query, cursor: nextCursor })}>
          Siguiente página
        </button>
      )}
    </section>
  );
};
