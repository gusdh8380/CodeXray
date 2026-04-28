import json
from pathlib import Path

from codexray.graph import build_graph, to_json


def _make(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_python_self_reference(tmp_path: Path) -> None:
    _make(tmp_path, "pkg/__init__.py", "")
    _make(tmp_path, "pkg/util.py", "x = 1\n")
    _make(tmp_path, "pkg/main.py", "from .util import x\nimport os\n")

    graph = build_graph(tmp_path)
    paths = sorted(n.path for n in graph.nodes)
    assert paths == ["pkg/__init__.py", "pkg/main.py", "pkg/util.py"]

    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("pkg/main.py", "pkg/util.py", "internal") in edges
    assert ("pkg/main.py", "os", "external") in edges


def test_typescript_mix(tmp_path: Path) -> None:
    _make(tmp_path, "util.ts", "export const z = 1;\n")
    _make(
        tmp_path,
        "main.ts",
        'import { z } from "./util";\nimport React from "react";\n',
    )
    graph = build_graph(tmp_path)
    edges = {(e.from_, e.to, e.kind) for e in graph.edges}
    assert ("main.ts", "util.ts", "internal") in edges
    assert ("main.ts", "react", "external") in edges


def test_java_excluded_other_targets_included(tmp_path: Path) -> None:
    _make(tmp_path, "Main.java", "package x; class Main {}\n")
    _make(tmp_path, "Foo.cs", "namespace X { class Foo {} }\n")
    _make(tmp_path, "main.py", "import os\n")
    graph = build_graph(tmp_path)
    assert [n.path for n in graph.nodes] == ["Foo.cs", "main.py"]


def test_deterministic_output(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "import os\nimport sys\n")
    _make(tmp_path, "b.py", "import json\nimport re\n")
    first = to_json(build_graph(tmp_path))
    second = to_json(build_graph(tmp_path))
    assert first == second
    parsed = json.loads(first)
    assert parsed["schema_version"] == 1
    assert "nodes" in parsed
    assert "edges" in parsed


def test_syntax_error_node_kept_no_edges(tmp_path: Path, capsys) -> None:
    _make(tmp_path, "broken.py", "def x(\n")
    _make(tmp_path, "ok.py", "import os\n")
    graph = build_graph(tmp_path)
    paths = [n.path for n in graph.nodes]
    assert "broken.py" in paths
    edges_from_broken = [e for e in graph.edges if e.from_ == "broken.py"]
    assert edges_from_broken == []
    captured = capsys.readouterr()
    assert "syntax error" in captured.err
