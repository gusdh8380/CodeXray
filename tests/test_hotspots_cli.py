import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from codexray.cli import app

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def _init_git(cwd: Path) -> None:
    subprocess.run(
        ["git", "init", "-q"],
        cwd=cwd,
        check=True,
        env=_GIT_ENV,
        capture_output=True,
    )


def _make(tmp: Path, name: str, content: str) -> None:
    p = tmp / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def test_hotspots_emits_valid_schema(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    _make(tmp_path, "b.py", "import sys\n")
    runner = CliRunner()
    result = runner.invoke(app, ["hotspots", str(tmp_path)])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["schema_version"] == 1
    assert set(parsed["thresholds"].keys()) == {"change_count_median", "coupling_median"}
    assert set(parsed["summary"].keys()) == {
        "hotspot",
        "active_stable",
        "neglected_complex",
        "stable",
    }


def test_hotspots_file_keys(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    runner = CliRunner()
    result = runner.invoke(app, ["hotspots", str(tmp_path)])
    parsed = json.loads(result.output)
    if parsed["files"]:
        keys = set(parsed["files"][0].keys())
        assert keys == {"path", "change_count", "coupling", "category"}


def test_hotspots_deterministic(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    _make(tmp_path, "b.py", "import sys\n")
    runner = CliRunner()
    one = runner.invoke(app, ["hotspots", str(tmp_path)]).output
    two = runner.invoke(app, ["hotspots", str(tmp_path)]).output
    assert one == two


def test_hotspots_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["hotspots", str(tmp_path / "nope")])
    assert result.exit_code != 0


def test_hotspots_empty_tree(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "README.md", "# hi\n")
    runner = CliRunner()
    result = runner.invoke(app, ["hotspots", str(tmp_path)])
    parsed = json.loads(result.output)
    assert parsed["files"] == []
    assert parsed["summary"] == {
        "hotspot": 0,
        "active_stable": 0,
        "neglected_complex": 0,
        "stable": 0,
    }
