from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

_BLOCK_NAMESPACE = re.compile(r"\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*\{")
_FILE_SCOPED_NAMESPACE = re.compile(r"\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;")
_TYPE_DECL = re.compile(
    r"\b(?:public|internal|private|protected|sealed|static|abstract|partial)?"
    r"(?:\s+(?:public|internal|private|protected|sealed|static|abstract|partial))*"
    r"\s*(?:class|interface|struct|record|enum)\s+(\w+)"
)


@dataclass(frozen=True, slots=True)
class CSharpIndexes:
    namespace_to_files: dict[str, set[Path]]
    type_to_file: dict[tuple[str, str], Path]
    file_to_namespaces: dict[Path, set[str]]


def build_indexes(cs_files: Iterable[tuple[Path, str]]) -> CSharpIndexes:
    namespace_to_files: dict[str, set[Path]] = defaultdict(set)
    type_to_file: dict[tuple[str, str], Path] = {}
    file_to_namespaces: dict[Path, set[str]] = defaultdict(set)

    for path, source in cs_files:
        for namespace, content in _iter_namespace_segments(source):
            namespace_to_files[namespace].add(path)
            file_to_namespaces[path].add(namespace)
            for type_match in _TYPE_DECL.finditer(content):
                type_name = type_match.group(1)
                type_to_file[(namespace, type_name)] = path

    return CSharpIndexes(
        namespace_to_files=dict(namespace_to_files),
        type_to_file=type_to_file,
        file_to_namespaces=dict(file_to_namespaces),
    )


def build_namespace_index(
    cs_files: Iterable[tuple[Path, str]],
) -> dict[str, set[Path]]:
    """Backward-compatible wrapper used by older callers/tests."""
    return build_indexes(cs_files).namespace_to_files


def _iter_namespace_segments(source: str) -> Iterable[tuple[str, str]]:
    """Yield (namespace, content) pairs for each namespace declared in the source.

    File-scoped: ``namespace X;`` makes the rest of the file a single segment.
    Block: ``namespace X { ... }`` yields each block separately.
    """
    file_scoped = _FILE_SCOPED_NAMESPACE.search(source)
    if file_scoped:
        yield file_scoped.group(1), source[file_scoped.end():]
        return

    pos = 0
    while True:
        m = _BLOCK_NAMESPACE.search(source, pos)
        if m is None:
            return
        namespace = m.group(1)
        start = m.end()
        end = _find_matching_brace(source, start)
        yield namespace, source[start:end]
        pos = end + 1 if end > start else m.end()


def _find_matching_brace(source: str, start: int) -> int:
    depth = 1
    i = start
    n = len(source)
    while i < n and depth > 0:
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n
