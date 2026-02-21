import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from orchestrator.adapters.registry import AdapterRegistry
from orchestrator.api.routes import router
from orchestrator.core.errors import install_error_handlers
from orchestrator.core.logging import configure_logging
from orchestrator.core.settings import settings
from orchestrator.core.use_case_loader import UseCaseLoader

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://127.0.0.1:3100', 'http://localhost:3100'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    loader = UseCaseLoader(settings.ORCH_CONFIG_PATH)
    routing = loader.load()
    app.state.adapter_registry = AdapterRegistry(routing, settings.UPSTREAM_TIMEOUT_MS)
    app.include_router(router)
    install_error_handlers(app)

    @app.middleware('http')
    async def request_logging_middleware(request: Request, call_next) -> Response:
        request_id = request.headers.get('x-request-id') or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        caso_de_uso = request.query_params.get('caso_de_uso', '-')
        response.headers['x-request-id'] = request_id
        logger.info(
            'request_id=%s method=%s path=%s status=%s latency_ms=%s caso_de_uso=%s',
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
            caso_de_uso,
        )
        return response

    return app


app = create_app()
