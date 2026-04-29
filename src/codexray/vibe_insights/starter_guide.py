"""First-step guide for repos that don't yet show vibe-coding signals."""

from __future__ import annotations

from typing import Any


def build_starter_guide(*, quality: Any, hotspots: Any) -> list[dict[str, str]]:
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
