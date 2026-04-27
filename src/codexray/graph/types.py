from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Node:
    path: str
    language: str


@dataclass(frozen=True, slots=True)
class Edge:
    from_: str
    to: str
    kind: str  # "internal" | "external"


@dataclass(frozen=True, slots=True)
class Graph:
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]


@dataclass(frozen=True, slots=True)
class RawImport:
    source: Path
    raw: str
    level: int  # 0 for absolute / non-Python, >= 1 for Python relative imports
    language: str  # "Python" | "JavaScript" | "TypeScript"
