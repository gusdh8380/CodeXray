from __future__ import annotations

import json
from typing import Any

from .types import EntrypointResult


def to_json(result: EntrypointResult) -> str:
    payload: dict[str, Any] = {
        "schema_version": result.schema_version,
        "entrypoints": [
            {
                "path": e.path,
                "language": e.language,
                "kind": e.kind,
                "detail": e.detail,
            }
            for e in result.entrypoints
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
