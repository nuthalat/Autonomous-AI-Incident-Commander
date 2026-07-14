# Threat Model (Stage 1 Draft)

## Assets

- Production-like credentials in environment configuration
- Approval tokens authorizing write/destructive MCP tools
- Incident evidence that may contain PII or secrets
- Model prompts that include retrieved documents

## Adversaries / misuse cases

1. Prompt injection via logs, runbooks, or tickets instructing the agent to
   bypass approval.
2. Unauthorized rollback or follow-up task creation.
3. Secret leakage through logs or exported reports.
4. Cost / recursion abuse through unbounded investigation loops.

## Stage 1 controls already in place

- Read-only and dry-run defaults in settings
- No write MCP tool execution paths yet
- Anthropic provider fails closed without an explicit transport
- Structured logging (no secret printing helpers)
- Domain `ApprovalDeniedError` reserved for later gating

## Controls planned for later stages

- Per-agent tool allowlists
- Approval token issuance with TTL
- Prompt-injection filtering for retrieved content
- Evidence citation requirements
- Cost budget and recursion limits enforced in the graph
- Audit logging for approvals and write tools
