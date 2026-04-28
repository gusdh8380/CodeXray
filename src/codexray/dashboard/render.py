from __future__ import annotations

import json
from typing import Any

from ..entrypoints import to_json as entrypoints_to_json
from ..graph import to_json as graph_to_json
from ..hotspots import to_json as hotspots_to_json
from ..metrics import to_json as metrics_to_json
from ..quality import to_json as quality_to_json
from .template import HTML_TEMPLATE
from .types import DashboardData


def to_html(data: DashboardData) -> str:
    quality_overall = data.quality.overall
    grade = quality_overall.grade or "N/A"
    score = (
        str(quality_overall.score) if quality_overall.score is not None else "N/A"
    )
    grade_class = grade if grade in {"A", "B", "C", "D", "F"} else "NA"

    return HTML_TEMPLATE.substitute(
        title=_safe(data.path),
        path=_safe(data.path),
        date=data.generated_date,
        grade=grade,
        score=score,
        grade_class=grade_class,
        data_inventory=_inventory_json(data),
        data_graph=graph_to_json(data.graph),
        data_metrics=metrics_to_json(data.metrics),
        data_entrypoints=entrypoints_to_json(data.entrypoints),
        data_quality=quality_to_json(data.quality),
        data_hotspots=hotspots_to_json(data.hotspots),
    )


def _inventory_json(data: DashboardData) -> str:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "rows": [
            {
                "language": row.language,
                "file_count": row.file_count,
                "loc": row.loc,
                "last_modified_at": row.last_modified_at,
            }
            for row in data.inventory
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def _safe(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
