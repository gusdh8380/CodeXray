from __future__ import annotations

from collections import defaultdict

from ..graph.types import Graph
from .scoring import score_to_grade
from .types import DimensionScore


def compute(graph: Graph) -> DimensionScore:
    if not graph.nodes:
        return DimensionScore(
            score=None, grade=None, detail={"reason": "no nodes in graph"}
        )

    fan_in: dict[str, int] = defaultdict(int)
    fan_out: dict[str, int] = defaultdict(int)
    for edge in graph.edges:
        if edge.kind != "internal":
            continue
        fan_out[edge.from_] += 1
        fan_in[edge.to] += 1

    counts = [fan_in[n.path] + fan_out[n.path] for n in graph.nodes]
    avg = sum(counts) / len(counts)
    score_float = max(0.0, min(100.0, 100 - avg * 10))
    score = round(score_float)
    return DimensionScore(
        score=score,
        grade=score_to_grade(score),
        detail={
            "avg_fan_inout": round(avg, 2),
            "max": max(counts),
        },
    )
