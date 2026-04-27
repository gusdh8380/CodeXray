from __future__ import annotations

import sys
from pathlib import Path

import typer

from .inventory import aggregate
from .render import render

app = typer.Typer(add_completion=False, no_args_is_help=True, help="CodeXray CLI")


@app.callback()
def _root() -> None:
    """CodeXray — codebase X-ray (구조 분석 + 품질 평가)."""


@app.command("inventory")
def inventory_cmd(path: str = typer.Argument(..., metavar="PATH")) -> None:
    """Print a per-language inventory table for ``PATH``."""
    target = Path(path)
    if not target.exists():
        typer.echo(f"path does not exist: {path}", err=True)
        raise typer.Exit(code=2)
    if not target.is_dir():
        typer.echo(f"path is not a directory: {path}", err=True)
        raise typer.Exit(code=2)
    try:
        rows = aggregate(target)
    except PermissionError as exc:
        typer.echo(f"permission denied: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    render(rows)


def main() -> None:
    app()


if __name__ == "__main__":
    sys.exit(0 if app() is None else 1)
