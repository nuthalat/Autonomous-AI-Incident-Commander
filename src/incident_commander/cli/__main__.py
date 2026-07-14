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

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
