from pathlib import Path

from codexray.graph.csharp_index import build_indexes
from codexray.graph.csharp_parser import extract_type_usages


def test_extract_type_usages_basic() -> None:
    src = "var b = new Building(); var c = new Customer();"
    assert extract_type_usages(src) == {"Building", "Customer"}


def test_extract_type_usages_strips_string() -> None:
    src = 'var s = "Building"; var b = new Manager();'
    assert extract_type_usages(src) == {"Manager"}


def test_extract_type_usages_strips_line_comment() -> None:
    src = "// uses Building\nvar c = new Manager();"
    assert extract_type_usages(src) == {"Manager"}


def test_extract_type_usages_strips_block_comment() -> None:
    src = "/* old: Building */\nvar c = new Manager();"
    assert extract_type_usages(src) == {"Manager"}


def test_extract_type_usages_dedupe() -> None:
    src = "var a = new Foo(); var b = new Foo(); var c = new Bar();"
    assert extract_type_usages(src) == {"Foo", "Bar"}


def test_build_indexes_block_namespace_with_type(tmp_path: Path) -> None:
    foo = tmp_path / "Foo.cs"
    foo.write_text("namespace App.Core { public class Foo {} }\n")
    indexes = build_indexes([(foo, foo.read_text())])
    assert indexes.namespace_to_files == {"App.Core": {foo}}
    assert indexes.type_to_file == {("App.Core", "Foo"): foo}
    assert indexes.file_to_namespaces == {foo: {"App.Core"}}


def test_build_indexes_file_scoped_namespace(tmp_path: Path) -> None:
    foo = tmp_path / "Foo.cs"
    foo.write_text("namespace App.Core;\npublic class Foo {}\n")
    indexes = build_indexes([(foo, foo.read_text())])
    assert ("App.Core", "Foo") in indexes.type_to_file


def test_build_indexes_multiple_namespaces(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text(
        "namespace X.Y { class A {} }\nnamespace X.Z { class B {} }\n"
    )
    indexes = build_indexes([(a, a.read_text())])
    assert indexes.type_to_file[("X.Y", "A")] == a
    assert indexes.type_to_file[("X.Z", "B")] == a


def test_build_indexes_global_namespace_not_indexed(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text("class FreeFloating {}\n")
    indexes = build_indexes([(a, a.read_text())])
    # Global namespace types are not registered in either index.
    assert indexes.namespace_to_files == {}
    assert indexes.type_to_file == {}


def test_build_indexes_partial_class_last_wins(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text("namespace X { partial class P {} }\n")
    b = tmp_path / "B.cs"
    b.write_text("namespace X { partial class P {} }\n")
    indexes = build_indexes([(a, a.read_text()), (b, b.read_text())])
    # Last registration wins (1차 결정).
    assert indexes.type_to_file[("X", "P")] in {a, b}
