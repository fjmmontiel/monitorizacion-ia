import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Header, Query, Request

from orchestrator.adapters.base import AdapterContext
from orchestrator.adapters.registry import AdapterRegistry
from orchestrator.api.schemas import (
    CardsResponse,
    DatopsOverviewResponse,
    DatopsRoutes,
    DatopsUseCase,
    DashboardDetailResponse,
    DashboardResponse,
    QueryRequest,
)
from orchestrator.core.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_registry(request: Request) -> AdapterRegistry:
    return request.app.state.adapter_registry


@router.get('/health', tags=['Root'])
async def health() -> dict:
    return {'status': 'ok', 'service': settings.PROJECT_NAME, 'version': settings.PROJECT_VERSION}


@router.post('/cards', response_model=CardsResponse)
async def cards(
    request: Request,
    req: QueryRequest,
    caso_de_uso: str = Query(..., min_length=1),
    x_request_id: str | None = Header(default=None),
    x_trace_id: str | None = Header(default=None),
) -> CardsResponse:
    registry = get_registry(request)
    adapter = registry.resolve(caso_de_uso)
    request_id = x_request_id or getattr(request.state, 'request_id', None)
    ctx = AdapterContext(caso_de_uso, request_id, x_trace_id, registry.timeout_for(caso_de_uso))
    return await adapter.get_cards(ctx, req)


@router.post('/dashboard', response_model=DashboardResponse)
async def dashboard(
    request: Request,
    req: QueryRequest,
    caso_de_uso: str = Query(..., min_length=1),
    x_request_id: str | None = Header(default=None),
    x_trace_id: str | None = Header(default=None),
) -> DashboardResponse:
    registry = get_registry(request)
    adapter = registry.resolve(caso_de_uso)
    request_id = x_request_id or getattr(request.state, 'request_id', None)
    ctx = AdapterContext(caso_de_uso, request_id, x_trace_id, registry.timeout_for(caso_de_uso))
    return await adapter.get_dashboard(ctx, req)


@router.post('/dashboard_detail', response_model=DashboardDetailResponse)
async def dashboard_detail(
    request: Request,
    req: QueryRequest | None = Body(default=None),
    caso_de_uso: str = Query(..., min_length=1),
    id: str = Query(..., min_length=1),
    x_request_id: str | None = Header(default=None),
    x_trace_id: str | None = Header(default=None),
) -> DashboardDetailResponse:
    registry = get_registry(request)
    adapter = registry.resolve(caso_de_uso)
    request_id = x_request_id or getattr(request.state, 'request_id', None)
    ctx = AdapterContext(caso_de_uso, request_id, x_trace_id, registry.timeout_for(caso_de_uso))
    return await adapter.get_detail(ctx, id, req)


@router.get('/datops/overview', response_model=DatopsOverviewResponse, tags=['DatOps'])
async def datops_overview(request: Request) -> DatopsOverviewResponse:
    registry = get_registry(request)
    use_cases = []
    for case_id, cfg in registry.routing.use_cases.items():
        use_cases.append(
            DatopsUseCase(
                id=case_id,
                adapter=cfg.adapter,
                timeout_ms=registry.timeout_for(case_id),
                upstream_base_url=cfg.upstream.base_url if cfg.upstream else None,
                routes=DatopsRoutes(
                    cards=f'/cards?caso_de_uso={case_id}',
                    dashboard=f'/dashboard?caso_de_uso={case_id}',
                    dashboard_detail=f'/dashboard_detail?caso_de_uso={case_id}&id={{id}}',
                ),
            )
        )

    return DatopsOverviewResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        profile=settings.ENVIRONMENT,
        use_cases=use_cases,
    )
