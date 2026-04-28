from __future__ import annotations

from pathlib import Path

from ..entrypoints import build_entrypoints
from ..graph import build_graph
from ..hotspots import build_hotspots
from ..inventory import aggregate
from ..metrics import build_metrics
from ..quality import build_quality
from ..vibe import build_vibe_coding_report
from .git_history import build_git_history
from .types import BriefingCard, BriefingEvidence, BriefingSlide, CodebaseBriefing

SCHEMA_VERSION = 1


def build_codebase_briefing(root: Path) -> CodebaseBriefing:
    resolved = root.resolve()
    inventory = tuple(aggregate(resolved))
    graph = build_graph(resolved)
    metrics = build_metrics(graph)
    entrypoints = build_entrypoints(resolved)
    quality = build_quality(resolved)
    hotspots = build_hotspots(resolved)
    vibe = build_vibe_coding_report(resolved)
    history = build_git_history(resolved)

    total_files = sum(row.file_count for row in inventory)
    total_loc = sum(row.loc for row in inventory)
    languages = ", ".join(row.language for row in inventory) or "source files 없음"
    grade = quality.overall.grade or "N/A"
    score = "N/A" if quality.overall.score is None else str(quality.overall.score)
    top_hotspot = next((item for item in hotspots.files if item.category == "hotspot"), None)
    top_hotspot_text = top_hotspot.path if top_hotspot is not None else "N/A"
    entrypoint_text = str(len(entrypoints.entrypoints))
    executive = (
        BriefingCard(
            title="한 문장 요약",
            text=(
                f"{resolved.name}은 {languages} 중심의 로컬 코드베이스이며, "
                f"현재 품질 등급은 {grade}({score})입니다."
            ),
            evidence=(
                BriefingEvidence("files", str(total_files)),
                BriefingEvidence("loc", str(total_loc)),
                BriefingEvidence("grade", f"{grade} ({score})"),
            ),
        ),
        BriefingCard(
            title="팀에 바로 공유할 상태",
            text=_team_status(grade, hotspots.summary.hotspot, vibe.confidence),
            evidence=(
                BriefingEvidence("hotspots", str(hotspots.summary.hotspot)),
                BriefingEvidence("vibe evidence", vibe.confidence),
            ),
        ),
    )
    architecture = (
        BriefingCard(
            title="구조",
            text=(
                f"{len(graph.nodes)}개 파일 노드와 {len(graph.edges)}개 의존성 edge가 "
                "관찰됩니다."
            ),
            evidence=(
                BriefingEvidence("nodes", str(len(graph.nodes))),
                BriefingEvidence("edges", str(len(graph.edges))),
                BriefingEvidence("largest SCC", str(metrics.graph.largest_scc_size)),
            ),
        ),
        BriefingCard(
            title="실행 시작점",
            text=f"자동 식별된 entrypoint는 {entrypoint_text}개입니다.",
            evidence=(BriefingEvidence("entrypoints", entrypoint_text),),
        ),
    )
    quality_risk = (
        BriefingCard(
            title="품질 등급",
            text=f"종합 품질 등급은 {grade}({score})입니다.",
            evidence=tuple(
                BriefingEvidence(name, f"{dim.grade or 'N/A'} ({dim.score or 'N/A'})")
                for name, dim in sorted(quality.dimensions.items())
            ),
        ),
        BriefingCard(
            title="우선 리스크",
            text=f"가장 먼저 볼 파일은 {top_hotspot_text}입니다.",
            evidence=(
                BriefingEvidence("top hotspot", top_hotspot_text),
                BriefingEvidence("hotspot count", str(hotspots.summary.hotspot)),
            ),
        ),
    )
    build_process = (
        BriefingCard(
            title="바이브코딩 환경",
            text=(
                f"레포 안의 프로세스 증거는 {vibe.confidence} 신뢰도로 관찰됩니다. "
                f"{len(vibe.process_areas)}개 영역에서 "
                f"{len(vibe.evidence)}개 근거를 찾았습니다."
            ),
            evidence=tuple(
                BriefingEvidence(item.area, item.path) for item in vibe.evidence[:6]
            ),
        ),
        BriefingCard(
            title="Git 제작 과정",
            text=_history_text(history_available=history.available, count=history.commit_count),
            evidence=_history_evidence(history),
        ),
    )
    explain = (
        BriefingCard(
            title="비개발자 설명",
            text=(
                "이 화면은 레포를 하나의 프로젝트 자료처럼 요약합니다. "
                "파일 규모, 품질 신호, 위험 위치, 제작 과정 흔적을 함께 봅니다."
            ),
            evidence=(
                BriefingEvidence("languages", languages),
                BriefingEvidence("status", f"{grade} ({score})"),
            ),
        ),
        BriefingCard(
            title="회의에서 말할 다음 문장",
            text=_plain_next_action(
                grade=grade,
                hotspot_count=hotspots.summary.hotspot,
                top_hotspot=top_hotspot_text,
            ),
            evidence=(
                BriefingEvidence("grade", f"{grade} ({score})"),
                BriefingEvidence("top hotspot", top_hotspot_text),
                BriefingEvidence("hotspots", str(hotspots.summary.hotspot)),
            ),
        ),
    )
    deep_dive = (
        BriefingCard(
            title="상세 분석",
            text=(
                "Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report, "
                "Dashboard, Review, Vibe Coding 상세 화면에서 근거를 더 깊게 확인합니다."
            ),
            evidence=(
                BriefingEvidence("views", "inventory/graph/metrics/hotspots/quality"),
                BriefingEvidence("views", "entrypoints/report/dashboard/review/vibe-coding"),
            ),
        ),
    )
    presenter_summary = _presenter_summary(
        name=resolved.name,
        languages=languages,
        grade=grade,
        score=score,
        top_hotspot=top_hotspot_text,
        history_available=history.available,
    )
    presentation_slides = _presentation_slides(
        executive=executive,
        architecture=architecture,
        quality_risk=quality_risk,
        build_process=build_process,
        explain=explain,
        deep_dive=deep_dive,
    )

    return CodebaseBriefing(
        schema_version=SCHEMA_VERSION,
        path=str(resolved),
        title=f"{resolved.name} 코드베이스 브리핑",
        executive=executive,
        architecture=architecture,
        quality_risk=quality_risk,
        build_process=build_process,
        explain=explain,
        deep_dive=deep_dive,
        presenter_summary=presenter_summary,
        presentation_slides=presentation_slides,
        git_history=history,
    )


def _team_status(grade: str, hotspots: int, vibe_confidence: str) -> str:
    if grade in {"A", "B"} and hotspots == 0:
        return "구조와 품질 신호가 안정적이므로 기능 이해와 유지 관리 계획을 세우기 좋습니다."
    if grade in {"D", "F"} or hotspots > 0:
        return (
            "바로 확장하기보다 위험 파일과 테스트 보강 지점을 먼저 공유하는 편이 좋습니다. "
            f"제작 과정 증거는 {vibe_confidence} 수준입니다."
        )
    return f"기본 구조는 파악 가능하며, 제작 과정 증거는 {vibe_confidence} 수준입니다."


def _history_text(*, history_available: bool, count: int) -> str:
    if not history_available:
        return "git history를 읽을 수 없어 제작 순서는 레포 안 파일 증거만으로 판단합니다."
    return f"최근 git history 기준 총 {count}개 commit 흐름에서 제작 과정을 요약합니다."


def _history_evidence(history) -> tuple[BriefingEvidence, ...]:
    if not history.available:
        return (BriefingEvidence("history", history.unavailable_reason or "unavailable"),)
    evidence = [BriefingEvidence("commits", str(history.commit_count))]
    evidence.extend(history.type_distribution[:4])
    evidence.extend(
        BriefingEvidence(commit.hash, commit.subject) for commit in history.process_commits[:4]
    )
    return tuple(evidence)


def _plain_next_action(*, grade: str, hotspot_count: int, top_hotspot: str) -> str:
    if grade in {"D", "F"}:
        return "다음 행동은 낮은 품질 등급의 원인을 확인하고 테스트 보강 지점을 잡는 것입니다."
    if hotspot_count > 0:
        return "다음 행동은 자주 바뀌고 결합도도 높은 파일을 먼저 검토하는 것입니다."
    if top_hotspot != "N/A":
        return f"먼저 {top_hotspot} 파일이 왜 중요한지 확인하고 테스트 계획을 잡으세요."
    return "먼저 구조와 실행 시작점을 확인한 뒤 작은 검증 작업부터 정하세요."


def _presenter_summary(
    *,
    name: str,
    languages: str,
    grade: str,
    score: str,
    top_hotspot: str,
    history_available: bool,
) -> str:
    history_text = (
        "git history까지 확인했습니다"
        if history_available
        else "git history는 제한적으로 확인했습니다"
    )
    return (
        f"{name}은 {languages} 기반의 코드베이스입니다. 현재 품질 신호는 {grade}({score})이고, "
        f"우선 확인할 위치는 {top_hotspot}입니다. {history_text}. "
        "이 브리핑은 팀이 구조, 위험, 제작 과정, 다음 행동을 한 번에 공유하도록 구성됐습니다."
    )


def _presentation_slides(
    *,
    executive: tuple[BriefingCard, ...],
    architecture: tuple[BriefingCard, ...],
    quality_risk: tuple[BriefingCard, ...],
    build_process: tuple[BriefingCard, ...],
    explain: tuple[BriefingCard, ...],
    deep_dive: tuple[BriefingCard, ...],
) -> tuple[BriefingSlide, ...]:
    return (
        _slide(
            "opening",
            "오늘 이 레포를 어떻게 볼 것인가",
            "Opening",
            executive,
            ("Overview", "Report"),
        ),
        _slide(
            "shape",
            "시스템의 생김새",
            "Architecture",
            architecture,
            ("Inventory", "Graph", "Entrypoints"),
        ),
        _slide(
            "health",
            "현재 품질과 위험",
            "Quality & Risk",
            quality_risk,
            ("Quality", "Hotspots", "Metrics"),
        ),
        _slide(
            "process",
            "어떻게 만들어졌는가",
            "How It Was Built",
            build_process,
            ("Vibe Coding", "Git History"),
        ),
        _slide("plain", "비개발자에게 설명하기", "Explain", explain, ("Briefing", "Report")),
        _slide(
            "next",
            "다음 행동과 상세 확인",
            "Deep Dive",
            deep_dive,
            ("Deep Dive", "Review", "Dashboard"),
        ),
    )


def _slide(
    slide_id: str,
    title: str,
    eyebrow: str,
    cards: tuple[BriefingCard, ...],
    deep_links: tuple[str, ...],
) -> BriefingSlide:
    first = cards[0]
    evidence = tuple(item for card in cards for item in card.evidence)[:8]
    if not evidence:
        evidence = (BriefingEvidence("evidence", first.title),)
    narrative = " ".join(card.text for card in cards)
    return BriefingSlide(
        id=slide_id,
        title=title,
        eyebrow=eyebrow,
        narrative=narrative,
        evidence=evidence,
        deep_links=deep_links,
    )
