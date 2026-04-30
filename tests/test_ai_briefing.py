from __future__ import annotations

import json

from codexray.web.ai_briefing import parse_ai_briefing_response


def _wrap(payload: dict) -> str:
    return f"```json\n{json.dumps(payload, ensure_ascii=False)}\n```"


def _payload_with_actions(actions: list[dict]) -> dict:
    return {
        "executive": "summary",
        "architecture": "arch",
        "quality_risk": "risk",
        "next_actions": actions,
        "key_insight": "insight",
        "intent_alignment": "",
    }


def test_parse_next_actions_keeps_known_category() -> None:
    result = parse_ai_briefing_response(
        _wrap(
            _payload_with_actions(
                [
                    {
                        "action": "split api router",
                        "reason": "router is busy",
                        "evidence": "api_v2.py 288 lines",
                        "ai_prompt": "",
                        "category": "structural",
                    }
                ]
            )
        ),
        backend="codex",
    )
    assert result is not None
    assert len(result.next_actions) == 1
    assert result.next_actions[0].category == "structural"


def test_parse_next_actions_missing_category_falls_back_to_code() -> None:
    result = parse_ai_briefing_response(
        _wrap(
            _payload_with_actions(
                [
                    {
                        "action": "add unit tests for foo",
                        "reason": "no tests",
                        "evidence": "tests/ has no test_foo.py",
                        "ai_prompt": "",
                    }
                ]
            )
        ),
        backend="codex",
    )
    assert result is not None
    assert result.next_actions[0].category == "code"


def test_parse_next_actions_invalid_category_falls_back_to_code() -> None:
    result = parse_ai_briefing_response(
        _wrap(
            _payload_with_actions(
                [
                    {
                        "action": "x",
                        "reason": "y",
                        "evidence": "z",
                        "ai_prompt": "",
                        "category": "invalid_bucket",
                    }
                ]
            )
        ),
        backend="codex",
    )
    assert result is not None
    assert result.next_actions[0].category == "code"


def test_parse_next_actions_string_form_defaults_to_code() -> None:
    result = parse_ai_briefing_response(
        _wrap(_payload_with_actions(["just a string action"])),
        backend="codex",
    )
    assert result is not None
    assert result.next_actions[0].category == "code"


def test_parse_next_actions_vibe_coding_category_demoted_to_code() -> None:
    # AI is told not to generate vibe_coding (system synthesizes it from
    # vibe_insights data). If AI accidentally returns vibe_coding the parser
    # demotes it to code so behavior is consistent across parser and payload.
    result = parse_ai_briefing_response(
        _wrap(
            _payload_with_actions(
                [
                    {
                        "action": "write CLAUDE.md",
                        "reason": "AI ergonomics",
                        "evidence": "missing",
                        "ai_prompt": "",
                        "category": "vibe_coding",
                    }
                ]
            )
        ),
        backend="codex",
    )
    assert result is not None
    assert result.next_actions[0].category == "code"
