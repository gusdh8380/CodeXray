from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Strength:
    category: str  # "quality" | "hotspots" | "metrics"
    text: str
    evidence: dict[str, Any]


@dataclass(frozen=True, slots=True)
class Weakness:
    category: str
    text: str
    evidence: dict[str, Any]


@dataclass(frozen=True, slots=True)
class Action:
    text: str
    evidence: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SummaryResult:
    schema_version: int
    strengths: tuple[Strength, ...]
    weaknesses: tuple[Weakness, ...]
    actions: tuple[Action, ...]
