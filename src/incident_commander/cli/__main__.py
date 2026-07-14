"""CLI entrypoint: ``python -m incident_commander.cli``."""

from __future__ import annotations

import argparse
import json
import sys

from incident_commander import __version__
from incident_commander.config import get_settings
from incident_commander.logging import configure_logging, get_logger


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="incident-commander",
        description="Autonomous AI Incident Commander CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "version",
        help="Print the package version",
    )

    info_parser = subparsers.add_parser(
        "info",
        help="Show runtime configuration (secrets redacted)",
    )
    info_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON",
    )

    subparsers.add_parser(
        "list-scenarios",
        help="List packaged synthetic incident scenarios",
    )

    scenario_parser = subparsers.add_parser(
        "show-scenario",
        help="Show a synthetic incident scenario summary",
    )
    scenario_parser.add_argument(
        "scenario_id",
        help="Scenario identifier (see list-scenarios)",
    )
    scenario_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "version":
        print(__version__)
        return 0

    if args.command == "info":
        settings = get_settings()
        configure_logging(settings)
        logger = get_logger("incident_commander.cli")
        payload = {
            "version": __version__,
            "app_name": settings.app_name,
            "environment": settings.environment,
            "model_provider": settings.model_provider,
            "model_name": settings.model_name,
            "dry_run": settings.dry_run,
            "read_only": settings.read_only,
            "api_host": settings.api_host,
            "api_port": settings.api_port,
        }
        logger.info("cli_info", **payload)
        if args.json:
            print(json.dumps(payload, indent=2, default=str))
        else:
            for key, value in payload.items():
                print(f"{key}={value}")
        return 0

    if args.command == "list-scenarios":
        from incident_commander.fixtures import list_scenario_ids

        for scenario_id in list_scenario_ids():
            print(scenario_id)
        return 0

    if args.command == "show-scenario":
        from incident_commander.fixtures import load_scenario

        bundle = load_scenario(args.scenario_id)
        payload = {
            "scenario_id": bundle.scenario_id,
            "name": bundle.name,
            "description": bundle.description,
            "incident_id": bundle.incident.incident_id,
            "severity": bundle.incident.severity,
            "affected_services": bundle.incident.affected_services,
            "expected_root_cause": bundle.expected_root_cause,
            "expected_evidence_ids": bundle.expected_evidence_ids,
            "safe_actions": [action.action_id for action in bundle.safe_remediation_options],
            "unsafe_actions": [
                action.action_id for action in bundle.unsafe_remediation_options
            ],
            "seed_evidence_count": len(bundle.seed_evidence),
        }
        if args.json:
            print(json.dumps(payload, indent=2, default=str))
        else:
            for key, value in payload.items():
                print(f"{key}={value}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
