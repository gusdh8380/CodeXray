from __future__ import annotations

from collections.abc import Iterable

from ..entrypoints.types import EntrypointResult
from ..hotspots.types import HotspotsReport
from ..inventory import Row
from ..metrics.types import MetricsResult
from ..quality.types import QualityReport
from .types import Action, Strength, SummaryResult, Weakness

SCHEMA_VERSION = 1
TOP_N = 3

_TIER_F = 0
_TIER_D = 1
_TIER_STRUCTURAL = 2
_TIER_A = 3
_TIER_B = 4
_TIER_OTHER = 9

_ACTION_FOR_DIMENSION = {
    "test": "characterization test 우선 보강",
    "coupling": "결합도 분해 (책임 분리)",
    "documentation": "문서화 진입점 작성",
    "cohesion": "모듈 책임 재정렬",
}


def build_summary(
    quality: QualityReport,
    hotspots: HotspotsReport,
    metrics: MetricsResult,
    entrypoints: EntrypointResult,  # noqa: ARG001 — reserved for future rules.
    inventory: Iterable[Row],  # noqa: ARG001 — reserved for future rules.
) -> SummaryResult:
    strengths_pool = _collect_strengths(quality, hotspots, metrics)
    weaknesses_pool = _collect_weaknesses(quality, hotspots, metrics)

    strengths = sorted(strengths_pool, key=_strength_sort_key)[:TOP_N]
    sorted_weaknesses = sorted(weaknesses_pool, key=_weakness_sort_key)
    weaknesses = sorted_weaknesses[:TOP_N]
    actions = _derive_actions(sorted_weaknesses)

    return SummaryResult(
        schema_version=SCHEMA_VERSION,
        strengths=tuple(strengths),
        weaknesses=tuple(weaknesses),
        actions=tuple(actions),
    )


def _collect_strengths(
    quality: QualityReport,
    hotspots: HotspotsReport,
    metrics: MetricsResult,
) -> list[Strength]:
    items: list[Strength] = []

    for name, dim in sorted(quality.dimensions.items()):
        if dim.grade in {"A", "B"}:
            items.append(
                Strength(
                    category="quality",
                    text=f"{name} 차원 {dim.grade} 등급",
                    evidence={
                        "dimension": name,
                        "grade": dim.grade,
                        "score": dim.score,
                    },
                )
            )

    summary = hotspots.summary
    total = (
        summary.hotspot
        + summary.active_stable
        + summary.neglected_complex
        + summary.stable
    )
    if total > 0 and (summary.stable / total) >= 0.5:
        ratio = int(round(100 * summary.stable / total))
        items.append(
            Strength(
                category="hotspots",
                text=f"안정 영역(stable) 비중 {ratio}%",
                evidence={
                    "stable": summary.stable,
                    "total": total,
                    "ratio_pct": ratio,
                },
            )
        )

    if metrics.graph.is_dag:
        items.append(
            Strength(
                category="metrics",
                text="순환 의존 없음 (DAG)",
                evidence={"node_count": metrics.graph.node_count},
            )
        )

    sorted_files = sorted(
        hotspots.files,
        key=lambda f: (-(f.change_count * f.coupling), f.path),
    )
    if sorted_files and sorted_files[0].category == "active_stable":
        top = sorted_files[0]
        items.append(
            Strength(
                category="hotspots",
                text=f"Top 활동 파일이 active_stable: {top.path}",
                evidence={
                    "path": top.path,
                    "change_count": top.change_count,
                    "coupling": top.coupling,
                },
            )
        )

    return items


def _collect_weaknesses(
    quality: QualityReport,
    hotspots: HotspotsReport,
    metrics: MetricsResult,
) -> list[Weakness]:
    items: list[Weakness] = []

    for name, dim in sorted(quality.dimensions.items()):
        if dim.grade in {"D", "F"}:
            items.append(
                Weakness(
                    category="quality",
                    text=f"{name} 차원 {dim.grade} 등급",
                    evidence={
                        "dimension": name,
                        "grade": dim.grade,
                        "score": dim.score,
                    },
                )
            )

    nc = [f for f in hotspots.files if f.category == "neglected_complex"]
    if nc:
        nc.sort(key=lambda f: (-f.coupling, f.path))
        top = nc[0]
        items.append(
            Weakness(
                category="hotspots",
                text=f"neglected_complex 파일 발견: {top.path}",
                evidence={
                    "path": top.path,
                    "coupling": top.coupling,
                    "count": hotspots.summary.neglected_complex,
                },
            )
        )

    if metrics.graph.largest_scc_size > 1:
        items.append(
            Weakness(
                category="metrics",
                text=f"순환 의존 발견 (SCC 크기 {metrics.graph.largest_scc_size})",
                evidence={
                    "largest_scc_size": metrics.graph.largest_scc_size,
                    "scc_count": metrics.graph.scc_count,
                },
            )
        )

    hotspots_only = [f for f in hotspots.files if f.category == "hotspot"]
    if hotspots_only:
        hotspots_only.sort(key=lambda f: (-(f.change_count * f.coupling), f.path))
        top = hotspots_only[0]
        items.append(
            Weakness(
                category="hotspots",
                text=f"Top hotspot 위험: {top.path}",
                evidence={
                    "path": top.path,
                    "change_count": top.change_count,
                    "coupling": top.coupling,
                    "priority": top.change_count * top.coupling,
                },
            )
        )

    return items


def _derive_actions(sorted_weaknesses: list[Weakness]) -> list[Action]:
    actions: list[Action] = []
    seen_keys: set[str] = set()
    for weakness in sorted_weaknesses:
        action_text, action_key = _action_for(weakness)
        if action_text is None or action_key is None or action_key in seen_keys:
            continue
        seen_keys.add(action_key)
        actions.append(Action(text=action_text, evidence=dict(weakness.evidence)))
        if len(actions) >= TOP_N:
            break
    return actions


def _action_for(weakness: Weakness) -> tuple[str | None, str | None]:
    if weakness.category == "quality":
        dim = weakness.evidence.get("dimension")
        if not isinstance(dim, str):
            return None, None
        text = _ACTION_FOR_DIMENSION.get(dim)
        if text is None:
            return None, None
        return text, f"quality:{dim}"
    if weakness.category == "metrics":
        return "최대 SCC 끊기 (한 모듈 추출)", "metrics:scc"
    if weakness.category == "hotspots":
        if "priority" in weakness.evidence:
            return "Top hotspot에 테스트 + 책임 분리", "hotspot:top"
        return "neglected_complex 파일 소유권·테스트 정리", "hotspot:neglected"
    return None, None


def _strength_sort_key(item: Strength) -> tuple[int, int, str]:
    grade = item.evidence.get("grade")
    if grade == "A":
        tier = _TIER_A
    elif grade == "B":
        tier = _TIER_B
    else:
        tier = _TIER_STRUCTURAL
    score = item.evidence.get("score")
    score_neg = -int(score) if isinstance(score, int) else 0
    return (tier, score_neg, item.text)


def _weakness_sort_key(item: Weakness) -> tuple[int, int, str]:
    grade = item.evidence.get("grade")
    if grade == "F":
        tier = _TIER_F
    elif grade == "D":
        tier = _TIER_D
    elif item.category in {"hotspots", "metrics"}:
        tier = _TIER_STRUCTURAL
    else:
        tier = _TIER_OTHER
    score = item.evidence.get("score")
    score_asc = int(score) if isinstance(score, int) else 0
    return (tier, score_asc, item.text)
