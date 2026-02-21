import httpx

from orchestrator.adapters.base import Adapter, AdapterContext
from orchestrator.api.schemas import (
    CardsResponse,
    DashboardDetailRequest,
    DashboardDetailResponse,
    DashboardResponse,
    QueryRequest,
)
from orchestrator.core.errors import ErrorCode, OrchestratorError
from orchestrator.core.use_case_loader import UseCaseConfig


class HttpProxyAdapter(Adapter):
    def __init__(self, cfg: UseCaseConfig, default_timeout_ms: int):
        if not cfg.upstream:
            raise ValueError('HttpProxyAdapter requires upstream config')
        self.cfg = cfg
        self.default_timeout_ms = default_timeout_ms

    async def _post(self, path: str, payload: dict, timeout_ms: int) -> dict:
        url = f"{self.cfg.upstream.base_url.rstrip('/')}{path}"
        try:
            async with httpx.AsyncClient(timeout=timeout_ms / 1000) as client:
                res = await client.post(url, json=payload)
        except httpx.TimeoutException as exc:
            raise OrchestratorError(ErrorCode.UPSTREAM_TIMEOUT, 'Upstream timeout', 504) from exc
        except httpx.HTTPError as exc:
            raise OrchestratorError(ErrorCode.UPSTREAM_ERROR, 'Upstream connection error', 502) from exc
        if res.status_code >= 400:
            raise OrchestratorError(
                ErrorCode.UPSTREAM_ERROR,
                'Upstream returned error',
                502,
                detail={'status_code': res.status_code},
            )
        return res.json()

    async def get_cards(self, ctx: AdapterContext, req: QueryRequest) -> CardsResponse:
        payload = await self._post(self.cfg.upstream.routes.cards, req.model_dump(), ctx.timeout_ms)
        return CardsResponse.model_validate(payload)

    async def get_dashboard(self, ctx: AdapterContext, req: QueryRequest) -> DashboardResponse:
        payload = await self._post(self.cfg.upstream.routes.dashboard, req.model_dump(), ctx.timeout_ms)
        return DashboardResponse.model_validate(payload)

    async def get_detail(self, ctx: AdapterContext, req: DashboardDetailRequest) -> DashboardDetailResponse:
        payload = await self._post(self.cfg.upstream.routes.dashboard_detail, req.model_dump(), ctx.timeout_ms)
        return DashboardDetailResponse.model_validate(payload)
