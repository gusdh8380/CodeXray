from pathlib import Path

from typer.testing import CliRunner

from codexray.cli import app


def test_inventory_runs_against_tmp_tree(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n")
    (tmp_path / "b.ts").write_text("export const z = 1;\nconsole.log(z);\n")

    runner = CliRunner()
    result = runner.invoke(app, ["inventory", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Python" in result.output
    assert "TypeScript" in result.output
    assert "language" in result.output
    assert "loc" in result.output


def test_inventory_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    missing = tmp_path / "nope"
    result = runner.invoke(app, ["inventory", str(missing)])
    assert result.exit_code != 0
    assert "does not exist" in (result.output + (result.stderr or ""))


def test_inventory_rejects_file_path(tmp_path: Path) -> None:
    f = tmp_path / "f.txt"
    f.write_text("x")
    runner = CliRunner()
    result = runner.invoke(app, ["inventory", str(f)])
    assert result.exit_code != 0
    assert "not a directory" in (result.output + (result.stderr or ""))


def test_no_args_shows_help_and_exits_nonzero() -> None:
    runner = CliRunner()
    result = runner.invoke(app, [])
    assert result.exit_code != 0


def test_empty_tree_emits_only_header(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# hi\n")
    runner = CliRunner()
    result = runner.invoke(app, ["inventory", str(tmp_path)])
    assert result.exit_code == 0
    assert "language" in result.output
    assert "Python" not in result.output
    assert "TypeScript" not in result.output
