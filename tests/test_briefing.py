from __future__ import annotations

import json
import subprocess
from pathlib import Path

from codexray.briefing import build_codebase_briefing, to_json
from codexray.briefing.git_history import build_git_history


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("from b import value\nprint(value)\n")
    (root / "b.py").write_text("value = 1\n")
    (root / "AGENTS.md").write_text("# agent rules\n")
    (root / "openspec" / "changes").mkdir(parents=True)
    (root / "docs" / "validation").mkdir(parents=True)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(
        root,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        message,
    )


def test_briefing_composes_sections_and_serializes(tmp_path: Path) -> None:
    _make_tree(tmp_path)

    briefing = build_codebase_briefing(tmp_path)
    payload = json.loads(to_json(briefing))

    assert briefing.schema_version == 1
    assert "코드베이스 브리핑" in briefing.title
    assert briefing.executive
    assert briefing.architecture
    assert briefing.quality_risk
    assert briefing.build_process
    assert briefing.explain
    assert briefing.deep_dive
    assert briefing.presenter_summary
    assert len(briefing.presentation_slides) == 6
    assert payload["schema_version"] == 1
    assert payload["presenter_summary"] == briefing.presenter_summary
    assert len(payload["presentation_slides"]) == 6
    assert to_json(briefing) == to_json(build_codebase_briefing(tmp_path))


def test_briefing_presentation_slides_have_evidence_and_links(tmp_path: Path) -> None:
    _make_tree(tmp_path)

    briefing = build_codebase_briefing(tmp_path)

    for slide in briefing.presentation_slides:
        assert slide.id
        assert slide.title
        assert slide.eyebrow
        assert slide.narrative
        assert slide.evidence
        assert slide.deep_links


def test_git_history_detects_vibe_process_commits(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "AGENTS.md").write_text("# agent\n")
    _commit(tmp_path, "docs: add agent handbook")
    (tmp_path / "openspec" / "changes" / "demo").mkdir(parents=True)
    (tmp_path / "openspec" / "changes" / "demo" / "proposal.md").write_text("x\n")
    _commit(tmp_path, "feat: add demo proposal")
    (tmp_path / "docs" / "validation").mkdir(parents=True)
    (tmp_path / "docs" / "validation" / "demo.md").write_text("ok\n")
    _commit(tmp_path, "docs: capture validation evidence")

    history = build_git_history(tmp_path)

    assert history.available
    assert history.commit_count == 3
    assert any(item.label == "docs" for item in history.type_distribution)
    categories = {
        category
        for commit in history.process_commits
        for category in commit.process_categories
    }
    assert "에이전트 지침" in categories
    assert "OpenSpec 명세" in categories
    assert "검증 캡처" in categories


def test_git_history_unavailable_for_non_git_path(tmp_path: Path) -> None:
    history = build_git_history(tmp_path)

    assert not history.available
    assert history.unavailable_reason == "not a git repository"
