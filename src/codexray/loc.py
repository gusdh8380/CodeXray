from __future__ import annotations

from pathlib import Path


def count_nonempty_lines(path: Path) -> int:
    """Count lines whose content is not empty after stripping whitespace.

    Decoding errors are ignored (best-effort UTF-8 read). Whitespace-only
    lines are treated as empty.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    if not text:
        return 0
    return sum(1 for line in text.splitlines() if line.strip())
