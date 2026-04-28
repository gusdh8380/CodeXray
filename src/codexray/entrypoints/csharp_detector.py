from __future__ import annotations

import re

_MAIN_PATTERN = re.compile(
    r"(?:public|private|internal|protected)?\s*"
    r"static\s+(?:async\s+)?"
    r"(void|int|Task(?:<\s*int\s*>)?)"
    r"\s+Main\s*\(",
)


def detect_main_method(source_code: str) -> str | None:
    """Return the return type of the first matching ``Main`` method, or None.

    Recognized return types: ``void``, ``int``, ``Task``, ``Task<int>``.
    """
    match = _MAIN_PATTERN.search(source_code)
    if match is None:
        return None
    return _normalize(match.group(1))


def _normalize(return_type: str) -> str:
    compact = re.sub(r"\s+", "", return_type)
    return compact
