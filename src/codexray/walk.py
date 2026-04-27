from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from pathspec import PathSpec

DEFAULT_IGNORE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        "dist",
        "build",
        "venv",
        ".venv",
        "__pycache__",
        ".next",
        "target",
    }
)


def _load_root_gitignore(root: Path) -> PathSpec:
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        return PathSpec.from_lines("gitignore", [])
    try:
        lines = gitignore.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return PathSpec.from_lines("gitignore", [])
    return PathSpec.from_lines("gitignore", lines)


def walk(root: Path) -> Iterator[Path]:
    """Yield file paths under ``root`` honoring .gitignore + default ignore dirs.

    Symlinks are not followed; symlink entries themselves are skipped.
    """
    spec = _load_root_gitignore(root)
    yield from _scan(root, root, spec)


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _scan(root: Path, current: Path, spec: PathSpec) -> Iterator[Path]:
    try:
        scanner = os.scandir(current)
    except (PermissionError, OSError):
        return
    with scanner as it:
        entries = list(it)
    for entry in entries:
        path = Path(entry.path)
        if entry.is_symlink():
            continue
        try:
            is_dir = entry.is_dir(follow_symlinks=False)
        except OSError:
            continue
        if is_dir:
            if entry.name in DEFAULT_IGNORE_DIRS:
                continue
            if path != root and spec.match_file(_rel(root, path) + "/"):
                continue
            yield from _scan(root, path, spec)
            continue
        try:
            is_file = entry.is_file(follow_symlinks=False)
        except OSError:
            continue
        if not is_file:
            continue
        if spec.match_file(_rel(root, path)):
            continue
        yield path
