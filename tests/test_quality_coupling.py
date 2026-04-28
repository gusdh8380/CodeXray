from codexray.graph.types import Edge, Graph, Node
from codexray.quality.coupling import compute


def _g(nodes: list[Node], edges: list[Edge]) -> Graph:
    return Graph(nodes=tuple(nodes), edges=tuple(edges))


def test_zero_coupling_full_score() -> None:
    g = _g([Node("a.py", "Python"), Node("b.py", "Python")], [])
    result = compute(g)
    assert result.score == 100
    assert result.grade == "A"


def test_average_two_yields_eighty() -> None:
    # Two nodes, two edges (a→b, b→a) → fan_in+fan_out per node = 2, avg=2
    g = _g(
        [Node("a.py", "Python"), Node("b.py", "Python")],
        [
            Edge("a.py", "b.py", "internal"),
            Edge("b.py", "a.py", "internal"),
        ],
    )
    result = compute(g)
    assert result.score == 80
    assert result.grade == "B"
    assert result.detail["avg_fan_inout"] == 2.0


def test_max_in_detail() -> None:
    g = _g(
        [Node("a.py", "Python"), Node("b.py", "Python"), Node("c.py", "Python")],
        [
            Edge("a.py", "b.py", "internal"),
            Edge("a.py", "c.py", "internal"),
            Edge("c.py", "b.py", "internal"),
        ],
    )
    result = compute(g)
    # b.py has fan_in=2, fan_out=0 → 2 (max)
    assert result.detail["max"] == 2


def test_external_edges_ignored() -> None:
    g = _g(
        [Node("a.py", "Python")],
        [Edge("a.py", "os", "external"), Edge("a.py", "sys", "external")],
    )
    result = compute(g)
    assert result.score == 100  # external doesn't count


def test_empty_graph_returns_none() -> None:
    g = _g([], [])
    result = compute(g)
    assert result.score is None
    assert result.grade is None
    assert "reason" in result.detail
