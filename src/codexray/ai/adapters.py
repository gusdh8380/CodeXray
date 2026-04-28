from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from typing import Protocol


class AIAdapterError(RuntimeError):
    """Raised when no AI backend is usable or a backend call fails."""


class AIAdapter(Protocol):
    name: str

    def review(self, prompt: str, timeout: int = 120) -> str:
        ...


class CodexCLIAdapter:
    name = "codex"

    def review(self, prompt: str, timeout: int = 120) -> str:
        out_file = tempfile.NamedTemporaryFile(  # noqa: SIM115 — explicit close below
            mode="w", suffix=".txt", delete=False
        )
        out_file.close()
        try:
            try:
                result = subprocess.run(
                    [
                        "codex",
                        "exec",
                        "--color",
                        "never",
                        "--skip-git-repo-check",
                        "--ephemeral",
                        "--output-last-message",
                        out_file.name,
                        prompt,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=timeout,
                )
            except FileNotFoundError as exc:
                raise AIAdapterError("codex CLI not found on PATH") from exc
            except subprocess.TimeoutExpired as exc:
                raise AIAdapterError(
                    f"codex CLI timed out after {timeout}s"
                ) from exc
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                raise AIAdapterError(
                    f"codex CLI exit {result.returncode}: {stderr[:200]}"
                )
            with open(out_file.name, encoding="utf-8") as fh:
                return fh.read()
        finally:
            with contextlib.suppress(OSError):
                os.unlink(out_file.name)


class ClaudeCLIAdapter:
    name = "claude"

    def review(self, prompt: str, timeout: int = 120) -> str:
        try:
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )
        except FileNotFoundError as exc:
            raise AIAdapterError("claude CLI not found on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise AIAdapterError(f"claude CLI timed out after {timeout}s") from exc
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise AIAdapterError(
                f"claude CLI exit {result.returncode}: {stderr[:200]}"
            )
        return result.stdout


def select_adapter(env: Mapping[str, str]) -> AIAdapter:
    backend = env.get("CODEXRAY_AI_BACKEND", "auto").strip().lower() or "auto"

    if backend == "codex":
        if shutil.which("codex") is None:
            raise AIAdapterError(
                "CODEXRAY_AI_BACKEND=codex but codex CLI not found on PATH"
            )
        return CodexCLIAdapter()
    if backend == "claude":
        if shutil.which("claude") is None:
            raise AIAdapterError(
                "CODEXRAY_AI_BACKEND=claude but claude CLI not found on PATH"
            )
        return ClaudeCLIAdapter()
    if backend != "auto":
        raise AIAdapterError(
            f"unknown CODEXRAY_AI_BACKEND value: {backend!r} "
            "(expected auto/codex/claude)"
        )

    if shutil.which("codex") is not None:
        return CodexCLIAdapter()
    if shutil.which("claude") is not None:
        return ClaudeCLIAdapter()
    raise AIAdapterError(
        "no AI backend available — install codex (`brew install --cask codex`) "
        "or claude CLI"
    )
