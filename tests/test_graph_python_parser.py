from pathlib import Path

from codexray.graph.python_parser import extract_imports


def _names(imports) -> set[tuple[str, int]]:
    return {(i.raw, i.level) for i in imports}


def test_absolute_imports() -> None:
    src = "import os\nimport json\nfrom typing import Any\n"
    imports, syntax_error = extract_imports(src, Path("a.py"))
    assert syntax_error is False
    assert _names(imports) == {("os", 0), ("json", 0), ("typing", 0)}


def test_aliased_import() -> None:
    src = "import numpy as np\nfrom typing import Any as A\n"
    imports, _ = extract_imports(src, Path("a.py"))
    assert _names(imports) == {("numpy", 0), ("typing", 0)}


def test_multiname_from() -> None:
    src = "from os import path, sep, linesep\n"
    imports, _ = extract_imports(src, Path("a.py"))
    # ImportFrom with module='os' contributes a single edge
    assert _names(imports) == {("os", 0)}


def test_relative_import() -> None:
    src = "from .x import y\nfrom ..pkg import z\nfrom . import sib\n"
    imports, _ = extract_imports(src, Path("a/b.py"))
    assert ("x", 1) in _names(imports)
    assert ("pkg", 2) in _names(imports)
    assert ("sib", 1) in _names(imports)


def test_syntax_error_reports() -> None:
    src = "def broken(\n"
    imports, syntax_error = extract_imports(src, Path("bad.py"))
    assert imports == []
    assert syntax_error is True
