"""Deterministic fallback narrative when no AI synthesis is available."""

from __future__ import annotations

from typing import Any


def fallback_narrative(axes: list[dict[str, Any]]) -> str:
    sorted_axes = sorted(axes, key=lambda a: a["score"])
    weakest = sorted_axes[0]
    strongest = sorted_axes[-1]
    return (
        f"{strongest['label']}({strongest['score']})은 비교적 잘 갖춰져 있지만, "
        f"{weakest['label']}({weakest['score']})에서 약점이 보입니다. "
        "다음 행동은 이 약점부터 메우는 방향이 효과적입니다."
    )
