"""Tool registry metadata for the Engineering Knowledge MCP server."""

from __future__ import annotations

from typing import Final, TypedDict


class ServerMetadata(TypedDict):
    name: str
    version: str
    description: str
    read_only: bool


SERVER_METADATA: Final[ServerMetadata] = {
    "name": "knowledge",
    "version": "0.1.0",
    "description": (
        "Service topology, ownership, architecture documents, runbooks, "
        "and operational policies."
    ),
    "read_only": True,
}

TOOL_NAMES: Final[tuple[str, ...]] = (
    "get_service_topology",
    "get_service_owner",
    "search_runbooks",
    "search_architecture_docs",
)

RESOURCE_TYPES: Final[tuple[str, ...]] = (
    "service_topology",
    "service_ownership",
    "architecture_document",
    "runbook",
    "operational_policy",
)
