import json

from codexray.ai.prompt import build_prompt, parse_response


def _valid_payload(max_line: int) -> dict:
    return {
        "dimensions": {
            "readability": {
                "score": 80,
                "evidence_lines": [1, max_line],
                "comment": "ok",
                "suggestion": "minor cleanup",
            },
            "design": {
                "score": 70,
                "evidence_lines": [1],
                "comment": "single responsibility",
                "suggestion": "split when grows",
            },
            "maintainability": {
                "score": 75,
                "evidence_lines": [1],
                "comment": "easy to follow",
                "suggestion": "add docstring",
            },
            "risk": {
                "score": 90,
                "evidence_lines": [1],
                "comment": "low surface",
                "suggestion": "add type hints",
            },
        },
        "confidence": "medium",
        "limitations": "no caller context",
    }


def _wrap(payload: dict) -> str:
    return f"```json\n{json.dumps(payload)}\n```"


def test_prompt_includes_numbered_lines() -> None:
    prompt = build_prompt("foo.py", "x = 1\ny = 2\n")
    assert "1: x = 1" in prompt
    assert "2: y = 2" in prompt
    assert "foo.py" in prompt


def test_prompt_deterministic() -> None:
    src = "def f():\n    return 1\n"
    assert build_prompt("a.py", src) == build_prompt("a.py", src)


def test_parse_valid_response() -> None:
    payload, reason = parse_response(_wrap(_valid_payload(5)), max_line=5)
    assert reason is None
    assert payload is not None
    assert payload["confidence"] == "medium"


def test_parse_no_json_block() -> None:
    payload, reason = parse_response("just plain text, no JSON", max_line=5)
    assert payload is None
    assert "json" in (reason or "").lower()


def test_parse_invalid_json() -> None:
    payload, reason = parse_response("```json\n{not valid}\n```", max_line=5)
    assert payload is None
    assert "json" in (reason or "").lower()


def test_parse_missing_dimension() -> None:
    p = _valid_payload(5)
    del p["dimensions"]["risk"]
    payload, reason = parse_response(_wrap(p), max_line=5)
    assert payload is None
    assert "risk" in (reason or "")


def test_parse_empty_evidence_lines() -> None:
    p = _valid_payload(5)
    p["dimensions"]["readability"]["evidence_lines"] = []
    payload, reason = parse_response(_wrap(p), max_line=5)
    assert payload is None
    assert "evidence_lines" in (reason or "")


def test_parse_evidence_out_of_range() -> None:
    p = _valid_payload(5)
    p["dimensions"]["design"]["evidence_lines"] = [99]
    payload, reason = parse_response(_wrap(p), max_line=5)
    assert payload is None
    assert "design" in (reason or "")


def test_parse_score_out_of_range() -> None:
    p = _valid_payload(5)
    p["dimensions"]["risk"]["score"] = 150
    payload, reason = parse_response(_wrap(p), max_line=5)
    assert payload is None
    assert "score" in (reason or "")


def test_parse_invalid_confidence() -> None:
    p = _valid_payload(5)
    p["confidence"] = "uncertain"
    payload, reason = parse_response(_wrap(p), max_line=5)
    assert payload is None
    assert "confidence" in (reason or "")


def test_parse_empty_limitations() -> None:
    p = _valid_payload(5)
    p["limitations"] = "   "
    payload, reason = parse_response(_wrap(p), max_line=5)
    assert payload is None
    assert "limitations" in (reason or "")


def test_parse_empty_comment() -> None:
    p = _valid_payload(5)
    p["dimensions"]["maintainability"]["comment"] = ""
    payload, reason = parse_response(_wrap(p), max_line=5)
    assert payload is None
    assert "maintainability" in (reason or "")
