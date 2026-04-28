from codexray.graph.types import Edge, Graph, Node
from codexray.quality.cohesion import compute


def test_single_group_full_internal() -> None:
    g = Graph(
        nodes=(
            Node("src/pkg/a.py", "Python"),
            Node("src/pkg/b.py", "Python"),
        ),
        edges=(Edge("src/pkg/a.py", "src/pkg/b.py", "internal"),),
    )
    result = compute(g)
    assert result.score == 100
    assert result.grade == "A"


def test_two_groups_full_cross() -> None:
    g = Graph(
        nodes=(
            Node("src/x/a.py", "Python"),
            Node("src/y/b.py", "Python"),
        ),
        edges=(
            Edge("src/x/a.py", "src/y/b.py", "internal"),
            Edge("src/y/b.py", "src/x/a.py", "internal"),
        ),
    )
    result = compute(g)
    assert result.score == 0
    assert result.grade == "F"


def test_no_internal_edges_returns_none() -> None:
    g = Graph(
        nodes=(Node("a.py", "Python"),),
        edges=(Edge("a.py", "os", "external"),),
    )
    result = compute(g)
    assert result.score is None


def test_root_group_for_top_level_files() -> None:
    g = Graph(
        nodes=(Node("a.py", "Python"), Node("b.py", "Python")),
        edges=(Edge("a.py", "b.py", "internal"),),
    )
    result = compute(g)
    # Both files are in (root) group → 100% cohesion
    assert result.score == 100
