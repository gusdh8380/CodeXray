from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DimensionScore:
    score: int | None
    grade: str | None
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class OverallScore:
    score: int | None
    grade: str | None


@dataclass(frozen=True, slots=True)
class QualityReport:
    schema_version: int
    overall: OverallScore
    dimensions: dict[str, DimensionScore]
