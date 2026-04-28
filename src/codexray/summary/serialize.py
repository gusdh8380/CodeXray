from __future__ import annotations

import json

from .types import SummaryResult


def to_json(result: SummaryResult) -> str:
    payload = {
        "schema_version": result.schema_version,
        "strengths": [
            {
                "category": item.category,
                "text": item.text,
                "evidence": dict(item.evidence),
            }
            for item in result.strengths
        ],
        "weaknesses": [
            {
                "category": item.category,
                "text": item.text,
                "evidence": dict(item.evidence),
            }
            for item in result.weaknesses
        ],
        "actions": [
            {
                "text": item.text,
                "evidence": dict(item.evidence),
            }
            for item in result.actions
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
