from __future__ import annotations

from dataclasses import dataclass, field

from ..entrypoints.types import EntrypointResult
from ..graph.types import Graph
from ..hotspots.types import HotspotsReport
from ..inventory import Row
from ..metrics.types import MetricsResult
from ..quality.types import QualityReport
from ..summary.types import SummaryResult


def _empty_summary() -> SummaryResult:
    return SummaryResult(
        schema_version=1,
        strengths=(),
        weaknesses=(),
        actions=(),
    )


@dataclass(frozen=True, slots=True)
class Recommendation:
    priority: int
    text: str


@dataclass(frozen=True, slots=True)
class ReportData:
    path: str
    generated_date: str
    inventory: tuple[Row, ...]
    graph: Graph
    metrics: MetricsResult
    entrypoints: EntrypointResult
    quality: QualityReport
    hotspots: HotspotsReport
    recommendations: tuple[Recommendation, ...]
    summary: SummaryResult = field(default_factory=_empty_summary)
