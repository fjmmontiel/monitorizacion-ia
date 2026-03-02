from collections.abc import Callable

from orchestrator.adapters.base import Adapter
from orchestrator.adapters.http_proxy import HttpProxyAdapter
from orchestrator.adapters.native import NativeAdapter
from orchestrator.core.errors import ErrorCode, OrchestratorError
from orchestrator.core.use_case_loader import RoutingConfig


AdapterFactory = Callable[[str], Adapter]


class AdapterRegistry:
    def __init__(
        self,
        routing: RoutingConfig,
        default_timeout_ms: int,
        adapter_factories: dict[str, AdapterFactory] | None = None,
    ):
        self.routing = routing
        self.default_timeout_ms = default_timeout_ms
        self._adapter_instances: dict[str, Adapter] = {}
        self._adapter_factories: dict[str, AdapterFactory] = {
            'native': self._build_native_adapter,
            'http_proxy': self._build_http_proxy_adapter,
            **(adapter_factories or {}),
        }

    def resolve(self, caso_de_uso: str) -> Adapter:
        if caso_de_uso in self._adapter_instances:
            return self._adapter_instances[caso_de_uso]

        cfg = self.routing.use_cases.get(caso_de_uso)
        if not cfg:
            raise OrchestratorError(
                ErrorCode.UNKNOWN_USE_CASE,
                f'caso_de_uso not registered: {caso_de_uso}',
                404,
            )

        factory = self._adapter_factories.get(cfg.adapter)
        if not factory:
            raise OrchestratorError(ErrorCode.VALIDATION_ERROR, f'Unsupported adapter: {cfg.adapter}', 500)

        adapter = factory(caso_de_uso)
        self._adapter_instances[caso_de_uso] = adapter
        return adapter

    def timeout_for(self, caso_de_uso: str) -> int:
        cfg = self.routing.use_cases[caso_de_uso]
        return cfg.timeouts.ms or self.default_timeout_ms

    def _build_native_adapter(self, caso_de_uso: str) -> Adapter:
        cfg = self.routing.use_cases[caso_de_uso]
        return NativeAdapter(cfg)

    def _build_http_proxy_adapter(self, caso_de_uso: str) -> Adapter:
        cfg = self.routing.use_cases[caso_de_uso]
        return HttpProxyAdapter(cfg, self.default_timeout_ms)
