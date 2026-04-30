"""AI-first codebase briefing.

Builds a raw-source-code bundle (with selective files) plus supporting
metrics, calls the codex/claude CLI adapter, and parses the structured
narrative response. The cache key includes PROMPT_VERSION so bumping the
version automatically invalidates prior cached results.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..ai.adapters import AIAdapter, AIAdapterError, select_adapter
from ..briefing import build_codebase_briefing
from ..entrypoints import build_entrypoints
from ..graph import build_graph
from ..hotspots import build_hotspots
from ..inventory import aggregate
from ..metrics import build_metrics
from ..quality import build_quality

PROMPT_VERSION = "v5-categorized-actions"
SCHEMA_VERSION = 5

# vibe_coding 카테고리는 시스템이 vibe_insights 데이터에서만 합성한다.
# AI 응답에 vibe_coding 이 들어와도 code 로 강등 — design.md D2 결정 일관 적용.
_AI_ALLOWED_CATEGORIES = {"code", "structural"}
_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)

# Bundle budgets (chars). codex/claude CLIs accept ~200K tokens; ~3 chars/token
# for Korean prose + code keeps us safely under that budget while leaving
# headroom for the model's response.
_BUNDLE_TOTAL_BUDGET = 90_000
_PER_FILE_MAX = 18_000
_TRUNCATION_HEAD = 12_000
_TRUNCATION_TAIL = 4_000

_KEY_DOC_PATHS = [
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "docs/intent.md",
    "docs/constraints.md",
    "openspec/project.md",
]


@dataclass(frozen=True, slots=True)
class AINextAction:
    action: str
    reason: str
    evidence: str
    ai_prompt: str = ""
    category: str = "code"


@dataclass(frozen=True, slots=True)
class AIBriefingResult:
    schema_version: int
    backend: str
    prompt_version: str
    executive: str
    architecture: str
    quality_risk: str
    next_actions: tuple[AINextAction, ...]
    key_insight: str
    intent_alignment: str = ""
    fallback: bool = False


def build_evidence_bundle(root: Path) -> tuple[str, str]:
    """Backwards-compatible alias for build_raw_code_bundle."""
    return build_raw_code_bundle(root)


def build_raw_code_bundle(root: Path) -> tuple[str, str]:
    """Build a markdown bundle of metadata + selected source files for AI input.

    Returns (bundle_markdown, presenter_summary).
    """
    inventory_rows = list(aggregate(root))
    total_loc = sum(r.loc for r in inventory_rows)
    total_files = sum(r.file_count for r in inventory_rows)

    graph = build_graph(root)
    metrics = build_metrics(graph)
    quality = build_quality(root)
    hotspots = build_hotspots(root)
    entrypoints = build_entrypoints(root)
    briefing = build_codebase_briefing(root)

    selected_paths = _select_key_files(
        root=root,
        metrics=metrics,
        hotspots=hotspots,
        entrypoints=entrypoints,
    )

    sections: list[str] = []
    sections.append(f"# Repository: {root.name}\n")
    sections.append(_format_overview(inventory_rows, total_files, total_loc, quality))
    sections.append(_format_structure(graph, metrics, hotspots))
    sections.append(_format_files_section(root, selected_paths))

    bundle = "\n\n".join(sections)
    bundle = _enforce_budget(bundle, _BUNDLE_TOTAL_BUDGET)
    return bundle, briefing.presenter_summary


def _format_overview(
    inventory_rows: list[Any],
    total_files: int,
    total_loc: int,
    quality: Any,
) -> str:
    languages = ", ".join(
        f"{r.language}({r.file_count}f / {r.loc}L)" for r in inventory_rows
    ) or "감지된 언어 없음"
    grade = quality.overall.grade or "N/A"
    score = quality.overall.score if quality.overall.score is not None else "N/A"
    dim_lines = "\n".join(
        f"- {name}: {dim.grade or 'N/A'} ({dim.score if dim.score is not None else 'N/A'})"
        for name, dim in sorted(quality.dimensions.items())
    )
    return (
        "## 메타데이터\n\n"
        f"- 총 파일: {total_files}\n"
        f"- 총 LoC: {total_loc}\n"
        f"- 언어: {languages}\n"
        f"- 종합 품질: {grade} ({score})\n\n"
        "## 품질 차원\n\n"
        f"{dim_lines or '- (차원 데이터 없음)'}"
    )


def _format_structure(graph: Any, metrics: Any, hotspots: Any) -> str:
    top_coupled = sorted(
        metrics.nodes,
        key=lambda n: -(n.fan_in + n.fan_out + n.external_fan_out),
    )[:5]
    top_hot = sorted(hotspots.files, key=lambda f: -(f.change_count * f.coupling))[:5]
    coupled_lines = "\n".join(
        f"- {n.path}: fan_in={n.fan_in}, fan_out={n.fan_out}, "
        f"coupling={n.fan_in + n.fan_out + n.external_fan_out}"
        for n in top_coupled
    )
    hot_lines = "\n".join(
        f"- {f.path}: priority={f.change_count * f.coupling}, "
        f"changes={f.change_count}, coupling={f.coupling}, category={f.category}"
        for f in top_hot
    )
    return (
        "## 구조 요약\n\n"
        f"- nodes: {len(graph.nodes)}, edges: {len(graph.edges)}\n"
        f"- DAG: {metrics.graph.is_dag}, largest SCC: {metrics.graph.largest_scc_size}\n"
        f"- hotspot 카운트: {hotspots.summary.hotspot}\n\n"
        "### 결합도 상위 파일\n"
        f"{coupled_lines or '- (없음)'}\n\n"
        "### Hotspot 상위 파일\n"
        f"{hot_lines or '- (없음)'}"
    )


def _format_files_section(root: Path, selected: list[tuple[str, Path]]) -> str:
    if not selected:
        return "## 핵심 소스 파일\n\n(선택된 파일이 없습니다.)"
    blocks: list[str] = ["## 핵심 소스 파일\n"]
    for label, path in selected:
        rel = path.relative_to(root) if path.is_absolute() else path
        content = _read_truncated(path)
        blocks.append(f"### `{rel}` — {label}\n\n```\n{content}\n```")
    return "\n\n".join(blocks)


def _select_key_files(
    *,
    root: Path,
    metrics: Any,
    hotspots: Any,
    entrypoints: Any,
) -> list[tuple[str, Path]]:
    selected: list[tuple[str, Path]] = []
    seen: set[str] = set()

    def add(label: str, candidate: Path) -> None:
        try:
            resolved = candidate.resolve()
        except OSError:
            return
        if not resolved.is_file():
            return
        key = str(resolved)
        if key in seen:
            return
        seen.add(key)
        selected.append((label, resolved))

    for rel in _KEY_DOC_PATHS:
        add("project doc", root / rel)

    for ep in list(entrypoints.entrypoints)[:2]:
        add(f"entrypoint ({ep.kind})", root / ep.path)

    top_hot = sorted(hotspots.files, key=lambda f: -(f.change_count * f.coupling))[:3]
    for f in top_hot:
        add("top hotspot", root / f.path)

    top_coupled = sorted(
        metrics.nodes,
        key=lambda n: -(n.fan_in + n.fan_out + n.external_fan_out),
    )[:3]
    for n in top_coupled:
        add("high coupling", root / n.path)

    return selected


def _read_truncated(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"(파일 읽기 실패: {exc})"
    if len(text) <= _PER_FILE_MAX:
        return text
    head = text[:_TRUNCATION_HEAD]
    tail = text[-_TRUNCATION_TAIL:]
    omitted = len(text) - _TRUNCATION_HEAD - _TRUNCATION_TAIL
    return f"{head}\n\n... [중략 — {omitted}자 생략] ...\n\n{tail}"


def _enforce_budget(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n... [전체 번들 길이 초과 — 마지막 부분 생략] ..."


def build_ai_briefing_prompt(bundle_markdown: str) -> str:
    return f"""당신은 시니어 개발자이자 바이브코딩 코치입니다. **독자는 코드를 모르는 비개발자(바이브코더)**입니다. 아래에 레포의 메타데이터, 구조 요약, 핵심 소스 파일이 직접 첨부되어 있습니다. 직접 코드를 읽고 한국어로 종합 브리핑을 작성하십시오.

다음 JSON 형식으로만 답하십시오. 다른 설명 없이 JSON 블록만:

```json
{{
  "executive": "이 코드베이스가 무엇을 하는 프로젝트인지, 도메인·역할·주요 기능을 한두 문장으로",
  "architecture": "구조적 특징을 평어로 — '한 파일이 너무 많은 일을 함', '흐름이 한 방향으로 흐름' 같은 표현. 메트릭 용어 자체는 쓰지 말고 의미만 전달",
  "quality_risk": "품질 등급의 실질적 의미와 상위 위험 파일이 사용자에게 미칠 영향 2~3문장. 등급 자체는 인용하되 '의미는 ~이다' 형태로 풀어 설명",
  "next_actions": [
    {{
      "action": "구체적이고 실행 가능한 행동 한 줄",
      "reason": "왜 이 행동이 필요한지 한 문장 — '~기 때문에'로 인과 연결",
      "evidence": "분석에서 인용한 근거 (등급/파일명/수치/커밋)",
      "ai_prompt": "비개발자가 Claude/Codex CLI에 그대로 복사·붙여넣기 할 수 있는 자연어 명령. 예: 'src/foo.py를 두 부분으로 나누세요. 1) 데이터 가져오기 2) 화면 그리기. 변경 후 기존 동작이 그대로 유지되어야 합니다.'",
      "category": "code 또는 structural 중 하나. code는 함수/모듈 내부 변경(테스트 보강·에러 처리·로직 정리 등), structural은 모듈 분리·의존성 정리·아키텍처 변경"
    }},
    {{ "action": "...", "reason": "...", "evidence": "...", "ai_prompt": "...", "category": "code | structural" }},
    {{ "action": "...", "reason": "...", "evidence": "...", "ai_prompt": "...", "category": "code | structural" }}
  ],
  "key_insight": "코드를 읽고 발견한 가장 중요한 한 가지 통찰 (의도/구조 차원)",
  "intent_alignment": "docs/intent.md 또는 README가 있다면 그 내용과 현재 코드의 일치/불일치를 한 문단으로 짚어라. 의도와 결과 사이의 갭을 구체적으로. 의도 문서가 없으면 빈 문자열을 반환"
}}
```

**중요한 작성 규칙 (비개발자가 독자):**
1. 메트릭 용어 (DAG, SCC, fan-in, fan-out, coupling, hotspot priority, p90 등) **직접 사용 금지**. 대신 '순환 없는 흐름', '한 파일에 의존이 몰림', '자주 바뀌고 위험한 파일' 같은 평어 사용
2. 등급 (A/B/C/D/F)과 파일 경로는 그대로 인용 OK
3. 수치 (예: 'Hotspot 23개', '테스트 0점')는 인용하되 의미를 함께 풀어줄 것
4. next_actions의 ai_prompt 필드는 비개발자가 그대로 AI에게 복사해서 보낼 수 있는 자연어 작업 지시여야 함 (코드 작성 지침)
5. intent_alignment는 의도 문서가 있을 때만 채우고, 의도와 코드 사이의 구체적 갭을 짚을 것
6. next_actions의 category 필드는 반드시 "code" 또는 "structural" 중 하나로 채울 것. "vibe_coding" 카테고리는 시스템이 별도로 채우니 **절대 생성하지 말 것**
7. next_actions는 카테고리당 최대 3개, 합쳐서 최대 6개 (vibe_coding은 시스템이 별도로 추가). 카테고리가 비어있어도 OK (해당 카테고리에 추천할 게 없으면 그 카테고리 항목 자체를 생략)

레포 자료:

{bundle_markdown}
"""


def parse_ai_briefing_response(text: str, backend: str) -> AIBriefingResult | None:
    match = _JSON_BLOCK_RE.search(text)
    raw = match.group(1) if match else text.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            return None
        try:
            data = json.loads(text[start:end])
        except json.JSONDecodeError:
            return None

    executive = str(data.get("executive", "")).strip()
    architecture = str(data.get("architecture", "")).strip()
    quality_risk = str(data.get("quality_risk", "")).strip()
    key_insight = str(data.get("key_insight", "")).strip()
    intent_alignment = str(data.get("intent_alignment", "")).strip()
    next_actions = _parse_next_actions(data.get("next_actions", []))

    if not executive or not quality_risk or not next_actions:
        return None

    return AIBriefingResult(
        schema_version=SCHEMA_VERSION,
        backend=backend,
        prompt_version=PROMPT_VERSION,
        executive=executive,
        architecture=architecture,
        quality_risk=quality_risk,
        next_actions=next_actions,
        key_insight=key_insight,
        intent_alignment=intent_alignment,
    )


def _parse_next_actions(raw: Any) -> tuple[AINextAction, ...]:
    if not isinstance(raw, list):
        return ()
    actions: list[AINextAction] = []
    for item in raw:
        if isinstance(item, dict):
            action = str(item.get("action", "")).strip()
            reason = str(item.get("reason", "")).strip()
            evidence = str(item.get("evidence", "")).strip()
            ai_prompt = str(item.get("ai_prompt", "")).strip()
            category = str(item.get("category", "code")).strip()
            if category not in _AI_ALLOWED_CATEGORIES:
                category = "code"
            if not action:
                continue
            actions.append(
                AINextAction(
                    action=action,
                    reason=reason or "AI 해석에서 도출된 우선 행동입니다.",
                    evidence=evidence or "근거 인용 없음",
                    ai_prompt=ai_prompt,
                    category=category,
                )
            )
        elif isinstance(item, str):
            text = item.strip()
            if text:
                actions.append(
                    AINextAction(
                        action=text,
                        reason="AI 해석에서 도출된 우선 행동입니다.",
                        evidence="근거 인용 없음",
                        ai_prompt="",
                        category="code",
                    )
                )
    return tuple(actions)


def make_cache_key(root: Path, evidence_json: str, adapter_id: str) -> str:
    h = hashlib.sha256()
    h.update(f"{root}\x00{adapter_id}\x00{PROMPT_VERSION}\x00".encode())
    h.update(evidence_json.encode("utf-8"))
    return h.hexdigest()


def _cache_dir() -> Path:
    override = os.environ.get("CODEXRAY_CACHE_DIR", "").strip()
    base = Path(override) if override else Path.home() / ".cache" / "codexray" / "ai-briefing"
    base.mkdir(parents=True, exist_ok=True)
    return base


def cache_get(key: str) -> AIBriefingResult | None:
    target = _cache_dir() / f"{key}.json"
    if not target.exists():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if int(data.get("schema_version", 0)) != SCHEMA_VERSION:
            return None
        if str(data.get("prompt_version", "")) != PROMPT_VERSION:
            return None
        return AIBriefingResult(
            schema_version=int(data["schema_version"]),
            backend=str(data["backend"]),
            prompt_version=str(data["prompt_version"]),
            executive=str(data["executive"]),
            architecture=str(data["architecture"]),
            quality_risk=str(data["quality_risk"]),
            next_actions=tuple(
                AINextAction(
                    action=str(a["action"]),
                    reason=str(a["reason"]),
                    evidence=str(a["evidence"]),
                    ai_prompt=str(a.get("ai_prompt", "")),
                    category=(
                        str(a.get("category", "code"))
                        if str(a.get("category", "code")) in _AI_ALLOWED_CATEGORIES
                        else "code"
                    ),
                )
                for a in data["next_actions"]
            ),
            key_insight=str(data["key_insight"]),
            intent_alignment=str(data.get("intent_alignment", "")),
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return None


def cache_put(key: str, result: AIBriefingResult) -> None:
    target = _cache_dir() / f"{key}.json"
    target.write_text(
        json.dumps(
            {
                "schema_version": result.schema_version,
                "backend": result.backend,
                "prompt_version": result.prompt_version,
                "executive": result.executive,
                "architecture": result.architecture,
                "quality_risk": result.quality_risk,
                "next_actions": [
                    {
                        "action": a.action,
                        "reason": a.reason,
                        "evidence": a.evidence,
                        "ai_prompt": a.ai_prompt,
                        "category": a.category,
                    }
                    for a in result.next_actions
                ],
                "key_insight": result.key_insight,
                "intent_alignment": result.intent_alignment,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def build_ai_briefing(
    root: Path,
    evidence_json: str,
    adapter: AIAdapter | None = None,
) -> tuple[AIBriefingResult | None, str | None]:
    if adapter is None:
        try:
            adapter = select_adapter(os.environ)
        except AIAdapterError as exc:
            return None, f"AI 어댑터 미설정: {exc}"

    cache_key = make_cache_key(root, evidence_json, adapter.name)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached, None

    prompt = build_ai_briefing_prompt(evidence_json)
    try:
        response = adapter.review(prompt, timeout=300)
    except AIAdapterError as exc:
        return None, f"AI 호출 실패: {exc}"

    result = parse_ai_briefing_response(response, adapter.name)
    if result is None:
        return None, "AI 응답 파싱 실패"

    cache_put(cache_key, result)
    return result, None
