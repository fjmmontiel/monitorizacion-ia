from orchestrator.adapters.base import Adapter, AdapterContext
from orchestrator.api.schemas import (
    CardItem,
    CardsResponse,
    DashboardAction,
    DashboardActionPayload,
    DashboardDetailRequest,
    DashboardDetailResponse,
    DashboardResponse,
    DashboardRow,
    DetailBlock,
    MessageBlock,
    QueryRequest,
)


class NativeAdapter(Adapter):
    async def get_cards(self, ctx: AdapterContext, req: QueryRequest) -> CardsResponse:
        return CardsResponse(cards=[CardItem(id='total', title=f'Total {ctx.caso_de_uso}', value=1)])

    async def get_dashboard(self, ctx: AdapterContext, req: QueryRequest) -> DashboardResponse:
        row = DashboardRow(
            id='row-1',
            data={'status': 'ok', 'caso_de_uso': ctx.caso_de_uso},
            detail=DashboardAction(payload=DashboardActionPayload(id='row-1')),
        )
        return DashboardResponse(columns=['id', 'status', 'caso_de_uso', 'detail'], rows=[row])

    async def get_detail(self, ctx: AdapterContext, req: DashboardDetailRequest) -> DashboardDetailResponse:
        return DashboardDetailResponse(
            id=req.id,
            left={'messages': [MessageBlock(role='assistant', text='Detalle generado por NativeAdapter')]},
            right={
                'blocks': [
                    DetailBlock(type='meta', title='Contexto', content={'caso_de_uso': ctx.caso_de_uso, 'id': req.id})
                ]
            },
        )
