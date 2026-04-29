"""Detect modules from file paths via directory structure."""

from __future__ import annotations

from pathlib import PurePosixPath


_MODULE_PALETTE = (
    "#3b82f6",  # blue
    "#8b5cf6",  # purple
    "#ec4899",  # pink
    "#f59e0b",  # amber
    "#10b981",  # emerald
    "#06b6d4",  # cyan
    "#ef4444",  # red
    "#84cc16",  # lime
    "#a855f7",  # violet
    "#14b8a6",  # teal
    "#f97316",  # orange
    "#0ea5e9",  # sky
)


def detect_module(path: str) -> str:
    """Return a module label for a file path.

    Rules:
    - `src/<pkg>/<module>/...` → `<module>`
    - `src/<pkg>/<file>.py` (top-level package file) → `core`
    - `tests/<dir>/...` → `tests/<dir>`
    - `tests/<file>.py` → `tests`
    - other top-level dirs → first segment
    - root files → `root`
    """
    parts = PurePosixPath(path).parts
    if not parts:
        return "root"
    if parts[0] == "src" and len(parts) >= 3:
        # src/pkg/<module>/...
        if len(parts) >= 4:
            return parts[2]
        # src/pkg/<file>.py
        return "core"
    if parts[0] == "tests":
        if len(parts) >= 3:
            return f"tests/{parts[1]}"
        return "tests"
    if len(parts) >= 2:
        return parts[0]
    return "root"


def assign_module_colors(modules: list[str]) -> dict[str, str]:
    """Assign deterministic colors per module name."""
    sorted_modules = sorted(set(modules))
    return {name: _MODULE_PALETTE[i % len(_MODULE_PALETTE)] for i, name in enumerate(sorted_modules)}
