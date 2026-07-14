"""API tests for liveness and readiness endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from incident_commander.config import Settings
from incident_commander.main import create_app
from incident_commander.models.health import DependencyStatus
from incident_commander.services.health import HealthService


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"]
    assert payload["service"]


def test_ready_returns_ok_by_default(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is True
    assert payload["status"] == "ok"
    assert any(check["name"] == "application" for check in payload["checks"])


def test_ready_returns_503_when_dependency_fails(test_settings: Settings) -> None:
    app = create_app(settings=test_settings)

    async def db_down() -> DependencyStatus:
        return DependencyStatus(name="postgres", healthy=False, message="not ready")

    app.state.health_service = HealthService(
        settings=test_settings,
        dependency_checks=[db_down],
    )

    with TestClient(app) as client:
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["ready"] is False
