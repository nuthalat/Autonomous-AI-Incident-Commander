# Portability Guide

This project is designed so the **agentic control plane** (typed state, workflow,
safety gates, evaluation) can move to another environment without rewriting the
orchestration core. What changes is the **data plane**: models, MCP adapters,
fixtures/topology, and environment settings.

## Two portability modes

### A. Same problem, different stack (recommended first)

Keep incident-response semantics. Swap integrations for your org:

- Datadog / Prometheus / CloudWatch instead of fixture metrics
- Your deploy system instead of mock deployments
- GitHub / GitLab instead of the local mock repo
- PagerDuty / Jira / ServiceNow instead of mock incident management

### B. Different problem, same agent pattern

Reuse the skeleton for another agentic workflow (for example change review,
capacity planning, or security triage):

- Keep: settings DI, `ModelClient`, reducers, approval gates, report fact/inference split
- Replace: domain models, agent registry, MCP tool catalogs, fixtures, evaluation labels

## What stays portable

| Layer | Location | Why it ports |
| --- | --- | --- |
| Typed settings | `src/incident_commander/config.py` | Env-driven; no hardcoded vendor URLs |
| Model interface | `src/incident_commander/services/llm/` | Swap providers via factory |
| Domain state | `src/incident_commander/domain/` | Vendor-agnostic incident semantics |
| Phase / approval gates | `src/incident_commander/domain/transitions.py` | Safety rules independent of tools |
| Evidence reducers | `src/incident_commander/domain/reducers.py` | Parallel aggregation pattern |
| App DI | `src/incident_commander/main.py`, `api/deps.py` | Inject adapters; avoid globals |
| MCP tool *contracts* | `servers/*/metadata.py` | Stable tool names; swappable backends |
| Scenario schema | `src/incident_commander/fixtures/schema.py` | Validate any environment pack |

## What you change (and where)

### 1. Runtime / environment knobs

**Files:** `.env`, `.env.example`, `src/incident_commander/config.py`

| Concern | Setting / env var |
| --- | --- |
| App identity | `INCIDENT_COMMANDER_APP_NAME` |
| Model backend | `INCIDENT_COMMANDER_MODEL_PROVIDER` (`fake` \| `anthropic`) |
| Model id / timeouts | `INCIDENT_COMMANDER_MODEL_NAME`, `*_TIMEOUT_SECONDS`, `*_MAX_RETRIES` |
| Anthropic key / model | `ANTHROPIC_API_KEY`, `INCIDENT_COMMANDER_ANTHROPIC_MODEL` |
| Safety defaults | `INCIDENT_COMMANDER_DRY_RUN`, `INCIDENT_COMMANDER_READ_ONLY` |
| Loop / cost limits | `INCIDENT_COMMANDER_MAX_REINVESTIGATION_LOOPS`, `*_COST_BUDGET_USD` |
| Approval TTL | `INCIDENT_COMMANDER_APPROVAL_TOKEN_TTL_SECONDS` |
| Prompt-injection filter | `INCIDENT_COMMANDER_PROMPT_INJECTION_FILTER` |
| Database / Redis | `INCIDENT_COMMANDER_DATABASE_URL`, `INCIDENT_COMMANDER_REDIS_URL` |
| OTEL | `INCIDENT_COMMANDER_OTEL_*` |

Start every new environment from `.env.example`. Keep `DRY_RUN=true` and
`READ_ONLY=true` until write adapters are proven.

### 2. Model provider

**Files:**

- `src/incident_commander/services/llm/base.py` — interface
- `src/incident_commander/services/llm/fake.py` — offline default
- `src/incident_commander/services/llm/anthropic_adapter.py` — Claude boundary
- `src/incident_commander/services/llm/__init__.py` — `create_model_client()`

To add OpenAI, Gemini, or an internal gateway:

1. Implement `ModelClient.complete()` / `aclose()`
2. Register it in `create_model_client()`
3. Extend `ModelProvider` in `config.py`
4. Document the new env vars in `.env.example`

Agents should depend only on `ModelClient`, never on a vendor SDK directly.

### 3. MCP tool backends (largest portability surface)

**Contracts (keep stable if possible):** `servers/<name>_mcp/metadata.py`

**Runtime adapters (swap these):** later stages under `servers/*/`, plus typed
clients in `src/incident_commander/mcp_clients/`

| MCP server | Port to your system by implementing |
| --- | --- |
| Observability | `query_metric`, `search_logs`, `get_trace`, … against your APM/logs |
| Deployment | `list_deployments`, config/flag history, gated `execute_approved_rollback` |
| Knowledge | topology, ownership, runbooks, architecture docs |
| Source control | code/commit/PR APIs (GitHub-compatible interface preferred) |
| Incident management | ticket history, status updates, approvals, follow-ups |

Rule of thumb: **agents call tool names; adapters talk to vendors.** Do not put
Datadog/GitHub URLs inside agent prompts or graph nodes.

### 4. Service topology and synthetic (or real) fixtures

**Files:**

- Packs: `src/incident_commander/fixtures/scenarios/<scenario-id>/`
- Schema: `src/incident_commander/fixtures/schema.py`
- Loader: `src/incident_commander/fixtures/loader.py`
- Generator helper: `scripts/generate_stage2_scenarios.py`

For another microservice estate:

1. Replace `topology.json` services/dependencies
2. Replace metrics/logs/traces/deployments/config/code/runbooks/history
3. Keep `seed_evidence.json` IDs stable for evaluation, or update expected IDs
4. Validate with `load_scenario()` / CLI `show-scenario`

When moving from fixtures to live systems, keep the same evidence schema
(`Evidence`, confidence, URI, raw reference) so reports and evals still work.

### 5. Agents and workflow (when implemented)

**Files:**

- Registry: `src/incident_commander/agents/__init__.py` (`AGENT_REGISTRY`)
- Phases: `src/incident_commander/graph/__init__.py` (`WORKFLOW_PHASES`)
- Transition policy: `src/incident_commander/domain/transitions.py`
- Future agent modules under `src/incident_commander/agents/`

Porting checklist:

- Narrow each agent’s tool allowlist to the MCP tools it needs
- Keep skeptic / approval / report agents even if investigator tools change
- Do not bypass `validate_phase_transition` or `assert_can_execute_remediation`

### 6. Safety posture

**Files:** `src/incident_commander/safety/`, `domain/transitions.py`,
`domain/models/remediation.py`, deployment MCP write tools

Portable invariants (do not weaken when integrating a new system):

- Read-only / dry-run defaults
- Human approval + token for destructive writes
- Retrieved documents treated as untrusted data
- Final report distinguishes facts, inferences, uncertainty, and executed actions

### 7. API / CLI product surface

**Files:** `src/incident_commander/api/`, `src/incident_commander/cli/`,
`src/incident_commander/main.py`

Keep route shapes stable (`/api/v1/incidents/...`) when embedding in another
platform. Swap persistence behind repositories in
`src/incident_commander/persistence/` rather than changing handlers.

## Suggested adoption path

1. Run offline with `MODEL_PROVIDER=fake` and packaged scenarios
2. Point one MCP server (usually observability) at a real read-only backend
3. Add your topology + one production-like scenario pack
4. Enable Anthropic (or another provider) behind `ModelClient`
5. Wire write tools last, still behind approval tokens and dry-run

## Anti-patterns

- Hardcoding vendor credentials or project IDs in agent prompts
- Letting runbooks/tickets override safety policy via prompt injection
- Skipping approval because “the new system’s API is already gated”
- Coupling graph nodes to a specific metrics vendor SDK
