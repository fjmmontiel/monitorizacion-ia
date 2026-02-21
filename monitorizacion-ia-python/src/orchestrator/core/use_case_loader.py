from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator


class UpstreamRoutes(BaseModel):
    cards: str
    dashboard: str
    dashboard_detail: str


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

    @model_validator(mode='after')
    def validate_by_adapter(self):
        if self.adapter == 'http_proxy':
            if not self.upstream:
                raise ValueError('http_proxy adapter requires upstream config')
            if '{id}' not in self.upstream.routes.dashboard_detail:
                raise ValueError('upstream.routes.dashboard_detail must include {id} template')
        return self


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
