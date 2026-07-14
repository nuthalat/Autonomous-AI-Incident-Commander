"""Load and validate synthetic incident scenario fixtures."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from incident_commander.domain.exceptions import FixtureValidationError
from incident_commander.fixtures.schema import ScenarioBundle

SCENARIO_PACKAGE = "incident_commander.fixtures.scenarios"
REQUIRED_PART_FILES: tuple[str, ...] = (
    "manifest.json",
    "incident.json",
    "topology.json",
    "metrics.json",
    "logs.json",
    "traces.json",
    "deployments.json",
    "configuration.json",
    "code_changes.json",
    "runbooks.json",
    "historical_incidents.json",
    "seed_evidence.json",
)


def list_scenario_ids() -> list[str]:
    """Return sorted scenario directory names packaged with the library."""
    root = resources.files(SCENARIO_PACKAGE)
    ids: list[str] = []
    for path in root.iterdir():
        if not path.is_dir() or path.name.startswith("_"):
            continue
        if path.joinpath("manifest.json").is_file():
            ids.append(path.name)
    return sorted(ids)


def load_scenario(scenario_id: str) -> ScenarioBundle:
    """Load a scenario by ID from packaged fixture data."""
    scenario_root = resources.files(SCENARIO_PACKAGE).joinpath(scenario_id)
    if not scenario_root.is_dir():
        raise FixtureValidationError(
            f"Unknown scenario: {scenario_id}",
            details={"scenario_id": scenario_id, "available": list_scenario_ids()},
        )
    return _load_from_traversable(scenario_root, scenario_id=scenario_id)


def load_scenario_from_dir(directory: Path, *, scenario_id: str | None = None) -> ScenarioBundle:
    """Load and validate a scenario from a filesystem directory."""
    if not directory.is_dir():
        raise FixtureValidationError(
            f"Scenario directory does not exist: {directory}",
            details={"path": str(directory)},
        )
    resolved_id = scenario_id or directory.name
    missing = [name for name in REQUIRED_PART_FILES if not (directory / name).is_file()]
    if missing:
        raise FixtureValidationError(
            f"Scenario {resolved_id} missing required files",
            details={"missing": missing, "path": str(directory)},
        )

    def read_part(name: str) -> Any:
        return _read_json_text((directory / name).read_text(encoding="utf-8"), name=name)

    manifest = read_part("manifest.json")
    if not isinstance(manifest, dict):
        raise FixtureValidationError(
            "manifest.json must contain an object",
            details={"path": str(directory)},
        )

    payload: dict[str, Any] = {
        **manifest,
        "scenario_id": resolved_id,
        "incident": read_part("incident.json"),
        "topology": read_part("topology.json"),
        "metrics": read_part("metrics.json"),
        "logs": read_part("logs.json"),
        "traces": read_part("traces.json"),
        "deployments": read_part("deployments.json"),
        "configuration_changes": read_part("configuration.json"),
        "code_changes": read_part("code_changes.json"),
        "runbooks": read_part("runbooks.json"),
        "historical_incidents": read_part("historical_incidents.json"),
        "seed_evidence": read_part("seed_evidence.json"),
    }
    return _validate_payload(payload, scenario_id=resolved_id)


@lru_cache(maxsize=16)
def load_scenario_cached(scenario_id: str) -> ScenarioBundle:
    """Cached scenario loader for repeated CLI/eval access."""
    return load_scenario(scenario_id)


def clear_scenario_cache() -> None:
    """Clear the scenario loader cache (tests)."""
    load_scenario_cached.cache_clear()


def _load_from_traversable(root: Traversable, *, scenario_id: str) -> ScenarioBundle:
    missing = [name for name in REQUIRED_PART_FILES if not root.joinpath(name).is_file()]
    if missing:
        raise FixtureValidationError(
            f"Scenario {scenario_id} missing required files",
            details={"missing": missing, "scenario_id": scenario_id},
        )

    manifest = _read_json_resource(root.joinpath("manifest.json"))
    if not isinstance(manifest, dict):
        raise FixtureValidationError(
            "manifest.json must contain an object",
            details={"scenario_id": scenario_id},
        )

    payload: dict[str, Any] = {
        **manifest,
        "scenario_id": scenario_id,
        "incident": _read_json_resource(root.joinpath("incident.json")),
        "topology": _read_json_resource(root.joinpath("topology.json")),
        "metrics": _read_json_resource(root.joinpath("metrics.json")),
        "logs": _read_json_resource(root.joinpath("logs.json")),
        "traces": _read_json_resource(root.joinpath("traces.json")),
        "deployments": _read_json_resource(root.joinpath("deployments.json")),
        "configuration_changes": _read_json_resource(root.joinpath("configuration.json")),
        "code_changes": _read_json_resource(root.joinpath("code_changes.json")),
        "runbooks": _read_json_resource(root.joinpath("runbooks.json")),
        "historical_incidents": _read_json_resource(root.joinpath("historical_incidents.json")),
        "seed_evidence": _read_json_resource(root.joinpath("seed_evidence.json")),
    }
    return _validate_payload(payload, scenario_id=scenario_id)


def _validate_payload(payload: dict[str, Any], *, scenario_id: str) -> ScenarioBundle:
    try:
        return ScenarioBundle.model_validate(payload)
    except ValidationError as exc:
        raise FixtureValidationError(
            f"Scenario fixture failed validation: {scenario_id}",
            details={"scenario_id": scenario_id, "errors": exc.errors()},
        ) from exc


def _read_json_resource(path: Traversable) -> Any:
    return _read_json_text(path.read_text(encoding="utf-8"), name=path.name)


def _read_json_text(text: str, *, name: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise FixtureValidationError(
            f"Invalid JSON in {name}",
            details={"name": name, "error": str(exc)},
        ) from exc
