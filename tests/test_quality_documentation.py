from pathlib import Path

from codexray.quality.documentation import compute


def _make(tmp_path: Path, name: str, content: str) -> None:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def test_python_all_documented_full_score(tmp_path: Path) -> None:
    src = (
        '"""module."""\n\n'
        'def f():\n    """func."""\n    pass\n\n'
        'class C:\n    """class."""\n    pass\n'
    )
    _make(tmp_path, "a.py", src)
    result = compute(tmp_path)
    assert result.score == 100
    assert result.detail["items_total"] == 3
    assert result.detail["documented"] == 3


def test_python_half_documented(tmp_path: Path) -> None:
    src = '"""module."""\n\ndef f():\n    pass\n'  # 2 items, 1 documented (module only)
    _make(tmp_path, "a.py", src)
    result = compute(tmp_path)
    assert result.detail["items_total"] == 2
    assert result.detail["documented"] == 1
    assert result.score == 50


def test_python_none_documented(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "x = 1\ndef f():\n    pass\n")
    result = compute(tmp_path)
    assert result.score == 0


def test_csharp_documented(tmp_path: Path) -> None:
    src = "/// <summary>X</summary>\npublic class A { }\n"
    _make(tmp_path, "A.cs", src)
    result = compute(tmp_path)
    assert result.detail["items_total"] >= 1
    assert result.detail["documented"] >= 1


def test_csharp_no_doc(tmp_path: Path) -> None:
    src = "public class A { }\n"
    _make(tmp_path, "A.cs", src)
    result = compute(tmp_path)
    assert result.detail["items_total"] >= 1
    assert result.detail["documented"] == 0


def test_no_python_or_csharp_returns_none(tmp_path: Path) -> None:
    _make(tmp_path, "a.ts", "export const x = 1;\n")
    result = compute(tmp_path)
    assert result.score is None
    assert result.grade is None
