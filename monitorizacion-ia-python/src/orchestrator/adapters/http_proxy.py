import httpx

from orchestrator.adapters.base import Adapter, AdapterContext
from orchestrator.api.schemas import (
    CardsResponse,
    DashboardDetailResponse,
    DashboardResponse,
    QueryRequest,
)
from orchestrator.core.errors import ErrorCode, OrchestratorError


class HttpProxyAdapter(Adapter):
    def __init__(
        self,
        base_url: str,
        default_timeout_ms: int,
        routes: dict[str, str] | None = None,
    ):
        self.base_url = base_url
        self.default_timeout_ms = default_timeout_ms
        self.routes = {
            'cards': '/cards',
            'dashboard': '/dashboard',
            'dashboard_detail': '/dashboard_detail/{id}',
            **(routes or {}),
        }

    async def _post(self, path: str, payload: dict, timeout_ms: int) -> dict:
        url = f"{self.base_url.rstrip('/')}{path}"
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
        payload = await self._post(self.routes['cards'], req.model_dump(), ctx.timeout_ms)
        return CardsResponse.model_validate(payload)

    async def get_dashboard(self, ctx: AdapterContext, req: QueryRequest) -> DashboardResponse:
        payload = await self._post(self.routes['dashboard'], req.model_dump(), ctx.timeout_ms)
        return DashboardResponse.model_validate(payload)

    async def get_detail(self, ctx: AdapterContext, id: str, req: QueryRequest | None) -> DashboardDetailResponse:
        detail_path = self.routes['dashboard_detail']
        if '{id}' in detail_path:
            detail_path = detail_path.replace('{id}', id)
        payload = await self._post(detail_path, (req or QueryRequest()).model_dump(), ctx.timeout_ms)
        return DashboardDetailResponse.model_validate(payload)
