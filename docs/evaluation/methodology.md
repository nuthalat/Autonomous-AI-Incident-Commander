# Evaluation Methodology

Stage 1 establishes the metric list and package boundary. The runner and
baseline comparison (single-agent vs multi-agent vs multi-agent with skeptic)
are implemented once investigation agents and synthetic scenarios exist.

## Metrics

- Root-cause identification accuracy
- Evidence precision / recall
- Unsupported-claim rate
- Hypothesis ranking quality
- Remediation safety
- Refusal correctness
- Approval-policy compliance
- Investigation latency
- Token usage and estimated cost
- Tool-call count

## Rules

- Do not fabricate evaluation numbers.
- Produce results only from deterministic sample scenarios.
- Keep the fake model as the default provider for offline baselines.
