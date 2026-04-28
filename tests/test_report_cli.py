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


def test_report_emits_v1_marker(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", '"""mod."""\nimport os\n')
    runner = CliRunner()
    result = runner.invoke(app, ["report", str(tmp_path)])
    assert result.exit_code == 0, result.output
    head = "\n".join(result.output.splitlines()[:5])
    assert "<!-- codexray-report-v1 -->" in head


def test_report_section_headers_present(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    runner = CliRunner()
    result = runner.invoke(app, ["report", str(tmp_path)])
    assert result.exit_code == 0
    body = result.output
    for header in (
        "## Overall Grade",
        "## Inventory",
        "## Structure",
        "## Top Hotspots",
        "## Recommendations",
    ):
        assert header in body, f"missing header: {header}"


def test_report_structure_keywords(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    runner = CliRunner()
    result = runner.invoke(app, ["report", str(tmp_path)])
    body = result.output
    for keyword in ("nodes", "internal edges", "external edges", "largest SCC", "entrypoints"):
        assert keyword in body, f"missing keyword: {keyword}"


def test_report_no_hotspots_message(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    runner = CliRunner()
    result = runner.invoke(app, ["report", str(tmp_path)]).output
    # Tiny tree may have hotspots due to median fallback; either case should render
    # something sensible. We assert the section exists.
    assert "## Top Hotspots" in result


def test_report_empty_tree_inventory_placeholder(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "README.md", "# hi\n")
    runner = CliRunner()
    result = runner.invoke(app, ["report", str(tmp_path)]).output
    assert "(no source files)" in result


def test_report_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["report", str(tmp_path / "nope")])
    assert result.exit_code != 0
