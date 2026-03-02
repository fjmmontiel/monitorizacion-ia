from orchestrator.adapters.base import Adapter, AdapterContext
from orchestrator.adapters.registry import AdapterRegistry
from orchestrator.core.use_case_loader import RoutingConfig


class FakeAdapter(Adapter):
    async def get_cards(self, ctx: AdapterContext, req):
        return {'cards': []}

    async def get_dashboard(self, ctx: AdapterContext, req):
        return {'table': {'columns': [], 'rows': []}}

    async def get_detail(self, ctx: AdapterContext, id: str, req):
        return {'left': {'messages': []}, 'right': []}


def test_resolve_caches_adapter_instances_per_use_case():
    routing = RoutingConfig.model_validate({'use_cases': {'hipotecas': {'adapter': 'native'}}})
    registry = AdapterRegistry(routing, default_timeout_ms=5000)

    first = registry.resolve('hipotecas')
    second = registry.resolve('hipotecas')

    assert first is second


def test_resolve_supports_custom_adapter_factory():
    routing = RoutingConfig.model_validate({'use_cases': {'hipotecas': {'adapter': 'custom'}}})

    registry = AdapterRegistry(
        routing,
        default_timeout_ms=5000,
        adapter_factories={'custom': lambda _: FakeAdapter()},
    )

    resolved = registry.resolve('hipotecas')
    assert isinstance(resolved, FakeAdapter)
