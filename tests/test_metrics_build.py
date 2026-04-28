from pathlib import Path

from codexray.graph import build_graph
from codexray.graph.types import Edge, Graph, Node
from codexray.metrics import build_metrics


def _make(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_fan_in_fan_out_basic(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "from .b import x\nfrom .c import y\nimport os\n")
    _make(tmp_path, "b.py", "")
    _make(tmp_path, "c.py", "")
    metrics = build_metrics(build_graph(tmp_path))
    by_path = {n.path: n for n in metrics.nodes}
    assert by_path["a.py"].fan_out == 2
    assert by_path["a.py"].external_fan_out == 1
    assert by_path["b.py"].fan_in == 1
    assert by_path["c.py"].fan_in == 1


def test_external_node_not_in_metrics() -> None:
    graph = Graph(
        nodes=(Node(path="a.py", language="Python"),),
        edges=(
            Edge(from_="a.py", to="os", kind="external"),
            Edge(from_="a.py", to="sys", kind="external"),
        ),
    )
    metrics = build_metrics(graph)
    assert [n.path for n in metrics.nodes] == ["a.py"]
    assert metrics.nodes[0].external_fan_out == 2
    assert metrics.nodes[0].fan_in == 0


def test_dag_is_dag_true() -> None:
    graph = Graph(
        nodes=(
            Node(path="a.py", language="Python"),
            Node(path="b.py", language="Python"),
            Node(path="c.py", language="Python"),
        ),
        edges=(
            Edge(from_="a.py", to="b.py", kind="internal"),
            Edge(from_="b.py", to="c.py", kind="internal"),
        ),
    )
    metrics = build_metrics(graph)
    assert metrics.graph.is_dag is True
    assert metrics.graph.scc_count == 3
    assert metrics.graph.largest_scc_size == 1


def test_cycle_is_dag_false() -> None:
    graph = Graph(
        nodes=(
            Node(path="a.py", language="Python"),
            Node(path="b.py", language="Python"),
        ),
        edges=(
            Edge(from_="a.py", to="b.py", kind="internal"),
            Edge(from_="b.py", to="a.py", kind="internal"),
        ),
    )
    metrics = build_metrics(graph)
    assert metrics.graph.is_dag is False
    assert metrics.graph.scc_count == 1
    assert metrics.graph.largest_scc_size == 2


def test_self_loop_breaks_dag() -> None:
    graph = Graph(
        nodes=(Node(path="a.py", language="Python"),),
        edges=(Edge(from_="a.py", to="a.py", kind="internal"),),
    )
    metrics = build_metrics(graph)
    assert metrics.graph.is_dag is False
    assert metrics.graph.scc_count == 1
    assert metrics.graph.largest_scc_size == 1


def test_count_consistency(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "from .b import x\nimport os\nimport sys\n")
    _make(tmp_path, "b.py", "import json\n")
    metrics = build_metrics(build_graph(tmp_path))
    fan_out_total = sum(n.fan_out for n in metrics.nodes)
    ext_total = sum(n.external_fan_out for n in metrics.nodes)
    assert metrics.graph.node_count == len(metrics.nodes)
    assert metrics.graph.edge_count_internal == fan_out_total
    assert metrics.graph.edge_count_external == ext_total


def test_empty_graph_is_dag() -> None:
    graph = Graph(nodes=(), edges=())
    metrics = build_metrics(graph)
    assert metrics.graph.is_dag is True
    assert metrics.graph.scc_count == 0
    assert metrics.graph.largest_scc_size == 0
