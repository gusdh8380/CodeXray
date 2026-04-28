from pathlib import Path

from codexray.graph.csharp_parser import extract_imports


def _raws(imports) -> set[str]:
    return {i.raw for i in imports}


def test_simple_using() -> None:
    src = "using System;\nusing System.Collections.Generic;\n"
    assert _raws(extract_imports(src, Path("a.cs"))) == {
        "System",
        "System.Collections.Generic",
    }


def test_using_static() -> None:
    src = "using static System.Math;\n"
    assert _raws(extract_imports(src, Path("a.cs"))) == {"System.Math"}


def test_alias_not_extracted() -> None:
    src = "using G = System.Collections.Generic;\n"
    assert _raws(extract_imports(src, Path("a.cs"))) == set()


def test_global_using_not_extracted() -> None:
    src = "global using System;\n"
    assert _raws(extract_imports(src, Path("a.cs"))) == set()


def test_using_block_in_method_not_extracted() -> None:
    # `using (var x = ...)` is a resource block, not an import; no semicolon-terminated identifier.
    src = "void M() { using (var s = new X()) { } }\n"
    assert _raws(extract_imports(src, Path("a.cs"))) == set()


def test_dedupe_per_file() -> None:
    src = "using System;\nusing System;\n"
    assert _raws(extract_imports(src, Path("a.cs"))) == {"System"}


def test_leading_whitespace_allowed() -> None:
    src = "    using System.IO;\n"
    assert _raws(extract_imports(src, Path("a.cs"))) == {"System.IO"}
