from __future__ import annotations

from collections.abc import Mapping


def tarjan_scc(adj: Mapping[str, list[str]]) -> list[set[str]]:
    """Return strongly connected components, computed iteratively.

    ``adj`` maps each node to its neighbors. Order of node enumeration is
    fixed by sorting keys so the SCC list order is deterministic.
    """
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    on_stack: set[str] = set()
    component_stack: list[str] = []
    sccs: list[set[str]] = []
    index_counter = 0

    nodes_sorted = sorted(adj.keys())

    for start in nodes_sorted:
        if start in indices:
            continue

        indices[start] = index_counter
        lowlinks[start] = index_counter
        index_counter += 1
        component_stack.append(start)
        on_stack.add(start)
        call_stack: list[tuple[str, list[str], int]] = [
            (start, sorted(adj.get(start, [])), 0)
        ]

        while call_stack:
            v, neighbors, idx = call_stack[-1]
            advanced = False
            while idx < len(neighbors):
                w = neighbors[idx]
                idx += 1
                if w not in indices:
                    call_stack[-1] = (v, neighbors, idx)
                    indices[w] = index_counter
                    lowlinks[w] = index_counter
                    index_counter += 1
                    component_stack.append(w)
                    on_stack.add(w)
                    call_stack.append((w, sorted(adj.get(w, [])), 0))
                    advanced = True
                    break
                if w in on_stack:
                    lowlinks[v] = min(lowlinks[v], indices[w])
            if advanced:
                continue

            call_stack.pop()
            if lowlinks[v] == indices[v]:
                component: set[str] = set()
                while True:
                    w = component_stack.pop()
                    on_stack.discard(w)
                    component.add(w)
                    if w == v:
                        break
                sccs.append(component)
            if call_stack:
                parent, parent_neighbors, parent_idx = call_stack[-1]
                lowlinks[parent] = min(lowlinks[parent], lowlinks[v])
                call_stack[-1] = (parent, parent_neighbors, parent_idx)

    return sccs
