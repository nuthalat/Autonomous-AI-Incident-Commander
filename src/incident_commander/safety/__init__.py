"""Safety controls: approval tokens, redaction, and policy enforcement.

Stage 1 defines the package and default safety posture flags consumed by
settings. Approval token issuance and write-tool gating arrive in later stages.
"""

from __future__ import annotations

DEFAULT_SAFETY_POSTURE: dict[str, bool] = {
    "read_only_default": True,
    "dry_run_default": True,
    "require_approval_for_writes": True,
    "treat_retrieved_docs_as_untrusted": True,
}

__all__ = ["DEFAULT_SAFETY_POSTURE"]
