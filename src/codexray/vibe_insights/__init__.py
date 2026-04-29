"""Vibe coding insights — auto-detection, three-axis evaluation, timeline.

This module reads file-system signals, vibe-coding evidence, and git history to
answer one core question: *did the team do vibe coding well, and if so, where
are the gaps?* It returns a JSON-friendly dict consumed by the web Briefing
payload.

Public surface:
- ``build_vibe_insights(root, vibe, quality, hotspots, history, ai_key_insight)``
"""

from __future__ import annotations

from .builder import build_vibe_insights

__all__ = ["build_vibe_insights"]
