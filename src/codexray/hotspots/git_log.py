from __future__ import annotations

import subprocess
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

_TIMEOUT = 30


def is_git_repo(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=_TIMEOUT,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def change_counts(root: Path, allowed_paths: Iterable[str]) -> dict[str, int]:
    """Return per-file commit count restricted to ``allowed_paths``.

    Returns an empty dict on any subprocess failure.
    """
    allowed = set(allowed_paths)
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=_TIMEOUT,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}
    if result.returncode != 0:
        return {}

    counts: dict[str, int] = defaultdict(int)
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line in allowed:
            counts[line] += 1
    return dict(counts)
