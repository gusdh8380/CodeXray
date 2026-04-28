import json
from pathlib import Path

from typer.testing import CliRunner

from codexray.cli import app


def _make(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_metrics_emits_valid_json(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "from .b import x\nimport os\n")
    _make(tmp_path, "b.py", "")
    runner = CliRunner()
    result = runner.invoke(app, ["metrics", str(tmp_path)])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["schema_version"] == 1
    assert "nodes" in parsed and isinstance(parsed["nodes"], list)
    assert "graph" in parsed
    assert set(parsed["graph"].keys()) == {
        "node_count",
        "edge_count_internal",
        "edge_count_external",
        "scc_count",
        "largest_scc_size",
        "is_dag",
    }
    assert parsed["graph"]["node_count"] == len(parsed["nodes"])


def test_metrics_node_keys(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "import os\n")
    runner = CliRunner()
    result = runner.invoke(app, ["metrics", str(tmp_path)])
    parsed = json.loads(result.output)
    assert parsed["nodes"]
    keys = set(parsed["nodes"][0].keys())
    assert keys == {"path", "language", "fan_in", "fan_out", "external_fan_out"}


def test_metrics_deterministic(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "from .b import x\n")
    _make(tmp_path, "b.py", "from .a import y\n")  # cycle
    runner = CliRunner()
    one = runner.invoke(app, ["metrics", str(tmp_path)]).output
    two = runner.invoke(app, ["metrics", str(tmp_path)]).output
    assert one == two
    parsed = json.loads(one)
    assert parsed["graph"]["is_dag"] is False


def test_metrics_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["metrics", str(tmp_path / "nope")])
    assert result.exit_code != 0


def test_metrics_empty_tree(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# hi\n")
    runner = CliRunner()
    result = runner.invoke(app, ["metrics", str(tmp_path)])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["nodes"] == []
    assert parsed["graph"]["node_count"] == 0
    assert parsed["graph"]["is_dag"] is True
