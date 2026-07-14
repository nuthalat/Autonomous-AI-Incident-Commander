"""Tool registry metadata for the Source Control MCP server."""

from __future__ import annotations

from typing import Final, TypedDict


class ServerMetadata(TypedDict):
    name: str
    version: str
    description: str
    read_only: bool


SERVER_METADATA: Final[ServerMetadata] = {
    "name": "source_control",
    "version": "0.1.0",
    "description": (
        "Search code, commits, diffs, and pull requests. Local mock repository "
        "first; GitHub-compatible interface for a future adapter."
    ),
    "read_only": True,
}

TOOL_NAMES: Final[tuple[str, ...]] = (
    "search_code",
    "get_file",
    "get_commit",
    "get_commit_diff",
    "get_pull_request",
    "list_recent_changes",
)
