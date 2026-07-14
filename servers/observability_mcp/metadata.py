"""Tool registry metadata for the Observability MCP server."""

from __future__ import annotations

from typing import Final, TypedDict


class ServerMetadata(TypedDict):
    name: str
    version: str
    description: str
    read_only: bool


SERVER_METADATA: Final[ServerMetadata] = {
    "name": "observability",
    "version": "0.1.0",
    "description": "Query metrics, logs, and distributed traces for incident investigation.",
    "read_only": True,
}

TOOL_NAMES: Final[tuple[str, ...]] = (
    "query_metric",
    "compare_metric_windows",
    "detect_metric_anomaly",
    "search_logs",
    "cluster_log_errors",
    "get_log_context",
    "search_traces",
    "get_trace",
    "find_trace_critical_path",
)
