import json
from pathlib import Path

from orchestrator.adapters.base import Adapter, AdapterContext
from orchestrator.api.schemas import CardsResponse, DashboardDetailResponse, DashboardResponse, QueryRequest
from orchestrator.core.errors import ErrorCode, OrchestratorError


class NativeAdapter(Adapter):
    """Adapter nativo basado en JSON local por caso de uso (sin hardcodes)."""

    def __init__(self, local_data_dir: str | None = None):
        self._local_data_dir = local_data_dir
        self._cache: dict[str, dict] = {}

    async def get_cards(self, ctx: AdapterContext, req: QueryRequest) -> CardsResponse:
        payload = self._read_payload(ctx.caso_de_uso, 'cards.json')
        return CardsResponse.model_validate(payload)

    async def get_dashboard(self, ctx: AdapterContext, req: QueryRequest) -> DashboardResponse:
        payload = self._read_payload(ctx.caso_de_uso, 'dashboard.json')
        return DashboardResponse.model_validate(payload)

    async def get_detail(self, ctx: AdapterContext, id: str, req: QueryRequest | None) -> DashboardDetailResponse:
        payload = self._read_payload(ctx.caso_de_uso, 'dashboard_detail.json')
        return DashboardDetailResponse.model_validate(payload)

    def _resolve_base_path(self, caso_de_uso: str) -> Path:
        if self._local_data_dir:
            return Path(self._local_data_dir)
        return Path(__file__).resolve().parents[1] / 'data' / caso_de_uso

    def _read_payload(self, caso_de_uso: str, filename: str) -> dict:
        path = self._resolve_base_path(caso_de_uso) / filename
        cache_key = str(path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not path.exists():
            raise OrchestratorError(
                ErrorCode.VALIDATION_ERROR,
                f'Local data file not found for {caso_de_uso}: {path}',
                500,
            )

        payload = json.loads(path.read_text(encoding='utf-8'))
        self._cache[cache_key] = payload
        return payload
