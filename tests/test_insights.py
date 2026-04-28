from __future__ import annotations

from pathlib import Path

import pytest

from codexray.web.insights import (
    PROMPT_VERSION,
    InsightBullet,
    InsightResult,
    cache_get,
    cache_key,
    cache_put,
    parse_response,
)


def _wrap(body: str) -> str:
    return f"some prefix\n```text\n{body}\n```\nsome suffix"


def test_parse_response_accepts_minimum_valid_response() -> None:
    body = (
        "[risk] 모듈 X에 결합도가 높음\n변경 시 회귀 위험\n\n"
        "[next] 테스트 추가\n변경 안전성 확보"
    )
    bullets, reason = parse_response(_wrap(body))
    assert reason is None
    assert bullets is not None
    assert len(bullets) == 2
    assert bullets[0].tag == "risk"
    assert bullets[1].tag == "next"


def test_parse_response_accepts_general_bullet() -> None:
    body = (
        "[risk] 결합도 위험\n회귀 가능\n\n"
        "[next] 추가 테스트\n안전성 확보\n\n"
        "관찰 사실 한 줄\n그러므로 학습 가치"
    )
    bullets, reason = parse_response(_wrap(body))
    assert reason is None
    assert bullets is not None
    assert len(bullets) == 3
    assert bullets[2].tag == "general"


def test_parse_response_rejects_missing_risk() -> None:
    body = "[next] 다음 행동 한 줄\n함의 한 줄\n\n관찰 한 줄\n또 다른 함의"
    bullets, reason = parse_response(_wrap(body))
    assert bullets is None
    assert reason is not None
    assert "risk" in reason


def test_parse_response_rejects_missing_next() -> None:
    body = "[risk] 위험 한 줄\n함의 한 줄\n\n관찰 한 줄\n함의 한 줄"
    bullets, reason = parse_response(_wrap(body))
    assert bullets is None
    assert reason is not None
    assert "next" in reason


def test_parse_response_rejects_empty_response() -> None:
    bullets, reason = parse_response("")
    assert bullets is None
    assert reason == "empty response"


def test_parse_response_rejects_too_short_bullet() -> None:
    body = "[risk] x\ny"
    bullets, reason = parse_response(_wrap(body))
    assert bullets is None
    assert reason is not None
    assert "short" in reason


def test_parse_response_rejects_too_many_bullets() -> None:
    chunks = ["[risk] 위험 한 줄\n함의 한 줄", "[next] 다음 행동\n함의 한 줄"]
    for _ in range(9):
        chunks.append("관찰 한 줄\n함의 한 줄")
    body = "\n\n".join(chunks)
    bullets, reason = parse_response(_wrap(body))
    assert bullets is None
    assert reason is not None
    assert "too many" in reason


def test_parse_response_works_without_code_block() -> None:
    body = "[risk] 위험 관찰 한 줄\n함의 한 줄\n\n[next] 행동 한 줄\n함의 한 줄"
    bullets, reason = parse_response(body)
    assert reason is None
    assert bullets is not None


def test_cache_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEXRAY_CACHE_DIR", str(tmp_path))
    result = InsightResult(
        schema_version=1,
        backend="codex",
        prompt_version=PROMPT_VERSION,
        tab="quality",
        bullets=(
            InsightBullet(tag="risk", observation="결합도 높음", implication="회귀 위험"),
            InsightBullet(tag="next", observation="테스트 추가", implication="안전성 확보"),
        ),
    )
    key = cache_key(path="/x", tab="quality", raw_json="{}", adapter_id="codex")
    cache_put(key, result)
    loaded = cache_get(key)
    assert loaded is not None
    assert loaded.tab == "quality"
    assert loaded.backend == "codex"
    assert len(loaded.bullets) == 2
    assert loaded.bullets[0].tag == "risk"


def test_cache_miss_returns_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEXRAY_CACHE_DIR", str(tmp_path))
    assert cache_get("nonexistent") is None


def test_cache_key_changes_when_inputs_differ() -> None:
    base = cache_key(path="/a", tab="inventory", raw_json="{}", adapter_id="codex")
    by_path = cache_key(path="/b", tab="inventory", raw_json="{}", adapter_id="codex")
    by_tab = cache_key(path="/a", tab="graph", raw_json="{}", adapter_id="codex")
    by_raw = cache_key(path="/a", tab="inventory", raw_json="{}\n", adapter_id="codex")
    by_adapter = cache_key(path="/a", tab="inventory", raw_json="{}", adapter_id="claude")
    keys = {base, by_path, by_tab, by_raw, by_adapter}
    assert len(keys) == 5
