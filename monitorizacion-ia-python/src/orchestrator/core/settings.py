from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    ENVIRONMENT: str = Field(default='development')
    PROJECT_NAME: str = Field(default='monitorizacion-ia-orchestrator')
    PROJECT_VERSION: str = Field(default='0.1.0')
    ORCH_CONFIG_PATH: str = Field(default='src/orchestrator/config/use_cases.yaml')
    UPSTREAM_TIMEOUT_MS: int = Field(default=5000, ge=100, le=60000)
    UPSTREAM_LIMIT_DEFAULT: int = Field(default=25, ge=1, le=1000)
    UPSTREAM_LIMIT_MAX: int = Field(default=100, ge=1, le=1000)


settings = Settings()
