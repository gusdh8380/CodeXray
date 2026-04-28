from __future__ import annotations

from pathlib import Path

from ..graph import build_graph
from . import cohesion, coupling, documentation
from . import test as test_dim
from .scoring import score_to_grade
from .types import DimensionScore, OverallScore, QualityReport

SCHEMA_VERSION = 1


def build_quality(root: Path) -> QualityReport:
    root = root.resolve()
    graph = build_graph(root)
    dimensions: dict[str, DimensionScore] = {
        "coupling": coupling.compute(graph),
        "cohesion": cohesion.compute(graph),
        "documentation": documentation.compute(root),
        "test": test_dim.compute(root),
    }

    measurable = [d.score for d in dimensions.values() if d.score is not None]
    if measurable:
        overall_score = round(sum(measurable) / len(measurable))
        overall = OverallScore(
            score=overall_score, grade=score_to_grade(overall_score)
        )
    else:
        overall = OverallScore(score=None, grade=None)

    return QualityReport(
        schema_version=SCHEMA_VERSION,
        overall=overall,
        dimensions=dimensions,
    )
