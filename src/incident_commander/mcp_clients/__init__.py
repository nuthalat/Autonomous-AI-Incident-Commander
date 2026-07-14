"""Typed clients for MCP servers used by investigation agents.

Each client wraps a narrow tool allowlist. Concrete transports and fixture
adapters are introduced alongside the MCP servers in later stages.
"""

from __future__ import annotations

MCP_SERVER_NAMES: tuple[str, ...] = (
    "observability",
    "deployment",
    "knowledge",
    "source_control",
    "incident_management",
)

__all__ = ["MCP_SERVER_NAMES"]
