"""Reconstruct the development-process timeline from git history."""

from __future__ import annotations

from typing import Any


def build_timeline(*, history: Any) -> list[dict[str, Any]]:
    if not history.available:
        return []
    entries: list[dict[str, Any]] = []
    seen_categories: set[str] = set()
    process_commits = list(reversed(history.process_commits))
    for idx, commit in enumerate(process_commits[:8]):
        for cat in commit.process_categories:
            if cat in seen_categories:
                continue
            seen_categories.add(cat)
            type_label, type_friendly = _category_to_timeline_type(cat)
            entries.append(
                {
                    "day": idx + 1,
                    "type": type_label,
                    "title": f"{type_friendly} 도입",
                    "evidence": f"{commit.hash[:7]} {commit.subject[:60]}",
                }
            )
    if not entries:
        for idx, commit in enumerate(list(history.recent_commits)[:5]):
            entries.append(
                {
                    "day": idx + 1,
                    "type": "code",
                    "title": commit.subject[:60],
                    "evidence": commit.hash[:7],
                }
            )
    return entries[:10]


def _category_to_timeline_type(category: str) -> tuple[str, str]:
    lower = category.lower()
    if "openspec" in lower or "명세" in category:
        return "spec", "OpenSpec 명세"
    if "claude" in lower or "에이전트" in category:
        return "agent", "에이전트 지침"
    if "validation" in lower or "검증" in category:
        return "validation", "검증 문서"
    if "vibe" in lower or "회고" in category or "handoff" in lower:
        return "retro", "회고/인수인계"
    return "code", category
