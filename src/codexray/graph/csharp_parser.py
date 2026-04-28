from __future__ import annotations

import re
from pathlib import Path

from .types import RawImport

_USING_PATTERN = re.compile(
    r"^\s*using(?:\s+static)?\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;",
    re.MULTILINE,
)


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
