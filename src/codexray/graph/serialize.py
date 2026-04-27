from __future__ import annotations

import json
from typing import Any

from .types import Graph

SCHEMA_VERSION = 1


def to_json(graph: Graph) -> str:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "nodes": [{"path": n.path, "language": n.language} for n in graph.nodes],
        "edges": [{"from": e.from_, "to": e.to, "kind": e.kind} for e in graph.edges],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
