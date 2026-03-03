from datetime import datetime, timezone

from fastapi import APIRouter, Body, Header, Query, Request
from fastapi import HTTPException

from orchestrator.adapters.base import AdapterContext
from orchestrator.adapters.http_proxy import HttpProxyAdapter
from orchestrator.adapters.native import NativeAdapter
from orchestrator.api.schemas import (
    CardsResponse,
    DatopsOverviewResponse,
    DatopsRoutes,
    DatopsUseCase,
    DashboardDetailResponse,
    DashboardResponse,
    QueryRequest,
    UIShellResponse,
    UIShellSystem,
    UIShellTab,
    ViewConfigCreate,
    ViewConfiguration,
    ViewConfigUpdate,
)
from orchestrator.core.errors import ErrorCode, OrchestratorError
from orchestrator.core.settings import settings

router = APIRouter()


def _use_case_label(case_id: str) -> str:
    return case_id.replace('_', ' ').title()


def _resolve_configured_view(request: Request, case_id: str) -> ViewConfiguration | None:
    views = get_view_store(request).list_configs(system=case_id, enabled=True)
    if not views:
        return None
    return sorted(views, key=lambda item: item.name)[0]


def _resolve_system_view(request: Request, case_id: str) -> ViewConfiguration:
    configured_view = _resolve_configured_view(request, case_id)
    if configured_view is not None:
        return configured_view
    raise OrchestratorError(
        ErrorCode.UNKNOWN_USE_CASE,
        f'caso_de_uso not configured in view storage: {case_id}',
        404,
    )


def _iter_available_systems(request: Request):
    seen: set[str] = set()
    configured_views = sorted(get_view_store(request).list_configs(enabled=True), key=lambda item: (item.system, item.name))
    for view in configured_views:
        if view.system in seen:
            continue
        seen.add(view.system)
        yield view.system


def _effective_system_metadata(request: Request, case_id: str):
    view = _resolve_configured_view(request, case_id)
    if view is None:
        return None

    if view.runtime is not None:
        return {
            'adapter': view.runtime.adapter,
            'timeout_ms': settings.UPSTREAM_TIMEOUT_MS,
            'upstream_base_url': view.runtime.upstream_base_url,
        }

    return {
        'adapter': 'native',
        'timeout_ms': settings.UPSTREAM_TIMEOUT_MS,
        'upstream_base_url': None,
    }


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
    request_id = x_request_id or getattr(request.state, 'request_id', None)
    view = _resolve_system_view(request, caso_de_uso)
    if view.runtime is not None:
        adapter = HttpProxyAdapter(view.runtime.upstream_base_url, settings.UPSTREAM_TIMEOUT_MS)
        timeout_ms = settings.UPSTREAM_TIMEOUT_MS
    else:
        adapter = NativeAdapter()
        timeout_ms = settings.UPSTREAM_TIMEOUT_MS
    ctx = AdapterContext(caso_de_uso, request_id, x_trace_id, timeout_ms)
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
    use_cases = []
    for case_id in _iter_available_systems(request):
        metadata = _effective_system_metadata(request, case_id)
        if metadata is None:
            continue
        use_cases.append(
            DatopsUseCase(
                id=case_id,
                label=_use_case_label(case_id),
                adapter=metadata['adapter'],
                timeout_ms=metadata['timeout_ms'],
                upstream_base_url=metadata['upstream_base_url'],
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


@router.get('/ui/shell', response_model=UIShellResponse, tags=['UI'])
async def ui_shell(request: Request) -> UIShellResponse:
    available_systems = list(_iter_available_systems(request))
    default_case = available_systems[0] if available_systems else None
    if default_case is None and available_systems:
        default_case = available_systems[0]

    systems = []
    for case_id in available_systems:
        label = _use_case_label(case_id)
        systems.append(
            UIShellSystem(
                id=case_id,
                label=label,
                default=case_id == default_case,
                route_path=f'/monitor?caso_de_uso={case_id}',
                view=_resolve_system_view(request, case_id),
            )
        )

    return UIShellResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        home=UIShellTab(id='home', label='HOME', path='/home'),
        systems=systems,
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
