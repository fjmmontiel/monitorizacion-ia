from orchestrator.adapters.native import NativeAdapter
from orchestrator.adapters.base import AdapterContext
from orchestrator.api.schemas import QueryRequest
from orchestrator.core.use_case_loader import UseCaseConfig


async def _fetch_cards(adapter: NativeAdapter):
    return await adapter.get_cards(AdapterContext('hipotecas', None, None, 2500), QueryRequest())


def test_native_adapter_loads_from_local_json_default_path():
    adapter = NativeAdapter()
    import asyncio
    cards = asyncio.run(_fetch_cards(adapter))
    assert len(cards.cards) > 0


def test_native_adapter_supports_configured_local_data_dir(tmp_path):
    use_case_dir = tmp_path / 'custom'
    use_case_dir.mkdir(parents=True)
    (use_case_dir / 'cards.json').write_text('{"cards":[{"title":"X","value":1}]}', encoding='utf-8')
    (use_case_dir / 'dashboard.json').write_text('{"table":{"columns":[],"rows":[]}}', encoding='utf-8')
    (use_case_dir / 'dashboard_detail.json').write_text('{"left":{"messages":[]},"right":[]}', encoding='utf-8')

    cfg = UseCaseConfig.model_validate({'adapter': 'native', 'local_data_dir': str(use_case_dir)})
    adapter = NativeAdapter(cfg)

    import asyncio
    cards = asyncio.run(adapter.get_cards(AdapterContext('any', None, None, 2500), QueryRequest()))
    assert cards.cards[0].title == 'X'
