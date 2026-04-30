"""Build the React-friendly BriefingPayload JSON from existing analyzers.

This module bridges the deterministic analyzers + AI briefing result + git history
into the 5-section + vibe-insights shape consumed by the React SPA.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..briefing import build_codebase_briefing
from ..briefing.git_history import build_git_history
from ..entrypoints import build_entrypoints
from ..graph import build_graph
from ..hotspots import build_hotspots
from ..inventory import aggregate
from ..metrics import build_metrics
from ..quality import build_quality
from ..vibe import build_vibe_coding_report
from ..vibe_insights import build_vibe_insights
from .ai_briefing import AIBriefingResult

SCHEMA_VERSION = 4

_PER_CATEGORY_LIMIT = 3


# briefing-persona-split: 결정론적 합성 ai_prompt — AI 가 만들지 않은 다음 행동
# 항목들에도 비개발자가 다음 AI 세션에 그대로 복사할 수 있는 6 라벨 prompt 가
# 들어가야 한다. 빈 문자열로 두면 카드에서 prompt 영역이 사라져 사용성이 깨진다.

def _build_hotspot_review_prompt(top_hotspot: str, hotspot_count: int) -> str:
    return (
        "[현재 프로젝트] 위 화면 상단의 정체 섹션에 설명된 프로젝트입니다.\n"
        f"[지금 상황] 자주 바뀌고 위험도가 높은 파일이 {hotspot_count}개 있고, "
        f"그 중 가장 위험한 것은 `{top_hotspot}` 입니다.\n"
        f"[해줄 일] `{top_hotspot}` 파일을 한 번 같이 읽어 주세요. "
        "1) 이 파일이 무엇을 하는 파일인지 한 단락으로 요약, "
        "2) 가장 큰 책임 두 개를 식별, "
        "3) 다음 변경 시 가장 깨질 가능성이 높은 부분 한 곳을 짚어 주세요. "
        "이번 세션에서는 코드 변경은 하지 마세요 — 분석만.\n"
        f"[작업 전 읽을 것] {top_hotspot}\n"
        "[끝나고 확인] 1) 위 세 가지 분석 결과를 채팅으로 받았는지, "
        "2) 어떤 파일도 수정되지 않았는지 확인해 주세요.\n"
        "[건드리지 말 것] 코드 변경 금지 — 다음 세션에서 별도로 합니다."
    )


def _build_low_grade_prompt(grade: str) -> str:
    return (
        "[현재 프로젝트] 위 화면 상단의 정체 섹션에 설명된 프로젝트입니다.\n"
        f"[지금 상황] 종합 품질 등급이 {grade} 로 낮습니다. "
        "어디부터 손대야 가장 효과적인지 우선 식별이 필요합니다.\n"
        "[해줄 일] CodeXray 의 상세 분석 토글을 펼친 다음 "
        "1) Code Quality 탭에서 가장 점수가 낮은 차원 한 개 식별, "
        "2) 그 차원의 정의를 평어로 설명, "
        "3) 그 차원을 올리려면 어떤 종류의 변경이 필요한지 한 단락으로 알려주세요. "
        "이번 세션에서는 코드 변경 없이 진단만.\n"
        "[끝나고 확인] 1) 가장 약한 차원 이름과 점수를 받았는지, "
        "2) 그 차원을 올릴 변경 방향을 받았는지 확인해 주세요.\n"
        "[건드리지 말 것] 코드 변경 금지 — 분석·추천만."
    )


def _build_vibe_axis_weakness_prompt(
    weakness: str, axis_label: str, state: str
) -> str:
    return (
        "[현재 프로젝트] 위 화면 상단의 정체 섹션에 설명된 프로젝트입니다.\n"
        f"[지금 상황] 바이브코딩 진단에서 '{axis_label}' 축이 가장 약합니다 "
        f"(상태 {state}). 그 축에서 빠진 항목 중 하나가 '{weakness}' 입니다.\n"
        f"[해줄 일] '{weakness}' 를 보완해 주세요. "
        "어떻게 보완할지 모르겠으면 먼저 'CodeXray 가 이 항목을 왜 지적했는지, "
        "구체적으로 무엇을 만들거나 고쳐야 하는지 설명해줘' 라고 AI 에게 물어 "
        "이해부터 잡고 시작하세요.\n"
        "[끝나고 확인] 1) 빠진 항목에 해당하는 새 파일/설정이 생겼거나 기존 항목이 "
        "보완됐는지, 2) 기존 코드/문서는 어떤 것도 의도치 않게 변경되지 않았는지 "
        "확인해 주세요.\n"
        "[건드리지 말 것] 이번 항목 외 다른 영역은 다음 세션에서 다루세요."
    )


def build_briefing_payload(root: Path, ai: AIBriefingResult | None) -> dict[str, Any]:
    """Build the JSON payload consumed by the React Briefing screen."""
    resolved = root.resolve()
    inventory = list(aggregate(resolved))
    graph = build_graph(resolved)
    metrics = build_metrics(graph)
    entrypoints = build_entrypoints(resolved)
    quality = build_quality(resolved)
    hotspots = build_hotspots(resolved)
    vibe = build_vibe_coding_report(resolved)
    history = build_git_history(resolved)
    deterministic = build_codebase_briefing(resolved)

    languages_text = ", ".join(row.language for row in inventory) or "감지된 언어 없음"
    total_files = sum(row.file_count for row in inventory)
    total_loc = sum(row.loc for row in inventory)
    grade = quality.overall.grade or "N/A"
    score = quality.overall.score if quality.overall.score is not None else 0
    top_hotspot = next((f for f in hotspots.files if f.category == "hotspot"), None)
    top_hotspot_path = top_hotspot.path if top_hotspot else "N/A"
    repo_name = resolved.name

    what = _build_what(
        repo_name=repo_name,
        languages=languages_text,
        inventory=inventory,
        total_files=total_files,
        total_loc=total_loc,
        grade=grade,
        ai_executive=ai.executive if ai else None,
    )
    how_built = _build_how_built(
        deterministic=deterministic,
        graph=graph,
        metrics=metrics,
        entrypoints=entrypoints,
        ai_architecture=ai.architecture if ai else None,
    )
    current_state = _build_current_state(
        grade=grade,
        score=score,
        hotspot_count=hotspots.summary.hotspot,
        top_hotspot=top_hotspot_path,
        quality=quality,
        hotspots=hotspots,
        ai_quality=ai.quality_risk if ai else None,
    )
    vibe_insights = build_vibe_insights(
        root=resolved,
        vibe=vibe,
        quality=quality,
        hotspots=hotspots,
        history=history,
        ai_key_insight=ai.key_insight if ai else None,
    )
    next_actions = _build_next_actions(
        ai_actions=ai.next_actions if ai else (),
        grade=grade,
        hotspot_count=hotspots.summary.hotspot,
        top_hotspot=top_hotspot_path,
        vibe_insights=vibe_insights,
    )

    intent_alignment = (ai.intent_alignment if ai else "").strip()
    if intent_alignment:
        vibe_insights["intent_alignment"] = {
            "narrative": intent_alignment,
            "intent_present": (resolved / "docs" / "intent.md").exists(),
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "path": str(resolved),
        "what": what,
        "how_built": how_built,
        "current_state": current_state,
        "vibe_insights": vibe_insights,
        "next_actions": next_actions,
        "ai_used": ai is not None and not ai.fallback,
    }


def _build_what(
    *,
    repo_name: str,
    languages: str,
    inventory: list[Any],
    total_files: int,
    total_loc: int,
    grade: str,
    ai_executive: str | None,
) -> dict[str, Any]:
    narrative = ai_executive or (
        f"{repo_name}은 {languages} 기반의 코드베이스로, "
        f"총 {total_files}개 파일·{total_loc:,} LoC 규모입니다. "
        f"현재 종합 품질 등급은 {grade}입니다."
    )
    language_rows = [
        {
            "language": row.language,
            "files": row.file_count,
            "loc": row.loc,
            "share": round(row.loc * 100 / total_loc, 1) if total_loc else 0.0,
        }
        for row in sorted(inventory, key=lambda r: -r.loc)[:5]
    ]
    return {
        "id": "what",
        "title": "개요",
        "narrative": narrative,
        "metrics": [
            {"label": "파일 수", "value": str(total_files)},
            {"label": "LoC", "value": f"{total_loc:,}"},
            {"label": "품질 등급", "value": grade},
        ],
        "details": {"languages": language_rows},
    }


def _build_how_built(
    *,
    deterministic: Any,
    graph: Any,
    metrics: Any,
    entrypoints: Any,
    ai_architecture: str | None,
) -> dict[str, Any]:
    arch_card = deterministic.architecture[0] if deterministic.architecture else None
    fallback = arch_card.text if arch_card else "구조 분석 데이터를 가져오지 못했습니다."

    top_coupled = sorted(
        metrics.nodes,
        key=lambda n: -(n.fan_in + n.fan_out + n.external_fan_out),
    )[:5]
    coupled_rows = [
        {
            "path": n.path,
            "fan_in": n.fan_in,
            "fan_out": n.fan_out,
            "external_fan_out": n.external_fan_out,
            "coupling": n.fan_in + n.fan_out + n.external_fan_out,
        }
        for n in top_coupled
    ]

    entrypoint_rows = [
        {"path": ep.path, "kind": ep.kind}
        for ep in list(entrypoints.entrypoints)[:5]
    ]

    return {
        "id": "how_built",
        "title": "어떻게 만들어졌나",
        "narrative": ai_architecture or fallback,
        "metrics": [
            {"label": "Nodes", "value": str(len(graph.nodes))},
            {"label": "Edges", "value": str(len(graph.edges))},
            {"label": "Largest SCC", "value": str(metrics.graph.largest_scc_size)},
        ],
        "details": {
            "top_coupled": coupled_rows,
            "entrypoints": entrypoint_rows,
            "is_dag": metrics.graph.is_dag,
        },
        "deep_link": {"label": "구조 그래프 보기", "tab": "graph"},
    }


def _build_current_state(
    *,
    grade: str,
    score: int,
    hotspot_count: int,
    top_hotspot: str,
    quality: Any,
    hotspots: Any,
    ai_quality: str | None,
) -> dict[str, Any]:
    if ai_quality:
        narrative = ai_quality
    else:
        narrative = (
            f"품질 등급은 {grade}({score})이고 hotspot은 {hotspot_count}개입니다. "
            f"가장 먼저 살펴볼 파일은 {top_hotspot}입니다."
        )

    dimension_rows = [
        {
            "name": name,
            "grade": dim.grade or "N/A",
            "score": dim.score if dim.score is not None else None,
        }
        for name, dim in sorted(quality.dimensions.items())
    ]

    top_hotspots = sorted(
        hotspots.files, key=lambda f: -(f.change_count * f.coupling)
    )[:5]
    hotspot_rows = [
        {
            "path": f.path,
            "priority": f.change_count * f.coupling,
            "changes": f.change_count,
            "coupling": f.coupling,
            "category": f.category,
        }
        for f in top_hotspots
    ]

    return {
        "id": "current_state",
        "title": "지금 상태",
        "narrative": narrative,
        "metrics": [
            {"label": "등급", "value": grade},
            {"label": "점수", "value": str(score)},
            {"label": "Hotspot", "value": str(hotspot_count)},
        ],
        "details": {
            "dimensions": dimension_rows,
            "hotspots": hotspot_rows,
        },
        "deep_link": {"label": "Quality 탭에서 자세히", "tab": "quality"},
    }


def _build_next_actions(
    *,
    ai_actions: Any,
    grade: str,
    hotspot_count: int,
    top_hotspot: str,
    vibe_insights: dict[str, Any],
) -> list[dict[str, Any]]:
    by_category: dict[str, list[dict[str, Any]]] = {
        "code": [],
        "structural": [],
        "vibe_coding": [],
    }

    structured = list(ai_actions) if ai_actions else []
    for a in structured:
        cat = a.category if a.category in {"code", "structural"} else "code"
        if len(by_category[cat]) >= _PER_CATEGORY_LIMIT:
            continue
        by_category[cat].append(
            {
                "action": a.action,
                "reason": a.reason,
                "evidence": a.evidence,
                "ai_prompt": a.ai_prompt,
                "category": cat,
            }
        )

    if not structured:
        if hotspot_count > 0 and top_hotspot != "N/A":
            by_category["code"].append(
                {
                    "action": f"{top_hotspot} 부터 리뷰",
                    "reason": (
                        "변경 빈도와 결합도가 모두 높아 다음 기능 추가 시 가장 먼저 깨질 위험이 "
                        "있는 파일입니다."
                    ),
                    "evidence": f"Hotspot {hotspot_count}개 중 최상위, 우선순위 1위",
                    "ai_prompt": _build_hotspot_review_prompt(top_hotspot, hotspot_count),
                    "category": "code",
                }
            )
        if grade in {"D", "F"}:
            by_category["structural"].append(
                {
                    "action": "낮은 품질 등급의 원인 차원부터 보강",
                    "reason": (
                        "전체 등급이 낮을 때 우선 어떤 차원이 가장 약한지 식별하면 가장 적은 "
                        "노력으로 평균을 올릴 수 있습니다."
                    ),
                    "evidence": f"종합 등급 {grade}",
                    "ai_prompt": _build_low_grade_prompt(grade),
                    "category": "structural",
                }
            )

    by_category["vibe_coding"].extend(_synthesize_vibe_coding_actions(vibe_insights))

    return (
        by_category["code"][:_PER_CATEGORY_LIMIT]
        + by_category["structural"][:_PER_CATEGORY_LIMIT]
        + by_category["vibe_coding"][:_PER_CATEGORY_LIMIT]
    )


_AXIS_LABEL = {
    "intent": "의도",
    "verification": "검증",
    "continuity": "이어받기",
}

_STATE_RANK = {"unknown": 0, "weak": 1, "moderate": 2, "strong": 3}


def _synthesize_vibe_coding_actions(
    vibe_insights: dict[str, Any],
) -> list[dict[str, Any]]:
    if not vibe_insights.get("detected"):
        guide = vibe_insights.get("starter_guide", []) or []
        return [
            {
                "action": item.get("action", ""),
                "reason": item.get("reason", ""),
                "evidence": "바이브코딩 신호 미감지 — 첫 걸음 추천",
                "ai_prompt": item.get("ai_prompt", ""),
                "category": "vibe_coding",
            }
            for item in guide[:_PER_CATEGORY_LIMIT]
            if item.get("action")
        ]

    axes = vibe_insights.get("axes") or []
    if not axes:
        return []
    weakest = min(axes, key=lambda ax: _STATE_RANK.get(ax.get("state", "unknown"), 0))
    weaknesses = list(weakest.get("weaknesses") or [])
    if not weaknesses:
        return []
    axis_name = str(weakest.get("name") or "")
    axis_label = _AXIS_LABEL.get(axis_name, axis_name or "바이브코딩 축")
    state = weakest.get("state", "unknown")
    return [
        {
            "action": f"{weakness} 보완",
            "reason": (
                f"{axis_label} 축이 가장 약합니다 (상태 {state}). "
                "이 항목을 채우면 바이브코딩 진단의 가장 큰 갭이 좁혀집니다."
            ),
            "evidence": f"바이브코딩 3축 — {axis_label} 빠진 항목",
            "ai_prompt": _build_vibe_axis_weakness_prompt(
                weakness=weakness, axis_label=axis_label, state=state
            ),
            "category": "vibe_coding",
        }
        for weakness in weaknesses[:_PER_CATEGORY_LIMIT]
    ]
