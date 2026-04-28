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
        name=resolved.name,
        languages=languages,
        total_files=total_files,
        total_loc=total_loc,
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        largest_scc=metrics.graph.largest_scc_size,
        entrypoint_count=len(entrypoints.entrypoints),
        grade=grade,
        score=score,
        hotspot_count=hotspots.summary.hotspot,
        top_hotspot=top_hotspot_text,
        vibe_confidence=vibe.confidence,
        vibe_evidence_count=len(vibe.evidence),
        vibe_area_count=len(vibe.process_areas),
        history_available=history.available,
        commit_count=history.commit_count,
        process_commit_count=len(history.process_commits),
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
    name: str,
    languages: str,
    total_files: int,
    total_loc: int,
    node_count: int,
    edge_count: int,
    largest_scc: int,
    entrypoint_count: int,
    grade: str,
    score: str,
    hotspot_count: int,
    top_hotspot: str,
    vibe_confidence: str,
    vibe_evidence_count: int,
    vibe_area_count: int,
    history_available: bool,
    commit_count: int,
    process_commit_count: int,
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
            summary=(
                f"{name}은 {languages} 기반의 {total_files}개 파일, "
                f"{total_loc} LoC 규모입니다."
            ),
            meaning=(
                f"현재 등급 {grade}({score})는 팀 공유 전에 상태와 리스크를 함께 설명해야 "
                "한다는 신호입니다."
            ),
            risk=_grade_risk(grade, top_hotspot),
            action="먼저 이 브리핑으로 전체 상태를 맞춘 뒤 Report와 Quality에서 근거를 확인하세요.",
        ),
        _slide(
            "shape",
            "시스템의 생김새",
            "Architecture",
            architecture,
            ("Inventory", "Graph", "Entrypoints"),
            summary=(
                f"의존성 그래프는 {node_count}개 노드와 {edge_count}개 연결, "
                f"{entrypoint_count}개 실행 시작점을 보여줍니다."
            ),
            meaning=_architecture_meaning(node_count, edge_count, largest_scc),
            risk=_architecture_risk(largest_scc, entrypoint_count),
            action=(
                "Graph에서 중심 노드와 SCC를 확인하고, "
                "Entrypoints에서 실제 시작 경로를 맞추세요."
            ),
        ),
        _slide(
            "health",
            "현재 품질과 위험",
            "Quality & Risk",
            quality_risk,
            ("Quality", "Hotspots", "Metrics"),
            summary=f"품질 등급은 {grade}({score})이고 hotspot은 {hotspot_count}개입니다.",
            meaning=_quality_meaning(grade, hotspot_count),
            risk=f"가장 먼저 볼 위험 위치는 {top_hotspot}입니다.",
            action="Quality의 낮은 dimension과 Hotspots의 상위 파일을 같은 회의 안건으로 묶으세요.",
        ),
        _slide(
            "process",
            "어떻게 만들어졌는가",
            "How It Was Built",
            build_process,
            ("Vibe Coding", "Git History"),
            summary=_process_summary(
                history_available=history_available,
                commit_count=commit_count,
                vibe_confidence=vibe_confidence,
            ),
            meaning=_process_meaning(
                vibe_area_count=vibe_area_count,
                vibe_evidence_count=vibe_evidence_count,
                process_commit_count=process_commit_count,
            ),
            risk=_process_risk(
                history_available=history_available,
                vibe_confidence=vibe_confidence,
                process_commit_count=process_commit_count,
            ),
            action="How It Was Built 근거를 보고 명세, 검증, 회고가 실제로 누적됐는지 확인하세요.",
        ),
        _slide(
            "plain",
            "비개발자에게 설명하기",
            "Explain",
            explain,
            ("Briefing", "Report"),
            summary=(
                "이 레포는 파일 묶음이 아니라 구조, 품질, 제작 과정이 함께 있는 "
                "프로젝트 자산입니다."
            ),
            meaning=(
                "좋은 설명은 기술 용어를 줄이고 '무엇을 하는지, 믿어도 되는지, "
                "어디를 먼저 봐야 하는지'로 바꾸는 것입니다."
            ),
            risk=(
                "등급이나 그래프만 보여주면 비개발자는 현재 의사결정에 필요한 "
                "위험을 놓치기 쉽습니다."
            ),
            action=(
                "회의에서는 Opening, Health, Process slide만 먼저 읽고 "
                "세부 질문 때 Deep Dive로 가세요."
            ),
        ),
        _slide(
            "next",
            "다음 행동과 상세 확인",
            "Deep Dive",
            deep_dive,
            ("Deep Dive", "Review", "Dashboard"),
            summary="브리핑은 방향을 정하고, 상세 탭은 그 판단을 검증하는 역할입니다.",
            meaning=(
                "다음 행동은 top hotspot, 낮은 품질 dimension, 제작 과정 공백을 "
                "순서대로 확인하는 것입니다."
            ),
            risk="상세 근거 없이 바로 수정하면 실제 병목이 아닌 파일을 먼저 고칠 수 있습니다.",
            action="Dashboard로 구조를 보고, Review는 명시적으로 실행해 정성 의견을 추가하세요.",
        ),
    )


def _slide(
    slide_id: str,
    title: str,
    eyebrow: str,
    cards: tuple[BriefingCard, ...],
    deep_links: tuple[str, ...],
    summary: str,
    meaning: str,
    risk: str,
    action: str,
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
        summary=summary,
        meaning=meaning,
        risk=risk,
        action=action,
        evidence=evidence,
        deep_links=deep_links,
    )


def _grade_risk(grade: str, top_hotspot: str) -> str:
    if grade in {"D", "F"}:
        return f"낮은 등급이므로 {top_hotspot} 같은 핵심 위험 파일을 설명 없이 넘기면 안 됩니다."
    if grade == "C":
        return "중간 등급이므로 확장 전 품질 편차와 테스트 공백을 확인해야 합니다."
    return (
        "현재 등급만으로는 큰 위험 신호가 적지만, "
        "변경 빈도가 높은 파일은 별도로 확인해야 합니다."
    )


def _architecture_meaning(node_count: int, edge_count: int, largest_scc: int) -> str:
    if node_count == 0:
        return "분석 가능한 소스 노드가 거의 없어 구조 설명은 제한적입니다."
    density = edge_count / node_count
    if largest_scc >= 10:
        return (
            "서로 얽힌 파일 묶음이 커서 한 부분을 바꾸면 "
            "여러 파일을 함께 이해해야 하는 구조입니다."
        )
    if density >= 4:
        return "파일 수 대비 연결이 많아 중심 파일과 의존 방향을 먼저 잡아야 합니다."
    return "구조는 비교적 분리되어 보이며, 시작점과 핵심 모듈을 따라가며 설명하기 좋습니다."


def _architecture_risk(largest_scc: int, entrypoint_count: int) -> str:
    if largest_scc >= 10:
        return f"largest SCC가 {largest_scc}라 순환 의존 또는 강한 결합을 우선 의심해야 합니다."
    if entrypoint_count == 0:
        return "명확한 실행 시작점이 없으면 팀원이 프로젝트를 실행하거나 검증하기 어렵습니다."
    return (
        "큰 구조 위험은 제한적이지만 중심 노드에 변경이 몰리는지는 "
        "Dashboard에서 확인해야 합니다."
    )


def _quality_meaning(grade: str, hotspot_count: int) -> str:
    if grade in {"D", "F"}:
        return "현재 상태는 기능 설명보다 유지보수 위험 설명이 먼저 필요한 코드베이스입니다."
    if hotspot_count > 0:
        return "전체 등급과 별개로 자주 바뀌고 결합도 높은 파일이 있어 우선순위를 분리해야 합니다."
    return "품질 신호가 비교적 안정적이어서 기능 이해와 계획 수립에 집중할 수 있습니다."


def _process_summary(*, history_available: bool, commit_count: int, vibe_confidence: str) -> str:
    if history_available:
        return (
            f"git history {commit_count}개 commit과 vibe-coding 증거 "
            f"{vibe_confidence} 신뢰도를 함께 봅니다."
        )
    return f"git history는 제한적이며, 레포 안 vibe-coding 증거는 {vibe_confidence} 신뢰도입니다."


def _process_meaning(
    *, vibe_area_count: int, vibe_evidence_count: int, process_commit_count: int
) -> str:
    if vibe_evidence_count == 0 and process_commit_count == 0:
        return "에이전트 지침, 명세, 검증, 회고 흔적이 적어 제작 방식을 코드만으로 추정해야 합니다."
    return (
        f"{vibe_area_count}개 프로세스 영역, {vibe_evidence_count}개 파일 증거, "
        f"{process_commit_count}개 process commit이 제작 습관을 설명합니다."
    )


def _process_risk(
    *, history_available: bool, vibe_confidence: str, process_commit_count: int
) -> str:
    if not history_available:
        return "history가 없으면 어떤 의사결정으로 현재 구조가 되었는지 검증하기 어렵습니다."
    if vibe_confidence == "low" and process_commit_count == 0:
        return "AI/에이전트 기반 제작 흔적이 약해 바이브코딩 관점의 재현성 판단은 제한됩니다."
    return "프로세스 증거가 있더라도 실제 품질은 validation과 hotspot 결과로 다시 확인해야 합니다."
