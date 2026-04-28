from __future__ import annotations

import json
from typing import Any

from .types import QualityReport


def to_json(report: QualityReport) -> str:
    payload: dict[str, Any] = {
        "schema_version": report.schema_version,
        "overall": {
            "score": report.overall.score,
            "grade": report.overall.grade,
        },
        "dimensions": {
            name: {
                "score": dim.score,
                "grade": dim.grade,
                "detail": dim.detail,
            }
            for name, dim in report.dimensions.items()
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
