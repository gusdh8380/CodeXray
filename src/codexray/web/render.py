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
    return render_json_panel("Inventory", payload)


def render_graph(graph: Graph) -> str:
    return render_json_panel("Dependency Graph", graph_to_json(graph))


def render_metrics(metrics: MetricsResult) -> str:
    return render_json_panel("Metrics", metrics_to_json(metrics))


def render_entrypoints(result: EntrypointResult) -> str:
    return render_json_panel("Entrypoints", entrypoints_to_json(result))


def render_quality(report: QualityReport) -> str:
    return render_json_panel("Quality", quality_to_json(report))


def render_hotspots(report: HotspotsReport) -> str:
    return render_json_panel("Hotspots", hotspots_to_json(report))


def render_review(result: Any) -> str:
    return render_json_panel("AI Review", review_to_json(result))


def render_report(data: ReportData, markdown: str) -> str:
    overall = data.quality.overall
    grade = overall.grade or "N/A"
    score = overall.score if overall.score is not None else "N/A"
    summary = (
        '<div class="summary-row">'
        f"<span>Grade</span><strong>{html.escape(str(grade))} ({html.escape(str(score))})</strong>"
        "</div>"
    )
    body = f'{summary}<pre class="markdown-output">{html.escape(markdown)}</pre>'
    return _panel("Report", body)


def render_dashboard(data: DashboardData) -> str:
    dashboard_html = html.escape(dashboard_to_html(data), quote=True)
    body = (
        '<iframe class="dashboard-frame" sandbox="allow-scripts allow-same-origin" '
        f'srcdoc="{dashboard_html}" title="CodeXray dashboard"></iframe>'
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
        '<form hx-post="/api/review" hx-target="#result-panel" hx-swap="innerHTML">'
        f'<input type="hidden" name="path" value="{escaped}">'
        '<input type="hidden" name="run" value="true">'
        '<button class="primary-action" type="submit">Run AI Review</button>'
        "</form>"
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
