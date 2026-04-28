from __future__ import annotations

import os
from pathlib import Path

from ..hotspots import build_hotspots
from .adapters import AIAdapter, AIAdapterError, select_adapter
from .prompt import build_prompt, parse_response
from .types import DimensionReview, FileReview, ReviewResult, Skipped

SCHEMA_VERSION = 1
_DIMENSIONS = ("readability", "design", "maintainability", "risk")


def build_review(
    root: Path,
    top_n: int = 5,
    adapter: AIAdapter | None = None,
) -> ReviewResult:
    root = root.resolve()
    if adapter is None:
        adapter = select_adapter(os.environ)

    hotspots = build_hotspots(root)
    candidates = [f for f in hotspots.files if f.category == "hotspot"]
    candidates.sort(key=lambda f: (-(f.change_count * f.coupling), f.path))
    targets = candidates[:top_n]

    reviews: list[FileReview] = []
    skipped: list[Skipped] = []

    for entry in targets:
        path_obj = root / entry.path
        try:
            source = path_obj.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            skipped.append(Skipped(path=entry.path, reason=f"read failed: {exc}"))
            continue

        max_line = max(1, len(source.splitlines()))
        prompt = build_prompt(entry.path, source)

        try:
            response = adapter.review(prompt)
        except AIAdapterError as exc:
            skipped.append(Skipped(path=entry.path, reason=f"adapter error: {exc}"))
            continue

        payload, reason = parse_response(response, max_line)
        if payload is None:
            skipped.append(Skipped(path=entry.path, reason=reason or "invalid response"))
            continue

        reviews.append(_to_file_review(entry.path, payload))

    reviews.sort(key=lambda r: r.path)
    skipped.sort(key=lambda s: s.path)

    return ReviewResult(
        schema_version=SCHEMA_VERSION,
        backend=adapter.name,
        files_reviewed=len(reviews),
        skipped=tuple(skipped),
        reviews=tuple(reviews),
    )


def _to_file_review(path: str, payload: dict) -> FileReview:
    dims_in = payload["dimensions"]
    dims_out: dict[str, DimensionReview] = {}
    for name in _DIMENSIONS:
        d = dims_in[name]
        dims_out[name] = DimensionReview(
            score=int(d["score"]),
            evidence_lines=tuple(int(x) for x in d["evidence_lines"]),
            comment=str(d["comment"]),
            suggestion=str(d["suggestion"]),
        )
    return FileReview(
        path=path,
        dimensions=dims_out,
        confidence=str(payload["confidence"]),
        limitations=str(payload["limitations"]),
    )
