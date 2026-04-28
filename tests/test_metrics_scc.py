from codexray.metrics.scc import tarjan_scc


def _normalize(sccs: list[set[str]]) -> list[set[str]]:
    return sorted(sccs, key=lambda s: sorted(s))


def test_empty_graph() -> None:
    assert tarjan_scc({}) == []


def test_single_node_no_edges() -> None:
    assert tarjan_scc({"a": []}) == [{"a"}]


def test_dag_chain() -> None:
    adj = {"a": ["b"], "b": ["c"], "c": []}
    sccs = _normalize(tarjan_scc(adj))
    assert sccs == [{"a"}, {"b"}, {"c"}]


def test_two_node_cycle() -> None:
    adj = {"a": ["b"], "b": ["a"]}
    sccs = tarjan_scc(adj)
    assert len(sccs) == 1
    assert sccs[0] == {"a", "b"}


def test_three_node_cycle() -> None:
    adj = {"a": ["b"], "b": ["c"], "c": ["a"]}
    sccs = tarjan_scc(adj)
    assert len(sccs) == 1
    assert sccs[0] == {"a", "b", "c"}


def test_mixed_dag_plus_scc() -> None:
    # a -> b <-> c, d isolated
    adj = {"a": ["b"], "b": ["c"], "c": ["b"], "d": []}
    sccs = _normalize(tarjan_scc(adj))
    assert {"a"} in sccs
    assert {"b", "c"} in sccs
    assert {"d"} in sccs
    assert len(sccs) == 3


def test_self_loop_is_size_one() -> None:
    adj = {"a": ["a"]}
    sccs = tarjan_scc(adj)
    assert sccs == [{"a"}]  # SCC size 1, but is_dag check considers self-loop separately


def test_disconnected_components() -> None:
    adj = {"a": ["b"], "b": [], "c": ["d"], "d": ["c"]}
    sccs = _normalize(tarjan_scc(adj))
    assert {"a"} in sccs
    assert {"b"} in sccs
    assert {"c", "d"} in sccs


def test_deterministic_order() -> None:
    adj = {"x": ["y"], "y": ["x"], "a": ["b"], "b": []}
    first = tarjan_scc(adj)
    second = tarjan_scc(adj)
    assert first == second
