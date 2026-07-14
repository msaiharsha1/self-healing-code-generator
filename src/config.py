"""Application configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"

    # LLM provider selection
    llm_provider: Literal["openai", "anthropic"] = "openai"

    # Application
    max_retries: int = 5
    execution_timeout: int = 10
    max_memory_mb: int = 256

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
