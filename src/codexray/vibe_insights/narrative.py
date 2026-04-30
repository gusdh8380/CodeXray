"""Deterministic fallback narrative when no AI synthesis is available."""

from __future__ import annotations

from typing import Any

_STATE_RANK = {"unknown": 0, "weak": 1, "moderate": 2, "strong": 3}


def fallback_narrative(axes: list[dict[str, Any]]) -> str:
    if not axes:
        return "바이브코딩 평가 데이터가 부족합니다."

    sorted_axes = sorted(axes, key=lambda a: _STATE_RANK.get(a.get("state", "unknown"), 0))
    weakest = sorted_axes[0]
    strongest = sorted_axes[-1]

    weakest_state = weakest.get("state", "unknown")
    strongest_state = strongest.get("state", "unknown")

    if all(a.get("state") == "strong" for a in axes):
        return (
            "의도 / 검증 / 이어받기 세 축이 모두 강함. "
            "이 패턴을 다음 변경에서도 유지하세요."
        )

    return (
        f"{strongest['label']} 축이 '{strongest_state}' 로 가장 잘 갖춰져 있고, "
        f"{weakest['label']} 축이 '{weakest_state}' 로 가장 약합니다. "
        "다음 행동은 약한 축부터 메우는 방향이 효과적입니다."
    )
