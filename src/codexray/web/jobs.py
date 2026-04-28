from __future__ import annotations

import os
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path

from ..ai import AIAdapterError, build_review, select_adapter
from ..ai.types import ReviewResult


@dataclass(frozen=True, slots=True)
class ReviewJob:
    id: str
    root: Path
    status: str
    result: ReviewResult | None = None
    error: str | None = None


_JOBS: dict[str, ReviewJob] = {}
_LOCK = threading.Lock()


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
