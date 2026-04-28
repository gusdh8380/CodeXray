import subprocess
from pathlib import Path

from codexray.hotspots.git_log import change_counts, is_git_repo

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


def test_is_git_repo_true(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    assert is_git_repo(tmp_path) is True


def test_is_git_repo_false(tmp_path: Path) -> None:
    assert is_git_repo(tmp_path) is False


def test_change_counts_tracks_per_file(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.py").write_text("x\n")
    (tmp_path / "b.py").write_text("y\n")
    _git(tmp_path, "add", "a.py", "b.py")
    _git(tmp_path, "commit", "-q", "-m", "1")

    (tmp_path / "a.py").write_text("x\nz\n")
    _git(tmp_path, "add", "a.py")
    _git(tmp_path, "commit", "-q", "-m", "2")

    (tmp_path / "a.py").write_text("x\nz\nq\n")
    _git(tmp_path, "add", "a.py")
    _git(tmp_path, "commit", "-q", "-m", "3")

    counts = change_counts(tmp_path, {"a.py", "b.py"})
    assert counts["a.py"] == 3
    assert counts["b.py"] == 1


def test_change_counts_filters_to_allowed(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.py").write_text("x\n")
    (tmp_path / "README.md").write_text("# hi\n")
    _git(tmp_path, "add", "a.py", "README.md")
    _git(tmp_path, "commit", "-q", "-m", "1")

    counts = change_counts(tmp_path, {"a.py"})
    assert counts == {"a.py": 1}
    assert "README.md" not in counts


def test_change_counts_non_git_returns_empty(tmp_path: Path) -> None:
    counts = change_counts(tmp_path, {"a.py"})
    assert counts == {}
