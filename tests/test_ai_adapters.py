from unittest.mock import patch

import pytest

from codexray.ai.adapters import (
    AIAdapterError,
    ClaudeCLIAdapter,
    CodexCLIAdapter,
    select_adapter,
)


def _which(found: set[str]):
    def _impl(cmd: str):
        return f"/usr/bin/{cmd}" if cmd in found else None

    return _impl


def test_select_auto_prefers_codex() -> None:
    with patch("codexray.ai.adapters.shutil.which", _which({"codex", "claude"})):
        adapter = select_adapter({})
    assert isinstance(adapter, CodexCLIAdapter)


def test_select_auto_falls_back_to_claude() -> None:
    with patch("codexray.ai.adapters.shutil.which", _which({"claude"})):
        adapter = select_adapter({})
    assert isinstance(adapter, ClaudeCLIAdapter)


def test_select_auto_no_backend_raises() -> None:
    with (
        patch("codexray.ai.adapters.shutil.which", _which(set())),
        pytest.raises(AIAdapterError, match="no AI backend"),
    ):
        select_adapter({})


def test_select_force_codex() -> None:
    with patch("codexray.ai.adapters.shutil.which", _which({"codex", "claude"})):
        adapter = select_adapter({"CODEXRAY_AI_BACKEND": "codex"})
    assert isinstance(adapter, CodexCLIAdapter)


def test_select_force_codex_missing_raises() -> None:
    with (
        patch("codexray.ai.adapters.shutil.which", _which({"claude"})),
        pytest.raises(AIAdapterError, match="codex CLI not found"),
    ):
        select_adapter({"CODEXRAY_AI_BACKEND": "codex"})


def test_select_force_claude() -> None:
    with patch("codexray.ai.adapters.shutil.which", _which({"codex", "claude"})):
        adapter = select_adapter({"CODEXRAY_AI_BACKEND": "claude"})
    assert isinstance(adapter, ClaudeCLIAdapter)


def test_select_force_claude_missing_raises() -> None:
    with (
        patch("codexray.ai.adapters.shutil.which", _which({"codex"})),
        pytest.raises(AIAdapterError, match="claude CLI not found"),
    ):
        select_adapter({"CODEXRAY_AI_BACKEND": "claude"})


def test_select_unknown_backend_raises() -> None:
    with (
        patch("codexray.ai.adapters.shutil.which", _which({"codex"})),
        pytest.raises(AIAdapterError, match="unknown CODEXRAY_AI_BACKEND"),
    ):
        select_adapter({"CODEXRAY_AI_BACKEND": "gemini"})


def test_select_uppercase_value_normalized() -> None:
    with patch("codexray.ai.adapters.shutil.which", _which({"codex"})):
        adapter = select_adapter({"CODEXRAY_AI_BACKEND": "CODEX"})
    assert isinstance(adapter, CodexCLIAdapter)


def test_codex_adapter_subprocess_failure() -> None:
    adapter = CodexCLIAdapter()
    fake_result = type(
        "R", (), {"returncode": 1, "stdout": "", "stderr": "auth missing"}
    )()
    with (
        patch("codexray.ai.adapters.subprocess.run", return_value=fake_result),
        pytest.raises(AIAdapterError, match="exit 1"),
    ):
        adapter.review("hi")


def test_claude_adapter_subprocess_failure() -> None:
    adapter = ClaudeCLIAdapter()
    fake_result = type(
        "R", (), {"returncode": 2, "stdout": "", "stderr": "rate limited"}
    )()
    with (
        patch("codexray.ai.adapters.subprocess.run", return_value=fake_result),
        pytest.raises(AIAdapterError, match="exit 2"),
    ):
        adapter.review("hi")


def test_claude_adapter_returns_stdout() -> None:
    adapter = ClaudeCLIAdapter()
    fake_result = type(
        "R", (), {"returncode": 0, "stdout": "hello", "stderr": ""}
    )()
    with patch("codexray.ai.adapters.subprocess.run", return_value=fake_result):
        assert adapter.review("hi") == "hello"
