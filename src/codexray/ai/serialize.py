from __future__ import annotations

import json
from typing import Any

from .types import ReviewResult

_DIMENSIONS = ("readability", "design", "maintainability", "risk")


def to_json(result: ReviewResult) -> str:
    payload: dict[str, Any] = {
        "schema_version": result.schema_version,
        "backend": result.backend,
        "files_reviewed": result.files_reviewed,
        "skipped": [
            {"path": s.path, "reason": s.reason} for s in result.skipped
        ],
        "reviews": [
            {
                "path": r.path,
                "dimensions": {
                    name: {
                        "score": r.dimensions[name].score,
                        "evidence_lines": list(r.dimensions[name].evidence_lines),
                        "comment": r.dimensions[name].comment,
                        "suggestion": r.dimensions[name].suggestion,
                    }
                    for name in _DIMENSIONS
                },
                "confidence": r.confidence,
                "limitations": r.limitations,
            }
            for r in result.reviews
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
