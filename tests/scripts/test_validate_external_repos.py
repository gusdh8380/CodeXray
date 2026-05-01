"""Smoke tests for scripts/validate_external_repos.py.

본 스크립트는 외부 OSS 검증을 위한 dev 도구이지만, JSON 출력 계약과 AI 호출
차단을 회귀 시키지 않으려고 작은 fixture 한 개로 점검한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import validate_external_repos as ver  # noqa: E402


@pytest.fixture()
def minimal_repo(tmp_path: Path) -> Path:
    """git history 가 있는 작은 fixture 레포."""
    import subprocess

    (tmp_path / "README.md").write_text(
        "# fixture\n\nThis is a tiny fixture used to test analysis.\n",
        encoding="utf-8",
    )
    (tmp_path / "main.py").write_text("print('hi')\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@e", "-c", "user.name=t", "add", "."],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@e",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "-m",
            "init",
        ],
        cwd=tmp_path,
        check=True,
    )
    return tmp_path


def test_collect_one_returns_payload(minimal_repo: Path) -> None:
    payload = ver.collect_one(minimal_repo)
    assert isinstance(payload, dict)
    assert "detected" in payload
    assert "blind_spots" in payload


def test_main_writes_json(minimal_repo: Path, tmp_path: Path, capsys) -> None:
    out_dir = tmp_path / "out"
    code = ver.main(
        [str(minimal_repo), "--output-dir", str(out_dir)]
    )
    assert code == 0
    files = list(out_dir.glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert "detected" in payload
    captured = capsys.readouterr()
    assert "[OK]" in captured.out


def test_main_no_paths_errors(capsys) -> None:
    with pytest.raises(SystemExit):
        ver.main([])
