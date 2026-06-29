from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    app_name: str = "AI Content Generator API"
    app_version: str = "1.0.0"
    environment: str = "development"

    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", validation_alias="GROQ_MODEL")
    groq_temperature: float = Field(default=0.7, ge=0.0, le=2.0, validation_alias="GROQ_TEMPERATURE")
    groq_max_tokens: int = Field(default=512, ge=1, le=8192, validation_alias="GROQ_MAX_TOKENS")

    rate_limit_requests: int = Field(default=60, ge=1, validation_alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, ge=1, validation_alias="RATE_LIMIT_WINDOW_SECONDS")

    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
