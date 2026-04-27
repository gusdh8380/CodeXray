from __future__ import annotations

import sys
from pathlib import Path

import typer

from .graph import build_graph, to_json
from .inventory import aggregate
from .render import render

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
    typer.echo(to_json(graph))


def main() -> None:
    app()


if __name__ == "__main__":
    sys.exit(0 if app() is None else 1)
