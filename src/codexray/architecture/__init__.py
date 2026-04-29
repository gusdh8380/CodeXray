"""Architecture view — module clustering + layer assignment + module flow.

This module turns the existing graph + hotspots data into a structure-aware
payload the SPA can render in multiple visual styles (force, layered, hull,
bundling). Module detection comes from directory structure, layers come from
topological sort with SCC-contract for cycle handling.
"""

from __future__ import annotations

from .builder import build_architecture_view

__all__ = ["build_architecture_view"]
