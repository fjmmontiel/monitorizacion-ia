from orchestrator.adapters.base import Adapter, AdapterContext
from orchestrator.api.schemas import (
    CardItem,
    CardsResponse,
    DashboardDetailResponse,
    DashboardResponse,
    DetailAction,
    KVItem,
    KVPanel,
    LeftPanel,
    ListPanel,
    MessageBlock,
    MetricItem,
    MetricsPanel,
    QueryRequest,
    TableColumn,
    TablePayload,
    TableRow,
    TimelineEvent,
    TimelinePanel,
)


class NativeAdapter(Adapter):
    async def get_cards(self, ctx: AdapterContext, req: QueryRequest) -> CardsResponse:
        if ctx.caso_de_uso == 'prestamos':
            return CardsResponse(
                cards=[
                    CardItem(title='Solicitudes activas', subtitle='Operaciones en curso', value=74, format='int'),
                    CardItem(title='Tiempo medio de aprobacion', subtitle='Media por solicitud', value=4.8, format='seconds'),
                    CardItem(title='Ratio de conversion', subtitle='Solicitudes aprobadas', value=0.64, format='percent'),
                    CardItem(title='Coste medio por solicitud', subtitle='Estimado interno', value=116, format='currencyEUR'),
                ]
            )

        return CardsResponse(
            cards=[
                CardItem(title='Conversaciones activas', subtitle='Sesiones abiertas', value=128, format='int'),
                CardItem(title='Tiempo medio de respuesta', subtitle='SLA de atención', value=2.31, format='seconds'),
                CardItem(title='Tasa de resolucion', subtitle='Consultas resueltas', value=0.92, format='percent'),
                CardItem(title='Coste medio por llamada', subtitle='Canal voz + IA', value=0.116, format='currencyEUR'),
            ]
        )

    async def get_dashboard(self, ctx: AdapterContext, req: QueryRequest) -> DashboardResponse:
        if ctx.caso_de_uso == 'prestamos':
            rows = [
                TableRow(
                    id='pres-100',
                    detail=DetailAction(action='Ver detalle'),
                    fecha_hora='20-02-2026 · 12:01',
                    numero_entrante='+34608281798',
                    nombre_cliente='Marta Ruiz',
                    razones_llamada='Consulta de preaprobacion',
                    duracion='0 min 39 s',
                    resolucion='Pendiente',
                ),
                TableRow(
                    id='pres-101',
                    detail=DetailAction(action='Ver detalle'),
                    fecha_hora='20-02-2026 · 12:19',
                    numero_entrante='+34600122334',
                    nombre_cliente='Carlos Vega',
                    razones_llamada='Solicitud de carencia',
                    duracion='1 min 10 s',
                    resolucion='Aprobado',
                ),
            ]
            columns = [
                TableColumn(key='fecha_hora', label='Fecha · Hora', sortable=True),
                TableColumn(key='numero_entrante', label='Numero entrante', filterable=True),
                TableColumn(key='nombre_cliente', label='Nombre del cliente', filterable=True),
                TableColumn(key='razones_llamada', label='Razones de la llamada', filterable=True),
                TableColumn(key='duracion', label='Duracion', sortable=True),
                TableColumn(key='resolucion', label='Resolucion', filterable=True, sortable=True),
                TableColumn(key='detail', label='Detalle'),
            ]
        else:
            rows = [
                TableRow(
                    id='conv-001',
                    detail=DetailAction(action='Ver detalle'),
                    fecha_hora='20-02-2026 · 10:01',
                    numero_entrante='+34608281798',
                    nombre_cliente='Ana Lopez',
                    razones_llamada='Hipoteca fija',
                    duracion='0 min 39 s',
                    resolucion='Completada',
                ),
                TableRow(
                    id='conv-002',
                    detail=DetailAction(action='Ver detalle'),
                    fecha_hora='20-02-2026 · 10:08',
                    numero_entrante='+34611222333',
                    nombre_cliente='Luis Perez',
                    razones_llamada='Revision de cuota',
                    duracion='1 min 22 s',
                    resolucion='En curso',
                ),
            ]
            columns = [
                TableColumn(key='fecha_hora', label='Fecha · Hora', sortable=True),
                TableColumn(key='numero_entrante', label='Numero entrante', filterable=True),
                TableColumn(key='nombre_cliente', label='Nombre del cliente', filterable=True),
                TableColumn(key='razones_llamada', label='Razones de la llamada', filterable=True),
                TableColumn(key='duracion', label='Duracion', sortable=True),
                TableColumn(key='resolucion', label='Resolucion', filterable=True, sortable=True),
                TableColumn(key='detail', label='Detalle'),
            ]

        return DashboardResponse(
            table=TablePayload(
                columns=columns,
                rows=rows,
                nextCursor='page-2',
            )
        )

    async def get_detail(self, ctx: AdapterContext, id: str, req: QueryRequest | None) -> DashboardDetailResponse:
        if ctx.caso_de_uso == 'prestamos':
            return DashboardDetailResponse(
                left=LeftPanel(
                    messages=[
                        MessageBlock(role='cliente', text='Quiero revisar las condiciones del prestamo', timestamp='11:15'),
                        MessageBlock(role='agente', text='Te muestro el resumen de condiciones', timestamp='11:16'),
                        MessageBlock(role='agente', text='Necesito confirmar ingresos mensuales', timestamp='11:17'),
                    ]
                ),
                right=[
                    ListPanel(
                        type='list',
                        title='Documentacion',
                        items=['DNI', 'Nominas', 'Declaracion de renta'],
                    ),
                    TimelinePanel(
                        type='timeline',
                        title='Hitos',
                        events=[
                            TimelineEvent(label='Solicitud recibida', time='2026-02-20 09:30'),
                            TimelineEvent(label='Analisis de riesgo', time='2026-02-20 12:15'),
                            TimelineEvent(label='Revision final', time='2026-02-20 13:42'),
                        ],
                    ),
                    MetricsPanel(
                        type='metrics',
                        title='Metricas',
                        metrics=[
                            MetricItem(label='ID', value=id),
                            MetricItem(label='Turnos', value=6),
                            MetricItem(label='Riesgo', value='Medio'),
                        ],
                    ),
                ],
            )

        return DashboardDetailResponse(
            left=LeftPanel(
                messages=[
                    MessageBlock(role='cliente', text='Necesito informacion sobre una hipoteca fija', timestamp='10:01'),
                    MessageBlock(role='agente', text='Claro, que importe necesitas?', timestamp='10:02'),
                    MessageBlock(role='cliente', text='Unos 180.000 euros a 30 anos', timestamp='10:03'),
                ]
            ),
            right=[
                KVPanel(
                    type='kv',
                    title='Contexto',
                    items=[
                        KVItem(key='Canal', value='Web'),
                        KVItem(key='Caso de uso', value=ctx.caso_de_uso),
                        KVItem(key='Pais', value='ES'),
                    ],
                ),
                MetricsPanel(
                    type='metrics',
                    title='Metricas',
                    metrics=[
                        MetricItem(label='Sentimiento', value='Positivo'),
                        MetricItem(label='Mensajes', value=12),
                        MetricItem(label='Id', value=id),
                    ],
                ),
            ],
        )
