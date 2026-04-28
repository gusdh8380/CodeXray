from __future__ import annotations

import os
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path

from ..ai import AIAdapterError, build_review, select_adapter
from ..ai.adapters import AIAdapter
from ..ai.types import ReviewResult
from .ai_briefing import AIBriefingResult, build_ai_briefing, build_evidence_bundle
from .insights import InsightResult, build_insights, cache_put


@dataclass(frozen=True, slots=True)
class ReviewJob:
    id: str
    root: Path
    status: str
    result: ReviewResult | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class InsightsJob:
    id: str
    root: Path
    tab: str
    status: str  # "running" | "done" | "cancelled" | "failed" | "skipped"
    cache_key: str
    result: InsightResult | None = None
    error: str | None = None
    skip_reason: str | None = None


_JOBS: dict[str, ReviewJob] = {}
_LOCK = threading.Lock()
_INSIGHTS_JOBS: dict[str, InsightsJob] = {}
_INSIGHTS_LOCK = threading.Lock()


def start_review_job(root: Path) -> ReviewJob:
    job_id = uuid.uuid4().hex
    job = ReviewJob(id=job_id, root=root, status="running")
    with _LOCK:
        _JOBS[job_id] = job

    thread = threading.Thread(target=_run_review, args=(job_id, root), daemon=True)
    thread.start()
    return job


def get_review_job(job_id: str) -> ReviewJob | None:
    with _LOCK:
        return _JOBS.get(job_id)


def cancel_review_job(job_id: str) -> ReviewJob | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            return None
        cancelled = ReviewJob(id=job.id, root=job.root, status="cancelled")
        _JOBS[job_id] = cancelled
        return cancelled


def _run_review(job_id: str, root: Path) -> None:
    try:
        adapter = select_adapter(os.environ)
        top_n_env = os.environ.get("CODEXRAY_AI_TOP_N", "5").strip()
        try:
            top_n = max(0, int(top_n_env))
        except ValueError as exc:
            raise AIAdapterError(f"invalid CODEXRAY_AI_TOP_N value: {top_n_env!r}") from exc
        result = build_review(root, top_n, adapter)
    except Exception as exc:  # noqa: BLE001 — background job must report any failure.
        if _is_cancelled(job_id):
            return
        _set_job(ReviewJob(id=job_id, root=root, status="failed", error=str(exc)))
        return
    if _is_cancelled(job_id):
        return
    _set_job(ReviewJob(id=job_id, root=root, status="done", result=result))


def _set_job(job: ReviewJob) -> None:
    with _LOCK:
        _JOBS[job.id] = job


def _is_cancelled(job_id: str) -> bool:
    with _LOCK:
        job = _JOBS.get(job_id)
        return job is not None and job.status == "cancelled"


def start_insights_job(
    root: Path,
    tab: str,
    raw_json: str,
    adapter: AIAdapter,
    cache_key: str,
) -> InsightsJob:
    job_id = uuid.uuid4().hex
    job = InsightsJob(
        id=job_id, root=root, tab=tab, status="running", cache_key=cache_key
    )
    with _INSIGHTS_LOCK:
        _INSIGHTS_JOBS[job_id] = job
    thread = threading.Thread(
        target=_run_insights,
        args=(job_id, root, tab, raw_json, adapter, cache_key),
        daemon=True,
    )
    thread.start()
    return job


def get_insights_job(job_id: str) -> InsightsJob | None:
    with _INSIGHTS_LOCK:
        return _INSIGHTS_JOBS.get(job_id)


def cancel_insights_job(job_id: str) -> InsightsJob | None:
    with _INSIGHTS_LOCK:
        job = _INSIGHTS_JOBS.get(job_id)
        if job is None:
            return None
        cancelled = InsightsJob(
            id=job.id,
            root=job.root,
            tab=job.tab,
            status="cancelled",
            cache_key=job.cache_key,
        )
        _INSIGHTS_JOBS[job_id] = cancelled
        return cancelled


def _run_insights(
    job_id: str,
    root: Path,
    tab: str,
    raw_json: str,
    adapter: AIAdapter,
    key: str,
) -> None:
    try:
        result, reason = build_insights(tab, raw_json, adapter)
    except Exception as exc:  # noqa: BLE001 — background job must report any failure.
        if _is_insights_cancelled(job_id):
            return
        _set_insights_job(
            InsightsJob(
                id=job_id,
                root=root,
                tab=tab,
                status="failed",
                cache_key=key,
                error=str(exc),
            )
        )
        return
    if _is_insights_cancelled(job_id):
        return
    if result is None:
        _set_insights_job(
            InsightsJob(
                id=job_id,
                root=root,
                tab=tab,
                status="skipped",
                cache_key=key,
                skip_reason=reason,
            )
        )
        return
    cache_put(key, result)
    _set_insights_job(
        InsightsJob(
            id=job_id,
            root=root,
            tab=tab,
            status="done",
            cache_key=key,
            result=result,
        )
    )


def _set_insights_job(job: InsightsJob) -> None:
    with _INSIGHTS_LOCK:
        _INSIGHTS_JOBS[job.id] = job


def _is_insights_cancelled(job_id: str) -> bool:
    with _INSIGHTS_LOCK:
        job = _INSIGHTS_JOBS.get(job_id)
        return job is not None and job.status == "cancelled"


@dataclass(frozen=True, slots=True)
class AIBriefingJob:
    id: str
    root: Path
    status: str  # "running" | "done" | "cancelled" | "failed"
    step: str = "시작 중..."
    result: AIBriefingResult | None = None
    fallback_briefing: str | None = None
    error: str | None = None


_AI_BRIEFING_JOBS: dict[str, AIBriefingJob] = {}
_AI_BRIEFING_LOCK = threading.Lock()


def start_ai_briefing_job(root: Path) -> AIBriefingJob:
    job_id = uuid.uuid4().hex
    job = AIBriefingJob(id=job_id, root=root, status="running", step="Python 분석 중...")
    with _AI_BRIEFING_LOCK:
        _AI_BRIEFING_JOBS[job_id] = job
    thread = threading.Thread(target=_run_ai_briefing, args=(job_id, root), daemon=True)
    thread.start()
    return job


def get_ai_briefing_job(job_id: str) -> AIBriefingJob | None:
    with _AI_BRIEFING_LOCK:
        return _AI_BRIEFING_JOBS.get(job_id)


def cancel_ai_briefing_job(job_id: str) -> AIBriefingJob | None:
    with _AI_BRIEFING_LOCK:
        job = _AI_BRIEFING_JOBS.get(job_id)
        if job is None:
            return None
        cancelled = AIBriefingJob(id=job.id, root=job.root, status="cancelled", step="취소됨")
        _AI_BRIEFING_JOBS[job_id] = cancelled
        return cancelled


def _run_ai_briefing(job_id: str, root: Path) -> None:
    def update_step(step: str) -> bool:
        with _AI_BRIEFING_LOCK:
            job = _AI_BRIEFING_JOBS.get(job_id)
            if job is None or job.status == "cancelled":
                return False
            _AI_BRIEFING_JOBS[job_id] = AIBriefingJob(
                id=job.id, root=job.root, status="running", step=step
            )
        return True

    try:
        if not update_step("Python 분석 중..."):
            return
        evidence_json, _ = build_evidence_bundle(root)

        if not update_step("AI 해석 중..."):
            return
        result, error = build_ai_briefing(root, evidence_json)
    except Exception as exc:  # noqa: BLE001
        with _AI_BRIEFING_LOCK:
            job = _AI_BRIEFING_JOBS.get(job_id)
            if job and job.status != "cancelled":
                _AI_BRIEFING_JOBS[job_id] = AIBriefingJob(
                    id=job_id, root=root, status="failed", step="실패", error=str(exc)
                )
        return

    with _AI_BRIEFING_LOCK:
        job = _AI_BRIEFING_JOBS.get(job_id)
        if job is None or job.status == "cancelled":
            return
        _AI_BRIEFING_JOBS[job_id] = AIBriefingJob(
            id=job_id,
            root=root,
            status="done",
            step="완료",
            result=result,
            error=error,
        )
