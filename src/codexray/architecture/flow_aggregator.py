"""Aggregate file-level edges into module-to-module flow counts."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def aggregate_module_flows(
    node_module: dict[str, str],
    edges: Iterable[tuple[str, str]],
) -> list[dict[str, object]]:
    """Return list of {from, to, count} for module-to-module dependency edges.

    Self-loops (within same module) are excluded from the result. Caller can
    sum the counts of edges where ``from == to`` if needed for cohesion stats.
    """
    flows: dict[tuple[str, str], int] = defaultdict(int)
    for src, dst in edges:
        if src not in node_module or dst not in node_module:
            continue
        a = node_module[src]
        b = node_module[dst]
        if a == b:
            continue
        flows[(a, b)] += 1
    return [
        {"from": a, "to": b, "count": count}
        for (a, b), count in sorted(flows.items(), key=lambda kv: -kv[1])
    ]
