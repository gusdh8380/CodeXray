from codexray.entrypoints.types import EntrypointResult
from codexray.graph.types import Edge, Graph, Node
from codexray.hotspots.types import (
    FileHotspot,
    HotspotsReport,
    Summary,
    Thresholds,
)
from codexray.metrics import build_metrics
from codexray.quality.types import (
    DimensionScore,
    OverallScore,
    QualityReport,
)
from codexray.report.recommendations import generate


def _quality(grades: dict[str, str]) -> QualityReport:
    dims: dict[str, DimensionScore] = {}
    for name in ("coupling", "cohesion", "documentation", "test"):
        grade = grades.get(name)
        score = {"A": 95, "B": 80, "C": 65, "D": 50, "F": 20}.get(grade or "")
        dims[name] = DimensionScore(score=score, grade=grade, detail={})
    return QualityReport(
        schema_version=1,
        overall=OverallScore(score=50, grade="D"),
        dimensions=dims,
    )


def _empty_metrics() -> object:
    graph = Graph(nodes=(), edges=())
    return build_metrics(graph)


def _metrics_with_cycle():
    graph = Graph(
        nodes=(Node("a.py", "Python"), Node("b.py", "Python")),
        edges=(
            Edge("a.py", "b.py", "internal"),
            Edge("b.py", "a.py", "internal"),
        ),
    )
    return build_metrics(graph)


def _empty_entrypoints() -> EntrypointResult:
    return EntrypointResult(schema_version=1, entrypoints=())


def _empty_hotspots() -> HotspotsReport:
    return HotspotsReport(
        schema_version=1,
        thresholds=Thresholds(0, 0),
        summary=Summary(0, 0, 0, 0),
        files=(),
    )


def _hotspot(path: str, change: int, coupling: int) -> FileHotspot:
    return FileHotspot(path=path, change_count=change, coupling=coupling, category="hotspot")


def _hotspots_with_top(path: str, change: int, coupling: int) -> HotspotsReport:
    return HotspotsReport(
        schema_version=1,
        thresholds=Thresholds(1, 1),
        summary=Summary(1, 0, 0, 0),
        files=(_hotspot(path, change, coupling),),
    )


def test_top_hotspot_priority_highest() -> None:
    recs = generate(
        quality=_quality({}),
        metrics=_empty_metrics(),
        hotspots=_hotspots_with_top("src/big.py", 10, 30),
        entrypoints=_empty_entrypoints(),
    )
    assert recs[0].priority == 100
    assert "src/big.py" in recs[0].text


def test_f_grade_dimensions_emit_recommendation() -> None:
    recs = generate(
        quality=_quality({"test": "F", "documentation": "F"}),
        metrics=_empty_metrics(),
        hotspots=_empty_hotspots(),
        entrypoints=_empty_entrypoints(),
    )
    texts = " ".join(r.text for r in recs)
    assert "test" in texts
    assert "documentation" in texts
    assert all(r.priority == 80 for r in recs if "grade F" in r.text)


def test_cycle_detected_recommendation() -> None:
    recs = generate(
        quality=_quality({}),
        metrics=_metrics_with_cycle(),
        hotspots=_empty_hotspots(),
        entrypoints=_empty_entrypoints(),
    )
    cycle_recs = [r for r in recs if "Cycle" in r.text or "SCC" in r.text]
    assert cycle_recs
    assert cycle_recs[0].priority == 60


def test_no_entrypoints_recommendation() -> None:
    recs = generate(
        quality=_quality({}),
        metrics=_empty_metrics(),
        hotspots=_empty_hotspots(),
        entrypoints=_empty_entrypoints(),
    )
    eps_recs = [r for r in recs if "entrypoint" in r.text.lower()]
    assert eps_recs
    assert eps_recs[0].priority == 20


def test_recommendations_capped_at_five() -> None:
    grades = {"coupling": "F", "cohesion": "F", "documentation": "F", "test": "F"}
    recs = generate(
        quality=_quality(grades),
        metrics=_metrics_with_cycle(),
        hotspots=_hotspots_with_top("a.py", 10, 30),
        entrypoints=_empty_entrypoints(),
    )
    assert len(recs) == 5


def test_recommendations_sorted_by_priority_desc() -> None:
    recs = generate(
        quality=_quality({"test": "F"}),
        metrics=_metrics_with_cycle(),
        hotspots=_hotspots_with_top("a.py", 10, 30),
        entrypoints=_empty_entrypoints(),
    )
    priorities = [r.priority for r in recs]
    assert priorities == sorted(priorities, reverse=True)


def test_no_recommendations_when_clean() -> None:
    recs = generate(
        quality=_quality({}),
        metrics=_empty_metrics(),
        hotspots=_empty_hotspots(),
        entrypoints=EntrypointResult(
            schema_version=1,
            entrypoints=(),
        ),
    )
    eps_only = [r for r in recs if "entrypoint" in r.text.lower()]
    assert len(eps_only) == 1
