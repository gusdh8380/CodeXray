import json
import subprocess
from pathlib import Path

from codexray.ai import build_review

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


def _wrap(payload: dict) -> str:
    return f"```json\n{json.dumps(payload)}\n```"


def _valid_response_for(max_line: int) -> str:
    return _wrap(
        {
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
    )


class FakeAdapter:
    name = "fake"

    def __init__(self, response: str) -> None:
        self._response = response
        self.calls = 0

    def review(self, prompt: str, timeout: int = 120) -> str:
        self.calls += 1
        return self._response


class FailingAdapter:
    name = "fake"

    def review(self, prompt: str, timeout: int = 120) -> str:
        return "no json here, just narrative text"


def _seed_hotspot_tree(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    _make(tmp_path, "hot.py", "from .other import x\nimport os\n")
    _make(tmp_path, "other.py", "x = 1\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    for i in range(4):
        (tmp_path / "hot.py").write_text(
            f"from .other import x\nimport os\n# r{i}\n"
        )
        _git(tmp_path, "add", "hot.py")
        _git(tmp_path, "commit", "-q", "-m", f"r{i}")


def test_build_review_with_valid_responses(tmp_path: Path) -> None:
    _seed_hotspot_tree(tmp_path)
    adapter = FakeAdapter(_valid_response_for(10))
    result = build_review(tmp_path, top_n=5, adapter=adapter)
    assert result.backend == "fake"
    assert result.files_reviewed >= 1
    assert all(r.confidence == "medium" for r in result.reviews)
    assert all(len(r.dimensions) == 4 for r in result.reviews)
    assert adapter.calls == result.files_reviewed + len(result.skipped)


def test_build_review_invalid_response_skipped(tmp_path: Path) -> None:
    _seed_hotspot_tree(tmp_path)
    adapter = FailingAdapter()
    result = build_review(tmp_path, top_n=5, adapter=adapter)
    assert result.files_reviewed == 0
    assert len(result.skipped) >= 1
    assert all(s.reason for s in result.skipped)


def test_build_review_top_n_caps(tmp_path: Path) -> None:
    _seed_hotspot_tree(tmp_path)
    adapter = FakeAdapter(_valid_response_for(10))
    result = build_review(tmp_path, top_n=1, adapter=adapter)
    # At most 1 review/skipped combined.
    assert len(result.reviews) + len(result.skipped) <= 1


def test_build_review_no_hotspots(tmp_path: Path) -> None:
    # No git, no source — hotspots empty, builder should produce empty output.
    _make(tmp_path, "README.md", "# hi\n")
    adapter = FakeAdapter(_valid_response_for(10))
    result = build_review(tmp_path, top_n=5, adapter=adapter)
    assert result.files_reviewed == 0
    assert result.reviews == ()
    assert result.skipped == ()
    assert adapter.calls == 0


def test_build_review_sorted_by_path(tmp_path: Path) -> None:
    _seed_hotspot_tree(tmp_path)
    adapter = FakeAdapter(_valid_response_for(10))
    result = build_review(tmp_path, top_n=5, adapter=adapter)
    paths = [r.path for r in result.reviews]
    assert paths == sorted(paths)
