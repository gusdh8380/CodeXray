from __future__ import annotations

from collections.abc import Iterable

from rich.console import Console
from rich.table import Table

from .inventory import Row


def render(rows: Iterable[Row], console: Console | None = None) -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("language")
    table.add_column("file_count", justify="right")
    table.add_column("loc", justify="right")
    table.add_column("last_modified_at")
    for row in rows:
        table.add_row(
            row.language,
            str(row.file_count),
            str(row.loc),
            row.last_modified_at,
        )
    (console or Console()).print(table)
