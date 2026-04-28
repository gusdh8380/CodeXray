from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..dashboard import build_dashboard
from ..entrypoints import build_entrypoints
from ..graph import build_graph
from ..hotspots import build_hotspots
from ..inventory import aggregate
from ..metrics import build_metrics
from ..quality import build_quality
from ..report import build_report, to_markdown
from .jobs import get_review_job, start_review_job
from .render import (
    render_dashboard,
    render_entrypoints,
    render_error,
    render_graph,
    render_hotspots,
    render_inventory,
    render_metrics,
    render_overview,
    render_quality,
    render_report,
    render_review,
    render_review_failed,
    render_review_prompt,
    render_review_running,
    validate_root,
)


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
        if job.status == "failed":
            return HTMLResponse(render_review_failed(job), status_code=500)
        if job.result is None:
            return _error_response("review job completed without a result")
        return HTMLResponse(render_review(job.result))

    return router


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
    inventory = aggregate(root)
    graph = build_graph(root)
    quality = build_quality(root)
    hotspots = build_hotspots(root)
    return render_overview(root, inventory, quality, hotspots, graph)


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
