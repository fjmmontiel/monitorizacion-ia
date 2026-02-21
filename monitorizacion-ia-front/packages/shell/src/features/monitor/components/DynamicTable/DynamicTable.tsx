import { DashboardResponse, QueryRequest } from '#/shell/shared/contracts/monitor.contracts';
import { ViewConfig } from '#/shell/shared/config/views';

type Props = {
  data: DashboardResponse | null;
  loading: boolean;
  error: string | null;
  query: QueryRequest;
  onQueryChange: (next: QueryRequest) => void;
  onOpenDetail: (id: string) => void;
  view: ViewConfig;
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
  const hasRequiredColumns = columns.some(column => column.key === 'id') && columns.some(column => column.key === 'detail');
  const filterableColumns = columns.filter(column => column.filterable);

  if (!hasRequiredColumns) {
    return <p>Configuración inválida: faltan columnas obligatorias id/detail.</p>;
  }

  return (
    <section
      style={{
        background: view.theme.surfaceBackground,
        border: `1px solid ${view.theme.surfaceBorder}`,
        borderRadius: 8,
        marginTop: 12,
        padding: 12,
      }}
    >
      {filterableColumns.length > 0 && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          {filterableColumns.map(column => (
            <label key={column.key}>
              <span>{column.label}</span>
              <input
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
      <table style={{ width: '100%' }}>
        <thead>
          <tr style={{ background: view.theme.pageBackground }}>
            {columns.map(column => (
              <th key={column.key}>
                <span>{column.label}</span>
                {column.sortable && (
                  <button
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
            <tr key={row.id}>
              {columns.map(column => {
                if (column.key === 'detail') {
                  return (
                    <td key={`${row.id}-${column.key}`}>
                      <button onClick={() => onOpenDetail(row.id)}>{row.detail.action}</button>
                    </td>
                  );
                }

                const value = row[column.key];
                return <td key={`${row.id}-${column.key}`}>{typeof value === 'string' || typeof value === 'number' ? value : '-'}</td>;
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
