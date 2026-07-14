"""Fixture loader and scenario consistency tests."""

from __future__ import annotations

import pytest

from incident_commander.domain.exceptions import FixtureValidationError
from incident_commander.fixtures import list_scenario_ids, load_scenario
from incident_commander.fixtures.schema import ScenarioBundle

EXPECTED_SCENARIOS = {
    "connection-pool-exhaustion",
    "payment-service-timeout",
    "feature-flag-misconfiguration",
    "queue-saturation-retry-amplification",
    "insufficient-evidence",
}


def test_lists_all_five_scenarios() -> None:
    assert set(list_scenario_ids()) == EXPECTED_SCENARIOS


@pytest.mark.parametrize("scenario_id", sorted(EXPECTED_SCENARIOS))
def test_each_scenario_loads_and_is_consistent(scenario_id: str) -> None:
    bundle = load_scenario(scenario_id)
    assert isinstance(bundle, ScenarioBundle)
    assert bundle.scenario_id == scenario_id
    assert bundle.expected_root_cause
    assert bundle.metrics
    assert bundle.logs
    assert bundle.traces
    assert bundle.deployments
    assert bundle.configuration_changes
    assert bundle.code_changes
    assert bundle.runbooks
    assert bundle.historical_incidents
    assert bundle.safe_remediation_options
    assert bundle.unsafe_remediation_options

    seed_ids = {item.evidence_id for item in bundle.seed_evidence}
    assert set(bundle.expected_evidence_ids).issubset(seed_ids)
    assert set(bundle.evidence_required_for_evaluation).issubset(seed_ids)

    topology_services = {node.name for node in bundle.topology.services}
    required_services = (
        "frontend",
        "checkout-api",
        "inventory-service",
        "payment-service",
        "postgres",
        "redis",
    )
    for service in required_services:
        assert service in topology_services

    for action in bundle.safe_remediation_options:
        assert action.is_safe is True
    for action in bundle.unsafe_remediation_options:
        assert action.is_safe is False


def test_unknown_scenario_raises() -> None:
    with pytest.raises(FixtureValidationError):
        load_scenario("does-not-exist")


def test_insufficient_evidence_marks_unknown_root_cause() -> None:
    bundle = load_scenario("insufficient-evidence")
    assert "unknown" in bundle.expected_root_cause.lower()
    assert any(
        action.action_type.value == "investigate_further"
        for action in bundle.safe_remediation_options
    )
