import json
from pathlib import Path

from codexray.graph import build_graph, to_json


def _make(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_csharp_one_to_one_internal(tmp_path: Path) -> None:
    _make(tmp_path, "Foo.cs", "namespace App.Core { class Foo {} }\n")
    _make(tmp_path, "Bar.cs", "using App.Core;\n\nclass Bar {}\n")
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Bar.cs", "Foo.cs", "internal") in edges


def test_csharp_one_to_many_internal(tmp_path: Path) -> None:
    _make(tmp_path, "A.cs", "namespace App.Core { class A {} }\n")
    _make(tmp_path, "B.cs", "namespace App.Core { class B {} }\n")
    _make(tmp_path, "Main.cs", "using App.Core;\nclass Main {}\n")
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Main.cs", "A.cs", "internal") in edges
    assert ("Main.cs", "B.cs", "internal") in edges


def test_csharp_unknown_namespace_external(tmp_path: Path) -> None:
    _make(tmp_path, "Bar.cs", "using UnityEngine;\nclass Bar {}\n")
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Bar.cs", "UnityEngine", "external") in edges


def test_csharp_global_namespace_not_internal_target(tmp_path: Path) -> None:
    _make(tmp_path, "Free.cs", "class Free {}\n")  # no namespace
    _make(tmp_path, "Bar.cs", "using SomethingMissing;\nclass Bar {}\n")
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    # Free.cs cannot be an internal target via using; only external.
    assert ("Bar.cs", "SomethingMissing", "external") in edges
    assert all(not (e.from_ == "Bar.cs" and e.to == "Free.cs") for e in graph.edges)


def test_csharp_file_scoped_namespace_internal(tmp_path: Path) -> None:
    _make(tmp_path, "Foo.cs", "namespace App.Core;\nclass Foo {}\n")
    _make(tmp_path, "Bar.cs", "using App.Core;\nclass Bar {}\n")
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("Bar.cs", "Foo.cs", "internal") in edges


def test_csharp_node_language(tmp_path: Path) -> None:
    _make(tmp_path, "A.cs", "class A {}\n")
    graph = build_graph(tmp_path)
    assert graph.nodes[0].language == "C#"


def test_csharp_serialization_emits_csharp_node(tmp_path: Path) -> None:
    _make(tmp_path, "A.cs", "namespace App;\nclass A {}\n")
    _make(tmp_path, "B.cs", "using App;\n")
    parsed = json.loads(to_json(build_graph(tmp_path)))
    languages = {n["language"] for n in parsed["nodes"]}
    assert "C#" in languages
    assert any(
        e["from"] == "B.cs" and e["to"] == "A.cs" and e["kind"] == "internal"
        for e in parsed["edges"]
    )
