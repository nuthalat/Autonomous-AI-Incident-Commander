"""Local MCP server packages for the Incident Commander platform."""

from __future__ import annotations

__all__ = ["SERVER_PACKAGES"]

SERVER_PACKAGES: tuple[str, ...] = (
    "observability_mcp",
    "deployment_mcp",
    "knowledge_mcp",
    "source_control_mcp",
    "incident_management_mcp",
)
