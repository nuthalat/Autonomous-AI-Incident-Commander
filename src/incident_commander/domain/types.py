"""Reusable annotated types for domain validation."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

ConfidenceScore = Annotated[
    float,
    Field(ge=0.0, le=1.0, description="Confidence in the range [0.0, 1.0]"),
]

NonEmptyStr = Annotated[str, Field(min_length=1)]
