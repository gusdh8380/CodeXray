from __future__ import annotations

from pathlib import Path

LANGUAGES_BY_EXT: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cs": "C#",
}


def classify(path: Path) -> str | None:
    return LANGUAGES_BY_EXT.get(path.suffix.lower())
