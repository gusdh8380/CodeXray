from __future__ import annotations

from pathlib import Path

from codexray.report import build_report, to_markdown


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("from .b import value\n")
    (root / "b.py").write_text("value = 1\n")
    (root / "README.md").write_text("# example\n")


def test_three_sections_present(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    md = to_markdown(build_report(tmp_path))
    assert "## Strengths" in md
    assert "## Weaknesses" in md
    assert "## Next Actions" in md


def test_three_sections_between_overall_and_hotspots(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    md = to_markdown(build_report(tmp_path))
    overall_idx = md.index("## Overall Grade")
    strengths_idx = md.index("## Strengths")
    weaknesses_idx = md.index("## Weaknesses")
    actions_idx = md.index("## Next Actions")
    hotspots_idx = md.index("## Top Hotspots")
    assert overall_idx < strengths_idx < weaknesses_idx < actions_idx < hotspots_idx


def test_fallback_text_when_empty(tmp_path: Path) -> None:
    # 작은 트리에서 보통 hotspot 없음 → strengths 비어있을 수 있음.
    _make_tree(tmp_path)
    md = to_markdown(build_report(tmp_path))
    # 적어도 한 섹션은 존재하고, 비어있다면 fallback 텍스트.
    assert "## Strengths" in md
    if "(특이사항 없음)" not in md:
        # 비어있지 않다면 1~3 항목.
        section = md.split("## Strengths", 1)[1].split("##", 1)[0]
        bullets = [
            line for line in section.splitlines()
            if line.strip().startswith(("1.", "2.", "3."))
        ]
        assert 1 <= len(bullets) <= 3


def test_marker_still_first_line(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    md = to_markdown(build_report(tmp_path))
    first_lines = md.splitlines()[:5]
    assert any("codexray-report-v1" in line for line in first_lines)


def test_byte_determinism(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    md1 = to_markdown(build_report(tmp_path))
    md2 = to_markdown(build_report(tmp_path))
    assert md1 == md2
