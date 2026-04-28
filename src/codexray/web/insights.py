"""Senior insights generation from raw analysis JSON.

Generates 3~5 Korean bullets via codex/claude CLI adapter and disk-caches by
sha256 of (path | tab | raw_json | adapter | prompt_version).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from ..ai.adapters import AIAdapter, AIAdapterError, select_adapter

PROMPT_VERSION = "v1"
SCHEMA_VERSION = 1
_MIN_BULLETS = 1
_MAX_BULLETS = 10
_BULLET_LEN_FLOOR = 5
_RISK_PREFIXES = ("[risk]", "[위험]")
_NEXT_PREFIXES = ("[next]", "[next-action]", "[다음]", "[다음 행동]")
_BLOCK_RE = re.compile(r"```text\s*(.*?)```", re.DOTALL)


@dataclass(frozen=True, slots=True)
class InsightBullet:
    tag: str  # "risk" | "next" | "general"
    observation: str
    implication: str


@dataclass(frozen=True, slots=True)
class InsightResult:
    schema_version: int
    backend: str
    prompt_version: str
    tab: str
    bullets: tuple[InsightBullet, ...]


def build_prompt(tab: str, raw_json: str) -> str:
    return f"""당신은 시니어 코드 리뷰어입니다. 아래는 CodeXray의 `{tab}` 분석 결과 raw JSON입니다.
이 JSON만 보고 시니어 개발자 관점에서 한국어 인사이트 3~5개를 작성하십시오.

규칙:
- 각 불릿은 정확히 두 줄로 작성합니다.
  첫 줄은 관찰(JSON에서 보이는 사실), 둘째 줄은 함의(그래서 무엇이 위험·기회인가).
- 적어도 1개 불릿은 `[risk]` 태그로 시작 (위험 신호).
- 적어도 1개 불릿은 `[next]` 태그로 시작 (다음 행동 제안).
- 나머지는 태그 없이 일반 관찰.
- 출력은 ```text ... ``` 코드 블록으로 감싸고 다른 설명 없이 불릿만.

형식:
```text
[risk] 관찰 한 줄
함의 한 줄

[next] 관찰 한 줄
함의 한 줄

관찰 한 줄
함의 한 줄
```

`{tab}` 분석 결과 JSON:
```json
{raw_json}
```
"""


def parse_response(text: str) -> tuple[tuple[InsightBullet, ...] | None, str | None]:
    match = _BLOCK_RE.search(text)
    body = (match.group(1) if match else text).strip()
    if not body:
        return None, "empty response"

    raw_blocks = re.split(r"\n\s*\n", body)
    bullets: list[InsightBullet] = []
    for block in raw_blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        observation = lines[0]
        implication = " ".join(lines[1:])
        tag = "general"
        lower = observation.lower()
        matched = False
        for prefix in _RISK_PREFIXES:
            if lower.startswith(prefix):
                tag = "risk"
                observation = observation[len(prefix):].strip()
                matched = True
                break
        if not matched:
            for prefix in _NEXT_PREFIXES:
                if lower.startswith(prefix):
                    tag = "next"
                    observation = observation[len(prefix):].strip()
                    break
        if len(observation) < _BULLET_LEN_FLOOR or len(implication) < _BULLET_LEN_FLOOR:
            return None, "bullet too short"
        bullets.append(
            InsightBullet(tag=tag, observation=observation, implication=implication)
        )

    if len(bullets) < _MIN_BULLETS:
        return None, f"too few bullets ({len(bullets)} < {_MIN_BULLETS})"
    if len(bullets) > _MAX_BULLETS:
        return None, f"too many bullets ({len(bullets)} > {_MAX_BULLETS})"
    if not any(b.tag == "risk" for b in bullets):
        return None, "missing [risk] bullet"
    if not any(b.tag == "next" for b in bullets):
        return None, "missing [next] bullet"
    return tuple(bullets), None


def cache_dir(env: Mapping[str, str] | None = None) -> Path:
    e = env if env is not None else os.environ
    base_str = e.get("CODEXRAY_CACHE_DIR", "")
    base = Path(base_str) if base_str else Path.home() / ".cache" / "codexray" / "insights"
    base.mkdir(parents=True, exist_ok=True)
    return base


def cache_key(*, path: str, tab: str, raw_json: str, adapter_id: str) -> str:
    h = hashlib.sha256()
    h.update(f"{path}\x00{tab}\x00{adapter_id}\x00{PROMPT_VERSION}\x00".encode())
    h.update(raw_json.encode("utf-8"))
    return h.hexdigest()


def cache_get(key: str, env: Mapping[str, str] | None = None) -> InsightResult | None:
    target = cache_dir(env) / f"{key}.json"
    if not target.exists():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return _result_from_dict(data)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def cache_put(
    key: str, result: InsightResult, env: Mapping[str, str] | None = None
) -> None:
    target = cache_dir(env) / f"{key}.json"
    target.write_text(
        json.dumps(_result_to_dict(result), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_insights(
    tab: str,
    raw_json: str,
    adapter: AIAdapter | None = None,
) -> tuple[InsightResult | None, str | None]:
    if adapter is None:
        adapter = select_adapter(os.environ)
    prompt = build_prompt(tab, raw_json)
    try:
        response = adapter.review(prompt, timeout=300)
    except AIAdapterError as exc:
        return None, f"adapter error: {exc}"
    bullets, reason = parse_response(response)
    if bullets is None:
        return None, reason or "invalid response"
    return (
        InsightResult(
            schema_version=SCHEMA_VERSION,
            backend=adapter.name,
            prompt_version=PROMPT_VERSION,
            tab=tab,
            bullets=bullets,
        ),
        None,
    )


def _result_to_dict(result: InsightResult) -> dict:
    return {
        "schema_version": result.schema_version,
        "backend": result.backend,
        "prompt_version": result.prompt_version,
        "tab": result.tab,
        "bullets": [
            {"tag": b.tag, "observation": b.observation, "implication": b.implication}
            for b in result.bullets
        ],
    }


def _result_from_dict(data: dict) -> InsightResult:
    return InsightResult(
        schema_version=int(data["schema_version"]),
        backend=str(data["backend"]),
        prompt_version=str(data["prompt_version"]),
        tab=str(data["tab"]),
        bullets=tuple(
            InsightBullet(
                tag=str(b["tag"]),
                observation=str(b["observation"]),
                implication=str(b["implication"]),
            )
            for b in data["bullets"]
        ),
    )
