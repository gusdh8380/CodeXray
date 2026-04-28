from __future__ import annotations

import json
from pathlib import Path

from codexray.vibe import build_vibe_coding_report, to_json


def test_detects_agent_environment_and_process_areas(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# rules\n")
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    (tmp_path / ".claude" / "commands").mkdir()
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    (tmp_path / "openspec" / "specs").mkdir()
    (tmp_path / ".omc").mkdir()
    (tmp_path / ".omc" / "project-memory.json").write_text("{}\n")
    (tmp_path / "docs" / "validation").mkdir(parents=True)
    (tmp_path / "docs" / "vibe-coding").mkdir()
    (tmp_path / ".roboco").mkdir()
    (tmp_path / ".roboco" / "config.json").write_text("{}\n")

    report = build_vibe_coding_report(tmp_path)

    assert report.confidence == "high"
    assert set(report.process_areas) == {
        "agent_instructions",
        "automation",
        "memory_handoff",
        "retrospectives",
        "spec_workflow",
        "validation",
    }
    assert "AGENTS.md" in {item.path for item in report.evidence}
    assert any(item.category == "spec_workflow" for item in report.strengths)


def test_missing_validation_becomes_risk_and_action(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# claude\n")
    (tmp_path / "openspec" / "changes").mkdir(parents=True)

    report = build_vibe_coding_report(tmp_path)

    assert report.confidence == "medium"
    assert any("검증" in item.text for item in report.risks)
    assert any(
        "docs/validation" in path
        for item in report.actions
        for path in item.evidence_paths
    )


def test_no_artifacts_returns_low_confidence_with_missing_evidence(tmp_path: Path) -> None:
    report = build_vibe_coding_report(tmp_path)

    assert report.confidence == "low"
    assert report.confidence_score == 0
    assert report.evidence == ()
    assert report.risks[0].evidence_paths == ("missing:vibe-coding-artifacts",)


def test_vibe_report_serialization_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# rules\n")
    (tmp_path / ".omc").mkdir()
    (tmp_path / ".omc" / "project-memory.json").write_text("{}\n")

    first = to_json(build_vibe_coding_report(tmp_path))
    second = to_json(build_vibe_coding_report(tmp_path))
    payload = json.loads(first)

    assert first == second
    assert payload["schema_version"] == 1
    paths = [item["path"] for item in payload["evidence"]]
    assert paths == ["AGENTS.md", ".omc/project-memory.json"]
    assert all("\\" not in path for path in paths)
