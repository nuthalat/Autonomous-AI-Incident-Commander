"""Tool registry metadata for the Incident Management MCP server."""

from __future__ import annotations

from typing import Final, TypedDict


class ServerMetadata(TypedDict):
    name: str
    version: str
    description: str
    read_only: bool


SERVER_METADATA: Final[ServerMetadata] = {
    "name": "incident_management",
    "version": "0.1.0",
    "description": (
        "Historical incidents, status updates, follow-up tasks, and human "
        "approval requests. Write tools support dry-run mode."
    ),
    "read_only": False,
}

TOOL_NAMES: Final[tuple[str, ...]] = (
    "search_historical_incidents",
    "get_incident",
    "create_incident",
    "create_followup_task",
    "post_status_update",
    "request_human_approval",
)

WRITE_TOOLS: Final[tuple[str, ...]] = (
    "create_incident",
    "create_followup_task",
    "post_status_update",
    "request_human_approval",
)
