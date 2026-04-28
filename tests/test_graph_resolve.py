from pathlib import Path

from codexray.graph.resolve import resolve
from codexray.graph.types import RawImport


def test_python_absolute_to_module(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "x.py").write_text("")
    src = pkg / "main.py"
    src.write_text("import pkg.x\n")
    internal = {(pkg / "__init__.py").resolve(), (pkg / "x.py").resolve(), src.resolve()}

    raw = RawImport(source=src.resolve(), raw="pkg.x", level=0, language="Python")
    assert resolve(raw, tmp_path.resolve(), internal, None) == [(pkg / "x.py").resolve()]


def test_python_absolute_unresolved(tmp_path: Path) -> None:
    src = tmp_path / "a.py"
    src.write_text("")
    internal = {src.resolve()}
    raw = RawImport(source=src.resolve(), raw="os", level=0, language="Python")
    assert resolve(raw, tmp_path.resolve(), internal, None) == []


def test_python_relative_sibling(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "sib.py").write_text("")
    src = pkg / "main.py"
    src.write_text("from .sib import x\n")
    internal = {(pkg / "__init__.py").resolve(), (pkg / "sib.py").resolve(), src.resolve()}
    raw = RawImport(source=src.resolve(), raw="sib", level=1, language="Python")
    assert resolve(raw, tmp_path.resolve(), internal, None) == [(pkg / "sib.py").resolve()]


def test_python_relative_no_match(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    init = pkg / "__init__.py"
    init.write_text("")
    src = pkg / "main.py"
    src.write_text("from . import xs\n")
    internal = {init.resolve(), src.resolve()}
    raw = RawImport(source=src.resolve(), raw="xs", level=1, language="Python")
    assert resolve(raw, tmp_path.resolve(), internal, None) == []


def test_js_relative_extension_omitted(tmp_path: Path) -> None:
    util = tmp_path / "util.ts"
    util.write_text("")
    src = tmp_path / "a.ts"
    src.write_text("")
    internal = {util.resolve(), src.resolve()}
    raw = RawImport(source=src.resolve(), raw="./util", level=0, language="TypeScript")
    assert resolve(raw, tmp_path.resolve(), internal, None) == [util.resolve()]


def test_js_relative_index(tmp_path: Path) -> None:
    mod = tmp_path / "mod"
    mod.mkdir()
    idx = mod / "index.ts"
    idx.write_text("")
    src = tmp_path / "a.ts"
    src.write_text("")
    internal = {idx.resolve(), src.resolve()}
    raw = RawImport(source=src.resolve(), raw="./mod", level=0, language="TypeScript")
    assert resolve(raw, tmp_path.resolve(), internal, None) == [idx.resolve()]


def test_js_bare_specifier_unresolved(tmp_path: Path) -> None:
    src = tmp_path / "a.ts"
    src.write_text("")
    internal = {src.resolve()}
    raw = RawImport(source=src.resolve(), raw="react", level=0, language="TypeScript")
    assert resolve(raw, tmp_path.resolve(), internal, None) == []


def test_resolved_to_ignored_dir_returns_empty(tmp_path: Path) -> None:
    nm = tmp_path / "node_modules" / "lib.js"
    nm.parent.mkdir()
    nm.write_text("")
    src = tmp_path / "a.js"
    src.write_text("")
    internal = {src.resolve()}
    raw = RawImport(source=src.resolve(), raw="./node_modules/lib", level=0, language="JavaScript")
    assert resolve(raw, tmp_path.resolve(), internal, None) == []


def test_csharp_namespace_one_to_one(tmp_path: Path) -> None:
    foo = tmp_path / "Foo.cs"
    foo.write_text("namespace App.Core { class X {} }\n")
    bar = tmp_path / "Bar.cs"
    bar.write_text("using App.Core;\n")
    internal = {foo.resolve(), bar.resolve()}
    index = {"App.Core": {foo.resolve()}}
    raw = RawImport(source=bar.resolve(), raw="App.Core", level=0, language="C#")
    assert resolve(raw, tmp_path.resolve(), internal, index) == [foo.resolve()]


def test_csharp_namespace_one_to_many(tmp_path: Path) -> None:
    a = tmp_path / "A.cs"
    a.write_text("namespace App.Core { class X {} }\n")
    b = tmp_path / "B.cs"
    b.write_text("namespace App.Core { class Y {} }\n")
    main = tmp_path / "Main.cs"
    main.write_text("using App.Core;\n")
    internal = {a.resolve(), b.resolve(), main.resolve()}
    index = {"App.Core": {a.resolve(), b.resolve()}}
    raw = RawImport(source=main.resolve(), raw="App.Core", level=0, language="C#")
    assert resolve(raw, tmp_path.resolve(), internal, index) == sorted(
        [a.resolve(), b.resolve()]
    )


def test_csharp_namespace_unresolved(tmp_path: Path) -> None:
    src = tmp_path / "Bar.cs"
    src.write_text("using UnityEngine;\n")
    raw = RawImport(source=src.resolve(), raw="UnityEngine", level=0, language="C#")
    assert resolve(raw, tmp_path.resolve(), {src.resolve()}, {}) == []
