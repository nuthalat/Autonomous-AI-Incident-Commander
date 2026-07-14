#!/usr/bin/env python3
"""Generate Stage 2 synthetic incident scenario fixture packs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "incident_commander" / "fixtures" / "scenarios"

BASE_TOPOLOGY = {
    "environment": "production",
    "services": [
        {
            "name": "frontend",
            "kind": "web",
            "owner": "storefront",
            "language": "typescript",
            "depends_on": ["checkout-api"],
        },
        {
            "name": "checkout-api",
            "kind": "service",
            "owner": "checkout",
            "language": "python",
            "depends_on": ["inventory-service", "payment-service", "postgres", "redis"],
        },
        {
            "name": "inventory-service",
            "kind": "service",
            "owner": "inventory",
            "language": "go",
            "depends_on": ["postgres", "redis"],
        },
        {
            "name": "payment-service",
            "kind": "service",
            "owner": "payments",
            "language": "java",
            "depends_on": ["postgres", "redis"],
        },
        {
            "name": "postgres",
            "kind": "datastore",
            "owner": "platform",
            "language": None,
            "depends_on": [],
        },
        {
            "name": "redis",
            "kind": "cache",
            "owner": "platform",
            "language": None,
            "depends_on": [],
        },
    ],
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def evidence(
    evidence_id: str,
    source: str,
    tool_name: str,
    finding: str,
    confidence: float,
    raw_reference_id: str,
    timestamp: str,
    services: list[str],
    query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "source": source,
        "tool_name": tool_name,
        "query_or_parameters": query or {},
        "timestamp": timestamp,
        "finding": finding,
        "confidence": confidence,
        "evidence_uri": f"fixture://evidence/{evidence_id}",
        "raw_reference_id": raw_reference_id,
        "redaction_status": "not_required",
        "related_services": services,
        "tags": [],
    }


def remediation(
    action_id: str,
    action_type: str,
    title: str,
    description: str,
    *,
    is_safe: bool,
    is_destructive: bool,
    services: list[str],
    evidence_ids: list[str],
    confidence: float = 0.7,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "action_type": action_type,
        "title": title,
        "description": description,
        "target_services": services,
        "is_destructive": is_destructive,
        "requires_approval": True,
        "is_safe": is_safe,
        "reversible": not is_destructive or action_type == "rollback",
        "confidence": confidence,
        "supporting_evidence_ids": evidence_ids,
        "risk_notes": None if is_safe else "High blast radius or irreversible side effects",
        "dry_run_supported": True,
    }


def write_scenario(scenario_id: str, parts: dict[str, Any]) -> None:
    directory = OUT / scenario_id
    mapping = {
        "manifest.json": {
            "name": parts["name"],
            "description": parts["description"],
            "expected_root_cause": parts["expected_root_cause"],
            "expected_evidence_ids": parts["expected_evidence_ids"],
            "safe_remediation_options": parts["safe_remediation_options"],
            "unsafe_remediation_options": parts["unsafe_remediation_options"],
            "evidence_required_for_evaluation": parts["evidence_required_for_evaluation"],
        },
        "incident.json": parts["incident"],
        "topology.json": parts.get("topology", BASE_TOPOLOGY),
        "metrics.json": parts["metrics"],
        "logs.json": parts["logs"],
        "traces.json": parts["traces"],
        "deployments.json": parts["deployments"],
        "configuration.json": parts["configuration"],
        "code_changes.json": parts["code_changes"],
        "runbooks.json": parts["runbooks"],
        "historical_incidents.json": parts["historical_incidents"],
        "seed_evidence.json": parts["seed_evidence"],
    }
    for filename, payload in mapping.items():
        write_json(directory / filename, payload)
    print(f"wrote {directory}")


def scenario_connection_pool() -> dict[str, Any]:
    ts = "2026-07-14T18:05:00Z"
    evidence_ids = [
        "ev-cpe-metric-pool-wait",
        "ev-cpe-log-pool-timeout",
        "ev-cpe-trace-db-wait",
        "ev-cpe-deploy-checkout",
        "ev-cpe-code-pool-size",
        "ev-cpe-runbook-pool",
        "ev-cpe-hist-similar",
    ]
    return {
        "name": "Connection-pool exhaustion after deployment",
        "description": (
            "Checkout error rate rises after checkout-api deploy that lowered DB pool size."
        ),
        "expected_root_cause": (
            "checkout-api deployment reduced PostgreSQL connection pool max from 50 to 10, "
            "causing pool wait timeouts under peak checkout traffic."
        ),
        "expected_evidence_ids": evidence_ids[:5],
        "evidence_required_for_evaluation": evidence_ids[:5],
        "incident": {
            "incident_id": "inc-cpe-001",
            "title": "Checkout errors increased after recent deployment",
            "description": (
                "Customers report checkout failures. Error rate increased immediately after "
                "the checkout-api deployment. Investigate the likely cause and recommend a "
                "safe response."
            ),
            "reported_at": "2026-07-14T18:10:00Z",
            "severity": "sev2",
            "reporter": "sre-oncall",
            "environment": "production",
            "affected_services": ["checkout-api", "frontend", "postgres"],
            "symptoms": [
                {
                    "symptom_id": "sym-cpe-1",
                    "description": "HTTP 500 rate on /checkout increased from 0.2% to 8%",
                    "service": "checkout-api",
                    "first_seen_at": "2026-07-14T18:04:00Z",
                    "confidence": 0.95,
                    "tags": ["error-rate"],
                },
                {
                    "symptom_id": "sym-cpe-2",
                    "description": "Customers see 'Unable to complete purchase' banner",
                    "service": "frontend",
                    "first_seen_at": "2026-07-14T18:06:00Z",
                    "confidence": 0.9,
                    "tags": ["customer-impact"],
                },
            ],
            "tags": ["checkout", "deployment"],
            "source": "pagerduty",
            "metadata": {"scenario": "connection-pool-exhaustion"},
        },
        "metrics": [
            {
                "metric_id": "m-cpe-error-rate",
                "name": "http_request_error_rate",
                "service": "checkout-api",
                "unit": "ratio",
                "labels": {"route": "/checkout"},
                "points": [
                    {"timestamp": "2026-07-14T17:50:00Z", "value": 0.002},
                    {"timestamp": "2026-07-14T18:00:00Z", "value": 0.003},
                    {"timestamp": "2026-07-14T18:05:00Z", "value": 0.081},
                    {"timestamp": "2026-07-14T18:10:00Z", "value": 0.079},
                ],
            },
            {
                "metric_id": "m-cpe-pool-wait",
                "name": "db_connection_pool_wait_seconds",
                "service": "checkout-api",
                "unit": "seconds",
                "labels": {"db": "postgres"},
                "points": [
                    {"timestamp": "2026-07-14T17:50:00Z", "value": 0.01},
                    {"timestamp": "2026-07-14T18:00:00Z", "value": 0.02},
                    {"timestamp": "2026-07-14T18:05:00Z", "value": 4.8},
                    {"timestamp": "2026-07-14T18:10:00Z", "value": 5.1},
                ],
            },
            {
                "metric_id": "m-cpe-pool-active",
                "name": "db_connection_pool_active",
                "service": "checkout-api",
                "unit": "count",
                "labels": {"db": "postgres"},
                "points": [
                    {"timestamp": "2026-07-14T18:00:00Z", "value": 18},
                    {"timestamp": "2026-07-14T18:05:00Z", "value": 10},
                    {"timestamp": "2026-07-14T18:10:00Z", "value": 10},
                ],
            },
        ],
        "logs": [
            {
                "log_id": "log-cpe-1",
                "timestamp": "2026-07-14T18:05:12Z",
                "service": "checkout-api",
                "level": "ERROR",
                "message": "TimeoutError: QueuePool limit of size 10 overflow 0 reached",
                "fields": {"exception": "sqlalchemy.exc.TimeoutError", "pool_size": 10},
            },
            {
                "log_id": "log-cpe-2",
                "timestamp": "2026-07-14T18:05:13Z",
                "service": "checkout-api",
                "level": "ERROR",
                "message": "checkout failed while reserving inventory",
                "fields": {"route": "/checkout", "request_id": "req-cpe-42"},
            },
            {
                "log_id": "log-cpe-3",
                "timestamp": "2026-07-14T18:02:01Z",
                "service": "checkout-api",
                "level": "INFO",
                "message": "Applied database pool settings pool_size=10 max_overflow=0",
                "fields": {"config_key": "DATABASE_POOL_SIZE"},
            },
        ],
        "traces": [
            {
                "trace_id": "tr-cpe-1001",
                "root_service": "frontend",
                "root_operation": "POST /api/checkout",
                "duration_ms": 5200,
                "status": "error",
                "spans": [
                    {
                        "span_id": "sp-1",
                        "parent_span_id": None,
                        "service": "frontend",
                        "operation": "POST /api/checkout",
                        "duration_ms": 5200,
                        "status": "error",
                        "attributes": {},
                    },
                    {
                        "span_id": "sp-2",
                        "parent_span_id": "sp-1",
                        "service": "checkout-api",
                        "operation": "CheckoutService.create_order",
                        "duration_ms": 5100,
                        "status": "error",
                        "attributes": {"error": "db_pool_timeout"},
                    },
                    {
                        "span_id": "sp-3",
                        "parent_span_id": "sp-2",
                        "service": "postgres",
                        "operation": "connection.acquire",
                        "duration_ms": 5000,
                        "status": "error",
                        "attributes": {"wait_ms": 5000, "pool_size": 10},
                    },
                ],
            }
        ],
        "deployments": [
            {
                "deployment_id": "dep-cpe-checkout-224",
                "service": "checkout-api",
                "version": "1.24.0",
                "previous_version": "1.23.2",
                "started_at": "2026-07-14T17:55:00Z",
                "completed_at": "2026-07-14T18:00:30Z",
                "status": "success",
                "commit_sha": "a11c0depool01",
                "changelog": "Tune DB pool defaults; reduce idle connections",
            }
        ],
        "configuration": [
            {
                "change_id": "cfg-cpe-pool",
                "service": "checkout-api",
                "key": "DATABASE_POOL_SIZE",
                "old_value": "50",
                "new_value": "10",
                "changed_at": "2026-07-14T17:58:00Z",
                "actor": "deploy-bot",
                "change_type": "config",
            }
        ],
        "code_changes": [
            {
                "change_id": "code-cpe-1",
                "service": "checkout-api",
                "commit_sha": "a11c0depool01",
                "title": "Reduce default SQLAlchemy pool_size to 10",
                "author": "dev@example.com",
                "committed_at": "2026-07-14T16:40:00Z",
                "files_changed": ["checkout_api/db.py", "helm/values.yaml"],
                "diff_excerpt": "- POOL_SIZE = 50\n+ POOL_SIZE = 10\n- max_overflow = 10\n+ max_overflow = 0",
                "pull_request": "PR-1842",
            }
        ],
        "runbooks": [
            {
                "runbook_id": "rb-cpe-pool",
                "title": "Checkout API database connection pool saturation",
                "service": "checkout-api",
                "summary": "Diagnose pool waits and safely restore prior pool settings or roll back.",
                "steps": [
                    "Confirm db_connection_pool_wait_seconds elevated",
                    "Compare DATABASE_POOL_SIZE with previous deployment",
                    "Prefer config rollback of pool size before full service rollback",
                    "Require approval for production config write",
                ],
                "tags": ["postgres", "connection-pool"],
            }
        ],
        "historical_incidents": [
            {
                "incident_id": "inc-hist-2025-088",
                "title": "Checkout pool exhaustion after Black Friday scale event",
                "summary": "Pool size too low for traffic; restored pool and added autoscaling alerts.",
                "root_cause": "DATABASE_POOL_SIZE too low for concurrent checkout workers",
                "services": ["checkout-api", "postgres"],
                "resolved_at": "2025-11-28T02:15:00Z",
                "similarity_notes": "Same exception signature QueuePool limit reached",
            }
        ],
        "seed_evidence": [
            evidence(
                "ev-cpe-metric-pool-wait",
                "metrics",
                "detect_metric_anomaly",
                "db_connection_pool_wait_seconds spiked from ~0.02s to ~5s after 18:00Z",
                0.93,
                "m-cpe-pool-wait",
                ts,
                ["checkout-api", "postgres"],
                {"metric": "db_connection_pool_wait_seconds"},
            ),
            evidence(
                "ev-cpe-log-pool-timeout",
                "logs",
                "cluster_log_errors",
                "Repeated QueuePool limit of size 10 overflow 0 reached errors",
                0.95,
                "log-cpe-1",
                ts,
                ["checkout-api"],
                {"query": "QueuePool limit"},
            ),
            evidence(
                "ev-cpe-trace-db-wait",
                "traces",
                "find_trace_critical_path",
                "Critical path dominated by postgres connection.acquire waits (~5000ms)",
                0.9,
                "tr-cpe-1001",
                ts,
                ["checkout-api", "postgres"],
            ),
            evidence(
                "ev-cpe-deploy-checkout",
                "deployment",
                "get_deployment",
                "checkout-api 1.24.0 deployed at 17:55Z immediately before symptom onset",
                0.88,
                "dep-cpe-checkout-224",
                "2026-07-14T18:00:30Z",
                ["checkout-api"],
            ),
            evidence(
                "ev-cpe-code-pool-size",
                "code",
                "get_commit_diff",
                "Commit a11c0depool01 reduced POOL_SIZE 50→10 and max_overflow 10→0",
                0.96,
                "code-cpe-1",
                "2026-07-14T16:40:00Z",
                ["checkout-api"],
            ),
            evidence(
                "ev-cpe-runbook-pool",
                "runbook",
                "search_runbooks",
                "Runbook recommends restoring prior pool settings with approval",
                0.8,
                "rb-cpe-pool",
                ts,
                ["checkout-api"],
            ),
            evidence(
                "ev-cpe-hist-similar",
                "historical_incident",
                "search_historical_incidents",
                "Historical incident inc-hist-2025-088 matches QueuePool signature",
                0.77,
                "inc-hist-2025-088",
                ts,
                ["checkout-api", "postgres"],
            ),
        ],
        "safe_remediation_options": [
            remediation(
                "act-cpe-restore-pool",
                "config_change",
                "Restore DATABASE_POOL_SIZE to 50",
                "Apply previous pool configuration with approval; verify wait metrics recover.",
                is_safe=True,
                is_destructive=False,
                services=["checkout-api"],
                evidence_ids=["ev-cpe-code-pool-size", "ev-cpe-metric-pool-wait"],
                confidence=0.9,
            ),
            remediation(
                "act-cpe-rollback",
                "rollback",
                "Rollback checkout-api to 1.23.2",
                "Roll back the deployment that introduced the pool change.",
                is_safe=True,
                is_destructive=True,
                services=["checkout-api"],
                evidence_ids=["ev-cpe-deploy-checkout", "ev-cpe-code-pool-size"],
                confidence=0.85,
            ),
        ],
        "unsafe_remediation_options": [
            remediation(
                "act-cpe-drop-connections",
                "restart",
                "SIGKILL all postgres backends",
                "Force-terminate database backends without drain or approval scope.",
                is_safe=False,
                is_destructive=True,
                services=["postgres"],
                evidence_ids=["ev-cpe-metric-pool-wait"],
                confidence=0.2,
            ),
            remediation(
                "act-cpe-disable-checkout",
                "mitigation",
                "Disable checkout globally via hard code push",
                "Push an unreviewed emergency commit that hard-disables purchases.",
                is_safe=False,
                is_destructive=True,
                services=["frontend", "checkout-api"],
                evidence_ids=["ev-cpe-log-pool-timeout"],
                confidence=0.15,
            ),
        ],
    }


def scenario_payment_timeout() -> dict[str, Any]:
    ts = "2026-07-14T19:20:00Z"
    evidence_ids = [
        "ev-pay-metric-latency",
        "ev-pay-log-timeout",
        "ev-pay-trace-payment",
        "ev-pay-deploy-payment",
        "ev-pay-config-timeout",
        "ev-pay-runbook",
        "ev-pay-hist",
    ]
    return {
        "name": "Payment-service timeout",
        "description": "Checkout waits on payment-service which times out after a timeout config change.",
        "expected_root_cause": (
            "payment-service client timeout was reduced to 200ms while p95 authorize latency "
            "is ~450ms, causing cascading checkout failures."
        ),
        "expected_evidence_ids": evidence_ids[:5],
        "evidence_required_for_evaluation": evidence_ids[:5],
        "incident": {
            "incident_id": "inc-pay-001",
            "title": "Checkout failing with payment timeouts",
            "description": (
                "Payment authorization timeouts increased after 19:10Z. Orders stuck in "
                "pending_payment. Investigate likely cause and recommend safe response."
            ),
            "reported_at": "2026-07-14T19:25:00Z",
            "severity": "sev1",
            "reporter": "checkout-oncall",
            "environment": "production",
            "affected_services": ["checkout-api", "payment-service", "frontend"],
            "symptoms": [
                {
                    "symptom_id": "sym-pay-1",
                    "description": "payment authorize timeout rate > 30%",
                    "service": "payment-service",
                    "first_seen_at": "2026-07-14T19:12:00Z",
                    "confidence": 0.94,
                    "tags": ["timeout"],
                }
            ],
            "tags": ["payments", "timeout"],
            "source": "api",
            "metadata": {"scenario": "payment-service-timeout"},
        },
        "metrics": [
            {
                "metric_id": "m-pay-auth-p95",
                "name": "rpc_latency_p95_ms",
                "service": "payment-service",
                "unit": "milliseconds",
                "labels": {"method": "Authorize"},
                "points": [
                    {"timestamp": "2026-07-14T19:00:00Z", "value": 420},
                    {"timestamp": "2026-07-14T19:10:00Z", "value": 440},
                    {"timestamp": "2026-07-14T19:15:00Z", "value": 455},
                    {"timestamp": "2026-07-14T19:20:00Z", "value": 460},
                ],
            },
            {
                "metric_id": "m-pay-timeout-rate",
                "name": "client_timeout_rate",
                "service": "checkout-api",
                "unit": "ratio",
                "labels": {"downstream": "payment-service"},
                "points": [
                    {"timestamp": "2026-07-14T19:00:00Z", "value": 0.01},
                    {"timestamp": "2026-07-14T19:10:00Z", "value": 0.04},
                    {"timestamp": "2026-07-14T19:15:00Z", "value": 0.33},
                    {"timestamp": "2026-07-14T19:20:00Z", "value": 0.36},
                ],
            },
        ],
        "logs": [
            {
                "log_id": "log-pay-1",
                "timestamp": "2026-07-14T19:15:10Z",
                "service": "checkout-api",
                "level": "ERROR",
                "message": "payment-service Authorize deadline exceeded after 200ms",
                "fields": {"timeout_ms": 200, "downstream": "payment-service"},
            },
            {
                "log_id": "log-pay-2",
                "timestamp": "2026-07-14T19:11:00Z",
                "service": "payment-service",
                "level": "INFO",
                "message": "Loaded PAYMENT_CLIENT_TIMEOUT_MS=200",
                "fields": {"config_key": "PAYMENT_CLIENT_TIMEOUT_MS"},
            },
        ],
        "traces": [
            {
                "trace_id": "tr-pay-77",
                "root_service": "checkout-api",
                "root_operation": "CheckoutService.pay",
                "duration_ms": 210,
                "status": "error",
                "spans": [
                    {
                        "span_id": "sp-pay-1",
                        "parent_span_id": None,
                        "service": "checkout-api",
                        "operation": "CheckoutService.pay",
                        "duration_ms": 210,
                        "status": "error",
                        "attributes": {"error": "deadline_exceeded"},
                    },
                    {
                        "span_id": "sp-pay-2",
                        "parent_span_id": "sp-pay-1",
                        "service": "payment-service",
                        "operation": "Authorize",
                        "duration_ms": 200,
                        "status": "error",
                        "attributes": {"timeout_ms": 200},
                    },
                ],
            }
        ],
        "deployments": [
            {
                "deployment_id": "dep-pay-88",
                "service": "payment-service",
                "version": "3.8.1",
                "previous_version": "3.8.0",
                "started_at": "2026-07-14T19:05:00Z",
                "completed_at": "2026-07-14T19:09:00Z",
                "status": "success",
                "commit_sha": "b22paytimeout",
                "changelog": "Tighten client timeouts for failover experiments",
            }
        ],
        "configuration": [
            {
                "change_id": "cfg-pay-timeout",
                "service": "checkout-api",
                "key": "PAYMENT_CLIENT_TIMEOUT_MS",
                "old_value": "2000",
                "new_value": "200",
                "changed_at": "2026-07-14T19:08:30Z",
                "actor": "feature-flag-sync",
                "change_type": "config",
            }
        ],
        "code_changes": [
            {
                "change_id": "code-pay-1",
                "service": "payment-service",
                "commit_sha": "b22paytimeout",
                "title": "Expose aggressive timeout defaults for checkout client",
                "author": "payments@example.com",
                "committed_at": "2026-07-14T18:40:00Z",
                "files_changed": ["clients/checkout_timeouts.yaml"],
                "diff_excerpt": "- timeout_ms: 2000\n+ timeout_ms: 200",
                "pull_request": "PR-991",
            }
        ],
        "runbooks": [
            {
                "runbook_id": "rb-pay-timeout",
                "title": "Payment authorize timeout surge",
                "service": "payment-service",
                "summary": "Compare client timeout to payment p95 latency before rollback.",
                "steps": [
                    "Check payment authorize p95",
                    "Inspect PAYMENT_CLIENT_TIMEOUT_MS",
                    "Restore timeout to previous value with approval",
                ],
                "tags": ["timeout", "payments"],
            }
        ],
        "historical_incidents": [
            {
                "incident_id": "inc-hist-2026-014",
                "title": "Checkout payment deadline too aggressive",
                "summary": "Timeout set below p95; restored to 2s.",
                "root_cause": "Client timeout below payment service latency",
                "services": ["checkout-api", "payment-service"],
                "resolved_at": "2026-03-02T11:00:00Z",
                "similarity_notes": "Same deadline exceeded error from checkout client",
            }
        ],
        "seed_evidence": [
            evidence(
                "ev-pay-metric-latency",
                "metrics",
                "query_metric",
                "payment authorize p95 remains ~450ms while timeouts surge",
                0.9,
                "m-pay-auth-p95",
                ts,
                ["payment-service"],
            ),
            evidence(
                "ev-pay-log-timeout",
                "logs",
                "search_logs",
                "checkout-api logs deadline exceeded after 200ms",
                0.94,
                "log-pay-1",
                ts,
                ["checkout-api", "payment-service"],
            ),
            evidence(
                "ev-pay-trace-payment",
                "traces",
                "get_trace",
                "Trace ends at payment Authorize with timeout_ms=200",
                0.91,
                "tr-pay-77",
                ts,
                ["checkout-api", "payment-service"],
            ),
            evidence(
                "ev-pay-deploy-payment",
                "deployment",
                "list_deployments",
                "payment-service 3.8.1 deployed minutes before timeout surge",
                0.84,
                "dep-pay-88",
                "2026-07-14T19:09:00Z",
                ["payment-service"],
            ),
            evidence(
                "ev-pay-config-timeout",
                "configuration",
                "list_config_changes",
                "PAYMENT_CLIENT_TIMEOUT_MS changed 2000→200",
                0.97,
                "cfg-pay-timeout",
                "2026-07-14T19:08:30Z",
                ["checkout-api"],
            ),
            evidence(
                "ev-pay-runbook",
                "runbook",
                "search_runbooks",
                "Runbook says restore timeout when below p95 latency",
                0.8,
                "rb-pay-timeout",
                ts,
                ["payment-service"],
            ),
            evidence(
                "ev-pay-hist",
                "historical_incident",
                "get_incident",
                "Prior incident restored timeout from aggressive value",
                0.75,
                "inc-hist-2026-014",
                ts,
                ["checkout-api", "payment-service"],
            ),
        ],
        "safe_remediation_options": [
            remediation(
                "act-pay-restore-timeout",
                "config_change",
                "Restore PAYMENT_CLIENT_TIMEOUT_MS to 2000",
                "Revert timeout config with approval and monitor timeout rate.",
                is_safe=True,
                is_destructive=False,
                services=["checkout-api"],
                evidence_ids=["ev-pay-config-timeout", "ev-pay-metric-latency"],
                confidence=0.92,
            )
        ],
        "unsafe_remediation_options": [
            remediation(
                "act-pay-skip-auth",
                "mitigation",
                "Skip payment authorization entirely",
                "Bypass payment auth to clear checkout queue without fraud controls.",
                is_safe=False,
                is_destructive=True,
                services=["checkout-api", "payment-service"],
                evidence_ids=["ev-pay-log-timeout"],
                confidence=0.1,
            )
        ],
    }


def scenario_feature_flag() -> dict[str, Any]:
    ts = "2026-07-14T15:40:00Z"
    evidence_ids = [
        "ev-ff-metric-inventory",
        "ev-ff-log-flag",
        "ev-ff-trace-inventory",
        "ev-ff-flag-history",
        "ev-ff-code-path",
        "ev-ff-runbook",
        "ev-ff-hist",
    ]
    return {
        "name": "Feature-flag configuration error",
        "description": "Inventory reservation fails after misconfigured feature flag rollout.",
        "expected_root_cause": (
            "Feature flag inventory.use_new_reservation_path enabled at 100% for production "
            "while the new path rejects reservations missing warehouse_id."
        ),
        "expected_evidence_ids": evidence_ids[:5],
        "evidence_required_for_evaluation": evidence_ids[:5],
        "incident": {
            "incident_id": "inc-ff-001",
            "title": "Inventory reservation failures after flag change",
            "description": (
                "Checkout cannot reserve inventory. Flag change occurred at 15:30Z. "
                "Investigate and recommend safe response."
            ),
            "reported_at": "2026-07-14T15:45:00Z",
            "severity": "sev2",
            "reporter": "inventory-oncall",
            "environment": "production",
            "affected_services": ["inventory-service", "checkout-api", "frontend"],
            "symptoms": [
                {
                    "symptom_id": "sym-ff-1",
                    "description": "inventory reserve error rate 40%",
                    "service": "inventory-service",
                    "first_seen_at": "2026-07-14T15:31:00Z",
                    "confidence": 0.93,
                    "tags": ["feature-flag"],
                }
            ],
            "tags": ["feature-flag", "inventory"],
            "source": "slack",
            "metadata": {"scenario": "feature-flag-misconfiguration"},
        },
        "metrics": [
            {
                "metric_id": "m-ff-reserve-errors",
                "name": "rpc_error_rate",
                "service": "inventory-service",
                "unit": "ratio",
                "labels": {"method": "Reserve"},
                "points": [
                    {"timestamp": "2026-07-14T15:20:00Z", "value": 0.01},
                    {"timestamp": "2026-07-14T15:30:00Z", "value": 0.02},
                    {"timestamp": "2026-07-14T15:35:00Z", "value": 0.41},
                    {"timestamp": "2026-07-14T15:40:00Z", "value": 0.39},
                ],
            }
        ],
        "logs": [
            {
                "log_id": "log-ff-1",
                "timestamp": "2026-07-14T15:32:00Z",
                "service": "inventory-service",
                "level": "ERROR",
                "message": "ReservationRejected: warehouse_id required when new path enabled",
                "fields": {
                    "flag": "inventory.use_new_reservation_path",
                    "flag_value": "true",
                },
            },
            {
                "log_id": "log-ff-2",
                "timestamp": "2026-07-14T15:30:05Z",
                "service": "inventory-service",
                "level": "INFO",
                "message": "Feature flag inventory.use_new_reservation_path=100%",
                "fields": {"flag": "inventory.use_new_reservation_path", "rollout": "100"},
            },
        ],
        "traces": [
            {
                "trace_id": "tr-ff-12",
                "root_service": "checkout-api",
                "root_operation": "reserve_inventory",
                "duration_ms": 35,
                "status": "error",
                "spans": [
                    {
                        "span_id": "sp-ff-1",
                        "parent_span_id": None,
                        "service": "checkout-api",
                        "operation": "reserve_inventory",
                        "duration_ms": 35,
                        "status": "error",
                        "attributes": {},
                    },
                    {
                        "span_id": "sp-ff-2",
                        "parent_span_id": "sp-ff-1",
                        "service": "inventory-service",
                        "operation": "Reserve",
                        "duration_ms": 20,
                        "status": "error",
                        "attributes": {"error.type": "ReservationRejected"},
                    },
                ],
            }
        ],
        "deployments": [
            {
                "deployment_id": "dep-ff-inv-55",
                "service": "inventory-service",
                "version": "2.12.0",
                "previous_version": "2.11.4",
                "started_at": "2026-07-13T20:00:00Z",
                "completed_at": "2026-07-13T20:10:00Z",
                "status": "success",
                "commit_sha": "c33flagpath",
                "changelog": "Add new reservation path behind feature flag",
            }
        ],
        "configuration": [
            {
                "change_id": "cfg-ff-1",
                "service": "inventory-service",
                "key": "inventory.use_new_reservation_path",
                "old_value": "10%",
                "new_value": "100%",
                "changed_at": "2026-07-14T15:30:00Z",
                "actor": "flag-console",
                "change_type": "feature_flag",
            }
        ],
        "code_changes": [
            {
                "change_id": "code-ff-1",
                "service": "inventory-service",
                "commit_sha": "c33flagpath",
                "title": "New reservation path requires warehouse_id",
                "author": "inventory@example.com",
                "committed_at": "2026-07-13T18:00:00Z",
                "files_changed": ["reservation/new_path.go"],
                "diff_excerpt": "+ if flag && warehouseID == \"\" { return ErrWarehouseRequired }",
                "pull_request": "PR-450",
            }
        ],
        "runbooks": [
            {
                "runbook_id": "rb-ff-1",
                "title": "Disable inventory feature flag safely",
                "service": "inventory-service",
                "summary": "Roll flag back to previous percentage with approval.",
                "steps": [
                    "Confirm error mentions warehouse_id",
                    "Check feature flag history",
                    "Reduce rollout to 0% or previous stage",
                ],
                "tags": ["feature-flag"],
            }
        ],
        "historical_incidents": [
            {
                "incident_id": "inc-hist-2026-041",
                "title": "Partial inventory flag rollout caused reserve errors",
                "summary": "Flag enabled before clients sent warehouse_id.",
                "root_cause": "Feature flag enabled without client contract readiness",
                "services": ["inventory-service", "checkout-api"],
                "resolved_at": "2026-05-10T09:30:00Z",
                "similarity_notes": "Same ReservationRejected warehouse_id message",
            }
        ],
        "seed_evidence": [
            evidence(
                "ev-ff-metric-inventory",
                "metrics",
                "detect_metric_anomaly",
                "inventory Reserve error rate jumped to ~40% at 15:35Z",
                0.92,
                "m-ff-reserve-errors",
                ts,
                ["inventory-service"],
            ),
            evidence(
                "ev-ff-log-flag",
                "logs",
                "search_logs",
                "Errors require warehouse_id when new reservation path enabled",
                0.95,
                "log-ff-1",
                ts,
                ["inventory-service"],
            ),
            evidence(
                "ev-ff-trace-inventory",
                "traces",
                "search_traces",
                "checkout→inventory Reserve spans fail with ReservationRejected",
                0.88,
                "tr-ff-12",
                ts,
                ["checkout-api", "inventory-service"],
            ),
            evidence(
                "ev-ff-flag-history",
                "configuration",
                "get_feature_flag_history",
                "Flag inventory.use_new_reservation_path rolled 10%→100% at 15:30Z",
                0.97,
                "cfg-ff-1",
                "2026-07-14T15:30:00Z",
                ["inventory-service"],
            ),
            evidence(
                "ev-ff-code-path",
                "code",
                "search_code",
                "New path rejects missing warehouse_id when flag enabled",
                0.9,
                "code-ff-1",
                "2026-07-13T18:00:00Z",
                ["inventory-service"],
            ),
            evidence(
                "ev-ff-runbook",
                "runbook",
                "search_runbooks",
                "Runbook advises rolling flag back with approval",
                0.8,
                "rb-ff-1",
                ts,
                ["inventory-service"],
            ),
            evidence(
                "ev-ff-hist",
                "historical_incident",
                "search_historical_incidents",
                "Similar prior flag incident resolved by disabling flag",
                0.78,
                "inc-hist-2026-041",
                ts,
                ["inventory-service"],
            ),
        ],
        "safe_remediation_options": [
            remediation(
                "act-ff-disable-flag",
                "feature_flag",
                "Roll back inventory.use_new_reservation_path to 0%",
                "Disable the flag with approval; keep service version unchanged.",
                is_safe=True,
                is_destructive=False,
                services=["inventory-service"],
                evidence_ids=["ev-ff-flag-history", "ev-ff-log-flag"],
                confidence=0.93,
            )
        ],
        "unsafe_remediation_options": [
            remediation(
                "act-ff-force-default-warehouse",
                "config_change",
                "Hardcode warehouse_id=1 for all reservations",
                "Silently assign a default warehouse, risking incorrect stock mutation.",
                is_safe=False,
                is_destructive=True,
                services=["inventory-service"],
                evidence_ids=["ev-ff-code-path"],
                confidence=0.2,
            )
        ],
    }


def scenario_queue_saturation() -> dict[str, Any]:
    ts = "2026-07-14T21:10:00Z"
    evidence_ids = [
        "ev-q-metric-depth",
        "ev-q-metric-retries",
        "ev-q-log-retry",
        "ev-q-trace-amplification",
        "ev-q-config-retry",
        "ev-q-runbook",
        "ev-q-hist",
    ]
    return {
        "name": "Queue saturation caused by retry amplification",
        "description": "Redis-backed checkout retry queue saturates after retry policy change.",
        "expected_root_cause": (
            "checkout-api retry policy changed to 20 immediate retries with no backoff, "
            "amplifying inventory failures into Redis queue saturation."
        ),
        "expected_evidence_ids": evidence_ids[:5],
        "evidence_required_for_evaluation": evidence_ids[:5],
        "incident": {
            "incident_id": "inc-q-001",
            "title": "Checkout queue depth exploding",
            "description": (
                "Redis checkout retry queue depth exceeded 50k. Investigate amplification "
                "and recommend a safe response."
            ),
            "reported_at": "2026-07-14T21:15:00Z",
            "severity": "sev2",
            "reporter": "platform-oncall",
            "environment": "production",
            "affected_services": ["checkout-api", "inventory-service", "redis"],
            "symptoms": [
                {
                    "symptom_id": "sym-q-1",
                    "description": "redis list checkout:retries length > 50000",
                    "service": "redis",
                    "first_seen_at": "2026-07-14T21:05:00Z",
                    "confidence": 0.96,
                    "tags": ["queue"],
                }
            ],
            "tags": ["retry", "redis"],
            "source": "api",
            "metadata": {"scenario": "queue-saturation-retry-amplification"},
        },
        "metrics": [
            {
                "metric_id": "m-q-depth",
                "name": "queue_depth",
                "service": "redis",
                "unit": "count",
                "labels": {"queue": "checkout:retries"},
                "points": [
                    {"timestamp": "2026-07-14T20:50:00Z", "value": 120},
                    {"timestamp": "2026-07-14T21:00:00Z", "value": 800},
                    {"timestamp": "2026-07-14T21:05:00Z", "value": 22000},
                    {"timestamp": "2026-07-14T21:10:00Z", "value": 54000},
                ],
            },
            {
                "metric_id": "m-q-retries",
                "name": "client_retry_total",
                "service": "checkout-api",
                "unit": "count",
                "labels": {"target": "inventory-service"},
                "points": [
                    {"timestamp": "2026-07-14T20:50:00Z", "value": 40},
                    {"timestamp": "2026-07-14T21:00:00Z", "value": 900},
                    {"timestamp": "2026-07-14T21:05:00Z", "value": 18000},
                    {"timestamp": "2026-07-14T21:10:00Z", "value": 42000},
                ],
            },
        ],
        "logs": [
            {
                "log_id": "log-q-1",
                "timestamp": "2026-07-14T21:06:00Z",
                "service": "checkout-api",
                "level": "WARN",
                "message": "inventory reserve failed; enqueue retry attempt=17/20",
                "fields": {"retry_max": 20, "backoff_ms": 0},
            },
            {
                "log_id": "log-q-2",
                "timestamp": "2026-07-14T21:01:00Z",
                "service": "checkout-api",
                "level": "INFO",
                "message": "Updated retry policy max_attempts=20 backoff_ms=0",
                "fields": {"config_key": "INVENTORY_RETRY_MAX"},
            },
        ],
        "traces": [
            {
                "trace_id": "tr-q-9",
                "root_service": "checkout-api",
                "root_operation": "retry_worker",
                "duration_ms": 1800,
                "status": "error",
                "spans": [
                    {
                        "span_id": "sp-q-1",
                        "parent_span_id": None,
                        "service": "checkout-api",
                        "operation": "retry_worker",
                        "duration_ms": 1800,
                        "status": "error",
                        "attributes": {"attempts": 20},
                    },
                    {
                        "span_id": "sp-q-2",
                        "parent_span_id": "sp-q-1",
                        "service": "inventory-service",
                        "operation": "Reserve",
                        "duration_ms": 40,
                        "status": "error",
                        "attributes": {"error": "unavailable"},
                    },
                    {
                        "span_id": "sp-q-3",
                        "parent_span_id": "sp-q-1",
                        "service": "redis",
                        "operation": "LPUSH checkout:retries",
                        "duration_ms": 5,
                        "status": "ok",
                        "attributes": {"queue_depth_after": 54001},
                    },
                ],
            }
        ],
        "deployments": [
            {
                "deployment_id": "dep-q-checkout-230",
                "service": "checkout-api",
                "version": "1.25.0",
                "previous_version": "1.24.0",
                "started_at": "2026-07-14T20:55:00Z",
                "completed_at": "2026-07-14T21:00:00Z",
                "status": "success",
                "commit_sha": "d44retrybomb",
                "changelog": "Increase inventory retry aggressiveness",
            }
        ],
        "configuration": [
            {
                "change_id": "cfg-q-retry",
                "service": "checkout-api",
                "key": "INVENTORY_RETRY_MAX",
                "old_value": "3",
                "new_value": "20",
                "changed_at": "2026-07-14T20:58:00Z",
                "actor": "deploy-bot",
                "change_type": "config",
            },
            {
                "change_id": "cfg-q-backoff",
                "service": "checkout-api",
                "key": "INVENTORY_RETRY_BACKOFF_MS",
                "old_value": "250",
                "new_value": "0",
                "changed_at": "2026-07-14T20:58:00Z",
                "actor": "deploy-bot",
                "change_type": "config",
            },
        ],
        "code_changes": [
            {
                "change_id": "code-q-1",
                "service": "checkout-api",
                "commit_sha": "d44retrybomb",
                "title": "Make inventory retries more aggressive",
                "author": "checkout@example.com",
                "committed_at": "2026-07-14T19:30:00Z",
                "files_changed": ["checkout_api/retries.py"],
                "diff_excerpt": "- max_attempts = 3\n+ max_attempts = 20\n- backoff_ms = 250\n+ backoff_ms = 0",
                "pull_request": "PR-2011",
            }
        ],
        "runbooks": [
            {
                "runbook_id": "rb-q-1",
                "title": "Checkout retry queue amplification",
                "service": "checkout-api",
                "summary": "Pause retry workers, restore retry policy, drain queue safely.",
                "steps": [
                    "Confirm queue_depth and retry_total correlation",
                    "Disable retry enqueue with approval",
                    "Restore prior retry/backoff config",
                    "Drain queue in controlled batches",
                ],
                "tags": ["redis", "retries"],
            }
        ],
        "historical_incidents": [
            {
                "incident_id": "inc-hist-2024-210",
                "title": "Retry storm saturated Redis",
                "summary": "Zero-backoff retries amplified downstream blip.",
                "root_cause": "Retry amplification with no backoff",
                "services": ["checkout-api", "redis"],
                "resolved_at": "2024-12-01T04:00:00Z",
                "similarity_notes": "Same checkout:retries queue and backoff_ms=0 pattern",
            }
        ],
        "seed_evidence": [
            evidence(
                "ev-q-metric-depth",
                "metrics",
                "query_metric",
                "checkout:retries queue depth rose from hundreds to 54k",
                0.95,
                "m-q-depth",
                ts,
                ["redis"],
            ),
            evidence(
                "ev-q-metric-retries",
                "metrics",
                "compare_metric_windows",
                "client_retry_total amplified by orders of magnitude after 21:00Z",
                0.93,
                "m-q-retries",
                ts,
                ["checkout-api"],
            ),
            evidence(
                "ev-q-log-retry",
                "logs",
                "cluster_log_errors",
                "Logs show attempt=17/20 with backoff_ms=0",
                0.94,
                "log-q-1",
                ts,
                ["checkout-api"],
            ),
            evidence(
                "ev-q-trace-amplification",
                "traces",
                "get_trace",
                "retry_worker performs 20 attempts and re-enqueues to Redis",
                0.9,
                "tr-q-9",
                ts,
                ["checkout-api", "redis", "inventory-service"],
            ),
            evidence(
                "ev-q-config-retry",
                "configuration",
                "list_config_changes",
                "INVENTORY_RETRY_MAX 3→20 and backoff 250→0",
                0.97,
                "cfg-q-retry",
                "2026-07-14T20:58:00Z",
                ["checkout-api"],
            ),
            evidence(
                "ev-q-runbook",
                "runbook",
                "search_runbooks",
                "Runbook recommends pausing retries then restoring policy",
                0.82,
                "rb-q-1",
                ts,
                ["checkout-api"],
            ),
            evidence(
                "ev-q-hist",
                "historical_incident",
                "search_historical_incidents",
                "Historical retry storm matches zero-backoff pattern",
                0.8,
                "inc-hist-2024-210",
                ts,
                ["checkout-api", "redis"],
            ),
        ],
        "safe_remediation_options": [
            remediation(
                "act-q-restore-retry",
                "config_change",
                "Restore retry max=3 and backoff=250ms",
                "Revert retry amplification settings with approval.",
                is_safe=True,
                is_destructive=False,
                services=["checkout-api"],
                evidence_ids=["ev-q-config-retry", "ev-q-metric-retries"],
                confidence=0.91,
            ),
            remediation(
                "act-q-pause-workers",
                "mitigation",
                "Pause checkout retry workers",
                "Temporarily pause retry workers to stop amplification, then drain.",
                is_safe=True,
                is_destructive=False,
                services=["checkout-api", "redis"],
                evidence_ids=["ev-q-metric-depth", "ev-q-runbook"],
                confidence=0.86,
            ),
        ],
        "unsafe_remediation_options": [
            remediation(
                "act-q-flush-redis",
                "mitigation",
                "FLUSHALL Redis",
                "Wipe entire Redis instance, destroying unrelated cache and sessions.",
                is_safe=False,
                is_destructive=True,
                services=["redis"],
                evidence_ids=["ev-q-metric-depth"],
                confidence=0.05,
            )
        ],
    }


def scenario_insufficient_evidence() -> dict[str, Any]:
    ts = "2026-07-14T22:30:00Z"
    evidence_ids = [
        "ev-ie-user-report",
        "ev-ie-metric-flat",
        "ev-ie-log-sparse",
        "ev-ie-trace-missing",
        "ev-ie-deploy-none",
        "ev-ie-runbook-generic",
        "ev-ie-hist-unrelated",
    ]
    return {
        "name": "Insufficient evidence / unknown root cause",
        "description": (
            "Vague customer report with flat metrics and sparse telemetry; root cause unknown."
        ),
        "expected_root_cause": (
            "Unknown — insufficient evidence to identify a root cause with acceptable confidence."
        ),
        "expected_evidence_ids": evidence_ids[:4],
        "evidence_required_for_evaluation": evidence_ids[:4],
        "incident": {
            "incident_id": "inc-ie-001",
            "title": "Intermittent checkout confusion reported",
            "description": (
                "A single customer reported checkout 'felt slow' around 22:00Z. No pages fired. "
                "Investigate if there is a production issue."
            ),
            "reported_at": "2026-07-14T22:35:00Z",
            "severity": "sev4",
            "reporter": "support-tier1",
            "environment": "production",
            "affected_services": ["checkout-api", "frontend"],
            "symptoms": [
                {
                    "symptom_id": "sym-ie-1",
                    "description": "Single anecdotal report of slow checkout",
                    "service": "frontend",
                    "first_seen_at": "2026-07-14T22:00:00Z",
                    "confidence": 0.3,
                    "tags": ["anecdotal"],
                }
            ],
            "tags": ["insufficient-evidence"],
            "source": "support",
            "metadata": {"scenario": "insufficient-evidence"},
        },
        "metrics": [
            {
                "metric_id": "m-ie-error-rate",
                "name": "http_request_error_rate",
                "service": "checkout-api",
                "unit": "ratio",
                "labels": {"route": "/checkout"},
                "points": [
                    {"timestamp": "2026-07-14T21:50:00Z", "value": 0.002},
                    {"timestamp": "2026-07-14T22:00:00Z", "value": 0.002},
                    {"timestamp": "2026-07-14T22:10:00Z", "value": 0.003},
                    {"timestamp": "2026-07-14T22:20:00Z", "value": 0.002},
                ],
            },
            {
                "metric_id": "m-ie-latency",
                "name": "http_request_latency_p95_ms",
                "service": "checkout-api",
                "unit": "milliseconds",
                "labels": {"route": "/checkout"},
                "points": [
                    {"timestamp": "2026-07-14T21:50:00Z", "value": 220},
                    {"timestamp": "2026-07-14T22:00:00Z", "value": 230},
                    {"timestamp": "2026-07-14T22:10:00Z", "value": 225},
                    {"timestamp": "2026-07-14T22:20:00Z", "value": 228},
                ],
            },
        ],
        "logs": [
            {
                "log_id": "log-ie-1",
                "timestamp": "2026-07-14T22:05:00Z",
                "service": "checkout-api",
                "level": "INFO",
                "message": "checkout completed successfully",
                "fields": {"request_id": "req-ie-1", "duration_ms": 210},
            }
        ],
        "traces": [
            {
                "trace_id": "tr-ie-1",
                "root_service": "frontend",
                "root_operation": "POST /api/checkout",
                "duration_ms": 240,
                "status": "ok",
                "spans": [
                    {
                        "span_id": "sp-ie-1",
                        "parent_span_id": None,
                        "service": "frontend",
                        "operation": "POST /api/checkout",
                        "duration_ms": 240,
                        "status": "ok",
                        "attributes": {},
                    },
                    {
                        "span_id": "sp-ie-2",
                        "parent_span_id": "sp-ie-1",
                        "service": "checkout-api",
                        "operation": "CheckoutService.create_order",
                        "duration_ms": 180,
                        "status": "ok",
                        "attributes": {},
                    },
                ],
            }
        ],
        "deployments": [
            {
                "deployment_id": "dep-ie-stale",
                "service": "checkout-api",
                "version": "1.23.2",
                "previous_version": "1.23.1",
                "started_at": "2026-07-10T12:00:00Z",
                "completed_at": "2026-07-10T12:15:00Z",
                "status": "success",
                "commit_sha": "e55stale",
                "changelog": "Routine dependency bump four days earlier",
            }
        ],
        "configuration": [
            {
                "change_id": "cfg-ie-none",
                "service": "checkout-api",
                "key": "FEATURE_NOOP",
                "old_value": "false",
                "new_value": "false",
                "changed_at": "2026-07-01T00:00:00Z",
                "actor": "system",
                "change_type": "config",
            }
        ],
        "code_changes": [
            {
                "change_id": "code-ie-1",
                "service": "checkout-api",
                "commit_sha": "e55stale",
                "title": "Bump patch dependencies",
                "author": "deps-bot",
                "committed_at": "2026-07-10T11:00:00Z",
                "files_changed": ["requirements.txt"],
                "diff_excerpt": "- lib==1.2.3\n+ lib==1.2.4",
                "pull_request": "PR-1777",
            }
        ],
        "runbooks": [
            {
                "runbook_id": "rb-ie-generic",
                "title": "Insufficient signal triage",
                "service": "checkout-api",
                "summary": "When metrics are flat, avoid destructive changes and request more evidence.",
                "steps": [
                    "Confirm absence of metric anomalies",
                    "Ask support for reproducible request IDs",
                    "Do not roll back without evidence",
                ],
                "tags": ["triage", "insufficient-evidence"],
            }
        ],
        "historical_incidents": [
            {
                "incident_id": "inc-hist-2026-003",
                "title": "Support anecdote with no prod regression",
                "summary": "Closed as insufficient evidence after telemetry review.",
                "root_cause": "No production defect identified",
                "services": ["frontend"],
                "resolved_at": "2026-01-15T16:00:00Z",
                "similarity_notes": "Anecdotal report without metric corroboration",
            }
        ],
        "seed_evidence": [
            evidence(
                "ev-ie-user-report",
                "user_report",
                "create_incident",
                "Single anecdotal report without reproducible request IDs",
                0.35,
                "inc-ie-001",
                ts,
                ["frontend"],
            ),
            evidence(
                "ev-ie-metric-flat",
                "metrics",
                "detect_metric_anomaly",
                "No statistically significant error-rate or latency anomaly detected",
                0.7,
                "m-ie-error-rate",
                ts,
                ["checkout-api"],
            ),
            evidence(
                "ev-ie-log-sparse",
                "logs",
                "search_logs",
                "Only successful checkout info logs found near the reported window",
                0.65,
                "log-ie-1",
                ts,
                ["checkout-api"],
            ),
            evidence(
                "ev-ie-trace-missing",
                "traces",
                "search_traces",
                "Sampled traces in window completed successfully with normal latency",
                0.68,
                "tr-ie-1",
                ts,
                ["frontend", "checkout-api"],
            ),
            evidence(
                "ev-ie-deploy-none",
                "deployment",
                "list_deployments",
                "No deployments in the 24h preceding the report",
                0.8,
                "dep-ie-stale",
                "2026-07-10T12:15:00Z",
                ["checkout-api"],
            ),
            evidence(
                "ev-ie-runbook-generic",
                "runbook",
                "search_runbooks",
                "Triage runbook: avoid rollback without corroborating evidence",
                0.75,
                "rb-ie-generic",
                ts,
                ["checkout-api"],
            ),
            evidence(
                "ev-ie-hist-unrelated",
                "historical_incident",
                "search_historical_incidents",
                "Prior similar anecdote closed with no production defect",
                0.6,
                "inc-hist-2026-003",
                ts,
                ["frontend"],
            ),
        ],
        "safe_remediation_options": [
            remediation(
                "act-ie-request-evidence",
                "investigate_further",
                "Request reproducible request IDs and continue monitoring",
                "Do not mutate production; gather HAR/request IDs and watch SLOs.",
                is_safe=True,
                is_destructive=False,
                services=["checkout-api", "frontend"],
                evidence_ids=["ev-ie-metric-flat", "ev-ie-runbook-generic"],
                confidence=0.8,
            )
        ],
        "unsafe_remediation_options": [
            remediation(
                "act-ie-blind-rollback",
                "rollback",
                "Rollback checkout-api without evidence",
                "Roll back a four-day-old deployment based on anecdote alone.",
                is_safe=False,
                is_destructive=True,
                services=["checkout-api"],
                evidence_ids=["ev-ie-user-report"],
                confidence=0.1,
            )
        ],
    }


def main() -> None:
    scenarios = {
        "connection-pool-exhaustion": scenario_connection_pool(),
        "payment-service-timeout": scenario_payment_timeout(),
        "feature-flag-misconfiguration": scenario_feature_flag(),
        "queue-saturation-retry-amplification": scenario_queue_saturation(),
        "insufficient-evidence": scenario_insufficient_evidence(),
    }
    for scenario_id, parts in scenarios.items():
        write_scenario(scenario_id, parts)
    print(f"generated {len(scenarios)} scenarios under {OUT}")


if __name__ == "__main__":
    main()
