/* istanbul ignore file */
import { useEffect, useState } from 'react';
import { FilterMatchMode } from 'primereact/api';
import { Calendar } from '@internal-channels-components/calendar';
import { Column } from 'primereact/column';
import { SortOrder } from 'primereact/datatable';
import { useNavigate } from 'react-router-dom';
import { Icon } from '@internal-channels-components/icon';

import { Sesion, SesionSortAndFilterOptions } from '../../domains/Sesion.domain';
import sesionService from '../../services/SesionService';

import { ActionButton, Main, StyledDataTable, Titulo } from './SessionList.styles';

const SessionListPage = () => {
  const navigate = useNavigate();
  const [sesiones, setSesiones] = useState<Sesion[] | null>([]);
  const [filters, setFilters] = useState({
    fechaInicio: { value: null, matchMode: FilterMatchMode.DATE_AFTER },
    fechaFin: { value: null, matchMode: FilterMatchMode.DATE_BEFORE },
    gestor: { value: null, matchMode: FilterMatchMode.CONTAINS },
  });
  const [loading, setLoading] = useState(true);
  const [totalRecords, setTotalRecords] = useState(0);
  const [page, setPage] = useState(0);
  const [rows, setRows] = useState(10);
  const [sortField, setSortField] = useState<string | null>('fechaInicio');
  const [sortOrder, setSortOrder] = useState<SortOrder>(-1);

  const orderDict: Record<string, string> = {
    '-1': 'desc',
    '1': 'asc',
  };

  const fieldDict: Record<string, string> = {
    numTokensEntrada: 'NUM_INPUT_TOKENS',
    numTokensSalida: 'NUM_OUTPUT_TOKENS',
    coste: 'POC_COSTE',
    valoracion: 'NUM_VALORACION',
    comentarios: 'DES_COMENTARIOS',
    numMuestrasInteres: 'NUM_MUESTRA_INTERES',
    duracion: 'NUM_SESION_DURACION',
    fechaInicio: 'AUD_TIM_SESION_INI',
    fechaFin: 'AUD_TIM_SESION_FIN',
    gestor: 'COD_GESTOR_SESION',
  };

  useEffect(() => {
    fetchData();
  }, [page, rows, sortField, sortOrder, filters]);

  const fetchData = async () => {
    setLoading(true);

    try {
      // Contruimos objeto de ordenación y filtrado
      const sesionSortAndFilterOptions: SesionSortAndFilterOptions = {
        pagina: Number.isFinite(page) ? page + 1 : null,
        tamano: Number.isFinite(rows) ? rows : null,
        campoOrden: sortField ? fieldDict[sortField] ?? null : null,
        direccionOrden: sortOrder ? orderDict[sortOrder.toString()] ?? null : null,
        filtros: [
          ...(filters.gestor?.value ? [{ campo: fieldDict['gestor'], valor: String(filters.gestor.value) }] : []),
          ...(filters.fechaInicio?.value
            ? [{ campo: fieldDict['fechaInicio'], valor: (filters.fechaInicio.value as Date).toISOString() }]
            : []),
          ...(filters.fechaFin?.value
            ? [{ campo: fieldDict['fechaFin'], valor: (filters.fechaFin.value as Date).toISOString() }]
            : []),
        ],
      };

      // llamamos al servicio
      const data = await sesionService.getSesiones(sesionSortAndFilterOptions);
      const items = data?.map((item: any) => ({
        ...item,
        fechaDesde: item.fechaDesde ? new Date(item.fechaDesde) : null,
        fechaHasta: item.fechaHasta ? new Date(item.fechaHasta) : null,
      }));

      setSesiones(items ?? null);
      setTotalRecords(items?.length ?? 0);
    } catch (e) {
      // const items = sesiones_mock?.map((item: any) => ({
      //   ...item,
      //   fechaDesde: item.fechaDesde ? new Date(item.fechaDesde) : null,
      //   fechaHasta: item.fechaHasta ? new Date(item.fechaHasta) : null,
      // }));
      setSesiones([]);
      setTotalRecords(0);
    } finally {
      setLoading(false);
    }
  };

  const onFilter = (e: any) => {
    setFilters(e.filters);
    setPage(0);
  };

  const onPageChange = (event: any) => {
    setPage(event.page);
    setRows(event.rows);
  };

  const onSort = (event: any) => {
    setSortField(event.sortField);
    setSortOrder(event.sortOrder);
  };

  const dateFilterTemplate = (options: any) => {
    return (
      <Calendar
        value={options.value}
        onSelect={e => {
          if (e.value !== null) {
            options.filterApplyCallback(e.value, options.index);
          }
        }}
        showTime
        hideOnDateTimeSelect
        dateFormat="yy-mm-dd"
        hourFormat="24"
        placeholder="Seleccionar fecha"
      />
    );
  };

  const actionTemplate = (rowData: any) => (
    <ActionButton
      className="action-btn"
      onClick={() => navigate(`/sesion/${rowData.idSesion}`)}
      data-testid="action-btn">
      <Icon name="interfaceEditView" width={20} height={20} />
    </ActionButton>
  );

  return (
    <Main>
      <Titulo>Listado de sesiones</Titulo>
      <StyledDataTable
        data={sesiones ?? undefined}
        filters={filters}
        filterDisplay="row"
        filterDelay={1000}
        loading={loading}
        lazy
        emptyMessage="No se han encontrado sesiones."
        paginator
        totalRecords={totalRecords}
        first={page * rows}
        onPage={onPageChange}
        onFilter={onFilter}
        onSort={onSort}
        sortField={sortField || undefined}
        sortOrder={sortOrder}
        rows={rows}
        rowsPerPageOptions={[10, 20, 50]}>
        <Column field="idSesion" header="ID Sesion" />
        <Column
          field="gestor"
          header="Gestor"
          filter
          filterPlaceholder="Gestor"
          sortable
          sortField="gestor"
          showFilterMenu={false}
        />
        <Column
          field="fechaInicio"
          dataType="date"
          header="Inicio"
          sortable
          filter
          filterField="fechaInicio"
          filterElement={dateFilterTemplate}
          showFilterMenu={false}
        />
        <Column
          field="fechaFin"
          dataType="date"
          header="Fin"
          sortable
          filter
          filterField="fechaFin"
          filterElement={dateFilterTemplate}
          showFilterMenu={false}
        />
        <Column field="duracion" header="Duración" sortable />
        <Column
          field="numMuestrasInteres"
          header="Muestras interés generadas"
          sortable
          sortField="numMuestrasInteres"
        />
        <Column field="numTokensEntrada" header="Tokens entrada" sortable />
        <Column field="numTokensSalida" header="Tokens salida" sortable />
        <Column field="coste" header="Coste" sortable />
        <Column field="valoracion" header="Valoración" sortable />
        <Column field="comentarios" header="Comentarios" />
        <Column body={actionTemplate} style={{ width: '40px' }} />
      </StyledDataTable>
    </Main>
  );
};

export const element = <SessionListPage />;
