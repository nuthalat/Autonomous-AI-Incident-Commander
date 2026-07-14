"""Typed application settings loaded from environment variables."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Annotated

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Deployment environment identifier."""

    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class ModelProvider(StrEnum):
    """Supported LLM providers for investigation agents."""

    FAKE = "fake"
    ANTHROPIC = "anthropic"


class Settings(BaseSettings):
    """Runtime configuration for the Incident Commander application.

    Values are loaded from environment variables with the
    ``INCIDENT_COMMANDER_`` prefix, plus ``ANTHROPIC_API_KEY`` for Claude.
    """

    model_config = SettingsConfigDict(
        env_prefix="INCIDENT_COMMANDER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Autonomous AI Incident Commander"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: str = "INFO"
    log_json: bool = True

    api_host: str = "0.0.0.0"  # noqa: S104 — intentional bind-all default for containers
    api_port: Annotated[int, Field(ge=1, le=65535)] = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_provider: ModelProvider = ModelProvider.FAKE
    model_name: str = "fake-deterministic-v1"
    model_timeout_seconds: Annotated[float, Field(gt=0)] = 60.0
    model_max_retries: Annotated[int, Field(ge=0)] = 2
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "ANTHROPIC_API_KEY",
            "INCIDENT_COMMANDER_ANTHROPIC_API_KEY",
        ),
    )

    dry_run: bool = True
    read_only: bool = True
    max_reinvestigation_loops: Annotated[int, Field(ge=0)] = 2
    max_agent_retries: Annotated[int, Field(ge=0)] = 2
    cost_budget_usd: Annotated[float, Field(ge=0)] = 5.0

    database_url: str = (
        "postgresql+asyncpg://incident:incident@localhost:5432/incident_commander"
    )
    database_pool_size: Annotated[int, Field(ge=1)] = 5
    redis_url: str = "redis://localhost:6379/0"

    approval_token_ttl_seconds: Annotated[int, Field(ge=1)] = 3600
    prompt_injection_filter: bool = True

    otel_enabled: bool = False
    otel_service_name: str = "incident-commander"
    otel_exporter_endpoint: str = "http://localhost:4317"

    # Stage 1 readiness: skip external dependency probes unless explicitly enabled.
    readiness_check_database: bool = False
    readiness_check_redis: bool = False

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Normalize log level to uppercase standard names."""
        normalized = value.strip().upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in allowed:
            msg = f"log_level must be one of {sorted(allowed)}, got {value!r}"
            raise ValueError(msg)
        return normalized

    @property
    def is_production(self) -> bool:
        """Return True when running in the production environment."""
        return self.environment == Environment.PRODUCTION

    def require_anthropic_api_key(self) -> SecretStr:
        """Return the Anthropic API key or raise if missing."""
        if self.anthropic_api_key is None or not self.anthropic_api_key.get_secret_value():
            from incident_commander.domain.exceptions import ConfigurationError

            raise ConfigurationError(
                "ANTHROPIC_API_KEY is required when model_provider=anthropic",
                code="missing_anthropic_api_key",
            )
        return self.anthropic_api_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Call :func:`clear_settings_cache` in tests when environment variables change.
    """
    return Settings()


def clear_settings_cache() -> None:
    """Clear the cached settings instance (primarily for tests)."""
    get_settings.cache_clear()
