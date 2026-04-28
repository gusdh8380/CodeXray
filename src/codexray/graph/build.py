from __future__ import annotations

import sys
from pathlib import Path

from ..language import classify
from ..walk import walk
from . import csharp_parser, js_parser, python_parser
from .csharp_index import build_namespace_index
from .resolve import resolve
from .types import Edge, Graph, Node, RawImport

_TARGET_LANGUAGES: frozenset[str] = frozenset(
    {"Python", "JavaScript", "TypeScript", "C#"}
)


def build_graph(root: Path) -> Graph:
    root = root.resolve()
    typed_files: list[tuple[Path, str]] = []
    for path in walk(root):
        language = classify(path)
        if language in _TARGET_LANGUAGES:
            typed_files.append((path.resolve(), language))

    internal_paths = {path for path, _ in typed_files}
    namespace_index = _build_csharp_index(typed_files)

    edge_set: set[tuple[str, str, str]] = set()
    for path, language in typed_files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        raws, syntax_error = _extract(text, path, language)
        if syntax_error:
            print(
                f"warning: syntax error parsing {path.relative_to(root).as_posix()}",
                file=sys.stderr,
            )
        from_rel = path.relative_to(root).as_posix()
        for raw in raws:
            resolved = resolve(raw, root, internal_paths, namespace_index)
            if not resolved:
                edge_set.add((from_rel, raw.raw, "external"))
                continue
            for target in resolved:
                edge_set.add((from_rel, target.relative_to(root).as_posix(), "internal"))

    nodes = [
        Node(path=path.relative_to(root).as_posix(), language=language)
        for path, language in typed_files
    ]
    nodes.sort(key=lambda n: n.path)

    edges = [Edge(from_=f, to=t, kind=k) for f, t, k in edge_set]
    edges.sort(key=lambda e: (e.from_, e.to, e.kind))

    return Graph(nodes=tuple(nodes), edges=tuple(edges))


def _build_csharp_index(typed_files: list[tuple[Path, str]]) -> dict[str, set[Path]]:
    cs_inputs: list[tuple[Path, str]] = []
    for path, language in typed_files:
        if language != "C#":
            continue
        try:
            cs_inputs.append((path, path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return build_namespace_index(cs_inputs)


def _extract(
    text: str, path: Path, language: str
) -> tuple[list[RawImport], bool]:
    if language == "Python":
        return python_parser.extract_imports(text, path)
    if language == "C#":
        return csharp_parser.extract_imports(text, path), False
    return js_parser.extract_imports(text, path, language), False
