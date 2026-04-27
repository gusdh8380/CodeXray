import json
from pathlib import Path

from typer.testing import CliRunner

from codexray.cli import app


def test_graph_cli_emits_valid_json(tmp_path: Path) -> None:
    (tmp_path / "util.ts").write_text("export const z = 1;\n")
    (tmp_path / "main.ts").write_text('import { z } from "./util";\n')
    runner = CliRunner()
    result = runner.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["schema_version"] == 1
    paths = sorted(n["path"] for n in parsed["nodes"])
    assert paths == ["main.ts", "util.ts"]
    assert any(
        e["from"] == "main.ts" and e["to"] == "util.ts" and e["kind"] == "internal"
        for e in parsed["edges"]
    )


def test_graph_cli_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["graph", str(tmp_path / "nope")])
    assert result.exit_code != 0


def test_graph_cli_empty_tree(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# hi\n")
    runner = CliRunner()
    result = runner.invoke(app, ["graph", str(tmp_path)])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["schema_version"] == 1
    assert parsed["nodes"] == []
    assert parsed["edges"] == []
