from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entrypoint:
    path: str
    language: str | None
    kind: str
    detail: str


@dataclass(frozen=True, slots=True)
class EntrypointResult:
    schema_version: int
    entrypoints: tuple[Entrypoint, ...]
