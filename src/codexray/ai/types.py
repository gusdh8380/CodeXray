from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DimensionReview:
    score: int
    evidence_lines: tuple[int, ...]
    comment: str
    suggestion: str


@dataclass(frozen=True, slots=True)
class FileReview:
    path: str
    dimensions: dict[str, DimensionReview]  # readability/design/maintainability/risk
    confidence: str  # "low" | "medium" | "high"
    limitations: str


@dataclass(frozen=True, slots=True)
class Skipped:
    path: str
    reason: str


@dataclass(frozen=True, slots=True)
class ReviewResult:
    schema_version: int
    backend: str
    files_reviewed: int
    skipped: tuple[Skipped, ...]
    reviews: tuple[FileReview, ...]
