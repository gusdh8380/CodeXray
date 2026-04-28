from __future__ import annotations

import os
import sys
from pathlib import Path

import typer

from .ai import AIAdapterError, build_review, select_adapter
from .ai import to_json as review_to_json
from .dashboard import build_dashboard, to_html
from .entrypoints import build_entrypoints
from .entrypoints import to_json as entrypoints_to_json
from .graph import build_graph
from .graph import to_json as graph_to_json
from .hotspots import build_hotspots
from .hotspots import to_json as hotspots_to_json
from .inventory import aggregate
from .metrics import build_metrics
from .metrics import to_json as metrics_to_json
from .quality import build_quality
from .quality import to_json as quality_to_json
from .render import render
from .report import build_report, to_markdown
from .web import serve as serve_web

app = typer.Typer(add_completion=False, no_args_is_help=True, help="CodeXray CLI")


@app.callback()
def _root() -> None:
    """CodeXray — codebase X-ray (구조 분석 + 품질 평가)."""


def _validate_dir(path: str) -> Path:
    target = Path(path)
    if not target.exists():
        typer.echo(f"path does not exist: {path}", err=True)
        raise typer.Exit(code=2)
    if not target.is_dir():
        typer.echo(f"path is not a directory: {path}", err=True)
        raise typer.Exit(code=2)
    return target


@app.command("inventory")
def inventory_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Print a per-language inventory table for ``PATH``."""
    target = _validate_dir(path)
    try:
        rows = aggregate(target)
    except PermissionError as exc:
        typer.echo(f"permission denied: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    render(rows)


@app.command("graph")
def graph_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Emit the file-level dependency graph of ``PATH`` as JSON."""
    target = _validate_dir(path)
    graph = build_graph(target)
    typer.echo(graph_to_json(graph))


@app.command("metrics")
def metrics_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Emit fan-in/fan-out/SCC metrics for ``PATH`` as JSON."""
    target = _validate_dir(path)
    graph = build_graph(target)
    result = build_metrics(graph)
    typer.echo(metrics_to_json(result))


@app.command("entrypoints")
def entrypoints_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Emit detected entrypoints for ``PATH`` as JSON."""
    target = _validate_dir(path)
    result = build_entrypoints(target)
    typer.echo(entrypoints_to_json(result))


@app.command("quality")
def quality_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Emit a 4-dimension quality grade JSON for ``PATH``."""
    target = _validate_dir(path)
    report = build_quality(target)
    typer.echo(quality_to_json(report))


@app.command("hotspots")
def hotspots_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Emit change-frequency × coupling hotspots JSON for ``PATH``."""
    target = _validate_dir(path)
    report = build_hotspots(target)
    typer.echo(hotspots_to_json(report))


@app.command("report")
def report_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Emit a 1-page Markdown report combining all analyses for ``PATH``."""
    target = _validate_dir(path)
    data = build_report(target)
    typer.echo(to_markdown(data))


@app.command("dashboard")
def dashboard_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Emit a single self-contained HTML dashboard for ``PATH``."""
    target = _validate_dir(path)
    data = build_dashboard(target)
    typer.echo(to_html(data))


@app.command("review")
def review_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Run AI qualitative review on the top hotspot files for ``PATH``."""
    target = _validate_dir(path)
    try:
        adapter = select_adapter(os.environ)
    except AIAdapterError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(f"using AI backend: {adapter.name}", err=True)
    top_n_env = os.environ.get("CODEXRAY_AI_TOP_N", "5").strip()
    try:
        top_n = max(0, int(top_n_env))
    except ValueError as exc:
        typer.echo(
            f"error: invalid CODEXRAY_AI_TOP_N value: {top_n_env!r}",
            err=True,
        )
        raise typer.Exit(code=2) from exc
    result = build_review(target, top_n=top_n, adapter=adapter)
    typer.echo(review_to_json(result))


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", "--host", help="Host interface to bind."),
    port: int = typer.Option(8080, "--port", help="Port to bind."),
    no_browser: bool = typer.Option(
        False,
        "--no-browser",
        help="Do not open the browser automatically.",
    ),
) -> None:
    """Start the localhost web UI."""
    serve_web(host=host, port=port, open_browser=not no_browser)


def main() -> None:
    app()


if __name__ == "__main__":
    sys.exit(0 if app() is None else 1)
