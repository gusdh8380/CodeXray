"""AI-first codebase briefing: collect all evidence, call Claude/Codex CLI, return structured analysis."""
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
from ..briefing import to_json as briefing_to_json
from ..graph import build_graph
from ..graph import to_json as graph_to_json
from ..hotspots import build_hotspots
from ..hotspots import to_json as hotspots_to_json
from ..inventory import aggregate
from ..metrics import build_metrics
from ..metrics import to_json as metrics_to_json
from ..quality import build_quality
from ..quality import to_json as quality_to_json

PROMPT_VERSION = "v1"
SCHEMA_VERSION = 1
_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


@dataclass(frozen=True, slots=True)
class AIBriefingResult:
    schema_version: int
    backend: str
    prompt_version: str
    executive: str
    architecture: str
    quality_risk: str
    next_actions: tuple[str, ...]
    key_insight: str
    fallback: bool = False


def build_evidence_bundle(root: Path) -> tuple[str, str]:
    """Run all deterministic analyzers and return (evidence_json, briefing_presenter_summary)."""
    inventory_rows = aggregate(root)
    total_loc = sum(r.loc for r in inventory_rows)
    languages = [{"language": r.language, "files": r.file_count, "loc": r.loc} for r in inventory_rows]

    graph = build_graph(root)
    graph_data = json.loads(graph_to_json(graph))

    metrics = build_metrics(graph)
    metrics_data = json.loads(metrics_to_json(metrics))
    top_coupled = sorted(
        metrics.nodes,
        key=lambda n: -(n.fan_in + n.fan_out + n.external_fan_out),
    )[:5]

    quality = build_quality(root)
    quality_data = json.loads(quality_to_json(quality))

    hotspots = build_hotspots(root)
    hotspots_data = json.loads(hotspots_to_json(hotspots))
    top_hotspots = sorted(
        hotspots.files,
        key=lambda f: -(f.change_count * f.coupling),
    )[:5]

    briefing = build_codebase_briefing(root)
    presenter_summary = briefing.presenter_summary

    evidence: dict[str, Any] = {
        "inventory": {
            "total_loc": total_loc,
            "file_count": sum(r.file_count for r in inventory_rows),
            "languages": languages,
        },
        "graph": {
            "node_count": graph_data.get("node_count"),
            "edge_count": graph_data.get("edge_count"),
            "is_dag": metrics.graph.is_dag,
            "largest_scc_size": metrics.graph.largest_scc_size,
        },
        "metrics": {
            "top_coupled": [
                {
                    "path": n.path,
                    "fan_in": n.fan_in,
                    "fan_out": n.fan_out,
                    "coupling": n.fan_in + n.fan_out + n.external_fan_out,
                }
                for n in top_coupled
            ],
        },
        "quality": {
            "overall_grade": quality_data.get("overall", {}).get("grade"),
            "overall_score": quality_data.get("overall", {}).get("score"),
            "dimensions": {
                name: {"grade": dim.get("grade"), "score": dim.get("score")}
                for name, dim in quality_data.get("dimensions", {}).items()
            },
        },
        "hotspots": {
            "summary": hotspots_data.get("summary"),
            "top_files": [
                {
                    "path": f.path,
                    "category": f.category,
                    "coupling": f.coupling,
                    "change_count": f.change_count,
                    "priority": f.change_count * f.coupling,
                }
                for f in top_hotspots
            ],
        },
    }
    return json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True), presenter_summary


def build_ai_briefing_prompt(evidence_json: str) -> str:
    return f"""당신은 코드베이스 분석 전문가입니다. 아래 분석 데이터를 보고 한국어로 종합 분석을 작성하십시오.

다음 JSON 형식으로만 답하십시오. 다른 설명 없이 JSON 블록만:

```json
{{
  "executive": "이 코드베이스가 무엇인지, 현재 상태를 한두 문장으로",
  "architecture": "구조적 특징 (규모, 결합도, DAG 여부, 주요 의존 구조) 2~3문장",
  "quality_risk": "품질 등급 해석과 상위 위험 파일 중심으로 실질적 위험 2~3문장",
  "next_actions": ["우선순위 높은 다음 행동 1", "다음 행동 2", "다음 행동 3"],
  "key_insight": "시니어 개발자 관점에서 가장 중요한 한 가지 인사이트"
}}
```

요구사항:
- 수치 근거를 반드시 포함할 것 (등급, 파일명, 숫자)
- 비개발자도 이해할 수 있는 언어로 작성
- next_actions는 구체적이고 실행 가능해야 함

분석 데이터:
```json
{evidence_json}
```"""


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
    actions_raw = data.get("next_actions", [])
    next_actions = tuple(str(a).strip() for a in actions_raw if str(a).strip())

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
    )


def make_cache_key(root: Path, evidence_json: str, adapter_id: str) -> str:
    h = hashlib.sha256()
    h.update(f"{root}\x00{adapter_id}\x00{PROMPT_VERSION}\x00".encode())
    h.update(evidence_json.encode("utf-8"))
    return h.hexdigest()


def _cache_dir() -> Path:
    base = Path(os.environ.get("CODEXRAY_CACHE_DIR", "")) or (
        Path.home() / ".cache" / "codexray" / "ai-briefing"
    )
    base.mkdir(parents=True, exist_ok=True)
    return base


def cache_get(key: str) -> AIBriefingResult | None:
    target = _cache_dir() / f"{key}.json"
    if not target.exists():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return AIBriefingResult(
            schema_version=int(data["schema_version"]),
            backend=str(data["backend"]),
            prompt_version=str(data["prompt_version"]),
            executive=str(data["executive"]),
            architecture=str(data["architecture"]),
            quality_risk=str(data["quality_risk"]),
            next_actions=tuple(str(a) for a in data["next_actions"]),
            key_insight=str(data["key_insight"]),
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
                "next_actions": list(result.next_actions),
                "key_insight": result.key_insight,
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
