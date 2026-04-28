from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .types import VibeCodingReport, VibeEvidence, VibeFinding

SCHEMA_VERSION = 1

_EXACT_ARTIFACTS: tuple[tuple[str, str, str, str], ...] = (
    ("AGENTS.md", "agent_instructions", "file", "Agent operating handbook"),
    ("CLAUDE.md", "agent_instructions", "file", "Claude Code project instructions"),
    (".claude/skills", "agent_instructions", "directory", "Claude/OpenSpec skills"),
    (".claude/commands", "agent_instructions", "directory", "Claude slash commands"),
    ("openspec/changes", "spec_workflow", "directory", "OpenSpec change proposals"),
    ("openspec/specs", "spec_workflow", "directory", "Archived capability specs"),
    (".omc/project-memory.json", "memory_handoff", "file", "OMC project memory"),
    (".omc/sessions", "memory_handoff", "directory", "OMC session history"),
    ("docs/validation", "validation", "directory", "Validation captures"),
    ("docs/vibe-coding", "retrospectives", "directory", "Vibe-coding retrospectives"),
    (".roboco/config.json", "automation", "file", "ROBOCO project setup"),
    (".husky/pre-commit", "automation", "file", "Git hook automation"),
    (".claude/settings.json", "automation", "file", "Claude project permissions"),
    (".claude/settings.local.json", "automation", "file", "Claude local permissions"),
)

_GLOB_ARTIFACTS: tuple[tuple[str, str, str, str], ...] = (
    ("docs/handoff*.md", "memory_handoff", "file", "Handoff document"),
    ("docs/**/retro*.md", "retrospectives", "file", "Retrospective document"),
    ("**/AGENTS.md", "agent_instructions", "file", "Nested agent handbook"),
    ("**/CLAUDE.md", "agent_instructions", "file", "Nested Claude instructions"),
)

_AREA_LABELS = {
    "agent_instructions": "agent instructions",
    "spec_workflow": "spec workflow",
    "memory_handoff": "memory and handoff",
    "validation": "validation",
    "retrospectives": "retrospectives",
    "automation": "automation",
}


def build_vibe_coding_report(root: Path) -> VibeCodingReport:
    resolved = root.resolve()
    evidence = tuple(sorted(_detect_evidence(resolved), key=_evidence_sort_key))
    areas = tuple(sorted({item.area for item in evidence}))
    score = _confidence_score(areas)
    return VibeCodingReport(
        schema_version=SCHEMA_VERSION,
        confidence=_confidence_label(score),
        confidence_score=score,
        process_areas=areas,
        evidence=evidence,
        strengths=tuple(_strengths(areas, evidence)),
        risks=tuple(_risks(areas, evidence)),
        actions=tuple(_actions(areas, evidence)),
    )


def _detect_evidence(root: Path) -> Iterable[VibeEvidence]:
    seen: set[tuple[str, str]] = set()
    for rel_path, area, kind, detail in _EXACT_ARTIFACTS:
        path = root / rel_path
        if kind == "directory" and not path.is_dir():
            continue
        if kind == "file" and not path.is_file():
            continue
        key = (area, rel_path)
        seen.add(key)
        yield VibeEvidence(area=area, path=rel_path, kind=kind, detail=detail)

    for pattern, area, kind, detail in _GLOB_ARTIFACTS:
        for path in sorted(root.glob(pattern), key=lambda p: p.relative_to(root).as_posix()):
            rel_path = path.relative_to(root).as_posix()
            if rel_path.startswith(".git/"):
                continue
            if kind == "directory" and not path.is_dir():
                continue
            if kind == "file" and not path.is_file():
                continue
            key = (area, rel_path)
            if key in seen:
                continue
            seen.add(key)
            yield VibeEvidence(area=area, path=rel_path, kind=kind, detail=detail)


def _confidence_score(areas: tuple[str, ...]) -> int:
    if not areas:
        return 0
    return min(100, len(areas) * 18)


def _confidence_label(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def _strengths(
    areas: tuple[str, ...],
    evidence: tuple[VibeEvidence, ...],
) -> list[VibeFinding]:
    items: list[VibeFinding] = []
    area_set = set(areas)
    if "agent_instructions" in area_set:
        items.append(
            VibeFinding(
                category="agent_instructions",
                text="에이전트가 따라야 할 작업 규칙이 레포 안에 남아 있습니다.",
                evidence_paths=_paths_for(evidence, "agent_instructions"),
            )
        )
    if "spec_workflow" in area_set:
        items.append(
            VibeFinding(
                category="spec_workflow",
                text="코드 전에 변경 의도와 요구사항을 남기는 명세 흐름이 보입니다.",
                evidence_paths=_paths_for(evidence, "spec_workflow"),
            )
        )
    if "validation" in area_set:
        items.append(
            VibeFinding(
                category="validation",
                text="분석 결과를 실제 프로젝트에서 검증한 흔적이 있습니다.",
                evidence_paths=_paths_for(evidence, "validation"),
            )
        )
    if "retrospectives" in area_set:
        items.append(
            VibeFinding(
                category="retrospectives",
                text="세션 회고를 통해 작업 방식의 문제와 학습을 기록했습니다.",
                evidence_paths=_paths_for(evidence, "retrospectives"),
            )
        )
    return items[:3]


def _risks(
    areas: tuple[str, ...],
    evidence: tuple[VibeEvidence, ...],
) -> list[VibeFinding]:
    items: list[VibeFinding] = []
    area_set = set(areas)
    if not area_set:
        return [
            VibeFinding(
                category="missing_evidence",
                text="바이브코딩 과정이나 에이전트 환경을 판단할 근거가 거의 없습니다.",
                evidence_paths=("missing:vibe-coding-artifacts",),
            )
        ]
    if "validation" not in area_set:
        items.append(
            VibeFinding(
                category="validation",
                text="에이전트 작업 결과를 실제 입력으로 검증한 캡처가 보이지 않습니다.",
                evidence_paths=("missing:docs/validation",),
            )
        )
    if "memory_handoff" not in area_set:
        items.append(
            VibeFinding(
                category="memory_handoff",
                text="다음 세션이 이어받을 메모리나 handoff 근거가 부족합니다.",
                evidence_paths=("missing:.omc/project-memory.json", "missing:docs/handoff*.md"),
            )
        )
    if "agent_instructions" in area_set and "spec_workflow" not in area_set:
        items.append(
            VibeFinding(
                category="spec_workflow",
                text="에이전트 지침은 있지만 변경 명세를 강제하는 흐름은 약해 보입니다.",
                evidence_paths=_paths_for(evidence, "agent_instructions")
                + ("missing:openspec",),
            )
        )
    return items[:3]


def _actions(
    areas: tuple[str, ...],
    evidence: tuple[VibeEvidence, ...],
) -> list[VibeFinding]:
    area_set = set(areas)
    items: list[VibeFinding] = []
    if "agent_instructions" not in area_set:
        items.append(
            VibeFinding(
                category="agent_instructions",
                text="AGENTS.md 또는 CLAUDE.md에 에이전트 작업 규칙을 먼저 정리하세요.",
                evidence_paths=("missing:AGENTS.md", "missing:CLAUDE.md"),
            )
        )
    if "spec_workflow" not in area_set:
        items.append(
            VibeFinding(
                category="spec_workflow",
                text="큰 변경은 OpenSpec 같은 명세 흐름으로 의도와 검증 조건을 남기세요.",
                evidence_paths=("missing:openspec",),
            )
        )
    if "validation" not in area_set:
        items.append(
            VibeFinding(
                category="validation",
                text="대표 입력에서 실행 결과를 docs/validation 아래에 캡처하세요.",
                evidence_paths=("missing:docs/validation",),
            )
        )
    if "memory_handoff" not in area_set:
        items.append(
            VibeFinding(
                category="memory_handoff",
                text="다음 에이전트가 이어받을 handoff와 프로젝트 메모리를 남기세요.",
                evidence_paths=("missing:.omc/project-memory.json", "missing:docs/handoff*.md"),
            )
        )
    if not items:
        items.append(
            VibeFinding(
                category="maintenance",
                text="현재 환경을 유지하되, 새 결정은 메모리와 회고에 계속 누적하세요.",
                evidence_paths=tuple(item.path for item in evidence[:3]),
            )
        )
    return items[:3]


def _paths_for(evidence: tuple[VibeEvidence, ...], area: str) -> tuple[str, ...]:
    return tuple(item.path for item in evidence if item.area == area)


def _evidence_sort_key(item: VibeEvidence) -> tuple[str, str, str]:
    return (_AREA_LABELS.get(item.area, item.area), item.path, item.kind)
