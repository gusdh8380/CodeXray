from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .language import classify
from .loc import count_nonempty_lines
from .walk import walk


@dataclass(frozen=True, slots=True)
class Row:
    language: str
    file_count: int
    loc: int
    last_modified_at: str


def aggregate(root: Path) -> list[Row]:
    counts: dict[str, int] = defaultdict(int)
    locs: dict[str, int] = defaultdict(int)
    mtimes: dict[str, float] = {}

    for path in walk(root):
        language = classify(path)
        if language is None:
            continue
        counts[language] += 1
        locs[language] += count_nonempty_lines(path)
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if language not in mtimes or mtime > mtimes[language]:
            mtimes[language] = mtime

    rows = [
        Row(
            language=language,
            file_count=counts[language],
            loc=locs[language],
            last_modified_at=_format_mtime(mtimes[language]),
        )
        for language in counts
        if language in mtimes
    ]
    rows.sort(key=lambda r: (-r.loc, r.language))
    return rows


def _format_mtime(epoch: float) -> str:
    return datetime.fromtimestamp(epoch).astimezone().isoformat(timespec="seconds")
