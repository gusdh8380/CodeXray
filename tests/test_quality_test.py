from pathlib import Path

from codexray.quality.test import compute


def _make(tmp_path: Path, name: str, content: str) -> None:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def test_no_tests_yields_zero(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "x = 1\n" * 100)
    result = compute(tmp_path)
    assert result.score == 0
    assert result.detail["src_loc"] == 100
    assert result.detail["test_loc"] == 0


def test_full_score_at_half_ratio(tmp_path: Path) -> None:
    _make(tmp_path, "src/a.py", "x = 1\n" * 100)
    _make(tmp_path, "tests/test_a.py", "y = 1\n" * 50)
    result = compute(tmp_path)
    assert result.score == 100
    assert result.detail["ratio"] == 0.5


def test_low_ratio(tmp_path: Path) -> None:
    _make(tmp_path, "src/a.py", "x = 1\n" * 100)
    _make(tmp_path, "tests/test_a.py", "y = 1\n" * 10)
    result = compute(tmp_path)
    assert result.score == 20
    assert result.grade == "F"


def test_filename_pattern_csharp(tmp_path: Path) -> None:
    _make(tmp_path, "src/Foo.cs", "class Foo {}\n" * 100)
    _make(tmp_path, "src/FooTests.cs", "class FooTests {}\n" * 50)
    result = compute(tmp_path)
    assert result.detail["test_loc"] == 50
    assert result.detail["src_loc"] == 100


def test_typescript_spec(tmp_path: Path) -> None:
    _make(tmp_path, "a.ts", "x\n" * 100)
    _make(tmp_path, "a.spec.ts", "y\n" * 60)
    result = compute(tmp_path)
    assert result.detail["test_loc"] == 60


def test_no_source_returns_none(tmp_path: Path) -> None:
    _make(tmp_path, "README.md", "# hi")
    result = compute(tmp_path)
    assert result.score is None


def test_unity_assets_tests_dir(tmp_path: Path) -> None:
    _make(tmp_path, "Assets/Scripts/Game.cs", "x\n" * 100)
    _make(tmp_path, "Assets/Tests/EditMode/GameTests.cs", "y\n" * 30)
    result = compute(tmp_path)
    # Both file-name pattern and directory match — counted once as test
    assert result.detail["test_loc"] == 30
    assert result.detail["src_loc"] == 100
