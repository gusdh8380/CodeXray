"""Orchestrate detection + axes + timeline + narrative into one dict payload."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .axes import axis_environment, axis_handoff, axis_process
from .detection import detect_vibe_coding
from .narrative import fallback_narrative
from .starter_guide import build_starter_guide
from .timeline import build_timeline


def build_vibe_insights(
    *,
    root: Path,
    vibe: Any,
    quality: Any,
    hotspots: Any,
    history: Any,
    ai_key_insight: str | None = None,
) -> dict[str, Any]:
    """Build the JSON payload consumed by the React VibeInsightsSection.

    Returns either a *detected* shape with three axes, timeline, and narrative,
    or a *not-detected* shape with a starter guide.
    """
    detected = detect_vibe_coding(root=root, vibe=vibe, history=history)
    if not detected:
        return {
            "detected": False,
            "starter_guide": build_starter_guide(quality=quality, hotspots=hotspots),
        }

    axes = [
        axis_environment(root=root, vibe=vibe),
        axis_process(history=history, hotspots=hotspots, quality=quality),
        axis_handoff(root=root, quality=quality),
    ]
    timeline = build_timeline(history=history)
    ai_narrative = ai_key_insight or fallback_narrative(axes)
    return {
        "detected": True,
        "axes": axes,
        "timeline": timeline,
        "ai_narrative": ai_narrative,
    }
