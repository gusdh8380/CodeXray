from __future__ import annotations

from collections import defaultdict
from pathlib import PurePosixPath

from ..graph.types import Graph
from .scoring import score_to_grade
from .types import DimensionScore


def _group(path: str) -> str:
    parts = PurePosixPath(path).parts[:-1]
    if not parts:
        return "(root)"
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]}/{parts[1]}"


def compute(graph: Graph) -> DimensionScore:
    if not graph.nodes:
        return DimensionScore(
            score=None, grade=None, detail={"reason": "no nodes in graph"}
        )
    internal_edges = [e for e in graph.edges if e.kind == "internal"]
    if not internal_edges:
        return DimensionScore(
            score=None, grade=None, detail={"reason": "no internal edges"}
        )

    file_to_group: dict[str, str] = {n.path: _group(n.path) for n in graph.nodes}

    group_files: dict[str, set[str]] = defaultdict(set)
    for path, group in file_to_group.items():
        group_files[group].add(path)

    group_total: dict[str, int] = defaultdict(int)
    group_internal: dict[str, int] = defaultdict(int)
    for edge in internal_edges:
        from_group = file_to_group.get(edge.from_)
        to_group = file_to_group.get(edge.to)
        if from_group is None:
            continue
        group_total[from_group] += 1
        if to_group == from_group:
            group_internal[from_group] += 1

    weighted_sum = 0.0
    weight_total = 0
    groups_evaluated = 0
    for group, files in group_files.items():
        total = group_total.get(group, 0)
        if total == 0:
            continue  # Group has no outgoing edges → skip in cohesion
        ratio = group_internal.get(group, 0) / total
        weight = len(files)
        weighted_sum += ratio * weight
        weight_total += weight
        groups_evaluated += 1

    if weight_total == 0:
        return DimensionScore(
            score=None,
            grade=None,
            detail={"reason": "no group with outgoing internal edges"},
        )

    score = round((weighted_sum / weight_total) * 100)
    return DimensionScore(
        score=score,
        grade=score_to_grade(score),
        detail={"groups_evaluated": groups_evaluated},
    )
