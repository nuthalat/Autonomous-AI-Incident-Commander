"""Tool registry metadata for the Deployment MCP server."""

from __future__ import annotations

from typing import Final, TypedDict


class ServerMetadata(TypedDict):
    name: str
    version: str
    description: str
    read_only: bool


SERVER_METADATA: Final[ServerMetadata] = {
    "name": "deployment",
    "version": "0.1.0",
    "description": (
        "Deployment history, configuration changes, feature flags, and "
        "approval-gated rollback execution."
    ),
    "read_only": False,
}

TOOL_NAMES: Final[tuple[str, ...]] = (
    "list_deployments",
    "get_deployment",
    "get_deployment_diff",
    "list_config_changes",
    "get_feature_flag_history",
    "get_rollout_status",
    "propose_rollback",
    "execute_approved_rollback",
)

WRITE_TOOLS_REQUIRING_APPROVAL: Final[tuple[str, ...]] = (
    "execute_approved_rollback",
)
