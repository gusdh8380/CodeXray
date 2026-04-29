"""Build the architecture view JSON consumed by the SPA's GraphTab."""

from __future__ import annotations

from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from ..graph import build_graph
from ..hotspots import build_hotspots
from ..metrics import build_metrics
from .flow_aggregator import aggregate_module_flows
from .layer_assigner import assign_layers
from .module_detector import assign_module_colors, detect_module


SCHEMA_VERSION = 1


def build_architecture_view(root: Path) -> dict[str, Any]:
    graph = build_graph(root)
    metrics = build_metrics(graph)
    hotspots = build_hotspots(root)

    coupling_by_path = {
        n.path: n.fan_in + n.fan_out + n.external_fan_out for n in metrics.nodes
    }
    fan_by_path = {n.path: (n.fan_in, n.fan_out, n.external_fan_out) for n in metrics.nodes}
    category_by_path = {f.path: f.category for f in hotspots.files}

    paths = [n.path for n in graph.nodes]
    internal_edges = [(e.from_, e.to) for e in graph.edges if e.kind == "internal"]
    layers = assign_layers(paths, internal_edges)
    node_module = {p: detect_module(p) for p in paths}

    module_counter = Counter(node_module.values())
    color_map = assign_module_colors(list(module_counter.keys()))

    nodes = []
    for n in graph.nodes:
        coupling = coupling_by_path.get(n.path, 0)
        fan_in, fan_out, ext = fan_by_path.get(n.path, (0, 0, 0))
        nodes.append(
            {
                "path": n.path,
                "label": _short_label(n.path),
                "module": node_module[n.path],
                "layer": layers.get(n.path, 0),
                "language": n.language,
                "coupling": coupling,
                "fan_in": fan_in,
                "fan_out": fan_out,
                "external_fan_out": ext,
                "category": category_by_path.get(n.path, "stable"),
            }
        )

    edges = [
        {"from": e.from_, "to": e.to}
        for e in graph.edges
        if e.kind == "internal" and e.from_ != e.to
    ]

    modules = [
        {"name": name, "color": color_map[name], "node_count": count}
        for name, count in sorted(module_counter.items(), key=lambda kv: -kv[1])
    ]

    module_flows = aggregate_module_flows(node_module, internal_edges)

    layer_count = max(layers.values(), default=0) + 1

    return {
        "schema_version": SCHEMA_VERSION,
        "nodes": nodes,
        "edges": edges,
        "modules": modules,
        "module_flows": module_flows,
        "layer_count": layer_count,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "module_count": len(modules),
            "is_dag": metrics.graph.is_dag,
            "largest_scc": metrics.graph.largest_scc_size,
        },
    }


def _short_label(path: str) -> str:
    parts = PurePosixPath(path).parts
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return parts[-1] if parts else path
