from __future__ import annotations

import json
from typing import Any

from .types import HotspotsReport


def to_json(report: HotspotsReport) -> str:
    payload: dict[str, Any] = {
        "schema_version": report.schema_version,
        "thresholds": {
            "change_count_median": report.thresholds.change_count_median,
            "coupling_median": report.thresholds.coupling_median,
        },
        "summary": {
            "hotspot": report.summary.hotspot,
            "active_stable": report.summary.active_stable,
            "neglected_complex": report.summary.neglected_complex,
            "stable": report.summary.stable,
        },
        "files": [
            {
                "path": f.path,
                "change_count": f.change_count,
                "coupling": f.coupling,
                "category": f.category,
            }
            for f in report.files
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
