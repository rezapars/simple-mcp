from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendSettings(BaseSettings):
    app_name: str = "Mock Client Backend"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKEND_",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_backend_settings() -> BackendSettings:
    return BackendSettings()
