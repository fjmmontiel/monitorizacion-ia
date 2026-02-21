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
    MessageBlock,
    MetricItem,
    MetricsPanel,
    QueryRequest,
    TableColumn,
    TablePayload,
    TableRow,
)


class NativeAdapter(Adapter):
    async def get_cards(self, ctx: AdapterContext, req: QueryRequest) -> CardsResponse:
        return CardsResponse(
            cards=[
                CardItem(title='Conversaciones activas', value=128, format='int'),
                CardItem(title='Tiempo medio de respuesta', value=2.31, format='seconds'),
                CardItem(title='Tasa de resolucion', value=0.92, format='percent'),
            ]
        )

    async def get_dashboard(self, ctx: AdapterContext, req: QueryRequest) -> DashboardResponse:
        rows = [
            TableRow(
                id='conv-001',
                detail=DetailAction(action='Ver detalle'),
                cliente='Ana Lopez',
                estado='Completada',
            ),
            TableRow(
                id='conv-002',
                detail=DetailAction(action='Ver detalle'),
                cliente='Luis Perez',
                estado='En curso',
            ),
        ]
        return DashboardResponse(
            table=TablePayload(
                columns=[
                    TableColumn(key='id', label='Id', sortable=True),
                    TableColumn(key='cliente', label='Cliente', filterable=True),
                    TableColumn(key='estado', label='Estado', filterable=True, sortable=True),
                    TableColumn(key='detail', label='Detalle'),
                ],
                rows=rows,
                nextCursor='page-2',
            )
        )

    async def get_detail(self, ctx: AdapterContext, id: str, req: QueryRequest | None) -> DashboardDetailResponse:
        return DashboardDetailResponse(
            left=LeftPanel(
                messages=[
                    MessageBlock(role='cliente', text='Necesito informacion sobre una hipoteca fija', timestamp='10:01'),
                    MessageBlock(role='agente', text='Claro, que importe necesitas?', timestamp='10:02'),
                ]
            ),
            right=[
                KVPanel(
                    type='kv',
                    title='Contexto',
                    items=[KVItem(key='Canal', value='Web'), KVItem(key='Caso de uso', value=ctx.caso_de_uso)],
                ),
                MetricsPanel(
                    type='metrics',
                    title='Metricas',
                    metrics=[MetricItem(label='Mensajes', value=12), MetricItem(label='Id', value=id)],
                ),
            ],
        )
