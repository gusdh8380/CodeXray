from __future__ import annotations

from dataclasses import dataclass

from ..entrypoints.types import EntrypointResult
from ..graph.types import Graph
from ..hotspots.types import HotspotsReport
from ..inventory import Row
from ..metrics.types import MetricsResult
from ..quality.types import QualityReport


@dataclass(frozen=True, slots=True)
class DashboardData:
    path: str
    generated_date: str
    inventory: tuple[Row, ...]
    graph: Graph
    metrics: MetricsResult
    entrypoints: EntrypointResult
    quality: QualityReport
    hotspots: HotspotsReport
