import json
from pathlib import Path

from typer.testing import CliRunner

from codexray.cli import app


def _make(tmp_path: Path, name: str, content: str) -> None:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def test_quality_emits_valid_schema(tmp_path: Path) -> None:
    _make(
        tmp_path,
        "src/a.py",
        '"""mod."""\n\ndef f():\n    """doc."""\n    return 1\n',
    )
    _make(
        tmp_path,
        "tests/test_a.py",
        "from src import a\n\ndef test_f():\n    assert a.f() == 1\n",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["quality", str(tmp_path)])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["schema_version"] == 1
    assert "overall" in parsed
    assert set(parsed["dimensions"].keys()) == {
        "coupling",
        "cohesion",
        "documentation",
        "test",
    }


def test_quality_overall_average(tmp_path: Path) -> None:
    # Trivial tree: one Python module, one test
    _make(tmp_path, "a.py", '"""mod."""\n')
    _make(tmp_path, "test_a.py", "x\n")
    runner = CliRunner()
    result = runner.invoke(app, ["quality", str(tmp_path)])
    parsed = json.loads(result.output)
    measurable = [
        d["score"] for d in parsed["dimensions"].values() if d["score"] is not None
    ]
    if measurable:
        expected = round(sum(measurable) / len(measurable))
        assert parsed["overall"]["score"] == expected


def test_quality_empty_tree_overall_null(tmp_path: Path) -> None:
    _make(tmp_path, "README.md", "# hi\n")
    runner = CliRunner()
    result = runner.invoke(app, ["quality", str(tmp_path)])
    parsed = json.loads(result.output)
    assert parsed["overall"]["score"] is None
    assert parsed["overall"]["grade"] is None


def test_quality_deterministic(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "import os\n")
    _make(tmp_path, "test_a.py", "x\n")
    runner = CliRunner()
    one = runner.invoke(app, ["quality", str(tmp_path)]).output
    two = runner.invoke(app, ["quality", str(tmp_path)]).output
    assert one == two


def test_quality_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["quality", str(tmp_path / "nope")])
    assert result.exit_code != 0
