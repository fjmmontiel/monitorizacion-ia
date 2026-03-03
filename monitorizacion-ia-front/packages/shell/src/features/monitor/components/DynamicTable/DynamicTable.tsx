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
  config?: Record<string, unknown>;
};

const renderCellValue = (value: unknown) => {
  if (typeof value === 'string' || typeof value === 'number') {
    return value;
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  if (value === null || typeof value === 'undefined') {
    return '-';
  }
  if (Array.isArray(value)) {
    return value.map(item => (typeof item === 'string' || typeof item === 'number' ? String(item) : JSON.stringify(item))).join(', ');
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
};

export const DynamicTable = ({ data, loading, error, query, onQueryChange, onOpenDetail, view, config }: Props) => {
  if (loading) {
    return <p>Cargando tabla...</p>;
  }

  if (error) {
    return <p>Error tabla: {error}</p>;
  }

  if (!data) {
    return null;
  }

  const tableConfig = config ?? {};
  const { columns: sourceColumns, rows, nextCursor } = data.table;
  const visibleColumns = Array.isArray(tableConfig.visible_columns)
    ? sourceColumns.filter(column => (tableConfig.visible_columns as string[]).includes(column.key))
    : sourceColumns;
  const requiredColumns = Array.isArray(tableConfig.required_columns)
    ? (tableConfig.required_columns as string[])
    : ['id', 'detail'];

  const hasRequiredColumns = requiredColumns.every(required => {
    if (required === 'id') {
      return rows.every(row => typeof row.id === 'string' && row.id.length > 0);
    }
    if (required === 'detail') {
      return sourceColumns.some(column => column.key === 'detail');
    }
    return sourceColumns.some(column => column.key === required);
  });
  const filterableColumns = visibleColumns.filter(column => column.filterable);

  if (!hasRequiredColumns) {
    return <p>Configuración inválida: la tabla exige `id` y `detail`.</p>;
  }

  return (
    <section
      style={{
        border: `1px solid ${view.theme.surfaceBorder}`,
        borderRadius: 8,
        overflowX: 'auto',
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
      <table style={{ border: `1px solid ${view.theme.surfaceBorder}`, borderRadius: 6, tableLayout: 'auto', width: '100%' }}>
        <thead>
          <tr style={{ background: view.theme.pageBackground, textAlign: 'left' }}>
            {visibleColumns.map(column => (
              <th key={column.key} style={{ borderBottom: `1px solid ${view.theme.surfaceBorder}`, padding: 10, whiteSpace: 'nowrap' }}>
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
              {visibleColumns.map(column => {
                if (column.key === 'detail') {
                  return (
                    <td key={`${row.id}-${column.key}`} style={{ padding: 10, whiteSpace: 'nowrap' }}>
                      <button onClick={() => onOpenDetail(row.id)}>{row.detail.action}</button>
                    </td>
                  );
                }

                const value = column.key === 'id' ? row.id : row[column.key];
                return (
                  <td key={`${row.id}-${column.key}`} style={{ maxWidth: 360, padding: 10, verticalAlign: 'top' }}>
                    <div style={{ overflowWrap: 'anywhere' }}>{renderCellValue(value)}</div>
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
