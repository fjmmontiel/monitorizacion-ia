from dataclasses import dataclass

from orchestrator.api.schemas import (
    CardsResponse,
    DashboardDetailResponse,
    DashboardResponse,
    QueryRequest,
)


@dataclass
class AdapterContext:
    caso_de_uso: str
    request_id: str | None
    trace_id: str | None
    timeout_ms: int
    user: str | None = None
    roles: list[str] | None = None


class Adapter:
    async def get_cards(self, ctx: AdapterContext, req: QueryRequest) -> CardsResponse:
        raise NotImplementedError

    async def get_dashboard(self, ctx: AdapterContext, req: QueryRequest) -> DashboardResponse:
        raise NotImplementedError

    async def get_detail(self, ctx: AdapterContext, id: str, req: QueryRequest | None) -> DashboardDetailResponse:
        raise NotImplementedError
