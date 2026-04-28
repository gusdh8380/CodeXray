import json
from pathlib import Path

from typer.testing import CliRunner

from codexray.cli import app


def _make(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_entrypoints_combined_tree(tmp_path: Path) -> None:
    _make(
        tmp_path,
        "pyproject.toml",
        '[project]\nname="x"\n[project.scripts]\ncli = "x:main"\n',
    )
    _make(tmp_path, "package.json", '{"bin": "./bin/x.js"}')
    _make(tmp_path, "main.py", 'if __name__ == "__main__":\n    pass\n')
    _make(tmp_path, "Program.cs", "static void Main(string[] args) {}\n")
    _make(
        tmp_path,
        "Player.cs",
        "class Player : MonoBehaviour { void Update() {} }\n",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["entrypoints", str(tmp_path)])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["schema_version"] == 1
    kinds = {e["kind"] for e in parsed["entrypoints"]}
    assert kinds == {
        "pyproject_script",
        "package_bin",
        "main_guard",
        "main_method",
        "unity_lifecycle",
    }


def test_entrypoints_deterministic(tmp_path: Path) -> None:
    _make(tmp_path, "main.py", 'if __name__ == "__main__":\n    pass\n')
    _make(tmp_path, "Program.cs", "static void Main() {}\n")
    runner = CliRunner()
    one = runner.invoke(app, ["entrypoints", str(tmp_path)]).output
    two = runner.invoke(app, ["entrypoints", str(tmp_path)]).output
    assert one == two


def test_entrypoints_empty_tree(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["entrypoints", str(tmp_path)])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed["entrypoints"] == []


def test_entrypoints_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["entrypoints", str(tmp_path / "nope")])
    assert result.exit_code != 0


def test_entry_object_keys(tmp_path: Path) -> None:
    _make(tmp_path, "main.py", 'if __name__ == "__main__":\n    pass\n')
    runner = CliRunner()
    result = runner.invoke(app, ["entrypoints", str(tmp_path)])
    parsed = json.loads(result.output)
    assert parsed["entrypoints"]
    keys = set(parsed["entrypoints"][0].keys())
    assert keys == {"path", "language", "kind", "detail"}
