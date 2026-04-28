"""Build the React-friendly BriefingPayload JSON from existing analyzers.

This module bridges the deterministic analyzers + AI briefing result + git history
into the 5-section + vibe-insights shape consumed by the React SPA.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..briefing import build_codebase_briefing
from ..briefing.git_history import build_git_history
from ..hotspots import build_hotspots
from ..inventory import aggregate
from ..quality import build_quality
from ..vibe import build_vibe_coding_report
from .ai_briefing import AIBriefingResult


SCHEMA_VERSION = 1


_PROCESS_FILE_SIGNALS = {
    "CLAUDE.md": ("agent", "에이전트 지침"),
    "AGENTS.md": ("agent", "에이전트 지침"),
    ".claude": ("agent", ".claude 설정"),
    ".omc": ("agent", ".omc 메모리"),
    "openspec": ("spec", "OpenSpec 명세"),
    "docs/intent.md": ("spec", "의도 문서"),
    "docs/validation": ("validation", "검증 문서"),
    "docs/vibe-coding": ("retro", "회고록"),
    "docs/handoff": ("retro", "인수인계"),
}


def build_briefing_payload(root: Path, ai: AIBriefingResult | None) -> dict[str, Any]:
    """Build the JSON payload consumed by the React Briefing screen."""
    resolved = root.resolve()
    inventory = list(aggregate(resolved))
    quality = build_quality(resolved)
    hotspots = build_hotspots(resolved)
    vibe = build_vibe_coding_report(resolved)
    history = build_git_history(resolved)
    deterministic = build_codebase_briefing(resolved)

    languages = ", ".join(row.language for row in inventory) or "감지된 언어 없음"
    total_files = sum(row.file_count for row in inventory)
    total_loc = sum(row.loc for row in inventory)
    grade = quality.overall.grade or "N/A"
    score = quality.overall.score if quality.overall.score is not None else 0
    top_hotspot = next((f for f in hotspots.files if f.category == "hotspot"), None)
    top_hotspot_path = top_hotspot.path if top_hotspot else "N/A"
    repo_name = resolved.name

    what = _build_what(
        repo_name=repo_name,
        languages=languages,
        total_files=total_files,
        total_loc=total_loc,
        grade=grade,
        ai_executive=ai.executive if ai else None,
    )
    how_built = _build_how_built(
        deterministic=deterministic,
        ai_architecture=ai.architecture if ai else None,
    )
    current_state = _build_current_state(
        grade=grade,
        score=score,
        hotspot_count=hotspots.summary.hotspot,
        top_hotspot=top_hotspot_path,
        ai_quality=ai.quality_risk if ai else None,
    )
    vibe_insights = _build_vibe_insights(
        root=resolved,
        vibe=vibe,
        quality=quality,
        hotspots=hotspots,
        history=history,
        ai_key_insight=ai.key_insight if ai else None,
    )
    next_actions = _build_next_actions(
        ai_actions=list(ai.next_actions) if ai else [],
        grade=grade,
        hotspot_count=hotspots.summary.hotspot,
        top_hotspot=top_hotspot_path,
        vibe_detected=vibe_insights["detected"],
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "path": str(resolved),
        "what": what,
        "how_built": how_built,
        "current_state": current_state,
        "vibe_insights": vibe_insights,
        "next_actions": next_actions,
        "ai_used": ai is not None and not ai.fallback,
    }


def _build_what(
    *,
    repo_name: str,
    languages: str,
    total_files: int,
    total_loc: int,
    grade: str,
    ai_executive: str | None,
) -> dict[str, Any]:
    narrative = ai_executive or (
        f"{repo_name}은 {languages} 기반의 코드베이스로, "
        f"총 {total_files}개 파일·{total_loc:,} LoC 규모입니다. "
        f"현재 종합 품질 등급은 {grade}입니다."
    )
    return {
        "id": "what",
        "title": "이게 뭐야",
        "narrative": narrative,
        "metrics": [
            {"label": "파일 수", "value": str(total_files)},
            {"label": "LoC", "value": f"{total_loc:,}"},
            {"label": "품질 등급", "value": grade},
        ],
    }


def _build_how_built(*, deterministic: Any, ai_architecture: str | None) -> dict[str, Any]:
    arch_card = deterministic.architecture[0] if deterministic.architecture else None
    fallback = arch_card.text if arch_card else "구조 분석 데이터를 가져오지 못했습니다."
    return {
        "id": "how_built",
        "title": "어떻게 만들어졌나",
        "narrative": ai_architecture or fallback,
        "metrics": [
            {"label": e.label, "value": e.value}
            for e in (arch_card.evidence[:3] if arch_card else [])
        ],
        "deep_link": {"label": "구조 그래프 보기", "tab": "graph"},
    }


def _build_current_state(
    *,
    grade: str,
    score: int,
    hotspot_count: int,
    top_hotspot: str,
    ai_quality: str | None,
) -> dict[str, Any]:
    if ai_quality:
        narrative = ai_quality
    else:
        narrative = (
            f"품질 등급은 {grade}({score})이고 hotspot은 {hotspot_count}개입니다. "
            f"가장 먼저 살펴볼 파일은 {top_hotspot}입니다."
        )
    return {
        "id": "current_state",
        "title": "지금 상태",
        "narrative": narrative,
        "metrics": [
            {"label": "등급", "value": grade},
            {"label": "Hotspot", "value": str(hotspot_count)},
        ],
        "deep_link": {"label": "Quality 탭에서 자세히", "tab": "quality"},
    }


def _build_vibe_insights(
    *,
    root: Path,
    vibe: Any,
    quality: Any,
    hotspots: Any,
    history: Any,
    ai_key_insight: str | None,
) -> dict[str, Any]:
    detected = _detect_vibe_coding(root=root, vibe=vibe, history=history)
    if not detected:
        return {
            "detected": False,
            "starter_guide": _build_starter_guide(quality=quality, hotspots=hotspots),
        }

    axes = [
        _axis_environment(root=root, vibe=vibe),
        _axis_process(history=history, hotspots=hotspots, quality=quality),
        _axis_handoff(root=root, quality=quality),
    ]
    timeline = _build_timeline(history=history)
    ai_narrative = ai_key_insight or _fallback_vibe_narrative(axes)
    return {
        "detected": True,
        "axes": axes,
        "timeline": timeline,
        "ai_narrative": ai_narrative,
    }


def _detect_vibe_coding(*, root: Path, vibe: Any, history: Any) -> bool:
    strong_paths = ["CLAUDE.md", "AGENTS.md", ".claude", ".omc", "openspec"]
    for rel in strong_paths:
        if (root / rel).exists():
            return True
    if vibe.confidence in {"medium", "high"}:
        return True
    if history.process_commits:
        return True
    if any("Co-Authored-By: Claude" in (c.subject or "") for c in history.recent_commits):
        return True
    return False


def _axis_environment(*, root: Path, vibe: Any) -> dict[str, Any]:
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


def _axis_process(*, history: Any, hotspots: Any, quality: Any) -> dict[str, Any]:
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
    return {
        "name": "process",
        "label": "개발 과정 깔끔함",
        "score": score,
        "weaknesses": weaknesses[:3],
    }


def _axis_handoff(*, root: Path, quality: Any) -> dict[str, Any]:
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


def _build_timeline(*, history: Any) -> list[dict[str, Any]]:
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


def _fallback_vibe_narrative(axes: list[dict[str, Any]]) -> str:
    sorted_axes = sorted(axes, key=lambda a: a["score"])
    weakest = sorted_axes[0]
    strongest = sorted_axes[-1]
    return (
        f"{strongest['label']}({strongest['score']})은 비교적 잘 갖춰져 있지만, "
        f"{weakest['label']}({weakest['score']})에서 약점이 보입니다. "
        "다음 행동은 이 약점부터 메우는 방향이 효과적입니다."
    )


def _build_starter_guide(*, quality: Any, hotspots: Any) -> list[dict[str, str]]:
    grade = quality.overall.grade or "N/A"
    return [
        {
            "action": "프로젝트에 CLAUDE.md 작성",
            "reason": (
                "AI 에이전트가 이 레포의 목적·스택·관행을 매번 다시 파악하지 않고 바로 일을 "
                "이어받을 수 있게 하려면 가장 먼저 갖춰야 할 파일입니다."
            ),
        },
        {
            "action": "docs/intent.md 로 의도 명문화",
            "reason": (
                "Why를 글로 남겨두지 않으면 코드만 보고 의도를 추론하느라 AI가 빗나가기 "
                f"쉽습니다. 현재 등급 {grade}, hotspot {hotspots.summary.hotspot}개 상태에서 "
                "의도 명확화는 다음 변경의 위험을 크게 줄입니다."
            ),
        },
        {
            "action": "openspec 도입으로 변경마다 명세부터",
            "reason": (
                "코드 변경 전에 명세를 작성하면 AI 협업의 결과물이 일관되게 누적됩니다. "
                "처음에는 작은 변경 한 건부터 시작해도 효과가 있습니다."
            ),
        },
    ]


def _build_next_actions(
    *,
    ai_actions: list[str],
    grade: str,
    hotspot_count: int,
    top_hotspot: str,
    vibe_detected: bool,
) -> list[dict[str, str]]:
    if ai_actions:
        return [_format_ai_action(a, grade, hotspot_count, top_hotspot) for a in ai_actions[:3]]

    actions: list[dict[str, str]] = []
    if hotspot_count > 0 and top_hotspot != "N/A":
        actions.append(
            {
                "action": f"{top_hotspot} 부터 리뷰",
                "reason": (
                    "변경 빈도와 결합도가 모두 높아 다음 기능 추가 시 가장 먼저 깨질 위험이 "
                    "있는 파일입니다."
                ),
                "evidence": f"Hotspot {hotspot_count}개 중 최상위, 우선순위 1위",
            }
        )
    if grade in {"D", "F"}:
        actions.append(
            {
                "action": "낮은 품질 등급의 원인 차원부터 보강",
                "reason": (
                    "전체 등급이 낮을 때 우선 어떤 차원이 가장 약한지 식별하면 가장 적은 "
                    "노력으로 평균을 올릴 수 있습니다."
                ),
                "evidence": f"종합 등급 {grade}",
            }
        )
    if not vibe_detected:
        actions.append(
            {
                "action": "CLAUDE.md 한 페이지부터 작성",
                "reason": "AI 협업 흔적이 없는 상태에서 가장 적은 비용으로 시작할 수 있는 첫 단계입니다.",
                "evidence": "바이브코딩 신호 미감지",
            }
        )
    if not actions:
        actions.append(
            {
                "action": "프로젝트 사용자 인터뷰로 의도 검증",
                "reason": "현재 구조와 품질이 안정적이므로 다음 우선순위는 만드는 사람과 쓰는 사람의 합의 검증입니다.",
                "evidence": "주요 위험 신호 없음",
            }
        )
    return actions[:3]


def _format_ai_action(
    raw: str,
    grade: str,
    hotspot_count: int,
    top_hotspot: str,
) -> dict[str, str]:
    text = raw.strip()
    return {
        "action": text[:120],
        "reason": "AI 해석에서 도출된 다음 행동입니다.",
        "evidence": (
            f"등급 {grade}, Hotspot {hotspot_count}개"
            + (f", top {top_hotspot}" if top_hotspot != "N/A" else "")
        ),
    }
