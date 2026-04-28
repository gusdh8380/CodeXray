from __future__ import annotations

import html
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..ai import to_json as review_to_json
from ..briefing import to_json as briefing_to_json
from ..briefing.types import BriefingCard, CodebaseBriefing
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
from ..vibe import to_json as vibe_to_json
from ..vibe.types import VibeCodingReport, VibeFinding
from .folder_picker import FolderPickerResult
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
    return _panel("Inventory", _analysis_layout(body, _explanation("inventory")))


def render_codebase_briefing(briefing: CodebaseBriefing) -> str:
    payload = json.loads(briefing_to_json(briefing))
    history = briefing.git_history
    history_rows = [
        (
            commit.hash,
            commit.commit_type,
            commit.subject,
            ", ".join(commit.process_categories) or "일반 commit",
        )
        for commit in history.process_commits[:8]
    ]
    if not history_rows and history.recent_commits:
        history_rows = [
            (commit.hash, commit.commit_type, commit.subject, "최근 commit")
            for commit in history.recent_commits[:5]
        ]
    body = "".join(
        [
            '<article class="briefing-deck" data-codexray-briefing="deck">',
            f'<header class="briefing-hero"><h2>{html.escape(briefing.title)}</h2>'
            "<p>소스파일/레포를 팀에 설명할 수 있는 발표자료형 분석입니다.</p></header>",
            _briefing_section("Briefing", briefing.executive),
            _briefing_section("Architecture", briefing.architecture),
            _briefing_section("Quality & Risk", briefing.quality_risk),
            _briefing_section("How It Was Built", briefing.build_process),
            (
                "<h3>Git 제작 과정 근거</h3>"
                + _table(("hash", "type", "message", "process evidence"), history_rows)
            ),
            _briefing_section("Explain", briefing.explain),
            _briefing_section("Deep Dive", briefing.deep_dive),
            _raw_details(payload),
            "</article>",
        ]
    )
    return _panel("Briefing", body)


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
    return _panel("Dependency Graph", _analysis_layout(body, _explanation("graph")))


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
    return _panel("Metrics", _analysis_layout(body, _explanation("metrics")))


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
    return _panel("Entrypoints", _analysis_layout(body, _explanation("entrypoints")))


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
    return _panel("Quality", _analysis_layout(body, _explanation("quality")))


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
    return _panel("Hotspots", _analysis_layout(body, _explanation("hotspots")))


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
    return _panel("Report", _analysis_layout(body, _explanation("report")))


def render_dashboard(data: DashboardData) -> str:
    dashboard_html = html.escape(dashboard_to_html(data), quote=True)
    body = (
        '<div class="dashboard-workspace">'
        '<iframe class="dashboard-frame" sandbox="allow-scripts allow-same-origin" '
        f'srcdoc="{dashboard_html}" title="CodeXray dashboard"></iframe>'
        "</div>"
    )
    return _panel("Dashboard", body)


def render_vibe_coding_report(report: VibeCodingReport) -> str:
    payload = json.loads(vibe_to_json(report))
    area_rows = [
        (
            _area_label(area),
            str(sum(1 for item in report.evidence if item.area == area)),
        )
        for area in report.process_areas
    ]
    evidence_rows = [
        (_area_label(item.area), item.path, item.kind, item.detail)
        for item in report.evidence
    ]
    body = "".join(
        [
            '<div class="vibe-report" data-codexray-vibe="report">',
            _summary_grid(
                [
                    ("신뢰도", f"{report.confidence} ({report.confidence_score})"),
                    ("근거 영역", str(len(report.process_areas))),
                    ("근거 파일", str(len(report.evidence))),
                ]
            ),
            _insight(
                "이 탭은 코드가 아니라 에이전트와 사람이 어떤 방식으로 협업했는지 "
                "레포 안의 흔적으로 해석합니다. 관찰된 사실과 추론을 분리해서 보세요."
            ),
            '<div class="vibe-card-grid">',
            _finding_card("잘한 점", report.strengths, "vibe-strength"),
            _finding_card("주의할 점", report.risks, "vibe-risk"),
            _finding_card("다음 행동", report.actions, "vibe-action"),
            "</div>",
            "<h3>프로세스 영역</h3>",
            _table(("area", "evidence count"), area_rows),
            "<h3>관찰된 근거</h3>",
            _table(("area", "path", "kind", "detail"), evidence_rows),
            _raw_details(payload),
            "</div>",
        ]
    )
    return _panel("Vibe Coding", body)


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


def _briefing_section(title: str, cards: tuple[BriefingCard, ...]) -> str:
    return (
        f'<section class="briefing-section" data-briefing-section="{html.escape(title)}">'
        f"<h3>{html.escape(title)}</h3>"
        '<div class="briefing-card-grid">'
        + "".join(_briefing_card(card) for card in cards)
        + "</div></section>"
    )


def _briefing_card(card: BriefingCard) -> str:
    evidence = "".join(
        '<span class="briefing-evidence">'
        f"<strong>{html.escape(item.label)}</strong>: {html.escape(item.value)}"
        "</span>"
        for item in card.evidence
    )
    return (
        '<article class="briefing-card">'
        f"<h4>{html.escape(card.title)}</h4>"
        f"<p>{html.escape(card.text)}</p>"
        f'<div class="briefing-evidence-list">{evidence}</div>'
        "</article>"
    )


def _finding_card(
    title: str,
    items: tuple[VibeFinding, ...],
    css_class: str,
) -> str:
    if not items:
        body = '<p class="muted">표시할 항목 없음</p>'
    else:
        rendered = []
        for item in items:
            evidence = ", ".join(item.evidence_paths)
            rendered.append(
                '<li class="vibe-finding">'
                f"<strong>{html.escape(item.text)}</strong>"
                f'<span class="summary-evidence">{html.escape(evidence)}</span>'
                "</li>"
            )
        body = f'<ul class="summary-items">{"".join(rendered)}</ul>'
    return (
        f'<section class="summary-card {css_class}">'
        f"<h3>{html.escape(title)}</h3>{body}</section>"
    )


def _area_label(area: str) -> str:
    labels = {
        "agent_instructions": "에이전트 지침",
        "spec_workflow": "명세 워크플로",
        "memory_handoff": "메모리/인수인계",
        "validation": "검증",
        "retrospectives": "회고",
        "automation": "자동화",
    }
    return labels.get(area, area)


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


def render_folder_picker_result(result: FolderPickerResult) -> str:
    if result.path is not None:
        escaped = html.escape(result.path)
        return (
            f'<input id="path-input" name="path" type="text" value="{escaped}" '
            'autocomplete="off" hx-swap-oob="true">'
            '<span id="status-text" class="status-text" role="status">'
            "Folder selected"
            "</span>"
        )
    message = "Folder selection cancelled" if result.cancelled else result.error
    return (
        '<span id="status-text" class="status-text" role="status">'
        f"{html.escape(message or 'Folder picker failed')}"
        "</span>"
    )


def _panel(title: str, body: str) -> str:
    return (
        f'<section class="result-panel" data-codexray-result="{html.escape(title.lower())}">'
        f"<h2>{html.escape(title)}</h2>"
        f"{body}"
        "</section>"
    )


def _analysis_layout(main: str, aside: str) -> str:
    return (
        '<div class="analysis-layout">'
        f'<div class="analysis-main">{main}</div>'
        f'<aside class="analysis-explainer">{aside}</aside>'
        "</div>"
    )


def _metric(label: str, value: str) -> str:
    return (
        '<div class="metric">'
        f"<span>{html.escape(label)}</span>"
        f"<strong>{html.escape(value)}</strong>"
        "</div>"
    )


def _explanation(name: str) -> str:
    explanations: dict[str, tuple[str, tuple[str, ...]]] = {
        "inventory": (
            "이 화면은 코드베이스의 규모와 언어 구성을 보는 출발점입니다.",
            (
                "시니어 관점에서는 LoC가 큰 언어와 파일 수가 많은 영역을 먼저 봅니다. "
                "그곳이 테스트 비용, 리팩터링 비용, 온보딩 비용을 대부분 결정합니다.",
                "언어가 여러 개라면 경계면을 확인해야 합니다. Python, C#, TypeScript처럼 "
                "런타임이 다른 코드가 섞이면 빌드·배포·테스트 책임도 나뉠 가능성이 큽니다.",
                "다음 행동은 가장 큰 언어의 entrypoint와 hotspot을 이어서 확인하는 것입니다.",
            ),
        ),
        "graph": (
            "이 화면은 파일 사이의 의존 방향을 보여줍니다.",
            (
                "fan-in이 높은 파일은 많은 코드가 의존하는 중심축입니다. 변경 전 회귀 테스트와 "
                "호출자 영향 범위를 먼저 확인해야 합니다.",
                "fan-out이 높은 파일은 많은 것을 알고 있는 조정자일 가능성이 큽니다. 비즈니스 "
                "규칙이 한 파일에 몰렸는지, adapter나 service 분리가 필요한지 봅니다.",
                "좋은 그래프는 모든 의존이 없는 그래프가 아니라, 중요한 의존이 "
                "설명 가능한 그래프입니다.",
            ),
        ),
        "metrics": (
            "이 화면은 구조 리스크를 숫자로 압축한 것입니다.",
            (
                "coupling이 높은 파일은 작업 전후 검증 범위가 넓습니다. 작은 수정도 주변 기능에 "
                "영향을 줄 수 있으므로 테스트 보강 우선순위가 높습니다.",
                "largest SCC가 크면 순환 의존이 있다는 뜻입니다. 순환은 변경 순서와 "
                "모듈 분리를 어렵게 만듭니다.",
                "시니어는 점수를 절대값으로만 보지 않고, hotspot과 겹치는 파일을 "
                "우선순위로 잡습니다.",
            ),
        ),
        "hotspots": (
            "이 화면은 자주 바뀌면서 구조적으로도 복잡한 파일을 찾습니다.",
            (
                "hotspot은 '나쁜 파일'이라기보다 투자 우선순위입니다. 자주 바뀌는 곳에 테스트와 "
                "명확한 소유권이 없으면 개발 속도가 계속 느려집니다.",
                "priority가 높은 파일은 바로 대규모 리팩터링하기보다, 먼저 characterization test와 "
                "작은 추출을 반복하는 편이 안전합니다.",
                "active stable은 많이 바뀌지만 결합은 낮은 영역이고, neglected "
                "complex는 안 바뀌지만 "
                "구조적으로 위험한 영역입니다. 둘은 대응 전략이 다릅니다.",
            ),
        ),
        "quality": (
            "이 화면은 코드베이스 품질을 결합도, 응집도, 문서화, 테스트 관점으로 나눠 봅니다.",
            (
                "전체 등급보다 중요한 것은 어떤 dimension이 발목을 잡는지입니다. "
                "테스트 점수가 낮으면 "
                "리팩터링보다 검증 기반을 먼저 깔아야 합니다.",
                "coupling과 cohesion이 동시에 낮으면 설계 경계가 흐릴 가능성이 "
                "큽니다. 이 경우 기능 추가 전에 "
                "모듈 책임을 다시 정리하는 것이 장기적으로 싸게 먹힙니다.",
                "품질 점수는 의사결정 신호입니다. PR 차단 기준이 아니라 다음 개선 "
                "순서를 정하는 데 사용합니다.",
            ),
        ),
        "entrypoints": (
            "이 화면은 프로그램이 어디서 시작되는지 보여줍니다.",
            (
                "entrypoint는 코드 읽기의 시작점입니다. 신규 개발자는 여기서 런타임 "
                "흐름을 따라가면 "
                "전체 구조를 더 빨리 이해합니다.",
                "entrypoint가 너무 많으면 실행 경로가 분산되어 테스트 전략이 "
                "어려워질 수 있습니다. 반대로 "
                "감지되지 않으면 빌드 설정이나 framework convention을 별도로 확인해야 합니다.",
                "시니어는 entrypoint와 hotspot이 가까운지 봅니다. 시작점 근처 "
                "hotspot은 사용자 영향도가 높을 수 있습니다.",
            ),
        ),
        "report": (
            "이 화면은 앞선 분석을 다음 행동 중심으로 묶은 요약 리포트입니다.",
            (
                "Report는 세부 수치보다 의사결정 순서를 잡는 용도입니다. grade, "
                "top risk, recommendation을 "
                "먼저 보고 필요한 탭으로 내려가 근거를 확인합니다.",
                "추천은 자동 생성된 규칙 기반 제안입니다. 그대로 실행하기보다 현재 "
                "제품 일정, 장애 이력, "
                "팀 소유권과 맞춰 우선순위를 조정해야 합니다.",
                "시니어 리뷰에서는 이 리포트를 작업 계획의 초안으로 쓰고, hotspot "
                "파일을 실제 코드 리뷰로 검증합니다.",
            ),
        ),
    }
    title, paragraphs = explanations[name]
    return (
        "<h3>시니어 개발자 관점</h3>"
        f"<p><strong>{html.escape(title)}</strong></p>"
        + "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs)
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
