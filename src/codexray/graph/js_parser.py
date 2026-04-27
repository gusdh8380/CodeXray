from __future__ import annotations

import re
from pathlib import Path

from .types import RawImport

_QUOTED = r"""['"`]([^'"`]+)['"`]"""

_PATTERNS = (
    re.compile(rf"\bfrom\s+{_QUOTED}"),
    re.compile(rf"\bimport\s+{_QUOTED}"),
    re.compile(rf"\brequire\s*\(\s*{_QUOTED}"),
    re.compile(rf"\bimport\s*\(\s*{_QUOTED}"),
)


def extract_imports(source_code: str, source_path: Path, language: str) -> list[RawImport]:
    seen: set[str] = set()
    out: list[RawImport] = []
    for pattern in _PATTERNS:
        for match in pattern.finditer(source_code):
            raw = match.group(1)
            key = f"{pattern.pattern}|{raw}"
            if key in seen:
                continue
            seen.add(key)
            out.append(RawImport(source=source_path, raw=raw, level=0, language=language))
    return out
