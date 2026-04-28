from __future__ import annotations

import statistics
import sys
from pathlib import Path

from ..graph import build_graph
from ..metrics import build_metrics
from .git_log import change_counts, is_git_repo
from .types import FileHotspot, HotspotsReport, Summary, Thresholds

SCHEMA_VERSION = 1


def build_hotspots(root: Path) -> HotspotsReport:
    root = root.resolve()
    graph = build_graph(root)
    metrics = build_metrics(graph)

    coupling_by_path: dict[str, int] = {
        n.path: n.fan_in + n.fan_out + n.external_fan_out for n in metrics.nodes
    }
    paths = sorted(coupling_by_path.keys())

    git_available = is_git_repo(root)
    if git_available:
        counts = change_counts(root, paths)
    else:
        print(
            "warning: not a git repository, change frequency unavailable",
            file=sys.stderr,
        )
        counts = {}

    coupling_values = [coupling_by_path[p] for p in paths]
    change_values = (
        [counts.get(p, 0) for p in paths] if git_available else [0 for _ in paths]
    )

    coupling_median = int(statistics.median(coupling_values)) if coupling_values else 0
    change_median = (
        int(statistics.median(change_values)) if change_values and git_available else 0
    )

    files: list[FileHotspot] = []
    summary_counts = {
        "hotspot": 0,
        "active_stable": 0,
        "neglected_complex": 0,
        "stable": 0,
    }
    for path in paths:
        coupling = coupling_by_path[path]
        change = counts.get(path, 0)
        category = _classify(
            change=change,
            coupling=coupling,
            change_median=change_median,
            coupling_median=coupling_median,
            git_available=git_available,
        )
        summary_counts[category] += 1
        files.append(
            FileHotspot(
                path=path,
                change_count=change,
                coupling=coupling,
                category=category,
            )
        )

    return HotspotsReport(
        schema_version=SCHEMA_VERSION,
        thresholds=Thresholds(
            change_count_median=change_median,
            coupling_median=coupling_median,
        ),
        summary=Summary(**summary_counts),
        files=tuple(files),
    )


def _classify(
    *,
    change: int,
    coupling: int,
    change_median: int,
    coupling_median: int,
    git_available: bool,
) -> str:
    high_coupling = coupling >= coupling_median
    if not git_available:
        return "hotspot" if high_coupling else "stable"

    high_change = change >= change_median
    if high_change and high_coupling:
        return "hotspot"
    if high_change and not high_coupling:
        return "active_stable"
    if not high_change and high_coupling:
        return "neglected_complex"
    return "stable"
