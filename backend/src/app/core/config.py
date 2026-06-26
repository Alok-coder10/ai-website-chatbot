from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI Website Assistant"
    app_version: str = "0.1.0"

    debug: bool = True

    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000

    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./assistant.db"

    llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    The settings are loaded only once during the application's lifetime.
    """
    return Settings()


settings: Settings = get_settings()