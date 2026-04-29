"""JSON API for the React SPA.

This is the v2 web layer that returns JSON instead of HTML fragments. It runs
in parallel with the legacy htmx routes during the briefing-rebuild migration;
the React SPA only uses the routes defined here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..entrypoints import build_entrypoints
from ..entrypoints import to_json as entrypoints_to_json
from ..graph import build_graph
from ..graph import to_json as graph_to_json
from ..hotspots import build_hotspots
from ..hotspots import to_json as hotspots_to_json
from dataclasses import asdict

from ..inventory import aggregate
from ..metrics import build_metrics
from ..metrics import to_json as metrics_to_json
from ..quality import build_quality
from ..quality import to_json as quality_to_json
from ..dashboard import build_dashboard
from ..dashboard import to_html as dashboard_to_html
from ..report import build_report
from ..report import to_markdown as report_to_markdown
from ..summary import to_json as summary_to_json
from ..vibe import build_vibe_coding_report
from ..vibe import to_json as vibe_to_json
from .briefing_payload import build_briefing_payload
from .jobs import (
    AIBriefingJob,
    ReviewJob,
    cancel_ai_briefing_job,
    cancel_review_job,
    get_ai_briefing_job,
    get_review_job,
    start_ai_briefing_job,
    start_review_job,
)


class PathRequest(BaseModel):
    path: str


_STEP_TO_PROGRESS = {
    "시작 중...": 0.05,
    "Python 분석 중...": 0.20,
    "AI 해석 중...": 0.65,
    "완료": 1.0,
    "실패": 1.0,
    "취소됨": 1.0,
}


def create_v2_router() -> APIRouter:
    router = APIRouter()

    @router.get("/api/default-path")
    async def default_path() -> JSONResponse:
        return JSONResponse({"path": os.getcwd()})

    @router.post("/api/briefing")
    async def start_briefing(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(req, lambda p: {"job_id": start_ai_briefing_job(p).id})

    @router.get("/api/briefing/status/{job_id}")
    async def briefing_status(job_id: str) -> JSONResponse:
        job = get_ai_briefing_job(job_id)
        if job is None:
            return JSONResponse({"error": "job not found"}, status_code=404)
        return JSONResponse(_serialize_job(job))

    @router.post("/api/briefing/cancel/{job_id}")
    async def briefing_cancel(job_id: str) -> JSONResponse:
        job = cancel_ai_briefing_job(job_id)
        if job is None:
            return JSONResponse({"error": "job not found"}, status_code=404)
        return JSONResponse(_serialize_job(job))

    @router.post("/api/inventory")
    async def inventory_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(
            req,
            lambda p: {
                "schema_version": 1,
                "rows": [asdict(row) for row in aggregate(p)],
            },
        )

    @router.post("/api/graph")
    async def graph_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(req, lambda p: _decode(graph_to_json(build_graph(p))))

    @router.post("/api/metrics")
    async def metrics_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(
            req, lambda p: _decode(metrics_to_json(build_metrics(build_graph(p))))
        )

    @router.post("/api/entrypoints")
    async def entrypoints_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(
            req, lambda p: _decode(entrypoints_to_json(build_entrypoints(p)))
        )

    @router.post("/api/quality")
    async def quality_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(req, lambda p: _decode(quality_to_json(build_quality(p))))

    @router.post("/api/hotspots")
    async def hotspots_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(req, lambda p: _decode(hotspots_to_json(build_hotspots(p))))

    @router.post("/api/vibe-coding")
    async def vibe_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(
            req, lambda p: _decode(vibe_to_json(build_vibe_coding_report(p)))
        )

    @router.post("/api/dashboard")
    async def dashboard_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(
            req,
            lambda p: {
                "schema_version": 1,
                "html": dashboard_to_html(build_dashboard(p)),
            },
        )

    @router.post("/api/report")
    async def report_endpoint(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(req, _build_report_payload)

    @router.post("/api/review")
    async def start_review(req: PathRequest) -> JSONResponse:
        return _validate_path_or_run(
            req, lambda p: {"job_id": start_review_job(p).id}
        )

    @router.get("/api/review/status/{job_id}")
    async def review_status(job_id: str) -> JSONResponse:
        job = get_review_job(job_id)
        if job is None:
            return JSONResponse({"error": "review job not found"}, status_code=404)
        return JSONResponse(_serialize_review_job(job))

    @router.post("/api/review/cancel/{job_id}")
    async def review_cancel(job_id: str) -> JSONResponse:
        job = cancel_review_job(job_id)
        if job is None:
            return JSONResponse({"error": "review job not found"}, status_code=404)
        return JSONResponse(_serialize_review_job(job))

    @router.post("/api/browse-folder")
    async def browse_folder_endpoint() -> JSONResponse:
        from .folder_picker import choose_folder

        result = choose_folder()
        if result.cancelled:
            return JSONResponse({"cancelled": True})
        if result.error:
            return JSONResponse({"error": result.error}, status_code=400)
        return JSONResponse({"path": result.path})

    return router


def _build_report_payload(root: Path) -> dict[str, Any]:
    report = build_report(root)
    summary = json.loads(summary_to_json(report.summary))
    return {
        "schema_version": 1,
        "path": report.path,
        "generated_date": report.generated_date,
        "summary": summary,
        "recommendations": [
            {"priority": r.priority, "text": r.text} for r in report.recommendations
        ],
        "markdown": report_to_markdown(report),
    }


def _validate_path_or_run(
    req: PathRequest,
    runner: Callable[[Path], dict[str, Any]],
) -> JSONResponse:
    candidate = Path(req.path).expanduser()
    if not candidate.exists():
        return JSONResponse(
            {"error": f"경로를 찾을 수 없습니다: {candidate}"},
            status_code=400,
        )
    if not candidate.is_dir():
        return JSONResponse(
            {"error": f"디렉토리가 아닙니다: {candidate}"},
            status_code=400,
        )
    try:
        return JSONResponse(runner(candidate))
    except Exception as exc:  # noqa: BLE001 — surface analyzer errors to the SPA
        return JSONResponse({"error": f"분석 실패: {exc}"}, status_code=500)


def _decode(json_text: str) -> dict[str, Any]:
    return json.loads(json_text)


def _serialize_job(job: AIBriefingJob) -> dict[str, Any]:
    progress = _STEP_TO_PROGRESS.get(job.step, 0.5)
    payload: dict[str, Any] = {
        "job_id": job.id,
        "status": _normalize_status(job.status),
        "step": job.step,
        "progress": progress,
    }
    if job.status == "done":
        try:
            payload["result"] = build_briefing_payload(job.root, job.result)
        except Exception as exc:  # noqa: BLE001 — surface adapter errors to client
            payload["status"] = "failed"
            payload["error"] = f"briefing 결과 변환 실패: {exc}"
    elif job.status == "failed":
        payload["error"] = job.error or "알 수 없는 오류"
        try:
            payload["result"] = build_briefing_payload(job.root, None)
        except Exception:  # noqa: BLE001 — fallback failure is non-fatal here
            pass
    return payload


def _normalize_status(status: str) -> str:
    if status == "done":
        return "completed"
    return status


def _serialize_review_job(job: ReviewJob) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "job_id": job.id,
        "status": _normalize_status(job.status),
    }
    if job.status == "done" and job.result is not None:
        payload["result"] = _serialize_review_result(job.result)
    elif job.status == "failed":
        payload["error"] = job.error or "알 수 없는 오류"
    return payload


def _serialize_review_result(result: Any) -> dict[str, Any]:
    return {
        "schema_version": result.schema_version,
        "backend": result.backend,
        "files_reviewed": result.files_reviewed,
        "skipped": [{"path": s.path, "reason": s.reason} for s in result.skipped],
        "reviews": [
            {
                "path": r.path,
                "confidence": r.confidence,
                "limitations": r.limitations,
                "dimensions": {
                    name: {
                        "score": d.score,
                        "evidence_lines": list(d.evidence_lines),
                        "comment": d.comment,
                        "suggestion": d.suggestion,
                    }
                    for name, d in r.dimensions.items()
                },
            }
            for r in result.reviews
        ],
    }
