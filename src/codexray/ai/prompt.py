from __future__ import annotations

import json
import re

_DIMENSIONS = ("readability", "design", "maintainability", "risk")
_CONFIDENCE_VALUES = frozenset({"low", "medium", "high"})
_JSON_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def build_prompt(rel_path: str, source: str) -> str:
    numbered = "\n".join(
        f"{i + 1}: {line}" for i, line in enumerate(source.splitlines())
    )
    return f"""당신은 코드 리뷰어입니다. 아래 파일을 읽고 4차원으로 평가하십시오:
가독성(readability), 설계(design), 유지보수성(maintainability), 위험(risk).

규칙:
- 각 차원에 0-100 점수, 근거가 되는 라인 번호 list(>=1개), 1-2문장 코멘트, 1-2문장 개선 제안.
- evidence_lines가 비면 그 차원은 invalid이므로 반드시 1개 이상 포함.
- confidence는 "low"/"medium"/"high" 중 하나. 파일이 짧거나 컨텍스트 부족하면 low.
- limitations는 보지 못한 부분(예: 호출자, 테스트 부재)을 1-2문장으로 반드시 채울 것.
- 출력은 ```json ... ``` 코드 블록으로 감싼 단일 JSON. 다른 텍스트 금지.

JSON 스키마:
```json
{{
  "dimensions": {{
    "readability":     {{"score": 0, "evidence_lines": [1], "comment": "", "suggestion": ""}},
    "design":          {{"score": 0, "evidence_lines": [1], "comment": "", "suggestion": ""}},
    "maintainability": {{"score": 0, "evidence_lines": [1], "comment": "", "suggestion": ""}},
    "risk":            {{"score": 0, "evidence_lines": [1], "comment": "", "suggestion": ""}}
  }},
  "confidence": "low",
  "limitations": ""
}}
```

파일: {rel_path}
```
{numbered}
```
"""


def parse_response(text: str, max_line: int) -> tuple[dict | None, str | None]:
    """Return ``(parsed_payload, skip_reason)``.

    On success, ``parsed_payload`` is a validated dict and ``skip_reason`` is
    ``None``. On any validation failure, ``parsed_payload`` is ``None`` and
    ``skip_reason`` describes why.
    """
    match = _JSON_BLOCK.search(text)
    if match is None:
        return None, "no ```json ... ``` block found in response"
    raw = match.group(1)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"json decode error: {exc.msg}"
    if not isinstance(payload, dict):
        return None, "top-level payload is not an object"

    dims = payload.get("dimensions")
    if not isinstance(dims, dict):
        return None, "missing or non-object 'dimensions'"
    for name in _DIMENSIONS:
        dim = dims.get(name)
        reason = _validate_dimension(name, dim, max_line)
        if reason is not None:
            return None, reason

    confidence = payload.get("confidence")
    if confidence not in _CONFIDENCE_VALUES:
        return None, "missing or invalid 'confidence' (must be low/medium/high)"

    limitations = payload.get("limitations")
    if not isinstance(limitations, str) or not limitations.strip():
        return None, "missing or empty 'limitations'"

    return payload, None


def _validate_dimension(name: str, dim, max_line: int) -> str | None:
    if not isinstance(dim, dict):
        return f"missing or non-object dimension '{name}'"
    score = dim.get("score")
    if not isinstance(score, int) or not 0 <= score <= 100:
        return f"dimension '{name}' has invalid score (must be int 0-100)"
    evidence = dim.get("evidence_lines")
    if not isinstance(evidence, list) or not evidence:
        return f"dimension '{name}' has empty or missing evidence_lines"
    if not all(isinstance(line, int) for line in evidence):
        return f"dimension '{name}' evidence_lines must be int list"
    if any(line < 1 or line > max_line for line in evidence):
        return f"dimension '{name}' evidence_lines outside file range (1..{max_line})"
    comment = dim.get("comment")
    if not isinstance(comment, str) or not comment.strip():
        return f"dimension '{name}' has empty or missing comment"
    suggestion = dim.get("suggestion")
    if not isinstance(suggestion, str) or not suggestion.strip():
        return f"dimension '{name}' has empty or missing suggestion"
    return None
