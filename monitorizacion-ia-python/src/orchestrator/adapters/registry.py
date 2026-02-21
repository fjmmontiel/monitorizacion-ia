from orchestrator.adapters.base import Adapter
from orchestrator.adapters.http_proxy import HttpProxyAdapter
from orchestrator.adapters.native import NativeAdapter
from orchestrator.core.errors import ErrorCode, OrchestratorError
from orchestrator.core.use_case_loader import RoutingConfig


class AdapterRegistry:
    def __init__(self, routing: RoutingConfig, default_timeout_ms: int):
        self.routing = routing
        self.default_timeout_ms = default_timeout_ms

    def resolve(self, caso_de_uso: str) -> Adapter:
        cfg = self.routing.use_cases.get(caso_de_uso)
        if not cfg:
            raise OrchestratorError(
                ErrorCode.UNKNOWN_CASO_DE_USO,
                f'caso_de_uso not registered: {caso_de_uso}',
                404,
            )
        if cfg.adapter == 'http_proxy':
            return HttpProxyAdapter(cfg, self.default_timeout_ms)
        if cfg.adapter == 'native':
            return NativeAdapter()
        raise OrchestratorError(ErrorCode.VALIDATION_ERROR, f'Unsupported adapter: {cfg.adapter}', 500)

    def timeout_for(self, caso_de_uso: str) -> int:
        cfg = self.routing.use_cases[caso_de_uso]
        return cfg.timeouts.ms or self.default_timeout_ms
