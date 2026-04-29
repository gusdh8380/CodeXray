"""Three-axis vibe-coding scoring (environment / process / handoff).

Each axis returns a breakdown list so the SPA can show *why* a score is what
it is — every check item carries its delta and whether the repo satisfied it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _item(label: str, delta: int, satisfied: bool, hint: str = "") -> dict[str, Any]:
    return {"label": label, "delta": delta, "satisfied": satisfied, "hint": hint}


def axis_environment(*, root: Path, vibe: Any) -> dict[str, Any]:
    """Score how well the repo is set up for AI to work in."""
    breakdown: list[dict[str, Any]] = []
    weaknesses: list[str] = []

    has_claude = (root / "CLAUDE.md").exists()
    breakdown.append(
        _item(
            "CLAUDE.md (에이전트 지침서)",
            30,
            has_claude,
            "AI가 매번 프로젝트 맥락을 다시 파악하지 않게 해주는 가장 중요한 파일",
        )
    )
    if not has_claude:
        weaknesses.append("CLAUDE.md 없음")

    has_agents = (root / "AGENTS.md").exists()
    breakdown.append(
        _item(
            "AGENTS.md (에이전트별 역할 분리)",
            15,
            has_agents,
            "여러 AI 에이전트를 함께 쓰는 경우 누가 뭘 하는지 분리한 문서",
        )
    )

    has_claude_dir = (root / ".claude").exists()
    breakdown.append(
        _item(
            ".claude/ 설정 폴더",
            15,
            has_claude_dir,
            "Claude Code의 도구 권한·환경 설정",
        )
    )

    has_openspec = (root / "openspec").exists()
    breakdown.append(
        _item(
            "openspec/ 명세 체계",
            25,
            has_openspec,
            "변경마다 명세부터 쓰는 구조화된 워크플로우",
        )
    )
    if not has_openspec:
        weaknesses.append("OpenSpec 명세 체계 없음")

    confidence_label, confidence_delta = _confidence_score(vibe.confidence)
    breakdown.append(
        _item(
            f"vibe 분석기 신뢰도 ({confidence_label})",
            confidence_delta,
            confidence_delta > 0,
            "파일·git 흔적 종합 신뢰도 (낮음/중간/높음)",
        )
    )

    score = sum(item["delta"] for item in breakdown if item["satisfied"])
    score = max(0, min(score, 100))
    return {
        "name": "environment",
        "label": "환경 구축",
        "score": score,
        "weaknesses": weaknesses[:3],
        "breakdown": breakdown,
    }


def _confidence_score(confidence: str) -> tuple[str, int]:
    if confidence == "high":
        return "높음", 15
    if confidence == "medium":
        return "중간", 8
    return "낮음", 0


def axis_process(*, history: Any, hotspots: Any, quality: Any) -> dict[str, Any]:
    """Score whether AI development stayed on track during build."""
    breakdown: list[dict[str, Any]] = []
    weaknesses: list[str] = []
    score = 50  # baseline
    breakdown.append(
        _item(
            "기본 점수",
            50,
            True,
            "git history가 없어도 기본 50점에서 시작",
        )
    )

    if history.available and history.commit_count > 0:
        process_ratio = len(history.process_commits) / max(1, history.commit_count)
        if process_ratio >= 0.15:
            breakdown.append(
                _item(
                    f"프로세스 커밋 비율 충분 ({process_ratio*100:.0f}%)",
                    25,
                    True,
                    "명세·검증·회고 같은 프로세스 커밋이 전체의 15% 이상",
                )
            )
            score += 25
        elif process_ratio >= 0.05:
            breakdown.append(
                _item(
                    f"프로세스 커밋 비율 부분적 ({process_ratio*100:.0f}%)",
                    10,
                    True,
                    "5~15% 사이 — 시작은 했지만 더 자주 누적되어야 함",
                )
            )
            score += 10
        else:
            breakdown.append(
                _item(
                    f"프로세스 커밋 비율 낮음 ({process_ratio*100:.0f}%)",
                    25,
                    False,
                    "15% 이상이면 가산. 명세/검증/회고 커밋이 거의 없으면 0",
                )
            )
            weaknesses.append("프로세스 커밋 비율이 매우 낮음")

        type_dist = {e.label: int(e.value) for e in history.type_distribution}
        feat_count = type_dist.get("feat", 0)
        fix_count = type_dist.get("fix", 0)
        if feat_count > 0:
            fix_ratio = fix_count / feat_count
            if fix_ratio > 0.6:
                breakdown.append(
                    _item(
                        f"fix 비율 과도 (fix {fix_count}/feat {feat_count})",
                        -20,
                        True,
                        "fix가 feat의 60%를 넘으면 AI가 자주 빗나갔다는 신호",
                    )
                )
                score -= 20
                weaknesses.append(
                    f"fix 대비 feat 비율이 높음 (fix {fix_count}/feat {feat_count})"
                )
            elif fix_ratio > 0.3:
                breakdown.append(
                    _item(
                        f"fix 비율 보통 (fix {fix_count}/feat {feat_count})",
                        -8,
                        True,
                        "30~60% 사이 — 큰 문제는 아니지만 회고 거리",
                    )
                )
                score -= 8
            else:
                breakdown.append(
                    _item(
                        f"fix 비율 양호 (fix {fix_count}/feat {feat_count})",
                        0,
                        True,
                        "30% 미만이면 AI가 의도대로 잘 달린 신호",
                    )
                )
    else:
        breakdown.append(
            _item(
                "git history 없음",
                -10,
                False,
                "히스토리가 있어야 과정 추론 가능",
            )
        )
        weaknesses.append("git history 없음 — 과정 추론 불가")
        score -= 10

    if hotspots.summary.hotspot >= 10:
        breakdown.append(
            _item(
                f"Hotspot 누적 ({hotspots.summary.hotspot}개)",
                -15,
                True,
                "Hotspot이 10개 이상이면 자주 변경 + 결합 높은 파일이 누적된 상태",
            )
        )
        score -= 15
        weaknesses.append(f"Hotspot {hotspots.summary.hotspot}개 누적")
    else:
        breakdown.append(
            _item(
                f"Hotspot 적음 ({hotspots.summary.hotspot}개)",
                0,
                True,
                "10개 미만 — 변경이 분산되어 있다는 신호",
            )
        )

    score = max(0, min(score, 100))
    _ = quality  # reserved for future quality-driven adjustments
    return {
        "name": "process",
        "label": "개발 과정 깔끔함",
        "score": score,
        "weaknesses": weaknesses[:3],
        "breakdown": breakdown,
    }


def axis_handoff(*, root: Path, quality: Any) -> dict[str, Any]:
    """Score whether the next AI session can take over without context loss."""
    breakdown: list[dict[str, Any]] = []
    weaknesses: list[str] = []

    has_validation = (root / "docs" / "validation").exists()
    breakdown.append(
        _item(
            "docs/validation/ (검증 문서)",
            30,
            has_validation,
            "이 코드가 진짜 동작하는지 다음 세션이 확인할 수 있게 하는 핵심 문서",
        )
    )
    if not has_validation:
        weaknesses.append("검증 문서(docs/validation/) 없음")

    has_retro = (root / "docs" / "vibe-coding").exists()
    breakdown.append(
        _item(
            "docs/vibe-coding/ (회고 문서)",
            25,
            has_retro,
            "어떤 결정을 왜 했는지 다음 세션이 알 수 있게 함",
        )
    )
    if not has_retro:
        weaknesses.append("회고 문서(docs/vibe-coding/) 없음")

    has_handoff = (root / "docs" / "handoff").exists()
    breakdown.append(
        _item(
            "docs/handoff/ (인수인계 문서)",
            15,
            has_handoff,
            "현재 어디까지 했고 다음에 뭘 해야 하는지의 메모",
        )
    )

    has_intent = (root / "docs" / "intent.md").exists()
    breakdown.append(
        _item(
            "docs/intent.md (의도 문서)",
            15,
            has_intent,
            "Why를 명문화한 문서. 의도 drift 방지의 핵심",
        )
    )
    if not has_intent:
        weaknesses.append("의도 문서(docs/intent.md) 없음")

    test_dim = quality.dimensions.get("test")
    test_grade = test_dim.grade if test_dim else None
    if test_grade in {"A", "B"}:
        breakdown.append(
            _item(
                f"테스트 등급 양호 ({test_grade})",
                15,
                True,
                "다음 세션이 수정해도 깨졌는지 자동 확인 가능",
            )
        )
    elif test_grade in {"D", "F"}:
        breakdown.append(
            _item(
                f"테스트 등급 낮음 ({test_grade})",
                15,
                False,
                "A/B면 가산. 테스트가 부실하면 다음 세션이 안전하게 이어받기 어려움",
            )
        )
        weaknesses.append(f"테스트 등급 {test_grade}")
    else:
        breakdown.append(
            _item(
                "테스트 차원 미감지",
                15,
                False,
                "테스트 분석 결과 없음",
            )
        )

    score = sum(item["delta"] for item in breakdown if item["satisfied"])
    score = max(0, min(score, 100))
    return {
        "name": "handoff",
        "label": "이어받기 가능성",
        "score": score,
        "weaknesses": weaknesses[:3],
        "breakdown": breakdown,
    }
