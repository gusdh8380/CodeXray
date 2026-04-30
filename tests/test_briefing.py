from __future__ import annotations

import json
import subprocess
from pathlib import Path

from codexray.briefing import build_codebase_briefing, to_json
from codexray.briefing.git_history import build_git_history
from codexray.web.briefing_payload import SCHEMA_VERSION, build_briefing_payload


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
    assert len(briefing.presentation_slides) == 7
    assert payload["schema_version"] == 1
    assert payload["presenter_summary"] == briefing.presenter_summary
    assert len(payload["presentation_slides"]) == 7
    assert to_json(briefing) == to_json(build_codebase_briefing(tmp_path))


def test_briefing_presentation_slides_have_evidence_and_links(tmp_path: Path) -> None:
    _make_tree(tmp_path)

    briefing = build_codebase_briefing(tmp_path)

    for slide in briefing.presentation_slides:
        assert slide.id
        assert slide.title
        assert slide.eyebrow
        assert slide.narrative
        assert slide.summary
        assert slide.meaning
        assert slide.risk
        assert slide.action
        assert slide.evidence
        assert slide.deep_links


def test_briefing_process_slide_explains_creation_story(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "AGENTS.md").write_text("# agent\n")
    _commit(tmp_path, "docs: add agent handbook")
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    (tmp_path / ".claude" / "skills" / "demo.md").write_text("x\n")
    _commit(tmp_path, "chore: add agent skill")

    briefing = build_codebase_briefing(tmp_path)
    process = next(slide for slide in briefing.presentation_slides if slide.id == "process")

    assert "commit" in process.summary
    assert "프로세스" in process.meaning or "process" in process.meaning
    assert process.risk
    assert process.action


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


def test_briefing_payload_has_five_sections_and_schema_version(tmp_path: Path) -> None:
    _make_tree(tmp_path)

    payload = build_briefing_payload(tmp_path, ai=None)

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["path"] == str(tmp_path.resolve())
    assert payload["ai_used"] is False

    for section_id in ("what", "how_built", "current_state"):
        section = payload[section_id]
        assert section["id"] == section_id
        assert section["title"]
        assert section["narrative"]
        assert isinstance(section["metrics"], list) and section["metrics"]

    vibe_insights = payload["vibe_insights"]
    assert "detected" in vibe_insights
    assert "axes" in vibe_insights

    next_actions = payload["next_actions"]
    assert isinstance(next_actions, list) and next_actions
    allowed_categories = {"code", "structural", "vibe_coding"}
    for action in next_actions:
        assert action["action"]
        assert action["reason"]
        assert action["evidence"]
        assert action["category"] in allowed_categories
    by_category: dict[str, list[dict]] = {}
    for a in next_actions:
        by_category.setdefault(a["category"], []).append(a)
    for items in by_category.values():
        assert len(items) <= 3
    assert any(a["category"] == "vibe_coding" for a in next_actions), (
        "vibe_coding 카테고리는 starter_guide(미감지) 또는 axes 약점(감지)에서 합성되어야 함"
    )


def test_briefing_payload_serializes_as_json(tmp_path: Path) -> None:
    _make_tree(tmp_path)

    payload = build_briefing_payload(tmp_path, ai=None)
    serialized = json.dumps(payload)
    roundtrip = json.loads(serialized)

    assert roundtrip["schema_version"] == SCHEMA_VERSION
    assert {"what", "how_built", "current_state", "vibe_insights", "next_actions"}.issubset(
        roundtrip.keys()
    )
