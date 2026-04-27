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
    assert resolve(raw, tmp_path.resolve(), internal) == (pkg / "x.py").resolve()


def test_python_absolute_unresolved(tmp_path: Path) -> None:
    src = tmp_path / "a.py"
    src.write_text("")
    internal = {src.resolve()}
    raw = RawImport(source=src.resolve(), raw="os", level=0, language="Python")
    assert resolve(raw, tmp_path.resolve(), internal) is None


def test_python_relative_sibling(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "sib.py").write_text("")
    src = pkg / "main.py"
    src.write_text("from .sib import x\n")
    internal = {(pkg / "__init__.py").resolve(), (pkg / "sib.py").resolve(), src.resolve()}
    raw = RawImport(source=src.resolve(), raw="sib", level=1, language="Python")
    assert resolve(raw, tmp_path.resolve(), internal) == (pkg / "sib.py").resolve()


def test_python_relative_to_init(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    init = pkg / "__init__.py"
    init.write_text("")
    src = pkg / "main.py"
    src.write_text("from . import xs\n")
    internal = {init.resolve(), src.resolve()}
    # `from . import xs` with no submodule file falls back to package __init__.py
    raw = RawImport(source=src.resolve(), raw="xs", level=1, language="Python")
    # No xs.py, no xs/ — unresolved
    assert resolve(raw, tmp_path.resolve(), internal) is None


def test_js_relative_extension_omitted(tmp_path: Path) -> None:
    util = tmp_path / "util.ts"
    util.write_text("")
    src = tmp_path / "a.ts"
    src.write_text("")
    internal = {util.resolve(), src.resolve()}
    raw = RawImport(source=src.resolve(), raw="./util", level=0, language="TypeScript")
    assert resolve(raw, tmp_path.resolve(), internal) == util.resolve()


def test_js_relative_index(tmp_path: Path) -> None:
    mod = tmp_path / "mod"
    mod.mkdir()
    idx = mod / "index.ts"
    idx.write_text("")
    src = tmp_path / "a.ts"
    src.write_text("")
    internal = {idx.resolve(), src.resolve()}
    raw = RawImport(source=src.resolve(), raw="./mod", level=0, language="TypeScript")
    assert resolve(raw, tmp_path.resolve(), internal) == idx.resolve()


def test_js_bare_specifier_unresolved(tmp_path: Path) -> None:
    src = tmp_path / "a.ts"
    src.write_text("")
    internal = {src.resolve()}
    raw = RawImport(source=src.resolve(), raw="react", level=0, language="TypeScript")
    assert resolve(raw, tmp_path.resolve(), internal) is None


def test_resolved_to_ignored_dir_returns_none(tmp_path: Path) -> None:
    nm = tmp_path / "node_modules" / "lib.js"
    nm.parent.mkdir()
    nm.write_text("")
    src = tmp_path / "a.js"
    src.write_text("")
    # node_modules content is NOT in internal_paths (walk would skip it)
    internal = {src.resolve()}
    raw = RawImport(source=src.resolve(), raw="./node_modules/lib", level=0, language="JavaScript")
    assert resolve(raw, tmp_path.resolve(), internal) is None
