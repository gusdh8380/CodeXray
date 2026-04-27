import os
from pathlib import Path

from codexray.walk import walk


def _names(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in walk(root)}


def test_default_ignore_dirs_excluded(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("x = 1\n")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "lib.js").write_text("console.log(1)\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main\n")

    assert _names(tmp_path) == {"src/main.py"}


def test_gitignore_pattern_excluded(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("*.log\n")
    (tmp_path / "app.log").write_text("noise\n")
    (tmp_path / "main.py").write_text("x = 1\n")

    assert _names(tmp_path) == {".gitignore", "main.py"}


def test_no_gitignore_only_default_ignores(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("x = 1\n")
    (tmp_path / "data.log").write_text("kept\n")
    (tmp_path / "venv").mkdir()
    (tmp_path / "venv" / "lib.py").write_text("y = 2\n")

    assert _names(tmp_path) == {"main.py", "data.log"}


def test_symlinks_not_followed(tmp_path: Path) -> None:
    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "main.py").write_text("x = 1\n")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("y = 2\n")
    os.symlink(outside, tmp_path / "real" / "linked")

    names = _names(tmp_path)
    assert "real/main.py" in names
    assert "outside/secret.py" in names  # discovered as a sibling, not via the link
    assert not any("linked" in n for n in names)
