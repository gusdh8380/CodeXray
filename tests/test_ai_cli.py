import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from codexray.cli import app

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, env=_GIT_ENV, capture_output=True
    )


def _make(tmp: Path, name: str, content: str) -> None:
    p = tmp / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def _parse_json(output: str) -> dict:
    """Extract JSON payload from CLI output, skipping any leading stderr noise."""
    start = output.find("{")
    assert start != -1, f"no JSON found in output: {output!r}"
    return json.loads(output[start:])


def _valid_response() -> str:
    payload = {
        "dimensions": {
            "readability": {
                "score": 80,
                "evidence_lines": [1],
                "comment": "ok",
                "suggestion": "minor",
            },
            "design": {
                "score": 70,
                "evidence_lines": [1],
                "comment": "ok",
                "suggestion": "minor",
            },
            "maintainability": {
                "score": 75,
                "evidence_lines": [1],
                "comment": "ok",
                "suggestion": "minor",
            },
            "risk": {
                "score": 90,
                "evidence_lines": [1],
                "comment": "ok",
                "suggestion": "minor",
            },
        },
        "confidence": "medium",
        "limitations": "no caller context",
    }
    return f"```json\n{json.dumps(payload)}\n```"


class FakeAdapter:
    name = "fake"

    def review(self, prompt: str, timeout: int = 120) -> str:
        return _valid_response()


def _seed(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    _make(tmp_path, "hot.py", "from .other import x\n")
    _make(tmp_path, "other.py", "x = 1\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    for i in range(3):
        (tmp_path / "hot.py").write_text(f"from .other import x\n# r{i}\n")
        _git(tmp_path, "add", "hot.py")
        _git(tmp_path, "commit", "-q", "-m", f"r{i}")


def test_review_emits_valid_schema(tmp_path: Path) -> None:
    _seed(tmp_path)
    runner = CliRunner()
    with patch("codexray.cli.select_adapter", return_value=FakeAdapter()):
        result = runner.invoke(app, ["review", str(tmp_path)])
    assert result.exit_code == 0, result.output
    parsed = _parse_json(result.output)
    assert parsed["schema_version"] == 1
    assert parsed["backend"] == "fake"
    assert isinstance(parsed["reviews"], list)
    assert isinstance(parsed["skipped"], list)
    if parsed["reviews"]:
        review = parsed["reviews"][0]
        assert set(review.keys()) == {
            "path",
            "dimensions",
            "confidence",
            "limitations",
        }
        assert set(review["dimensions"].keys()) == {
            "readability",
            "design",
            "maintainability",
            "risk",
        }


def test_review_rejects_missing_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["review", str(tmp_path / "nope")])
    assert result.exit_code != 0


def test_review_no_backend_clean_error(tmp_path: Path) -> None:
    from codexray.ai import AIAdapterError

    _seed(tmp_path)
    runner = CliRunner()
    with patch(
        "codexray.cli.select_adapter",
        side_effect=AIAdapterError("no AI backend available"),
    ):
        result = runner.invoke(app, ["review", str(tmp_path)])
    assert result.exit_code != 0


def test_review_top_n_env_override(tmp_path: Path) -> None:
    _seed(tmp_path)
    runner = CliRunner()
    with patch("codexray.cli.select_adapter", return_value=FakeAdapter()):
        result = runner.invoke(
            app,
            ["review", str(tmp_path)],
            env={"CODEXRAY_AI_TOP_N": "1"},
        )
    parsed = _parse_json(result.output)
    # At most 1 file processed (review or skipped)
    assert len(parsed["reviews"]) + len(parsed["skipped"]) <= 1


def test_review_invalid_top_n(tmp_path: Path) -> None:
    _seed(tmp_path)
    runner = CliRunner()
    with patch("codexray.cli.select_adapter", return_value=FakeAdapter()):
        result = runner.invoke(
            app,
            ["review", str(tmp_path)],
            env={"CODEXRAY_AI_TOP_N": "abc"},
        )
    assert result.exit_code != 0
