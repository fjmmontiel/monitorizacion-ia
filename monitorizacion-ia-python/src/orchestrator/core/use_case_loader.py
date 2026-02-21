from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class UpstreamRoutes(BaseModel):
    cards: str = '/cards'
    dashboard: str = '/dashboard'
    dashboard_detail: str = '/dashboard_detail'


class UpstreamConfig(BaseModel):
    base_url: str
    routes: UpstreamRoutes = Field(default_factory=UpstreamRoutes)


class UseCaseTimeouts(BaseModel):
    ms: int | None = None


class UseCaseConfig(BaseModel):
    adapter: str
    upstream: UpstreamConfig | None = None
    timeouts: UseCaseTimeouts = Field(default_factory=UseCaseTimeouts)
    headers_passthrough: dict | None = None


class RoutingConfig(BaseModel):
    use_cases: dict[str, UseCaseConfig]


class UseCaseLoader:
    def __init__(self, config_path: str):
        self._config_path = Path(config_path)

    def load(self) -> RoutingConfig:
        if not self._config_path.exists():
            raise FileNotFoundError(f'Routing config not found: {self._config_path}')
        data = yaml.safe_load(self._config_path.read_text(encoding='utf-8')) or {}
        return RoutingConfig.model_validate(data)
