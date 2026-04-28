from pathlib import Path

from codexray.graph.csharp_index import build_namespace_index


def test_block_namespace(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text("namespace App.Core { class X {} }\n")
    index = build_namespace_index([(a, a.read_text())])
    assert index == {"App.Core": {a}}


def test_file_scoped_namespace(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text("namespace App.Core;\nclass X {}\n")
    index = build_namespace_index([(a, a.read_text())])
    assert index == {"App.Core": {a}}


def test_multiple_files_share_namespace(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text("namespace App.Core { class X {} }\n")
    b = tmp_path / "B.cs"
    b.write_text("namespace App.Core { class Y {} }\n")
    index = build_namespace_index([(a, a.read_text()), (b, b.read_text())])
    assert index == {"App.Core": {a, b}}


def test_multiple_namespaces_in_one_file(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text(
        "namespace X.Y { class A {} }\nnamespace X.Z { class B {} }\n"
    )
    index = build_namespace_index([(a, a.read_text())])
    assert index == {"X.Y": {a}, "X.Z": {a}}


def test_no_namespace_declaration(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text("class FreeFloating {}\n")
    index = build_namespace_index([(a, a.read_text())])
    assert index == {}
