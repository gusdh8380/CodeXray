from __future__ import annotations

import json as _json
import os
from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..ai.adapters import AIAdapterError, select_adapter
from ..briefing import build_codebase_briefing
from ..dashboard import build_dashboard
from ..entrypoints import build_entrypoints
from ..entrypoints import to_json as entrypoints_to_json
from ..graph import build_graph
from ..graph import to_json as graph_to_json
from ..hotspots import build_hotspots
from ..hotspots import to_json as hotspots_to_json
from ..inventory import aggregate
from ..metrics import build_metrics
from ..metrics import to_json as metrics_to_json
from ..quality import build_quality
from ..quality import to_json as quality_to_json
from ..report import build_report, to_markdown
from ..summary import build_summary
from ..vibe import build_vibe_coding_report
from .folder_picker import choose_folder
from .insights import cache_get
from .insights import cache_key as _insights_cache_key
from .jobs import (
    cancel_ai_briefing_job,
    cancel_insights_job,
    cancel_review_job,
    get_ai_briefing_job,
    get_insights_job,
    get_review_job,
    start_ai_briefing_job,
    start_insights_job,
    start_review_job,
)
from .render import (
    render_ai_briefing_cancelled,
    render_ai_briefing_failed,
    render_ai_briefing_fallback,
    render_ai_briefing_result,
    render_ai_briefing_running,
    render_codebase_briefing,
    render_dashboard,
    render_entrypoints,
    render_error,
    render_folder_picker_result,
    render_graph,
    render_hotspots,
    render_insights_cancelled,
    render_insights_disabled,
    render_insights_failed,
    render_insights_ready,
    render_insights_running,
    render_insights_skipped,
    render_insights_unavailable,
    render_inventory,
    render_metrics,
    render_overview,
    render_quality,
    render_report,
    render_review,
    render_review_cancelled,
    render_review_failed,
    render_review_prompt,
    render_review_running,
    render_vibe_coding_report,
    validate_root,
)

INSIGHTS_TABS = frozenset(
    {"overview", "inventory", "graph", "metrics", "entrypoints", "quality", "hotspots", "report"}
)
INSIGHTS_DISABLED_TABS = frozenset({"dashboard", "review"})


def create_router(templates: Jinja2Templates) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"default_path": str(Path.cwd())},
        )

    @router.post("/api/overview", response_class=HTMLResponse)
    async def overview(request: Request) -> Response:
        return await _with_root(request, _overview)

    @router.post("/api/briefing", response_class=HTMLResponse)
    async def briefing(request: Request) -> Response:
        form = await _parse_form(request)
        validation = validate_root(form.get("path", ""))
        if validation.error is not None or validation.root is None:
            return _error_response(validation.error or "invalid path")
        return HTMLResponse(render_ai_briefing_running(start_ai_briefing_job(validation.root)))

    @router.get("/api/briefing/status/{job_id}", response_class=HTMLResponse)
    async def briefing_status(job_id: str) -> Response:
        job = get_ai_briefing_job(job_id)
        if job is None:
            return _error_response("briefing job not found")
        if job.status == "running":
            return HTMLResponse(render_ai_briefing_running(job))
        if job.status == "cancelled":
            return HTMLResponse(render_ai_briefing_cancelled(job))
        if job.status == "failed":
            return HTMLResponse(render_ai_briefing_failed(job), status_code=500)
        if job.result is not None:
            return HTMLResponse(render_ai_briefing_result(job.result))
        fallback = build_codebase_briefing(job.root)
        return HTMLResponse(render_ai_briefing_fallback(fallback, job.error or "AI 해석 실패"))

    @router.post("/api/inventory", response_class=HTMLResponse)
    async def inventory(request: Request) -> Response:
        return await _with_root(request, lambda root: render_inventory(aggregate(root)))

    @router.post("/api/graph", response_class=HTMLResponse)
    async def graph(request: Request) -> Response:
        return await _with_root(request, lambda root: render_graph(build_graph(root)))

    @router.post("/api/metrics", response_class=HTMLResponse)
    async def metrics(request: Request) -> Response:
        return await _with_root(request, _metrics)

    @router.post("/api/entrypoints", response_class=HTMLResponse)
    async def entrypoints(request: Request) -> Response:
        return await _with_root(
            request,
            lambda root: render_entrypoints(build_entrypoints(root)),
        )

    @router.post("/api/quality", response_class=HTMLResponse)
    async def quality(request: Request) -> Response:
        return await _with_root(request, lambda root: render_quality(build_quality(root)))

    @router.post("/api/hotspots", response_class=HTMLResponse)
    async def hotspots(request: Request) -> Response:
        return await _with_root(
            request,
            lambda root: render_hotspots(build_hotspots(root)),
        )

    @router.post("/api/report", response_class=HTMLResponse)
    async def report(request: Request) -> Response:
        return await _with_root(request, _report)

    @router.post("/api/dashboard", response_class=HTMLResponse)
    async def dashboard(request: Request) -> Response:
        return await _with_root(
            request,
            lambda root: render_dashboard(build_dashboard(root)),
        )

    @router.post("/api/vibe-coding", response_class=HTMLResponse)
    async def vibe_coding(request: Request) -> Response:
        return await _with_root(
            request,
            lambda root: render_vibe_coding_report(build_vibe_coding_report(root)),
        )

    @router.post("/api/review", response_class=HTMLResponse)
    async def review(request: Request) -> Response:
        form = await _parse_form(request)
        validation = validate_root(form.get("path", ""))
        if validation.error is not None or validation.root is None:
            return _error_response(validation.error or "invalid path")
        if form.get("run") != "true":
            return HTMLResponse(render_review_prompt(str(validation.root)))
        return HTMLResponse(render_review_running(start_review_job(validation.root)))

    @router.get("/api/review/status/{job_id}", response_class=HTMLResponse)
    async def review_status(job_id: str) -> Response:
        job = get_review_job(job_id)
        if job is None:
            return _error_response("review job not found")
        if job.status == "running":
            return HTMLResponse(render_review_running(job))
        if job.status == "cancelled":
            return HTMLResponse(render_review_cancelled(job))
        if job.status == "failed":
            return HTMLResponse(render_review_failed(job), status_code=500)
        if job.result is None:
            return _error_response("review job completed without a result")
        return HTMLResponse(render_review(job.result))

    @router.post("/api/review/cancel/{job_id}", response_class=HTMLResponse)
    async def review_cancel(job_id: str) -> Response:
        job = cancel_review_job(job_id)
        if job is None:
            return _error_response("review job not found")
        return HTMLResponse(render_review_cancelled(job))

    @router.post("/api/browse-folder", response_class=HTMLResponse)
    async def browse_folder() -> Response:
        return HTMLResponse(render_folder_picker_result(choose_folder()))

    @router.post("/api/insights/{tab}", response_class=HTMLResponse)
    async def insights_start(request: Request, tab: str) -> Response:
        return await _insights_dispatch(request, tab, force=False)

    @router.post("/api/insights/{tab}/regenerate", response_class=HTMLResponse)
    async def insights_regenerate(request: Request, tab: str) -> Response:
        return await _insights_dispatch(request, tab, force=True)

    @router.get("/api/insights/status/{job_id}", response_class=HTMLResponse)
    async def insights_status(job_id: str) -> Response:
        job = get_insights_job(job_id)
        if job is None:
            return _error_response("insights job not found")
        if job.status == "running":
            return HTMLResponse(render_insights_running(job))
        if job.status == "cancelled":
            return HTMLResponse(render_insights_cancelled(job))
        if job.status == "failed":
            return HTMLResponse(
                render_insights_failed(job.tab, job.error or "failed"),
                status_code=500,
            )
        if job.status == "skipped":
            return HTMLResponse(
                render_insights_skipped(job.tab, job.skip_reason or "skipped")
            )
        if job.result is None:
            return _error_response("insights job completed without a result")
        return HTMLResponse(render_insights_ready(job.result))

    @router.post("/api/insights/cancel/{job_id}", response_class=HTMLResponse)
    async def insights_cancel(job_id: str) -> Response:
        job = cancel_insights_job(job_id)
        if job is None:
            return _error_response("insights job not found")
        return HTMLResponse(render_insights_cancelled(job))

    return router


async def _insights_dispatch(request: Request, tab: str, *, force: bool) -> Response:
    if tab in INSIGHTS_DISABLED_TABS:
        return HTMLResponse(
            render_insights_disabled(tab, "본 변경에서 인사이트가 비활성화된 탭입니다.")
        )
    if tab not in INSIGHTS_TABS:
        return _error_response(f"unsupported tab: {tab}")
    form = await _parse_form(request)
    validation = validate_root(form.get("path", ""))
    if validation.error is not None or validation.root is None:
        return _error_response(validation.error or "invalid path")
    try:
        adapter = select_adapter(os.environ)
    except AIAdapterError as exc:
        return HTMLResponse(render_insights_unavailable(tab, str(exc)))
    raw_json = _build_raw_json(validation.root, tab)
    key = _insights_cache_key(
        path=str(validation.root),
        tab=tab,
        raw_json=raw_json,
        adapter_id=adapter.name,
    )
    if not force:
        cached = cache_get(key)
        if cached is not None:
            return HTMLResponse(render_insights_ready(cached))
    job = start_insights_job(validation.root, tab, raw_json, adapter, key)
    return HTMLResponse(render_insights_running(job))


def _build_raw_json(root: Path, tab: str) -> str:
    if tab == "inventory":
        rows = list(aggregate(root))
        payload = {
            "schema_version": 1,
            "tab": "inventory",
            "rows": [
                {
                    "language": row.language,
                    "file_count": row.file_count,
                    "loc": row.loc,
                    "last_modified_at": row.last_modified_at,
                }
                for row in rows
            ],
        }
        return _json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if tab == "graph":
        return graph_to_json(build_graph(root))
    if tab == "metrics":
        return metrics_to_json(build_metrics(build_graph(root)))
    if tab == "entrypoints":
        return entrypoints_to_json(build_entrypoints(root))
    if tab == "quality":
        return quality_to_json(build_quality(root))
    if tab == "hotspots":
        return hotspots_to_json(build_hotspots(root))
    if tab == "report":
        data = build_report(root)
        overall = data.quality.overall
        payload = {
            "schema_version": 1,
            "tab": "report",
            "grade": {"grade": overall.grade, "score": overall.score},
            "files": sum(row.file_count for row in data.inventory),
            "hotspots_summary": {
                "hotspot": data.hotspots.summary.hotspot,
                "active_stable": data.hotspots.summary.active_stable,
                "neglected_complex": data.hotspots.summary.neglected_complex,
                "stable": data.hotspots.summary.stable,
            },
            "top_hotspots": [
                {
                    "path": item.path,
                    "category": item.category,
                    "score": item.change_count * item.coupling,
                }
                for item in list(data.hotspots.files)[:10]
            ],
            "recommendations": [rec.text for rec in data.recommendations],
        }
        return _json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if tab == "overview":
        rows = list(aggregate(root))
        graph = build_graph(root)
        quality = build_quality(root)
        hotspots = build_hotspots(root)
        overall = quality.overall
        top_hotspot = next(
            (item for item in hotspots.files if item.category == "hotspot"),
            None,
        )
        payload = {
            "schema_version": 1,
            "tab": "overview",
            "files": sum(row.file_count for row in rows),
            "loc": sum(row.loc for row in rows),
            "languages": [row.language for row in rows],
            "graph": {"nodes": len(graph.nodes), "edges": len(graph.edges)},
            "grade": {"grade": overall.grade, "score": overall.score},
            "hotspots_summary": {
                "hotspot": hotspots.summary.hotspot,
                "active_stable": hotspots.summary.active_stable,
                "neglected_complex": hotspots.summary.neglected_complex,
                "stable": hotspots.summary.stable,
            },
            "top_hotspot": (
                {
                    "path": top_hotspot.path,
                    "score": top_hotspot.change_count * top_hotspot.coupling,
                }
                if top_hotspot is not None
                else None
            ),
        }
        return _json.dumps(payload, ensure_ascii=False, sort_keys=True)
    raise ValueError(f"unsupported insights tab: {tab}")


async def _with_root(
    request: Request,
    handler: Callable[[Path], str],
) -> Response:
    form = await _parse_form(request)
    validation = validate_root(form.get("path", ""))
    if validation.error is not None or validation.root is None:
        return _error_response(validation.error or "invalid path")
    return HTMLResponse(handler(validation.root))


async def _parse_form(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _overview(root: Path) -> str:
    inventory = tuple(aggregate(root))
    graph = build_graph(root)
    metrics = build_metrics(graph)
    entrypoints = build_entrypoints(root)
    quality = build_quality(root)
    hotspots = build_hotspots(root)
    summary = build_summary(quality, hotspots, metrics, entrypoints, inventory)
    return render_overview(root, inventory, quality, hotspots, graph, summary)


def _metrics(root: Path) -> str:
    graph = build_graph(root)
    return render_metrics(build_metrics(graph))


def _report(root: Path) -> str:
    data = build_report(root)
    return render_report(data, to_markdown(data))


def _error_response(message: str) -> HTMLResponse:
    return HTMLResponse(
        render_error(message),
        status_code=status.HTTP_400_BAD_REQUEST,
    )
