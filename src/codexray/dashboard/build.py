from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..entrypoints import build_entrypoints
from ..graph import build_graph
from ..hotspots import build_hotspots
from ..inventory import aggregate
from ..metrics import build_metrics
from ..quality import build_quality
from .types import DashboardData


def build_dashboard(root: Path) -> DashboardData:
    root = root.resolve()
    inventory_rows = aggregate(root)
    graph = build_graph(root)
    metrics = build_metrics(graph)
    entrypoints = build_entrypoints(root)
    quality = build_quality(root)
    hotspots = build_hotspots(root)
    generated_date = datetime.now().astimezone().date().isoformat()
    return DashboardData(
        path=str(root),
        generated_date=generated_date,
        inventory=tuple(inventory_rows),
        graph=graph,
        metrics=metrics,
        entrypoints=entrypoints,
        quality=quality,
        hotspots=hotspots,
    )
