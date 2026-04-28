from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

_BLOCK_NAMESPACE = re.compile(r"\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*\{")
_FILE_SCOPED_NAMESPACE = re.compile(r"\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;")


def build_namespace_index(cs_files: Iterable[tuple[Path, str]]) -> dict[str, set[Path]]:
    """Map each declared namespace to the set of files that declare it.

    ``cs_files`` is an iterable of ``(path, source_code)`` pairs. Files that
    declare no namespace contribute nothing to the index.
    """
    index: dict[str, set[Path]] = defaultdict(set)
    for path, source in cs_files:
        for match in _BLOCK_NAMESPACE.finditer(source):
            index[match.group(1)].add(path)
        for match in _FILE_SCOPED_NAMESPACE.finditer(source):
            index[match.group(1)].add(path)
    return dict(index)
