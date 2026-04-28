from __future__ import annotations

import re

_MONOBEHAVIOUR_CLASS = re.compile(r"\bclass\s+\w+\s*:\s*[^{]*\bMonoBehaviour\b")

_LIFECYCLE_NAMES = (
    "Awake",
    "OnEnable",
    "Start",
    "FixedUpdate",
    "Update",
    "LateUpdate",
    "OnDisable",
    "OnDestroy",
)
_LIFECYCLE_PATTERN = re.compile(
    r"\b(" + "|".join(_LIFECYCLE_NAMES) + r")\s*\(",
)


def detect_unity_lifecycle(source_code: str) -> list[str]:
    """Return sorted lifecycle method names if the file declares a MonoBehaviour
    subclass that defines at least one of them. Empty list otherwise."""
    if not _MONOBEHAVIOUR_CLASS.search(source_code):
        return []
    matches = {m.group(1) for m in _LIFECYCLE_PATTERN.finditer(source_code)}
    if not matches:
        return []
    return sorted(matches)
