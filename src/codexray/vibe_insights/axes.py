"""Three-axis vibe-coding evaluation: intent / verification / continuity.

Each axis evaluates a non-negotiable aspect of "주인이 있는 프로젝트":
- intent: 외부화된 의도 — 새 AI 세션이 맥락 없이도 이어받을 수 있는가
- verification: 독립 검증 — 결과를 사람이 직접 확인할 수 있는가
- continuity: 이어받기 — 다음 세션이 진행을 이어갈 수 있는가

Returns a 4-level state (strong / moderate / weak / unknown) instead of a
0–100 score so the false precision trap is avoided. Raw ratio is preserved
in `_raw_score` for debugging.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# State thresholds (ratio of detected signals over pool size).
_STRONG_RATIO = 0.7
_MODERATE_RATIO = 0.4
_WEAK_RATIO = 0.1

# Minimum size for an AI guide doc to count as "충실도 충족".
_MIN_GUIDE_SIZE = 500

# README purpose detection keywords (English + Korean).
_PURPOSE_KEYWORDS = (
    "what",
    "purpose",
    "why",
    "이 프로젝트",
    "이 도구",
    "이 라이브러리",
    "this is",
    "we built",
    "designed to",
    "정체",
    "무엇",
    "역할",
)


def _file_exists(root: Path, path: str) -> bool:
    p = root / path
    return p.exists() and p.is_file()


def _dir_exists(root: Path, path: str) -> bool:
    p = root / path
    return p.exists() and p.is_dir()


def _file_size(root: Path, path: str) -> int:
    p = root / path
    if not p.exists() or not p.is_file():
        return 0
    try:
        return p.stat().st_size
    except OSError:
        return 0


def _read_text_safe(root: Path, path: str, *, max_chars: int = 5000) -> str:
    p = root / path
    if not p.exists() or not p.is_file():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError:
        return ""


def _has_purpose_paragraph(readme_text: str) -> bool:
    """README가 'what / why / 이 프로젝트는' 같은 의도 표현을 첫 단락에 포함하는가."""
    if not readme_text or len(readme_text) < 200:
        return False
    paras = [p.strip() for p in readme_text.split("\n\n") if p.strip()][:5]
    head = "\n".join(paras).lower()
    return any(kw.lower() in head for kw in _PURPOSE_KEYWORDS)


def _signal(label: str, present: bool, evidence: str = "") -> dict[str, Any]:
    return {"label": label, "present": present, "evidence": evidence}


# --- intent 축 sub-categories ---

_AI_GUIDE_FILES = (
    "CLAUDE.md",
    "AGENTS.md",
    ".cursorrules",
    ".windsurfrules",
    ".aider.conf.yml",
    ".github/copilot-instructions.md",
)
_AI_GUIDE_DIRS = (".cursor/rules", ".continue", ".windsurf")


def _check_ai_guide_doc(root: Path) -> dict[str, Any]:
    """Sub-cat 1 of intent: AI 지속 지시 문서 1종 이상 + 충실도."""
    found: list[str] = []
    for path in _AI_GUIDE_FILES:
        if _file_exists(root, path) and _file_size(root, path) >= _MIN_GUIDE_SIZE:
            found.append(path)
    for d in _AI_GUIDE_DIRS:
        if _dir_exists(root, d):
            found.append(f"{d}/")
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "AI 지속 지시 문서 없음"
    return _signal("AI 지속 지시 문서", present, evidence)


_PROJECT_INTENT_FILES = (
    "docs/intent.md",
    "VISION.md",
    "ABOUT.md",
    "PROJECT.md",
    "OVERVIEW.md",
    "openspec/project.md",
)


def _check_project_intent_doc(root: Path) -> dict[str, Any]:
    """Sub-cat 2 of intent: 프로젝트 의도 문서 1종 이상 (README purpose 문단 포함)."""
    found: list[str] = []
    for path in _PROJECT_INTENT_FILES:
        if _file_exists(root, path):
            found.append(path)
    if not found:
        readme_text = _read_text_safe(root, "README.md")
        if _has_purpose_paragraph(readme_text):
            found.append("README.md (purpose 문단)")
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "프로젝트 의도 문서 없음"
    return _signal("프로젝트 의도 문서", present, evidence)


def _check_intent_vs_non_intent(root: Path) -> dict[str, Any]:
    """Sub-cat 3 of intent: 의도와 비의도(Not / Out of Scope / ADR / decision log)."""
    found: list[str] = []
    for intent_path in ("docs/intent.md", "openspec/project.md"):
        if _file_exists(root, intent_path):
            text = _read_text_safe(root, intent_path)
            if re.search(
                r"^##+\s*(Not|Non[- ]?Goals|Out of Scope|하지 않을)",
                text,
                re.MULTILINE | re.IGNORECASE,
            ):
                found.append(f"{intent_path} 의 Not 섹션")
    if _dir_exists(root, "docs/adr") or _dir_exists(root, "docs/decisions"):
        found.append("ADR / decisions 디렉토리")
    if _file_exists(root, "CHANGELOG.md"):
        text = _read_text_safe(root, "CHANGELOG.md")
        if len(text) > 1000 and re.search(r"because|reason|이유|why", text, re.IGNORECASE):
            found.append("CHANGELOG.md (reasoning)")
    proposal_dir = root / "openspec" / "changes"
    if proposal_dir.exists():
        try:
            for p in proposal_dir.rglob("proposal.md"):
                text = p.read_text(encoding="utf-8", errors="replace")[:2000]
                if re.search(r"^##\s*Why", text, re.MULTILINE):
                    found.append("openspec proposal Why")
                    break
        except (OSError, ValueError):
            pass
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "의도+비의도 명문화 없음"
    return _signal("의도와 비의도 명문화", present, evidence)


# --- verification 축 sub-categories ---

def _check_manual_validation(root: Path) -> dict[str, Any]:
    """Sub-cat 1 of verification: 손 검증 흔적."""
    found: list[str] = []
    if _dir_exists(root, "docs/validation"):
        found.append("docs/validation/")
    for d in ("screenshots", "screenshot", "demo", "docs/demo", "docs/screenshots"):
        if _dir_exists(root, d):
            found.append(f"{d}/")
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "손 검증 흔적 없음"
    return _signal("손 검증 흔적", present, evidence)


_TEST_DIRS = ("tests", "test", "__tests__", "spec")
_CI_PATHS = (
    (".github/workflows", True),
    (".gitlab-ci.yml", False),
    (".circleci", True),
    ("Jenkinsfile", False),
    ("azure-pipelines.yml", False),
)


def _check_test_and_ci(root: Path) -> dict[str, Any]:
    """Sub-cat 2 of verification: 자동 테스트 + CI."""
    found: list[str] = []
    for d in _TEST_DIRS:
        if _dir_exists(root, d):
            found.append(f"{d}/")
            break
    for path, is_dir in _CI_PATHS:
        if (is_dir and _dir_exists(root, path)) or (not is_dir and _file_exists(root, path)):
            found.append(path + ("/" if is_dir else ""))
            break
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "자동 테스트 / CI 없음"
    return _signal("자동 테스트와 CI", present, evidence)


def _check_runnable_path(root: Path) -> dict[str, Any]:
    """Sub-cat 3 of verification: 재현 가능 실행 경로."""
    found: list[str] = []
    readme = _read_text_safe(root, "README.md")
    if re.search(
        r"```(?:bash|sh|shell)?\s*\n[^`]*?(?:npm|pnpm|yarn|pip|poetry|cargo|make|go|python|node)\s+\w+",
        readme,
    ):
        found.append("README 명령 블록")
    pkg_text = _read_text_safe(root, "package.json", max_chars=2000)
    if pkg_text and '"scripts"' in pkg_text:
        found.append("package.json scripts")
    pyproject = _read_text_safe(root, "pyproject.toml", max_chars=3000)
    if pyproject and ("[project.scripts]" in pyproject or "[tool.poetry.scripts]" in pyproject):
        found.append("pyproject.toml scripts")
    if _file_exists(root, "Makefile"):
        found.append("Makefile")
    if _file_exists(root, "justfile") or _file_exists(root, ".justfile"):
        found.append("justfile")
    if _file_exists(root, "Dockerfile"):
        found.append("Dockerfile")
    if _file_exists(root, "docker-compose.yml") or _file_exists(root, "docker-compose.yaml"):
        found.append("docker-compose")
    for env in (".env.example", ".env.sample", "env.example"):
        if _file_exists(root, env):
            found.append(env)
            break
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "재현 가능 실행 경로 없음"
    return _signal("재현 가능 실행 경로", present, evidence)


# --- continuity 축 sub-categories ---

def _check_small_continuity(root: Path, history: Any) -> dict[str, Any]:
    """Sub-cat 1 of continuity: 작게 쪼개고 이어갈 수 있다."""
    found: list[str] = []
    for p in ("openspec/changes", "PLANS.md", "TODO.md", "ROADMAP.md", ".github/ISSUE_TEMPLATE"):
        if _dir_exists(root, p) or _file_exists(root, p):
            found.append(p)
    if history.available and history.commit_count >= 5:
        found.append(f"git history ({history.commit_count}개 커밋)")
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "작게 이어가기 흔적 없음"
    return _signal("작게 이어가기", present, evidence)


def _check_learning_capture(root: Path, history: Any) -> dict[str, Any]:
    """Sub-cat 2 of continuity: 실패에서 배운 흔적이 다음 변경에 반영."""
    found: list[str] = []
    for d in ("docs/retro", "docs/postmortem", "docs/lessons", "docs/vibe-coding"):
        if _dir_exists(root, d):
            found.append(f"{d}/")
    if _file_exists(root, "CHANGELOG.md"):
        found.append("CHANGELOG.md")
    if history.available and history.process_commits:
        process_count = len(history.process_commits)
        if process_count > 0:
            found.append(f"프로세스 커밋 ({process_count}개)")
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "학습 반영 흔적 없음"
    return _signal("학습 반영", present, evidence)


def _check_handoff_doc(root: Path) -> dict[str, Any]:
    """Sub-cat 3 of continuity: 핸드오프 문서."""
    found: list[str] = []
    for path in ("HANDOFF.md", "ONBOARDING.md", "CONTRIBUTING.md", "docs/handoff"):
        if _file_exists(root, path) or _dir_exists(root, path):
            found.append(path)
    present = len(found) > 0
    evidence = ", ".join(found[:3]) if found else "핸드오프 문서 없음"
    return _signal("핸드오프 문서", present, evidence)


# --- State derivation ---

def _state_from_signals(
    signals: list[dict[str, Any]],
    *,
    core_satisfied: bool,
) -> tuple[str, int, int, float]:
    """Compute (state, signal_count, pool_size, ratio).

    state: strong (ratio ≥ 0.7 AND core_satisfied) > moderate (≥ 0.4) >
    weak (≥ 0.1) > unknown (0 or empty pool).
    """
    pool_size = len(signals)
    if pool_size == 0:
        return "unknown", 0, 0, 0.0
    signal_count = sum(1 for s in signals if s["present"])
    ratio = signal_count / pool_size
    if signal_count == 0:
        return "unknown", 0, pool_size, 0.0
    if ratio >= _STRONG_RATIO and core_satisfied:
        return "strong", signal_count, pool_size, ratio
    if ratio >= _MODERATE_RATIO:
        return "moderate", signal_count, pool_size, ratio
    if ratio >= _WEAK_RATIO:
        return "weak", signal_count, pool_size, ratio
    return "weak", signal_count, pool_size, ratio


def _build_axis(
    *,
    name: str,
    label: str,
    signals: list[dict[str, Any]],
    core_satisfied: bool,
) -> dict[str, Any]:
    state, count, pool, ratio = _state_from_signals(signals, core_satisfied=core_satisfied)
    top_signals = [s["evidence"] for s in signals if s["present"]][:3]
    weaknesses = [s["label"] for s in signals if not s["present"]]
    return {
        "name": name,
        "label": label,
        "state": state,
        "signal_count": count,
        "signal_pool_size": pool,
        "signal_ratio": round(ratio, 2),
        "top_signals": top_signals,
        "weaknesses": weaknesses,
        "breakdown": signals,
        "_raw_score": int(ratio * 100),
    }


# --- Public axes API ---

def axis_intent(*, root: Path) -> dict[str, Any]:
    """의도 축 — 외부화된 의도가 있는가."""
    signals = [
        _check_ai_guide_doc(root),
        _check_project_intent_doc(root),
        _check_intent_vs_non_intent(root),
    ]
    # 핵심 신호: AI 지속 지시 문서 + 프로젝트 의도 문서 — 둘 다 있어야 strong 가능.
    core = signals[0]["present"] and signals[1]["present"]
    return _build_axis(name="intent", label="의도", signals=signals, core_satisfied=core)


def axis_verification(*, root: Path) -> dict[str, Any]:
    """검증 축 — 결과를 독립적으로 확인할 수 있는가."""
    signals = [
        _check_manual_validation(root),
        _check_test_and_ci(root),
        _check_runnable_path(root),
    ]
    # 핵심 신호: 자동 테스트+CI + 재현 가능 실행 경로 — 둘 다 있어야 strong 가능.
    core = signals[1]["present"] and signals[2]["present"]
    return _build_axis(name="verification", label="검증", signals=signals, core_satisfied=core)


def axis_continuity(*, root: Path, history: Any) -> dict[str, Any]:
    """이어받기 축 — 다음 세션이 이어갈 수 있는가."""
    signals = [
        _check_small_continuity(root, history),
        _check_learning_capture(root, history),
        _check_handoff_doc(root),
    ]
    # 핵심 신호: 작게 이어가기 sub-cat (saved plans) — strong 의 필수.
    core = signals[0]["present"]
    return _build_axis(name="continuity", label="이어받기", signals=signals, core_satisfied=core)


# --- Process proxies (Decision 8) ---

def build_process_proxies(*, history: Any, hotspots: Any) -> dict[str, Any]:
    """약한 process proxy 정보를 보조 정보로 분리.

    feat/fix 비율, 프로세스 커밋 비율, hotspot 누적 — Goodhart 위험이 있는 약한
    proxy. 축 상태 결정에는 사용하지 않고 사용자에게 *참고용* 으로만 노출.
    """
    items: list[dict[str, Any]] = []

    if history.available and history.commit_count > 0:
        process_ratio = len(history.process_commits) / max(1, history.commit_count)
        items.append(
            {
                "label": "프로세스 커밋 비율",
                "value": f"{process_ratio*100:.0f}%",
                "raw": round(process_ratio, 3),
            }
        )
        type_dist = {e.label: int(e.value) for e in history.type_distribution}
        feat_count = type_dist.get("feat", 0)
        fix_count = type_dist.get("fix", 0)
        if feat_count > 0:
            items.append(
                {
                    "label": "fix/feat 비율",
                    "value": (
                        f"{fix_count}/{feat_count} ({fix_count/feat_count*100:.0f}%)"
                    ),
                    "raw": round(fix_count / feat_count, 3),
                }
            )

    if hotspots.summary.hotspot > 0:
        items.append(
            {
                "label": "Hotspot 개수",
                "value": str(hotspots.summary.hotspot),
                "raw": hotspots.summary.hotspot,
            }
        )

    return {
        "available": len(items) > 0,
        "items": items,
        "note": "참고용 — 단독 판정 근거 아님",
    }


# --- Blind spots (Decision 6) ---

BLIND_SPOTS: tuple[str, ...] = (
    "사용자(나)가 What/Why/Next 를 자기 입으로 설명할 수 있는가",
    "다음 행동의 우선순위를 사람이 정하고 있는가",
    "손으로 한 검증이 실제로 매번 굴러가는가",
    (
        "외부 도구(Notion, Confluence, Slack, Linear 등)와 README 같은 문서의 "
        "질적 깊이는 자동 판단 못 합니다"
    ),
)


def get_blind_spots() -> list[str]:
    """평가 결과와 무관하게 항상 함께 노출되는 사각지대 4 항목."""
    return list(BLIND_SPOTS)
