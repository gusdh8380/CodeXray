"""Three-axis vibe-coding scoring (environment / process / handoff)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def axis_environment(*, root: Path, vibe: Any) -> dict[str, Any]:
    """Score how well the repo is set up for AI to work in."""
    score = 0
    weaknesses: list[str] = []
    if (root / "CLAUDE.md").exists():
        score += 30
    else:
        weaknesses.append("CLAUDE.md 없음")
    if (root / "AGENTS.md").exists():
        score += 15
    if (root / ".claude").exists():
        score += 15
    if (root / "openspec").exists():
        score += 25
    else:
        weaknesses.append("OpenSpec 명세 체계 없음")
    if vibe.confidence == "high":
        score += 15
    elif vibe.confidence == "medium":
        score += 8
    score = min(score, 100)
    return {
        "name": "environment",
        "label": "환경 구축",
        "score": score,
        "weaknesses": weaknesses[:3],
    }


def axis_process(*, history: Any, hotspots: Any, quality: Any) -> dict[str, Any]:
    """Score whether AI development stayed on track during build."""
    score = 50
    weaknesses: list[str] = []
    if history.available and history.commit_count > 0:
        process_ratio = len(history.process_commits) / max(1, history.commit_count)
        if process_ratio >= 0.15:
            score += 25
        elif process_ratio >= 0.05:
            score += 10
        else:
            weaknesses.append("프로세스 커밋 비율이 매우 낮음")

        type_dist = {e.label: int(e.value) for e in history.type_distribution}
        feat_count = type_dist.get("feat", 0)
        fix_count = type_dist.get("fix", 0)
        if feat_count > 0:
            fix_ratio = fix_count / feat_count
            if fix_ratio > 0.6:
                score -= 20
                weaknesses.append(
                    f"fix 대비 feat 비율이 높음 (fix {fix_count}/feat {feat_count})"
                )
            elif fix_ratio > 0.3:
                score -= 8
    else:
        weaknesses.append("git history 없음 — 과정 추론 불가")
        score -= 10

    if hotspots.summary.hotspot >= 10:
        score -= 15
        weaknesses.append(f"Hotspot {hotspots.summary.hotspot}개 누적")

    score = max(0, min(score, 100))
    _ = quality  # reserved for future quality-driven adjustments
    return {
        "name": "process",
        "label": "개발 과정 깔끔함",
        "score": score,
        "weaknesses": weaknesses[:3],
    }


def axis_handoff(*, root: Path, quality: Any) -> dict[str, Any]:
    """Score whether the next AI session can take over without context loss."""
    score = 0
    weaknesses: list[str] = []
    if (root / "docs" / "validation").exists():
        score += 30
    else:
        weaknesses.append("검증 문서(docs/validation/) 없음")
    if (root / "docs" / "vibe-coding").exists():
        score += 25
    else:
        weaknesses.append("회고 문서(docs/vibe-coding/) 없음")
    if (root / "docs" / "handoff").exists():
        score += 15
    if (root / "docs" / "intent.md").exists():
        score += 15
    else:
        weaknesses.append("의도 문서(docs/intent.md) 없음")

    test_dim = quality.dimensions.get("test")
    if test_dim and test_dim.grade in {"A", "B"}:
        score += 15
    elif test_dim and test_dim.grade in {"D", "F"}:
        weaknesses.append(f"테스트 등급 {test_dim.grade}")

    score = min(score, 100)
    return {
        "name": "handoff",
        "label": "이어받기 가능성",
        "score": score,
        "weaknesses": weaknesses[:3],
    }
