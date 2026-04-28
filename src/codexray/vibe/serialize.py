from __future__ import annotations

import json

from .types import VibeCodingReport, VibeEvidence, VibeFinding


def to_json(report: VibeCodingReport) -> str:
    payload = {
        "schema_version": report.schema_version,
        "confidence": report.confidence,
        "confidence_score": report.confidence_score,
        "process_areas": list(report.process_areas),
        "evidence": [_evidence(item) for item in report.evidence],
        "strengths": [_finding(item) for item in report.strengths],
        "risks": [_finding(item) for item in report.risks],
        "actions": [_finding(item) for item in report.actions],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def _evidence(item: VibeEvidence) -> dict[str, str]:
    return {
        "area": item.area,
        "path": item.path,
        "kind": item.kind,
        "detail": item.detail,
    }


def _finding(item: VibeFinding) -> dict[str, object]:
    return {
        "category": item.category,
        "text": item.text,
        "evidence_paths": list(item.evidence_paths),
    }
