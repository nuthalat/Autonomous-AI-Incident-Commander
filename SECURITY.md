# Security Policy

## Supported versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

If you discover a security issue, please report it privately.

**Do not** open a public GitHub issue for vulnerabilities.

Email: tejasvinuthalapati@gmail.com

Include:

1. Description of the issue and impact
2. Steps to reproduce
3. Affected versions or commit SHA
4. Any proof-of-concept (non-destructive)

We aim to acknowledge reports within 5 business days and provide a remediation
timeline after triage.

## Safety model (product)

This project is designed so that:

- Read-only mode is the default.
- Destructive or write tools require a valid, unexpired human approval token.
- Retrieved documents are treated as untrusted data, not instructions.
- Secrets and PII should be redacted before logging or model prompts.
- Audit logs record approval and write-tool usage.

If you believe an agent path can bypass approval or execute writes without a
token, treat that as a vulnerability and report it using the process above.
