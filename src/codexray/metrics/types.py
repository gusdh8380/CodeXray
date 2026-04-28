from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NodeMetrics:
    path: str
    language: str
    fan_in: int
    fan_out: int
    external_fan_out: int


@dataclass(frozen=True, slots=True)
class GraphMetrics:
    node_count: int
    edge_count_internal: int
    edge_count_external: int
    scc_count: int
    largest_scc_size: int
    is_dag: bool


@dataclass(frozen=True, slots=True)
class MetricsResult:
    schema_version: int
    nodes: tuple[NodeMetrics, ...]
    graph: GraphMetrics
