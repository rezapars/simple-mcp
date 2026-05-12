from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Client Onboarding MCP Service"
    app_version: str = "1.0.0"
    api_version: str = "v1"
    host: str = "0.0.0.0"
    port: int = 8000
    backend_base_url: str = "http://localhost:8001"
    request_timeout_seconds: float = 10.0
    log_level: str = "INFO"
    auth_required: bool = False
    api_key_header: str = "x-api-key"
    api_key: str = Field(default="local-dev-key", min_length=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MCP_",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
