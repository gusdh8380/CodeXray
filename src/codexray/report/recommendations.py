from __future__ import annotations

from ..entrypoints.types import EntrypointResult
from ..hotspots.types import HotspotsReport
from ..metrics.types import MetricsResult
from ..quality.types import QualityReport
from .types import Recommendation

_F = "F"
_D = "D"
_LIMIT = 5


def generate(
    quality: QualityReport,
    metrics: MetricsResult,
    hotspots: HotspotsReport,
    entrypoints: EntrypointResult,
) -> list[Recommendation]:
    out: list[Recommendation] = []

    top = _top_hotspot(hotspots)
    if top is not None:
        out.append(
            Recommendation(
                priority=100,
                text=(
                    f"Top hotspot: `{top.path}` (change={top.change_count}, "
                    f"coupling={top.coupling}). 책임 분리·테스트 추가 우선."
                ),
            )
        )

    for name, dim in sorted(quality.dimensions.items()):
        if dim.grade == _F:
            out.append(
                Recommendation(
                    priority=80,
                    text=f"`{name}` grade F (score {dim.score}). detail: {dim.detail}",
                )
            )

    if not metrics.graph.is_dag:
        out.append(
            Recommendation(
                priority=60,
                text=(
                    f"Cycle detected — largest SCC size {metrics.graph.largest_scc_size}, "
                    f"{metrics.graph.scc_count} SCCs total. 사이클 분해 검토."
                ),
            )
        )

    for name, dim in sorted(quality.dimensions.items()):
        if dim.grade == _D:
            out.append(
                Recommendation(
                    priority=40,
                    text=f"`{name}` grade D (score {dim.score}). detail: {dim.detail}",
                )
            )

    if len(entrypoints.entrypoints) == 0:
        out.append(
            Recommendation(
                priority=20,
                text=(
                    "No entrypoints detected. 도달성 분석이 어려움 — "
                    "main guard, package script, MonoBehaviour 라이프사이클 등 추가 검토."
                ),
            )
        )

    out.sort(key=lambda r: (-r.priority, r.text))
    return out[:_LIMIT]


def _top_hotspot(hotspots: HotspotsReport):
    candidates = [f for f in hotspots.files if f.category == "hotspot"]
    if not candidates:
        return None
    candidates.sort(key=lambda f: (-(f.change_count * f.coupling), f.path))
    return candidates[0]
