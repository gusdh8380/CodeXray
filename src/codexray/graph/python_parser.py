from __future__ import annotations

import ast
from pathlib import Path

from .types import RawImport


def extract_imports(source_code: str, source_path: Path) -> tuple[list[RawImport], bool]:
    """Return (imports, syntax_error). On SyntaxError, returns ([], True)."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return [], True

    imports: list[RawImport] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    RawImport(
                        source=source_path,
                        raw=alias.name,
                        level=0,
                        language="Python",
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            level = node.level or 0
            if node.module:
                imports.append(
                    RawImport(
                        source=source_path,
                        raw=node.module,
                        level=level,
                        language="Python",
                    )
                )
            else:
                # `from . import X, Y` — emit one RawImport per name.
                for alias in node.names:
                    imports.append(
                        RawImport(
                            source=source_path,
                            raw=alias.name,
                            level=level,
                            language="Python",
                        )
                    )
    return imports, False
