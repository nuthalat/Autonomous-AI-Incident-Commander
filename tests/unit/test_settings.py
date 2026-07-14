"""Tests for typed application settings."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from incident_commander.config import ModelProvider, Settings, clear_settings_cache, get_settings
from incident_commander.domain.exceptions import ConfigurationError


def test_default_model_provider_is_fake() -> None:
    settings = Settings()
    assert settings.model_provider == ModelProvider.FAKE
    assert settings.dry_run is True
    assert settings.read_only is True


def test_invalid_log_level_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(log_level="VERBOSE")


def test_require_anthropic_api_key_raises_when_missing() -> None:
    settings = Settings(model_provider=ModelProvider.ANTHROPIC, anthropic_api_key=None)
    with pytest.raises(ConfigurationError) as exc_info:
        settings.require_anthropic_api_key()
    assert exc_info.value.code == "missing_anthropic_api_key"


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_settings_cache()
    monkeypatch.setenv("INCIDENT_COMMANDER_APP_NAME", "Cached App")
    first = get_settings()
    monkeypatch.setenv("INCIDENT_COMMANDER_APP_NAME", "Changed App")
    second = get_settings()
    assert first is second
    assert first.app_name == "Cached App"
    clear_settings_cache()
    third = get_settings()
    assert third.app_name == "Changed App"
