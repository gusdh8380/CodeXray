from __future__ import annotations

from pathlib import Path

from codexray.briefing.git_history import build_git_history
from codexray.hotspots import build_hotspots
from codexray.quality import build_quality
from codexray.vibe import build_vibe_coding_report
from codexray.vibe_insights import build_vibe_insights
from codexray.vibe_insights.detection import detect_vibe_coding


def _make_simple_tree(root: Path) -> None:
    (root / "a.py").write_text("from .b import value\n")
    (root / "b.py").write_text("value = 1\n")
    (root / "README.md").write_text("# example\n")


def test_detect_vibe_coding_strong_signal_claude_md(tmp_path: Path) -> None:
    _make_simple_tree(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("# agent\n")
    vibe = build_vibe_coding_report(tmp_path)
    history = build_git_history(tmp_path)
    assert detect_vibe_coding(root=tmp_path, vibe=vibe, history=history) is True


def test_detect_vibe_coding_no_signal(tmp_path: Path) -> None:
    _make_simple_tree(tmp_path)
    vibe = build_vibe_coding_report(tmp_path)
    history = build_git_history(tmp_path)
    assert detect_vibe_coding(root=tmp_path, vibe=vibe, history=history) is False


def test_build_vibe_insights_detected_returns_three_axes(tmp_path: Path) -> None:
    _make_simple_tree(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("# agent\n" + "x" * 600)  # exceed _MIN_GUIDE_SIZE
    (tmp_path / "openspec").mkdir()
    payload = _run(tmp_path)
    assert payload["detected"] is True
    axis_names = {a["name"] for a in payload["axes"]}
    assert axis_names == {"intent", "verification", "continuity"}
    for axis in payload["axes"]:
        assert axis["state"] in {"strong", "moderate", "weak", "unknown"}
        assert axis["signal_pool_size"] == 3
        assert 0 <= axis["signal_count"] <= 3
        assert 0.0 <= axis["signal_ratio"] <= 1.0


def test_build_vibe_insights_detected_includes_blind_spots_and_proxies(
    tmp_path: Path,
) -> None:
    # Decision 6 + 8 — blind_spots 항상 4 항목, process_proxies 분리.
    _make_simple_tree(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("# agent\n" + "x" * 600)
    (tmp_path / "openspec").mkdir()
    payload = _run(tmp_path)
    assert payload["detected"] is True
    assert "blind_spots" in payload
    assert isinstance(payload["blind_spots"], list)
    assert len(payload["blind_spots"]) == 4
    assert "process_proxies" in payload
    proxies = payload["process_proxies"]
    assert "available" in proxies and "items" in proxies and "note" in proxies


def test_build_vibe_insights_not_detected_returns_none(tmp_path: Path) -> None:
    # vibe-detection-rebalance: 비감지 시 None 반환 (이전: starter_guide 포함 dict)
    _make_simple_tree(tmp_path)
    payload = _run(tmp_path)
    assert payload is None


def test_build_vibe_insights_uses_ai_key_insight_when_provided(tmp_path: Path) -> None:
    _make_simple_tree(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("# agent\n")
    payload = _run(tmp_path, ai_key_insight="AI가 작성한 종합 해석")
    assert payload["ai_narrative"] == "AI가 작성한 종합 해석"


# --- vibe-signal-pool-expand: 신규 신호별 단위 테스트 ---


def test_pyproject_description_long_counts_as_intent_signal(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_project_intent_doc

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndescription = "A long enough description for the intent signal."\n',
        encoding="utf-8",
    )
    sig = _check_project_intent_doc(tmp_path)
    assert sig["present"] is True
    assert "pyproject" in sig["evidence"]


def test_pyproject_description_empty_does_not_count(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_project_intent_doc

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndescription = ""\n',
        encoding="utf-8",
    )
    sig = _check_project_intent_doc(tmp_path)
    assert sig["present"] is False


def test_package_json_description_with_keywords_counts(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_project_intent_doc

    (tmp_path / "package.json").write_text(
        '{"name":"x","description":"short","keywords":["cli","tool"]}',
        encoding="utf-8",
    )
    sig = _check_project_intent_doc(tmp_path)
    assert sig["present"] is True
    assert "package.json" in sig["evidence"]


def test_readme_what_section_header_counts_as_intent(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_project_intent_doc

    # 첫 5 단락에 키워드 없음 — 섹션 헤더가 유일한 신호.
    # _has_purpose_paragraph 의 len >= 200 가드 통과를 위해 padding.
    pad = "neutral content with no signal here. " * 8  # ~ 280 chars
    body = (
        "# title\n\n"
        + pad
        + "\n\n"
        + ("filler\n\n" * 6)
        + "## What\n\nThis is what.\n"
    )
    (tmp_path / "README.md").write_text(body, encoding="utf-8")
    sig = _check_project_intent_doc(tmp_path)
    assert sig["present"] is True


def test_examples_dir_nonempty_counts_as_validation(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_manual_validation

    (tmp_path / "examples").mkdir()
    (tmp_path / "examples" / "demo.py").write_text("print('hi')\n", encoding="utf-8")
    sig = _check_manual_validation(tmp_path)
    assert sig["present"] is True
    assert "examples" in sig["evidence"]


def test_examples_dir_empty_does_not_count(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_manual_validation

    (tmp_path / "examples").mkdir()
    sig = _check_manual_validation(tmp_path)
    assert sig["present"] is False


def test_maintainers_md_counts_as_handoff(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_handoff_doc

    (tmp_path / "MAINTAINERS.md").write_text("- @alice\n", encoding="utf-8")
    sig = _check_handoff_doc(tmp_path)
    assert sig["present"] is True
    assert "MAINTAINERS" in sig["evidence"]


def test_docs_getting_started_counts_as_handoff(tmp_path: Path) -> None:
    from codexray.vibe_insights.axes import _check_handoff_doc

    (tmp_path / "docs" / "getting-started").mkdir(parents=True)
    sig = _check_handoff_doc(tmp_path)
    assert sig["present"] is True
    assert "getting-started" in sig["evidence"]


def _run(root: Path, ai_key_insight: str | None = None) -> dict[str, object]:
    vibe = build_vibe_coding_report(root)
    quality = build_quality(root)
    hotspots = build_hotspots(root)
    history = build_git_history(root)
    return build_vibe_insights(
        root=root,
        vibe=vibe,
        quality=quality,
        hotspots=hotspots,
        history=history,
        ai_key_insight=ai_key_insight,
    )
