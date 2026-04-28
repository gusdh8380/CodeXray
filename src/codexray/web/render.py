from __future__ import annotations

import html
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..ai import to_json as review_to_json
from ..dashboard import to_html as dashboard_to_html
from ..dashboard.types import DashboardData
from ..entrypoints import to_json as entrypoints_to_json
from ..entrypoints.types import EntrypointResult
from ..graph import to_json as graph_to_json
from ..graph.types import Graph
from ..hotspots import to_json as hotspots_to_json
from ..hotspots.types import HotspotsReport
from ..inventory import Row
from ..metrics import to_json as metrics_to_json
from ..metrics.types import MetricsResult
from ..quality import to_json as quality_to_json
from ..quality.types import QualityReport
from ..report.types import ReportData
from .jobs import ReviewJob


@dataclass(frozen=True, slots=True)
class PathValidationResult:
    root: Path | None
    error: str | None


def validate_root(raw_path: str) -> PathValidationResult:
    text = raw_path.strip()
    if not text:
        return PathValidationResult(None, "path is required")
    target = Path(text).expanduser()
    try:
        resolved = target.resolve()
    except OSError as exc:
        return PathValidationResult(None, f"path cannot be resolved: {exc}")
    if not resolved.exists():
        return PathValidationResult(None, f"path does not exist: {text}")
    if not resolved.is_dir():
        return PathValidationResult(None, f"path is not a directory: {text}")
    return PathValidationResult(resolved, None)


def render_json_panel(title: str, payload: str | dict[str, Any]) -> str:
    parsed = json.loads(payload) if isinstance(payload, str) else payload
    pretty = json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
    return _panel(title, f'<pre class="json-output">{html.escape(pretty)}</pre>')


def render_inventory(rows: Iterable[Row]) -> str:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "rows": [
            {
                "language": row.language,
                "file_count": row.file_count,
                "loc": row.loc,
                "last_modified_at": row.last_modified_at,
            }
            for row in rows
        ],
    }
    table_rows = [
        (
            row["language"],
            str(row["file_count"]),
            f"{row['loc']:,}",
            row["last_modified_at"],
        )
        for row in payload["rows"]
    ]
    total_files = sum(int(row[1]) for row in table_rows)
    total_loc = sum(row["loc"] for row in payload["rows"])
    body = "".join(
        [
            _summary_grid(
                [
                    ("Languages", str(len(table_rows))),
                    ("Source files", str(total_files)),
                    ("Non-empty LoC", f"{total_loc:,}"),
                ]
            ),
            _insight(
                "Inventory shows the size and language mix. Start with the largest language "
                "rows when estimating migration, testing, or refactor cost."
            ),
            _table(("language", "files", "loc", "last modified"), table_rows),
            _raw_details(payload),
        ]
    )
    return _panel("Inventory", body)


def render_graph(graph: Graph) -> str:
    payload = json.loads(graph_to_json(graph))
    internal = [edge for edge in graph.edges if edge.kind == "internal"]
    external = [edge for edge in graph.edges if edge.kind == "external"]
    outbound: dict[str, int] = {}
    inbound: dict[str, int] = {}
    for edge in internal:
        outbound[edge.from_] = outbound.get(edge.from_, 0) + 1
        inbound[edge.to] = inbound.get(edge.to, 0) + 1
    ranked = sorted(
        graph.nodes,
        key=lambda node: (-(outbound.get(node.path, 0) + inbound.get(node.path, 0)), node.path),
    )[:12]
    rows = [
        (
            node.path,
            node.language,
            str(inbound.get(node.path, 0)),
            str(outbound.get(node.path, 0)),
        )
        for node in ranked
    ]
    body = "".join(
        [
            _summary_grid(
                [
                    ("Files", str(len(graph.nodes))),
                    ("Internal edges", str(len(internal))),
                    ("External refs", str(len(external))),
                ]
            ),
            _insight(
                "Graph highlights file-to-file dependency pressure. Files with both high "
                "inbound and outbound links deserve extra care because changes can ripple."
            ),
            _table(("path", "language", "fan in", "fan out"), rows),
            _raw_details(payload),
        ]
    )
    return _panel("Dependency Graph", body)


def render_metrics(metrics: MetricsResult) -> str:
    payload = json.loads(metrics_to_json(metrics))
    ranked = sorted(
        metrics.nodes,
        key=lambda node: (-(node.fan_in + node.fan_out + node.external_fan_out), node.path),
    )[:15]
    rows = [
        (
            node.path,
            node.language,
            str(node.fan_in),
            str(node.fan_out),
            str(node.external_fan_out),
            str(node.fan_in + node.fan_out + node.external_fan_out),
        )
        for node in ranked
    ]
    body = "".join(
        [
            _summary_grid(
                [
                    ("Nodes", str(metrics.graph.node_count)),
                    ("Largest SCC", str(metrics.graph.largest_scc_size)),
                    ("DAG", "yes" if metrics.graph.is_dag else "no"),
                ]
            ),
            _insight(
                "Coupling is the practical risk signal. High fan-in means many files depend "
                "on this file; high fan-out means this file depends on many others."
            ),
            _table(
                ("path", "language", "fan in", "fan out", "external", "coupling"),
                rows,
            ),
            _raw_details(payload),
        ]
    )
    return _panel("Metrics", body)


def render_entrypoints(result: EntrypointResult) -> str:
    payload = json.loads(entrypoints_to_json(result))
    kind_counts: dict[str, int] = {}
    for entry in result.entrypoints:
        kind_counts[entry.kind] = kind_counts.get(entry.kind, 0) + 1
    rows = [
        (
            entry.path,
            entry.language or "N/A",
            entry.kind,
            entry.detail,
        )
        for entry in result.entrypoints[:30]
    ]
    body = "".join(
        [
            _summary_grid(
                [("Entrypoints", str(len(result.entrypoints)))]
                + [(kind, str(count)) for kind, count in sorted(kind_counts.items())[:3]]
            ),
            _insight(
                "Entrypoints are where runtime behavior begins. They are useful anchors "
                "for onboarding, smoke tests, and impact analysis."
            ),
            _table(("path", "language", "kind", "detail"), rows),
            _raw_details(payload),
        ]
    )
    return _panel("Entrypoints", body)


def render_quality(report: QualityReport) -> str:
    payload = json.loads(quality_to_json(report))
    overall = report.overall
    cards = [
        ("Overall", _grade_text(overall.grade, overall.score)),
    ]
    rows = []
    for name, dim in sorted(report.dimensions.items()):
        cards.append((name.title(), _grade_text(dim.grade, dim.score)))
        rows.append(
            (
                name,
                dim.grade or "N/A",
                "N/A" if dim.score is None else str(dim.score),
                _detail_text(dim.detail),
            )
        )
    body = "".join(
        [
            _summary_grid(cards),
            _insight(_quality_interpretation(overall.grade)),
            _table(("dimension", "grade", "score", "detail"), rows),
            _raw_details(payload),
        ]
    )
    return _panel("Quality", body)


def render_hotspots(report: HotspotsReport) -> str:
    payload = json.loads(hotspots_to_json(report))
    ranked = sorted(
        report.files,
        key=lambda item: (-(item.change_count * item.coupling), item.path),
    )[:15]
    rows = [
        (
            item.path,
            item.category,
            str(item.change_count),
            str(item.coupling),
            str(item.change_count * item.coupling),
        )
        for item in ranked
    ]
    body = "".join(
        [
            _summary_grid(
                [
                    ("Hotspots", str(report.summary.hotspot)),
                    ("Active stable", str(report.summary.active_stable)),
                    ("Neglected complex", str(report.summary.neglected_complex)),
                    ("Stable", str(report.summary.stable)),
                ]
            ),
            _insight(
                "Hotspots combine change frequency and coupling. Prioritize high score "
                "files for tests, ownership cleanup, and small refactors."
            ),
            _table(("path", "category", "changes", "coupling", "priority"), rows),
            _raw_details(payload),
        ]
    )
    return _panel("Hotspots", body)


def render_review(result: Any) -> str:
    payload = json.loads(review_to_json(result))
    cards = [
        ("Backend", payload["backend"]),
        ("Files reviewed", str(payload["files_reviewed"])),
        ("Skipped", str(len(payload["skipped"]))),
    ]
    review_cards = []
    for review in payload["reviews"]:
        dims = review["dimensions"]
        rows = [
            (
                name,
                str(data["score"]),
                ", ".join(str(line) for line in data["evidence_lines"]),
                data["comment"],
                data["suggestion"],
            )
            for name, data in dims.items()
        ]
        review_cards.append(
            '<article class="review-card">'
            f"<h3>{html.escape(review['path'])}</h3>"
            f"<p><strong>Confidence:</strong> {html.escape(review['confidence'])}</p>"
            + _table(("dimension", "score", "lines", "comment", "suggestion"), rows)
            + '<p class="muted"><strong>Limitations:</strong> '
            + html.escape(review["limitations"])
            + "</p>"
            "</article>"
        )
    skipped = [
        (item["path"], item["reason"])
        for item in payload["skipped"]
    ]
    body = "".join(
        [
            _summary_grid(cards),
            _insight(
                "AI review is qualitative. Treat it as a senior-review prompt, then verify "
                "the evidence lines before changing code."
            ),
            "".join(review_cards) or '<p class="muted">No completed AI reviews.</p>',
            _table(("skipped path", "reason"), skipped) if skipped else "",
            _raw_details(payload),
        ]
    )
    return _panel("AI Review", body)


def render_report(data: ReportData, markdown: str) -> str:
    overall = data.quality.overall
    grade = overall.grade or "N/A"
    score = overall.score if overall.score is not None else "N/A"
    top_hotspot = next(
        (file for file in data.hotspots.files if file.category == "hotspot"),
        None,
    )
    cards = [
        ("Grade", f"{grade} ({score})"),
        ("Files", str(sum(row.file_count for row in data.inventory))),
        ("Hotspots", str(data.hotspots.summary.hotspot)),
        ("Top risk", top_hotspot.path if top_hotspot else "N/A"),
    ]
    recommendations = "".join(
        f"<li>{html.escape(rec.text)}</li>" for rec in data.recommendations
    )
    body = "".join(
        [
            _summary_grid(cards),
            _insight(
                "This report combines structure, quality, entrypoints, and hotspots into "
                "a next-action view."
            ),
            "<h3>Recommendations</h3>",
            (
                f'<ol class="recommendations">{recommendations}</ol>'
                if recommendations
                else '<p class="muted">No recommendations.</p>'
            ),
            "<h3>Full Markdown Report</h3>",
            f'<pre class="markdown-output">{html.escape(markdown)}</pre>',
        ]
    )
    return _panel("Report", body)


def render_dashboard(data: DashboardData) -> str:
    dashboard_html = html.escape(dashboard_to_html(data), quote=True)
    body = (
        '<div class="dashboard-workspace">'
        '<iframe class="dashboard-frame" sandbox="allow-scripts allow-same-origin" '
        f'srcdoc="{dashboard_html}" title="CodeXray dashboard"></iframe>'
        "</div>"
    )
    return _panel("Dashboard", body)


def render_overview(
    root: Path,
    inventory: Iterable[Row],
    quality: QualityReport,
    hotspots: HotspotsReport,
    graph: Graph,
) -> str:
    overall = quality.overall
    grade = overall.grade or "N/A"
    score = overall.score if overall.score is not None else "N/A"
    rows = list(inventory)
    total_files = sum(row.file_count for row in rows)
    total_loc = sum(row.loc for row in rows)
    top_hotspot = next(
        (file for file in hotspots.files if file.category == "hotspot"),
        None,
    )
    hotspot_text = (
        f"{top_hotspot.path} ({top_hotspot.change_count}x{top_hotspot.coupling})"
        if top_hotspot is not None
        else "N/A"
    )
    body = "\n".join(
        [
            '<div class="overview-grid">',
            _metric("Path", str(root)),
            _metric("Grade", f"{grade} ({score})"),
            _metric("Source files", str(total_files)),
            _metric("LoC", str(total_loc)),
            _metric("Graph", f"{len(graph.nodes)} nodes / {len(graph.edges)} edges"),
            _metric("Top hotspot", hotspot_text),
            "</div>",
        ]
    )
    return _panel("Overview", body)


def render_error(message: str) -> str:
    return (
        '<section class="result-panel error-panel" data-codexray-result="error">'
        "<h2>Request Error</h2>"
        f"<p>{html.escape(message)}</p>"
        "</section>"
    )


def render_review_prompt(path: str) -> str:
    escaped = html.escape(path)
    body = (
        '<div class="warning-box">'
        "<strong>AI review is opt-in.</strong>"
        "<p>This can take 1-5 minutes and may call your configured Codex or Claude CLI.</p>"
        "</div>"
        '<form class="review-run-form" hx-post="/api/review" '
        'hx-target="#result-panel" hx-swap="innerHTML">'
        f'<input type="hidden" name="path" value="{escaped}">'
        '<input type="hidden" name="run" value="true">'
        '<button class="primary-action" type="submit">Run AI Review</button>'
        "</form>"
    )
    return _panel("AI Review", body)


def render_review_running(job: ReviewJob) -> str:
    short_id = job.id[:8]
    body = (
        '<div class="warning-box running-box">'
        "<strong>AI review is running.</strong>"
        f"<p>Job {html.escape(short_id)} is polling every 2 seconds. Other tabs remain usable.</p>"
        "</div>"
        f'<form class="review-cancel-form" hx-post="/api/review/cancel/{html.escape(job.id)}" '
        'hx-target="#result-panel" hx-swap="innerHTML">'
        '<button class="secondary-action danger-action" type="submit">Cancel Review</button>'
        "</form>"
        f'<div hx-get="/api/review/status/{html.escape(job.id)}" '
        'hx-trigger="load delay:2s" hx-target="#result-panel" hx-swap="innerHTML"></div>'
    )
    return _panel("AI Review", body)


def render_review_failed(job: ReviewJob) -> str:
    message = job.error or "review failed"
    return render_error(message)


def render_review_cancelled(job: ReviewJob) -> str:
    short_id = job.id[:8]
    body = (
        '<div class="warning-box cancelled-box">'
        "<strong>AI review cancelled.</strong>"
        f"<p>Job {html.escape(short_id)} is no longer being polled.</p>"
        "</div>"
    )
    return _panel("AI Review", body)


def _panel(title: str, body: str) -> str:
    return (
        f'<section class="result-panel" data-codexray-result="{html.escape(title.lower())}">'
        f"<h2>{html.escape(title)}</h2>"
        f"{body}"
        "</section>"
    )


def _metric(label: str, value: str) -> str:
    return (
        '<div class="metric">'
        f"<span>{html.escape(label)}</span>"
        f"<strong>{html.escape(value)}</strong>"
        "</div>"
    )


def _summary_grid(items: Iterable[tuple[str, str]]) -> str:
    return '<div class="overview-grid">' + "".join(_metric(k, v) for k, v in items) + "</div>"


def _insight(text: str) -> str:
    return f'<p class="insight">{html.escape(text)}</p>'


def _table(headers: tuple[str, ...], rows: Iterable[tuple[str, ...]]) -> str:
    rows = list(rows)
    if not rows:
        return '<p class="muted">No rows to show.</p>'
    head = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return (
        '<div class="table-wrap"><table class="analysis-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )


def _raw_details(payload: dict[str, Any]) -> str:
    pretty = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    return (
        '<details class="raw-details">'
        "<summary>Raw JSON</summary>"
        f'<pre class="json-output">{html.escape(pretty)}</pre>'
        "</details>"
    )


def _grade_text(grade: str | None, score: int | None) -> str:
    return f"{grade or 'N/A'} ({score if score is not None else 'N/A'})"


def _detail_text(detail: dict[str, Any]) -> str:
    if not detail:
        return "N/A"
    return ", ".join(f"{key}={value}" for key, value in sorted(detail.items()))


def _quality_interpretation(grade: str | None) -> str:
    if grade in {"A", "B"}:
        return (
            "Quality signals are healthy. Use hotspots to decide where targeted "
            "cleanup still matters."
        )
    if grade in {"C", "D"}:
        return (
            "Quality is workable but risky. Focus on the weakest dimensions before "
            "large feature work."
        )
    if grade == "F":
        return (
            "Quality risk is high. Add tests and reduce coupling around top hotspots "
            "before broad changes."
        )
    return "Quality could not be fully measured for this tree."
