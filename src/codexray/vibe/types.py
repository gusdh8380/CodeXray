from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VibeEvidence:
    area: str
    path: str
    kind: str
    detail: str


@dataclass(frozen=True, slots=True)
class VibeFinding:
    category: str
    text: str
    evidence_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VibeCodingReport:
    schema_version: int
    confidence: str
    confidence_score: int
    process_areas: tuple[str, ...]
    evidence: tuple[VibeEvidence, ...]
    strengths: tuple[VibeFinding, ...]
    risks: tuple[VibeFinding, ...]
    actions: tuple[VibeFinding, ...]
