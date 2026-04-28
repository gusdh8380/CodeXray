from __future__ import annotations

import sys
from pathlib import Path

from ..language import classify
from ..walk import walk
from . import csharp_parser, js_parser, python_parser
from .csharp_index import CSharpIndexes, build_indexes
from .resolve import resolve_csharp_types, resolve_js, resolve_python
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
    cs_indexes = _build_csharp_indexes(typed_files)
    cs_type_usages = _build_csharp_type_usages(typed_files)

    edge_set: set[tuple[str, str, str]] = set()
    for path, language in typed_files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        from_rel = path.relative_to(root).as_posix()

        if language == "Python":
            raws, syntax_error = python_parser.extract_imports(text, path)
            if syntax_error:
                print(
                    f"warning: syntax error parsing {from_rel}",
                    file=sys.stderr,
                )
            _emit_python_edges(raws, root, internal_paths, from_rel, edge_set)
        elif language == "C#":
            raws = csharp_parser.extract_imports(text, path)
            type_usages = cs_type_usages.get(path, set())
            _emit_csharp_edges(
                raws,
                path,
                from_rel,
                root,
                cs_indexes,
                type_usages,
                edge_set,
            )
        else:
            raws = js_parser.extract_imports(text, path, language)
            _emit_js_edges(raws, internal_paths, root, from_rel, edge_set)

    nodes = [
        Node(path=path.relative_to(root).as_posix(), language=language)
        for path, language in typed_files
    ]
    nodes.sort(key=lambda n: n.path)

    edges = [Edge(from_=f, to=t, kind=k) for f, t, k in edge_set]
    edges.sort(key=lambda e: (e.from_, e.to, e.kind))

    return Graph(nodes=tuple(nodes), edges=tuple(edges))


def _build_csharp_indexes(typed_files: list[tuple[Path, str]]) -> CSharpIndexes:
    cs_inputs: list[tuple[Path, str]] = []
    for path, language in typed_files:
        if language != "C#":
            continue
        try:
            cs_inputs.append((path, path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return build_indexes(cs_inputs)


def _build_csharp_type_usages(
    typed_files: list[tuple[Path, str]],
) -> dict[Path, set[str]]:
    out: dict[Path, set[str]] = {}
    for path, language in typed_files:
        if language != "C#":
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        out[path] = csharp_parser.extract_type_usages(source)
    return out


def _emit_python_edges(
    raws: list[RawImport],
    root: Path,
    internal_paths: set[Path],
    from_rel: str,
    edge_set: set[tuple[str, str, str]],
) -> None:
    for raw in raws:
        targets = resolve_python(raw, root, internal_paths)
        if targets:
            for target in targets:
                edge_set.add((from_rel, target.relative_to(root).as_posix(), "internal"))
        else:
            edge_set.add((from_rel, raw.raw, "external"))


def _emit_js_edges(
    raws: list[RawImport],
    internal_paths: set[Path],
    root: Path,
    from_rel: str,
    edge_set: set[tuple[str, str, str]],
) -> None:
    for raw in raws:
        targets = resolve_js(raw, internal_paths)
        if targets:
            for target in targets:
                edge_set.add((from_rel, target.relative_to(root).as_posix(), "internal"))
        else:
            edge_set.add((from_rel, raw.raw, "external"))


def _emit_csharp_edges(
    raws: list[RawImport],
    source: Path,
    from_rel: str,
    root: Path,
    indexes: CSharpIndexes,
    type_usages: set[str],
    edge_set: set[tuple[str, str, str]],
) -> None:
    explicit_namespaces: set[str] = set()
    for raw in raws:
        explicit_namespaces.add(raw.raw)
        if raw.raw not in indexes.namespace_to_files:
            edge_set.add((from_rel, raw.raw, "external"))
            continue
        targets = resolve_csharp_types(
            raw.raw, source, type_usages, indexes.type_to_file
        )
        for target in targets:
            edge_set.add((from_rel, target.relative_to(root).as_posix(), "internal"))

    for own_namespace in indexes.file_to_namespaces.get(source, set()):
        if own_namespace in explicit_namespaces:
            continue
        targets = resolve_csharp_types(
            own_namespace, source, type_usages, indexes.type_to_file
        )
        for target in targets:
            edge_set.add((from_rel, target.relative_to(root).as_posix(), "internal"))
