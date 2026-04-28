import json
from pathlib import Path

from codexray.graph import build_graph, to_json


def _make(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_csharp_using_with_type_usage_internal(tmp_path: Path) -> None:
    _make(tmp_path, "Foo.cs", "namespace App.Core { class Foo {} }\n")
    _make(
        tmp_path,
        "Bar.cs",
        "using App.Core;\nclass Bar { void M() { var f = new Foo(); } }\n",
    )
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Bar.cs", "Foo.cs", "internal") in edges


def test_csharp_only_used_types_get_edges(tmp_path: Path) -> None:
    _make(tmp_path, "A.cs", "namespace App.Core { class A {} }\n")
    _make(tmp_path, "B.cs", "namespace App.Core { class B {} }\n")
    _make(
        tmp_path,
        "Main.cs",
        "using App.Core;\nclass Main { void M() { var a = new A(); var b = new B(); } }\n",
    )
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Main.cs", "A.cs", "internal") in edges
    assert ("Main.cs", "B.cs", "internal") in edges


def test_csharp_unused_types_get_no_edge(tmp_path: Path) -> None:
    _make(tmp_path, "A.cs", "namespace App.Core { class A {} }\n")
    _make(tmp_path, "B.cs", "namespace App.Core { class B {} }\n")
    _make(
        tmp_path,
        "Main.cs",
        "using App.Core;\nclass Main { void M() { var a = new A(); } }\n",
    )
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Main.cs", "A.cs", "internal") in edges
    assert ("Main.cs", "B.cs", "internal") not in edges


def test_csharp_using_without_any_type_usage_no_edge(tmp_path: Path) -> None:
    _make(tmp_path, "Foo.cs", "namespace App.Core { class Foo {} }\n")
    _make(tmp_path, "Bar.cs", "using App.Core;\nclass Bar {}\n")
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    # Bar uses no type from App.Core → no internal edge to Foo.cs.
    assert ("Bar.cs", "Foo.cs", "internal") not in edges
    # Also no external edge for App.Core (it IS in the index).
    assert ("Bar.cs", "App.Core", "external") not in edges


def test_csharp_unknown_namespace_external(tmp_path: Path) -> None:
    _make(tmp_path, "Bar.cs", "using UnityEngine;\nclass Bar {}\n")
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Bar.cs", "UnityEngine", "external") in edges


def test_csharp_global_namespace_not_internal_target(tmp_path: Path) -> None:
    _make(tmp_path, "Free.cs", "class Free {}\n")
    _make(
        tmp_path,
        "Bar.cs",
        "using SomethingMissing;\nclass Bar { void M() { var f = new Free(); } }\n",
    )
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    # SomethingMissing is unknown → external.
    assert ("Bar.cs", "SomethingMissing", "external") in edges
    # Free is in the global namespace, never an internal target.
    assert all(not (e.from_ == "Bar.cs" and e.to == "Free.cs") for e in graph.edges)


def test_csharp_file_scoped_namespace(tmp_path: Path) -> None:
    _make(tmp_path, "Foo.cs", "namespace App.Core;\nclass Foo {}\n")
    _make(
        tmp_path,
        "Bar.cs",
        "using App.Core;\nclass Bar { void M() { var f = new Foo(); } }\n",
    )
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Bar.cs", "Foo.cs", "internal") in edges


def test_csharp_implicit_own_namespace(tmp_path: Path) -> None:
    _make(tmp_path, "Building.cs", "namespace App.Core { class Building {} }\n")
    _make(
        tmp_path,
        "Manager.cs",
        "namespace App.Core { class Manager { void M() { var b = new Building(); } } }\n",
    )
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    # No `using App.Core;` in Manager.cs, but it's in App.Core itself,
    # so the implicit own-namespace lookup resolves Building → Building.cs.
    assert ("Manager.cs", "Building.cs", "internal") in edges


def test_csharp_node_language(tmp_path: Path) -> None:
    _make(tmp_path, "A.cs", "class A {}\n")
    graph = build_graph(tmp_path)
    assert graph.nodes[0].language == "C#"


def test_csharp_serialization_emits_csharp_node(tmp_path: Path) -> None:
    _make(tmp_path, "A.cs", "namespace App;\nclass A {}\n")
    _make(
        tmp_path,
        "B.cs",
        "using App;\nclass B { void M() { var a = new A(); } }\n",
    )
    parsed = json.loads(to_json(build_graph(tmp_path)))
    languages = {n["language"] for n in parsed["nodes"]}
    assert "C#" in languages
    assert any(
        e["from"] == "B.cs" and e["to"] == "A.cs" and e["kind"] == "internal"
        for e in parsed["edges"]
    )
