"""Contract checks for MCP server tool registries."""

from __future__ import annotations

from servers.deployment_mcp.metadata import (
    TOOL_NAMES as DEPLOYMENT_TOOLS,
)
from servers.deployment_mcp.metadata import (
    WRITE_TOOLS_REQUIRING_APPROVAL,
)
from servers.incident_management_mcp.metadata import TOOL_NAMES as INCIDENT_TOOLS
from servers.incident_management_mcp.metadata import WRITE_TOOLS
from servers.knowledge_mcp.metadata import TOOL_NAMES as KNOWLEDGE_TOOLS
from servers.observability_mcp.metadata import TOOL_NAMES as OBS_TOOLS
from servers.source_control_mcp.metadata import TOOL_NAMES as SOURCE_TOOLS


def test_observability_exposes_required_tools() -> None:
    required = {
        "query_metric",
        "search_logs",
        "get_trace",
        "find_trace_critical_path",
    }
    assert required.issubset(set(OBS_TOOLS))


def test_rollback_requires_approval_listing() -> None:
    assert "execute_approved_rollback" in DEPLOYMENT_TOOLS
    assert "execute_approved_rollback" in WRITE_TOOLS_REQUIRING_APPROVAL


def test_incident_write_tools_are_listed() -> None:
    assert set(WRITE_TOOLS).issubset(set(INCIDENT_TOOLS))


def test_knowledge_and_source_control_tool_counts() -> None:
    assert len(KNOWLEDGE_TOOLS) >= 4
    assert len(SOURCE_TOOLS) >= 6
