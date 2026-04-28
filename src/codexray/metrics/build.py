from __future__ import annotations

from collections import defaultdict

from ..graph.types import Graph
from .scc import tarjan_scc
from .types import GraphMetrics, MetricsResult, NodeMetrics

SCHEMA_VERSION = 1


def build_metrics(graph: Graph) -> MetricsResult:
    fan_in: dict[str, int] = defaultdict(int)
    fan_out: dict[str, int] = defaultdict(int)
    external_fan_out: dict[str, int] = defaultdict(int)
    self_loop_nodes: set[str] = set()

    internal_adj: dict[str, list[str]] = {n.path: [] for n in graph.nodes}

    edge_count_internal = 0
    edge_count_external = 0
    for edge in graph.edges:
        if edge.kind == "internal":
            edge_count_internal += 1
            fan_out[edge.from_] += 1
            fan_in[edge.to] += 1
            internal_adj.setdefault(edge.from_, []).append(edge.to)
            if edge.from_ == edge.to:
                self_loop_nodes.add(edge.from_)
        else:
            edge_count_external += 1
            external_fan_out[edge.from_] += 1

    sccs = tarjan_scc(internal_adj)
    scc_count = len(sccs)
    largest_scc_size = max((len(c) for c in sccs), default=0)
    is_dag = all(len(c) == 1 for c in sccs) and not self_loop_nodes

    node_metrics = tuple(
        NodeMetrics(
            path=node.path,
            language=node.language,
            fan_in=fan_in[node.path],
            fan_out=fan_out[node.path],
            external_fan_out=external_fan_out[node.path],
        )
        for node in graph.nodes
    )

    graph_metrics = GraphMetrics(
        node_count=len(graph.nodes),
        edge_count_internal=edge_count_internal,
        edge_count_external=edge_count_external,
        scc_count=scc_count,
        largest_scc_size=largest_scc_size,
        is_dag=is_dag,
    )

    return MetricsResult(
        schema_version=SCHEMA_VERSION,
        nodes=node_metrics,
        graph=graph_metrics,
    )
