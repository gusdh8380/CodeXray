from __future__ import annotations

from codexray.entrypoints.types import EntrypointResult
from codexray.hotspots.types import (
    FileHotspot,
    HotspotsReport,
    Summary,
    Thresholds,
)
from codexray.metrics.types import GraphMetrics, MetricsResult
from codexray.quality.types import DimensionScore, OverallScore, QualityReport
from codexray.summary import build_summary
from codexray.summary.types import SummaryResult


def _quality(grades: dict[str, str], scores: dict[str, int] | None = None) -> QualityReport:
    scores = scores or {}
    dims = {
        name: DimensionScore(score=scores.get(name, 50), grade=grade, detail={})
        for name, grade in grades.items()
    }
    return QualityReport(
        schema_version=1,
        overall=OverallScore(score=50, grade="C"),
        dimensions=dims,
    )


_EMPTY_HOTSPOTS_SUMMARY = Summary(0, 0, 0, 0)


def _hotspots(
    *,
    files: tuple[FileHotspot, ...] = (),
    summary: Summary = _EMPTY_HOTSPOTS_SUMMARY,
) -> HotspotsReport:
    return HotspotsReport(
        schema_version=1,
        thresholds=Thresholds(change_count_median=1, coupling_median=1),
        summary=summary,
        files=files,
    )


def _metrics(
    *, is_dag: bool = True, largest_scc_size: int = 1, scc_count: int = 0, node_count: int = 0
) -> MetricsResult:
    return MetricsResult(
        schema_version=1,
        nodes=(),
        graph=GraphMetrics(
            node_count=node_count,
            edge_count_internal=0,
            edge_count_external=0,
            scc_count=scc_count,
            largest_scc_size=largest_scc_size,
            is_dag=is_dag,
        ),
    )


_EMPTY_ENTRYPOINTS = EntrypointResult(schema_version=1, entrypoints=())


def _build(quality, hotspots=None, metrics=None) -> SummaryResult:
    return build_summary(
        quality=quality,
        hotspots=hotspots or _hotspots(),
        metrics=metrics or _metrics(),
        entrypoints=_EMPTY_ENTRYPOINTS,
        inventory=(),
    )


# --- Strength rules ----------------------------------------------------------


def test_strength_s1_a_b_grade_dimension() -> None:
    result = _build(_quality({"coupling": "A", "test": "B", "documentation": "C"}))
    grades = {s.evidence.get("dimension"): s.evidence.get("grade") for s in result.strengths}
    assert grades.get("coupling") == "A"
    assert grades.get("test") == "B"
    assert "documentation" not in grades


def test_strength_s2_stable_ratio_at_least_half() -> None:
    summary = Summary(hotspot=1, active_stable=1, neglected_complex=0, stable=8)  # 80%
    result = _build(_quality({}), hotspots=_hotspots(summary=summary))
    assert any(s.text.startswith("안정 영역") for s in result.strengths)
    s = next(s for s in result.strengths if s.text.startswith("안정 영역"))
    assert s.evidence["ratio_pct"] >= 50


def test_strength_s2_skipped_when_below_half() -> None:
    summary = Summary(hotspot=4, active_stable=4, neglected_complex=0, stable=2)  # 20%
    result = _build(_quality({}), hotspots=_hotspots(summary=summary))
    assert not any(s.text.startswith("안정 영역") for s in result.strengths)


def test_strength_s3_dag() -> None:
    result = _build(_quality({}), metrics=_metrics(is_dag=True, node_count=42))
    dag_items = [s for s in result.strengths if "DAG" in s.text]
    assert len(dag_items) == 1
    assert dag_items[0].evidence["node_count"] == 42


def test_strength_s4_active_stable_top_hotspot() -> None:
    files = (
        FileHotspot(path="a.py", change_count=10, coupling=10, category="active_stable"),
        FileHotspot(path="b.py", change_count=1, coupling=1, category="stable"),
    )
    result = _build(
        _quality({}),
        hotspots=_hotspots(files=files, summary=Summary(0, 1, 0, 1)),
    )
    assert any("active_stable" in s.text for s in result.strengths)


# --- Weakness rules ----------------------------------------------------------


def test_weakness_w1_d_f_grade_dimension() -> None:
    result = _build(_quality({"test": "F", "coupling": "D", "documentation": "B"}))
    grades = {w.evidence.get("dimension"): w.evidence.get("grade") for w in result.weaknesses}
    assert grades.get("test") == "F"
    assert grades.get("coupling") == "D"
    assert "documentation" not in grades


def test_weakness_w2_neglected_complex() -> None:
    files = (
        FileHotspot(path="bad.py", change_count=1, coupling=15, category="neglected_complex"),
    )
    result = _build(
        _quality({}),
        hotspots=_hotspots(files=files, summary=Summary(0, 0, 1, 0)),
    )
    assert any("neglected_complex" in w.text for w in result.weaknesses)
    w = next(w for w in result.weaknesses if "neglected_complex" in w.text)
    assert w.evidence["path"] == "bad.py"


def test_weakness_w3_largest_scc_greater_than_one() -> None:
    result = _build(
        _quality({}),
        metrics=_metrics(is_dag=False, largest_scc_size=4, scc_count=2),
    )
    assert any("SCC" in w.text for w in result.weaknesses)


def test_weakness_w4_top_hotspot_category_hotspot() -> None:
    files = (
        FileHotspot(path="hot.py", change_count=15, coupling=45, category="hotspot"),
        FileHotspot(path="cold.py", change_count=1, coupling=1, category="stable"),
    )
    result = _build(
        _quality({}),
        hotspots=_hotspots(files=files, summary=Summary(1, 0, 0, 1)),
    )
    assert any("Top hotspot" in w.text for w in result.weaknesses)
    w = next(w for w in result.weaknesses if "Top hotspot" in w.text)
    assert w.evidence["priority"] == 15 * 45


# --- Action mapping ----------------------------------------------------------


def test_action_for_test_dimension() -> None:
    result = _build(_quality({"test": "F"}))
    assert any("characterization test" in a.text for a in result.actions)


def test_action_for_coupling_dimension() -> None:
    result = _build(_quality({"coupling": "D"}))
    assert any("결합도 분해" in a.text for a in result.actions)


def test_action_for_documentation_dimension() -> None:
    result = _build(_quality({"documentation": "F"}))
    assert any("문서화 진입점" in a.text for a in result.actions)


def test_action_for_cohesion_dimension() -> None:
    result = _build(_quality({"cohesion": "D"}))
    assert any("모듈 책임 재정렬" in a.text for a in result.actions)


def test_action_for_top_hotspot() -> None:
    files = (FileHotspot(path="h.py", change_count=10, coupling=10, category="hotspot"),)
    result = _build(
        _quality({}),
        hotspots=_hotspots(files=files, summary=Summary(1, 0, 0, 0)),
    )
    assert any("Top hotspot" in a.text and "테스트 + 책임 분리" in a.text for a in result.actions)


def test_action_for_neglected_complex() -> None:
    files = (
        FileHotspot(path="n.py", change_count=1, coupling=20, category="neglected_complex"),
    )
    result = _build(
        _quality({}),
        hotspots=_hotspots(files=files, summary=Summary(0, 0, 1, 0)),
    )
    assert any("neglected_complex 파일 소유권" in a.text for a in result.actions)


def test_action_for_scc() -> None:
    result = _build(
        _quality({}),
        metrics=_metrics(is_dag=False, largest_scc_size=3, scc_count=1),
    )
    assert any("SCC 끊기" in a.text for a in result.actions)


def test_action_dedup_per_key() -> None:
    # 두 개의 hotspot weakness가 있어도 동일 action 한 번만.
    files = (
        FileHotspot(path="a.py", change_count=10, coupling=10, category="hotspot"),
        FileHotspot(path="b.py", change_count=8, coupling=8, category="hotspot"),
    )
    result = _build(
        _quality({}),
        hotspots=_hotspots(files=files, summary=Summary(2, 0, 0, 0)),
    )
    matching = [a for a in result.actions if "Top hotspot" in a.text]
    assert len(matching) == 1


# --- Top 3 cap & fallback ----------------------------------------------------


def test_top_three_cap_strengths() -> None:
    quality = _quality(
        {"coupling": "A", "cohesion": "A", "test": "B", "documentation": "B"},
    )
    files = (
        FileHotspot(path="t.py", change_count=10, coupling=1, category="active_stable"),
    )
    summary = Summary(hotspot=0, active_stable=1, neglected_complex=0, stable=10)
    metrics = _metrics(is_dag=True, node_count=10)
    result = _build(quality, hotspots=_hotspots(files=files, summary=summary), metrics=metrics)
    assert len(result.strengths) == 3


def test_top_three_cap_weaknesses() -> None:
    quality = _quality(
        {"coupling": "F", "cohesion": "F", "test": "D", "documentation": "D"},
    )
    files = (
        FileHotspot(path="h.py", change_count=10, coupling=10, category="hotspot"),
    )
    metrics = _metrics(is_dag=False, largest_scc_size=2, scc_count=1)
    hotspots = _hotspots(files=files, summary=Summary(1, 0, 0, 0))
    result = _build(quality, hotspots=hotspots, metrics=metrics)
    assert len(result.weaknesses) == 3


def test_top_three_cap_actions() -> None:
    quality = _quality({"coupling": "F", "cohesion": "F", "test": "F", "documentation": "F"})
    result = _build(quality)
    # Test/coupling/cohesion/documentation 매핑이 있어 4 후보 → cap 3.
    assert len(result.actions) == 3


def test_empty_inputs_yield_empty_pools() -> None:
    result = _build(_quality({}))
    # No quality dims, no hotspots, DAG=true, no SCC → DAG 강점 1개만 가능.
    assert all(s.text == "순환 의존 없음 (DAG)" for s in result.strengths) or not result.strengths
    assert result.weaknesses == ()
    assert result.actions == ()


def test_severity_priority_f_before_d() -> None:
    quality = _quality({"coupling": "D", "test": "F"})
    result = _build(quality)
    assert result.weaknesses[0].evidence["grade"] == "F"
    assert result.weaknesses[1].evidence["grade"] == "D"


def test_evidence_required() -> None:
    files = (FileHotspot(path="h.py", change_count=10, coupling=10, category="hotspot"),)
    hotspots = _hotspots(files=files, summary=Summary(1, 0, 0, 0))
    result = _build(_quality({"test": "F"}), hotspots=hotspots)
    for item in (*result.strengths, *result.weaknesses, *result.actions):
        assert item.evidence
