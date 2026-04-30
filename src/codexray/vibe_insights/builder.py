"""Orchestrate detection + axes + timeline + narrative into one dict payload."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .axes import (
    axis_continuity,
    axis_intent,
    axis_verification,
    build_process_proxies,
    get_blind_spots,
)
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

    Returns either a *detected* shape with three axes, blind_spots,
    process_proxies, timeline, and narrative, or a *not-detected* shape with
    a starter guide.
    """
    detected = detect_vibe_coding(root=root, vibe=vibe, history=history)
    if not detected:
        return {
            "detected": False,
            "starter_guide": build_starter_guide(quality=quality, hotspots=hotspots),
            "blind_spots": get_blind_spots(),
        }

    axes = [
        axis_intent(root=root),
        axis_verification(root=root),
        axis_continuity(root=root, history=history),
    ]
    timeline = build_timeline(history=history)
    process_proxies = build_process_proxies(history=history, hotspots=hotspots)
    blind_spots = get_blind_spots()
    ai_narrative = ai_key_insight or fallback_narrative(axes)
    _ = vibe  # Reserved — detection used `vibe` already; kept in signature for callers.
    _ = quality  # Reserved for future quality-driven adjustments.
    return {
        "detected": True,
        "axes": axes,
        "timeline": timeline,
        "ai_narrative": ai_narrative,
        "blind_spots": blind_spots,
        "process_proxies": process_proxies,
    }
