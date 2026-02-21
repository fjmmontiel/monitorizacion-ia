from fastapi import FastAPI

from orchestrator.adapters.registry import AdapterRegistry
from orchestrator.api.routes import router
from orchestrator.core.errors import install_error_handlers
from orchestrator.core.logging import configure_logging
from orchestrator.core.settings import settings
from orchestrator.core.use_case_loader import UseCaseLoader


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    loader = UseCaseLoader(settings.ORCH_CONFIG_PATH)
    routing = loader.load()
    app.state.adapter_registry = AdapterRegistry(routing, settings.UPSTREAM_TIMEOUT_MS)
    app.include_router(router)
    install_error_handlers(app)
    return app


app = create_app()
