import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Header, Query, Request
from fastapi import HTTPException

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
    ViewConfigCreate,
    ViewConfiguration,
    ViewConfigUpdate,
)
from orchestrator.core.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_registry(request: Request) -> AdapterRegistry:
    return request.app.state.adapter_registry


def get_view_store(request: Request):
    return request.app.state.view_config_store


def get_metrics(request: Request):
    return request.app.state.metrics


def _admin_client_key(request: Request) -> str:
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


def enforce_admin_rate_limit(request: Request) -> None:
    limiter = request.app.state.admin_rate_limiter
    if not limiter.allow(_admin_client_key(request)):
        raise HTTPException(status_code=429, detail='admin rate limit exceeded')


async def execute_use_case_operation(
    request: Request,
    caso_de_uso: str,
    x_request_id: str | None,
    x_trace_id: str | None,
    operation,
):
    registry = get_registry(request)
    adapter = registry.resolve(caso_de_uso)
    request_id = x_request_id or getattr(request.state, 'request_id', None)
    ctx = AdapterContext(caso_de_uso, request_id, x_trace_id, registry.timeout_for(caso_de_uso))
    return await operation(adapter, ctx)


@router.get('/health', tags=['Root'])
async def health() -> dict:
    return {'status': 'ok', 'service': settings.PROJECT_NAME, 'version': settings.PROJECT_VERSION}


@router.get('/metrics', tags=['Root'])
async def metrics(request: Request) -> dict:
    return get_metrics(request).snapshot()


@router.post('/cards', response_model=CardsResponse)
async def cards(
    request: Request,
    req: QueryRequest,
    caso_de_uso: str = Query(..., min_length=1),
    x_request_id: str | None = Header(default=None),
    x_trace_id: str | None = Header(default=None),
) -> CardsResponse:
    return await execute_use_case_operation(
        request,
        caso_de_uso,
        x_request_id,
        x_trace_id,
        lambda adapter, ctx: adapter.get_cards(ctx, req),
    )


@router.post('/dashboard', response_model=DashboardResponse)
async def dashboard(
    request: Request,
    req: QueryRequest,
    caso_de_uso: str = Query(..., min_length=1),
    x_request_id: str | None = Header(default=None),
    x_trace_id: str | None = Header(default=None),
) -> DashboardResponse:
    return await execute_use_case_operation(
        request,
        caso_de_uso,
        x_request_id,
        x_trace_id,
        lambda adapter, ctx: adapter.get_dashboard(ctx, req),
    )


@router.post('/dashboard_detail', response_model=DashboardDetailResponse)
async def dashboard_detail(
    request: Request,
    req: QueryRequest | None = Body(default=None),
    caso_de_uso: str = Query(..., min_length=1),
    id: str = Query(..., min_length=1),
    x_request_id: str | None = Header(default=None),
    x_trace_id: str | None = Header(default=None),
) -> DashboardDetailResponse:
    return await execute_use_case_operation(
        request,
        caso_de_uso,
        x_request_id,
        x_trace_id,
        lambda adapter, ctx: adapter.get_detail(ctx, id, req),
    )


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


@router.get('/admin/view-configs', response_model=list[ViewConfiguration], tags=['Admin'])
async def list_view_configs(
    request: Request,
    system: str | None = Query(default=None, min_length=1),
    enabled: bool | None = Query(default=None),
) -> list[ViewConfiguration]:
    return get_view_store(request).list_configs(system=system, enabled=enabled)


@router.get('/admin/view-configs/{view_id}', response_model=ViewConfiguration, tags=['Admin'])
async def get_view_config(request: Request, view_id: str) -> ViewConfiguration:
    try:
        return get_view_store(request).get(view_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=f'view_id not found: {view_id}') from error


@router.post('/admin/view-configs', response_model=ViewConfiguration, tags=['Admin'])
async def create_view_config(request: Request, payload: ViewConfigCreate) -> ViewConfiguration:
    enforce_admin_rate_limit(request)
    try:
        return get_view_store(request).create(payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.put('/admin/view-configs/{view_id}', response_model=ViewConfiguration, tags=['Admin'])
async def update_view_config(request: Request, view_id: str, payload: ViewConfigUpdate) -> ViewConfiguration:
    enforce_admin_rate_limit(request)
    try:
        return get_view_store(request).update(view_id, payload)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=f'view_id not found: {view_id}') from error


@router.delete('/admin/view-configs/{view_id}', status_code=204, tags=['Admin'])
async def delete_view_config(request: Request, view_id: str) -> None:
    enforce_admin_rate_limit(request)
    try:
        get_view_store(request).delete(view_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=f'view_id not found: {view_id}') from error
