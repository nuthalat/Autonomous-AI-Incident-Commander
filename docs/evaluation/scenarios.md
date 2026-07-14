# Synthetic Incident Scenarios

Five packaged scenarios live under
`src/incident_commander/fixtures/scenarios/`.

| Scenario ID | Expected root cause theme |
| --- | --- |
| `connection-pool-exhaustion` | DB pool size reduced after deploy |
| `payment-service-timeout` | Client timeout below payment p95 |
| `feature-flag-misconfiguration` | Inventory flag enabled before client readiness |
| `queue-saturation-retry-amplification` | Zero-backoff retry storm into Redis |
| `insufficient-evidence` | Unknown — telemetry does not support a cause |

Each pack includes multipart JSON:

- incident request
- service topology
- metrics / logs / traces
- deployments / configuration / code changes
- runbooks / historical incidents
- seed evidence with stable IDs
- safe and unsafe remediation options
- expected evidence IDs for evaluation

Load with:

```bash
python -m incident_commander.cli list-scenarios
python -m incident_commander.cli show-scenario connection-pool-exhaustion --json
```
