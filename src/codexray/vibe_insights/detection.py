"""Auto-detection of vibe coding signals."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_STRONG_PATHS = ("CLAUDE.md", "AGENTS.md", ".claude", ".omc", "openspec")


def detect_vibe_coding(*, root: Path, vibe: Any, history: Any) -> bool:
    """Return True when this repo has at least one strong vibe-coding signal.

    Strong: CLAUDE.md / AGENTS.md / .claude/ / .omc/ / openspec/ / Co-Authored-By: Claude
    Medium: vibe analyzer reports medium/high confidence, or git history has process commits
    """
    for rel in _STRONG_PATHS:
        if (root / rel).exists():
            return True
    if vibe.confidence in {"medium", "high"}:
        return True
    if history.process_commits:
        return True
    if any(
        "Co-Authored-By: Claude" in (c.subject or "") for c in history.recent_commits
    ):
        return True
    return False
