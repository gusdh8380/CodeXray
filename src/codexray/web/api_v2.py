"""JSON API for the React SPA.

This is the v2 web layer that returns JSON instead of HTML fragments. It runs
in parallel with the legacy htmx routes during the briefing-rebuild migration;
the React SPA only uses the routes defined here.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .ai_briefing import build_evidence_bundle
from .briefing_payload import build_briefing_payload
from .jobs import (
    AIBriefingJob,
    cancel_ai_briefing_job,
    get_ai_briefing_job,
    start_ai_briefing_job,
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
        job = start_ai_briefing_job(candidate)
        return JSONResponse({"job_id": job.id})

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

    return router


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
