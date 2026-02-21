import { DashboardResponse, QueryRequest } from '#/shell/shared/contracts/monitor.contracts';

type Props = {
  data: DashboardResponse | null;
  loading: boolean;
  error: string | null;
  query: QueryRequest;
  onQueryChange: (next: QueryRequest) => void;
  onOpenDetail: (id: string) => void;
};

export const DynamicTable = ({ data, loading, error, query, onQueryChange, onOpenDetail }: Props) => {
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

  if (!hasRequiredColumns) {
    return <p>Configuración inválida: faltan columnas obligatorias id/detail.</p>;
  }

  return (
    <section>
      <table style={{ width: '100%' }}>
        <thead>
          <tr>
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
