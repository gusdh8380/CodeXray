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


# briefing-persona-split: ai_prompt 3단 구조 시나리오


_VALID_3STAGE_PROMPT = (
    "[현재 프로젝트] 로컬 코드베이스 분석 도구입니다.\n"
    "[해줄 일] api_v2.py 를 두 부분으로 나누세요.\n"
    "[성공 기준과 직접 확인 방법] 기존 API 엔드포인트가 그대로 응답하는지 확인해 주세요."
)


def test_parse_next_actions_keeps_valid_3stage_prompt_unchanged() -> None:
    result = parse_ai_briefing_response(
        _wrap(
            _payload_with_actions(
                [
                    {
                        "action": "split api router",
                        "reason": "router is busy",
                        "evidence": "api_v2.py 288 lines",
                        "ai_prompt": _VALID_3STAGE_PROMPT,
                        "category": "structural",
                    }
                ]
            )
        ),
        backend="codex",
    )
    assert result is not None
    assert result.next_actions[0].ai_prompt == _VALID_3STAGE_PROMPT


def test_parse_next_actions_missing_required_label_replaced_with_template() -> None:
    # AI returned a non-empty ai_prompt but skipped [성공 기준과 직접 확인 방법].
    # Parser must replace the whole text with a deterministic 3-stage template
    # that uses the parsed executive as the project context.
    bad_prompt = (
        "[현재 프로젝트] 로컬 분석 도구.\n"
        "[해줄 일] api_v2.py 를 분할하세요."
    )
    result = parse_ai_briefing_response(
        _wrap(
            {
                "executive": "이 레포는 로컬 코드 분석 도구입니다.",
                "architecture": "arch",
                "quality_risk": "risk",
                "next_actions": [
                    {
                        "action": "split api router",
                        "reason": "router is busy",
                        "evidence": "api_v2.py 288 lines",
                        "ai_prompt": bad_prompt,
                        "category": "structural",
                    }
                ],
                "key_insight": "insight",
                "intent_alignment": "",
            }
        ),
        backend="codex",
    )
    assert result is not None
    rewritten = result.next_actions[0].ai_prompt
    assert rewritten != bad_prompt
    assert "[현재 프로젝트]" in rewritten
    assert "[해줄 일]" in rewritten
    assert "[성공 기준과 직접 확인 방법]" in rewritten
    assert "로컬 코드 분석 도구" in rewritten  # executive 가 project_context 로 인용됨
    assert "split api router" in rewritten


def test_parse_next_actions_empty_prompt_stays_empty() -> None:
    # 빈 ai_prompt 는 backward-compat 으로 그대로 보존. 3단 규칙 미적용.
    result = parse_ai_briefing_response(
        _wrap(
            _payload_with_actions(
                [
                    {
                        "action": "x",
                        "reason": "y",
                        "evidence": "z",
                        "ai_prompt": "",
                        "category": "code",
                    }
                ]
            )
        ),
        backend="codex",
    )
    assert result is not None
    assert result.next_actions[0].ai_prompt == ""
