from __future__ import annotations

import re
from pathlib import Path

from .types import RawImport

_USING_PATTERN = re.compile(
    r"^\s*using(?:\s+static)?\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;",
    re.MULTILINE,
)

_STRING_OR_COMMENT = re.compile(
    r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|//[^\n]*|/\*.*?\*/',
    re.DOTALL,
)
_TYPE_TOKEN = re.compile(r"\b([A-Z]\w*)\b")


def extract_imports(source_code: str, source_path: Path) -> list[RawImport]:
    seen: set[str] = set()
    out: list[RawImport] = []
    for match in _USING_PATTERN.finditer(source_code):
        raw = match.group(1)
        if raw in seen:
            continue
        seen.add(raw)
        out.append(RawImport(source=source_path, raw=raw, level=0, language="C#"))
    return out


def extract_type_usages(source_code: str) -> set[str]:
    """Return PascalCase tokens used as potential type names.

    Strips string literals and comments first to avoid false positives.
    """
    cleaned = _STRING_OR_COMMENT.sub("", source_code)
    return {m.group(1) for m in _TYPE_TOKEN.finditer(cleaned)}
