"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from incident_commander.config import Environment, ModelProvider, Settings, clear_settings_cache
from incident_commander.main import create_app


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """Ensure settings cache does not leak across tests."""
    clear_settings_cache()
    yield
    clear_settings_cache()


@pytest.fixture
def test_settings() -> Settings:
    """Settings suitable for offline unit tests."""
    return Settings(
        app_name="Incident Commander Test",
        environment=Environment.TEST,
        debug=True,
        log_level="WARNING",
        log_json=False,
        model_provider=ModelProvider.FAKE,
        model_name="fake-test-v1",
        dry_run=True,
        read_only=True,
        readiness_check_database=False,
        readiness_check_redis=False,
    )


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """HTTP test client bound to a fresh application instance."""
    app = create_app(settings=test_settings)
    with TestClient(app) as test_client:
        yield test_client
