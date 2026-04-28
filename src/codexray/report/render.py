from __future__ import annotations

from collections import Counter

from .types import ReportData

_HOTSPOT_LIMIT = 5


def to_markdown(data: ReportData) -> str:
    parts: list[str] = []
    parts.append("<!-- codexray-report-v1 -->")
    parts.append(f"# CodeXray Report — `{data.path}`")
    parts.append(f"**Date:** {data.generated_date}")
    parts.append("")
    parts.extend(_overall_section(data))
    parts.append("")
    parts.extend(_strengths_section(data))
    parts.append("")
    parts.extend(_weaknesses_section(data))
    parts.append("")
    parts.extend(_actions_section(data))
    parts.append("")
    parts.extend(_inventory_section(data))
    parts.append("")
    parts.extend(_structure_section(data))
    parts.append("")
    parts.extend(_hotspots_section(data))
    parts.append("")
    parts.extend(_recommendations_section(data))
    parts.append("")
    return "\n".join(parts)


def _strengths_section(data: ReportData) -> list[str]:
    return _summary_section("Strengths", data.summary.strengths)


def _weaknesses_section(data: ReportData) -> list[str]:
    return _summary_section("Weaknesses", data.summary.weaknesses)


def _actions_section(data: ReportData) -> list[str]:
    return _summary_section("Next Actions", data.summary.actions)


def _summary_section(title: str, items) -> list[str]:
    lines = [f"## {title}"]
    if not items:
        lines.append("")
        lines.append("(특이사항 없음)")
        return lines
    lines.append("")
    for i, item in enumerate(items, start=1):
        evidence = _format_summary_evidence(item.evidence)
        lines.append(f"{i}. {item.text} — {evidence}")
    return lines


def _format_summary_evidence(evidence: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in sorted(evidence.items()))


def _overall_section(data: ReportData) -> list[str]:
    overall = data.quality.overall
    score = overall.score if overall.score is not None else "N/A"
    grade = overall.grade if overall.grade is not None else "N/A"
    lines = [
        f"## Overall Grade: {grade} ({score})",
        "",
        "| dimension | grade | score | detail |",
        "| --- | --- | --- | --- |",
    ]
    for name in ("coupling", "cohesion", "documentation", "test"):
        dim = data.quality.dimensions.get(name)
        if dim is None:
            lines.append(f"| {name} | N/A | N/A | — |")
            continue
        score_cell = "N/A" if dim.score is None else str(dim.score)
        grade_cell = "N/A" if dim.grade is None else dim.grade
        detail_cell = _format_detail(dim.detail)
        lines.append(f"| {name} | {grade_cell} | {score_cell} | {detail_cell} |")
    return lines


def _format_detail(detail: dict) -> str:
    if not detail:
        return "—"
    return ", ".join(f"{k}={v}" for k, v in sorted(detail.items()))


def _inventory_section(data: ReportData) -> list[str]:
    lines = ["## Inventory"]
    if not data.inventory:
        lines.append("")
        lines.append("(no source files)")
        return lines
    lines.append("")
    lines.append("| language | file_count | loc | last_modified_at |")
    lines.append("| --- | --- | --- | --- |")
    for row in data.inventory:
        lines.append(
            f"| {row.language} | {row.file_count} | {row.loc} | {row.last_modified_at} |"
        )
    return lines


def _structure_section(data: ReportData) -> list[str]:
    g = data.metrics.graph
    eps = data.entrypoints.entrypoints
    kind_dist = Counter(e.kind for e in eps)
    kind_text = (
        ", ".join(f"{k}={v}" for k, v in sorted(kind_dist.items()))
        if kind_dist
        else "none"
    )
    lines = [
        "## Structure",
        "",
        f"- nodes: {g.node_count}",
        f"- internal edges: {g.edge_count_internal}",
        f"- external edges: {g.edge_count_external}",
        f"- largest SCC: {g.largest_scc_size} (is_dag: {str(g.is_dag).lower()})",
        f"- entrypoints: {len(eps)} ({kind_text})",
    ]
    return lines


def _hotspots_section(data: ReportData) -> list[str]:
    lines = ["## Top Hotspots"]
    candidates = [f for f in data.hotspots.files if f.category == "hotspot"]
    if not candidates:
        lines.append("")
        lines.append("(no hotspots)")
        return lines
    candidates.sort(key=lambda f: (-(f.change_count * f.coupling), f.path))
    top = candidates[:_HOTSPOT_LIMIT]
    lines.append("")
    lines.append("| path | change_count | coupling |")
    lines.append("| --- | --- | --- |")
    for f in top:
        lines.append(f"| `{f.path}` | {f.change_count} | {f.coupling} |")
    return lines


def _recommendations_section(data: ReportData) -> list[str]:
    lines = ["## Recommendations"]
    if not data.recommendations:
        lines.append("")
        lines.append("(no recommendations)")
        return lines
    lines.append("")
    for i, rec in enumerate(data.recommendations, start=1):
        lines.append(f"{i}. {rec.text}")
    return lines
