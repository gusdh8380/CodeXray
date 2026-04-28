import json
import re
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from codexray.cli import app
from codexray.dashboard import build_dashboard, to_html

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


_DATA_BLOCK_RE = re.compile(
    r'<script type="application/json" id="(codexray-data-[a-z]+)">'
    r"(.+?)</script>",
    re.DOTALL,
)


def _extract_blocks(html: str) -> dict[str, dict]:
    blocks: dict[str, dict] = {}
    for match in _DATA_BLOCK_RE.finditer(html):
        blocks[match.group(1)] = json.loads(match.group(2))
    return blocks


def test_html_contains_v1_marker(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    data = build_dashboard(tmp_path)
    html = to_html(data)
    head = "\n".join(html.splitlines()[:5])
    assert "<!-- codexray-dashboard-v1 -->" in head


def test_html_contains_d3_cdn(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    html = to_html(build_dashboard(tmp_path))
    matches = re.findall(r"<script[^>]*src=\"[^\"]*d3@7[^\"]*\"", html)
    assert len(matches) == 1


def test_html_has_six_data_blocks(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    html = to_html(build_dashboard(tmp_path))
    blocks = _extract_blocks(html)
    assert set(blocks.keys()) == {
        "codexray-data-inventory",
        "codexray-data-graph",
        "codexray-data-metrics",
        "codexray-data-entrypoints",
        "codexray-data-quality",
        "codexray-data-hotspots",
    }


def test_data_blocks_parseable(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "from .b import x\n")
    _make(tmp_path, "b.py", "x = 1\n")
    html = to_html(build_dashboard(tmp_path))
    blocks = _extract_blocks(html)
    assert blocks["codexray-data-graph"]["nodes"]
    assert blocks["codexray-data-quality"]["schema_version"] == 1
    assert "files" in blocks["codexray-data-hotspots"]


def test_header_includes_path_and_grade(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    data = build_dashboard(tmp_path)
    html = to_html(data)
    assert str(tmp_path.resolve()) in html
    # Either a real grade or N/A.
    assert any(token in html for token in ("Grade: <strong>", "N/A"))


def test_empty_tree_n_a(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "README.md", "# hi\n")
    html = to_html(build_dashboard(tmp_path))
    assert "N/A" in html


def test_deterministic_for_fixed_date(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "from .b import x\n")
    _make(tmp_path, "b.py", "x = 1\n")
    one = build_dashboard(tmp_path)
    two = build_dashboard(tmp_path)
    object.__setattr__(two, "generated_date", one.generated_date)
    assert to_html(one) == to_html(two)


def test_cli_dashboard_emits_html(tmp_path: Path) -> None:
    _init_git(tmp_path)
    _make(tmp_path, "a.py", "import os\n")
    runner = CliRunner()
    result = runner.invoke(app, ["dashboard", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "<!-- codexray-dashboard-v1 -->" in result.output
    assert "codexray-data-graph" in result.output


def test_cli_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["dashboard", str(tmp_path / "nope")])
    assert result.exit_code != 0
