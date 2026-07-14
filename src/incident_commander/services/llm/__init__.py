"""LLM client interfaces and implementations."""

from __future__ import annotations

from incident_commander.config import ModelProvider, Settings
from incident_commander.domain.exceptions import ConfigurationError
from incident_commander.services.llm.anthropic_adapter import AnthropicModelClient
from incident_commander.services.llm.base import ModelClient
from incident_commander.services.llm.fake import FakeModelClient


def create_model_client(settings: Settings) -> ModelClient:
    """Factory that returns the configured model client implementation.

    Defaults to :class:`FakeModelClient`, which requires no API key.
    """
    if settings.model_provider == ModelProvider.FAKE:
        return FakeModelClient(model_name=settings.model_name)

    if settings.model_provider == ModelProvider.ANTHROPIC:
        api_key = settings.require_anthropic_api_key()
        return AnthropicModelClient(
            api_key=api_key.get_secret_value(),
            model_name=settings.anthropic_model,
            timeout_seconds=settings.model_timeout_seconds,
            max_retries=settings.model_max_retries,
        )

    raise ConfigurationError(
        f"Unsupported model provider: {settings.model_provider}",
        code="unsupported_model_provider",
        details={"provider": str(settings.model_provider)},
    )


__all__ = [
    "AnthropicModelClient",
    "FakeModelClient",
    "ModelClient",
    "create_model_client",
]
