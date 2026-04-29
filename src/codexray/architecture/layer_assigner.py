"""Compute architectural layer for each node via topological sort.

Cycles are handled by contracting strongly connected components into a single
node, sorting the condensation, then expanding back. Files inside a cycle
share the same layer.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def assign_layers(
    node_paths: Iterable[str],
    edges: Iterable[tuple[str, str]],
) -> dict[str, int]:
    """Return {path: layer_index}. Layer 0 = entrypoint/leaf nodes.

    The convention: layer = max(layer of dependencies) + 1. Entrypoints (no
    incoming edges from internal files) AND leaves (no outgoing) both end up
    at low layers. We define layer 0 as nodes with no outgoing internal deps
    (true leaves) and propagate upward — so callers naturally end up higher
    than callees, and the visual is "uses → things below it".
    """
    nodes = list(node_paths)
    if not nodes:
        return {}

    out_adj: dict[str, set[str]] = defaultdict(set)
    in_adj: dict[str, set[str]] = defaultdict(set)
    node_set = set(nodes)
    for src, dst in edges:
        if src in node_set and dst in node_set and src != dst:
            out_adj[src].add(dst)
            in_adj[dst].add(src)

    # Tarjan SCC
    sccs = _strongly_connected(nodes, out_adj)
    node_to_scc = {node: idx for idx, comp in enumerate(sccs) for node in comp}

    # Build condensation graph
    cond_out: dict[int, set[int]] = defaultdict(set)
    cond_in: dict[int, set[int]] = defaultdict(set)
    for src, targets in out_adj.items():
        a = node_to_scc[src]
        for dst in targets:
            b = node_to_scc[dst]
            if a != b:
                cond_out[a].add(b)
                cond_in[b].add(a)

    # Layer = longest path from a leaf (no out edges in condensation)
    layer_of_scc: dict[int, int] = {}

    def compute_layer(scc_id: int, stack: set[int]) -> int:
        if scc_id in layer_of_scc:
            return layer_of_scc[scc_id]
        if scc_id in stack:
            return 0  # already in recursion (shouldn't happen post-condensation)
        stack.add(scc_id)
        outs = cond_out.get(scc_id, set())
        if not outs:
            layer = 0
        else:
            layer = 1 + max(compute_layer(target, stack) for target in outs)
        stack.discard(scc_id)
        layer_of_scc[scc_id] = layer
        return layer

    for scc_id in range(len(sccs)):
        compute_layer(scc_id, set())

    return {node: layer_of_scc[node_to_scc[node]] for node in nodes}


def _strongly_connected(
    nodes: list[str],
    out_adj: dict[str, set[str]],
) -> list[list[str]]:
    """Tarjan's SCC algorithm. Returns list of components in reverse topo order."""
    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    result: list[list[str]] = []

    def strong(v: str) -> None:
        indices[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)
        for w in out_adj.get(v, ()):
            if w not in indices:
                strong(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.append(w)
                if w == v:
                    break
            result.append(comp)

    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(nodes) * 4 + 1000))
    for node in nodes:
        if node not in indices:
            strong(node)
    return result
