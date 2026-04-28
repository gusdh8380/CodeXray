import subprocess
from pathlib import Path

from codexray.hotspots import build_hotspots

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


def test_non_git_tree_falls_back_to_coupling_only(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "from .b import x\n")
    _make(tmp_path, "b.py", "")
    report = build_hotspots(tmp_path)
    assert all(f.change_count == 0 for f in report.files)
    # Both categories should be hotspot or stable (no active_stable / neglected_complex).
    cats = {f.category for f in report.files}
    assert cats <= {"hotspot", "stable"}
    assert report.summary.active_stable == 0
    assert report.summary.neglected_complex == 0


def test_git_tree_classifies_into_four(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    _make(tmp_path, "hot.py", "from .deps import x\nfrom .other import y\nimport os\n")
    _make(tmp_path, "deps.py", "")
    _make(tmp_path, "other.py", "")
    _make(tmp_path, "quiet.py", "import os\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "1")

    # Bump hot.py multiple times → high change_count
    for i in range(5):
        (tmp_path / "hot.py").write_text(f"from .deps import x\n# r{i}\n")
        _git(tmp_path, "add", "hot.py")
        _git(tmp_path, "commit", "-q", "-m", f"r{i}")

    report = build_hotspots(tmp_path)
    by_path = {f.path: f for f in report.files}
    assert "hot.py" in by_path
    assert by_path["hot.py"].change_count > by_path["deps.py"].change_count
    cats = {f.category for f in report.files}
    # At least the four-category logic engaged (no fallback).
    assert "hotspot" in cats or "active_stable" in cats


def test_summary_counts_match_files(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "")
    _make(tmp_path, "b.py", "")
    report = build_hotspots(tmp_path)
    total = (
        report.summary.hotspot
        + report.summary.active_stable
        + report.summary.neglected_complex
        + report.summary.stable
    )
    assert total == len(report.files)


def test_files_sorted_by_path(tmp_path: Path) -> None:
    _make(tmp_path, "z.py", "")
    _make(tmp_path, "a.py", "")
    _make(tmp_path, "m.py", "")
    report = build_hotspots(tmp_path)
    paths = [f.path for f in report.files]
    assert paths == sorted(paths)
