from __future__ import annotations

import json
from typing import Any

from .types import MetricsResult


def to_json(metrics: MetricsResult) -> str:
    payload: dict[str, Any] = {
        "schema_version": metrics.schema_version,
        "nodes": [
            {
                "path": n.path,
                "language": n.language,
                "fan_in": n.fan_in,
                "fan_out": n.fan_out,
                "external_fan_out": n.external_fan_out,
            }
            for n in metrics.nodes
        ],
        "graph": {
            "node_count": metrics.graph.node_count,
            "edge_count_internal": metrics.graph.edge_count_internal,
            "edge_count_external": metrics.graph.edge_count_external,
            "scc_count": metrics.graph.scc_count,
            "largest_scc_size": metrics.graph.largest_scc_size,
            "is_dag": metrics.graph.is_dag,
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
